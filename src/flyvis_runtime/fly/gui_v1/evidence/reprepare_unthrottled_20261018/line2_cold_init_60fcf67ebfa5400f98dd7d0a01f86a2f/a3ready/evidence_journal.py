"""Bounded append-only evidence batches. Python 3.8+, standard library only.

One durable file, lossless logical files/events, SHA256 chain and explicit
checkpoints. A readable batch is not a completed experiment. No recovery writes
or automatic resume are provided; a failed writer is permanently poisoned.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import threading
import time

MAGIC = b'FVEJ0001'
PREFIX = struct.Struct('>8sIQ32s')
MAX_DATA = 8 * 1024 * 1024
MAX_META = 2 * 1024 * 1024

def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def safe_name(name):
    if not isinstance(name, str) or not name or name in ('.', '..') or any(c in name for c in '/\\:'):
        raise ValueError('Invalid logical evidence filename')
    return name

class JournalWriter:
    def init__(self, directory, context, *, sync=None, max_pending=MAX_DATA):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.path = self.directory / 'evidence.fvej'
        self.stream = self.path.open('xb', buffering=0)
        self.lock = threading.RLock()
        self.context = dict(context)
        self.sync_fn = sync or os.fsync
        self.max_pending = min(max_pending, MAX_DATA)
        self.pending = []
        self.pending_bytes = 0
        self.names = set()
        self.previous = '0' * 64
        self.sequence = self.sync_calls = self.sync_ns = 0
        self.poisoned = self.closed = False
        try:
            self.checkpoint('OPEN')
            if os.name != 'nt':
                fd = os.open(str(self.directory), os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
        except BaseException:
            self.poisoned = True
            self.stream.close()
            raise

    def _ready(self):
        if self.poisoned or self.closed:
            raise RuntimeError('Evidence writer closed/poisoned; no retry')

    def add(self, name, data, *, kind='file'):
        with self.lock:
            self._ready()
            safe_name(name)
            if kind not in ('file', 'line') or not isinstance(data, bytes):
                raise TypeError('Evidence bytes/kind')
            if kind == 'file' and name in self.names:
                self.poisoned = True
                raise ValueError('Duplicate evidence file: ' + name)
            if self.pending_bytes + len(data) > self.max_pending or len(self.pending) >= 8192:
                self.poisoned = True
                raise BufferError('Evidence batch bound; stop before next side effect')
            self.names.add(name)
            self.pending.append((name, kind, data))
            self.pending_bytes += len(data)
            return {'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

    def checkpoint(self, barrier, terminal=None):
        with self.lock:
            self._ready()
            self.attempted_barrier = barrier
            catalog = []
            offset = 0
            for name, kind, data in self.pending:
                catalog.append(dict(name=name, kind=kind, offset=offset, size=len(data), sha256=hashlib.sha256(data).hexdigest()))
                offset += len(data)
            meta = encoded(dict(schema='flyvis-evidence-journal/v1', sequence=self.sequence, previous_sha256=self.previous,
                                context=self.context, barrier=barrier, terminal=terminal, records=catalog))
            if len(meta) > MAX_META:
                self.poisoned = True
                raise BufferError('Evidence metadata bound')
            payload = b''.join(data for _, _, data in self.pending)
            digest = hashlib.sha256(meta + payload).digest()
            packet = PREFIX.pack(MAGIC, len(meta), len(payload), digest) + meta + payload
            try:
                view = memoryview(packet)
                while view:
                    n = self.stream.write(view)
                    if n is None or n <= 0:
                        raise OSError('Short evidence write')
                    view = view[n:]
                self.stream.flush()
                tick = time.perf_counter_ns()
                self.sync_calls += 1
                self.sync_fn(self.stream.fileno())
                self.sync_ns += time.perf_counter_ns() - tick
            except BaseException:
                self.poisoned = True
                raise
            self.previous = digest.hex()
            self.sequence += 1
            self.pending = []
            self.pending_bytes = 0

    def close(self, status='INCOMPLETE', **counts):
        with self.lock:
            if self.closed:
                return
            try:
                self._ready()
                self.checkpoint('CLOSE', dict(status=status, **counts))
            finally:
                self.closed = True
                self.stream.close()

    def abandon(self):
        """Close the local handle only, without inventing a completion record."""
        with self.lock:
            self.poisoned = self.closed = True
            self.stream.close()

class JournalReader:
    def init__(self, path, *, allow_incomplete=False):
        self.path = Path(path)
        self.files = {}
        self.batches = []
        self.terminal = None
        self.truncated = False
        self.context = None
        previous = '0' * 64
        with self.path.open('rb') as stream:
            while True:
                head = stream.read(PREFIX.size)
                if not head:
                    break
                if self.terminal is not None:
                    raise ValueError('Bytes after closed evidence')
                if len(head) != PREFIX.size:
                    self.truncated = True
                    break
                magic, mlen, plen, digest = PREFIX.unpack(head)
                if magic != MAGIC or not 0 < mlen <= MAX_META or plen > MAX_DATA:
                    raise ValueError('Evidence prefix/bounds')
                meta = stream.read(mlen)
                data_offset = stream.tell()
                data = stream.read(plen)
                if len(meta) != mlen or len(data) != plen:
                    self.truncated = True
                    break
                if hashlib.sha256(meta + data).digest() != digest:
                    raise ValueError('Evidence checksum')
                batch = json.loads(meta)
                if batch['schema'] != 'flyvis-evidence-journal/v1' or batch['sequence'] != len(self.batches) or batch['previous_sha256'] != previous:
                    raise ValueError('Evidence sequence/chain')
                if self.context is None:
                    self.context = batch['context']
                if batch['context'] != self.context:
                    raise ValueError('Evidence identity changed')
                offset = 0
                for entry in batch['records']:
                    name = safe_name(entry['name'])
                    size = entry['size']
                    if entry['offset'] != offset or type(size) is not int or size < 0 or offset + size > plen:
                        raise ValueError('Evidence entry bounds')
                    if hashlib.sha256(data[offset:offset+size]).hexdigest() != entry['sha256']:
                        raise ValueError('Logical file checksum')
                    if entry['kind'] not in ('file', 'line') or (name in self.files and (entry['kind'] != 'line' or self.files[name][0]['kind'] != 'line')):
                        raise ValueError('Duplicate/mixed evidence file')
                    self.files.setdefault(name, []).append(dict(entry, absolute_offset=data_offset+offset))
                    offset += size
                if offset != plen:
                    raise ValueError('Unindexed payload')
                self.batches.append(batch)
                self.terminal = batch['terminal']
                previous = digest.hex()
        self.last_sha256 = previous
        if not allow_incomplete and (self.truncated or self.terminal is None):
            raise ValueError('Incomplete evidence; never promote to PASS')

    def read(self, name):
        chunks = []
        with self.path.open('rb') as stream:
            for entry in self.files[name]:
                stream.seek(entry['absolute_offset'])
                data = stream.read(entry['size'])
                if hashlib.sha256(data).hexdigest() != entry['sha256']:
                    raise ValueError('Evidence changed after indexing')
                chunks.append(data)
        return b''.join(chunks)

    def export(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=False)
        for name in self.files:
            with (directory / name).open('xb') as stream:
                stream.write(self.read(name))
        return directory
