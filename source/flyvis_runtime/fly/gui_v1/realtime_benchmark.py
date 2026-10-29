"""Explicit manual, bounded power-mode A/B benchmark. Default plan is CPU-only.

No power switching, camera, GUI, scientific campaign or board operations.
"""
import argparse
from datetime import datetime,timezone,timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import numpy as np
from live_protocol import HERE,Registry,canonical,host_path,load,require,sha,utc,write
from live_worker import import_file
from realtime_timing import Timings,CudaProbes

MODES=('quiet','balanced','performance','current_unconfirmed')
VARIANTS=('baseline','sampled','combined_checks','owned_checks')
REFERENCE=HERE/'evidence/recorded_gpu_20261012_172029_4d03e3fb'


def plan(power_mode,variant):
    require(power_mode in MODES and variant in VARIANTS,'BENCHMARK_SELECTION')
    return dict(schema='flyvis-realtime-benchmark/v1',power_mode_user_label=power_mode,variant=variant,
        power_mode_verified_by_program=False,program_changes_power_settings=False,
        warmup_steps=32,sampling_wall_s=10,max_steps=4000,max_session_s=180,display_target_Hz=20,
        input_kind='FROZEN_RECORDED_609_REPEATED_FOR_BENCHMARK_ONLY',repeat_rule='x[k % 609]; continuous own state; reset a0 after warmup',
        original_neural_core_unchanged=True,model_dt_s=.005,TF32=False,deterministic=True,
        baseline='Full D2H each step; decoder/full-state evidence every 32 steps',
        sampled='Full state stays CUDA; original decoder + 5768 slice at 20Hz; no step skips',
        combined_checks='Original neural update; same three input predicates in one host copy; candidate gate retained',
        owned_checks='Private tensor validation proof reuse + identical GPU input index + exact packed decoder audits',
        cpu_threads=1,stop_gpu_temperature_C=85,min_available_RAM_MiB=1536,max_output_MiB=900,
        no_live_camera_or_GUI=True,PL_execution=False,LIVE_CAMERA_GPU_PASS='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN',
        scope_note='One variant in one user-selected power mode per manual invocation. No automatic retries or mode changes.')


class Telemetry:
    def init__(self,root):self.root=root;self.stop=threading.Event();self.error=None;self.rows=[];self.thread=None
    def start(self):
        self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def loop(self):
        try:
            try:import psutil
            except ImportError:psutil=None
            while not self.stop.is_set():
                p=subprocess.run(['nvidia-smi','--query-gpu=power.draw,utilization.gpu,clocks.sm,clocks.mem,temperature.gpu,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=3,check=True)
                vals=[v.strip() for v in p.stdout.splitlines()[0].split(',')]
                def number(v):
                    try:return float(v)
                    except ValueError:return None
                row=dict(utc=utc(),monotonic_s=time.monotonic(),**dict(zip(('GPU_W','GPU_percent','SM_MHz','VRAM_MHz','GPU_C','VRAM_MiB'),map(number,vals))))
                if psutil:
                    proc=psutil.Process();row.update(WSL_CPU_percent=psutil.cpu_percent(),process_threads=proc.num_threads(),RSS_MiB=proc.memory_info().rss/1048576,
                        available_RAM_MiB=psutil.virtual_memory().available/1048576,CPU_MHz=getattr(psutil.cpu_freq(),'current',None))
                else:row.update(WSL_CPU_percent=None,process_threads=None,RSS_MiB=None,available_RAM_MiB=None,CPU_MHz=None)
                row['CPU_power_W']=None;row['CPU_temperature_C']=None
                self.rows.append(row)
                with (self.root/'device_telemetry.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
                if row['GPU_C'] is not None and row['GPU_C']>=85:raise ValueError('TEMPERATURE_LIMIT')
                if row['available_RAM_MiB'] is not None and row['available_RAM_MiB']<1536:raise ValueError('MEMORY_LIMIT')
                self.stop.wait(1)
        except BaseException as e:self.error=str(e)
    def close(self):
        self.stop.set()
        if self.thread:self.thread.join(timeout=4)


def launch(power_mode,variant):
    require(os.name=='nt','MANUAL_WINDOWS_ENTRY_REQUIRED')
    active=HERE/'runtime/demo_active.json'
    require(not active.exists() or load(active)['state'] in ('STOPPED','START_FAILED'),'STOP_EXISTING_DEMO_FIRST')
    spec=plan(power_mode,variant);rid=uuid.uuid4().hex;root=HERE/'runtime/benchmarks'/rid;root.mkdir(parents=True)
    begin=datetime.now(timezone.utc)
    spec.update(run_id=rid,confirmed_by_user=True,authorization_reference='USER_MANUAL_BENCHMARK_EnableGPU_INVOCATION',
        start_utc=begin.isoformat(),end_utc=(begin+timedelta(seconds=180)).isoformat(),harness_sha256=sha(__file__),
        adapter_sha256={name:sha(HERE/name) for name in ('checked_full.py','decoder_audit.py')})
    write(root/'scope.json',spec);print('One manual benchmark; power mode is user controlled. Output: '+str(root),flush=True)
    def linux(p):return '/mnt/'+str(p)[0].lower()+'/'+str(p)[3:].replace('\\','/')
    flags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP
    with (root/'worker.log').open('ab') as log:
        write(root/'controller.json',dict(unix_time=time.time(),pid=os.getpid()))
        process=subprocess.Popen(['wsl.exe','-d','FlyVisCPU','--exec','/opt/flyvis-gpu-venv/bin/python','-B','-u',linux(HERE/'realtime_benchmark.py'),'--worker',linux(root)],stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
        try:
            while process.poll() is None:
                write(root/'controller.json',dict(unix_time=time.time(),pid=os.getpid()))
                time.sleep(.5)
        except BaseException as exc:
            write(root/'STOP_REQUEST.json',dict(reason='LAUNCHER_STOP',error=repr(exc),utc=utc()))
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:print('STOP_WAITING_FOR_CUDA; no forced termination.',flush=True);raise
            raise
        finally:
            write(root/'launcher_result.json',dict(exit_code=process.poll(),worker_finished=process.poll() is not None,utc=utc()))
    require(process.returncode==0,'BENCHMARK_FAILED_SEE_WORKER_LOG '+str(root))
    print(json.dumps(load(root/'result.json'),ensure_ascii=False))


def worker(root):
    root=host_path(root).resolve();require(root.parent==HERE/'runtime/benchmarks','BENCHMARK_WRITE_SCOPE')
    spec=load(root/'scope.json');require(spec['confirmed_by_user'] and spec['harness_sha256']==sha(__file__),'BENCHMARK_NOT_AUTHORIZED')
    require(all(sha(HERE/name)==digest for name,digest in spec['adapter_sha256'].items()),'BENCHMARK_ADAPTER_CHANGED')
    expected=plan(spec['power_mode_user_label'],spec['variant'])
    require(all(spec[k]==v for k,v in expected.items()),'BENCHMARK_SCOPE_CHANGED')
    reg=Registry();runner=import_file('benchmark_original_lease',reg.path_for('runner_lease'))
    timing=Timings();telemetry=Telemetry(root);last_audit=[-1.];probes=None;compute=None;decoder_audit=None;torch=None;handle=None;steps=0;success=False
    monitor=[None]
    def audit(operation='check'):
        now=datetime.now(timezone.utc)
        require(datetime.fromisoformat(spec['start_utc'])<=now<datetime.fromisoformat(spec['end_utc']),'BENCHMARK_EXPIRED')
        require(not (root/'STOP_REQUEST.json').exists(),'BENCHMARK_STOP_REQUESTED')
        require(telemetry.error is None,'TELEMETRY_STOP '+str(telemetry.error))
        if time.monotonic()-last_audit[0]>.25:
            reg.unchanged();require(load(root/'scope.json')==spec,'BENCHMARK_CHANGED')
            require(all(sha(HERE/name)==digest for name,digest in spec['adapter_sha256'].items()),'BENCHMARK_ADAPTER_CHANGED')
            require(time.time()-load(root/'controller.json')['unix_time']<10,'BENCHMARK_CONTROLLER_DISCONNECTED')
            for marker in ('RESOURCE_QUARANTINE.json','EXTERNAL_GPU_BUSY.json','BOARD_RESERVED.json'):
                require(not runner.own_path('runtime',marker).exists(),marker)
            last_audit[0]=time.monotonic()
    def check(operation='check'):
        now=datetime.now(timezone.utc)
        require(datetime.fromisoformat(spec['start_utc'])<=now<datetime.fromisoformat(spec['end_utc']),'BENCHMARK_EXPIRED')
        if monitor[0]:return monitor[0].check(operation)
        return audit(operation)
    class Lease(runner.Lease):
        def init__(self):
            self.job=root;self.config=dict(campaign_id='BENCHMARK_'+spec['run_id'],stage=spec['variant'],queue_s=15)
            self.ticket=dict(config=self.config,identity_key=canonical(spec),job_dir=str(root),scope=spec)
        def check(self,operation='check'):check(operation)
    try:
        handle,queue_s=Lease().acquire();telemetry.start();check('before_torch')
        from stream_transport import AuditMonitor
        monitor[0]=AuditMonitor(audit)
        scratch=Path('/tmp')/('flyvis-gui-benchmark-'+spec['run_id'])
        os.environ.update(CUDA_VISIBLE_DEVICES='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',FLYVIS_ROOT_DIR=str(scratch/'flyvis'),
            MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'mpl'),NUMBA_CACHE_DIR=str(scratch/'numba'))
        tick=time.monotonic()
        import torch as torch_module
        torch=torch_module;require(torch.cuda.is_available(),'CUDA_REQUIRED');torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        Full=import_file('benchmark_original_full',reg.path_for('full')).FullNetworkOracle
        oracle=Full(reg.path_for('identity'),model_path=reg.data['runtime']['model_path'],device='cuda')
        Decode=import_file('benchmark_original_decoder',reg.path_for('decoder')).OfficialDecoderService
        decoder=Decode(reg.data['runtime']['model_path'],reg.path_for('decoder_contract'),device='cuda',check_scope=check)
        source=load(REFERENCE/'result.json');manifest=load(REFERENCE/'manifest.json')['files_sha256']
        require(source['binding']['model']==reg.data['model'],'BENCHMARK_INITIAL_MODEL_IDENTITY')
        for name in ('result.json','stimulus.npy','activities_full.npy'):require(sha(REFERENCE/name)==manifest[name],'BENCHMARK_REFERENCE_CHANGED')
        frames=torch.as_tensor(np.load(REFERENCE/'stimulus.npy',allow_pickle=False)[0,:,0],device='cuda')
        reference=np.load(REFERENCE/'activities_full.npy',mmap_mode='r',allow_pickle=False)
        require(sha(REFERENCE/'flow.npy')==manifest['flow.npy'],'BENCHMARK_FLOW_REFERENCE_CHANGED')
        reference_flow=np.load(REFERENCE/'flow.npy',mmap_mode='r',allow_pickle=False)
        initial=torch.as_tensor(np.load(reg.path_for('initial'),allow_pickle=False),device='cuda')
        compute=oracle;rejection_tests=[]
        if spec['variant'] in ('combined_checks','owned_checks'):
            from checked_full import CombinedCheckedFull,validate_rejections,validate_proof_rejections
            compute=CombinedCheckedFull(oracle,torch,timing,cache_validated_tensors=spec['variant']=='owned_checks')
            rejection_tests=validate_rejections(compute,initial,frames[0])
            if spec['variant']=='owned_checks':
                rejection_tests+=validate_proof_rejections(compute,initial,frames[0])
                from decoder_audit import PackedDecoderAudit
                decoder_audit=PackedDecoderAudit(decoder,timing).install()
        state=initial.clone();torch.cuda.synchronize();preload_s=time.monotonic()-tick
        tick=time.monotonic()
        for k in range(32):check('warmup');state=compute.step(state,frames[k])
        decoder.decode(state.detach().cpu().numpy()[None,None],chunk_frames=1);torch.cuda.synchronize()
        warmup_s=time.monotonic()-tick;state=initial.clone()
        # Main measurement must not include rejection tests or warmup timings.
        timing=Timings()
        if compute is not oracle:compute.timing=timing
        if decoder_audit:decoder_audit.timing=timing
        from spatial_state import SpatialRegistry
        spatial=SpatialRegistry();probes=CudaProbes(torch,timing)
        probes.wrap(oracle.net,'_next_state','neural_update_cuda_stream');probes.wrap(decoder.decoder,'forward','decoder_forward_cuda_stream')
        blocks=[];snapshots=[];last_display=-1.;written=0;violations=0;compared=0;maximum=0.;flow_maximum=0.;flow_violations=0;begin=time.monotonic()
        with (root/'step_commits.jsonl').open('x',encoding='utf-8') as commits:
            while time.monotonic()-begin<10 and steps<4000:
                with timing.measure('scope_gate'):check('step')
                with timing.measure('Full_step_host_including_checks'):candidate=compute.step(state,frames[steps%609])
                with timing.measure('finite_and_commit_gate'):
                    if spec['variant']=='owned_checks':
                        compute.validate_candidate(candidate);check('commit');state=compute.commit(candidate)
                    else:require(bool(torch.isfinite(candidate).all()),'NONFINITE_CANDIDATE');check('commit');state=candidate
                k=steps;steps+=1
                with timing.measure('commit_log'):
                    commits.write(json.dumps(dict(step_id=k,state_token=steps,status='COMMITTED',source_index=k%609))+'\n')
                if spec['variant']=='baseline':
                    with timing.measure('full_state_per_step_D2H'):blocks.append(state.detach().cpu().numpy().copy())
                    display=len(blocks)==32
                else:display=time.monotonic()-last_display>=.05
                if display:
                    if spec['variant']=='baseline':batch=np.asarray(blocks,dtype=np.float32)[None];blocks=[]
                    else:
                        with timing.measure('display_full_D2H'):batch=state.detach().cpu().numpy().copy()[None,None]
                    with timing.measure('decoder_host'):flow=decoder.decode(batch,chunk_frames=32)
                    full=batch[0,-1]
                    if k<609:
                        delta=np.abs(full-reference[0,k]);maximum=max(maximum,float(delta.max()));compared+=1
                        violations+=int(np.count_nonzero(delta>1e-5+1e-5*np.abs(reference[0,k])))
                        fd=np.abs(flow[0,-1]-reference_flow[0,k]);flow_maximum=max(flow_maximum,float(fd.max()))
                        flow_violations+=int(np.count_nonzero(fd>1e-5+1e-5*np.abs(reference_flow[0,k])))
                    with timing.measure('display_and_evidence_write'):
                        index=len(snapshots);file=root/f'chunk_{index:04}.npz'
                        np.savez(file,activity=batch if spec['variant']=='baseline' else spatial.extract(full),flow=flow,step_id=np.array(k))
                        written+=file.stat().st_size;require(written<900*1048576,'BENCHMARK_STORAGE_LIMIT')
                    probes.collect();snapshots.append(dict(step=k,elapsed_s=time.monotonic()-begin));last_display=time.monotonic()
            torch.cuda.synchronize();sample_wall_s=time.monotonic()-begin;probes.collect()
        require(violations==0 and flow_violations==0 and compared>0,'ORIGINAL_REFERENCE_PARITY_FAILED')
        oracle.assert_weights_unchanged();decoder.assert_weights_unchanged()
        write(root/'result.json',dict(status='PASS_BOUNDED_COMPUTE_BENCHMARK',run_id=spec['run_id'],spec=spec,preload_s=preload_s,warmup_s=warmup_s,
            sample_wall_s=sample_wall_s,model_steps=steps,steps_per_s=steps/sample_wall_s,display_samples=len(snapshots),stages=timing.summary(),
            reference_sample_count=compared,reference_max_abs=maximum,reference_violations=violations,atol=1e-5,rtol=1e-5,
            reference_flow_max_abs=flow_maximum,reference_flow_violations=flow_violations,
            device=torch.cuda.get_device_name(),snapshots=snapshots,partial_baseline_unpublished_steps=len(blocks),
            input_guard_adapter=compute.info() if compute is not oracle else None,input_rejection_tests=rejection_tests,
            packed_decoder_audit_calls=decoder_audit.calls if decoder_audit else 0,
            source_input_sha256=sha(REFERENCE/'stimulus.npy'),model=reg.data['model'],original_weights_unchanged=True,decoder_unchanged=True,
            LIVE_CAMERA_GPU_PASS='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN',GUI_display_FPS=None,source_to_screen_p95_ms=None,PL_execution=False))
        success=True
    except BaseException as e:write(root/'failure.json',dict(error=repr(e),step=steps,utc=utc()));raise
    finally:
        telemetry.close()
        if monitor[0]:monitor[0].close()
        try:
            if torch is not None:torch.cuda.synchronize()
            if probes:probes.close()
            if decoder_audit:decoder_audit.close()
            if compute is not None and hasattr(compute,'close'):compute.close()
        except BaseException as e:
            write(runner.own_path('runtime','RESOURCE_QUARANTINE.json'),dict(reason='BENCHMARK_CUDA_COMPLETION_UNKNOWN',error=repr(e)));raise
        finally:
            if handle:handle.close()
            write(root/'shutdown.json',dict(success=success,shared_lock_closed=handle is not None,utc=utc()))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--power-mode',choices=MODES,default='current_unconfirmed');p.add_argument('--variant',choices=VARIANTS,default='sampled')
    p.add_argument('--enable-gpu',action='store_true');p.add_argument('--worker');args=p.parse_args()
    if args.worker:worker(args.worker)
    elif args.enable_gpu:launch(args.power_mode,args.variant)
    else:print(json.dumps(plan(args.power_mode,args.variant),ensure_ascii=False,indent=2))
