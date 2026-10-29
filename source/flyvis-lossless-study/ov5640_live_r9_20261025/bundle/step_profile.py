"""Per-producer-step timing only; thread-local, no data or hardware ownership."""
import threading,time
_local=threading.local()
ENABLED=False
def begin():
    if ENABLED:_local.values={}
    elif hasattr(_local,'values'):del _local.values
def tick():return time.perf_counter_ns() if ENABLED else 0
def add(name,start,byte_count=0):
    values=getattr(_local,'values',None)
    if values is None:return
    d=values.setdefault(name,{'calls':0,'ms':0.0,'bytes':0})
    d['calls']+=1;d['ms']+=(time.perf_counter_ns()-start)/1e6;d['bytes']+=byte_count

def snapshot():return {k:dict(v) for k,v in getattr(_local,'values',{}).items()}
