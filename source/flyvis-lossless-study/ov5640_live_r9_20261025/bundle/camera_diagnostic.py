"""Readframe call-tree timing. No camera acquisition is started by this module.
Inclusive/exclusive timings have profiler overhead; not a zero-overhead benchmark.
"""
import sys,time,hashlib
from pathlib import Path
class CallTiming:
    def init__(self):self.stack=[];self.rows={};self.previous=None
    def _profile(self,frame,event,arg):
        if event=='call':
            key=frame.f_code.co_filename+':'+str(frame.f_code.co_firstlineno)+':'+frame.f_code.co_name
            self.stack.append([frame,key,time.perf_counter_ns(),0])
        elif event=='return' and self.stack and self.stack[-1][0] is frame:
            _,key,start,child=self.stack.pop();elapsed=time.perf_counter_ns()-start
            d=self.rows.setdefault(key,dict(calls=0,inclusive_ms=0.,exclusive_ms=0.))
            d['calls']+=1;d['inclusive_ms']+=elapsed/1e6;d['exclusive_ms']+=(elapsed-child)/1e6
            if self.stack:self.stack[-1][3]+=elapsed
    def call(self,fn):
        if sys.getprofile() is not None:raise RuntimeError('existing profiler; do not overwrite')
        begin=time.perf_counter_ns()
        try:
            sys.setprofile(self._profile)
            return fn()
        finally:
            sys.setprofile(None)
            self.total_ms=(time.perf_counter_ns()-begin)/1e6
    def report(self):
        return dict(total_ms=self.total_ms,functions=self.rows,
            scope='Python call tree; inclusive overlaps; C work charged to parent; profiler overhead included')

def source_inventory(directory):
    # Only reads .py source files already on disk; no module execution or MMIO.
    return {p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source=p.read_text(encoding='utf-8'))
            for p in sorted(Path(directory).glob('*.py'))}
