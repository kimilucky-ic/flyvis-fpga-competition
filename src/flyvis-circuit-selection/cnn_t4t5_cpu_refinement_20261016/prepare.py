"""Freeze all CPU training gates and new holdout design before refinement."""
from shared import *

assert shutil.disk_usage(HERE).free>6*1024**3
m=mapping();_,_,_,p=source();rr=r_service();target=OriginalTargets(p,m['R'])
initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'));pixels=torch.full((721,),.5)
# Training-only gradient view retains original R forward operation order.
old_grad=initial.clone().requires_grad_(True)
grad=OriginalTargets.step.__wrapped__(target,old_grad,pixels)
actual=rr.step(initial,pixels,step_id=0,run_id='gradient_check',condition_id='GRAY').activity
assert torch.equal(grad.detach(),actual)
value=torch.autograd.grad(grad.square().sum(),old_grad,retain_graph=False)[0]
assert torch.isfinite(value).all() and value[m['H']].abs().max()>0
dump(HERE/'PREFLIGHT.json',dict(status='PASS_CPU_SAME_ARCHITECTURE_AND_R_FORWARD',parameters=31168,
    differentiable_R_forward_bitwise_equal=True,original_H_in_gradient_R=False,new_R_candidates=2,
    torch=torch.__version__,GPU=0,free_bytes=shutil.disk_usage(HERE).free))
tests=[]
for name,sample,angle in [('ON30',3,30),('ON210',15,210),('OFF30',2,30),('OFF210',14,210)]:
    variants=['base']+(['speed_075','shift_v_minus3','local_left','local_right'] if name in ['ON30','OFF30'] else [])
    for variant in variants:tests.append(dict(id=name+'_'+variant,condition=name,original_sample=sample,angle=angle,polarity='ON' if name.startswith('ON') else 'OFF',variant=variant))
assert len(tests)==12
dump(HERE/'TEST_PLAN.json',tests)
raw=list((LANE/'phase4_direction_extension_20261010/prepared_inputs').glob('stimulus*.npy'));assert len(raw)==1
paths=[HERE/name for name in ['shared.py','prepare.py','train.py','evaluate.py']]
paths += [OLD/name for name in ['common.py','cnn.py','experiment.py','decoder_cpu.py','mapping.npz','R_CANDIDATE.json','training/cnn.pt','training/teacher_fields.npy','training/target_delta.npy','PREREGISTRATION.json']]
paths += [BUNDLE/name for name in ['expanded_parameters.npz','initial_state_full.npy','nodes_full.csv','identity_manifest.json']]
paths += [HERE/'TEST_PLAN.json',raw[0]]
for record in load(OLD/'PREREGISTRATION.json')['training']:paths.append(Path(record['path']))
pins={str(path):dict(bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,sha256=sha(path)) for path in paths}
dump(HERE/'PREREGISTRATION.json',dict(schema='same-CNN-CPU-refinement/v1',date='2026-10-16',pins=pins,architecture='unchanged HexCNN-AR1,31168 parameters; all original CNN definitions reused byte-for-byte',
    supervision='four accepted training stimuli only; time k%5==4 reserved for one-step validation (correlated temporal validation, not independent stimulus generalization)',
    augmentation=dict(teacher_H_states=256,seed=2026101607,source='training old states only, 1/4 gray a0',
        noise='independent Gaussian0.1*previous per-channel RMS on23 upstream fields including H; original H used ONLY to generate labels; no analytical H weights copied to CNN'),
    fit=dict(method='float64 weighted standardized matrix-free multi-output conjugate-gradient ridge; same learned convolution/recurrent/offset parameters',
        real_points=8192,augmented_points=8192,anchor_points=721,anchor_weight_squared=8,ridge_lambda=1e-6,max_CG_iterations=400,relative_residual_stop=1e-8,
        validation_points=4096,seed=2026101608),
    one_step_gate='validation RMSE/true increment RMS <=.10 overall AND<=.20 every type',
    short_gate='all4 train stimuli at k0/196/320,128 steps per window; gray128. Live original R plus own CNN H; one truth init per window only. H state nRMSE<=.05, R<=.01, every H subtype<=.10; gray H absoluteRMSE<=.002; no finite/magnitude failures',
    optional_BPTT=dict(trigger='only if ridge model fails either training gate',max_updates=100,length=16,
        method='true differentiable original R equations plus own CNN H, no mid-window truth; original R weights fixed',
        learning_rate=.0001,loss='normalized H state error +0.1 R state error, plus one-step patch auxiliary',checkpoints=[25,50,75,100],
        selection='training-time validation/short gates only; stop at first full pass; never examine fresh test to select checkpoint'),
    testing='only after both gates PASS and model SHA frozen; then twelve unseen direction/speed/position/local-window cases, Full+CNN and one numericalSham',
    new_cases=tests,stimulus_source=str(raw[0]),
    stimulus_transform='original721-point official retinal inputs; post200 speed075 causal floor(.75*j), shift v-3 with polarity background; local radius5 soft circular aperture centers x=-5/+5,y0, gray.5 outside, independent of angle/polarity',
    test_gate='unchanged first-pilot H response relativeL2<=.20 and fixed331ROI flow E<=.20/M[.8,1.2]/field angle<=15 in primary200:286 and allpost200:485; all485 finite. Weak reference not a pass.',
    honesty='old8 test cases not new holdouts; augmented states are training counterfactuals, not natural sensory trials; teacher labels and window starts never used in formal test production',
    budget=dict(CPU_threads=1,fit_wall_s=600,BPTT_wall_s=600,test_wall_s=600,new_disk_GiB_max=4,GPU=0,automatic_retries=0),
    stop='one registered refinement; if training gates fail, new holdout NOT_RUN; no model enlargement, GPU, architecture sweep or hardware'))
dump(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
print('CPU_REFINEMENT_REGISTERED',sha(HERE/'PREREGISTRATION.json'))
