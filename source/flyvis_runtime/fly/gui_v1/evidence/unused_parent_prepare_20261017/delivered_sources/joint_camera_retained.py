"""Manual-only transfer from the exact expired, NEVER STARTED camera owner.

Old poison/claim/evidence remain immutable. A fresh driver owns the same buffers
only after the prior HTTP/expiry threads close, with a durable transfer record.
No overlay constructor, register write, DMA, allocation or reset is used here.
"""
import hashlib, inspect, json, os, time
from pathlib import Path

EXPIRED_RUN='e13f6d0e6bc04fcaa4e5051cb0b37391'
NEXT_EXPIRED_RUN='393ffe7d6860457ebf9ad4b11fbec943'
ORIGINAL_RUN='c708f1c9bac14c07ac8f56d59678b95a'
UNUSED_EXPIRED_RUN='815a7069e02e42fb8dc0cf9477e97926'
UNUSED_SESSION='34e96b4d227f488bb3214190089569d1'

def require(value,message):
    if not value:raise ValueError(message)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inspect_completed(service,original,package,expected,*,cpu=False,successor=None):
    """Accept only the exact completed, independently audited parent capture."""
    from importlib import import_module
    d=service.driver;n=expected['completed_steps']
    require(type(n) is int and n>0,'COMPLETED_COUNT')
    require(service.state=='FINISHED_PENDING_AUDIT' and service.error is None,'COMPLETED_NOT_NORMAL')
    require(d.requests==d.commits==n and d.pending is None and not d.poisoned and not service.inflight,'COMPLETED_PENDING_OR_COUNTS')
    require(service.connections==1 and service.listener is None and service.connection is None
        and service.neural_thread is not None and not service.neural_thread.is_alive(),'COMPLETED_NEURAL_ACTIVE')
    used=getattr(d,'_line2_successor_claim',None)
    if successor is None:require(not used,'COMPLETED_ALREADY_TRANSFERRED')
    else:require(used and all(used[k]==successor[k] for k in ('run_id','server_session','scope_sha256','plan_sha256')),'COMPLETED_SUCCESSOR_CLAIM')
    require(all(service.config[k]==expected[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')),'COMPLETED_PARENT_IDENTITY')
    require(service.identity is not None and all(service.identity[k]==service.config[k]
        for k in ('run_id','server_session','boot_id','scope_sha256','listener_id')),'COMPLETED_START_IDENTITY')
    prior=d.committed.get(bytes.fromhex(d.bound_asid)) if d.bound_asid else None
    require(len(d.committed)==1 and prior is not None and prior[0]==n-1 and prior[2].hex()==expected['last_unified_commit_sha256']
        and prior[3].hex()==expected['last_txn'] and prior[4]==0,'COMPLETED_CANONICAL_COMMIT')
    receipt=service.finish_receipt
    require(all(receipt[k]==expected[k] for k in ('completed_steps','PS_capture_sha256','last_unified_commit_sha256','last_txn'))
        and receipt['capture_closed'] and receipt['requests']==receipt['commits']==n,'COMPLETED_FINISH_RECEIPT')
    require(d.evidence.journal.closed and sha(d.evidence.journal.path)==expected['PS_capture_sha256'],'COMPLETED_CAPTURE_CHANGED')
    reader=import_module(package.__name__+'.evidence_journal').JournalReader(d.evidence.journal.path)
    require(reader.terminal['status']=='CAPTURE_COMPLETE_NOT_HARDWARE_ADMISSION'
        and reader.terminal['requests']==reader.terminal['acks']==reader.terminal['completed_steps']==n
        and reader.terminal['source_closed'],'COMPLETED_CAPTURE_TERMINAL')
    events=[json.loads(row) for row in reader.read('events.jsonl').splitlines()]
    require(events[-1]['event']=='FINISH_WINDOW_ACCEPTED'
        and all(sum(e['event']==name for e in events)==n for name in ('DMA_LAUNCH_RETURNED','CANDIDATE_READY','RELEASE_CONFIRMED','ACK_SENT')),'COMPLETED_BOARD_EVENTS')
    last=[e for e in events if e['event']=='RELEASE_CONFIRMED'][-1]
    require(last['step']==n-1 and last['txn']==expected['last_txn'] and last['commit_sha']==expected['last_unified_commit_sha256']
        and last['state']==last['error']==0,'COMPLETED_FINAL_RELEASE')
    require(original.config['run_id']==ORIGINAL_RUN and original.state=='BOARD_COMPLETE'
        and original.driver.requests==original.driver.commits==485 and original.driver.pending is None and not original.driver.poisoned,'COMPLETED_ORIGINAL_OWNER')
    require(all(getattr(d,k) is getattr(original.driver,k) for k in ('overlay','src','dst','reg','dma','np')),'COMPLETED_SHARED_HANDLES')
    require(original.listener is None and original.connection is None and not original.neural_thread.is_alive(),'COMPLETED_ORIGINAL_ACTIVE')
    if not cpu:
        p=import_module(package.__name__+'.prepare')
        require(sha(inspect.getfile(type(d)))==sha(Path(package.__file__).parent/'driver.py')
            and sha(inspect.getfile(type(original.driver)))==p.SOURCE_DRIVER_SHA
            and sha(original.driver.evidence.journal.path)==p.SOURCE_CAPTURE_SHA,'COMPLETED_ORIGINAL_SOURCE')
    return dict(parent_run_id=expected['run_id'],parent_server_session=expected['server_session'],
        parent_capture_sha256=expected['PS_capture_sha256'],completed_steps=n,last_txn=expected['last_txn'],
        last_unified_commit_sha256=expected['last_unified_commit_sha256'],parent_capture_closed=True,
        original_claim_preserved=True,parent_state_preserved=True)

def close_completed_control(service):
    require(service.state=='FINISHED_PENDING_AUDIT' and service.thread.is_alive(),'COMPLETED_CLOSE_PHASE')
    service.http.shutdown();service.http.server_close();service.thread.join(2)
    if getattr(service,'expiry_thread',None):service.expiry_thread.join(2)
    require(not service.thread.is_alive() and not service.expiry_thread.is_alive(),'COMPLETED_CLOSE_UNCONFIRMED')

def inspect_expired(service,original,package,*,cpu=False,expected_run=EXPIRED_RUN,ancestor=None,receipt_sha=None,successor=None):
    d=service.driver
    require(expected_run in (EXPIRED_RUN,NEXT_EXPIRED_RUN) and service.config['run_id']==expected_run,'TRANSFER_WRONG_EXPIRED_RUN')
    require(service.state=='FAILED_OR_UNKNOWN' and service.error=='MANUAL_PREPARATION_EXPIRED','TRANSFER_NOT_UNUSED_EXPIRY')
    require(d.requests==d.commits==0 and d.pending is None and d.poisoned is True,'TRANSFER_COUNTS_OR_PENDING')
    require(service.identity is None and service.connections==0 and not service.inflight,'TRANSFER_START_OR_CONNECTION_OCCURRED')
    require(service.listener is None and service.connection is None and service.neural_thread is None,'TRANSFER_NEURAL_ACTIVITY')
    require(d.bound_asid is None and not d.committed and d.compute_deadline is None,'TRANSFER_DRIVER_ACTIVITY')
    require(d.evidence.journal.closed,'TRANSFER_EVIDENCE_NOT_CLOSED')
    used=getattr(d,'_line2_successor_claim',None)
    if successor is None:require(not used,'TRANSFER_EVIDENCE_OR_CONSUMED')
    else:require(used and all(used[k]==successor[k] for k in ('run_id','server_session','scope_sha256','plan_sha256')),'TRANSFER_ANCESTOR_SUCCESSOR_CLAIM')
    require(original.config['run_id']==ORIGINAL_RUN and original.state=='BOARD_COMPLETE','TRANSFER_ORIGINAL_OWNER')
    prior=original.driver
    require(prior.requests==prior.commits==485 and prior.pending is None and not prior.poisoned,'TRANSFER_ORIGINAL_CHANGED')
    claim=getattr(prior,'_camera_ready_claim',None)
    if expected_run==EXPIRED_RUN:
        require(claim and all(claim[k]==service.config[k] for k in ('run_id','server_session','scope_sha256','plan_sha256')),'TRANSFER_PARENT_CLAIM')
    else:
        require(ancestor is not None,'TRANSFER_ANCESTOR_REQUIRED')
        parent=inspect_expired(ancestor,original,package,cpu=cpu,successor=service.config)
        require(not ancestor.thread.is_alive() and not ancestor.expiry_thread.is_alive(),'TRANSFER_ANCESTOR_THREAD_ACTIVE')
    require(all(getattr(d,k) is getattr(prior,k) for k in ('overlay','src','dst','reg','dma','np')),'TRANSFER_SHARED_HANDLES_CHANGED')
    require(original.listener is None and original.connection is None and not original.neural_thread.is_alive(),'TRANSFER_ORIGINAL_ACTIVE')
    if not cpu:
        require(type(d).__name__=='Full485Driver' and sha(inspect.getfile(type(d)))==sha(Path(package.__file__).parent/'driver.py'),'TRANSFER_DRIVER_SOURCE')
        from importlib import import_module
        expected=import_module(package.__name__+'.prepare')
        require(type(prior).__module__=='a3latency485.driver' and sha(inspect.getfile(type(prior)))==expected.SOURCE_DRIVER_SHA
            and sha(prior.evidence.journal.path)==expected.SOURCE_CAPTURE_SHA,'TRANSFER_ORIGINAL_SOURCE_CHANGED')
    from importlib import import_module
    reader=import_module(package.__name__+'.evidence_journal').JournalReader(d.evidence.journal.path)
    require(reader.terminal['status']=='FAILED_OR_INCOMPLETE' and reader.terminal['requests']==reader.terminal['acks']==0,'TRANSFER_CAPTURE_NOT_ZERO')
    events=[json.loads(row) for row in reader.read('events.jsonl').splitlines()]
    require(events and events[-1]['event']=='FAIL_STOP' and events[-1]['error']=='MANUAL_PREPARATION_EXPIRED','TRANSFER_CAPTURE_NOT_EXPIRY')
    require(not any(name.startswith('wire_') for name in reader.files),'TRANSFER_WIRE_EXISTS')
    forbidden=('START_ARMED','NEURAL_CONNECTED','REQUEST_ACCEPTED','COMPUTE_WINDOW_STARTED','DMA_LAUNCH_RETURNED','CANDIDATE_READY','RELEASE_CONFIRMED','ACK_SENT')
    require(not any(row['event'] in forbidden or row['event'].startswith('WIRE_') for row in events),'TRANSFER_CAPTURE_ACTIVITY')
    if expected_run==NEXT_EXPIRED_RUN:
        raw=reader.read('PREPARATION_RECEIPT.json')
        require(receipt_sha and hashlib.sha256(raw).hexdigest()==receipt_sha,'TRANSFER_PRIOR_RECEIPT_IDENTITY')
        previous=json.loads(raw)
        require(all(previous[k]==service.config[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256')),'TRANSFER_PRIOR_RECEIPT_BINDING')
        require(previous['zero_step_transfer']['expired_capture_sha256']==parent['expired_capture_sha256'],'TRANSFER_ANCESTOR_CAPTURE_CHAIN')
    result=dict(expired_run_id=expected_run,expired_server_session=service.config['server_session'],
        expired_scope_sha256=service.config['scope_sha256'],expired_capture_sha256=sha(reader.path),
        requests=0,commits=0,neural_connections=0,start_received=False,old_poison_preserved=True,
        original_claim_preserved=True,source_capture_closed=True)
    if expected_run==NEXT_EXPIRED_RUN:result.update(ancestor_run_id=EXPIRED_RUN,prior_preparation_receipt_sha256=receipt_sha)
    return result

def close_expired_control(service):
    # stop() has already closed the failed journal and kept buffers pinned.
    # HTTP shutdown is software only; never call a hardware/DMA cleanup method.
    require(service.state=='FAILED_OR_UNKNOWN' and service.identity is None,'TRANSFER_CLOSE_PHASE')
    require(service.thread is not None and service.thread.is_alive(),'TRANSFER_CONTROL_NOT_RUNNING')
    service.http.shutdown();service.http.server_close();service.thread.join(2)
    if getattr(service,'expiry_thread',None):service.expiry_thread.join(2)
    require(not service.thread.is_alive() and not service.expiry_thread.is_alive(),'TRANSFER_CONTROL_STOP_UNCONFIRMED')


def inspect_unused_parent(service,original,package,expected,parent_service,*,cpu=False):
    """Only the registered never-STARTED 815 expiry, with its audited ancestor."""
    from importlib import import_module
    d=service.driver
    require(expected['run_id']==UNUSED_EXPIRED_RUN and service.config['run_id']==UNUSED_EXPIRED_RUN,'UNUSED_PARENT_RUN')
    require(all(service.config[k]==expected[k] for k in ('server_session','boot_id','scope_sha256','plan_sha256','listener_id')),'UNUSED_PARENT_IDENTITY')
    require(service.state=='FAILED_OR_UNKNOWN' and service.error=='MANUAL_PREPARATION_EXPIRED','UNUSED_PARENT_NOT_EXPIRY')
    require(d.requests==d.commits==0 and d.pending is None and d.poisoned is True,'UNUSED_PARENT_COUNTS_OR_PENDING')
    require(service.identity is None and service.connections==0 and not service.inflight
        and service.listener is None and service.connection is None and service.neural_thread is None,'UNUSED_PARENT_STARTED_OR_CONNECTED')
    require(d.bound_asid is None and not d.committed and d.compute_deadline is None,'UNUSED_PARENT_DRIVER_ACTIVITY')
    require(not getattr(d,'_line2_successor_claim',None) and d.evidence.journal.closed,'UNUSED_PARENT_CONSUMED_OR_OPEN')
    prior=expected['completed_parent']
    require(prior['run_id']=='2884821c976c4fb6851d61e17cbc22c5' and prior['completed_steps']==32
        and service.config.get('completed_parent')==prior and parent_service is not None,'UNUSED_PARENT_ANCESTOR')
    inspect_completed(parent_service,original,package,prior,cpu=cpu,successor=service.config)
    require(not parent_service.thread.is_alive() and not parent_service.expiry_thread.is_alive(),'UNUSED_ANCESTOR_CONTROL_ACTIVE')
    require(all(getattr(d,k) is getattr(parent_service.driver,k) for k in ('overlay','src','dst','reg','dma','np')),'UNUSED_PARENT_SHARED_HANDLES')
    if not cpu:require(sha(inspect.getfile(type(d)))==sha(Path(package.__file__).parent/'driver.py'),'UNUSED_PARENT_DRIVER_SOURCE')
    reader=import_module(package.__name__+'.evidence_journal').JournalReader(d.evidence.journal.path)
    require(reader.terminal['status']=='FAILED_OR_INCOMPLETE' and reader.terminal['requests']==reader.terminal['acks']==0,'UNUSED_PARENT_CAPTURE_COUNTS')
    events=[json.loads(x) for x in reader.read('events.jsonl').splitlines()]
    forbidden=('START_ARMED','NEURAL_CONNECTED','REQUEST_ACCEPTED','COMPUTE_WINDOW_STARTED','DMA_LAUNCH_RETURNED','CANDIDATE_READY','RELEASE_CONFIRMED','ACK_SENT')
    require(events and events[-1]['event']=='FAIL_STOP' and events[-1]['error']=='MANUAL_PREPARATION_EXPIRED'
        and not any(e['event'] in forbidden or e['event'].startswith('WIRE_') for e in events)
        and not any(n.startswith('wire_') for n in reader.files),'UNUSED_PARENT_CAPTURE_ACTIVITY')
    raw=reader.read('PREPARATION_RECEIPT.json');receipt=json.loads(raw)
    require(hashlib.sha256(raw).hexdigest()==expected['preparation_receipt_sha256']
        and all(receipt[k]==service.config[k] for k in ('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id')),'UNUSED_PARENT_RECEIPT')
    require(receipt['completed_transfer']['parent_run_id']==prior['run_id']
        and receipt['completed_transfer']['parent_capture_sha256']==prior['PS_capture_sha256']
        and receipt['completed_transfer']['old_control_thread_stopped'] is True,'UNUSED_PARENT_RECEIPT_ANCESTOR')
    return dict(unused_run_id=expected['run_id'],unused_server_session=expected['server_session'],
        unused_scope_sha256=expected['scope_sha256'],unused_capture_sha256=sha(reader.path),
        preparation_receipt_sha256=expected['preparation_receipt_sha256'],
        completed_parent_run_id=prior['run_id'],completed_parent_capture_sha256=prior['PS_capture_sha256'],
        requests=0,commits=0,neural_connections=0,start_received=False,old_poison_preserved=True,
        original_claim_preserved=True,source_capture_closed=True)

def prepare(root,service,original,config,scope_bytes,plan_bytes,clock,package,*,cpu=False,ancestor=None):
    from importlib import import_module
    helper=lambda name:import_module(package.__name__+'.'+name)
    p=helper('prepare');binding=helper('binding')
    binding.validate_scope_binding(config,scope_bytes,cpu_fixture=cpu,clock=clock)
    require(hashlib.sha256(plan_bytes).hexdigest()==config['plan_sha256'],'TRANSFER_PLAN_SHA')
    plan=json.loads(plan_bytes)
    completed=config.get('completed_parent');unused=config.get('unused_parent')
    require(not (completed and unused),'TRANSFER_AMBIGUOUS_PARENT')
    expected_run=config.get('transfer_from_expired_run',EXPIRED_RUN)
    if unused:
        require(plan['operation']=='TRANSFER_UNUSED_CAMERA_OWNER_READ20' and plan['unused_parent']==unused
            and plan['original_source_run']==ORIGINAL_RUN,'UNUSED_PLAN_OPERATION')
        inspect_source=lambda:inspect_unused_parent(service,original,package,unused,ancestor,cpu=cpu)
    elif completed:
        require(plan['operation']=='TRANSFER_COMPLETED_CAMERA_OWNER_READ20' and plan['completed_parent']==completed
            and plan['original_source_run']==ORIGINAL_RUN,'COMPLETED_PLAN_OPERATION')
        inspect_source=lambda:inspect_completed(service,original,package,completed,cpu=cpu)
    else:
        require(plan['operation']=='TRANSFER_ZERO_STEP_EXPIRED_OWNER_READ20' and plan['expired_run_id']==expected_run
            and plan['original_source_run']==ORIGINAL_RUN,'TRANSFER_PLAN_OPERATION')
        inspect_source=lambda:inspect_expired(service,original,package,cpu=cpu,expected_run=expected_run,ancestor=ancestor,receipt_sha=config.get('prior_preparation_receipt_sha256'))
    if not (completed or unused) and expected_run==NEXT_EXPIRED_RUN:
        require(plan['prior_preparation_receipt_sha256']==config['prior_preparation_receipt_sha256'],'TRANSFER_PRIOR_RECEIPT_PLAN')
    keys=('run_id','server_session','boot_id','max_steps','new_loads','new_resets','new_allocations',
          'kernel_file','retained_src_address','retained_dst_address','control_port','neural_port','pc_host','bind_host')
    require(all(plan[k]==config[k] for k in keys),'TRANSFER_PLAN_BINDING')
    require(plan['read_set']==[dict(bank=b,offset=o) for b,o in p.READS],'TRANSFER_READ_SET')
    require(cpu==bool(config.get('test_fixture')),'TRANSFER_MODE')
    if not cpu:require(p.boot_id()==config['boot_id'] and p.current_kernel()==config['kernel_file'],'TRANSFER_BOOT_KERNEL')
    require(service.driver.boot_id==original.driver.boot_id==config['boot_id'],'TRANSFER_BOOT_CHANGED')
    old=service.driver
    require(int(old.src.device_address)==config['retained_src_address'] and int(old.dst.device_address)==config['retained_dst_address']
        and old.src.nbytes==69216 and old.dst.nbytes==23072,'TRANSFER_BUFFER_IDENTITY')
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    with p.LOCK,service.lock:
        transfer=inspect_source()
        clock.check(config)
        # Forbid a later /start through the OLD control channel before joining it.
        require(service.state==('FINISHED_PENDING_AUDIT' if completed else 'FAILED_OR_UNKNOWN'),'TRANSFER_STATE_CHANGED')
    (close_completed_control if completed else close_expired_control)(service)
    with p.LOCK,service.lock:
        require(inspect_source()==transfer,'TRANSFER_SOURCE_CHANGED_WHILE_CLOSING')
        if not cpu:
            require(old.overlay.is_loaded() and sha(old.overlay.bitfile_name)==config['bit_sha256']
                and sha(Path(old.overlay.bitfile_name).with_suffix('.hwh'))==config['hwh_sha256'],'TRANSFER_IMAGE_CHANGED')
        require(old.src.device_address%64==old.dst.device_address%64==0,'TRANSFER_ALIGNMENT')
        require(old.src.device_address+old.src.nbytes<=old.dst.device_address or old.dst.device_address+old.dst.nbytes<=old.src.device_address,'TRANSFER_BUFFER_OVERLAP')
        claim=dict(run_id=config['run_id'],server_session=config['server_session'],scope_sha256=config['scope_sha256'],plan_sha256=config['plan_sha256'])
        with (root/('UNUSED_TRANSFER_CLAIM.json' if unused else 'COMPLETED_TRANSFER_CLAIM.json' if completed else 'ZERO_STEP_TRANSFER_CLAIM.json')).open('x',encoding='utf-8') as f:
            json.dump(dict(claim=claim,parent=transfer),f);f.flush();os.fsync(f.fileno())
        old._line2_successor_claim=dict(claim) # Consumed even if any later read fails.
        evidence=helper('light_evidence').Evidence(root/'ps',config)
        d=helper('driver').Full485Driver.__new__(helper('driver').Full485Driver)
        for key in ('overlay','src','dst','reg','dma','np','boot_id'):setattr(d,key,getattr(old,key))
        d.evidence=evidence;d.plan=config;d.clock_guard=clock;d.server_session=config['server_session'];d.last_registers={}
        d.requests=d.commits=0;d.pending=None;d.committed={};d.poisoned=False;d.bound_asid=None;d.compute_deadline=None
        d.session_deadline=time.monotonic()+clock.remaining_s(config)
        p.PINNED.extend((service,original,d,evidence))
        try:
            evidence.event('UNUSED_CAMERA_OWNER_TRANSFERRED' if unused else 'COMPLETED_CAMERA_OWNER_TRANSFERRED' if completed else 'ZERO_STEP_EXPIRED_OWNER_TRANSFERRED',**claim,**transfer)
            if unused:
                prior_raw=old.evidence.journal.path.read_bytes()
                require(hashlib.sha256(prior_raw).hexdigest()==transfer['unused_capture_sha256'],'UNUSED_CAPTURE_CHANGED_BEFORE_COPY')
                evidence.journal.add('PARENT_UNUSED_CAPTURE.fvej',prior_raw)
            rows=[]
            for bank,offset in p.READS:
                clock.check(config)
                if not cpu:require(p.boot_id()==config['boot_id'],'TRANSFER_BOOT_DURING_READ')
                rows.append(dict(bank=bank,offset=offset,value=d._read(bank,offset)))
            receipt={k:config[k] for k in ('run_id','server_session','boot_id','plan_sha256','scope_sha256','listener_id','bit_sha256','hwh_sha256','initial_full_sha256','initial_H_sha256','mapping_sha256')}
            receipt.update(requests=0,commits=0,pending=False,poisoned=False,old_receiver_stopped=True,new_loads=0,new_resets=0,new_allocations=0,
                kernel_id=config['kernel_file'],src_bytes=d.src.nbytes,dst_bytes=d.dst.nbytes,src_address=int(d.src.device_address),dst_address=int(d.dst.device_address),reads=rows,
                **{('unused_parent_transfer' if unused else 'completed_transfer' if completed else 'zero_step_transfer'):dict(transfer,old_control_thread_stopped=True)})
            binding.validate_readonly_receipt(config,receipt);clock.check(config)
            evidence.journal.add('CLOCK_PROOF.json',json.dumps(clock.receipt(config),sort_keys=True).encode())
            evidence.journal.add('PREPARATION_RECEIPT.json',json.dumps(receipt,sort_keys=True).encode());evidence.journal.checkpoint('ZERO_STEP_TRANSFER_READ20')
            return p.PreparedRetained(d,evidence,config,scope_bytes,clock,receipt,service)
        except BaseException:
            d.poisoned=True
            try:evidence.close()
            except BaseException:evidence.journal.abandon()
            raise
