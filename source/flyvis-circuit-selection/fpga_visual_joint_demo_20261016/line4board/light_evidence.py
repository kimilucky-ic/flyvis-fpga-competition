"""Keep raw IO and durable COMMIT/ACK before send; defer only ACK_SENT marker."""
import json,os,time
from pathlib import Path
from .fast_journal import JournalWriter
from .evidence import Evidence as OriginalEvidence,OWNERS
from . import protocol as w

class Evidence(OriginalEvidence):
    def init__(self,directory,config,*,sync=None):
        self.config=config;self.directory=Path(directory)
        self.journal=JournalWriter(self.directory,{'role':'BOARD','run_directory':self.directory.name,'admission':'UNVERIFIED_CAPTURE'},sync=sync)
        OWNERS[self.directory.resolve()]=self
        self.sequence=0;self.last_event=None;self.in_compute=False;self.requests=self.acks=0;self.failed=False
        self.step_start=None;self.current_step=None
    def wire(self,direction,raw):
        if direction=='rx' and len(raw)>=256:
            try:header=w.Header.unpack(raw[:256])
            except ValueError:header=None
            if header is not None and header.op==w.STEP:self.step_start=self.journal.snapshot();self.current_step=header.step
        return super().wire(direction,raw)
    def profile(self,total=False):
        current=self.journal.snapshot();before={} if total else (self.step_start or {})
        return dict(schema='flyvis-ps-light-io/v1',run_id=self.config['run_id'],server_session=self.config['server_session'],
            model_step=self.current_step,fsync_calls=current['fsync_calls']-before.get('fsync_calls',0),
            phase_ns={k:v-before.get('phase_ns',{}).get(k,0) for k,v in current['phase_ns'].items()},
            coverage='SERVICE_BEFORE_FINAL_CLOSE' if total else 'STEP_RX_THROUGH_DURABLE_ACK_TX',
            limits='Batch IO phases only. No per-event or per-MMIO timers. ACK_SENT marker joins next STEP_RX or final CLOSE; raw ACK and RELEASE proof already durable before send.')
    def record(self,record):
        with self.journal.lock:
            event=record['event'];self.last_event=event
            if event=='ACK_SENT':self.journal.add('ps_profile_%d.json'%record['step'],json.dumps(self.profile(),sort_keys=True).encode())
            elif event=='BOARD_COMPLETE':self.journal.add('PS_PROFILE_TOTAL.json',json.dumps(self.profile(total=True),sort_keys=True).encode())
            self.journal.append_line('events.jsonl',(json.dumps(record)+'\n').encode())
            if event in ('COMPUTE_WINDOW_STARTED','REQUEST_ACCEPTED'):self.in_compute=True
            if event=='REQUEST_ACCEPTED':self.requests+=1
            if event=='ACK_SENT':self.acks+=1
            failed=any(word in event for word in ('FAIL','UNKNOWN','INCOMPLETE'))
            if failed:self.failed=True
            if event=='BOARD_COMPLETE':
                if self.failed or self.requests!=1000 or self.acks!=1000 or record.get('requests')!=1000 or record.get('commits')!=1000:
                    raise ValueError('Incomplete board capture cannot close as complete')
                self.journal.close('CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION',requests=1000,acks=1000)
            elif not self.in_compute or event.startswith('WIRE_') or failed:self.journal.checkpoint(event)
            return record

def attach(driver,evidence):
    """No register proxies or per-event clock calls; numerical driver unchanged."""
    return None
