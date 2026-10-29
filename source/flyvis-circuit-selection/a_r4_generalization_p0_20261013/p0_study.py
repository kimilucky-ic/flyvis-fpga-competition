"""Frozen-model CPU P0 timing/location generalization; one bounded batch."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
import csv
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE.parent/'a_r4_video_direction_20261013'
sys.path.insert(0,str(source))
import cv2
import numpy as np
from independent_model import IndependentModel
from direction_readout import features,predict,evaluate
from video_io import decode_video,sha,make_video
cv2.setNumThreads(1)


def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def dump(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)


def digest(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def specs():
    rng=np.random.default_rng(2026101304)
    angles=[float(rng.uniform(10,35)+90*i) for i in range(4)]
    groups=[
        ('reference_timing',.5,1.25,None,0,'core'),
        ('start_early',.1,1.25,None,0,'core'),
        ('start_late',.9,1.25,None,0,'core'),
        ('cross_early',.5,.75,None,0,'core'),
        ('cross_late',.5,1.8,None,0,'core'),
        ('local_center',.5,1.25,1.6,0,'core'),
        ('local_minus2',.5,1.25,1.6,-2,'core'),
        ('local_plus2',.5,1.25,1.6,2,'core'),
        ('baseline_overlap',.1,.4,None,0,'boundary_challenge')]
    out=[]
    for group,onset,cross,radius,shift,role in groups:
        for ai,angle in enumerate(angles):
            for polarity in ['ON','OFF']:
                out.append(dict(id=f'{group}_a{ai}_{polarity}',group=group,role=role,kind='motion',
                    angle_deg=angle,polarity=polarity,onset_s=onset,cross_s=cross,speed_hex_s=12,
                    aperture_radius=radius,tangent_offset=shift))
    for shift in [-2,0,2]:
        for polarity in ['ON','OFF']:
            out.append(dict(id=f'static_local_{shift}_{polarity}',group='static',role='control',kind='static',
                angle_deg=angles[1],polarity=polarity,aperture_radius=1.6,tangent_offset=shift))
    for polarity in ['ON','OFF']:
        out.append(dict(id=f'static_full_{polarity}',group='static',role='control',kind='static',
            angle_deg=angles[3],polarity=polarity,aperture_radius=None,tangent_offset=0))
    assert len(out)==80
    return angles,out


def render_frame(spec,t):
    yy,xx=np.mgrid[:224,:224]
    x=(xx-111.5)/6;y=(111.5-yy)/6
    theta=np.deg2rad(spec['angle_deg']);nx,ny=np.cos(theta),np.sin(theta)
    projection=x*nx+y*ny
    if spec['kind']=='motion':
        v=spec['speed_hex_s'];on=spec['onset_s'];cross=spec['cross_s']
        position=v*(on-cross)+v*max(t-on,0)
    else:position=0
    behind=.5*(1+np.tanh((position-projection)*6))
    value=.2+.6*behind if spec['polarity']=='ON' else .8-.6*behind
    if spec['aperture_radius'] is not None:
        # A stationary circular aperture, translated perpendicular to motion.
        # n dot center=0 => time of crossing aperture center stays identical.
        shift=spec['tangent_offset'];cx=-shift*ny;cy=shift*nx
        radial=np.sqrt((x-cx)**2+(y-cy)**2)
        mask=.5*(1+np.tanh((spec['aperture_radius']-radial)*6))
        value=.5+mask*(value-.5)
    return np.rint(value*255).clip(0,255).astype(np.uint8)


def encode(path,spec):
    if path.exists():raise FileExistsError(path)
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'mp4v'),100,(224,224))
    if not writer.isOpened():raise RuntimeError('MP4 writer unavailable')
    try:
        for j in range(200):writer.write(cv2.cvtColor(render_frame(spec,j/100),cv2.COLOR_GRAY2BGR))
    finally:writer.release()


def preflight():
    test=HERE/'preflight';test.mkdir()
    spec=dict(kind='motion',angle_deg=60,polarity='ON',onset_s=.5,cross_s=1.25,speed_hex_s=12,aperture_radius=None,tangent_offset=0)
    encode(test/'new.mp4',spec);make_video(test/'old.mp4',spec)
    sampler=dict(np.load(source/'models/a_r4/sampler.npz'))
    a,_=decode_video(test/'new.mp4',sampler);b,_=decode_video(test/'old.mp4',sampler)
    checks=dict(reference_generator_decoded_input_bitwise=np.array_equal(a,b))
    checks['arbitrary_onset_formula']=abs((12*(.9-1.25)+12*(1.25-.9)))<1e-12
    theta=np.deg2rad(37.1);normal=np.array([np.cos(theta),np.sin(theta)]);center=2*np.array([-np.sin(theta),np.cos(theta)])
    checks['position_shift_orthogonal_to_motion']=abs(float(normal@center))<1e-12
    p=dict(spec,aperture_radius=1.6,tangent_offset=0);q=dict(p,tangent_offset=2)
    checks['local_translation_changes_actual_pixels']=not np.array_equal(render_frame(p,1.25),render_frame(q,1.25))
    static=dict(q,kind='static')
    checks['static_video_no_pixel_motion']=np.array_equal(render_frame(static,.1),render_frame(static,1.8))
    dump(HERE/'PREFLIGHT.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,new_neural_steps=0,GPU=False))
    assert all(checks.values())


def prepare():
    preflight();angles,cases=specs();dump(HERE/'CASES.json',cases)
    pins={str(HERE/'p0_study.py'):sha(HERE/'p0_study.py')}
    for name in ['independent_model.py','video_io.py','direction_readout.py','readout_Full.json','readout_A_R4.json','FROZEN_READOUTS.json','DELIVERY_MANIFEST.json']:
        pins[str(source/name)]=sha(source/name)
    for model in ['Full','a_r4']:
        for name in ['model.npz','sampler.npz','readout_local_ids.npy','readout_type_index.npy']:
            path=source/'models'/model/name;pins[str(path)]=sha(path)
        path=source/'initial'/model/'initial_state.npy';pins[str(path)]=sha(path)
    spec=dict(schema='a_r4-frozen-generalization-P0/v1',date='2026-10-13',status='FROZEN_BEFORE_NEW_NEURAL_RUNS',
        scope='one CPU timing-and-location boundary experiment; no model/readout update, GUI or hardware',
        angle_seed=2026101304,angles_deg=angles,conditions=len(cases),motion=72,static=8,
        source_pins=pins,case_sha=sha(HERE/'CASES.json'),
        input='new real MP4 encode/decode, same frozen sampling 224x224/100fps/2s and5msZOH; same .2/.8 contrast and12 neighbour-spacings/s',
        initialized='reuse exact previously saved own-gray200-step model-specific a0, not old movie states; same a0 across all new conditions',
        fixed_readout='unchanged old ROI56, states[60:100] baseline, states[100:400] response, thresholds and weights',
        primary='Full/shared versus a_r4/shared; a_r4/own always reported as secondary, no automatic profile choice',
        timing='two one-factor onset shifts(.1,.9) with cross1.25; two cross-time shifts(.75,1.8) with onset.5; reference .5/1.25',
        spatial='fixed smooth circular aperture radius1.6 neighbour spacings, background.5; centers translated by0/-2/+2 perpendicular to motion, crossing1.25 unchanged',
        spatial_interpretation='compare shifted aperture with centered aperture; compare centered aperture with full edge separately for shape/context effect; do not attribute all loss to position',
        boundary_challenge='onset.1/cross.4 overlaps frozen baseline; predeclared separate out-of-contract challenge, always report, excluded from core gate',
        metrics='unchanged frozen circular error, hit<=30deg,4sector accuracy,coverage,accepted MAE,p95,reject180penalized MAE,static false motion',
        group_gate=dict(n=8,hit30_min=.75,coverage_min=.9,accepted_MAE_max_deg=20),
        overall_gate='all eight core motion groups pass and static false motion0/8; boundary challenge separate; no claim over untested continuum',
        falsification='failure preserved, no refit/window shift/test selection; if centered aperture fails then shifted failures do not isolate position',
        bounds=dict(CPU_threads=1,wall_s=900,new_storage_GiB_max_estimate=1.2,GPU=0,automatic_retries=0),
        deferred='contrast/noise/expanded slow speed, natural camera video and continuous-window decoder; no FPGA readiness claim')
    dump(HERE/'PREREGISTRATION.json',spec)
    dump(HERE/'FREEZE_RECEIPT.json',dict(prereg_sha=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
    out=HERE/'videos';out.mkdir();records=[]
    for i,case in enumerate(cases):
        path=out/(case['id']+'.mp4');encode(path,case)
        records.append(dict(id=case['id'],sha256=sha(path)))
        if (i+1)%20==0:print(json.dumps(dict(stage='prepare',encoded=i+1,total=80)),flush=True)
    dump(HERE/'VIDEO_MANIFEST.json',records)
    print(json.dumps(dict(status='P0_PREPARED',angles=angles,clips=80,free_bytes=shutil.disk_usage(HERE).free)),flush=True)


def check():
    assert sha(HERE/'PREREGISTRATION.json')==load(HERE/'FREEZE_RECEIPT.json')['prereg_sha']
    proto=load(HERE/'PREREGISTRATION.json');assert sha(HERE/'CASES.json')==proto['case_sha']
    for path,digest in proto['source_pins'].items():assert sha(path)==digest,path
    return proto


def run():
    check();start=time.perf_counter();deadline=start+900
    all_cases=load(HERE/'CASES.json');videos={r['id']:r['sha256'] for r in load(HERE/'VIDEO_MANIFEST.json')}
    models={n:IndependentModel(source/'models'/n/'model.npz') for n in ['Full','a_r4']}
    params={n:dict(sampler=dict(np.load(source/'models'/n/'sampler.npz')),
        roi=np.load(source/'models'/n/'readout_local_ids.npy'),types=np.load(source/'models'/n/'readout_type_index.npy'),
        initial=np.load(source/'initial'/n/'initial_state.npy')) for n in models}
    all_results=[]
    for ci,case in enumerate(all_cases):
        path=HERE/'videos'/(case['id']+'.mp4');assert sha(path)==videos[case['id']]
        inputs={}
        for name,model in models.items():
            t=time.perf_counter();out=HERE/'runs'/name/case['id'];out.mkdir(parents=True)
            p=params[name];frames,metadata=decode_video(path,p['sampler']);inputs[name]=frames
            np.save(out/'input.npy',frames);dump(out/'video_input.json',metadata)
            roi=np.empty((400,56),np.float32);state=p['initial'].copy()
            saved=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(400,model.n)) if name=='a_r4' else None
            maximum=0.
            with (out/'steps.jsonl').open('x',encoding='utf-8') as f:
                for k,frame in enumerate(frames):
                    if time.perf_counter()>deadline:raise TimeoutError('P0 CPU budget')
                    old=digest(state);candidate=model.step(state,frame)
                    maximum=max(maximum,float(abs(candidate).max()))
                    if maximum>100:raise FloatingPointError('stability envelope')
                    f.write(json.dumps(dict(step=k,old=old,input=digest(frame),new=digest(candidate),time=k*.005,next_time=(k+1)*.005))+'\n')
                    state=candidate;roi[k]=state[p['roi']]
                    if saved is not None:saved[k]=state
            if saved is not None:saved.flush()
            np.save(out/'roi.npy',roi);np.save(out/'final_state.npy',state)
            feat=features(roi,p['types']);np.save(out/'features.npy',feat)
            result=dict(model=name,clip=case['id'],actual_CPU=True,steps=400,nodes=model.n,edges=len(model.p['weight']),
                elapsed_s=time.perf_counter()-t,max_abs_state=maximum,GPU=False,external_neural_state_reads=0,complete=True)
            dump(out/'result.json',result);all_results.append(result)
        assert np.array_equal(inputs['a_r4'],inputs['Full'][:,models['a_r4'].p['input_hex_global_index']])
        if (ci+1)%4==0:print(json.dumps(dict(stage='actual_CPU',completed=ci+1,total=80,elapsed_s=time.perf_counter()-start)),flush=True)
    dump(HERE/'EXECUTION.json',dict(status='PASS_ACTUAL_FROZEN_CPU_EXECUTION',clips=80,runs=160,new_neural_steps=64000,
        gray_warmup_recomputed=False,initialization='old model-specific own gray a0 only; not old movie state',wall_s=time.perf_counter()-start,results=all_results))


def stats(rows):
    errors=[r['angle_error_deg'] for r in rows if r['accepted']]
    return dict(n=len(rows),hit30=float(np.mean([r['direction_hit_30'] for r in rows])),
        four_way=float(np.mean([r['four_way_correct'] for r in rows])),coverage=float(np.mean([r['accepted'] for r in rows])),
        accepted_MAE=None if not errors else float(np.mean(errors)),accepted_p95=None if not errors else float(np.percentile(errors,95)),
        penalized_MAE=float(np.mean([r['penalized_error_deg'] for r in rows])))


def analyze():
    check();load(HERE/'EXECUTION.json');rows=[]
    for case in load(HERE/'CASES.json'):
        for branch in ['Full/shared','a_r4/shared','a_r4/own']:
            name,profile=branch.split('/')
            readout=load(source/f"readout_{name if profile=='own' else 'Full'}.json")
            feat=np.load(HERE/'runs'/name/case['id']/'features.npy');prediction=predict(feat,readout)
            row=dict(branch=branch,clip=case['id'],group=case['group'],role=case['role'],kind=case['kind'],
                polarity=case['polarity'],truth_angle_deg=case['angle_deg'])
            row.update(prediction);row.update(evaluate(prediction,case));rows.append(row)
    dump(HERE/'PREDICTIONS.json',rows)
    fields=['branch','clip','group','role','kind','polarity','truth_angle_deg','status','angle_deg','motion_feature_rms','vector_norm','accepted','angle_error_deg','penalized_error_deg','direction_hit_30','four_way_correct','false_motion']
    with (HERE/'PREDICTIONS.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    groups=list(dict.fromkeys(c['group'] for c in load(HERE/'CASES.json') if c['kind']=='motion'))
    summaries=[]
    for branch in ['Full/shared','a_r4/shared','a_r4/own']:
        own=[r for r in rows if r['branch']==branch];groupstats={}
        for group in groups:
            sample=[r for r in own if r['group']==group];s=stats(sample)
            s['pass']=bool(s['hit30']>=.75 and s['coverage']>=.9 and s['accepted_MAE'] is not None and s['accepted_MAE']<=20)
            groupstats[group]=s
        controls=[r for r in own if r['kind']=='static'];fp=sum(r['false_motion'] for r in controls)
        core_pass=all(s['pass'] for g,s in groupstats.items() if g!='baseline_overlap') and fp==0
        summaries.append(dict(branch=branch,groups=groupstats,static_false_motion=f'{fp}/8',core_generalization_pass=core_pass))
    dump(HERE/'SUMMARY.json',dict(status='COMPLETED_FROZEN_P0_BATCH',summaries=summaries,
        no_refit=True,no_window_changes=True,GPU_runs=0,hardware_operations=0,scope='discrete tested timing and aperture levels only, not whole continuous range'))
    print(json.dumps(summaries),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','run','analyze']);args=parser.parse_args()
    try:{'prepare':prepare,'run':run,'analyze':analyze}[args.stage]()
    except Exception as exc:
        dump(HERE/f'FAILURE_{args.stage}_{time.time_ns()}.json',dict(error=repr(exc),stage=args.stage,retry=False));raise
