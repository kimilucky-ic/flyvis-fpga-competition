"""Freeze an unchanged gate, then generate one new controlled CPU video batch."""
from pathlib import Path
import hashlib,json,time,shutil
import numpy as np
import cv2,psutil
HERE=Path(__file__).resolve().parent;LANE=HERE.parent;PROJECT=HERE.parents[2]
PREVIOUS=LANE/'flow_tracking_refinement_20261018';DIAG=LANE/'flow_tracking_transients_20261018'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,d):
    with (HERE/p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def cases():
    configs=[('C_EARLY35_V4',35,4,.075,1.25,5,0,0),
        ('C_LATE125_V6',125,6,1.65,1,5,0,0),
        ('C_SLOW205_V1',205,1,.7,4,10.5,0,0),
        ('C_SLOW295_V2',295,2,.45,2,6,0,0),
        ('N_EARLY55_V4',55,4,.2,1.5,5,2/255,0),
        ('N_SLOW145_V1p5',145,1.5,.8,8/3,8,2/255,0),
        ('B_LATE235_V5',235,5,1.5,1.2,5,0,.02),
        ('B_SLOW325_V1',325,1,.6,4,10.5,0,.02)]
    result=[]
    for i,(name,angle,speed,onset,leg,duration,noise,brightness) in enumerate(configs):
        a=np.deg2rad(angle);d=np.array([np.cos(a),np.sin(a)]);perp=np.array([-d[1],d[0]])
        center=perp*(3.7 if i%2==0 else -3.7)+d*(.65 if i%2==0 else -.65)
        result.append(dict(id=name,kind='motion',angle=angle,speed=speed,center=center.tolist(),
            onset=onset,turn=onset+leg,stop=onset+2*leg,halfspan=speed*leg/2,
            steps=int(round(duration/.005)),noise_sigma=noise,brightness_depth=brightness,seed=2026101820+i))
    controls=[('C_STATIC','static',[2.7,2.6],0,0),('N_STATIC','static',[-3.1,2.9],2/255,0),
        ('B_STATIC','static',[3.8,-1.9],0,.02),('NB_STATIC','static',[-2.6,-3.3],2/255,.02),
        ('N_BLANK','blank',[0,0],2/255,0),('B_BLANK','blank',[0,0],0,.02)]
    for i,(name,kind,center,noise,brightness) in enumerate(controls):
        result.append(dict(id=name,kind=kind,angle=0,speed=0,center=center,onset=None,turn=None,stop=None,halfspan=0,
            steps=1000,noise_sigma=noise,brightness_depth=brightness,seed=2026101830+i))
    return result

def trajectory(c):
    t=np.arange(c['steps'])*.005
    if c['kind']=='motion':
        s=np.where(t<c['onset'],-c['halfspan'],np.where(t<c['turn'],-c['halfspan']+c['speed']*(t-c['onset']),
            np.where(t<c['stop'],c['halfspan']-c['speed']*(t-c['turn']),-c['halfspan'])))
    else:s=np.zeros(len(t))
    a=np.deg2rad(c['angle']);d=np.array([np.cos(a),np.sin(a)]);p=np.asarray(c['center'])[None]+s[:,None]*d
    v=np.zeros_like(p)
    if c['kind']=='motion':
        v[(t>=c['onset'])&(t<c['turn'])]=c['speed']*d;v[(t>=c['turn'])&(t<c['stop'])]=-c['speed']*d
    return t,p,v

def main():
    cv2.setNumThreads(1)
    assert not (HERE/'videos').exists(),'DO_NOT_REGENERATE_FROZEN_TESTS'
    resource=dict(free_disk_bytes=shutil.disk_usage(HERE).free,available_windows_RAM=psutil.virtual_memory().available,
        estimated_new_bytes=3600000000,minimum_free_disk_bytes=6*2**30,preparation_minimum_RAM_bytes=2**30,
        stage='streaming224px_video_creation_not_neural_worker',neural_worker_minimum_RAM=2*2**30)
    dump('RESOURCE_CHECK.json',resource)
    assert resource['free_disk_bytes']>=6*2**30 and resource['available_windows_RAM']>=2**30
    accepted=load(DIAG/'CANDIDATE_SPEC.json');gate=DIAG/'input_verified_tracker.py'
    assert sha(gate)==accepted['algorithm_sha256']=='89665dda9c6b6f104326773d9179350b0f0a44dfb7232b56cfa55f62e97fb224'
    with (HERE/'input_verified_tracker.py').open('xb') as f:f.write(gate.read_bytes())
    old=load(PREVIOUS/'PREREGISTRATION.json');files=[gate,PREVIOUS/'tracker.py',PREVIOUS/'CALIBRATION.npz',HERE/'input_verified_tracker.py',
        HERE/'prepare.py',HERE/'run_cpu.py',HERE/'analyze.py',LANE/'flow_tracking_pilot_20261018/GRID.npz']
    for rel in old['pins']:
        if rel.startswith('fly/') or 'input_bundle/' in rel:files.append(PROJECT/rel)
    pins={str(f.relative_to(PROJECT)).replace('\\','/'):sha(f) for f in files}
    cs=cases();assert sum(c['steps'] for c in cs)==17000
    prereg=dict(schema='unchanged-input-stillness-gate-new-video-CPU-validation/v1',created_ns=time.time_ns(),
        source_candidate_spec_sha256=sha(DIAG/'CANDIDATE_SPEC.json'),gate_sha256=sha(HERE/'input_verified_tracker.py'),
        unchanged_old_gate=True,pins=pins,cases=cs,steps_total=17000,dt=.005,nodes=45669,edges=1513231,
        model='original continuous Euler, FP32, complete original state; official original DecoderGAVP recursively eval',
        video=dict(size=224,fps=200,pitch_px=6,radius_hex=2,background=1,foreground=0,sampler='same721 sites,3x3 mean8bit gray',codec='mp4v'),
        noise='independent Gaussian pixels sigma2/255, clipped0..1 before8bit andMP4, fixed per-clip seed; actual decoded input variability reported, no post-test amplitude adjustment',
        brightness='additive dimming offset=-depth*(1-cos(2*pi*.35*t))/2, depth=.02 when enabled; affects scene, not target position',
        primary='ALL20Hz outputs with consumed input[k] time in onset<=t<stop, includes first onset and reversal, no lag shift',
        unchanged_motion_gates=dict(coverage_min=.9,within18px_fraction_min=.8,valid_median_px_max=12),
        unchanged_static_gate=dict(window='all outputs at consumed step>=200, i.e.1s onward',false_detection_fraction_max=.05,applies_to='each of all6 controls, including noise/brightness; no nuisance exemption'),
        unchanged_evidence_gate=dict(all8_motion_must_pass=True,all6_controls_must_pass=True,mean_advantage_over_spatial_null_min=.2,mean_advantage_over_fixed_origin_min=.2),
        diagnostic_temporal_readouts=dict(startup='all outputs0..1s; report UNKNOWN separately; motion onset case also report pre-onset',
            stop='fraction triggered stop+.2s..end, last trigger time and first sustained quiet time, censored if quiet not observed',
            slow='ordinary trajectory metrics plus fixed-at-start position baseline, because18px can conceal insufficient displacement; extra baseline descriptive only'),
        no_new_startup_stop_gate='descriptive only; do not invent new cutoff or change primary acceptance',
        gate='unchanged100ms21sample history, half8bit3x3 input quantum epsilon, original flow-only coordinate module and calibration',
        predictions_before_truth_scoring=True,new_inputs_not_yet_generated=True,max_cpu_seconds=300,max_neural_attempts=1,
        analysis='frozen8motion/6control; compare gate versus same original tracker on same flow; no outcome-based removal or adjustment',
        scope='new controlled videos, not camera/real-time/biological truth; all prior data now development; preserve all failures',GPU=False,board=False)
    dump('PREREGISTRATION.json',prereg)
    dump('ALGORITHM_FREEZE.json',dict(time_ns=time.time_ns(),prereg_sha256=sha(HERE/'PREREGISTRATION.json'),
        gate_sha256=sha(HERE/'input_verified_tracker.py'),source_tracker_sha256=sha(PREVIOUS/'tracker.py'),
        calibration_sha256=sha(PREVIOUS/'CALIBRATION.npz'),videos_exist=False,test_generated=False))
    g=np.load(LANE/'flow_tracking_pilot_20261018/GRID.npz');xy=g['xy']
    xs=np.rint(111.5+6*xy[:,0]).astype(int);ys=np.rint(111.5-6*xy[:,1]).astype(int)
    yy,xx=np.mgrid[:224,:224];xx=(xx-111.5)/6;yy=(111.5-yy)/6
    for name in ['videos','inputs','truth']:(HERE/name).mkdir()
    old_hashes={r['input_sha256'] for folder in [PREVIOUS,LANE/'flow_tracking_pilot_20261018'] for r in load(folder/'INPUT_MANIFEST.json')}
    records=[]
    for c in cs:
        t,pos,vel=trajectory(c);rng=np.random.default_rng(c['seed']);movie=HERE/'videos'/(c['id']+'.mp4')
        uv0=-pos[:,1]-pos[:,0]/np.sqrt(3);uv1=2*pos[:,0]/np.sqrt(3)
        if c['kind']!='blank':assert np.max(np.maximum.reduce([abs(uv0),abs(uv1),abs(uv0+uv1)]))<9
        writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'mp4v'),200,(224,224));assert writer.isOpened()
        try:
            for k in range(c['steps']):
                z=np.ones((224,224)) if c['kind']=='blank' else .5*(1+np.tanh(6*(np.hypot(xx-pos[k,0],yy-pos[k,1])-2)))
                z+=-c['brightness_depth']*(1-np.cos(2*np.pi*.35*t[k]))/2
                if c['noise_sigma']:z+=rng.normal(0,c['noise_sigma'],z.shape)
                gray=np.rint(np.clip(z,0,1)*255).astype('uint8');writer.write(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR))
        finally:writer.release()
        cap=cv2.VideoCapture(str(movie));assert cap.isOpened() and abs(cap.get(cv2.CAP_PROP_FPS)-200)<1e-6
        values=[]
        try:
            while True:
                ok,frame=cap.read()
                if not ok:break
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                patch=np.stack([gray[ys+dy,xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
                values.append(patch.mean(0,dtype=float).astype('float32')/np.float32(255))
        finally:cap.release()
        pixels=np.asarray(values);assert pixels.shape==(c['steps'],721) and np.isfinite(pixels).all()
        np.save(HERE/'inputs'/(c['id']+'.npy'),pixels)
        np.savez(HERE/'truth'/(c['id']+'.npz'),position=pos,velocity=vel,input_t=t,output_t=t+.005)
        h=sha(HERE/'inputs'/(c['id']+'.npy'));assert h not in old_hashes,'NOT_NOVEL'
        records.append(dict(id=c['id'],decoded_frames=len(pixels),video_sha256=sha(movie),input_sha256=h,
            truth_sha256=sha(HERE/'truth'/(c['id']+'.npz')),differs_from_all_old16_inputs=True,
            decoded_input_late_step_change_max=float(np.abs(np.diff(pixels[200:],axis=0)).max()),
            late_unique_input_frames=int(len(np.unique(pixels[200:],axis=0)))))
        print('NEW_VIDEO',c['id'],len(pixels),flush=True)
    dump('INPUT_MANIFEST.json',records)
    dump('INPUT_GENERATION.json',dict(time_ns=time.time_ns(),after_algorithm_freeze=True,cases=len(records),steps=17000,
        all_actual_inputs_novel=True,neural_calls=0,GPU=False,board=False))

if __name__=='__main__':main()
