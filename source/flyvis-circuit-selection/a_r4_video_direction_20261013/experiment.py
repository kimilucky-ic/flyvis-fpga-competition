"""Bounded CPU preparation/design/heldout stages; no GPU or scheduling API."""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import csv
import hashlib
import json
import platform
import shutil
import time
import uuid
from pathlib import Path
import cv2
import numpy as np
from independent_model import IndependentModel
from video_io import sha, geometry, make_video, decode_video
from direction_readout import TYPES, features, fit_readout, predict, evaluate

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'whole_network_pruning_20261013'
MODEL_NAMES=['Full','a_r4']


def dump(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest_array(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def cases():
    result=[]
    for angle in range(0,360,45):
        for polarity in ['ON','OFF']:
            result.append(dict(id=f'D_{polarity}_{angle:03}_v12',split='design',kind='motion',polarity=polarity,angle_deg=angle,speed_hex_s=12))
    for cid, extra in [
        ('D_static_ON_000',dict(kind='static',polarity='ON',angle_deg=0)),
        ('D_static_OFF_090',dict(kind='static',polarity='OFF',angle_deg=90)),
        ('D_gray_02',dict(kind='gray',level=.2)),('D_gray_08',dict(kind='gray',level=.8))]:
        result.append(dict(id=cid,split='design',**extra))
    for speed in [12,6,24]:
        for angle in np.arange(22.5,360,45):
            for polarity in ['ON','OFF']:
                result.append(dict(id=f'T_{polarity}_{angle:05.1f}_v{speed}',split='heldout',kind='motion',polarity=polarity,angle_deg=float(angle),speed_hex_s=speed))
    for angle in [22.5,67.5]:
        for polarity in ['ON','OFF']:
            result.append(dict(id=f'T_static_{polarity}_{angle:04.1f}',split='heldout',kind='static',polarity=polarity,angle_deg=angle))
    result.extend([dict(id='T_gray_05',split='heldout',kind='gray',level=.5),
        dict(id='T_static_offset',split='heldout',kind='static',polarity='ON',angle_deg=112.5,offset_hex=1.5),
        dict(id='T_flash_ON',split='heldout',kind='flash',polarity='ON'),
        dict(id='T_flash_OFF',split='heldout',kind='flash',polarity='OFF')])
    assert len(result)==76
    return result


def prepare():
    if (HERE/'PREREGISTRATION.json').exists():raise FileExistsError('already frozen')
    start=time.perf_counter(); (HERE/'models').mkdir();(HERE/'videos').mkdir()
    for name,old in [('Full','CALIBRATION_FULL'),('a_r4','a_r4')]:
        out=HERE/'models'/name;out.mkdir()
        for filename in ['model.npz','readout_local_ids.npy','node_map.csv']:
            shutil.copyfile(PRIOR/f'models/{old}'/filename,out/filename)
        model=IndependentModel(out/'model.npz')
        rows=list(csv.DictReader((out/'node_map.csv').open(encoding='utf-8-sig')))
        idx=np.load(out/'readout_local_ids.npy')
        type_ids=np.array([TYPES.index(rows[i]['cell_type']) for i in idx],np.int64)
        assert all(np.sum(type_ids==i)==7 for i in range(8))
        np.save(out/'readout_type_index.npy',type_ids)
        us=[];vs=[]
        for pix in range(model.n_pixels):
            nodes=model.p['input_local_index'][model.p['input_pixel_index']==pix]
            coords={(int(rows[i]['u']),int(rows[i]['v'])) for i in nodes}
            assert len(coords)==1
            u,v=coords.pop();us.append(u);vs.append(v)
        x,y=geometry(us,vs)
        np.savez(out/'sampler.npz',x_pixel=x,y_pixel=y,u=np.array(us),v=np.array(vs),
            input_hex_global_index=model.p['input_hex_global_index'])
    specs=cases(); dump(HERE/'CASES.json',specs)
    core=['independent_model.py','video_io.py','direction_readout.py','experiment.py','run_video.py','test_contract.py']
    pinned={f:sha(HERE/f) for f in core}
    pinned.update({str(p.relative_to(HERE)):sha(p) for p in (HERE/'models').rglob('*') if p.is_file()})
    protocol=dict(schema='a_r4-independent-video-local-direction/v1',date='2026-10-13',
        status='FROZEN_BEFORE_ANY_DESIGN_OR_HELDOUT_NEURAL_RUN',
        neural_model='original fp32 expanded parameters and continuous Euler equations; original dynamics not trained',
        source_model_manifest_sha=sha(PRIOR/'DELIVERY_MANIFEST.json'),
        original_checkpoint_sha='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f',
        updater_source_sha=sha(PRIOR/'independent_model.py'),
        CPU_numerical_calibration=load(PRIOR/'CALIBRATION.json'),
        stimulus='new controlled Cartesian single moving edge, genuine mp4v encode/decode; not old official frozen stimulus replay',
        input=dict(size=[224,224],fps=100,duration_s=2,dt_s=.005,steps=400,
            motion_onset_s=.5,center_crossing_s=1.25,edge_levels=[.2,.8],spatial_transition_px=1,
            temporal='causal zero order hold',retina='3x3 grayscale average at original-coordinate-derived centers; pitch6px; Full721/a_r4 subset61',
            angle='0 right,90 up,180 left,270 down in image; no physical degree/s calibration'),
        initialization='same gray .5 and 200 own-state warmup steps per model; model-specific a0 reused identically across clips',
        design=dict(motion_clips=16,angles=list(range(0,360,45)),speed_hex_s=12,polarities=['ON','OFF'],static_clips=4),
        heldout=dict(motion_clips=48,angles=np.arange(22.5,360,45).tolist(),speeds_hex_s=[12,6,24],static_clips=6,uniform_flash_controls=2),
        features='56 central r1 T4/T5 nodes; subtract per-neuron states[60:100] mean; max positive over states[100:400], mean seven positions per type => eight features',
        readout='linear standardized eight-feature ridge to cos/sin; lambda=.1; training16 known-motion clips only; static design4 set abstention',
        motion_gate='RMS>=max(.001,1.25*max_design_static_RMS,.1*min_design_motion_RMS) AND predicted_vector_norm>=.25',
        primary_comparison='one Full-calibrated frozen readout applied to both Full and a_r4',
        preregistered_secondary='a_r4-calibrated readout, same design cases and algorithm; always report, never replace primary after results',
        metrics=dict(primary='direction hit within30degrees, rejected motion counted as miss',
            secondary=['4 cardinal sector accuracy, rejected motion wrong','coverage','accepted MAE and median/p95 circular angle error','all motion MAE with rejected=180deg','static false motion','flash false motion'],
            confidence='vector norm is not probability; no confident motion is not proof of static'),
        engineering_gate=dict(all48_hit30_min=.8,each_speed16_hit30_min=.75,each_polarity24_hit30_min=.75,
            accepted_angle_MAE_max_deg=20,coverage_min=.9,static_false_motion_max=0,
            scope='new small synthetic engineering gate, not biology; flash robustness separately reported; no threshold retuning'),
        heldout_access='generate video after preregistration; neural heldout requires FROZEN_READOUTS.json; fit function sees design features only',
        storage='all a_r4 states; Full central56 traces, own a0 and final45669 states; every step state SHA chain and finiteness; not all Full trajectories',
        limits=dict(GPU_runs=0,CPU_threads=1,each_stage_wall_limit_s=1200,expected_storage_GiB=1.2,automatic_retries=0),
        no_official_decoder=True,no_hardware=True,source_pins=pinned)
    dump(HERE/'PREREGISTRATION.json',protocol)
    dump(HERE/'FREEZE_RECEIPT.json',dict(prereg_sha256=sha(HERE/'PREREGISTRATION.json'),cases_sha256=sha(HERE/'CASES.json'),time_ns=time.time_ns()))
    video_records=[]
    for i,spec in enumerate(specs):
        path=HERE/'videos'/f"{spec['id']}.mp4";make_video(path,spec)
        video_records.append(dict(id=spec['id'],sha256=sha(path),bytes=path.stat().st_size))
        if (i+1)%16==0:print(json.dumps(dict(stage='video_encode',completed=i+1,total=len(specs))),flush=True)
    dump(HERE/'VIDEO_MANIFEST.json',video_records)
    dump(HERE/'PREPARATION.json',dict(status='PASS_PREREG_AND_VIDEO_GENERATION',CPU_only=True,new_neural_steps=0,
        wall_s=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,opencv=cv2.__version__,disk_free=shutil.disk_usage(HERE).free))


def check_frozen():
    receipt=load(HERE/'FREEZE_RECEIPT.json')
    if sha(HERE/'PREREGISTRATION.json')!=receipt['prereg_sha256'] or sha(HERE/'CASES.json')!=receipt['cases_sha256']:raise ValueError('protocol identity changed')
    proto=load(HERE/'PREREGISTRATION.json')
    for name,digest in proto['source_pins'].items():
        if sha(HERE/name)!=digest:raise ValueError(f'frozen source changed: {name}')
    return proto


def make_initial(model,name):
    out=HERE/'initial'/name
    if out.exists():return np.load(out/'initial_state.npy')
    out.mkdir(parents=True);state=model.p['bias'].copy();gray=np.full(model.n_pixels,.5,np.float32)
    history=[]
    for k in range(200):
        state=model.step(state,gray);history.append(state.copy())
    np.save(out/'warmup_states.npy',np.array(history,np.float32));np.save(out/'initial_state.npy',state)
    dump(out/'result.json',dict(steps=200,dt_s=.005,gray=.5,initial_sha256=sha(out/'initial_state.npy'),full_state_replay=False))
    return state


def run_case(name,model,initial,spec,deadline):
    out=HERE/'runs'/name/spec['id'];out.mkdir(parents=True)
    start=time.perf_counter();model_dir=HERE/'models'/name
    with np.load(model_dir/'sampler.npz') as d:sampler={k:d[k] for k in d.files}
    input_values,metadata=decode_video(HERE/'videos'/f"{spec['id']}.mp4",sampler)
    np.save(out/'input.npy',input_values);dump(out/'video_input.json',metadata)
    ids=np.load(model_dir/'readout_local_ids.npy');types=np.load(model_dir/'readout_type_index.npy')
    state=initial.copy();roi=np.empty((400,56),np.float32)
    full_saved=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(400,model.n)) if name=='a_r4' else None
    maximum=0.;uuid_run=str(uuid.uuid4())
    with (out/'steps.jsonl').open('x',encoding='utf-8') as journal:
        for k,frame in enumerate(input_values):
            if time.perf_counter()>deadline:raise TimeoutError('bounded CPU stage exceeded; no retry')
            old_sha=digest_array(state);new=model.step(state,frame)
            maximum=max(maximum,float(abs(new).max()))
            if maximum>100:raise FloatingPointError('finite stability bound exceeded; no commit')
            journal.write(json.dumps(dict(step=k,time_s=k*.005,new_time_s=(k+1)*.005,
                old_sha256=old_sha,input_sha256=digest_array(frame),new_sha256=digest_array(new),commit='COMMITTED'))+'\n')
            state=new;roi[k]=state[ids]
            if full_saved is not None:full_saved[k]=state
    if full_saved is not None:full_saved.flush()
    np.save(out/'roi.npy',roi);np.save(out/'final_state.npy',state)
    feat=features(roi,types);np.save(out/'features.npy',feat)
    result=dict(status='PASS_ACTUAL_CPU_OWN_STATE_ROLLOUT',model=name,clip=spec['id'],run_uuid=uuid_run,
        steps=400,n_nodes=model.n,n_edges=len(model.p['weight']),max_abs_state=maximum,
        wall_s=time.perf_counter()-start,model_sha=sha(model_dir/'model.npz'),initial_sha=sha(HERE/'initial'/name/'initial_state.npy'),
        full_network_future_state_reads=0,external_neural_input=0,GPU=False,features=feat.tolist())
    dump(out/'result.json',result);return result


def run_stage(split):
    check_frozen()
    if split=='heldout':
        lock=load(HERE/'FROZEN_READOUTS.json')
        for n,h in lock['readouts'].items():
            if sha(HERE/n)!=h:raise ValueError('readout changed')
    stage_out=HERE/f'{split.upper()}_EXECUTION.json'
    if stage_out.exists():raise FileExistsError('stage already complete')
    specs=[s for s in load(HERE/'CASES.json') if s['split']==split]
    video_hash={r['id']:r['sha256'] for r in load(HERE/'VIDEO_MANIFEST.json')}
    start=time.perf_counter();deadline=start+1200
    models={name:IndependentModel(HERE/'models'/name/'model.npz') for name in MODEL_NAMES}
    initials={name:make_initial(models[name],name) for name in MODEL_NAMES}
    results=[]
    for i,spec in enumerate(specs):
        if sha(HERE/'videos'/f"{spec['id']}.mp4")!=video_hash[spec['id']]:raise ValueError('video changed')
        for name in MODEL_NAMES:
            row=run_case(name,models[name],initials[name],spec,deadline);results.append(row)
        # This audit is on exogenous pixels only; never supplies any Full state to a_r4.
        f=np.load(HERE/'runs/Full'/spec['id']/'input.npy')
        c=np.load(HERE/'runs/a_r4'/spec['id']/'input.npy')
        assert np.array_equal(c,f[:,models['a_r4'].p['input_hex_global_index']])
        print(json.dumps(dict(stage=split,complete=i+1,total=len(specs),clip=spec['id'],elapsed_s=time.perf_counter()-start)),flush=True)
    dump(stage_out,dict(status='PASS_ACTUAL_CPU_EXECUTION',split=split,clips=len(specs),runs=len(results),
        neural_steps=len(results)*400,warmup_steps=400 if split=='design' else 0,wall_s=time.perf_counter()-start,
        input_subset_bitwise_equal=True,results=results))
    if split=='design':
        records={}
        for name in MODEL_NAMES:
            motion=[s for s in specs if s['kind']=='motion'];static=[s for s in specs if s['kind']!='motion']
            fs=lambda subset:[np.load(HERE/'runs'/name/s['id']/'features.npy') for s in subset]
            readout=fit_readout(fs(motion),[s['angle_deg'] for s in motion],fs(static),dict(model=name,
                design_case_ids=[s['id'] for s in specs],prereg_sha=sha(HERE/'PREREGISTRATION.json')))
            filename=f'readout_{name}.json';dump(HERE/filename,readout);records[filename]=sha(HERE/filename)
        dump(HERE/'FROZEN_READOUTS.json',dict(time_ns=time.time_ns(),status='FROZEN_BEFORE_HELDOUT',
            readouts=records,design_execution_sha256=sha(stage_out)))


def analyze():
    check_frozen();load(HERE/'HELDOUT_EXECUTION.json')
    models=['Full/shared','a_r4/shared','a_r4/own']
    rows=[]
    for spec in load(HERE/'CASES.json'):
        for branch in models:
            name,profile=branch.split('/')
            readout=load(HERE/f"readout_{name if profile=='own' else 'Full'}.json")
            f=np.load(HERE/'runs'/name/spec['id']/'features.npy')
            p=predict(f,readout);e=evaluate(p,spec)
            rows.append(dict(branch=branch,clip=spec['id'],split=spec['split'],kind=spec['kind'],
                polarity=spec.get('polarity'),angle_deg=spec.get('angle_deg'),speed_hex_s=spec.get('speed_hex_s'),**p,**e))
    dump(HERE/'PREDICTIONS.json',rows)
    summaries=[]
    for branch in models:
        test=[r for r in rows if r['branch']==branch and r['split']=='heldout']
        motion=[r for r in test if r['kind']=='motion']
        no_motion=[r for r in test if r['kind'] in ['static','gray']]
        flash=[r for r in test if r['kind']=='flash']
        def metric(rs):
            errors=[r['angle_error_deg'] for r in rs if r['accepted']]
            return dict(n=len(rs),direction_hit_30=float(np.mean([r['direction_hit_30'] for r in rs])),
                four_way_accuracy=float(np.mean([r['four_way_correct'] for r in rs])),coverage=float(np.mean([r['accepted'] for r in rs])),
                accepted_MAE_deg=None if not errors else float(np.mean(errors)),
                accepted_median_deg=None if not errors else float(np.median(errors)),
                accepted_p95_deg=None if not errors else float(np.percentile(errors,95)),
                penalized_MAE_deg=float(np.mean([r['penalized_error_deg'] for r in rs])))
        overall=metric(motion)
        speed={str(s):metric([r for r in motion if r['speed_hex_s']==s]) for s in [12,6,24]}
        polarity={p:metric([r for r in motion if r['polarity']==p]) for p in ['ON','OFF']}
        static_fp=sum(r['false_motion'] for r in no_motion);flash_fp=sum(r['false_motion'] for r in flash)
        gate=bool(overall['direction_hit_30']>=.8 and all(m['direction_hit_30']>=.75 for m in speed.values())
            and all(m['direction_hit_30']>=.75 for m in polarity.values()) and overall['coverage']>=.9
            and overall['accepted_MAE_deg'] is not None and overall['accepted_MAE_deg']<=20 and static_fp==0)
        summaries.append(dict(branch=branch,overall=overall,by_speed=speed,by_polarity=polarity,
            static_false_motion=f'{static_fp}/{len(no_motion)}',flash_false_motion=f'{flash_fp}/{len(flash)}',engineering_gate_pass=gate))
    dump(HERE/'SUMMARY.json',dict(status='COMPLETED_FIXED_BATCH',primary_comparison='Full/shared vs a_r4/shared',
        summaries=summaries,heldout_inputs_not_used_for_fit=True,GPU_runs=0,official_decoder=False,
        interpretation='local two-second single-edge readout; no natural-video, speed estimation, dense optical-flow or hardware proof'))
    print(json.dumps(summaries),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','design','heldout','analyze']);args=parser.parse_args()
    try:
        {'prepare':prepare,'design':lambda:run_stage('design'),'heldout':lambda:run_stage('heldout'),'analyze':analyze}[args.stage]()
    except Exception as exc:
        path=HERE/f'FAILURE_{args.stage}_{time.time_ns()}.json'
        dump(path,dict(stage=args.stage,error=repr(exc),automatic_retry=False));raise
