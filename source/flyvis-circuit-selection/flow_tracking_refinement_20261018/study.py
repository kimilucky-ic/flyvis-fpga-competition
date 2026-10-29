"""Old-data development -> immutable freeze -> genuinely new videos -> scoring."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,shutil,time
import numpy as np
import cv2
import psutil
from tracker import run,tests
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'flow_tracking_pilot_20261018'
ROOT=HERE.parents[1];PROJECT=ROOT.parent

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False)
def grid():
    g=np.load(OLD/'GRID.npz');return g['xy'],g['roi']
def calibration():return dict(np.load(HERE/'CALIBRATION.npz'))

def score(pred,truth,mask):
    valid=(pred[:,1]>0)&np.isfinite(pred[:,2:4]).all(1)
    k=pred[:,0].astype(int);error=np.linalg.norm(pred[:,2:4]-truth[k],axis=1)
    good=mask&valid;count=int(mask.sum());assert count>0
    e=error[good]
    coverage=float(good.sum()/count);hit=float(np.sum(good&(error<=3))/count)
    median=float(np.median(e)) if len(e) else None
    return dict(n=count,valid=int(good.sum()),coverage=coverage,within3_fraction=hit,
        median_valid_error_hex=median,MAE_valid_hex=float(e.mean()) if len(e) else None,
        p95_valid_error_hex=float(np.percentile(e,95)) if len(e) else None,
        miss_penalized_MAE_hex=float(np.where(valid,error,20)[mask].mean()),
        pass_gate=bool(coverage>=.9 and hit>=.8 and median is not None and median<=2))

def permuted_cal(cal,perm):
    out={k:v.copy() for k,v in cal.items()}
    out['background_prefix']=out['background_prefix'][:,:,perm]
    out['background_steady']=out['background_steady'][:,perm]
    return out

def develop():
    xy,roi=grid();oldmanifest=load(OLD/'DELIVERY_MANIFEST.json')
    pins={r['path'].replace('\\','/'):r['sha256'] for r in oldmanifest['files']}
    for name in ['CAL_BLANK','CAL_STATIC_DOT','HORIZONTAL','VERTICAL_OFFSET','DIAGONAL_OFFSET','HORIZONTAL_SLOW']:
        assert sha(OLD/'runs'/name/'flow.npy')==pins['runs/'+name+'/flow.npy']
    blank=np.load(OLD/'runs/CAL_BLANK/flow.npy')
    prefix=blank[:200].copy();steady=blank[800:].astype(float).mean(0).astype('float32')
    residual=np.linalg.norm(blank[200:].astype(float)-steady,axis=1)
    cal=dict(background_prefix=prefix,background_steady=steady,
        motion_threshold=np.array(load(OLD/'CALIBRATION.json')['threshold']),
        location_floor=np.array(max(1e-5,float(np.quantile(residual[:,roi],.999))*3)))
    np.savez(HERE/'CALIBRATION.npz',**cal)
    dump(HERE/'READOUT_TESTS.json',tests(np.load(OLD/'runs/HORIZONTAL/flow.npy'),xy,roi,cal))
    (HERE/'development').mkdir();rows=[];controls=[];steps=np.arange(9,1000,10);mask=(steps>=200)&(steps<800)
    perm=np.random.default_rng(2026101804).permutation(721)
    for c in load(OLD/'PREREGISTRATION.json')['cases']:
        f=np.load(OLD/'runs'/c['id']/'flow.npy');pred,meta=run(f,xy,roi,cal)
        np.save(HERE/'development'/(c['id']+'.npy'),pred)
        if c['kind']=='motion':
            truth=np.load(OLD/'truth'/(c['id']+'.npz'))['position'];m=score(pred,truth,mask)
            null,_=run(f[:,:,perm],xy,roi,permuted_cal(cal,perm))
            nullscore=score(null,truth,mask)
            const=float(np.mean(np.linalg.norm(truth[steps[mask]],axis=1)<=3))
            rows.append(dict(id=c['id'],primary=m,spatial_null=nullscore,
                constant_origin_fraction=const,meta=meta))
        else:
            rate=float(pred[steps>=200,1].mean());controls.append(dict(id=c['id'],false_detection_fraction=rate,pass_gate=rate<=.05))
    normal=float(np.mean([r['primary']['within3_fraction'] for r in rows]));null=float(np.mean([r['spatial_null']['within3_fraction'] for r in rows]));constant=float(np.mean([r['constant_origin_fraction'] for r in rows]))
    passed=all(r['primary']['pass_gate'] for r in rows) and all(r['pass_gate'] for r in controls) and normal-null>=.2 and normal-constant>=.2
    dump(HERE/'DEVELOPMENT.json',dict(status='PASS_OLD_DATA_DEVELOPMENT_GATE' if passed else 'FAIL_OLD_DATA_DEVELOPMENT_GATE',
        pass_gate=bool(passed),cases=rows,controls=controls,normal=normal,null=null,constant=constant,
        original_old_study_gate_unchanged='FAIL_FIXED_SIMPLE_FLOW_TRACKER',neural_steps=0,GPU=False,
        calibration_source='old known white background; no current/future target reference states',
        tracker_sha256=sha(HERE/'tracker.py'),calibration_sha256=sha(HERE/'CALIBRATION.npz')))
    print(json.dumps(dict(pass_gate=passed,cases=rows,controls=controls),indent=2))

def new_cases():
    cases=[]
    for i,(angle,speed,onset) in enumerate(zip([20,50,80,110,140,170],[3,5,7,10,4.5,9],[.85,1.10,1.25,.95,1.35,1.05])):
        theta=np.deg2rad(angle);direction=np.array([np.cos(theta),np.sin(theta)])
        perp=np.array([-direction[1],direction[0]])
        center=perp*(3.5 if i%2==0 else -3.5)+direction*(.4 if i%2==0 else -.4)
        leg=min(1.35,8/speed)
        cases.append(dict(id=f'NEW_DIR{angle}_V{speed:g}',kind='motion',angle=angle,speed=speed,
            center=center.tolist(),onset=onset,turn=onset+leg,stop=onset+2*leg,halfspan=speed*leg/2))
    for name,center in [('NEW_STATIC_A',[2.3,3.1]),('NEW_STATIC_B',[-3.8,1.4]),('NEW_STATIC_C',[3.2,-3.4])]:
        cases.append(dict(id=name,kind='static',center=center,angle=0,speed=0,onset=None,turn=None,stop=None,halfspan=0))
    cases.append(dict(id='WHITE_CONTROL',kind='blank',center=[0,0],angle=0,speed=0,onset=None,turn=None,stop=None,halfspan=0))
    return cases

def trajectory(case):
    t=np.arange(1000)*.005
    if case['kind']=='motion':
        s=np.where(t<case['onset'],-case['halfspan'],np.where(t<case['turn'],
            -case['halfspan']+case['speed']*(t-case['onset']),np.where(t<case['stop'],
            case['halfspan']-case['speed']*(t-case['turn']),-case['halfspan'])))
    else:s=np.zeros(1000)
    a=np.deg2rad(case['angle']);direction=np.array([np.cos(a),np.sin(a)])
    pos=np.asarray(case['center'])[None]+s[:,None]*direction;vel=np.zeros_like(pos)
    if case['kind']=='motion':
        vel[(t>=case['onset'])&(t<case['turn'])]=case['speed']*direction
        vel[(t>=case['turn'])&(t<case['stop'])]=-case['speed']*direction
    return pos,vel

def freeze_prepare():
    dev=load(HERE/'DEVELOPMENT.json');assert dev['pass_gate'],'OLD_GATE_FAILED_DO_NOT_LAUNCH_NEW_TEST'
    assert sha(HERE/'tracker.py')==dev['tracker_sha256'] and sha(HERE/'CALIBRATION.npz')==dev['calibration_sha256']
    resource=dict(free_disk_bytes=shutil.disk_usage(HERE).free,available_RAM_bytes=psutil.virtual_memory().available,
        stage='streaming224px_video_preparation_not_neural_worker',minimum_RAM_bytes=2**30,
        process_RSS_bytes=psutil.Process().memory_info().rss,
        bounded_buffers='one224x224 frame plus grids and one1000x721 float32 input array; frames never accumulated',
        neural_worker_minimum_RAM_bytes=2*2**30)
    dump(HERE/'RESOURCE_CHECK.json',resource)
    assert resource['free_disk_bytes']>4*2**30 and resource['available_RAM_bytes']>2**30
    files=[HERE/'tracker.py',HERE/'study.py',HERE/'run_cpu.py',HERE/'CALIBRATION.npz',OLD/'GRID.npz']
    oldpr=load(OLD/'PREREGISTRATION.json')
    for rel in oldpr['pins']:
        if rel.startswith('fly/') or 'input_bundle/' in rel:files.append(PROJECT/rel)
    pins={str(f.relative_to(PROJECT)).replace('\\','/'):sha(f) for f in files}
    metrics=dict(oldpr['metrics'])
    metrics['primary']='All50ms outputs whose consumed input step lies in the preregistered actual motion interval; includes onset and reversal, no optimized lag shift'
    metrics['secondary']='settled: onset+.2..turn-.05 and turn+.2..stop-.05; stopped: stop+.2..5s; static1..5s'
    prereg=dict(schema='frozen-postprocessing-new-video-CPU-validation/v1',time_ns=time.time_ns(),
        source_old_preregistration_sha256=sha(OLD/'PREREGISTRATION.json'),pins=pins,
        cases=new_cases(),metrics=metrics,dt=.005,steps_per_case=1000,nodes=45669,edges=1513231,
        algorithm='Separate raw100ms-change EMA motion confidence from instantaneous calibrated spatial half-peak centroid; alpha.8 velocity.2, reset rather than discard beyond4hex',
        calibration='old white background first200step template, then oldlate mean; old motion threshold0.00712712309; fixed location numerical floor; no new-clip teacher/history corrections',
        static_gate='each of3 new stationary dot videos and matched-white control: false moving-localization fraction<=.05 on steps200..999',
        motion_gate='ALL6 must meet unchanged coverage.9, within3.8, median2 plus old mean baseline margins.20',
        video=dict(size=224,fps=200,frames=1000,radius_hex=2,pitch_px=6,foreground=0,background=1,
            sampling='same721 original coordinates;3x3 grayscale mean; causal one decoded frame per5ms'),
        caveats='Six joint novel motion conditions, not full factorial. Static dots3 novel positions. White control intentionally same input as old blank, not an unseen scene. Fixed known white background/init calibration; not arbitrary camera.',
        max_cpu_seconds=350,GPU=False,board=False,neural_retries=0,new_test_generated=False)
    dump(HERE/'PREREGISTRATION.json',prereg)
    dump(HERE/'ALGORITHM_FREEZE.json',dict(time_ns=time.time_ns(),prereg_sha256=sha(HERE/'PREREGISTRATION.json'),
        tracker_sha256=sha(HERE/'tracker.py'),calibration_sha256=sha(HERE/'CALIBRATION.npz'),test_video_exists=False))
    cv2.setNumThreads(1);xy,roi=grid()
    (HERE/'videos').mkdir();(HERE/'inputs').mkdir();(HERE/'truth').mkdir()
    xs=np.rint(111.5+6*xy[:,0]).astype(int);ys=np.rint(111.5-6*xy[:,1]).astype(int)
    yy,xx=np.mgrid[:224,:224];x=(xx-111.5)/6;y=(111.5-yy)/6;records=[]
    for c in prereg['cases']:
        pos,vel=trajectory(c)
        uv0=-pos[:,1]-pos[:,0]/np.sqrt(3);uv1=2*pos[:,0]/np.sqrt(3)
        assert np.max(np.maximum.reduce([abs(uv0),abs(uv1),abs(uv0+uv1)]))<8
        movie=HERE/'videos'/(c['id']+'.mp4');writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'mp4v'),200,(224,224));assert writer.isOpened()
        try:
            for k in range(1000):
                z=np.ones_like(x) if c['kind']=='blank' else .5*(1+np.tanh(6*(np.hypot(x-pos[k,0],y-pos[k,1])-2)))
                gray=np.rint(z*255).clip(0,255).astype('uint8');writer.write(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR))
        finally:writer.release()
        cap=cv2.VideoCapture(str(movie));assert cap.isOpened() and abs(cap.get(cv2.CAP_PROP_FPS)-200)<1e-6
        values=[]
        try:
            while True:
                ok,frame=cap.read()
                if not ok:break
                assert frame.shape==(224,224,3)
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                patch=np.stack([gray[ys+dy,xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
                values.append(patch.mean(0,dtype=float).astype('float32')/np.float32(255))
        finally:cap.release()
        pixels=np.asarray(values);assert pixels.shape==(1000,721)
        np.save(HERE/'inputs'/(c['id']+'.npy'),pixels)
        np.savez(HERE/'truth'/(c['id']+'.npz'),position=pos,velocity=vel,input_t=np.arange(1000)*.005,output_t=(np.arange(1000)+1)*.005)
        is_old_blank=c['kind']=='blank' and np.array_equal(pixels,np.load(OLD/'inputs/CAL_BLANK.npy'))
        records.append(dict(id=c['id'],video_sha256=sha(movie),input_sha256=sha(HERE/'inputs'/(c['id']+'.npy')),
            truth_sha256=sha(HERE/'truth'/(c['id']+'.npz')),decoded_frames=1000,
            generated_after_freeze=True,input_identical_to_old_blank=bool(is_old_blank)))
        print('NEW_INPUT',c['id'],flush=True)
    dump(HERE/'INPUT_MANIFEST.json',records)
    dump(HERE/'INPUT_GENERATION.json',dict(time_ns=time.time_ns(),after_algorithm_freeze=True,
        neural_calls=0,clips=10,novel_motion=6,novel_static_dot=3,matched_white_control=1))

def analyze():
    p=load(HERE/'PREREGISTRATION.json');freeze=load(HERE/'ALGORITHM_FREEZE.json')
    assert sha(HERE/'PREREGISTRATION.json')==freeze['prereg_sha256']
    for rel,h in p['pins'].items():assert sha(PROJECT/rel)==h,rel
    execution=load(HERE/'EXECUTION.json');assert execution['neural_steps']==10000 and not execution['GPU']
    assert load(HERE/'INPUT_GENERATION.json')['time_ns']>freeze['time_ns']
    xy,roi=grid();cal=calibration();steps=np.arange(9,1000,10);times=steps*.005
    (HERE/'predictions').mkdir();preds={};meta={};flows={}
    perm=np.random.default_rng(2026101804).permutation(721)
    # All ordinary predictions frozen before any new test truth is read.
    for c in p['cases']:
        f=np.load(HERE/'runs'/c['id']/'flow.npy');flows[c['id']]=f
        pred,m=run(f,xy,roi,cal);preds[c['id']]=pred;meta[c['id']]=m
        np.save(HERE/'predictions'/(c['id']+'.npy'),pred)
    dump(HERE/'PREDICTIONS_FROZEN.json',dict(time_ns=time.time_ns(),new_truth_opened=False,tracker_sha256=sha(HERE/'tracker.py')))
    rows=[];controls=[];truths={}
    oldspec=importlib.util.spec_from_file_location('old_frozen_tracker',OLD/'readout.py')
    oldmodule=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(oldmodule)
    dist=np.linalg.norm(xy[:,None]-xy[None],axis=2);neighbors=[np.flatnonzero(np.isclose(dist[i],1,atol=1e-8)) for i in range(721)]
    oldth=load(OLD/'CALIBRATION.json')['threshold']
    for c in p['cases']:
        name=c['id'];pred=preds[name];truth=np.load(HERE/'truth'/(name+'.npz'));truths[name]=truth
        if c['kind']!='motion':
            rate=float(pred[steps>=200,1].mean());controls.append(dict(id=name,false_detection_fraction=rate,pass_gate=rate<=.05));continue
        active=(times>=c['onset'])&(times<c['stop'])
        m=score(pred,truth['position'],active)
        settled=((times>=c['onset']+.2)&(times<c['turn']-.05))|((times>=c['turn']+.2)&(times<c['stop']-.05))
        secondary=score(pred,truth['position'],settled)
        null,_=run(flows[name][:,:,perm],xy,roi,permuted_cal(cal,perm));np.save(HERE/'predictions'/(name+'_spatial_null.npy'),null)
        nm=score(null,truth['position'],active)
        old,_=oldmodule.track(flows[name],xy,neighbors,roi,oldth)
        np.save(HERE/'predictions'/(name+'_old_tracker.npy'),old)
        oldm=score(old,truth['position'],active)
        const=float(np.mean(np.linalg.norm(truth['position'][steps[active]],axis=1)<=3))
        stopped=times>=c['stop']+.2
        rows.append(dict(id=name,primary=m,settled=secondary,spatial_null=nm,old_tracker=oldm,
            fixed_origin_fraction=const,stopped_detection_fraction=float(pred[stopped,1].mean()),meta=meta[name]))
    normal=float(np.mean([r['primary']['within3_fraction'] for r in rows]));null=float(np.mean([r['spatial_null']['within3_fraction'] for r in rows]));const=float(np.mean([r['fixed_origin_fraction'] for r in rows]))
    passed=all(r['primary']['pass_gate'] for r in rows) and all(c['pass_gate'] for c in controls) and normal-null>=.2 and normal-const>=.2
    summary=dict(status='PASS_FROZEN_TRACKER_NEW_CONTROLLED_VIDEOS' if passed else 'FAIL_FROZEN_TRACKER_NEW_CONTROLLED_VIDEOS',
        cases=rows,controls=controls,mean_motion_within3=normal,mean_null_within3=null,mean_fixed_origin=const,
        algorithm_unchanged_after_freeze=True,neural_model_unchanged=True,GPU=False,board=False,
        limits=p['caveats'],original_pilot_status_unchanged='FAIL_FIXED_SIMPLE_FLOW_TRACKER')
    dump(HERE/'SUMMARY.json',summary)
    with (HERE/'METRICS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        flat=[dict(id=r['id'],**r['primary'],old_tracker_within3=r['old_tracker']['within3_fraction'],
            null_within3=r['spatial_null']['within3_fraction'],stopped_detection=r['stopped_detection_fraction']) for r in rows]
        writer=csv.DictWriter(f,fieldnames=flat[0]);writer.writeheader();writer.writerows(flat)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,3,figsize=(13,8))
    for ax,r in zip(axs.flat,rows):
        name=r['id'];truth=truths[name]['position'];pred=preds[name]
        ax.plot(truth[:,0],truth[:,1],color='black',lw=2,label='Actual path')
        ax.plot(pred[:,2],pred[:,3],'.-',ms=2,lw=.7,color='crimson',label='Frozen flow-only tracker')
        ax.scatter(xy[roi,0],xy[roi,1],s=2,color='gray',alpha=.15)
        ax.set(xlim=(-11,11),ylim=(-11,11),title=f"{name}\nwithin18px={r['primary']['within3_fraction']:.1%}, gate={r['primary']['pass_gate']}")
        ax.set_aspect('equal');ax.legend(fontsize=6)
    fig.suptitle('New videos generated after algorithm freeze; original full FlyVis CPU\nAll conditions retained; ground truth used for scoring only')
    fig.tight_layout();fig.savefig(HERE/'new_trajectories.png',dpi=150);plt.close(fig)
    # Offline review includes all6 new motion cases, no best-case selection.
    writer=cv2.VideoWriter(str(HERE/'new_tracking_review.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),20,(672,504));assert writer.isOpened()
    motion=p['cases'][:6];caps=[cv2.VideoCapture(str(HERE/'videos'/(c['id']+'.mp4'))) for c in motion]
    try:
        for j,k in enumerate(steps):
            tile=np.full((504,672,3),235,np.uint8)
            for i,c in enumerate(motion):
                caps[i].set(cv2.CAP_PROP_POS_FRAMES,int(k));ok,im=caps[i].read();assert ok
                q=truths[c['id']]['position'][k];pt=tuple(np.rint([111.5+6*q[0],111.5-6*q[1]]).astype(int))
                cv2.drawMarker(im,pt,(0,180,0),cv2.MARKER_CROSS,12,1)
                row=preds[c['id']][j]
                if row[1]:cv2.circle(im,tuple(np.rint([111.5+6*row[2],111.5-6*row[3]]).astype(int)),5,(0,0,230),1)
                x=i%3*224;y=i//3*252;tile[y:y+224,x:x+224]=im
                cv2.putText(tile,c['id'],(x+3,y+237),cv2.FONT_HERSHEY_SIMPLEX,.33,(0,0,0),1)
                cv2.putText(tile,'offline CPU; green truth/red estimate',(x+3,y+248),cv2.FONT_HERSHEY_SIMPLEX,.25,(0,0,0),1)
            writer.write(tile)
    finally:
        writer.release()
        for cap in caps:cap.release()
    for e in execution['cases']:
        folder=HERE/'runs'/e['id']
        assert sha(folder/'states.npy')==e['full_state_sha256'] and sha(folder/'flow.npy')==e['flow_sha256']
    dump(HERE/'SAVED_DATA_CHECK.json',dict(all10_state_and_flow_hashes=True,source_pins=True,
        freeze_before_inputs=True,predictions_before_truth=True,neural_steps=0,GPU=False))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['develop','freeze_prepare','analyze'])
    globals()[ap.parse_args().stage]()
