"""Thread-local sampled timing; no data/hardware ownership or per-step files.
Wall and thread CPU overlap across nested stages; never sum parent and child.
"""
import threading,time
_local=threading.local()
ENABLED=False

def begin(active=None,keys=None):
    enabled=ENABLED if active is None else bool(active)
    _local.keys=keys
    if enabled:_local.values={}
    elif hasattr(_local,'values'):del _local.values

def tick(name=None):
    if not hasattr(_local,'values'):return 0
    keys=getattr(_local,'keys',None)
    if keys is not None and name not in keys:return 0
    return (time.monotonic_ns(),time.thread_time_ns())

def add(name,start,byte_count=0):
    values=getattr(_local,'values',None)
    if values is None or not start:return
    cpu=time.thread_time_ns();wall=time.monotonic_ns()
    d=values.setdefault(name,{'calls':0,'ms':0.0,'thread_cpu_ms':0.0,'bytes':0,'start_ns':start[0],'end_ns':wall})
    d['end_ns']=wall
    d['calls']+=1;d['ms']+=(wall-start[0])/1e6;d['thread_cpu_ms']+=(cpu-start[1])/1e6;d['bytes']+=byte_count

def snapshot():return {k:dict(v) for k,v in getattr(_local,'values',{}).items()}
