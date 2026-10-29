"""Freeze one user-authorized three-step run. No network or device access."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib, json, secrets, sys, uuid, zipfile

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
from joint_camera_controller import source_pins
from joint_camera_protocol import validate_scope

def save(path,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    with path.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()

def main():
    package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
    template=package/'templates'
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    scope=read(HERE/'evidence/camera_joint_service_review_20261016/scope_draft_r2.json')
    metadata=read(Path(__file__).parent/'retained_metadata.json')
    run=uuid.uuid4().hex; root=HERE/'runtime/joint_prepare'/run;root.mkdir(parents=True,exist_ok=False)
    common=dict(run_id=run,server_session=uuid.uuid4().hex,boot_id=metadata['boot_id'],max_steps=3,
        new_loads=0,new_resets=0,new_allocations=0,kernel_file=metadata['kernel_file'],
        retained_src_address=metadata['src_address'],retained_dst_address=metadata['dst_address'],
        control_port=5790,neural_port=5768,pc_host='192.168.2.89',bind_host='192.168.2.99')
    plan=read(template/'PLAN_NOT_AUTHORIZED.json');plan.update(common,status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN')
    plan_sha=save(root/'PLAN.json',plan)
    declaration=read(template/'HARDWARE_HANDOFF_NOT_PREPARED.json')
    declaration.update({k:common[k] for k in ('run_id','server_session','boot_id')})
    declaration.update(status='DECLARED_NOT_PREPARED',execution_authority='APPROVED_BY_HUMAN',plan_sha256=plan_sha,
        listener_id=uuid.uuid4().hex,clock_policy='PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1',
        pc_authority_endpoint=dict(host='192.168.2.89',port=18791),
        endpoint=dict(host='192.168.2.99',port=5768),control_endpoint=dict(host='192.168.2.99',port=5790))
    declaration['capabilities']['max_steps']=3
    declaration['control_config']=dict(run_id=run,server_session=common['server_session'],plan_sha256=plan_sha,control_key=secrets.token_hex(32))
    for name,digest in declaration['software_sha256'].items():
        assert hashlib.sha256((package/name).read_bytes()).hexdigest()==digest,name
    decl_sha=save(root/'HARDWARE_DECLARATION.json',declaration)
    now=datetime.now(timezone.utc)
    scope.update({k:common[k] for k in ('run_id','server_session','boot_id','max_steps')})
    scope.update(status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        human_authorization_reference='CURRENT_CHAT_20261016_7_READY_START_BOUNDED_THREE_STEP',
        session_id=uuid.uuid4().hex,gpu_lease_id=uuid.uuid4().hex,comparison_id='CAMERA_'+run,
        start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=298)).isoformat(),
        hardware_declaration_sha256=decl_sha,source_sha256=source_pins())
    scope.pop('hardware_handoff_sha256',None);validate_scope(scope)
    scope_sha=save(root/'scope.json',scope)
    config=read(template/'PRIVATE_CONFIG_NOT_PREPARED.json');config.update(common)
    config.update(status='APPROVED_FOR_PREPARATION',prepared_status='PREPARED_FOR_THIS_CAMERA_RUN',
        execution_authority='APPROVED_BY_HUMAN',human_authorization_reference='EXACT_SCOPE_'+scope_sha,
        listener_id=declaration['listener_id'],scope_sha256=scope_sha,plan_sha256=plan_sha,
        control_key=declaration['control_config']['control_key'],pc_authority_endpoint=declaration['pc_authority_endpoint'])
    for key in ('max_worker_s','start_utc','end_utc'):config[key]=scope[key]
    save(root/'PRIVATE_CONFIG.json',config)
    save(root/'USER_AUTHORIZATION.json',dict(direct_user_messages=['那就由你来开始实验吧先怎么开始','7好了开始吧'],
        accepted_scope=dict(max_steps=3,capture_duration_s=10,max_worker_s=180,scope_seconds=300,
        new_loads=0,new_resets=0,new_allocations=0,automatic_retry=False),scope_sha256=scope_sha,
        origin='Current chat direct human instructions; no authorization inferred from a delivery template'))
    archive=root/('CAMERA3_'+run+'.zip')
    runtime=dict(declaration['software_sha256'])
    runtime['prepare_camera.py']=hashlib.sha256((HERE/'joint_camera_board_entry.py').read_bytes()).hexdigest()
    save(root/'RUNTIME_SHA256.json',runtime)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in declaration['software_sha256']:z.writestr(name,(package/name).read_bytes())
        z.writestr('prepare_camera.py',(HERE/'joint_camera_board_entry.py').read_bytes())
        for name in ('PLAN.json','scope.json','PRIVATE_CONFIG.json','RUNTIME_SHA256.json'):z.write(root/name,name)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    cell="""from pathlib import Path
import hashlib, zipfile, sys
camera3_zip=Path(%r)
assert hashlib.sha256(camera3_zip.read_bytes()).hexdigest()==%r, 'Uploaded bundle SHA mismatch'
camera3_root=Path(%r).resolve()
assert not camera3_root.exists(), 'Run directory already exists; no retry'
with zipfile.ZipFile(camera3_zip) as camera3_archive:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in camera3_archive.namelist())
    camera3_root.mkdir()
    camera3_archive.extractall(camera3_root)
sys.path.insert(0,str(camera3_root))
import prepare_camera
camera3_bundle,camera3_service_instance=prepare_camera.run(camera3_root,latency485_service_instance)
""" % (archive.name,digest,'CAMERA3_'+run)
    (root/'NOTEBOOK_CELL.txt').write_text(cell,encoding='utf-8')
    save(root/'BUNDLE_PUBLIC.json',dict(root=str(root),archive=str(archive),archive_sha256=digest,run_id=run,
        session_id=scope['session_id'],scope_sha256=scope_sha,end_utc=scope['end_utc'],max_steps=3))
    print(json.dumps(read(root/'BUNDLE_PUBLIC.json'),ensure_ascii=False))

if __name__=='__main__':main()
