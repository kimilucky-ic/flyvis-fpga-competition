"""One frozen three-step bundle, created only when the operator requests it."""
from datetime import datetime,timedelta,timezone
import hashlib,json,secrets,uuid,zipfile
from live_protocol import HERE,load,sha
from joint_camera_controller import source_pins
from joint_camera_protocol import validate_scope
from joint_camera_retained import EXPIRED_RUN,NEXT_EXPIRED_RUN

def save(path,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()

def completed_parent():
    """Explicit admitted run, never a directory scan or an unverified latest file."""
    from live_protocol import require
    active=load(HERE/'runtime/joint_active.json')
    # Explicitly registered accepted captures only; new folders are never admission.
    accepted={
        '836a3b037c84421eb43b0d6d912a66d5':('camera_joint_gpu_start_20261016/actual_camera3_836a3b_audit2','FINAL_AUDIT.json',3),
        '2884821c976c4fb6851d61e17cbc22c5':('camera_joint32_20261016','actual_32step/FINAL_AUDIT.json',32)}
    require(active['run_id'] in accepted,'COMPLETED_PARENT_NOT_REGISTERED')
    folder,relative,count=accepted[active['run_id']]
    admitted=HERE/'evidence'/folder;audit=load(admitted/relative);manifest=load(admitted/'DELIVERY_MANIFEST.json')
    require(audit['status']=='PASS_CAMERA_GPU_FPGA_%dSTEP_SAVED_DATA_PATH_AUDIT'%count
        and audit['run_id']==active['run_id'] and audit['steps']==count,'COMPLETED_PARENT_NOT_ADMITTED')
    require(sha(admitted/relative)==manifest['files'][relative],'COMPLETED_AUDIT_CHANGED')
    require(active['state']=='STOPPED' and active['run_id']==audit['run_id'] and active['session_id']==audit['session_id']
        and all(v==0 for v in active['exit_codes'].values()),'COMPLETED_PC_NOT_STOPPED')
    root=HERE/'runtime/joint'/audit['session_id'];finish=load(root/'PS_FINISH.json')
    require(sha(root/'pc/evidence.fvej')==audit['PC_capture_sha256']
        and sha(root/'ps_retrieved_authorized/evidence.fvej')==finish['PS_capture_sha256']==audit['PS_capture_sha256'],'COMPLETED_PARENT_CAPTURE_CHANGED')
    return {k:finish[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
        'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')}

def build(parent,completed=None):
    package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
    template=package/'templates';metadata=load(HERE/'evidence/camera_joint_start_20261016/retained_metadata.json')
    scope=load(HERE/'evidence/camera_joint_service_review_20261016/scope_draft_r2.json')
    run=uuid.uuid4().hex;root=parent/run;root.mkdir(parents=True,exist_ok=False)
    count=32 if completed else 3
    common=dict(run_id=run,server_session=uuid.uuid4().hex,boot_id=metadata['boot_id'],max_steps=count,
        new_loads=0,new_resets=0,new_allocations=0,kernel_file=metadata['kernel_file'],
        retained_src_address=metadata['src_address'],retained_dst_address=metadata['dst_address'],
        control_port=5790,neural_port=5768,pc_host='192.168.2.89',bind_host='192.168.2.99')
    if completed:
        if completed!=completed_parent():raise ValueError('COMPLETED_PARENT_CHANGED_BEFORE_BUILD')
        transfer_fields=dict(completed_parent=completed)
    else:
        previous=HERE/'runtime/joint_manual/d162cb0d6f09035f04e3560ca72cc8a0'/NEXT_EXPIRED_RUN
        from joint_camera_preparation import verify_prepared_handoff
        previous_body=verify_prepared_handoff(load(previous/'hardware_handoff.json'),load(previous/'scope.json'),previous)
        prior_receipt_sha=hashlib.sha256(json.dumps(previous_body['preparation_receipt'],sort_keys=True).encode()).hexdigest()
        transfer_fields=dict(transfer_from_expired_run=NEXT_EXPIRED_RUN,prior_preparation_receipt_sha256=prior_receipt_sha)
    plan=load(template/'PLAN_NOT_AUTHORIZED.json');plan.update(common,
        status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        operation='TRANSFER_COMPLETED_CAMERA_OWNER_READ20' if completed else 'TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20',original_source_run=plan['source_run'])
    plan.update(completed_parent=completed) if completed else plan.update(expired_run_id=NEXT_EXPIRED_RUN,prior_preparation_receipt_sha256=prior_receipt_sha)
    plan_sha=save(root/'PLAN.json',plan)
    declaration=load(template/'HARDWARE_HANDOFF_NOT_PREPARED.json')
    declaration.update({k:common[k] for k in ('run_id','server_session','boot_id')})
    declaration.update(status='DECLARED_NOT_PREPARED',execution_authority='APPROVED_BY_HUMAN',plan_sha256=plan_sha,
        listener_id=uuid.uuid4().hex,clock_policy='PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1',**transfer_fields,
        pc_authority_endpoint=dict(host='192.168.2.89',port=18791),
        endpoint=dict(host='192.168.2.99',port=5768),control_endpoint=dict(host='192.168.2.99',port=5790))
    declaration['capabilities']['max_steps']=count
    declaration['control_config']=dict(run_id=run,server_session=common['server_session'],plan_sha256=plan_sha,control_key=secrets.token_hex(32))
    for name,digest in declaration['software_sha256'].items():
        if sha(package/name)!=digest:raise ValueError('FROZEN_HARDWARE_HELPER_CHANGED '+name)
    declaration_sha=save(root/'HARDWARE_DECLARATION.json',declaration)
    now=datetime.now(timezone.utc)
    scope.update({k:common[k] for k in ('run_id','server_session','boot_id','max_steps')})
    scope.update(status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        human_authorization_reference='CURRENT_CHAT_20261016_START_REAL_CAMERA_EXPERIMENT_32_STEP' if completed else 'CURRENT_CHAT_USER_MANUAL_BOARD_LINE2_SOLE_OWNER_THREE_STEP',
        session_id=uuid.uuid4().hex,gpu_lease_id=uuid.uuid4().hex,comparison_id='CAMERA_'+run,
        capture_duration_s=30 if completed else 10,max_worker_s=300 if completed else 180,
        recording_required_before_camera=bool(completed),
        validation_policy='SAME_OLD_CPU_POST_RUN',runtime_audit_policy='LOADED_STATIC_START_END_HASH/v1',
        start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=598 if completed else 298)).isoformat(),
        hardware_declaration_sha256=declaration_sha,source_sha256=source_pins())
    scope.pop('hardware_handoff_sha256',None);validate_scope(scope);scope_sha=save(root/'scope.json',scope)
    config=load(template/'PRIVATE_CONFIG_NOT_PREPARED.json');config.update(common)
    config.update(status='APPROVED_FOR_PREPARATION',prepared_status='PREPARED_FOR_THIS_CAMERA_RUN',
        execution_authority='APPROVED_BY_HUMAN',human_authorization_reference='EXACT_SCOPE_'+scope_sha,
        listener_id=declaration['listener_id'],scope_sha256=scope_sha,plan_sha256=plan_sha,
        **transfer_fields,
        control_key=declaration['control_config']['control_key'],
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
        '都说你全权负责了你让7干嘛由你来告诉我我要启动什么','那就开始真实实验吧',
        '2026-10-16 再跑一轮32步短测；板端准备由用户手动，电脑侧由②负责；查清长停顿，对比前后，第一步前录像；原模型、精度和必要校验不变'],scope_sha256=scope_sha,
        operator='HUMAN_EXECUTES_BOARD_CELL',limits=dict(max_steps=count,capture_duration_s=scope['capture_duration_s'],max_worker_s=scope['max_worker_s'],
        new_loads=0,new_resets=0,new_allocations=0,automatic_retry=False)))
    save(root/'BUNDLE_PUBLIC.json',dict(root=str(root),archive=str(archive),archive_sha256=sha(archive),run_id=run,
        session_id=scope['session_id'],scope_sha256=scope_sha,end_utc=scope['end_utc'],max_steps=count))
    return root,archive
