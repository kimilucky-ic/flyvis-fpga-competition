"""Bounded host timing and lazy CUDA-event probes; import never initializes devices."""
from collections import defaultdict,deque
from contextlib import contextmanager
import time
import sys
import numpy as np


class Timings:
    def init__(self):
        self.rows=defaultdict(lambda:deque(maxlen=10000));self.totals=defaultdict(float);self.counts=defaultdict(int)
        self.trace=None
    def add(self,name,seconds):
        if not np.isfinite(seconds) or seconds<0:raise ValueError('INVALID_TIMING')
        self.rows[name].append(float(seconds));self.totals[name]+=float(seconds);self.counts[name]+=1
    @contextmanager
    def measure(self,name):
        start=time.perf_counter();trace=self.trace
        cpu=time.thread_time() if trace is not None and trace.current is not None else None
        try:yield
        finally:
            elapsed=time.perf_counter()-start;self.add(name,elapsed)
            if cpu is not None:trace.stage(name,elapsed,time.thread_time()-cpu)
    def summary(self):
        result={}
        for k,v in self.rows.items():
            if not v:continue
            values=np.fromiter(v,dtype=np.float64);p=np.percentile(values,[50,95,99])*1000
            result[k]=dict(count=self.counts[k],total_s=self.totals[k],p50_ms=float(p[0]),
                p95_ms=float(p[1]),p99_ms=float(p[2]),max_ms=float(values.max()*1000),sample_window=len(v))
        return result


class StepTrace:
    """Bounded in-memory host timeline; serialized only after CUDA/asset cleanup.

    Wall minus thread CPU includes CUDA/I/O waits AND OS scheduling, not a pure
    kernel measurement. Nested stage durations overlap and must not be summed.
    """
    def init__(self,capacity=60000):
        self.capacity=capacity;self.rows=[];self.current=None
    def begin(self,step,elapsed,lag,display_due):
        if self.current is not None or len(self.rows)>=self.capacity:raise ValueError('STEP_TRACE_BOUND_OR_ORDER')
        self.current=dict(step_id=step,entry_elapsed_s=elapsed,schedule_lag_wall_s=lag,
            display_due=bool(display_due),stages={})
        self.wall=time.perf_counter();self.cpu=time.thread_time()
    def stage(self,name,wall,cpu):
        if self.current is None:return
        row=self.current['stages'].setdefault(name,dict(wall_s=0.,thread_cpu_s=0.))
        row['wall_s']+=wall;row['thread_cpu_s']+=cpu
    def finish(self,computed_steps,durable_steps):
        if self.current is None:return
        self.current.update(cycle_wall_s=time.perf_counter()-self.wall,cycle_thread_cpu_s=time.thread_time()-self.cpu,
            computed_steps=computed_steps,durable_steps=durable_steps)
        self.rows.append(self.current);self.current=None
    def save(self,path,session_id,run_id):
        import json,os
        if self.current is not None:raise ValueError('STEP_TRACE_INCOMPLETE')
        with path.open('x',encoding='utf-8') as stream:
            for row in self.rows:
                stream.write(json.dumps(dict(schema='flyvis-host-step-trace/v1',session_id=session_id,run_id=run_id,**row),
                    separators=(',',':'),allow_nan=False)+'\n')
            stream.flush();os.fsync(stream.fileno())


class SummaryCache:
    """Percentiles are diagnostics, not neural state. Refresh at most once per second.

    Every underlying sample is still recorded; final results use Timings.summary().
    The cache is used only by its owning compute thread.
    """
    def init__(self,interval=1.):
        self.interval=interval;self.at=None;self.value={}
    def get(self,timing,now=None):
        now=time.monotonic() if now is None else now
        if self.at is None or now-self.at>=self.interval:
            self.value=timing.summary();self.at=now
        return self.value,now-self.at


@contextmanager
def host_scheduling(interval_s=.001):
    """Bound Python GIL handoff delays in this worker; no CUDA/model modification."""
    if interval_s not in (.001,.005):raise ValueError('UNKNOWN_HOST_SCHEDULING_PROFILE')
    previous=sys.getswitchinterval();sys.setswitchinterval(interval_s)
    try:yield dict(python_switch_interval_s=interval_s,previous_interval_s=previous,
                   neural_algorithm_changed=False,thread_count_changed=False)
    finally:sys.setswitchinterval(previous)


class CudaProbes:
    """Wrap original update/decoder calls without replacing their computation.

    Event elapsed measures the CUDA stream interval, not a profiler kernel sum.
    Collect only completed events; no synchronize is inserted into the hot loop.
    """
    def init__(self,torch,timings):self.torch=torch;self.timings=timings;self.pending=[];self.original=[]
    def wrap(self,obj,name,stage,sample_every=1):
        if type(sample_every) is not int or sample_every<1:raise ValueError('CUDA_PROBE_SAMPLE_INTERVAL')
        original=getattr(obj,name);self.original.append((obj,name,original))
        calls=0
        def measured(*args,**kwargs):
            nonlocal calls
            calls+=1
            if (calls-1)%sample_every:return original(*args,**kwargs)
            if len(self.pending)>=1024:raise ValueError('CUDA_TIMING_QUEUE_LIMIT')
            a=self.torch.cuda.Event(enable_timing=True);b=self.torch.cuda.Event(enable_timing=True)
            a.record()
            try:return original(*args,**kwargs)
            finally:b.record();self.pending.append((stage,a,b))
        setattr(obj,name,measured)
    def collect(self):
        outstanding=[]
        for stage,a,b in self.pending:
            if b.query():self.timings.add(stage,a.elapsed_time(b)/1000)
            else:outstanding.append((stage,a,b))
        self.pending=outstanding
    def close(self):
        for obj,name,original in reversed(self.original):setattr(obj,name,original)
        self.collect()


def latency_sample(source,draw_server_monotonic_ns,clock_uncertainty_ms):
    """Both timestamps are Windows monotonic; WSL clocks never subtracted."""
    value=(draw_server_monotonic_ns-source['received_monotonic_ns'])/1e6
    if not np.isfinite(value) or value<0 or not 0<=clock_uncertainty_ms<=50:raise ValueError('CLOCK_PAIR_INVALID')
    return dict(receipt_to_render_estimate_ms=value,clock_uncertainty_ms=clock_uncertainty_ms,
        lower_ms=max(0.,value-clock_uncertainty_ms),upper_ms=value+clock_uncertainty_ms,
        semantics='requestAnimationFrame callback estimate; physical screen scanout not measured')


def realtime_verdict(duration_s,steps,draws,upper_latencies_ms,dropped,clock_valid):
    if duration_s<10 or not upper_latencies_ms or not clock_valid:return 'NOT_RUN'
    return 'PASS_MEASURED_TARGETS_PENDING_LIVE_REVIEW' if (steps/duration_s>=200 and draws/duration_s>=15
        and np.percentile(upper_latencies_ms,95)<200 and dropped==0) else 'NOT_MET'
