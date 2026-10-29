"""Explicit three-step live entry. Default/preflight is read-only; never retries."""
import argparse,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from live_protocol import HERE,Registry,canonical,host_path,load,require,sha,utc,write
from live_worker import import_file
from hybrid_v2 import V2Contract
from hybrid_joint import connect_live,validate_short_scope
from hybrid_joint_evidence import board_acceptance
from realtime_timing import Timings

SOURCE_NAMES=['hybrid_joint_run.py','hybrid_joint.py','hybrid_joint_evidence.py','hybrid_a3.py',
              'hybrid_gpu.py','hybrid_v2.py','hybrid_joint_registry.json','board_actual_registry.json']
REFERENCE=HERE/'runtime/hybrid_software_checks/ca3f3c24c04d4c5d9c0dde9d36c8a511'
REFERENCE_MANIFEST_SHA='22f4e7e67583b84ae179fe912efd885b0c6b9b0b30078bf15537355ff157d163'

def source_pins():return {name:sha(HERE/name) for name in SOURCE_NAMES}

class SavedReference:
    """Independent accepted software result; used for checks, never as output."""
    def init__(self):
        require(sha(REFERENCE/'manifest.json')==REFERENCE_MANIFEST_SHA,'REFERENCE_MANIFEST_CHANGED')
        manifest=load(REFERENCE/'manifest.json')
        for name,digest in manifest['files'].items():require(sha(REFERENCE/name)==digest,'REFERENCE_FILE_CHANGED '+name)
        self.candidates=[]
        for k in range(200,203):
            with np.load(REFERENCE/f'candidates_{k}.npz',allow_pickle=False) as z:self.candidates.append({key:z[key].copy() for key in z.files})
        self.states=np.load(REFERENCE/'software_mixed_states.npy',allow_pickle=False)
        self.flows=np.load(REFERENCE/'official_flow.npy',allow_pickle=False)
    def check(self,old,output,k):
        ref=self.candidates[k-200]
        require(np.array_equal(old,ref['old_full']),'REFERENCE_REQUIRES_EXACT_SAME_OLD_STATE')
        require(np.array_equal(output['r_ids'],ref['r_ids']) and np.array_equal(output['x_full'],ref['x_full']),'REFERENCE_INPUT_ORDER')
        errors={name:float(np.max(np.abs(output[name]-ref[name]))) for name in ('new_R','chemical_H')}
        for name in errors:require(np.allclose(output[name],ref[name],atol=1e-5,rtol=1e-5),'CURRENT_GPU_REFERENCE_MISMATCH '+name)
        return {'status':'PASS_SAME_OLD_GPU_REFERENCE','max_abs':errors,'atol':1e-5,'rtol':1e-5,
                'reference_run':REFERENCE.name,'reference_manifest_sha256':REFERENCE_MANIFEST_SHA}

def preflight():
    c=V2Contract();reg=Registry();ref=SavedReference();a,words,_=c.initial()
    np.testing.assert_array_equal(a,ref.candidates[0]['old_full'])
    hmod=import_file('h_step',c.paths['h_step'])
    return dict(status='PASS_READ_ONLY_JOINT_PREFLIGHT',steps=[200,201,202],input=reg.binding('ON60'),
        initial_full_digest=hmod.array_hash(a),initial_H_sha256=c.wire.digest(words).hex(),mapping_sha256=c.mapping_sha,
        board_acceptance=board_acceptance(c),source_sha256=source_pins(),GPU_operations=0,board_operations=0)

def checked_scope(path):
    scope=load(host_path(path));c=V2Contract();acceptance=board_acceptance(c)
    validate_short_scope(scope,c,acceptance)
    require(scope.get('source_sha256')==source_pins(),'EXECUTABLE_SOURCE_CHANGED')
    require(scope.get('reference_manifest_sha256')==REFERENCE_MANIFEST_SHA,'REFERENCE_SCOPE')
    require(scope.get('max_worker_seconds')==300,'WORKER_BOUND')
    a,words,_=c.initial();hmod=import_file('h_step',c.paths['h_step'])
    require(scope.get('initial_full_digest')==hmod.array_hash(a)
        and scope.get('initial_H_sha256')==c.wire.digest(words).hex(),'INITIAL_SCOPE')
    return scope,c,acceptance

def worker(root):
    root=host_path(root).resolve();require(root.parent==HERE/'runtime/hybrid_joint_runs','OUTPUT_SCOPE')
    scope,c,acceptance=checked_scope(root/'scope.json');reg=Registry();reference=SavedReference()
    runner=import_file('gui_existing_joint_lease',reg.path_for('runner_lease'))
    began=time.monotonic();scope_sha=sha(root/'scope.json')
    class JointLease(runner.Lease):
        def init__(self):
            self.job=root;self.config={'campaign_id':scope['gpu_lease_id'],'stage':'ACTUAL_HYBRID_THREE_STEPS','queue_s':10}
            self.ticket={'config':self.config,'identity_key':canonical(scope),'job_dir':str(root),'scope':'3 actual GPU/PL steps only'}
        def check(self,phase='check'):
            require(time.monotonic()-began<300,'WORKER_DEADLINE')
            require(sha(root/'scope.json')==scope_sha and source_pins()==scope['source_sha256'],'SCOPE_OR_SOURCE_CHANGED')
            validate_short_scope(scope,c,acceptance)
            require(not (root/'STOP_REQUEST.json').exists(),'STOP_REQUESTED')
            require(not runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists(),'RESOURCE_QUARANTINE')
    lease=JointLease();handle=None;torch=None;adapter=None;rows=[];timing=Timings()
    try:
        handle,queue_s=lease.acquire();lease.check('before_import')
        scratch=Path('/tmp')/('hybrid-joint-'+scope['run_id']);scratch.mkdir()
        os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR=str(scratch/'flyvis'),
            MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'mpl'),NUMBA_CACHE_DIR=str(scratch/'numba'))
        import torch as t
        torch=t;torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        require(torch.cuda.is_available(),'CUDA_REQUIRED_NO_FALLBACK')
        require(torch.tensor([1.],device='cuda').add(1).item()==2,'CUDA_TENSOR_PROBE')
        Full=import_file('gui_joint_full_model',reg.path_for('full')).FullNetworkOracle
        oracle=Full(reg.path_for('identity'),model_path=reg.data['runtime']['model_path'],device='cuda')
        Decode=import_file('gui_joint_official_decoder',reg.path_for('decoder')).OfficialDecoderService
        decoder=Decode(reg.data['runtime']['model_path'],reg.path_for('decoder_contract'),device='cuda',check_scope=lease.check)
        from hybrid_gpu import GPUCandidates
        producer=GPUCandidates(reg,c,oracle,torch,timing)
        frames=np.array(reg.input('ON60')[0,200:203,0],copy=True)
        write(root/'GPU_READY.json',dict(run_id=scope['run_id'],utc=utc(),device=torch.cuda.get_device_name(),
              board_connected=False,scope_sha256=scope_sha,waiting_for='BOARD_READY.json'))
        # This one-time coordination gate neither probes the TCP listener nor sends HELLO.
        while not (root/'BOARD_READY.json').exists():lease.check('waiting_for_board_ready');time.sleep(.2)
        ready=load(root/'BOARD_READY.json')
        require(ready.get('run_id')==scope['run_id'] and ready.get('server_session')==scope['expected_server_session']
            and ready.get('boot_id')==scope['expected_boot_id'] and ready.get('status')=='TCP_LISTENING','BOARD_READY_IDENTITY')
        adapter=connect_live(c,scope,acceptance,producer,decoder,root/'pc',lease.check,candidate_validator=reference.check)
        for j,frame in enumerate(frames):
            row=adapter.step(frame);rows.append(row)
            write(root/'progress.json',dict(run_id=scope['run_id'],status='ACTUAL_COMMITTED',completed=len(rows),last=row))
        adapter.close();producer.check_unchanged();decoder.assert_weights_unchanged();torch.cuda.synchronize();reg.unchanged();c.unchanged()
        comparisons=[]
        for j,k in enumerate(range(200,203)):
            state=np.load(root/f'pc/committed_full_{k}.npy',allow_pickle=False);flow=np.load(root/f'pc/flow_{k}.npy',allow_pickle=False)
            require(np.allclose(state,reference.states[j],atol=1e-5,rtol=1e-5),'COMMITTED_STATE_REFERENCE')
            require(np.allclose(flow,reference.flows[j],atol=1e-5,rtol=1e-5),'OFFICIAL_FLOW_REFERENCE')
            comparisons.append(dict(step=k,state_max_abs=float(np.max(np.abs(state-reference.states[j]))),
                flow_max_abs=float(np.max(np.abs(flow-reference.flows[j])))))
        write(root/'result.json',dict(status='PC_THREE_COMMITS_PASS_PENDING_PS_AUDIT',run_id=scope['run_id'],rows=rows,
            completed=3,native_H_production_updates=producer.native_H_update_count,producer_calls=producer.calls,
            device=torch.cuda.get_device_name(),model=reg.data['model'],reference_comparisons=comparisons,
            numerical_profile='H_A3R1_Q24_R_ORIGINAL_FP32',queue_s=queue_s,total_s=time.monotonic()-began,
            timing=timing.summary(),peak_allocated_bytes=torch.cuda.max_memory_allocated(),PL_proven_global_ids=[],
            REALTIME_STREAM_PASS='NOT_CLAIMED',GUI_launches=0,PS_audit='PENDING'))
    except BaseException as exc:
        write(root/'result.json',dict(status='FAILED_OR_UNKNOWN',error=repr(exc),completed=len(rows),rows=rows,
              phase=None if adapter is None else adapter.barrier.phase,PL_proven_global_ids=[],automatic_retry=False))
        raise
    finally:
        if adapter is not None:adapter.close()
        waited=False
        try:
            if torch is not None and torch.cuda.is_available():torch.cuda.synchronize();waited=True
        finally:
            if handle is not None:handle.close()
            write(root/'exit.json',dict(utc=utc(),GPU_inflight_waited=waited,lease_closed=handle is not None))
            files={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file() and p.name not in ('worker.log','manifest.json')}
            write(root/'manifest.json',{'files':files,'evidence_level':'PC_JOINT_RESULT_REQUIRES_INDEPENDENT_PS_AUDIT'})

def execute(scope_path):
    require(os.name=='nt','WINDOWS_LAUNCHER_REQUIRED')
    scope,_,_=checked_scope(scope_path);reg=Registry()
    require(len(scope['run_id'])==32 and all(ch in '0123456789abcdef' for ch in scope['run_id']),'RUN_ID')
    root=HERE/'runtime/hybrid_joint_runs'/scope['run_id'];root.mkdir(parents=True,exist_ok=False)
    write(root/'scope.json',scope);print(str(root),flush=True)
    def linux(p):return '/mnt/'+str(p)[0].lower()+'/'+str(p)[3:].replace('\\','/')
    with (root/'worker.log').open('xb') as log:
        proc=subprocess.Popen(['wsl.exe','-d','FlyVisCPU','--exec',reg.data['runtime']['python'],'-B','-u',linux(Path(__file__)),
                               '--worker',linux(root)],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while proc.poll() is None:time.sleep(.3)
        except BaseException:
            write(root/'STOP_REQUEST.json',{'utc':utc(),'reason':'CONTROLLER_STOP'});proc.wait(timeout=30);raise
    write(root/'launcher_exit.json',{'utc':utc(),'exit_code':proc.returncode})
    require(proc.returncode==0,'JOINT_WORKER_FAILED '+str(root))
    print(str(root/'result.json'),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true')
    g.add_argument('--execute');g.add_argument('--worker');g.add_argument('--stop');a=p.parse_args()
    if a.worker:worker(a.worker)
    elif a.execute:execute(a.execute)
    elif a.stop:
        root=host_path(a.stop).resolve();require(root.parent==HERE/'runtime/hybrid_joint_runs','STOP_SCOPE')
        write(root/'STOP_REQUEST.json',{'utc':utc(),'reason':'USER_STOP'})
    else:print(__import__('json').dumps(preflight(),indent=2))
