"""Original four wire barriers, with explicit variable-window completion."""
import json
from pathlib import Path
from .legacy_light_evidence import Evidence as PreviousEvidence
from .fast_journal import JournalWriter
from .evidence import OWNERS

class Evidence(PreviousEvidence):
    def init__(self,directory,config,*,sync=None):
        self.config=config;self.directory=Path(directory)
        self.journal=JournalWriter(self.directory,dict(role='BOARD',run_directory=self.directory.name,admission='UNVERIFIED_CAPTURE',
            execution_kind='CPU_FIXTURE_ONLY' if config.get('test_fixture') is True else 'CAMERA_JOINT_PENDING_AUDIT'),sync=sync)
        OWNERS[self.directory.resolve()]=self
        self.sequence=0;self.last_event=None;self.in_compute=False;self.requests=self.acks=0;self.failed=False
        self.step_start=None;self.current_step=None
    def record(self,record):
        with self.journal.lock:
            event=record['event'];self.last_event=event
            if event=='ACK_SENT':self.journal.add('ps_profile_%d.json'%record['step'],json.dumps(self.profile(),sort_keys=True).encode())
            self.journal.append_line('events.jsonl',(json.dumps(record)+'\n').encode())
            if event in ('COMPUTE_WINDOW_STARTED','REQUEST_ACCEPTED'):self.in_compute=True
            if event=='REQUEST_ACCEPTED':self.requests+=1
            if event=='ACK_SENT':self.acks+=1
            failed=any(word in event for word in ('FAIL','UNKNOWN','INCOMPLETE'))
            if failed:self.failed=True
            if event=='BOARD_COMPLETE':raise ValueError('CAMERA_REQUIRES_FINISH_WINDOW')
            if not self.in_compute or event.startswith('WIRE_') or failed:self.journal.checkpoint(event)
            return record
    def finish_window(self,record):
        with self.journal.lock:
            n=record['completed_steps']
            if self.failed or self.requests!=self.acks or self.acks!=n or not 0<=n<=self.config['max_steps'] or record.get('source_closed') is not True:
                raise ValueError('INCOMPLETE_CAMERA_CAPTURE')
            self.journal.add('PS_PROFILE_TOTAL.json',json.dumps(self.profile(total=True),sort_keys=True).encode())
            self.event('FINISH_WINDOW_ACCEPTED',**record)
            self.journal.close('CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION',requests=n,acks=n,completed_steps=n,reason=record['reason'],source_closed=True,whole_run_acceptance='PENDING')
