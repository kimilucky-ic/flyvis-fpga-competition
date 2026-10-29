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
    # CMA is a subset of system memory, NOT additional memory. Keep both reserves.
    available=min(values['CmaFree']-16*MIB,values['MemAvailable']-96*MIB)
    slots=min(config['max_steps'],available//RECORD_BYTES)
    if slots<256:raise RuntimeError('Insufficient memory for bounded60s; candidate_slots=%d; minimum_slots=256; CmaFree_MiB=%.3f (need62); MemAvailable_MiB=%.3f (need142); no LOAD'%(slots,values['CmaFree']/MIB,values['MemAvailable']/MIB))
    period=max(float(config['minimum_period_s']),float(config['duration_s'])/(slots-1))
    return dict(schema='line11-memory-plan/v1',slots=slots,ddr_bytes=slots*RECORD_BYTES,
        minimum_period_s=period,maximum_start_rate_hz=1/period,duration_s=config['duration_s'],
        cma_reserve_bytes=16*MIB,system_reserve_bytes=96*MIB,meminfo_bytes=values,
        estimate_only=True,contiguous_allocation_not_proven=True,ring_reuse=False,
        speed_limited_by_capacity=slots<config['max_steps'])

def read_memory_plan(config):
    import json
    raw=Path('/proc/meminfo').read_text()
    wanted=('MemTotal','MemFree','MemAvailable','CmaTotal','CmaFree')
    selected={}
    for line in raw.splitlines():
        key,sep,value=line.partition(':')
        if sep and key in wanted:selected[key]=value.strip()
    print('LINE11_MEMORY_DIAGNOSTIC',json.dumps(dict(meminfo=selected,
        evidence='READ_ONLY_PROC_MEMINFO_NOT_ALLOCATION_TEST',required_CmaFree_MiB=62,
        required_MemAvailable_MiB=142,hardware_actions=0),sort_keys=True),flush=True)
    return memory_plan(config,raw)

class RunWindow:
    def init__(self,config,clock=time.monotonic,sleep=time.sleep):
        self.duration=float(config['duration_s']);self.period=float(config['minimum_period_s']);self.capacity=config['max_steps']
        if not math.isfinite(self.duration) or not 0<self.duration<=60:raise ValueError('duration bound')
        if not math.isfinite(self.period) or self.period<=0:raise ValueError('period bound')
        if type(self.capacity) is not int or not 1<=self.capacity<=1201:raise ValueError('capacity bound')
        if self.capacity<math.ceil(self.duration/self.period):raise ValueError('capacity cannot cover duration')
        self.clock=clock;self.sleep=sleep;self.start=None;self.last=None;self.starts=0;self.stop_reason=None
    def begin(self):
        if self.start is not None:raise RuntimeError('window already started')
        self.start=self.clock()
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
