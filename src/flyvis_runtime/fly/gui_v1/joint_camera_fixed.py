"""Installation notebook and first preparation glue for the existing workbench.

No new server, neural owner or hardware driver. Import and package export do
not connect to a board or start GPU/camera/GUI. The user runs the notebook.
"""
import ast,base64,hashlib,io,json,secrets,threading,uuid,zipfile
from pathlib import Path
from live_protocol import HERE,load,write,sha,require,host_path
from joint_camera_manual import ManualGate,board_cell,cold_board_cell,mac

BIT_PATH='/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/A3R1_FRESH_READY3_05aa0e5238e14b3aad54bb695882d043/neuron_a.bit'
NOTEBOOK=HERE/'FlyVis摄像头联合实验.ipynb'
INSTALLATION=HERE/'runtime/fixed_camera/INSTALLATION_PRIVATE.json'

def export_notebook():
    if INSTALLATION.exists():config=load(INSTALLATION)
    else:
        config=dict(installation_id=uuid.uuid4().hex,key=secrets.token_hex(32),
            pc_url='http://192.168.2.89:18790',bit_path=BIT_PATH)
        write(INSTALLATION,config)
    source=(HERE/'joint_camera_fixed_board.py').read_text(encoding='utf-8')
    ast.parse(source,feature_version=(3,8))
    cell=('''# 每次运行相同代码；准备逻辑和私有配对信息随本Notebook保存。
from pathlib import Path
import json,hashlib
line2_entry=json.loads(Path('FlyVis摄像头联合实验.ipynb').read_text(encoding='utf-8'))['metadata']['flyvis_fixed_entry']
assert hashlib.sha256(line2_entry['source'].encode()).hexdigest()==line2_entry['source_sha256'],'Notebook准备程序已改变'
exec(compile(line2_entry['source'],'FLYVIS_FIXED_NOTEBOOK_ENTRY','exec'),globals(),globals())
run(globals(),line2_entry['config'])
''')
    notebook=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),
        flyvis_fixed_entry=dict(config=config,source=source,source_sha256=hashlib.sha256(source.encode()).hexdigest())),
        cells=[dict(cell_type='markdown',id='instructions',metadata={},source=[
            '# FlyVis 摄像头 / 固定科学输入 GPU–FPGA 联合实验\n',
            '首次将本文件上传板端保存，之后一直打开它，不用更换代码。\n',
            '先双击电脑“打开FlyVis实验台”，再运行下面唯一代码格。新内核会要求你输入“准备”，确认板卡已释放并允许一次初始化。\n',
            '先在实验台选择摄像头或固定实验及条件。摄像头运行60秒；固定实验逐一处理485步，模型步长仍5ms。停止后等待自动保存和核验。\n',
            '板卡占用或状态不确定会停止，不自动关闭其他内核、不重试、不复位。此文件含本机私有配对信息，请勿公开。\n',
            '**软件协议已测试不等于实板验收。长实验和新内核首次使用仍待用户释放板卡后实测。**\n']),
            dict(cell_type='code',id='prepare-camera',metadata={},execution_count=None,outputs=[],source=cell.splitlines(keepends=True))])
    write(NOTEBOOK,notebook)
    return config

def build_cold(parent,inventory):
    """Freeze an exact current-boot/kernel zero-STEP plan; never execute it."""
    from hybrid_full485 import Full485Contract
    c=Full485Contract();w=c.wire
    require(inventory['bit_path']==BIT_PATH and inventory['bit_sha256']==w.BIT_SHA
        and inventory['hwh_sha256']==w.HWH_SHA,'FIXED_WRONG_IMAGE')
    require(inventory['existing_run'] is None and isinstance(inventory['pid'],int)
        and inventory['pid']>0 and uuid.UUID(inventory['boot_id'])
        and inventory['kernel_file'].startswith('kernel-') and inventory['kernel_file'].endswith('.json'),'FIXED_CURRENT_INVENTORY')
    run=uuid.uuid4().hex;root=parent/('LINE2_COLD_INIT_'+run);root.mkdir(parents=True,exist_ok=False)
    plan=dict(schema='flyvis-manual-fresh-initialization/v1',execution_authority='USER_MANUAL_EXECUTION_REQUIRED',
        run_id=run,max_steps=0,automatic_retry=False,new_loads=1,new_resets=1,new_allocations=2,
        boot_id=inventory['boot_id'],kernel_file=inventory['kernel_file'],bit_sha256=w.BIT_SHA,hwh_sha256=w.HWH_SHA)
    write(root/'INIT_PLAN.json',plan)
    config=dict(mode='MANUAL_FRESH_INIT_THEN_READ20/v1',run_id=run,boot_id=inventory['boot_id'],kernel_file=inventory['kernel_file'],
        plan=plan,plan_sha256=sha(root/'INIT_PLAN.json'),test_fixture=False,execution_authority='HUMAN_MANUAL_CELL_ONLY',
        bit_path=BIT_PATH,bit_sha256=w.BIT_SHA,hwh_sha256=w.HWH_SHA)
    write(root/'INIT_CONFIG.json',config)
    package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
    runtime=load(package/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')['software_sha256'].copy()
    files={}
    for name,digest in runtime.items():
        raw=(package/name).read_bytes();require(hashlib.sha256(raw).hexdigest()==digest,'FIXED_FROZEN_HELPER_CHANGED '+name);files[name]=raw
    for name,src in [('prepare_camera.py','joint_camera_board_entry.py'),('fresh_initializer.py','joint_camera_fresh.py')]:
        files[name]=(HERE/src).read_bytes();runtime[name]=hashlib.sha256(files[name]).hexdigest()
    for name in ('INIT_PLAN.json','INIT_CONFIG.json'):files[name]=(root/name).read_bytes()
    files['RUNTIME_SHA256.json']=json.dumps(runtime).encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,raw in files.items():z.writestr(name,raw)
    archive=root/'INITIALIZATION.zip';archive.write_bytes(buf.getvalue())
    prefix='''import urllib.request,json,hashlib,hmac,base64,zipfile,io,importlib.util,sys
from pathlib import Path
line2_init_bytes=base64.b64decode(%r,validate=True)
assert hashlib.sha256(line2_init_bytes).hexdigest()==%r,'Initialization ZIP changed'
line2_init_root=Path.cwd()/%r
assert not line2_init_root.exists() and 'line2_fresh_initialized' not in globals(),'Initialization already attempted; stop'
with zipfile.ZipFile(io.BytesIO(line2_init_bytes)) as line2_archive:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in line2_archive.namelist())
    line2_init_root.mkdir();line2_archive.extractall(line2_init_root)
line2_init_config=json.loads((line2_init_root/'INIT_CONFIG.json').read_text())
line2_init_runtime=json.loads((line2_init_root/'RUNTIME_SHA256.json').read_text())
line2_spec=importlib.util.spec_from_file_location('line2_fixed_loader_'+line2_init_config['run_id'],line2_init_root/'prepare_camera.py')
line2_loader=importlib.util.module_from_spec(line2_spec);line2_spec.loader.exec_module(line2_loader)
line2_package=line2_loader.load_pinned_package(line2_init_root,line2_init_config,line2_init_runtime)
line2_spec=importlib.util.spec_from_file_location('line2_fixed_initializer_'+line2_init_config['run_id'],line2_init_root/'fresh_initializer.py')
line2_initializer=importlib.util.module_from_spec(line2_spec);line2_spec.loader.exec_module(line2_initializer)
line2_fresh_initialized=line2_initializer.initialize(line2_init_root,line2_init_config,line2_package)
print('LINE2_FRESH_INITIALIZED '+json.dumps(line2_fresh_initialized.receipt,sort_keys=True))
'''%(base64.b64encode(buf.getvalue()).decode(),sha(archive),root.name)
    ast.parse(prefix,feature_version=(3,8));path=root/'INITIALIZE.py';path.write_bytes(prefix.encode('utf-8'))
    return dict(config=config,prefix=str(path),prefix_sha256=sha(path))

class FixedPreparation:
    def init__(self,parent,family,endpoint,installation):
        self.parent,self.family,self.endpoint,self.installation=parent,family,endpoint,installation
        self.gate=None;self.ready=threading.Event();self.lock=threading.RLock();self.nonces=set()
    def enter(self,packet,peer):
        with self.lock:
            require(peer=='192.168.2.99' and set(packet)=={'body','mac'}
                and secrets.compare_digest(mac(packet['body'],self.installation['key']),packet['mac']),'FIXED_NOTEBOOK_AUTH')
            body=packet['body'];inv=body['inventory'];nonce=body['nonce']
            require(body['schema']=='flyvis-fixed-notebook-request/v1' and body['installation_id']==self.installation['installation_id']
                and uuid.UUID(hex=nonce).hex==nonce and nonce not in self.nonces,'FIXED_NOTEBOOK_REQUEST')
            if self.gate is not None:
                require(inv['existing_run'] is not None,'FIXED_PREPARATION_ALREADY_ATTEMPTED')
                h=self.endpoint.handoff
                require(h and inv['existing_run']=={k:h[k] for k in ('run_id','scope_sha256','boot_id')},
                    'FIXED_EXISTING_OWNER_CHANGED')
                reply=dict(status='ALREADY_PREPARED',nonce=nonce,inventory=inv)
            else:
                if inv['existing_run'] is None:
                    require(body['initialize_approved'] is True,'FIXED_INITIALIZATION_NOT_AUTHORIZED')
                    write(self.parent/'HUMAN_PREPARATION_REQUEST.json',packet)
                    cold=build_cold(self.parent,inv)
                    gate=ManualGate(self.parent,cold_init=cold,minimal_compute=True,live5=True,repeat_family=self.family)
                    source=cold_board_cell(gate.token,cold)
                else:
                    from joint_camera_controller import ACTIVE
                    from joint_camera_audit import accepted_parent
                    active=load(ACTIVE);root=host_path(active['root'])
                    require(active['state']=='STOPPED' and inv['existing_run']==dict(run_id=active['run_id'],
                        scope_sha256=sha(root/'scope.json'),boot_id=load(root/'scope.json')['boot_id']),'FIXED_PC_PARENT_CHANGED')
                    selection=accepted_parent(root)  # Missing audit blocks; never invent acceptance.
                    require(selection['fresh']['kernel_file']==inv['kernel_file'],'FIXED_KERNEL_CHANGED')
                    gate=ManualGate(self.parent,**selection,minimal_compute=True,live5=True,repeat_family=self.family)
                    source=board_cell(gate.token,**selection)
                source+='\ncamera_entry.install_repeat(camera_new_root,globals())\n'
                self.gate=gate;self.endpoint.select(gate);self.ready.set()
                reply=dict(status='PREPARE',nonce=nonce,inventory=inv,source=source,source_sha256=hashlib.sha256(source.encode()).hexdigest())
            self.nonces.add(nonce)
            return dict(body=reply,mac=mac(reply,self.installation['key']))
