"""One bounded camera bundle, frozen only on the operator's preparation request."""
from datetime import datetime,timedelta,timezone
import hashlib,json,secrets,uuid,zipfile
from live_protocol import HERE,load,sha
from joint_camera_controller import source_pins
from joint_camera_protocol import validate_scope
from joint_camera_retained import EXPIRED_RUN,NEXT_EXPIRED_RUN
from joint_camera_retained import UNUSED_EXPIRED_RUN,UNUSED_SESSION

UNUSED_RUNTIME_PINS={
    'scope.json':'b81df9bb99a7cd0bcc81c91dd25e5f22f1756421a2de2520212de8003f778c4e',
    'result.json':'257178762c39cfe01f98fc5b96f24e3ffe2f5720df263952c8aec720903fbaa9',
    'worker_exit.json':'040a4586f9b4b78570aaec39d3dfcec70aac44d407b359b039a8758c14ff1352',
    'worker_start_failure.json':'b0e08b3247b2304f5a4d6eac961951c7a6b6c9f2c982b6017ee40e891b737b0d',
    'hardware_handoff.json':'03e40514dd93d292f9ff3bd1a925541b1960694ba11cef68dbc51a4d612e6f76'}
UNUSED_BUNDLE_PINS={
    'scope.json':UNUSED_RUNTIME_PINS['scope.json'],
    'PLAN.json':'800e8682ac4e6a5fbe8865bb2033a56a7d11072df6cf7c782b90d55cdefd0798',
    'PREPARED_PACKET.json':'88f8939f77cf56ebf0c0364482402dd26dad2a71b70fc11321f6b17df82c62d8',
    'HARDWARE_DECLARATION.json':'3fc3538cf77ff4486811fb19a69b55383b1ef6eabac68252e0ecce8452cb97dc'}

def save(path,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()

def completed_capture(run_id):
    """Explicit admitted run, never a directory scan or an unverified latest file."""
    from live_protocol import require
    # Explicitly registered accepted captures only; new folders are never admission.
    accepted={
        '836a3b037c84421eb43b0d6d912a66d5':('camera_joint_gpu_start_20261016/actual_camera3_836a3b_audit2','FINAL_AUDIT.json',3),
        '2884821c976c4fb6851d61e17cbc22c5':('camera_joint32_20261016','actual_32step/FINAL_AUDIT.json',32),
        'b3c166fcae404f878730ec3528f9012b':('camera_joint32_20261017_b3c166fc','actual_audit/FINAL_AUDIT.json',32)}
    require(run_id in accepted,'COMPLETED_PARENT_NOT_REGISTERED')
    folder,relative,count=accepted[run_id]
    admitted=HERE/'evidence'/folder;audit=load(admitted/relative);manifest=load(admitted/'DELIVERY_MANIFEST.json')
    manifest['files']={name.replace('\\','/'):value for name,value in manifest['files'].items()}
    require(audit['status']=='PASS_CAMERA_GPU_FPGA_%dSTEP_SAVED_DATA_PATH_AUDIT'%count
        and audit['run_id']==run_id and audit['steps']==count,'COMPLETED_PARENT_NOT_ADMITTED')
    require(sha(admitted/relative)==manifest['files'][relative],'COMPLETED_AUDIT_CHANGED')
    root=HERE/'runtime/joint'/audit['session_id'];finish=load(root/'PS_FINISH.json')
    require(sha(root/'pc/evidence.fvej')==audit['PC_capture_sha256']
        and sha(root/'ps_retrieved_authorized/evidence.fvej')==finish['PS_capture_sha256']==audit['PS_capture_sha256'],'COMPLETED_PARENT_CAPTURE_CHANGED')
    return {k:finish[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
        'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')}


def completed_parent():
    from live_protocol import require
    active=load(HERE/'runtime/joint_active.json');parent=completed_capture(active['run_id'])
    require(active['state']=='STOPPED' and all(v==0 for v in active['exit_codes'].values()),'COMPLETED_PC_NOT_STOPPED')
    audit_session={'836a3b037c84421eb43b0d6d912a66d5':'19c681c711c94cbdacb7b953b1091611',
        '2884821c976c4fb6851d61e17cbc22c5':'7f111da4437843539eeffef2c6c2546e',
        'b3c166fcae404f878730ec3528f9012b':'f2fd7b4d54a4445daa8a15065c60088e'}
    require(active['session_id']==audit_session[parent['run_id']],'COMPLETED_PC_SESSION')
    return parent


def unused_parent():
    """Admit only the pinned PC prestart failure, not arbitrary zero-count runs.

    This is a PC-side selection, NOT proof the board is currently unused. The
    user's one new cell must independently inspect the actual old owner.
    """
    from live_protocol import require,host_path
    from joint_camera_preparation import verify_prepared_handoff
    active=load(HERE/'runtime/joint_active.json');root=HERE/'runtime/joint'/UNUSED_SESSION
    require(active['state']=='STOPPED' and active['run_id']==UNUSED_EXPIRED_RUN
        and active['session_id']==UNUSED_SESSION and host_path(active['root']).resolve()==root.resolve()
        and active['exit_codes']==dict(gui=0,joint_worker=1),'UNUSED_PC_NOT_STOPPED')
    bundle=HERE/'runtime/joint_manual/d01f349844c82e451121f2c4c516fda4'/UNUSED_EXPIRED_RUN
    for base,pins in ((root,UNUSED_RUNTIME_PINS),(bundle,UNUSED_BUNDLE_PINS)):
        for name,digest in pins.items():require(sha(base/name)==digest,'UNUSED_PIN_CHANGED '+name)
    result,exit_state,scope=load(root/'result.json'),load(root/'worker_exit.json'),load(root/'scope.json')
    require(result['committed_steps']==result['coordinator_state_token']==0 and result['phase'] is None
        and result['automatic_retry'] is False,'UNUSED_PC_ACTIVITY')
    require(exit_state['run_id']==UNUSED_EXPIRED_RUN and exit_state['committed_steps']==0
        and exit_state['GPU_inflight_waited'] is True and exit_state['lease_closed'] is True
        and exit_state['cleanup_errors']==[],'UNUSED_PC_CLEANUP')
    require(not any((root/n).exists() for n in ('BOARD_READY.json','camera_capture.json','pc/evidence.fvej')),'UNUSED_PC_DEVICE_EVIDENCE_PRESENT')
    h=load(root/'hardware_handoff.json');body=verify_prepared_handoff(h,scope,bundle)
    prior=completed_capture('2884821c976c4fb6851d61e17cbc22c5')
    require(h['completed_parent']==prior,'UNUSED_COMPLETED_ANCESTOR')
    receipt=body['preparation_receipt']
    return dict({k:body['binding'][k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')},
        preparation_receipt_sha256=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest(),
        preparation_packet_sha256=UNUSED_BUNDLE_PINS['PREPARED_PACKET.json'],
        PC_cleanup_sha256=UNUSED_RUNTIME_PINS['worker_exit.json'],completed_parent=prior)


def preparation_parent():
    active=load(HERE/'runtime/joint_active.json')
    root=HERE/'runtime/joint'/active['session_id']
    if (root/'AUTO_ACCEPTANCE.json').exists():
        from joint_camera_audit import accepted_parent
        return accepted_parent(root)
    if active['run_id'] in ('1e1a77c8a6ba459cb3b79a9447cec3c8','ad5b4adac2b941f59b4a5271d1bde1fe'):
        return audited_compute_parent(active,root)
    if load(root/'scope.json').get('fresh_initialized_parent'):
        if load(root/'result.json').get('status')=='STOPPED_PENDING_PS_AUDIT':
            return dict(fresh=load(root/'scope.json')['fresh_initialized_parent'],completed_fresh=completed_parent())
        return fresh_unused_parent()
    return dict(unused=unused_parent(),completed=None) if active['run_id']==UNUSED_EXPIRED_RUN else dict(unused=None,completed=completed_parent())

def audited_compute_parent(active,root):
    """Explicit audited compute parents; no directory discovery or retry.

    Original failure stays intact. This admits only a NEW human preparation;
    the board independently checks clean finish, counters and same retained
    handles. It never resumes the failed scope or resends its last transaction.
    """
    from live_protocol import require,host_path
    run=active['run_id']
    live5=run=='ad5b4adac2b941f59b4a5271d1bde1fe'
    require(run in ('1e1a77c8a6ba459cb3b79a9447cec3c8','ad5b4adac2b941f59b4a5271d1bde1fe'),'AUDITED_COMPUTE_UNKNOWN_RUN')
    require(active['state']=='STOPPED' and active['run_id']==run
        and active['session_id']==('c59286b40c9c4c2e84a3e456a0856540' if live5 else '40feba4eb4ae49fca7d1df686cb62b0f')
        and host_path(active['root']).resolve()==root.resolve()
        and active['exit_codes']==dict(gui=0,joint_worker=0 if live5 else 1),'AUDITED_COMPUTE_PC_NOT_STOPPED')
    pins={'result.json':'577b3ad1687e5bed3baaf26c56d793e9629e7610b9ee7ecf494c695bcfc54137',
        'worker_exit.json':'f11488bfbbd143d05e00f4beccd65cd0f7ad066d9951ca9daaec23dc160254af',
        'PS_FINISH.json':'593b3a87a554aae58e127d0ea7893082ac50129020baba7874d026ed44a8ce05',
        'scope.json':'10eb820f58ddaf98065cc2f651c3d2e10e72f6828241c135f27bff4b57fae3ba'}
    if live5:
        pins={'result.json':'9d588ef2e4e90563fcea548bcb5294d30a7de323aadc11eb9d8ffdb7a35d0823',
            'worker_exit.json':'bc7c3bc2c8bb4d4f8728d2bed41e7b296ec2b29007e4e1ae713452b68d72125f',
            'PS_FINISH.json':'ce9a0029ca9e9e85b4ae3e16e1adf43009da79b696ec0adf328a453bfdcc0794',
            'scope.json':'f8a29f56bf4272ea019c9f660bddc096f0d231b7b2593e8b0f0881dcf8b88734'}
    for name,value in pins.items():require(sha(root/name)==value,'AUDITED_COMPUTE_SOURCE_CHANGED '+name)
    source=HERE/'evidence'/('camera_joint_live5_20261018' if live5 else 'camera_joint32_minimal_20261018')/'SAVED_DATA_AUDIT.json'
    require(sha(source)==('ffa1552a6fde479cfc5ed8abae8ed55e470b5065601d9b4735dc04ac7ece1442' if live5 else '14ae8ba896ed9cb0a1b5a9113ab26c2df22cf0bc9b21c404f4d344569312fa9c'),'AUDITED_COMPUTE_AUDIT_CHANGED')
    audit,finish,exited=load(source),load(root/'PS_FINISH.json'),load(root/'worker_exit.json')
    require(audit['status']=='PASS_SAVED_PC_NUMERICAL_CHAIN_AND_SIGNED_PS_FINISH'
        and audit['run_id']==finish['run_id']==exited['run_id']==run
        and audit['steps']==finish['completed_steps']==exited['committed_steps']==(100 if live5 else 32)
        and exited['GPU_inflight_waited'] and exited['lease_closed'] and not exited['cleanup_errors'],'AUDITED_COMPUTE_NOT_CLEAN')
    require(sha(root/'pc/evidence.fvej')==audit['PC_capture_sha256']
        and sha(root/'ps_retrieved_authorized/evidence.fvej')==audit['PS_capture_sha256']==finish['PS_capture_sha256'],
        'AUDITED_COMPUTE_CAPTURE_CHANGED')
    fields=('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id',
        'completed_steps','last_unified_commit_sha256','last_txn','PS_capture_sha256')
    return dict(fresh=load(root/'scope.json')['fresh_initialized_parent'],
        completed_fresh={k:finish[k] for k in fields})

def fresh_unused_parent():
    """Explicit stopped prestart failure, never a scan for the latest folder."""
    from live_protocol import require,host_path
    from joint_camera_preparation import verify_prepared_handoff
    import re
    active=load(HERE/'runtime/joint_active.json');run,session=active['run_id'],active['session_id']
    require(re.fullmatch('[a-f0-9]{32}',run) and re.fullmatch('[a-f0-9]{32}',session),'FRESH_UNUSED_PC_ID')
    root=HERE/'runtime/joint'/session
    require(active['state']=='STOPPED' and active['run_id']==run and active['session_id']==session
        and host_path(active['root']).resolve()==root.resolve() and active['exit_codes']==dict(gui=0,joint_worker=1),'FRESH_UNUSED_PC_NOT_STOPPED')
    result,exited=load(root/'result.json'),load(root/'worker_exit.json')
    clock_failure=result['error']=='AUDIT_REVOKED JOINT_PC_CLOCK_AUTHORITY_LOST'
    cancelled_before_start=(result['error']=='JOINT_CONVERTER_EXITED' and (root/'STOP_REQUEST.json').exists()
        and (root/'STOP_REQUEST.json').stat().st_mtime_ns<=(root/'result.json').stat().st_mtime_ns)
    require(result['committed_steps']==result['coordinator_state_token']==0 and result['phase'] is None and result['automatic_retry'] is False
        and (clock_failure or cancelled_before_start),'FRESH_UNUSED_PC_ACTIVITY')
    require(exited['run_id']==run and exited['committed_steps']==0 and exited['GPU_inflight_waited'] is True
        and exited['lease_closed'] is True and exited['cleanup_errors']==[],'FRESH_UNUSED_PC_CLEANUP')
    require(not any((root/n).exists() for n in ('BOARD_READY.json','CAMERA_START_REQUEST.json','camera_capture.json','pc/evidence.fvej')),'FRESH_UNUSED_PC_STARTED')
    if run=='b3ab3d3be1e24ee9b69cf676f3ec4326':
        bundle=HERE/'evidence/fresh_camera_start_20261017/actual_camera32/prepared_bundles'/run
    else:
        manual=load(HERE/'runtime/joint_manual_active.json');stage=host_path(manual['stage']).resolve()
        require(manual['status']=='STOPPED' and stage.parent==(HERE/'runtime/joint_manual').resolve(),'FRESH_UNUSED_MANUAL_NOT_STOPPED')
        bundle=stage/run
        if run=='2050d74ea5eb4948b37c9c687ac2733f':
            # This exact prestart attempt only renewed its PC time proof after
            # admission failed on 8771; the original board service stayed idle.
            bundle=host_path(load(HERE/'evidence/startup_wait_user_button_20261017/RECONNECT_READY.json')['attempt'])
    scope=load(root/'scope.json');handoff=load(root/'hardware_handoff.json')
    session_record=load(root/'session.json')
    require(scope['run_id']==run and scope['session_id']==session and session_record['scope_sha256']==sha(root/'scope.json')
        and session_record['hardware_handoff_sha256']==sha(root/'hardware_handoff.json'),'FRESH_UNUSED_SCOPE_CHANGED')
    body=verify_prepared_handoff(handoff,scope,bundle)
    initialized=load(HERE/'evidence/fresh_camera_start_20261017/actual_camera32/ACTUAL_INITIALIZATION_RECEIPT.json')
    require(initialized['initialization_capture_sha256']=='386aab9e73f6fcf749d2acdc4654e3725160a9c38f7925da7528d7fc1db052f8'
        and handoff['fresh_initialized_parent']==initialized,'FRESH_UNUSED_INITIALIZATION_CHANGED')
    receipt={k:v for k,v in body['preparation_receipt'].items() if k!='ps_durability'}
    prior=dict(body['binding'],preparation_receipt_sha256=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest())
    if cancelled_before_start:prior['allow_manual_prestart_cancel']=True
    return dict(fresh=handoff['fresh_initialized_parent'],unused_fresh=prior)

def build(parent,completed=None,unused=None,*,cpu_fixture=False,fresh=None,unused_fresh=None,completed_fresh=None,minimal_compute=False,live5=False,repeat_family=None):
    if live5 and not minimal_compute:raise ValueError('LIVE5_REQUIRES_MINIMAL_RUNTIME')
    package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
    template=package/'templates';metadata=load(HERE/'evidence/camera_joint_start_20261016/retained_metadata.json')
    scope=load(HERE/'evidence/camera_joint_service_review_20261016/scope_draft_r2.json')
    if sum(bool(p) for p in (completed,unused,fresh))>1:raise ValueError('AMBIGUOUS_PREPARATION_PARENT')
    if unused and unused!=unused_parent():raise ValueError('UNUSED_PARENT_CHANGED_BEFORE_BUILD')
    run=uuid.uuid4().hex;root=parent/run;root.mkdir(parents=True,exist_ok=False)
    window32=bool(completed or unused or fresh);count=100 if live5 else 32 if window32 else 3
    common=dict(run_id=run,server_session=uuid.uuid4().hex,boot_id=metadata['boot_id'],max_steps=count,
        new_loads=0,new_resets=0,new_allocations=0,kernel_file=metadata['kernel_file'],
        retained_src_address=metadata['src_address'],retained_dst_address=metadata['dst_address'],
        control_port=5790,neural_port=5768,pc_host='192.168.2.89',bind_host='192.168.2.99')
    if fresh:
        from joint_camera_fresh import MODE
        from live_protocol import require
        require(fresh['mode']==MODE and fresh['new_loads']==fresh['new_resets']==1 and fresh['new_allocations']==2
            and fresh['requests']==fresh['commits']==fresh['neural_listeners_started']==0,'FRESH_INIT_RECEIPT_REQUIRED')
        common.update(boot_id=fresh['boot_id'],kernel_file=fresh['kernel_file'],retained_src_address=fresh['src_address'],retained_dst_address=fresh['dst_address'])
        transfer_fields=dict(fresh_initialized_parent=fresh)
        if unused_fresh:transfer_fields['unused_fresh_parent']=unused_fresh
        if completed_fresh:transfer_fields['completed_fresh_parent']=completed_fresh
    elif unused_fresh:raise ValueError('UNUSED_FRESH_REQUIRES_INITIALIZATION_PARENT')
    elif unused:
        transfer_fields=dict(unused_parent=unused)
    elif completed:
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
        operation='FRESH_INITIALIZED_OWNER_READ20' if fresh else 'TRANSFER_UNUSED_CAMERA_OWNER_READ20' if unused else 'TRANSFER_COMPLETED_CAMERA_OWNER_READ20' if completed else 'TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20',original_source_run=plan['source_run'])
    if fresh:
        for key in ('source_run','source_capture_sha256','original_source_run'):plan.pop(key,None)
        plan.update(fresh_initialized_parent=fresh)
        if unused_fresh:plan['unused_fresh_parent']=unused_fresh
        if completed_fresh:plan['completed_fresh_parent']=completed_fresh
    elif unused:plan.update(unused_parent=unused)
    elif completed:plan.update(completed_parent=completed)
    else:plan.update(expired_run_id=NEXT_EXPIRED_RUN,prior_preparation_receipt_sha256=prior_receipt_sha)
    if cpu_fixture:plan.update(status='CPU_FIXTURE_ONLY',execution_authority='CPU_FIXTURE_ONLY')
    plan_sha=save(root/'PLAN.json',plan)
    declaration=load(template/'HARDWARE_HANDOFF_NOT_PREPARED.json')
    from joint_camera_clock_wait import PROFILE as WAIT_PROFILE,WAIT_S
    wait_fields=dict(clock_wait_profile=WAIT_PROFILE,clock_wait_s=WAIT_S,
        clock_wait_adapter_sha256=sha(HERE/'joint_camera_clock_wait.py')) if window32 else {}
    declaration.update(wait_fields)
    declaration.update(ps_durability_policy='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1',ps_evidence_adapter_sha256=sha(HERE/'ps_commit_evidence.py'))
    if minimal_compute:
        declaration.update(runtime_policy='MINIMAL_COMPUTE_ASYNC_V1',ps_durability_policy='ASYNC_AFTER_ACK_NO_CRASH_DURABILITY/v1',
            minimal_board_sha256=sha(HERE/'joint_minimal_board.py'),minimal_core_sha256=sha(HERE/'joint_minimal_core.py'))
    declaration.update({k:common[k] for k in ('run_id','server_session','boot_id')})
    declaration.update(status='DECLARED_NOT_PREPARED',execution_authority='APPROVED_BY_HUMAN',plan_sha256=plan_sha,
        listener_id=uuid.uuid4().hex,clock_policy='PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1',**transfer_fields,
        pc_authority_endpoint=dict(host='192.168.2.89',port=18791),
        endpoint=dict(host='192.168.2.99',port=5768),control_endpoint=dict(host='192.168.2.99',port=5790))
    if cpu_fixture:declaration['execution_authority']='CPU_FIXTURE_ONLY'
    declaration['capabilities']['max_steps']=count
    declaration['control_config']=dict(run_id=run,server_session=common['server_session'],plan_sha256=plan_sha,control_key=secrets.token_hex(32))
    for name,digest in declaration['software_sha256'].items():
        if sha(package/name)!=digest:raise ValueError('FROZEN_HARDWARE_HELPER_CHANGED '+name)
    declaration_sha=save(root/'HARDWARE_DECLARATION.json',declaration)
    now=datetime.now(timezone.utc)
    scope.update({k:common[k] for k in ('run_id','server_session','boot_id','max_steps')})
    scope.update(status='APPROVED_BY_HUMAN',execution_authority='APPROVED_BY_HUMAN',
        human_authorization_reference='CURRENT_CHAT_20261016_START_REAL_CAMERA_EXPERIMENT_32_STEP' if window32 else 'CURRENT_CHAT_USER_MANUAL_BOARD_LINE2_SOLE_OWNER_THREE_STEP',
        session_id=uuid.uuid4().hex,gpu_lease_id=uuid.uuid4().hex,comparison_id='CAMERA_'+run,
        capture_duration_s=30 if window32 else 10,max_worker_s=300 if window32 else 180,
        recording_required_before_camera=window32,
        validation_policy='SAME_OLD_CPU_POST_RUN',runtime_audit_policy='LOADED_STATIC_START_END_HASH/v1',
        neural_transport_policy='TCP_NODELAY_QUICKACK_WHEN_SUPPORTED/v1',journal_storage_policy='DIRECT_SESSION/v1',
        pc_commit_journal_policy='MERGED_INTENT_BEFORE_SEND/v1',
        ps_durability_policy=declaration['ps_durability_policy'],ps_evidence_adapter_sha256=declaration['ps_evidence_adapter_sha256'],
        start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=1798 if window32 else 298)).isoformat(),
        hardware_declaration_sha256=declaration_sha,source_sha256=source_pins())
    scope.update(wait_fields)
    if minimal_compute:
        scope.update(runtime_policy='MINIMAL_COMPUTE_ASYNC_V1',recording_required_before_camera=False,
            pc_commit_journal_policy='ASYNC_AFTER_ACK/v1',
            transport_probe_count=2,
            display_policy='POST_COMPUTE_LAST_REAL_STATE',recording_policy='ASYNC_BOUNDED_NONBLOCKING_DROP_ON_FULL',
            human_authorization_reference='CURRENT_CHAT_20261017_USER_REQUEST_MINIMAL_COMPUTE_32STEP_MANUAL_START',
            minimal_board_sha256=declaration['minimal_board_sha256'],minimal_core_sha256=declaration['minimal_core_sha256'])
    if live5:
        scope.update(live_response_hz=5,display_policy='LIVE_LATEST_COMMITTED_STATE_5HZ',
            human_authorization_reference='CURRENT_CHAT_20261018_USER_LIVE_PREVIEW_LATEST_INPUT_5HZ_REAL_GPU_FPGA')
    if fresh:scope['fresh_initialized_parent']=fresh
    if repeat_family:
        scope['repeat_family']=repeat_family
        scope['human_authorization_reference']='CURRENT_CHAT_20261018_USER_ONE_BOARD_PREP_REPEAT_START_STOP_WITH_AUTOMATIC_AUDIT'
    if unused_fresh:scope['unused_fresh_parent']=unused_fresh
    if completed_fresh:scope['completed_fresh_parent']=completed_fresh
    scope.pop('hardware_handoff_sha256',None)
    if cpu_fixture:
        scope.update(status='CPU_FIXTURE_ONLY',execution_authority='CPU_FIXTURE_ONLY',human_authorization_reference=None)
        validate_scope(dict(scope,status='APPROVED_BY_HUMAN',human_authorization_reference='CPU_FORMAT_CHECK_ONLY'))
    else:validate_scope(scope)
    scope_sha=save(root/'scope.json',scope)
    config=load(template/'PRIVATE_CONFIG_NOT_PREPARED.json');config.update(common)
    config.update(wait_fields)
    config.update(status='APPROVED_FOR_PREPARATION',prepared_status='PREPARED_FOR_THIS_CAMERA_RUN',
        execution_authority='APPROVED_BY_HUMAN',human_authorization_reference='EXACT_SCOPE_'+scope_sha,
        listener_id=declaration['listener_id'],scope_sha256=scope_sha,plan_sha256=plan_sha,
        **transfer_fields,
        control_key=declaration['control_config']['control_key'],
        pc_authority_endpoint=declaration['pc_authority_endpoint'])
    for key in ('max_worker_s','start_utc','end_utc'):config[key]=scope[key]
    for key in ('ps_durability_policy','ps_evidence_adapter_sha256'):config[key]=scope[key]
    if minimal_compute:
        for key in ('runtime_policy','minimal_board_sha256','minimal_core_sha256','transport_probe_count'):config[key]=scope[key]
    if live5:config['live_response_hz']=5
    if repeat_family:config['repeat_family']=repeat_family
    if cpu_fixture:config.update(status='CPU_FIXTURE_ONLY',execution_authority='CPU_FIXTURE_ONLY',human_authorization_reference=None,test_fixture=True)
    save(root/'PRIVATE_CONFIG.json',config)
    own={'prepare_camera.py':'joint_camera_board_entry.py','retained_transfer.py':'joint_camera_retained.py','ps_commit_evidence.py':'ps_commit_evidence.py'}
    if window32:own['clock_wait.py']='joint_camera_clock_wait.py'
    if fresh:own['fresh_camera.py']='joint_camera_fresh.py'
    if minimal_compute:
        own.update({'joint_minimal_board.py':'joint_minimal_board.py','joint_minimal_core.py':'joint_minimal_core.py'})
    if repeat_family:own['repeat_board.py']='joint_camera_repeat_board.py'
    runtime=dict(declaration['software_sha256']);runtime.update({dst:sha(HERE/src) for dst,src in own.items()})
    save(root/'RUNTIME_SHA256.json',runtime)
    archive=root/('CAMERA3_'+run+'.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in declaration['software_sha256']:z.writestr(name,(package/name).read_bytes())
        for dst,src in own.items():z.writestr(dst,(HERE/src).read_bytes())
        for name in ('PLAN.json','scope.json','PRIVATE_CONFIG.json','RUNTIME_SHA256.json'):z.write(root/name,name)
    save(root/'USER_AUTHORIZATION.json',dict(execution_authority='CPU_FIXTURE_ONLY' if cpu_fixture else 'APPROVED_BY_HUMAN',direct_user_messages=[] if cpu_fixture else ['7好了开始吧','老规矩要上版的东西我来弄',
        '都说你全权负责了你让7干嘛由你来告诉我我要启动什么','那就开始真实实验吧',
        '2026-10-16 再跑一轮32步短测；板端准备由用户手动，电脑侧由②负责；查清长停顿，对比前后，第一步前录像；原模型、精度和必要校验不变']+([
        '2026-10-17 直接改成最小计算路径；原模型和精度不变；检查、保存和显示移出计算主循环；记录异步且不能阻塞；保留已通过版本；用户准备板端并点启动测32步；分别报告GPU计算、纯传输、PL计算和总耗时'] if minimal_compute else []),scope_sha256=scope_sha,
        operator='CPU_FIXTURE_ONLY' if cpu_fixture else 'HUMAN_EXECUTES_BOARD_CELL',limits=dict(max_steps=count,capture_duration_s=scope['capture_duration_s'],max_worker_s=scope['max_worker_s'],
        new_loads=0,new_resets=0,new_allocations=0,automatic_retry=False)))
    save(root/'BUNDLE_PUBLIC.json',dict(root=str(root),archive=str(archive),archive_sha256=sha(archive),run_id=run,
        session_id=scope['session_id'],scope_sha256=scope_sha,end_utc=scope['end_utc'],max_steps=count))
    return root,archive
