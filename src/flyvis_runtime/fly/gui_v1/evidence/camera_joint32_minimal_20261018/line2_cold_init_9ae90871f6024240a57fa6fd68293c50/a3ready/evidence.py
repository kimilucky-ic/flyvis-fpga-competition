"""Drop-in board evidence API; no PYNQ imports or hardware side effects.

Deploy only as evidence.py in a future separately approved package. The original
numeric driver and protocol remain byte-for-byte unchanged.
"""
import json
import os
from pathlib import Path
import time
from .evidence_journal import JournalWriter

OWNERS = {}

def save_bytes(path, data):
    path = Path(path)
    owner = OWNERS.get(path.parent.resolve())
    if owner is None:
        # Explicit standalone metadata preserves the existing API.
        with path.open('xb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        return
    owner.journal.add(path.name, data)
    if path.name.endswith('PREPARED.json'):
        owner.journal.checkpoint('PREPARED_METADATA')

def save_json(path, record):
    save_bytes(path, (json.dumps(record, indent=2)+'\n').encode('utf-8'))

class Evidence:
    def init__(self, directory, *, sync=None):
        self.directory = Path(directory)
        self.journal = JournalWriter(self.directory, {'role':'BOARD', 'run_directory':self.directory.name, 'admission':'UNVERIFIED_CAPTURE'}, sync=sync)
        OWNERS[self.directory.resolve()] = self
        self.sequence = 0
        self.last_event = None
        self.in_compute = False
        self.requests = self.acks = 0
        self.failed = False

    def record(self, record):
        with self.journal.lock:
            event = record['event']
            self.last_event = event
            self.journal.add('events.jsonl', (json.dumps(record)+'\n').encode('utf-8'), kind='line')
            if event == 'COMPUTE_WINDOW_STARTED':
                self.in_compute = True
            if event == 'REQUEST_ACCEPTED':
                self.in_compute = True
                self.requests += 1
            if event == 'ACK_SENT':
                self.acks += 1
            failed = any(word in event for word in ('FAIL', 'UNKNOWN', 'INCOMPLETE'))
            if failed:
                self.failed = True
            if event == 'BOARD_COMPLETE':
                if self.failed or self.requests != 485 or self.acks != 485 or record.get('requests') != 485 or record.get('commits') != 485:
                    raise ValueError('Incomplete board capture cannot close as complete')
                self.journal.close('CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION', requests=485, acks=485)
            elif not self.in_compute or event == 'ACK_SENT' or event.startswith('WIRE_') or failed:
                # Initialization intent remains durable BEFORE load/reset/MMIO;
                # transaction fine-grained MMIO records are retained in RAM until
                # wire output barriers. No log sync is inserted ARM->MM2S.
                self.journal.checkpoint(event)
            return record

    def event(self, event, **values):
        with self.journal.lock:
            return self.record(dict(event=event, monotonic_ns=time.monotonic_ns(), **values))

    def wire(self, direction, raw):
        with self.journal.lock:
            name = 'wire_%03d_%s.bin' % (self.sequence, direction)
            self.sequence += 1
            self.journal.add(name, raw)
            # Wire observer is called before sendall or before received data is
            # returned to the driver. Persist request/COMMIT before MMIO and
            # candidate/RELEASE/ACK before sending. No network retry on failure.
            record = dict(event='WIRE_'+direction.upper(), monotonic_ns=time.monotonic_ns(), file=name, bytes=len(raw))
            if 'incomplete' in direction:
                self.failed = True
            self.record(record)

    def close(self):
        if not self.journal.closed:
            self.journal.close('FAILED_OR_INCOMPLETE', requests=self.requests, acks=self.acks)
