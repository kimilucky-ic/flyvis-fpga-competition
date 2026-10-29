"""Freeze science before any new neural inference; real200fps MP4 ->721 inputs."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
from pathlib import Path
import csv,hashlib,json,shutil,time
import numpy as np
import cv2
import psutil
from readout import tests
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];FLY=ROOT.parent/'fly'
BUNDLE=HERE.parent/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,d):
    with (HERE/name).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False)

def trajectory(c):
    t=np.arange(1000)*.005
    s=np.where(t<1,-c['halfspan'],np.where(t<2.5,-c['halfspan']+2*c['halfspan']*(t-1)/1.5,
        np.where(t<4,c['halfspan']-2*c['halfspan']*(t-2.5)/1.5,-c['halfspan'])))
    theta=np.deg2rad(c['angle']);direction=np.array([np.cos(theta),np.sin(theta)])
    if c['kind']!='motion':s[:]=0
    pos=np.array(c['center'])[None]+s[:,None]*direction
    vel=np.zeros_like(pos);vel[200:500]=direction*2*c['halfspan']/1.5;vel[500:800]=-direction*2*c['halfspan']/1.5
    if c['kind']!='motion':vel[:]=0
    return pos,vel

def main():
    cv2.setNumThreads(1)
    dump('RESOURCE_CHECK.json',dict(free_disk_bytes=shutil.disk_usage(HERE).free,
        available_RAM_bytes=psutil.virtual_memory().available,GPU=False))
    assert shutil.disk_usage(HERE).free>4*2**30 and psutil.virtual_memory().available>2*2**30
    m=np.load(HERE.parent/'cnn_t4t5_replacement_20261016/mapping.npz')
    uv=m['grid_uv'];xy=np.stack([np.sqrt(3)/2*uv[1],-(uv[0]+uv[1]/2)],1)
    assert xy.shape==(721,2)
    roi=np.flatnonzero(np.maximum.reduce([abs(uv[0]),abs(uv[1]),abs(uv[0]+uv[1])])<=10)
    assert len(roi)==331
    distances=np.linalg.norm(xy[:,None]-xy[None],axis=2)
    neighbors=[np.flatnonzero(np.isclose(distances[i],1,atol=1e-8)) for i in range(721)]
    unit=tests(xy,neighbors,roi);dump('READOUT_TESTS.json',unit)
    np.savez(HERE/'GRID.npz',uv=uv,xy=xy,roi=roi)
    cases=[dict(id='CAL_BLANK',kind='blank',center=[0,0],angle=0,halfspan=0),
        dict(id='CAL_STATIC_DOT',kind='static',center=[0,0],angle=0,halfspan=0),
        dict(id='HORIZONTAL',kind='motion',center=[0,0],angle=0,halfspan=6),
        dict(id='VERTICAL_OFFSET',kind='motion',center=[4,0],angle=90,halfspan=6),
        dict(id='DIAGONAL_OFFSET',kind='motion',center=[-3,0],angle=60,halfspan=6),
        dict(id='HORIZONTAL_SLOW',kind='motion',center=[0,0],angle=0,halfspan=4.5)]
    paths=[HERE/'prepare.py',HERE/'readout.py',HERE/'run_cpu.py',HERE/'analyze.py',
        HERE/'GRID.npz',BUNDLE/'initial_state_full.npy',BUNDLE/'nodes_full.csv',
        FLY/'data_cpu/results/flow/0000/000/chkpts/chkpt_00000',
        FLY/'upstream/flyvis/flyvis/network/network.py',FLY/'upstream/flyvis/flyvis/network/dynamics.py',
        FLY/'upstream/flyvis/flyvis/task/decoder.py']
    pins={str(p.relative_to(ROOT.parent)).replace('\\','/') :sha(p) for p in paths}
    prereg=dict(schema='flow-only-single-dot-tracking-CPU-pilot/v1',time_ns=time.time_ns(),
        goal='Determine whether original full FlyVis optical flow supports this fixed simple downstream tracker; not intrinsic object identity or living fly proof.',
        nodes=45669,edges=1513231,dt=.005,steps_per_case=1000,FP32=True,decoder='original DecoderGAVP eval no training',
        pins=pins,cases=cases,video=dict(size=224,fps=200,frames=1000,pitch_px=6,radius_hex=2,
            foreground=0,background=1,sampling='3x3 grayscale mean at721 original coordinates, one decoded frame per5ms',
            timeline='static0..1s, forward1..2.5s, reverse2.5..4s, stopped4..5s; geometry above'),
        readout=dict(api='only flow, xy, neighbors, fixed ROI331, scalar threshold; no images, stimulus pixels, GT coordinates or type labels',
            saliency='norm(flow[k]-flow[k-20]); causal EMA tau50ms; sample each10 steps',
            threshold='max(1e-5,3*99.9percentile of both control saliency values on ROI, k200..999)',
            components='6-neighbor, >=3 nodes, cut=max(threshold,.5*ROI_peak); largest energy initially',
            state='centroid + alpha.8, velocity EMA.2, association gate4hex, reset after4misses; predictions during misses not counted as detections',
            columns=['step_id','valid','x','y','raw_x','raw_y','component_mass','component_size']),
        metrics=dict(primary='all60 readouts with input step in[200,800), including onset/reversal',
            secondary='settled[240,490) and[540,790); stopped[840,1000)',
            success_per_motion='coverage>=.9 AND fraction(all primary frames with valid error<=3hex)>=.8 AND valid median error<=2hex',
            controls='reported calibration false detection fraction<=.05 on k200..999; not independent specificity estimate',
            evidence_gate='all4motion pass, controls pass, mean within3 success exceeds seeded spatial-permutation null and fixed-origin baseline by>=.20 each',
            missed_error='within3 denominator includes misses; separately report MAE valid only and20hex miss penalty',
            directions='secondary raw decoded flow weighted at detected component/position; not a direction recognition gate or calibrated physical velocity'),
        controls=dict(spatial_permutation_seed=2026101804,constant_origin=[0,0],zero_flow='must abstain'),
        budgets=dict(CPU_inference_seconds=240,max_cases=6,GPU=False,board=False,neural_retries=0),
        limits='one radius, one highcontrast disk, white static background; no identity/multiobject/occlusion/natural scenes; failures retained, no retuning')
    dump('PREREGISTRATION.json',prereg);dump('FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
    (HERE/'videos').mkdir();(HERE/'inputs').mkdir();(HERE/'truth').mkdir()
    xs=np.rint(111.5+6*xy[:,0]).astype(int);ys=np.rint(111.5-6*xy[:,1]).astype(int)
    yy,xx=np.mgrid[:224,:224];x=(xx-111.5)/6;y=(111.5-yy)/6
    records=[]
    for c in cases:
        pos,vel=trajectory(c);p=HERE/'videos'/(c['id']+'.mp4')
        writer=cv2.VideoWriter(str(p),cv2.VideoWriter_fourcc(*'mp4v'),200,(224,224));assert writer.isOpened()
        try:
            for k in range(1000):
                bright=np.ones_like(x) if c['kind']=='blank' else .5*(1+np.tanh(6*(np.hypot(x-pos[k,0],y-pos[k,1])-2)))
                gray=np.rint(bright*255).clip(0,255).astype('uint8');writer.write(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR))
        finally:writer.release()
        cap=cv2.VideoCapture(str(p));assert cap.isOpened() and abs(cap.get(cv2.CAP_PROP_FPS)-200)<1e-6
        values=[]
        try:
            while True:
                ok,frame=cap.read()
                if not ok:break
                assert frame.shape==(224,224,3)
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                patch=np.stack([gray[ys+dy,xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
                values.append(patch.mean(0,dtype=np.float64).astype('float32')/np.float32(255))
        finally:cap.release()
        z=np.asarray(values);assert z.shape==(1000,721) and np.isfinite(z).all()
        if c['kind']=='blank':assert z.min()>.95
        static_jitter=float(np.sqrt(np.mean((z[200:].astype(float)-z[200:].mean(0))**2))) if c['kind']!='motion' else None
        np.save(HERE/'inputs'/(c['id']+'.npy'),z)
        np.savez(HERE/'truth'/(c['id']+'.npz'),position=pos,velocity=vel,input_t=np.arange(1000)*.005,output_t=(np.arange(1000)+1)*.005)
        records.append(dict(id=c['id'],video_sha256=sha(p),input_sha256=sha(HERE/'inputs'/(c['id']+'.npy')),
            truth_sha256=sha(HERE/'truth'/(c['id']+'.npz')),decoded_frames=len(z),
            rendered_static=c['kind']!='motion',decoded_static_input_jitter_RMS=static_jitter))
        print('INPUT_DONE',c['id'],flush=True)
    dump('INPUT_MANIFEST.json',records)
    print('FROZEN',sha(HERE/'PREREGISTRATION.json'),flush=True)

if __name__=='__main__':main()
