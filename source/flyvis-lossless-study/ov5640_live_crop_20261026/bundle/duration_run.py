"""Bounded wall-clock session and read-only Linux memory admission. No hardware API."""
import math,time
from pathlib import Path
RECORD_BYTES=188416
MIB=1024*1024

def memory_plan(config,meminfo):
    values={}
    for line in meminfo.splitlines():
        a=line.split()
        if a and a[0].rstrip(':') in ('MemAvailable','CmaFree','CmaTotal'):
            if len(a)!=3 or a[2]!='kB':raise ValueError('meminfo units')
            values[a[0].rstrip(':')]=int(a[1])*1024
    if any(k not in values or values[k]<0 for k in ('MemAvailable','CmaFree','CmaTotal')):
        raise RuntimeError('Linux MemAvailable/CmaFree/CmaTotal required before LOAD')
    if values['CmaFree']>values['CmaTotal']:raise RuntimeError('inconsistent CMA counters; no LOAD')
    # A planning ceiling, NOT available contiguous memory. CmaFree can contain
    # movable-page effects and cannot prove allocation success or failure.
    # Existing buffers/fragmentation are resolved only by the one real allocator
    # call after explicit operator authorization, before neural restore/camera.
    budget=min(values['CmaTotal']-32*MIB,values['MemAvailable']-96*MIB)
    slots=config.get('ring_slots',64)
    if type(slots) is not int or not 32<=slots<=64:raise ValueError('ring slots32..64')
    if budget<slots*RECORD_BYTES:raise RuntimeError('insufficient ring allocation budget; no LOAD')
    return dict(schema='line11-ring-memory-plan/v1',slots=slots,ddr_bytes=slots*RECORD_BYTES,
        minimum_period_s=0.0,maximum_start_rate_hz=None,duration_s=config['duration_s'],
        meminfo_bytes=values,estimate_only=True,contiguous_allocation_not_proven=True,
        ring_reuse=True,CmaFree_is_diagnostic_only=True,actual_allocation_attempts=1,
        worker_queue_capacity=32,journal_limit_bytes=32*MIB,speed_limited_by_capacity=False)

def read_memory_plan(config):
    return memory_plan(config,Path('/proc/meminfo').read_text())

class RunWindow:
    def init__(self,config,clock=time.monotonic,sleep=time.sleep):
        self.duration=float(config['duration_s']);self.period=float(config['minimum_period_s']);self.capacity=config['max_steps']
        if not math.isfinite(self.duration) or not 0<self.duration<=60:raise ValueError('duration bound')
        if not math.isfinite(self.period) or self.period!=0:raise ValueError('period bound')
        if type(self.capacity) is not int or not 1<=self.capacity<=4096:raise ValueError('capacity bound')
        self.clock=clock;self.sleep=sleep;self.start=None;self.last=None;self.starts=0;self.stop_reason=None
    def begin(self):
        if self.start is not None:raise RuntimeError('window already started')
        self.start=self.clock()
    def admit_when_ready(self,check,ready):
        # Deadline applies even while storage is stalled. No new capture at expiry.
        while True:
            check()
            if self.clock()-self.start>=self.duration:
                self.stop_reason='DURATION_REACHED';return False
            if ready():return self.admit()
            self.sleep(.001)
    def admit(self):
        if self.start is None or self.stop_reason:raise RuntimeError('window inactive')
        now=self.clock()
        if self.last is not None:
            target=min(self.start+self.duration,self.last+self.period)
            while now<target:
                self.sleep(min(.05,target-now));now=self.clock()
        if now-self.start>=self.duration:
            self.stop_reason='DURATION_REACHED';return False
        if self.starts>=self.capacity:raise RuntimeError('capacity exhausted before duration; no new capture/STEP')
        self.last=now;self.starts+=1;return True
    def receipt(self,completed):
        if self.stop_reason!='DURATION_REACHED' or completed!=self.starts or completed<1:
            raise RuntimeError('incomplete timed run')
        return dict(schema='line11-duration/v1',stop_reason=self.stop_reason,requested_seconds=self.duration,
            elapsed_seconds=self.clock()-self.start,completed_steps=completed,capacity=self.capacity,
            minimum_period_s=self.period,last_frame_start_seconds=self.last-self.start,
            timing_definition='capture loop only; finish admitted frame, then no new frame; excludes setup/persistence/audit',
            synchronous_driver_timeout_guaranteed=False)

def validate_receipt(r,config,count):
    numbers=('requested_seconds','elapsed_seconds','minimum_period_s','last_frame_start_seconds')
    if any(type(r.get(k)) not in (int,float) or not math.isfinite(r[k]) for k in numbers):raise ValueError('duration numbers')
    if (r.get('schema')!='line11-duration/v1' or r.get('stop_reason')!='DURATION_REACHED' or
        r['requested_seconds']!=config['duration_s'] or r['elapsed_seconds']<r['requested_seconds'] or
        not 0<=r['last_frame_start_seconds']<r['requested_seconds'] or
        type(r.get('capacity')) is not int or not 1<=count<=r['capacity']<=config['max_steps'] or
        r.get('completed_steps')!=count or r['minimum_period_s']<config['minimum_period_s'] or
        r['last_frame_start_seconds']+1e-6<(count-1)*r['minimum_period_s']):
        raise ValueError('invalid timed completion')
