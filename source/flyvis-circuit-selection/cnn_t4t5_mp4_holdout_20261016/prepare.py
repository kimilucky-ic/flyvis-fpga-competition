"""Freeze stimuli/metrics BEFORE video generation or any neural evaluation."""
from core import *
import video_io

assert not (HERE/'PREREGISTRATION.json').exists()
assert shutil.disk_usage(HERE).free>=10*1024**3
resources=memory(); assert resources['available_bytes']>=2*1024**3
previous.check(deep=True); ref.freezecheck(deep=True); base.check_frozen()
m=ref.mapping(); common=np.load(ROI_PATH); plan=cases(); sampling=video_io.sampler(m['grid_uv'])
assert len(plan)==10 and sum(c['group']=='motion' for c in plan)==8
for c in plan:
    if c.get('local'): foreground_roi(c,m,common)
# Quantitative parity with the prior721-point Cartesian projection, no neural call.
uv=m['grid_uv']; xp=np.rint(111.5+1.5*uv[1]*(6/np.sqrt(3))).astype(np.int64)
yp=np.rint(111.5+6*(uv[0]+uv[1]/2)).astype(np.int64)
assert np.array_equal(xp,sampling['x_pixel']) and np.array_equal(yp,sampling['y_pixel'])
dump(HERE/'PRECHECK.json',dict(status='PASS_CPU_AND_RETINA_GEOMETRY',**resources,
    free_disk_bytes=shutil.disk_usage(HERE).free,cv2=video_io.cv2.__version__,source_identity=True,
    exact721_geometry=True,foreground_ROIs_in_original331=True,new_neural_steps=0,GPU=0,board=0))
np.savez(HERE/'SAMPLER.npz',**sampling)
paths=[HERE/n for n in ['core.py','video_io.py','prepare.py','run.py','analyze.py','audit.py','plots.py']]
paths += [PREVIOUS/n for n in ['core.py','run.py','audit.py','PREREGISTRATION.json','FINAL_AUDIT.json']]
paths += [MODEL,ref.HERE/'MODEL_FREEZE.json',base.HERE/'cnn.py',base.HERE/'experiment.py',base.HERE/'common.py',
          base.HERE/'decoder_cpu.py',base.HERE/'mapping.npz',base.HERE/'R_CANDIDATE.json',
          BUNDLE/'expanded_parameters.npz',BUNDLE/'initial_state_full.npy',ROI_PATH,HERE/'SAMPLER.npz']
pins={str(p):dict(bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,sha256=sha(p)) for p in paths}
dump(HERE/'PREREGISTRATION.json',dict(schema='frozen-CNN-real-MP4-controlled-inputs/v1',cases=plan,pins=pins,
    model_SHA=MODEL_SHA,parameters=31168,training_updates=0,GPU=0,board=0,dt=DT,
    input='New224x224100fps5s MP4v files, actually decoded500frames, 721points3x3means, causalZOH to1000steps; both networks consume identical saved decoded input. Synthetic controlled scenes, NOT natural footage.',
    timing='0-1sgray, .1s onset contrast ramp, 1-4smotion,4-5shold; full a0 shared. No neural warmup/reset/teacher during video.',
    motion_gate='Original331ROI/allH: each allpost200:1000,active320:720,stopped840:1000 HresponseL2<=.20; eligible flowE<=.20,M[.8,1.2],fieldangle<=15; weak reference neverPASS.',
    foreground='For fourlocal cases, active320:720 also must pass same flow gate on fixed radius3core around stimulus center, wholly inside original331. H gate remains all5768.',
    static_gate='Both adapted400:1000 andlate800:1000: absoluteRMSE H<=.002,R<=.002,ROI flowcomponent<=.002, identical prior numeric bounds. No direction-classifier false-positive claim.',
    evidence='Frozen original full/R-only/DecoderGAVP,recursiveeval,originalweights; originalH runtime guard in CNN. Accepted runner function body reused unchanged with explicit paths, separate freshFull refs.',
    budget=dict(CPU_threads=1,neural_wall_s_max=600,video_prepare_s_max=180,new_disk_GiB_max=6,free_disk_GiB_min=10,
                free_RAM_GiB_min=2,retries=0),
    stop='One batch, retain failures/NOT_EVALUABLE. No model/threshold changes, training,GPU,board,GUI,scheduler or additional datasets. Current videos become seen data.'))
dump(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
(HERE/'videos').mkdir(); (HERE/'inputs').mkdir(); records=[]; start=time.perf_counter()
for case in plan:
    if time.perf_counter()-start>180: raise TimeoutError('VIDEO_PREP_BUDGET')
    video=HERE/'videos'/(case['id']+'.mp4'); video_io.render(video,case)
    data,metadata=video_io.decode(video,sampling)
    assert data.shape==(1000,721) and data.dtype==np.float32 and np.isfinite(data).all() and data.min()>=0 and data.max()<=1
    p=HERE/'inputs'/(case['id']+'.npy'); np.save(p,data)
    dump(HERE/'inputs'/(case['id']+'_time.json'),metadata)
    records.append(dict(**case,path=str(p),sha256=sha(p),video_path=str(video),video_sha256=sha(video)))
    print(json.dumps(dict(stage='MP4_ACTUALLY_DECODED',case=case['id'],video_bytes=video.stat().st_size,input_sha=sha(p))),flush=True)
dump(HERE/'INPUTS.json',records)
dump(HERE/'VIDEO_PREPARATION.json',dict(status='ACTUAL_MP4_ENCODING_AND_DECODING',videos=10,frames=5000,
    input_steps=10000,neural_steps=0,wall_s=time.perf_counter()-start,prereg_sha=sha(HERE/'PREREGISTRATION.json'),GPU=0))
