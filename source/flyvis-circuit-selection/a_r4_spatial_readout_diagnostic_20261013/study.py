"""One preregistered CPU readout diagnostic. Original neural model never fitted."""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import csv
import hashlib
import json
import platform
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'a_r4_video_direction_20261013'
sys.path.insert(0, str(source))
import cv2
import numpy as np
from independent_model import IndependentModel
from video_io import decode_video, sha
from direction_readout import evaluate, predict as old_predict
cv2.setNumThreads(1)
TYPES = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
PROBES = ['legacy8', 'central8', 'central56', 'field8', 'field488']


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def dump(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)


def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def maps():
    def rows(model):
        with (source/'models'/model/'node_map.csv').open(encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))
    ar = [r for r in rows('a_r4') if r['cell_type'] in TYPES]
    ar.sort(key=lambda r: int(r['global_node_index']))
    full = {int(r['global_node_index']):int(r['local_node_index']) for r in rows('Full')}
    gids = np.array([int(r['global_node_index']) for r in ar], np.int64)
    types = np.array([TYPES.index(r['cell_type']) for r in ar], np.int64)
    u = np.array([int(r['u']) for r in ar]); v = np.array([int(r['v']) for r in ar])
    center = np.maximum.reduce([abs(u),abs(v),abs(u+v)]) <= 1
    assert len(ar)==488 and int(center.sum())==56
    assert np.array_equal(np.bincount(types), np.full(8,61))
    out = dict(global_id=gids, type_index=types, u=u, v=v, central_mask=center,
        a_r4=np.array([int(r['local_node_index']) for r in ar],np.int64),
        Full=np.array([full[int(g)] for g in gids],np.int64))
    for name in ['Full','a_r4']:
        assert np.array_equal(out[name][center],np.load(source/'models'/name/'readout_local_ids.npy'))
    return out


def cases():
    out=[]
    def add(split,group,angle,polarity,center,kind='motion',radius=1.6):
        out.append(dict(id=f'{split}_{len(out):03d}',split=split,group=group,
            kind=kind,angle_deg=float(angle),polarity=polarity,center_xy=list(center),
            radius=radius,speed_hex_s=12,onset_s=.5,cross_s=1.25))
    train_positions=[('center',(0,0)),('left',(-2,0)),('right',(2,0))]
    for label,center in train_positions:
        for angle in range(0,360,45):
            for polarity in ['ON','OFF']:
                add('design',label,angle,polarity,center)
        for polarity,angle in [('ON',0),('OFF',90)]:
            add('design','static',angle,polarity,center,'static')
    rng=np.random.default_rng(2026101317)
    a=float(rng.uniform(14,29)); b=float(rng.uniform(105,119))
    angles=[a,b,a+180,b+180]
    test_positions=train_positions+[('up',(0,2)),('down',(0,-2))]
    for ci,(label,center) in enumerate(test_positions):
        for angle in angles:
            for polarity in ['ON','OFF']:
                add('test',label,angle,polarity,center)
        for polarity in ['ON','OFF']:
            add('test','static',17+31*ci,polarity,center,'static')
    for angle in angles:
        for polarity in ['ON','OFF']:
            add('test','wide_edge',angle,polarity,(0,0),radius=None)
            add('test','edge_appearance',angle,polarity,(0,0),kind='appearance')
    assert len(out)==120
    assert sum(c['split']=='design' for c in out)==54
    return angles,out


def frame(c,t):
    yy,xx=np.mgrid[:224,:224]
    x=(xx-111.5)/6-c['center_xy'][0]
    y=(111.5-yy)/6-c['center_xy'][1]
    theta=np.deg2rad(c['angle_deg'])
    projection=x*np.cos(theta)+y*np.sin(theta)
    position=c['speed_hex_s']*(max(t-c['onset_s'],0)+c['onset_s']-c['cross_s']) if c['kind']=='motion' else 0
    behind=.5*(1+np.tanh(6*(position-projection)))
    value=.2+.6*behind if c['polarity']=='ON' else .8-.6*behind
    if c['radius'] is not None:
        mask=.5*(1+np.tanh(6*(c['radius']-np.sqrt(x*x+y*y))))
        value=.5+mask*(value-.5)
    if c['kind']=='appearance' and t<1:
        value=np.full((224,224),.5)
    return np.rint(value*255).clip(0,255).astype(np.uint8)


def encode(p,c):
    if p.exists(): raise FileExistsError(p)
    writer=cv2.VideoWriter(str(p),cv2.VideoWriter_fourcc(*'mp4v'),100,(224,224))
    if not writer.isOpened(): raise RuntimeError('MP4 encoder')
    try:
        for k in range(200): writer.write(cv2.cvtColor(frame(c,k/100),cv2.COLOR_GRAY2BGR))
    finally: writer.release()


def feature_set(activity,mapping):
    if activity.shape!=(400,488) or not np.isfinite(activity).all(): raise ValueError('activity')
    baseline=activity[60:100].astype(np.float64).mean(0)
    peak=np.maximum(activity[100:400].astype(np.float64)-baseline,0).max(0)
    ti=mapping['type_index']; mask=mapping['central_mask']
    central8=np.array([peak[mask&(ti==i)].mean() for i in range(8)])
    return dict(legacy8=central8,central8=central8,central56=peak[mask],
        field8=np.array([peak[ti==i].mean() for i in range(8)]),field488=peak)


def fit(x,angles,static):
    x=np.asarray(x,np.float64); d=x.shape[1]
    mean=x.mean(0); scale=np.maximum(x.std(0),1e-4); z=(x-mean)/scale
    radians=np.deg2rad(angles); target=np.column_stack([np.cos(radians),np.sin(radians)])
    # Algebraic dual ridge for d>n, same fixed lambda=0.1, no hyperparameter search.
    weights=z.T@np.linalg.solve(z@z.T+.1*np.eye(len(z)),target) if d>len(z) else np.linalg.solve(z.T@z+.1*np.eye(d),z.T@target)
    rms=np.sqrt(np.mean(x*x,axis=1)); static_rms=np.sqrt(np.mean(np.asarray(static)**2,axis=1))
    return dict(mean=mean.tolist(),scale=scale.tolist(),weights=weights.tolist(),bias=target.mean(0).tolist(),
        ridge_lambda=.1,motion_rms_threshold=max(.001,1.25*float(static_rms.max()),.1*float(rms.min())),
        vector_norm_threshold=.25,features=d,fit_source='48 Full design motion and 6 Full design static only')


def predict(f,r):
    z=(f-np.array(r['mean']))/np.array(r['scale'])
    vec=z@np.array(r['weights'])+np.array(r['bias']); norm=float(np.linalg.norm(vec))
    rms=float(np.sqrt(np.mean(f*f))); accepted=rms>=r['motion_rms_threshold'] and norm>=r['vector_norm_threshold']
    angle=None if norm<1e-12 else float(np.degrees(np.arctan2(vec[1],vec[0]))%360)
    return dict(status='DIRECTION' if accepted else 'NO_CONFIDENT_MOTION',angle_deg=angle if accepted else None,
        raw_angle_deg=angle,motion_feature_rms=rms,vector_norm=norm)


def validate_frozen():
    p=load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json')==load(HERE/'FREEZE_RECEIPT.json')['prereg_sha256']
    for path,value in p['pins'].items(): assert sha(path)==value,path
    return p


def prepare():
    assert shutil.disk_usage(HERE).free>3*1024**3
    mapping=maps(); np.savez(HERE/'READOUT_MAP.npz',**mapping)
    angles,cs=cases(); dump(HERE/'CASES.json',cs)
    checks={}
    # These checks target stimulus validity and causal update, not result scores.
    sample=next(c for c in cs if c['kind']=='motion')
    checks['static_pixels_constant']=np.array_equal(frame(dict(sample,kind='static'),.2),frame(dict(sample,kind='static'),1.8))
    checks['appearance_no_motion_after_onset']=np.array_equal(frame(dict(sample,kind='appearance'),1.1),frame(dict(sample,kind='appearance'),1.8))
    checks['motion_changes_pixels']=not np.array_equal(frame(sample,1.1),frame(sample,1.4))
    checks['each_position_balanced_all_directions']=all(len([c for c in cs if c['split']==s and c['group']==g and c['kind']=='motion'])==n for s,gs,n in [('design',['center','left','right'],16),('test',['center','left','right','up','down'],8)] for g in gs)
    test_angles=set(c['angle_deg'] for c in cs if c['split']=='test' and c['kind']=='motion')
    design_angles=set(c['angle_deg'] for c in cs if c['split']=='design' and c['kind']=='motion')
    checks['angles_disjoint']=not bool(test_angles&design_angles)
    # No actual original neural updates in preflight.
    tiny=np.zeros((400,488),np.float32); tiny[120:140]=np.linspace(0,.1,488)
    fs=feature_set(tiny,mapping)
    checks['old_feature_semantics_preserved']=np.array_equal(fs['legacy8'],fs['central8']) and fs['central56'].shape==(56,) and fs['field488'].shape==(488,)
    rng=np.random.default_rng(12); z=rng.normal(size=(6,9)); y=rng.normal(size=(6,2))
    checks['dual_ridge_matches_primal']=np.allclose(z.T@np.linalg.solve(z@z.T+.1*np.eye(6),y),np.linalg.solve(z.T@z+.1*np.eye(9),z.T@y),atol=1e-10)
    dump(HERE/'PREFLIGHT.json',dict(checks=checks,status='PASS' if all(checks.values()) else 'FAIL',neural_steps=0,free_bytes=shutil.disk_usage(HERE).free))
    assert all(checks.values())
    pins={str(p):sha(p) for p in [HERE/'study.py',HERE/'CASES.json',HERE/'READOUT_MAP.npz']}
    for name in ['independent_model.py','video_io.py','direction_readout.py','readout_Full.json']:
        p=source/name; pins[str(p)]=sha(p)
    for name in ['Full','a_r4']:
        for file in ['model.npz','sampler.npz','node_map.csv','readout_local_ids.npy','readout_type_index.npy']:
            p=source/'models'/name/file; pins[str(p)]=sha(p)
        p=source/'initial'/name/'initial_state.npy'; pins[str(p)]=sha(p)
    dump(HERE/'PREREGISTRATION.json',dict(schema='spatial-readout-diagnostic/v1',date='2026-10-13',
        question='Does frozen network activity contain local motion direction recoverable by a prespecified new readout?',
        neural_model='Original parameters and continuous float32 Euler dt=.005 unchanged; candidate own previous state only; no deleted-state inputs',
        evidence='CPU scientific diagnostic, not biological capability proof, official optical flow, continuous camera or FPGA',
        clips=120,design=dict(motion=48,static=6,angles=list(range(0,360,45)),positions=[[0,0],[-2,0],[2,0]]),
        test=dict(seed=2026101317,angles=angles,local_motion=40,wide_edge=8,static=10,appearance=8,
            positions=[[0,0],[-2,0],[2,0],[0,2],[0,-2]],new_positions=['up','down']),
        stimulus='Actual MP4 224x224/100fps/2s, stationary radius1.6 window with local translating ON/OFF edge; .2/.8, speed12, onset.5, center crossing1.25; screen-fixed centers independent of direction',
        readouts=dict(legacy8='original frozen Full readout',central8='same eight central56 pooled features, new design-only calibration',
            central56='unpooled same56 central neurons',field8='488 neurons in61 positions, mean peaks per eight types',field488='same488 individually retained peaks; PRIMARY diagnostic'),
        fitting='Full design only; same fitted readout applied to Full and a_r4. Fixed standardized ridge .1. No fit on oldP0 or newtest. Initial parameters only are reused from old experiment; no old movie states.',
        timing='baseline output states[60:100], positive peak over[100:400], unchanged; no temporal optimization',
        rejection='design-derived max(.001,1.25*staticRMSmax,.1*motionRMSmin) and norm>=.25; norm not calibrated confidence',
        primary_gate='field488 all five local position groups hit>=.75, coverage>=.9, acceptedMAE<=20deg; staticFP=0/10 and appearanceFP=0/8; never switch winning probe',
        interpretation='central8 versus legacy tests calibration shift; central56 versus central8 tests central pooling; field8 versus central8 tests spatial coverage with same8 dimensions; field488 versus field8 tests spatial unpooling. Success establishes decodability for this split, failure does not prove absent information or biological inability.',
        diagnostics='Opposite-pair field488 feature distance and correlation; Full/a_r4 local trajectory relative L2. No binary biological DSI claim.',
        metrics='hit<=30 degrees including rejects as misses, coverage, accepted MAE, rejected180 penalty, foursector accuracy, perposition and polarity; all failures saved',
        budget=dict(CPU_threads=1,wall_s_per_campaign=900,total_neural_steps=96000,new_storage_GiB_estimate_max=2,GPU=0,retries=0),pins=pins))
    dump(HERE/'FREEZE_RECEIPT.json',dict(prereg_sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
    out=HERE/'videos';out.mkdir(); records=[]
    for i,c in enumerate(cs):
        p=out/(c['id']+'.mp4');encode(p,c); records.append(dict(id=c['id'],sha256=sha(p)))
        if (i+1)%20==0: print(json.dumps(dict(stage='encode',done=i+1,total=120)),flush=True)
    dump(HERE/'VIDEO_MANIFEST.json',records)
    print(json.dumps(dict(stage='PREPARED',angles=angles,clips=len(cs))),flush=True)


def run_split(split):
    validate_frozen()
    if split=='test':
        receipt=load(HERE/'READOUT_FREEZE.json')
        assert sha(HERE/'READOUTS.json')==receipt['sha256']
    out_root=HERE/'runs'/split
    if out_root.exists(): raise FileExistsError('No automatic rerun or overwrite')
    start=time.perf_counter(); mapping=dict(np.load(HERE/'READOUT_MAP.npz'))
    models={name:IndependentModel(source/'models'/name/'model.npz') for name in ['Full','a_r4']}
    params={name:dict(sampler=dict(np.load(source/'models'/name/'sampler.npz')),
        initial=np.load(source/'initial'/name/'initial_state.npy')) for name in models}
    manifest={r['id']:r['sha256'] for r in load(HERE/'VIDEO_MANIFEST.json')}
    cs=[c for c in load(HERE/'CASES.json') if c['split']==split]; results=[]
    for ci,c in enumerate(cs):
        path=HERE/'videos'/(c['id']+'.mp4'); assert sha(path)==manifest[c['id']]
        inputs={}
        for name,model in models.items():
            tick=time.perf_counter(); out=out_root/name/c['id'];out.mkdir(parents=True)
            pixels,meta=decode_video(path,params[name]['sampler']); inputs[name]=pixels
            np.save(out/'input.npy',pixels);dump(out/'input_meta.json',meta)
            state=params[name]['initial'].copy(); activity=np.empty((400,488),np.float32)
            saved=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(400,model.n)) if name=='a_r4' else None
            maximum=0
            with (out/'steps.jsonl').open('x',encoding='utf-8') as stream:
                for k,p in enumerate(pixels):
                    if time.perf_counter()-start>900: raise TimeoutError('bounded campaign')
                    old=digest(state); candidate=model.step(state,p)
                    maximum=max(maximum,float(abs(candidate).max()))
                    if maximum>100: raise FloatingPointError('stability envelope')
                    stream.write(json.dumps(dict(k=k,t_old=k*.005,t_new=(k+1)*.005,old=old,input=digest(p),new=digest(candidate)))+'\n')
                    state=candidate;activity[k]=state[mapping[name]]
                    if saved is not None: saved[k]=state
            if saved is not None: saved.flush()
            np.save(out/'activity488.npy',activity);np.save(out/'final_state.npy',state)
            np.savez(out/'features.npz',**feature_set(activity,mapping))
            rec=dict(model=name,case=c['id'],steps=400,nodes=model.n,edges=len(model.p['weight']),
                wall_s=time.perf_counter()-tick,max_abs_state=maximum,actual_CPU=True,external_neural_state_reads=0)
            dump(out/'RESULT.json',rec);results.append(rec)
        assert np.array_equal(inputs['a_r4'],inputs['Full'][:,models['a_r4'].p['input_hex_global_index']])
        if (ci+1)%4==0: print(json.dumps(dict(stage=split,done=ci+1,total=len(cs),wall_s=time.perf_counter()-start)),flush=True)
    dump(HERE/f'EXECUTION_{split}.json',dict(status='PASS_ACTUAL_CPU',split=split,clips=len(cs),runs=len(results),
        steps=400*len(results),wall_s=time.perf_counter()-start,time_ns=time.time_ns(),results=results,
        python=sys.version,numpy=np.__version__,opencv=cv2.__version__,platform=platform.platform(),GPU=False))


def calibrate():
    validate_frozen();load(HERE/'EXECUTION_design.json')
    assert not (HERE/'runs/test').exists(), 'test must not run before readout freeze'
    cs=[c for c in load(HERE/'CASES.json') if c['split']=='design']
    readouts={'legacy8':load(source/'readout_Full.json')}
    for probe in PROBES[1:]:
        moving=[];static=[];angles=[]
        for c in cs:
            feature=np.load(HERE/'runs/design/Full'/c['id']/'features.npz')[probe]
            if c['kind']=='motion':moving.append(feature);angles.append(c['angle_deg'])
            else:static.append(feature)
        readouts[probe]=fit(moving,angles,static)
    dump(HERE/'READOUTS.json',readouts)
    dump(HERE/'READOUT_FREEZE.json',dict(sha256=sha(HERE/'READOUTS.json'),time_ns=time.time_ns(),
        design_execution_sha=sha(HERE/'EXECUTION_design.json'),test_has_started=False))
    print(json.dumps(dict(stage='READOUT_FROZEN',dimensions={p:len(r['mean']) for p,r in readouts.items()})),flush=True)


def stats(rows):
    errors=[r['angle_error_deg'] for r in rows if r['accepted']]
    return dict(n=len(rows),hits=sum(r['direction_hit_30'] for r in rows),hit30=float(np.mean([r['direction_hit_30'] for r in rows])),
        accepted=sum(r['accepted'] for r in rows),coverage=float(np.mean([r['accepted'] for r in rows])),
        MAE=None if not errors else float(np.mean(errors)),penalized_MAE=float(np.mean([r['penalized_error_deg'] for r in rows])),
        four_way_correct=sum(r['four_way_correct'] for r in rows))


def analyze():
    validate_frozen();load(HERE/'EXECUTION_test.json')
    assert sha(HERE/'READOUTS.json')==load(HERE/'READOUT_FREEZE.json')['sha256']
    readouts=load(HERE/'READOUTS.json');cs=[c for c in load(HERE/'CASES.json') if c['split']=='test'];rows=[]
    for c in cs:
        for name in ['Full','a_r4']:
            fs=np.load(HERE/'runs/test'/name/c['id']/'features.npz')
            for probe in PROBES:
                pred=old_predict(fs[probe],readouts[probe]) if probe=='legacy8' else predict(fs[probe],readouts[probe])
                row=dict(model=name,probe=probe,case=c['id'],group=c['group'],kind=c['kind'],polarity=c['polarity'],truth_angle=c['angle_deg'])
                row.update(pred);row.update(evaluate(pred,c));rows.append(row)
    dump(HERE/'PREDICTIONS.json',rows)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (HERE/'PREDICTIONS.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    result=[]
    for name in ['Full','a_r4']:
        for probe in PROBES:
            own=[r for r in rows if r['model']==name and r['probe']==probe]
            groups={g:stats([r for r in own if r['group']==g]) for g in ['center','left','right','up','down','wide_edge']}
            for g,s in groups.items():s['pass']=bool(s['hit30']>=.75 and s['coverage']>=.9 and s['MAE'] is not None and s['MAE']<=20)
            local=[r for r in own if r['group'] in ['center','left','right','up','down']]
            static_fp=sum(r['false_motion'] for r in own if r['kind']=='static')
            appearance_fp=sum(r['false_motion'] for r in own if r['kind']=='appearance')
            result.append(dict(model=name,probe=probe,groups=groups,local=stats(local),
                by_polarity={p:stats([r for r in local if r['polarity']==p]) for p in ['ON','OFF']},
                static_fp=static_fp,static_n=10,appearance_fp=appearance_fp,appearance_n=8,
                gate_pass=all(groups[g]['pass'] for g in ['center','left','right','up','down']) and static_fp==0 and appearance_fp==0))
    dump(HERE/'SUMMARY.json',dict(status='COMPLETE_FIXED_DIAGNOSTIC',primary='field488',results=result))
    dump(HERE/'FAILURES.json',[r for r in rows if (r['kind']=='motion' and not r['direction_hit_30']) or (r['kind']!='motion' and r['false_motion'])])
    opposite=[]; trajectory=[]
    for c in cs:
        if c['kind']!='motion':continue
        full=np.load(HERE/'runs/test/Full'/c['id']/'activity488.npy').astype(np.float64)
        ar=np.load(HERE/'runs/test/a_r4'/c['id']/'activity488.npy').astype(np.float64)
        full_delta=full[100:]-full[60:100].mean(0); ar_delta=ar[100:]-ar[60:100].mean(0)
        trajectory.append(dict(case=c['id'],group=c['group'],relative_L2=float(np.linalg.norm(ar_delta-full_delta)/max(np.linalg.norm(full_delta),1e-12)),max_abs_difference=float(abs(ar-full).max())))
        if c['angle_deg']>=180:continue
        match=next(x for x in cs if x['kind']=='motion' and x['group']==c['group'] and x['polarity']==c['polarity'] and abs(x['angle_deg']-c['angle_deg']-180)<1e-9)
        for name in ['Full','a_r4']:
            a=np.load(HERE/'runs/test'/name/c['id']/'features.npz')['field488']
            b=np.load(HERE/'runs/test'/name/match['id']/'features.npz')['field488']
            relative=float(np.linalg.norm(a-b)/max((np.linalg.norm(a)+np.linalg.norm(b))/2,1e-12))
            correlation=float(np.corrcoef(a,b)[0,1]) if min(a.std(),b.std())>0 else None
            opposite.append(dict(model=name,case=c['id'],opposite=match['id'],group=c['group'],polarity=c['polarity'],relative_distance=relative,correlation=correlation))
    dump(HERE/'SIGNAL_DIAGNOSTICS.json',dict(opposite_pairs=opposite,trajectory=trajectory,
        interpretation='Different deterministic responses do not by themselves establish robust direction decoding; no biological DSI claim'))
    print(json.dumps([dict(model=r['model'],probe=r['probe'],local=r['local'],static_fp=r['static_fp'],appearance_fp=r['appearance_fp'],gate=r['gate_pass']) for r in result]),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','design','calibrate','test','analyze']);a=ap.parse_args()
    try:
        if a.stage in ['design','test']:run_split(a.stage)
        else:globals()[a.stage]()
    except Exception as exc:
        dump(HERE/f'FAILURE_{a.stage}_{time.time_ns()}.json',dict(error=repr(exc),retry=False));raise
