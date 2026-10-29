"""Build only; no device import, socket, GPU or camera operation."""
import ast,base64,hashlib,json,uuid,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv=load(P/'ACTUAL_CURRENT_BOOT_INVENTORY.json')
run=uuid.uuid4().hex;root=P/('LINE2_COLD_INIT_'+run);root.mkdir(exist_ok=False)
plan=dict(schema='flyvis-manual-fresh-initialization/v1',execution_authority='USER_MANUAL_EXECUTION_REQUIRED',
    run_id=run,max_steps=0,automatic_retry=False,new_loads=1,new_resets=1,new_allocations=2,
    boot_id=inv['boot_id'],kernel_file=inv['kernel_file'],bit_sha256=inv['image_files'][0]['sha256'],hwh_sha256=inv['image_files'][1]['sha256'],
    source_constructor='UNCHANGED_a3ready.board_service.PLDriver.init__',
    human_authorization='2026-10-18 user confirmed line11 released; switch to line7 and run32',
    camera_scope='SEPARATE_NEW_32STEP_SCOPE_AFTER_INITIALIZATION_RECEIPT')
save(root/'INIT_PLAN.json',plan)
config=dict(mode='MANUAL_FRESH_INIT_THEN_READ20/v1',run_id=run,boot_id=inv['boot_id'],kernel_file=inv['kernel_file'],plan=plan,
    plan_sha256=sha(root/'INIT_PLAN.json'),test_fixture=False,execution_authority='HUMAN_MANUAL_CELL_ONLY',
    bit_path=inv['image_files'][0]['path'],bit_sha256=plan['bit_sha256'],hwh_sha256=plan['hwh_sha256'])
save(root/'INIT_CONFIG.json',config)
package=G.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
runtime={}
for name,digest in load(package/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256'].items():
    raw=(package/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);runtime[name]=digest
for name,source in [('prepare_camera.py','joint_camera_board_entry.py'),('fresh_initializer.py','joint_camera_fresh.py')]:
    raw=(G/source).read_bytes();ast.parse(raw,feature_version=(3,8));(root/name).write_bytes(raw);runtime[name]=sha(G/source)
save(root/'RUNTIME_SHA256.json',runtime)
archive=P/(root.name+'.zip')
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for f in sorted(root.rglob('*')):
        if f.is_file():z.write(f,f.relative_to(root).as_posix())
prefix='''# HUMAN AUTHORIZED: one A3R1 load, one DMA init reset, two CMA buffers; no STEP here.
from pathlib import Path
import hashlib,json,zipfile,importlib.util,sys,base64,io,urllib.request,hmac
from ipykernel.connect import get_connection_file
from pynq import Device
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==%r,'Boot changed; stop'
assert Path(get_connection_file()).name==%r,'Kernel changed; stop'
assert not any(n.endswith('_service_instance') for n in list(globals())),'Service owner exists; stop'
assert 'line2_fresh_initialized' not in globals() and 'line2_cold_init_started' not in globals(),'Initialization already attempted; do not retry'
assert str(getattr(Device.active_device,'bitfile_name',None))==%r,'Loaded image changed; stop'
assert hashlib.sha256(Path(Device.active_device.bitfile_name).read_bytes()).hexdigest()==%r,'Prior image file changed; stop'
line2_init_root=Path.cwd()/%r
assert not line2_init_root.exists(),'Initialization directory exists; do not retry'
line2_init_raw=base64.b64decode(%r,validate=True)
assert hashlib.sha256(line2_init_raw).hexdigest()==%r,'Initialization package changed'
with zipfile.ZipFile(io.BytesIO(line2_init_raw)) as line2_zip:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in line2_zip.namelist())
    line2_init_root.mkdir();line2_zip.extractall(line2_init_root)
assert hashlib.sha256((line2_init_root/'INIT_PLAN.json').read_bytes()).hexdigest()==%r,'Initialization plan changed'
line2_init_config=json.loads((line2_init_root/'INIT_CONFIG.json').read_text(encoding='utf8'))
line2_init_runtime=json.loads((line2_init_root/'RUNTIME_SHA256.json').read_text(encoding='utf8'))
line2_loader_spec=importlib.util.spec_from_file_location('line2_cold_loader_%s',line2_init_root/'prepare_camera.py')
line2_loader=importlib.util.module_from_spec(line2_loader_spec);line2_loader_spec.loader.exec_module(line2_loader)
line2_init_package=line2_loader.load_pinned_package(line2_init_root,line2_init_config,line2_init_runtime)
line2_initializer_spec=importlib.util.spec_from_file_location('line2_cold_initializer_%s',line2_init_root/'fresh_initializer.py')
line2_initializer=importlib.util.module_from_spec(line2_initializer_spec);line2_initializer_spec.loader.exec_module(line2_initializer)
line2_cold_init_started=True
line2_fresh_initialized=line2_initializer.initialize(line2_init_root,line2_init_config,line2_init_package)
print('LINE2_FRESH_INITIALIZED '+json.dumps(line2_fresh_initialized.receipt,sort_keys=True),flush=True)
'''%(inv['boot_id'],inv['kernel_file'],inv['loaded_bitfile_metadata'],inv['prior_bit_sha256'],root.name,
    base64.b64encode(archive.read_bytes()).decode(),sha(archive),config['plan_sha256'],run,run)
ast.parse(prefix,feature_version=(3,8));prefix_file=P/'cold_init_prefix.py';prefix_file.write_text(prefix,encoding='utf-8')
meta=dict(status='AWAITING_USER_MANUAL_INITIALIZATION_NOT_EXECUTED',root=str(root),archive=str(archive),archive_sha256=sha(archive),
    prefix=str(prefix_file),prefix_sha256=hashlib.sha256(prefix.encode()).hexdigest(),run_id=run,plan_sha256=config['plan_sha256'],
    boot_id=inv['boot_id'],kernel_file=inv['kernel_file'],new_loads=1,new_resets=1,new_allocations=2,neural_steps=0)
save(P/'COLD_INIT_PACKAGE.json',meta)
print(json.dumps({k:v for k,v in meta.items() if k not in ('prefix','root')},indent=2))
