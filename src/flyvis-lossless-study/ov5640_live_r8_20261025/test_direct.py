import sys,json,time,statistics,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from ps_input import PsInput
from direct_input import DirectInput,DirectAreaInput
from live_protocol import Store
source=P.parent/'ov5640_live_r2_20261025'
store=Store(source/'pc/records',json.loads((source/'pc/session.json').read_text()))
frames=[];hashes=[]
for k in range(32):
    _,raw,_=store.read(k);frames.append(np.frombuffer(raw,np.uint8).reshape(480,800,3));hashes.append(hashlib.sha256(raw).hexdigest())
def shrink(a,w,h):
    assert 800%w==480%h==0
    x=a.reshape(h,480//h,w,800//w,3).astype(np.uint32)
    n=(480//h)*(800//w)
    return ((x.sum(axis=(1,3))+n//2)//n).astype(np.uint8)
def measure(fn):
    samples=[]
    for _ in range(4):
        t=time.perf_counter_ns();out=fn();samples.append((time.perf_counter_ns()-t)/1e6)
    return out,statistics.median(samples)
old=PsInput(240,400,'BGR');baseline=[];oldtimes=[]
for a in frames:
    low=shrink(a,400,240);v,t=measure(lambda:old.render(low));baseline.append(v);oldtimes.append(t)
rows=[]
for w,h in [(40,24),(80,48),(160,96),(400,240)]:
    mapper=DirectAreaInput(h,w,'BGR');outputs=[];times=[]
    for a in frames:
        low=shrink(a,w,h);v,t=measure(lambda:mapper.render(low));outputs.append(v);times.append(t)
    actual=np.stack(outputs);ref=np.stack(baseline);diff=np.abs(actual-ref)
    delta=np.abs(np.diff(actual,axis=0)-np.diff(ref,axis=0))
    rows.append(dict(width=w,height=h,mapper_cpu_median_ms=statistics.median(times),
        median_speed_ratio=statistics.median(oldtimes)/statistics.median(times),mae=float(diff.mean()),
        p95_abs=float(np.quantile(diff,.95)),max_abs=float(diff.max()),temporal_delta_mae=float(delta.mean()),
        valid_receptors=int(mapper.valid.sum()),distinct_nearest_sites=int(len(set(map(int,mapper.indices[0,mapper.valid])))),
        input_sha256=hashlib.sha256(actual.astype('<f4').tobytes()).hexdigest()))
# Independent scalar implementation of NEW contract, no reuse of vector indices.
def scalar(frame):
    from ps_input import receptor_centers
    h,w=frame.shape[:2];scale=min(417/h,417/w);rh,rw=round(h*scale),round(w*scale);oy,ox=(417-rh)//2,(417-rw)//2
    ans=[];f=np.float32
    for row,col in receptor_centers():
        if not (oy<=row<oy+rh and ox<=col<ox+rw):ans.append(f(.5));continue
        y=np.clip((row-oy+.5)*h/rh-.5,0,h-1);x=np.clip((col-ox+.5)*w/rw-.5,0,w-1)
        y0,x0=int(np.floor(y)),int(np.floor(x));y1,x1=min(y0+1,h-1),min(x0+1,w-1);wx,wy=f(x-x0),f(y-y0)
        def grey(i,j):
            b,g,r=map(int,frame[i,j]);return f((19595*r+38470*g+7471*b+32768)>>16)/f(255)
        top=f(grey(y0,x0)*f(1-wx)+grey(y0,x1)*wx);bot=f(grey(y1,x0)*f(1-wx)+grey(y1,x1)*wx)
        ans.append(f(top*f(1-wy)+bot*wy))
    return np.asarray(ans,dtype=np.float32)
rng=np.random.default_rng(11);cases=0
for w,h in [(40,24),(80,48),(64,64),(160,96)]:
    mapper=DirectInput(h,w,'BGR')
    fixtures=[np.full((h,w,3),v,np.uint8) for v in (0,127,255)]
    fixtures += [rng.integers(0,256,(h,w,3),dtype=np.uint8) for _ in range(3)]
    for frame in fixtures:
        v=mapper.render(frame);r=scalar(frame);assert np.array_equal(v.view('u4'),r.view('u4'));cases+=1
    try:mapper.render(np.zeros((h,w,3),np.float32))
    except ValueError:pass
    else:raise AssertionError('bad type accepted')
same_resolution_max=0.
for w,h in [(40,24),(80,48),(160,96)]:
    direct=DirectAreaInput(h,w,'BGR');legacy=PsInput(h,w,'BGR')
    for a in frames:
        low=shrink(a,w,h);err=float(np.max(np.abs(direct.render(low)-legacy.render(low))))
        same_resolution_max=max(same_resolution_max,err);assert err<3e-6
result=dict(same_resolution_folded_max_abs=same_resolution_max,status='PASS_CPU_DIRECT_GREY_MAPPING_ONLY',source_run=store.final['run_id'],source_frame_sha256=hashes,
    old_r7_mapper_cpu_median_ms=statistics.median(oldtimes),candidates=rows,scalar_bitwise_cases=cases,
    mapping_changed=True,not_arm_timings=True,lowres_pixels='CPU area averages; not OV5640 scaler prediction',
    camera_capture_included=False,board_actions=0,biological_acceptance=False)
(P/'evidence/DIRECT_MAPPING.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
