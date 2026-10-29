"""Build a reviewable manual zero-STEP initialization package; never executes it."""
import ast,hashlib,json,uuid,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
inventory=dict(schema='flyvis-current-boot-software-inventory/v1',boot_id='35df570f-b50d-4cfc-aafc-0e35baf651df',
    kernel_file='kernel-4417274b-c932-4454-9872-47b19244e213.json',kernel_processes=[dict(pid=793,kernel_files=['kernel-4417274b-c932-4454-9872-47b19244e213.json'])],
    python='/usr/local/share/pynq-venv/bin/python3',pynq_version_metadata='2.7.0',
    cwd='/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1',existing_owners=[],neural_or_control_listeners=[],
    image_files=[dict(path='/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/A3R1_FRESH_READY3_05aa0e5238e14b3aad54bb695882d043/neuron_a.bit',
        exists=True,sha256='b607ea58005046f09f01bc7359c673dbd5e40b4de12b4169fca79ce88e43fd16'),
        dict(path='/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/A3R1_FRESH_READY3_05aa0e5238e14b3aad54bb695882d043/neuron_a.hwh',
        exists=True,sha256='54d271dc8aff904a50ca4fb0ff433f1810b0d486cf80f1daed2c204bc88d084c')],
    source='USER_MANUALLY_EXECUTED_READ_ONLY_BOOT_CELL_20261017',new_loads=0,new_resets=0,new_allocations=0,new_MMIO_reads=0,new_MMIO_writes=0,new_DMA=0)
save(P/'ACTUAL_CURRENT_BOOT_INVENTORY.json',inventory)
assert load(P/'CPU_RESULT.json')['status']=='PASS_CPU_ONLY'
run=uuid.uuid4().hex;root=P/('LINE2_FRESH_INIT_'+run);root.mkdir()
plan=dict(schema='flyvis-manual-fresh-initialization/v1',execution_authority='USER_MANUAL_EXECUTION_REQUIRED',
    run_id=run,max_steps=0,automatic_retry=False,new_loads=1,new_resets=1,new_allocations=2,
    boot_id=inventory['boot_id'],kernel_file=inventory['kernel_file'],
    bit_sha256=inventory['image_files'][0]['sha256'],hwh_sha256=inventory['image_files'][1]['sha256'],
    source_constructor='UNCHANGED_a3ready.board_service.PLDriver.init__',
    camera_scope='SEPARATE_NEW_32STEP_SCOPE_AFTER_INITIALIZATION_RECEIPT',
    preserved_old_run='2884821c976c4fb6851d61e17cbc22c5')
save(root/'INIT_PLAN.json',plan)
config=dict(mode='MANUAL_FRESH_INIT_THEN_READ20/v1',run_id=run,boot_id=inventory['boot_id'],kernel_file=inventory['kernel_file'],
    plan=plan,plan_sha256=sha(root/'INIT_PLAN.json'),test_fixture=False,execution_authority='HUMAN_MANUAL_CELL_ONLY',
    bit_path=inventory['image_files'][0]['path'],bit_sha256=plan['bit_sha256'],hwh_sha256=plan['hwh_sha256'])
save(root/'INIT_CONFIG.json',config)
package=G.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
pins=load(package/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256'];runtime={}
for name,digest in pins.items():
    raw=(package/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);runtime[name]=digest
for name,source in (('prepare_camera.py','joint_camera_board_entry.py'),('fresh_initializer.py','joint_camera_fresh.py')):
    raw=(G/source).read_bytes();ast.parse(raw,feature_version=(3,8));(root/name).write_bytes(raw);runtime[name]=sha(G/source)
save(root/'RUNTIME_SHA256.json',runtime)
archive=P/(root.name+'.zip')
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for f in sorted(root.rglob('*')):
        if f.is_file():z.write(f,f.relative_to(root).as_posix())
cell=f'''# LINE2 冷启动初始化：你手动执行一次；1次A3R1加载、1次DMA初始化复位、2次CMA分配；0次STEP
# 仅当前boot和内核；失败即停，不重跑；不启动GPU、摄像头或板端监听。
from pathlib import Path
import hashlib,json,zipfile,importlib.util,sys
line2_init_archive=Path.cwd()/{archive.name!r}
assert hashlib.sha256(line2_init_archive.read_bytes()).hexdigest()=={sha(archive)!r}, "Initialization ZIP SHA mismatch"
line2_init_root=Path.cwd()/{root.name!r}
assert not line2_init_root.exists(), "Initialization directory exists; stop, do not retry"
assert not any(n.endswith('_service_instance') and hasattr(v,'driver') for n,v in list(globals().items())), "Existing service owner; stop"
with zipfile.ZipFile(line2_init_archive) as z:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    line2_init_root.mkdir();z.extractall(line2_init_root)
assert hashlib.sha256((line2_init_root/'INIT_PLAN.json').read_bytes()).hexdigest()=={config['plan_sha256']!r}, "Exact initialization plan changed"
line2_init_config=json.loads((line2_init_root/'INIT_CONFIG.json').read_text(encoding='utf8'))
line2_init_runtime=json.loads((line2_init_root/'RUNTIME_SHA256.json').read_text(encoding='utf8'))
line2_loader_spec=importlib.util.spec_from_file_location('line2_fresh_loader_{run}',line2_init_root/'prepare_camera.py')
line2_loader=importlib.util.module_from_spec(line2_loader_spec);line2_loader_spec.loader.exec_module(line2_loader)
line2_init_package=line2_loader.load_pinned_package(line2_init_root,line2_init_config,line2_init_runtime)
line2_initializer_spec=importlib.util.spec_from_file_location('line2_initializer_{run}',line2_init_root/'fresh_initializer.py')
line2_initializer=importlib.util.module_from_spec(line2_initializer_spec);line2_initializer_spec.loader.exec_module(line2_initializer)
line2_fresh_initialized=line2_initializer.initialize(line2_init_root,line2_init_config,line2_init_package)
print('LINE2_FRESH_INITIALIZED '+json.dumps(line2_fresh_initialized.receipt,sort_keys=True))
'''
ast.parse(cell,feature_version=(3,8));(P/'next_fresh_init_cell.py').write_text(cell,encoding='utf8')
save(P/'INITIALIZATION_PACKAGE.json',dict(status='AWAITING_USER_MANUAL_INITIALIZATION_NOT_EXECUTED',root=str(root),archive=str(archive),
    archive_sha256=sha(archive),plan_sha256=config['plan_sha256'],run_id=run,boot_id=inventory['boot_id'],kernel_file=inventory['kernel_file'],
    new_loads=1,new_resets=1,new_allocations=2,neural_steps=0,neural_listeners=0,cell=str(P/'next_fresh_init_cell.py')))
print(json.dumps(load(P/'INITIALIZATION_PACKAGE.json'),indent=2))
