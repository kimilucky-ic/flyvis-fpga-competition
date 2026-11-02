"""Bounded diagnostic only: no forced collection, policy change, logging or I/O.
Step is the active producer step at event time; collector thread is separate.
A coincident event supports timing correlation, not proof of causation.
"""
import gc,threading,time
class GcEvents:
    def __init__(self,capacity=256):
        if type(capacity) is not int or not 1<=capacity<=1024:raise ValueError('bounded GC events')
        self.capacity=capacity;self.events=[];self.dropped=0;self.errors=0;self.step=None;self.active=False
        self.callback=self._event;self.before=dict(enabled=gc.isenabled(),threshold=list(gc.get_threshold()))
    def start(self):
        if self.active:raise RuntimeError('GC recorder already active')
        gc.callbacks.append(self.callback);self.active=True
    def _event(self,phase,info):
        if not self.active:return
        try:
            if len(self.events)>=self.capacity:self.dropped+=1;return
            self.events.append((phase,time.monotonic_ns(),time.thread_time_ns(),threading.get_ident(),self.step,
                info.get('generation',-1),info.get('collected',0),info.get('uncollectable',0)))
        except BaseException:self.errors+=1
    def close(self):
        self.active=False
        for i,callback in enumerate(gc.callbacks):
            if callback is self.callback:
                del gc.callbacks[i];break
    def report(self):
        return dict(schema='line11-gc-events/v1',columns=['phase','monotonic_ns','thread_cpu_ns','thread_id','active_producer_step','generation','collected','uncollectable'],events=list(self.events),capacity=self.capacity,dropped_events=self.dropped,callback_errors=self.errors,
          complete=self.dropped==0 and self.errors==0,collector_policy_before=self.before,
          collector_policy_after=dict(enabled=gc.isenabled(),threshold=list(gc.get_threshold())),
          scope='bounded producer-loop recording only; callback removed before flush; active step does not identify collector thread',forced_collections=0,policy_changes=0)
