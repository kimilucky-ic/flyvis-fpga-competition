"""Thread-local sampled timing; no data/hardware ownership or per-step files.
Wall and thread CPU overlap across nested stages; never sum parent and child.
"""
import threading,time
_local=threading.local()
ENABLED=False

def begin(active=None):
    enabled=ENABLED if active is None else bool(active)
    if enabled:_local.values={}
    elif hasattr(_local,'values'):del _local.values

def tick():
    if not hasattr(_local,'values'):return 0
    return (time.perf_counter_ns(),time.thread_time_ns())

def add(name,start,byte_count=0):
    values=getattr(_local,'values',None)
    if values is None or not start:return
    cpu=time.thread_time_ns();wall=time.perf_counter_ns()
    d=values.setdefault(name,{'calls':0,'ms':0.0,'thread_cpu_ms':0.0,'bytes':0})
    d['calls']+=1;d['ms']+=(wall-start[0])/1e6;d['thread_cpu_ms']+=(cpu-start[1])/1e6;d['bytes']+=byte_count

def snapshot():return {k:dict(v) for k,v in getattr(_local,'values',{}).items()}
