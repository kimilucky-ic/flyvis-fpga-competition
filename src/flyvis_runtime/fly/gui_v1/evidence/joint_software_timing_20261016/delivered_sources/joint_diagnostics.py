"""Bounded in-memory host observations; never changes a neural/durability decision.

Spans are inclusive and may overlap across stages/threads. Host wall minus thread
CPU includes scheduling and I/O/CUDA waits; it is not a kernel measurement.
All trace I/O happens at explicit cleanup, after the neural session is closed.
"""
from contextlib import contextmanager, nullcontext
import json
import os
import threading
import time


class NullDiagnostics:
    def measure(self, name): return nullcontext()
    def step(self, step): return nullcontext()
    def call(self, name, function, *args, **kwargs): return function(*args, **kwargs)


NONE = NullDiagnostics()


class JointDiagnostics:
    def init__(self, role, capacity=65536, *, wall=time.perf_counter_ns, cpu=time.thread_time_ns):
        if not isinstance(role,str) or not 1<=len(role)<=40 or type(capacity) is not int or not 1<=capacity<=131072:
            raise ValueError('JOINT_DIAGNOSTIC_BOUND')
        self.role,self.capacity,self.wall,self.cpu=role,capacity,wall,cpu
        self.origin=wall();self.rows=[];self.dropped=0;self.step_id=None;self.lock=threading.Lock()

    @contextmanager
    def step(self, step):
        prior=self.step_id;self.step_id=step
        try:
            with self.measure('engine.step_total'):yield
        finally:self.step_id=prior

    @contextmanager
    def measure(self, name):
        if not isinstance(name,str) or not 1<=len(name)<=100:raise ValueError('JOINT_DIAGNOSTIC_NAME')
        step=self.step_id;began=self.wall();cpu=self.cpu();failed=False
        try:yield
        except BaseException:
            failed=True;raise
        finally:
            end=self.wall();spent=self.cpu()-cpu
            row=dict(name=name,step_id=step,thread_id=threading.get_ident(),start_ns=began-self.origin,
                     duration_ns=end-began,thread_cpu_ns=spent,failed=failed)
            with self.lock:
                if len(self.rows)<self.capacity:self.rows.append(row)
                else:self.dropped+=1

    def call(self,name,function,*args,**kwargs):
        with self.measure(name):return function(*args,**kwargs)

    def save(self,path,session_id,run_id):
        with self.lock:rows=list(self.rows);dropped=self.dropped
        summary={}
        for row in rows:
            s=summary.setdefault(row['name'],dict(calls=0,wall_ns=0,thread_cpu_ns=0,max_wall_ns=0,failures=0))
            s['calls']+=1;s['wall_ns']+=row['duration_ns'];s['thread_cpu_ns']+=row['thread_cpu_ns']
            s['max_wall_ns']=max(s['max_wall_ns'],row['duration_ns']);s['failures']+=row['failed']
        data=dict(schema='flyvis-joint-host-diagnostics/v1',role=self.role,session_id=session_id,run_id=run_id,
                  clock_domain=os.name+'_PROCESS_LOCAL_PERF_COUNTER_NS',origin_ns=self.origin,
                  semantics='Inclusive nested spans; never sum overlapping spans. Wall minus thread CPU is mixed wait/scheduling.',
                  scope='HOST_OBSERVATIONS_NOT_PL_REGISTERS_OR_CUDA_KERNEL_SUM',dropped_spans=dropped,
                  diagnostic_complete=dropped==0,summary=summary,spans=rows)
        with path.open('x',encoding='utf-8') as f:
            json.dump(data,f,separators=(',',':'),allow_nan=False);f.flush();os.fsync(f.fileno())
        return data


class _StreamProbe:
    def init__(self,stream,diagnostics):self.stream,self.diagnostics=stream,diagnostics
    def __getattr__(self,name):return getattr(self.stream,name)
    def write(self,data):return self.diagnostics.call('PC_journal.write',self.stream.write,data)
    def flush(self):return self.diagnostics.call('PC_journal.flush',self.stream.flush)


class TimedJournal:
    """Observe the accepted writer, preserving every byte and fsync call/order."""
    def init__(self,writer,diagnostics):
        self.writer,self.diagnostics=writer,diagnostics
        writer.stream=_StreamProbe(writer.stream,diagnostics)
    def __getattr__(self,name):return getattr(self.writer,name)
    @property
    def sync_fn(self):return self.writer.sync_fn
    @sync_fn.setter
    def sync_fn(self,value):self.writer.sync_fn=value
    def add(self,*args,**kwargs):return self.diagnostics.call('PC_journal.add',self.writer.add,*args,**kwargs)
    def checkpoint(self,barrier,*args,**kwargs):
        return self.diagnostics.call('PC_journal.checkpoint.'+barrier,self.writer.checkpoint,barrier,*args,**kwargs)
    def close(self,*args,**kwargs):return self.diagnostics.call('PC_journal.close',self.writer.close,*args,**kwargs)


def measured_sync(diagnostics,sync=os.fsync):
    def preserve(fd):return diagnostics.call('PC_journal.fsync',sync,fd)
    return preserve
