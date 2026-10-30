from core import *

assert not (HERE/'PREREGISTRATION.json').exists(),'NEW_DIRECTORY_ONLY'
resources=dict(RAM=accepted.memory(),free_disk=shutil.disk_usage(HERE).free)
dump(HERE/('PREPARE_RESOURCE_'+str(time.time_ns())+'.json'),resources)
assert resources['RAM']['available_bytes']>=2*1024**3 and resources['free_disk']>=12*1024**3
source=(OLD/'video_io.py').read_text(encoding='utf-8').replace('(0,0),5)',"(0,0),case.get('texture_sigma',5))").replace('.12*texture',"case.get('texture_contrast',.12)*texture")
(HERE/'video_io.py').write_text(source,encoding='utf-8',newline='\n')
accepted.check(deep=True)
files={p for p in HERE.glob('*.py')}
files.update([MODEL,OLD/'PREREGISTRATION.json',OLD/'FREEZE.json',OLD/'video_io.py',OLD/'core.py',OLD/'SAMPLER.npz',
    LANE/'cnn_failure_diagnosis_20261016/OPERATOR_AUDIT.json',BUNDLE/'initial_state_full.npy',BUNDLE/'expanded_parameters.npz'])
files.update(Path(v) for v in load(OLD/'PREREGISTRATION.json')['pins'])
files.update([ref.OLD/'mapping.npz',ref.OLD/'PREREGISTRATION.json',BUNDLE/'identity_manifest.json',ref.OLD/'R_CANDIDATE.json'])
for n in ['ON60','ON240','OFF90','OFF270']:
    files.add(LANE/'t4t5_criticality_20261011/cpu_preparation_r1'/(n+'_stimulus.npy'))
for mod in list(sys.modules.values()):
    name=getattr(mod,'__file__',None)
    if name and Path(name).is_file() and Path(name).suffix=='.py' and Path(name).resolve().is_relative_to(LANE):files.add(Path(name).resolve())
for n in ['STATIC_TEXTURE5s','OFF345_local_moving_background']:
    for q in [OLD/'runs'/n/'Full/states_raw.npy',OLD/'inputs'/(n+'.npy')]:files.add(q)
legacy=ref.train_references()
legacy_paths={r['condition']:r['path'] for r in load(ref.OLD/'PREREGISTRATION.json')['training']}
files.update(Path(v) for v in legacy_paths.values())
pins={str(p):dict(bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,sha256=sha(p)) for p in sorted(files)}
plan=dict(schema='same-size-CNN-texture-local-CPU-refinement/v1',parameters=31168,initial_model_sha256=MODEL_SHA,
    training_cases=cases(True),testing_cases=cases(False),pins=pins,legacy_paths=legacy_paths,
    training_sources='old four directions; old two failures explicitly promoted to TRAIN; four new train-only movies; 128 synthetic old-state fields supervised by original H',
    split='sensory training time k%5!=4, validation k%5==4; augmentation train states0:96, validation96:128; correlated internal validation, NOT final independent sensory test',
    teacher='Original Full/H output labels only. No original H weights/bias/tau copied into CNN coefficients. No algebraic operator transplant.',
    fit=dict(method='float64 weighted centered/preconditioned residual ridge CG, eight RHS',ridge=1e-8,max_iterations=400,max_wall_s=360,
        training_points=dict(augmented=12288,sensory=6144,late_static=2048,initial=721),
        weights='ordinary1; late_static2; initial sqrt8; normalized target increments by unchanged output_scale',
        augmentation='128 independent Gaussian current fields centered0, std existing input_scale; original H next-state supervision; counterfactual states, not natural movies',
        stopping_relative_normal_equation_residual=1e-8,automatic_retry=False),
    one_step_gate='unchanged overall increment nRMSE<=.10, each type<=.20; evaluated separately on held sensory and held augmented states',
    short_gate='unchanged H state nRMSE<=.05,R<=.01,each type<=.10; all128 finite; static additionally original .002 H/R/flow RMSE',
    short_windows='each of ten sensory training sources at starts0,320,800 for1000-step source or0,196,320 for485;128steps; initialize once from teacher, never correct within window; gray0:128',
    formal_gate='unchanged allH responseL2<=.20;331ROI E<=.20,M[.8,1.2],fieldangle<=15 allpost200:1000,active320:720,stopped840:1000;local active foregroundradius3 same gates;staticadapted400:1000/late800:1000 abs H/R/flow<=.002',
    formal='only after training gates and model SHA freeze, actually encode/decode ten new5s MP4; Full/CNN own initial state, first caseSham; all45669states saved; nativeH forbidden in CNN',
    resource=dict(CPU_threads=1,GPU=0,board=0,max_new_disk_GiB=8,min_free_RAM_GiB=2,training_budget_s=480,formal_budget_s=360),
    stop='one fit, one gate, one new test batch; failure retained/no threshold or architecture changes/no GPU or board; stop after first full batch',
    hardware='discussion deferred until line2 and line7 mainline completion and separate user decision')
dump(HERE/'RESOURCE_CHECK.json',resources);dump(HERE/'PREREGISTRATION.json',plan)
dump(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
make_inputs('training')
print(json.dumps(dict(stage='PREREGISTERED_TRAINING_INPUTS_READY',sha256=sha(HERE/'PREREGISTRATION.json'),GPU=0,board=0)),flush=True)
