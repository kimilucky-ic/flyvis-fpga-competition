"""One frozen three-step bundle, created only when the operator requests it."""
from datetime import datetime,timedelta,timezone
import hashlib,json,secrets,uuid,zipfile
from live_protocol import HERE,load,sha
from joint_camera_controller import source_pins
from joint_camera_protocol import validate_scope
from joint_camera_retained import EXPIRED_RUN

def save(path,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()

def build(parent):
    package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
    template=package/'templates';metadata=load(HERE/'evidence/camera_joint_start_20261016/retained_metadata.json')
    scope=load(HERE/'evidence/camera_joint_service_review_20261016/scope_draft_r2.json')
    run=uuid.uuid4().hex;root=parent/run;root.mkdir(parents=True,exist_ok=False)
    common=dict(run_id=run,server_session=uuid.uuid4().hex,boot_id=metadata['boot_id'],max_steps=3,
        new_loads=0,new_resets=0,new_allocations=0,kernel_file=metadata['kernel_file'],
        retained_src_address=metadata['src_address'],retained_dst_address=metadata['dst_address'],
        control_port=5790,neural_port=5768,pc_host='192.168.2.89',bind_host='192.168.2.99')
    plan=load(template/'PLAN_NOT_AUTHORIZED.json');plan.update(common,
        status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        operation='TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20',expired_run_id=EXPIRED_RUN,original_source_run=plan['source_run'])
    plan_sha=save(root/'PLAN.json',plan)
    declaration=load(template/'HARDWARE_HANDOFF_NOT_PREPARED.json')
    declaration.update({k:common[k] for k in ('run_id','server_session','boot_id')})
    declaration.update(status='DECLARED_NOT_PREPARED',execution_authority='APPROVED_BY_HUMAN',plan_sha256=plan_sha,
        listener_id=uuid.uuid4().hex,clock_policy='PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1',transfer_from_expired_run=EXPIRED_RUN,
        pc_authority_endpoint=dict(host='192.168.2.89',port=18791),
        endpoint=dict(host='192.168.2.99',port=5768),control_endpoint=dict(host='192.168.2.99',port=5790))
    declaration['capabilities']['max_steps']=3
    declaration['control_config']=dict(run_id=run,server_session=common['server_session'],plan_sha256=plan_sha,control_key=secrets.token_hex(32))
    for name,digest in declaration['software_sha256'].items():
        if sha(package/name)!=digest:raise ValueError('FROZEN_HARDWARE_HELPER_CHANGED '+name)
    declaration_sha=save(root/'HARDWARE_DECLARATION.json',declaration)
    now=datetime.now(timezone.utc)
    scope.update({k:common[k] for k in ('run_id','server_session','boot_id','max_steps')})
    scope.update(status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        human_authorization_reference='CURRENT_CHAT_USER_MANUAL_BOARD_LINE2_SOLE_OWNER_THREE_STEP',
        session_id=uuid.uuid4().hex,gpu_lease_id=uuid.uuid4().hex,comparison_id='CAMERA_'+run,
        start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=298)).isoformat(),
        hardware_declaration_sha256=declaration_sha,source_sha256=source_pins())
    scope.pop('hardware_handoff_sha256',None);validate_scope(scope);scope_sha=save(root/'scope.json',scope)
    config=load(template/'PRIVATE_CONFIG_NOT_PREPARED.json');config.update(common)
    config.update(status='APPROVED_FOR_PREPARATION',prepared_status='PREPARED_FOR_THIS_CAMERA_RUN',
        execution_authority='APPROVED_BY_HUMAN',human_authorization_reference='EXACT_SCOPE_'+scope_sha,
        listener_id=declaration['listener_id'],scope_sha256=scope_sha,plan_sha256=plan_sha,
        transfer_from_expired_run=EXPIRED_RUN,control_key=declaration['control_config']['control_key'],
        pc_authority_endpoint=declaration['pc_authority_endpoint'])
    for key in ('max_worker_s','start_utc','end_utc'):config[key]=scope[key]
    save(root/'PRIVATE_CONFIG.json',config)
    own={'prepare_camera.py':'joint_camera_board_entry.py','retained_transfer.py':'joint_camera_retained.py'}
    runtime=dict(declaration['software_sha256']);runtime.update({dst:sha(HERE/src) for dst,src in own.items()})
    save(root/'RUNTIME_SHA256.json',runtime)
    archive=root/('CAMERA3_'+run+'.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in declaration['software_sha256']:z.writestr(name,(package/name).read_bytes())
        for dst,src in own.items():z.writestr(dst,(HERE/src).read_bytes())
        for name in ('PLAN.json','scope.json','PRIVATE_CONFIG.json','RUNTIME_SHA256.json'):z.write(root/name,name)
    save(root/'USER_AUTHORIZATION.json',dict(direct_user_messages=['7好了开始吧','老规矩要上版的东西我来弄',
        '都说你全权负责了你让7干嘛由你来告诉我我要启动什么'],scope_sha256=scope_sha,
        operator='HUMAN_EXECUTES_BOARD_CELL',limits=dict(max_steps=3,capture_duration_s=10,max_worker_s=180,
        new_loads=0,new_resets=0,new_allocations=0,automatic_retry=False)))
    save(root/'BUNDLE_PUBLIC.json',dict(root=str(root),archive=str(archive),archive_sha256=sha(archive),run_id=run,
        session_id=scope['session_id'],scope_sha256=scope_sha,end_utc=scope['end_utc'],max_steps=3))
    return root,archive
