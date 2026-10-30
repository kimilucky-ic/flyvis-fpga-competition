from contract import *
import uuid,ast,shutil

assert not (HERE/'PLAN.json').exists()
assert shutil.disk_usage(HERE).free>4*1024**3
registry=load(FLY/'gui_v1/live_registry.json')
old=HERE.parent/'cnn_t4t5_mp4_holdout_20261016'
source=HERE.parent/'cnn_t4t5_replacement_20261016'
assets=dict(video=old/'videos/ON75_v12_full.mp4',sampler=old/'SAMPLER.npz',
    mapping=source/'mapping.npz',CNN_source=source/'cnn.py',
    CNN_weights=HERE.parent/'cnn_t4t5_cpu_refinement_20261016/training/ridge.pt',
    R_manifest=source/'R_CANDIDATE.json',CPU_input=old/'inputs/ON75_v12_full.npy',
    CPU_Full=old/'runs/ON75_v12_full/Full/states_raw.npy',CPU_CNN=old/'runs/ON75_v12_full/CNN/states_raw.npy',
    CPU_Full_flow=old/'runs/ON75_v12_full/Full/flow.npy',CPU_CNN_flow=old/'runs/ON75_v12_full/CNN/flow.npy')
for key in ['full','r_only','decoder','decoder_contract','runner_lease','identity','parameters','initial']:
    pin=registry['pins'][key];assert sha(pin['path'])==pin['sha256'];assets[key]=path(pin['path'])
pins={str(p):sha(p) for p in assets.values()}
for name in ['contract.py','prepare.py','worker.py','viewer.py','audit.py','index.html']:
    p=HERE/name
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
    pins[str(p)]=sha(p)
assert sha(assets['CNN_weights'])=='cd00f98ab438e743b5437e05725830dba353183ac6f2d882a195c65b1ec2c016'
plan=dict(schema='line4-GPU-and-visual-stream/v1',run_id=uuid.uuid4().hex,pins=pins,
    assets={k:str(v) for k,v in assets.items()},runtime=registry['runtime'],
    user_authorization='我说的就是两个同时跑通，gpu与视觉同时运行，你先做一下看看',
    GPU_processes=1,shared_lease=True,board_operations=0,camera_operations=0,training_updates=0,
    max_frames=500,steps_per_backend=1000,dt_s=.005,target_steps_per_wall_second=100,
    decoder_interval_steps=10,display='input + actual FullGPU flow + actual CNNReplacementGPU flow during computation',
    backend='two independent live states, same current decoded frame, sequential kernels in ONE GPU worker; no reference state fed into CNN',
    CUDA_FP32=dict(deterministic=True,TF32=False),numerical_CPU_check=dict(atol=1e-5,rtol=1e-5),
    budgets=dict(GPU_total_s=300,GPU_queue_s=15,viewer_attach_s=120,source_loop_s=90,read_only_viewer_lifetime_s=600),
    acceptance='1000 own-state commits each backend, zero nativeH in CNN, exact video inputs, CPU comparison, decoder/model unchanged, >=5 browser renderACK during RUNNING and >=3 distinct displayed state IDs; no precomputed activity playback',
    limits='controlled existing5s MP4, known stimulus for integration only; target100steps/s means half model speed, not strict real time or new functional generalization; FPGA NOT_CONNECTED; no production GUI changes or retries')
write(HERE/'PLAN.json',plan);write(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PLAN.json'),time_ns=time.time_ns()))
print(json.dumps(dict(run_id=plan['run_id'],plan_sha=sha(HERE/'PLAN.json'),files=len(pins),GPU_not_started=True)))
