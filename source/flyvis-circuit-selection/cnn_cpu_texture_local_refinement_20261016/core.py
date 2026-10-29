"""CPU-only same-size CNN update; all previous experiments are read-only."""
from pathlib import Path
import csv, copy, ctypes, gc, hashlib, importlib.util, json, os, shutil, sys, time, uuid

HERE=Path(__file__).resolve().parent
LANE=HERE.parent
OLD=LANE/'cnn_t4t5_mp4_holdout_20261016'
spec=importlib.util.spec_from_file_location('line4_existing_MP4',OLD/'core.py')
accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
ref=accepted.ref
np,torch=accepted.np,accepted.torch
dump,load,sha,digest=accepted.dump,accepted.load,accepted.sha,accepted.digest
MODEL,MODEL_SHA=accepted.MODEL,accepted.MODEL_SHA
BUNDLE=accepted.BUNDLE
DT=.005

def check(deep=False):
    p=load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json')==load(HERE/'FREEZE.json')['sha256']
    for file,pin in p['pins'].items():
        s=Path(file).stat();assert (s.st_size,s.st_mtime_ns)==(pin['bytes'],pin['mtime_ns']),file
        if deep:assert sha(file)==pin['sha256'],file
    assert not torch.cuda.is_initialized() and torch.get_num_threads()==1
    return p

def cases(training):
    common=dict(steps=1000,duration_s=5,video_fps=100,texture_seed=2026101641,texture_contrast=.12,texture_sigma=5)
    if training:
        result=[dict(id='TRAIN_TEXTURE_A',kind='texture',group='static',texture_seed=2026101641,texture_contrast=.10,texture_sigma=4),
            dict(id='TRAIN_TEXTURE_B',kind='texture',group='static',texture_seed=2026101642,texture_contrast=.15,texture_sigma=6),
            dict(id='TRAIN_ON45_LOCAL',kind='motion',group='motion',polarity='ON',angle=45,speed=10,center=[-3,2],local=True,background='gray'),
            dict(id='TRAIN_OFF225_LOCAL',kind='motion',group='motion',polarity='OFF',angle=225,speed=14,center=[3,-2],local=True,background='moving_texture',background_angle=45,background_speed=2)]
    else:
        result=[dict(id='TEST_ON135_FULL',kind='motion',group='motion',polarity='ON',angle=135,speed=9,center=[0,0],local=False,background='gray'),
            dict(id='TEST_OFF315_FULL',kind='motion',group='motion',polarity='OFF',angle=315,speed=15,center=[0,0],local=False,background='gray'),
            dict(id='TEST_ON135_LOCAL_GRAY',kind='motion',group='motion',polarity='ON',angle=135,speed=8,center=[-2,-4],local=True,background='gray'),
            dict(id='TEST_OFF315_LOCAL_GRAY',kind='motion',group='motion',polarity='OFF',angle=315,speed=16,center=[2,4],local=True,background='gray'),
            dict(id='TEST_ON315_LOCAL_MOVING',kind='motion',group='motion',polarity='ON',angle=315,speed=11,center=[-4,-2],local=True,background='moving_texture',background_angle=135,background_speed=2.5),
            dict(id='TEST_OFF135_LOCAL_STATIC',kind='motion',group='motion',polarity='OFF',angle=135,speed=13,center=[4,2],local=True,background='static_texture'),
            dict(id='TEST_TEXTURE_LOW',kind='texture',group='static',texture_seed=2026101691,texture_contrast=.06,texture_sigma=2.5),
            dict(id='TEST_TEXTURE_MEDIUM',kind='texture',group='static',texture_seed=2026101692,texture_contrast=.12,texture_sigma=5.5),
            dict(id='TEST_TEXTURE_HIGH',kind='texture',group='static',texture_seed=2026101693,texture_contrast=.18,texture_sigma=8),
            dict(id='TEST_GRAY',kind='gray',group='static')]
    output=[]
    for i,v in enumerate(result):
        c=dict(common);c.update(v)
        if not training and c['kind']=='motion':c['texture_seed']=2026101680+i
        c['windows']=dict(allpost=[200,1000],active=[320,720],stopped=[840,1000]) if c['group']=='motion' else dict(adapted=[400,1000],late=[800,1000])
        output.append(c)
    return output

def make_inputs(which):
    p=check();training=which=='training';folder=HERE/which
    if not training:
        gate=load(HERE/'TRAINING_GATE.json');freeze=load(HERE/'MODEL_FREEZE.json')
        assert gate['pass_gate'] and sha(freeze['path'])==freeze['sha256']
        assert time.time_ns()>freeze['time_ns']
    folder.mkdir(exist_ok=True);(folder/'inputs').mkdir();(folder/'videos').mkdir()
    source=(OLD/'video_io.py').read_text(encoding='utf-8')
    source=source.replace('(0,0),5)',"(0,0),case.get('texture_sigma',5))")
    source=source.replace('.12*texture',"case.get('texture_contrast',.12)*texture")
    renderer=HERE/'video_io.py'
    assert renderer.read_text(encoding='utf-8')==source
    spec=importlib.util.spec_from_file_location('line4_refine_video_'+which,renderer)
    video=importlib.util.module_from_spec(spec);spec.loader.exec_module(video)
    sampling=dict(np.load(OLD/'SAMPLER.npz'));records=[]
    for case in p[which+'_cases']:
        c=copy.deepcopy(case);movie=folder/'videos'/(c['id']+'.mp4');video.render(movie,c)
        x,meta=video.decode(movie,sampling);f=folder/'inputs'/(c['id']+'.npy');np.save(f,x)
        c.update(path=str(f),sha256=sha(f),video_path=str(movie),video_sha256=sha(movie),time=meta)
        records.append(c)
    dump(folder/'INPUTS.json',records)
    dump(folder/'INPUT_GENERATION.json',dict(time_ns=time.time_ns(),actual_MP4=len(records),
        after_model_freeze=not training,model_sha=None if training else load(HERE/'MODEL_FREEZE.json')['sha256']))
    return records

def feature_rows(x,frames,pixels,model,m):
    f=torch.as_tensor(frames,dtype=torch.long);p=torch.as_tensor(pixels,dtype=torch.long)
    neighbors=torch.as_tensor(np.where(m['neighbors']>=0,m['neighbors'],721))
    patch=x[f[:,None,None],torch.arange(23)[None,:,None],neighbors[p,None,:]]
    raw=x[f[:,None],model.h_channels[None,:],p[:,None]]
    return torch.cat([(torch.relu(patch)/model.input_scale[None,:,None]).flatten(1),raw/model.h_scale],1)

def fresh_loop(model,m,initial,run):
    return ref.ClosedLoop(ref.r_service(),ref.CNNService(model,m),initial,m,run)

def score(case,full,cnn,ff,cf):
    m=ref.mapping();roi=np.load(accepted.ROI_PATH)
    errors=np.empty((len(full),3),np.float64)
    for k in range(len(full)):
        dh=cnn[k,m['H']].astype(np.float64)-full[k,m['H']]
        dr=cnn[k,m['R']].astype(np.float64)-full[k,m['R']]
        df=cf[k,:,roi].astype(np.float64)-ff[k,:,roi]
        errors[k]=[np.sqrt(np.mean(dh*dh)),np.sqrt(np.mean(dr*dr)),np.sqrt(np.mean(df*df))]
    if case['group']=='motion':windows=accepted.score_motion(case,full[:,m['H']],cnn[:,m['H']],ff,cf,roi,m)
    else:
        windows={}
        for name,(a,b) in case['windows'].items():
            h,r,f=np.sqrt(np.mean(errors[a:b]**2,axis=0))
            windows[name]=dict(H_RMSE=float(h),R_RMSE=float(r),flow_RMSE=float(f),pass_gate=bool(max(h,r,f)<=.002))
    return dict(case=case['id'],group=case['group'],pass_gate=all(z['pass_gate'] for z in windows.values()),windows=windows),errors
