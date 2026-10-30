"""One human-installed follower of the EXISTING prepared board owner.

No listener, overlay, allocator, reset, STEP or COMMIT implementation here.
Only a clean, closed run may transfer through the original prepare function.
Signed immutable preparation downloads can be polled while the PC is offline;
an attempted preparation or neural failure is never retried.
"""
import base64,hashlib,hmac,io,json,threading,time,urllib.request,uuid,zipfile
from pathlib import Path

def require(ok,message):
    if not ok:raise ValueError(message)

def mac(body,key):
    return hmac.new(bytes.fromhex(key),json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()

def verify_bundle(body,key,expected,family,runtime):
    require(set(body)=={'body','mac'} and hmac.compare_digest(mac(body['body'],key),body['mac']),'REPEAT_REPLY_AUTH')
    b=body['body']
    require(b['binding']==expected and b['family_id']==family['family_id'],'REPEAT_PARENT_BINDING')
    require(b['status'] in ('WAIT','PREPARE'),'REPEAT_STATUS')
    if b['status']=='WAIT':return None
    raw=base64.b64decode(b['archive_b64'],validate=True)
    require(len(raw)<=2000000 and hashlib.sha256(raw).hexdigest()==b['archive_sha256'],'REPEAT_ARCHIVE_SHA')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names=archive.namelist()
        require(len(names)==len(set(names)) and all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names),'REPEAT_ARCHIVE_PATH')
        require(sum(x.file_size for x in archive.infolist())<=4000000,'REPEAT_ARCHIVE_BOUND')
        new_runtime=json.loads(archive.read('RUNTIME_SHA256.json'))
        require(new_runtime==runtime,'REPEAT_RELEASE_CHANGED_REPREPARE_REQUIRED')
        for name,digest in runtime.items():
            require(hashlib.sha256(archive.read(name)).hexdigest()==digest,'REPEAT_SOFTWARE_SHA')
        config=json.loads(archive.read('PRIVATE_CONFIG.json'));scope=json.loads(archive.read('scope.json'))
        duration=family.get('run_duration_s')
        require((duration is None or (type(duration) is int and 1<=duration<=60))
            and config.get('run_duration_s')==scope.get('run_duration_s')==duration,'REPEAT_DURATION_BOUND')
        require(config['repeat_family']==scope['repeat_family']==family and scope['max_steps']<=(12000 if duration else 100)
            and config['boot_id']==expected['boot_id'] and config['new_loads']==config['new_resets']==config['new_allocations']==0,
            'REPEAT_SCOPE_OR_BOARD_OPERATIONS')
        require(config['completed_fresh_parent']['run_id']==expected['run_id']
            and config['completed_fresh_parent']['scope_sha256']==expected['scope_sha256'],'REPEAT_COMPLETED_PARENT')
        require(hashlib.sha256(archive.read('scope.json')).hexdigest()==config['scope_sha256'],'REPEAT_SCOPE_SHA')
        name='CAMERA3_'+config['run_id']
        require(b['root_name']==name and uuid.UUID(hex=config['run_id']).hex==config['run_id'],'REPEAT_NEW_RUN')
    return raw,name

def install(root,namespace,prepare):
    prior=namespace.get('camera_repeat_handle')
    if prior is not None and prior.get('stopped'):
        del namespace['camera_repeat_handle']
    require('camera_repeat_handle' not in namespace,'REPEAT_FOLLOWER_ALREADY_INSTALLED')
    root=Path(root);config=json.loads((root/'PRIVATE_CONFIG.json').read_text())
    family=config['repeat_family'];runtime=json.loads((root/'RUNTIME_SHA256.json').read_text())
    deadline=family_deadline(family,namespace['camera3_service_instance'])
    owner=namespace['line2_fresh_initialized'];state=dict(error=None,prepared_runs=1,stopped=False,stop_requested=threading.Event())
    def follow():
        try:
            while not state['stop_requested'].is_set() and time.monotonic()<deadline and state['prepared_runs']<family['max_runs']:
                service=namespace['camera3_service_instance'];bundle=namespace['camera3_bundle']
                with service.lock:
                    require(service.error is None and not service.driver.poisoned,'REPEAT_PREVIOUS_FAILED_OR_UNKNOWN')
                    finished=service.state=='FINISHED_PENDING_AUDIT'
                if not finished:time.sleep(.2);continue
                require(service.driver.pending is None and service.driver.requests==service.driver.commits>0
                    and not service.inflight and service.neural_exited.is_set(),'REPEAT_PENDING_OR_UNCLOSED')
                prior={k:service.config[k] for k in ('run_id','scope_sha256','boot_id')}
                request=dict(family_id=family['family_id'],binding=prior,nonce=uuid.uuid4().hex)
                packet=dict(body=request,mac=mac(request,service.config['control_key']))
                req=urllib.request.Request('http://192.168.2.89:18790/repeat-next',data=json.dumps(packet).encode(),headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req,timeout=5) as reply:response=json.loads(reply.read(3000001))
                except OSError:
                    # Read-only preparation polling only. Never re-enter a
                    # partially attempted prepare or retry any neural frame.
                    time.sleep(1);continue
                payload=verify_bundle(response,service.config['control_key'],prior,family,runtime)
                if state['stop_requested'].is_set():break
                if payload is None:time.sleep(.5);continue
                raw,name=payload;target=root.parent/name
                require(not target.exists(),'REPEAT_SCOPE_ALREADY_CONSUMED')
                target.mkdir()
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:archive.extractall(target)
                new_bundle,new_service=prepare(target,owner,service,bundle)
                namespace['camera3_bundle'],namespace['camera3_service_instance']=new_bundle,new_service
                state['prepared_runs']+=1
        except BaseException as error:
            state['error']=str(error)
            (root/'REPEAT_FAILURE.json').write_text(json.dumps(dict(family_id=family['family_id'],error=str(error),automatic_retry=False)))
            print('CAMERA_REPEAT_FAILED '+str(error),flush=True)
        finally:state['stopped']=True
    service=namespace['camera3_service_instance']
    notice=dict(family_id=family['family_id'],binding={k:service.config[k] for k in ('run_id','scope_sha256','boot_id')},
        repeat_board_sha256=runtime['repeat_board.py'])
    packet=dict(body=notice,mac=mac(notice,service.config['control_key']))
    req=urllib.request.Request('http://192.168.2.89:18790/repeat-ready',data=json.dumps(packet).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=5) as reply:
        response=json.loads(reply.read(65537))
    require(hmac.compare_digest(mac(response['body'],service.config['control_key']),response['mac'])
        and response['body']==dict(notice,ok=True),'REPEAT_INSTALL_ACK')
    thread=threading.Thread(target=follow,name='line2-existing-owner-preparation',daemon=True)
    state['thread']=thread;thread.start()
    print('CAMERA_REPEAT_READY '+json.dumps(dict(family_id=family['family_id'],max_runs=family['max_runs'],new_loads=0,new_resets=0,new_allocations=0)),flush=True)
    return state

def family_deadline(family,service):
    # The board's calendar may be years away from Windows. The existing
    # signed PC proof supplies UTC; only PS monotonic advances this deadline.
    # The PC endpoint separately checks family expiry for every new package.
    stamp=service.driver.clock_guard.check(service.config)
    duration=family['expires_unix']-family['created_unix']
    remaining=family['expires_unix']-stamp['utc_upper_ns']/1e9
    require(family['max_runs']==100 and 0<duration<=28800 and 0<remaining<=duration,'REPEAT_HUMAN_SCOPE')
    return time.monotonic()+remaining/(1+stamp['rate_error_bound_ppm']/1e6)
