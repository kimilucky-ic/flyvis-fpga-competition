"""One explicitly authorized recorded-input Full CUDA run; reuses frozen producer APIs.

No camera, GUI server, neural equations, cached activities, or board operations.
"""
import argparse
from datetime import datetime, timezone, timedelta
import os
from pathlib import Path
import time
import uuid
import numpy as np
from live_protocol import HERE, Registry, canonical, host_path, load, require, sha, utc, write
from live_worker import import_file


def prepare():
    registry = Registry()
    run_id = uuid.uuid4().hex
    root = HERE / 'evidence' / ('recorded_gpu_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + run_id[:8])
    root.mkdir()
    now = datetime.now(timezone.utc)
    scope = dict(schema='flyvis-recorded-full-once/v1', run_id=run_id,
        confirmed_by_user=True, authorization_reference='User: 赶紧开始吧我不是录过一段视频吗就用那个跑一遍',
        start_utc=now.isoformat(), end_utc=(now + timedelta(seconds=900)).isoformat(),
        max_runs=1, max_steps=609, mode='Full', camera_open=False, board_enabled=False,
        registry_sha256=canonical(registry.data), harness_sha256=sha(__file__),
        input_folder=registry.data['camera']['folder'])
    write(root / 'scope.json', scope)
    print(str(root), flush=True)


def run(root):
    root = host_path(root).resolve()
    require(root.parent == HERE / 'evidence', 'OUTPUT_SCOPE')
    scope = load(root / 'scope.json')
    require(not (root / 'attempt.json').exists(), 'ONE_ATTEMPT_ONLY')
    write(root / 'attempt.json', dict(pid=os.getpid(), started_utc=utc()))
    registry = Registry()
    require(canonical(registry.data) == scope['registry_sha256'] and sha(__file__) == scope['harness_sha256'], 'SOURCE_CHANGED')
    runner = import_file('recorded_existing_lease', registry.path_for('runner_lease'))
    started = time.monotonic()
    audit = [-1.]
    def check(operation='check'):
        require(scope['schema']=='flyvis-recorded-full-once/v1' and scope['confirmed_by_user'] is True
            and scope['mode']=='Full' and scope['max_runs']==1 and scope['max_steps']==609
            and scope['board_enabled'] is False and scope['camera_open'] is False, 'SCOPE')
        now = datetime.now(timezone.utc)
        begin, end = [datetime.fromisoformat(scope[k]) for k in ('start_utc','end_utc')]
        require(0 < (end-begin).total_seconds() <= 900 and begin <= now < end, 'SCOPE_EXPIRED')
        require(not (root / 'STOP_REQUEST.json').exists(), 'STOP_REQUESTED')
        if time.monotonic()-audit[0] >= .25:
            require(load(root/'scope.json') == scope, 'SCOPE_CHANGED')
            registry.unchanged()
            for marker in ('RESOURCE_QUARANTINE.json','EXTERNAL_GPU_BUSY.json','BOARD_RESERVED.json'):
                require(not runner.own_path('runtime', marker).exists(), marker)
            audit[0] = time.monotonic()
    class Lease(runner.Lease):
        def init__(self):
            self.job=root
            self.config=dict(campaign_id='RECORDED_'+scope['run_id'],stage='GUI_RECORDED_FULL_ONCE',queue_s=15)
            self.ticket=dict(config=self.config,identity_key=canonical(scope),job_dir=str(root),scope=scope)
        def check(self, operation='check'): check(operation)
    handle=None;torch=None;completed=0;success=False
    def status(state, **extra):
        row=dict(status=state,run_id=scope['run_id'],step=completed,total_steps=609,
            updated_utc=utc(),wall_time_s=time.monotonic()-started,**extra)
        write(root/'status.json',row)
        print(__import__('json').dumps(row),flush=True)
    try:
        status('VERIFYING_RECORDED_INPUT')
        reader=import_file('recorded_input_reader',registry.path_for('camera_reader'))
        identity,x,t,at=reader.load_frozen_input(scope['input_folder'])
        require(x.shape==(1,609,1,721), 'INPUT_STEPS')
        folder=host_path(scope['input_folder'])
        input_sha=sha(folder/'stimulus.npy')
        binding=dict(input_identity=identity,stimulus_sha256=input_sha,
            input_identity_sha256=sha(folder/'INPUT_IDENTITY.json'),manifest_sha256=sha(folder/'manifest.json'),
            model=registry.data['model'],node_map_sha256=registry.pins['nodes']['sha256'],
            source_kind='recorded_camera_frozen',input_time_sha256=sha(folder/'time.npy'),
            activity_time_sha256=sha(folder/'activity_time.npy'),dt_s=.005,
            initial_state_semantics='G2 full gray-adapted a0; fresh start at selected segment, not video-middle state',
            scientific_direction_metrics='NOT_APPLICABLE_UNCONTROLLED_CAMERA_NO_CALIBRATED_DIRECTION')
        write(root/'run_identity.json',dict(run_id=scope['run_id'],mode='Full',binding=binding,
            source_pins=registry.pins,execution_kind='new_inference_from_recorded_input',PL_execution=False))
        np.save(root/'stimulus.npy',x);np.save(root/'time.npy',t);np.save(root/'activity_time.npy',at)
        source_time=np.load(folder/'source_time.npy',allow_pickle=False)
        np.save(root/'source_frame_index.npy',np.searchsorted(source_time,t,side='right')-1)
        status('WAITING_FOR_GPU')
        handle,queue_s=Lease().acquire();check('before_torch')
        preload=time.monotonic()
        scratch=Path('/tmp')/('flyvis-gui-recorded-'+scope['run_id'])
        scratch.mkdir(parents=True,exist_ok=True)
        os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',CUDA_VISIBLE_DEVICES='0',
            FLYVIS_ROOT_DIR=str(scratch/'flyvis'),MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'matplotlib'),
            NUMBA_CACHE_DIR=str(scratch/'numba'))
        write(root/'environment.json',{key:os.environ[key] for key in ('CUDA_VISIBLE_DEVICES','FLYVIS_ROOT_DIR','MPLBACKEND','MPLCONFIGDIR','NUMBA_CACHE_DIR','CUBLAS_WORKSPACE_CONFIG')})
        import torch as torch_module
        torch=torch_module
        require(torch.cuda.is_available(),'CUDA_REQUIRED_NO_CPU_FALLBACK')
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        probe=torch.tensor([2.,3.],device='cuda').square().sum();torch.cuda.synchronize()
        require(probe.item()==13.,'CUDA_KERNEL_PROBE')
        device=dict(type='cuda',name=torch.cuda.get_device_name(),torch_version=torch.__version__,cuda_version=torch.version.cuda)
        status('PRELOADING',device=device)
        Full=import_file('recorded_original_full',registry.path_for('full')).FullNetworkOracle
        oracle=Full(registry.path_for('identity'),model_path=registry.data['runtime']['model_path'],device='cuda')
        Decode=import_file('recorded_official_decoder',registry.path_for('decoder')).OfficialDecoderService
        decoder=Decode(registry.data['runtime']['model_path'],registry.path_for('decoder_contract'),device='cuda',check_scope=check)
        state=torch.as_tensor(np.load(registry.path_for('initial'),allow_pickle=False),device='cuda',dtype=torch.float32).clone()
        frames=torch.as_tensor(np.array(x[0,:,0],copy=True),device='cuda')
        torch.cuda.synchronize();preload_s=time.monotonic()-preload
        states=np.lib.format.open_memmap(root/'activities_full.npy',mode='w+',dtype=np.float32,shape=(1,609,45669))
        flow=np.lib.format.open_memmap(root/'flow.npy',mode='w+',dtype=np.float32,shape=(1,609,2,721))
        neural_s=0.;decode_s=0.;chunks=[];compute_start=time.monotonic()
        with (root/'step_commits.jsonl').open('x',encoding='utf-8') as log:
            for a in range(0,609,32):
                b=min(a+32,609);rows=[];torch.cuda.synchronize();tick=time.monotonic()
                for k in range(a,b):
                    check('before_step')
                    candidate=oracle.step(state,frames[k])
                    require(candidate.shape==(45669,) and bool(torch.isfinite(candidate).all()),'INVALID_CANDIDATE')
                    check('before_commit');state=candidate
                    rows.append(state.detach().cpu().numpy().copy());completed=k+1
                    log.write(__import__('json').dumps(dict(run_id=scope['run_id'],step=k,state_token=k+1,status='COMMITTED',
                        input_time_s=float(t[k]),activity_time_s=float(at[k]),old_state_source='OWN_LIVE_COMMITTED_STATE'))+'\n')
                torch.cuda.synchronize();n=time.monotonic()-tick;neural_s+=n
                batch=np.asarray(rows,dtype=np.float32)[None]
                torch.cuda.synchronize();tick=time.monotonic()
                decoded=decoder.decode(batch,chunk_frames=32)
                torch.cuda.synchronize();d=time.monotonic()-tick;decode_s+=d
                check('before_publish');states[:,a:b]=batch;flow[:,a:b]=decoded;states.flush();flow.flush();log.flush()
                event=dict(start_step=a,stop_step=b,neural_s=n,decoder_s=d,utc=utc())
                chunks.append(event);write(root/'chunks.json',chunks)
                status('RUNNING',device=device,neural_s=neural_s,decoder_s=decode_s)
        compute_wall_s=time.monotonic()-compute_start
        oracle.assert_weights_unchanged();decoder.assert_weights_unchanged();registry.unchanged()
        require(sha(folder/'stimulus.npy')==input_sha,'INPUT_CHANGED')
        np.save(root/'t4t5.npy',states[0][:,registry.data['central_global_ids']])
        np.save(root/'final_state_full.npy',states[0,-1])
        result=dict(schema='flyvis-recorded-full-result/v1',status='PASS_ACTUAL_RECORDED_FULL_GPU',run_id=scope['run_id'],
            mode='Full',device=device,backend='original_FlyVis_CUDA',decoder_backend='official_DecoderGAVP_CUDA_eval',
            execution_kind='new_inference_from_recorded_input',display_kind='OFFLINE_REPLAY_AFTER_COMPUTE',
            actual_new_neural_computation=True,actual_new_decoder_computation=True,neural_steps=completed,decoder_frames=609,
            input_source_frames=len(source_time),simulation_duration_s=609*.005,source_span_s=float(source_time[-1]),
            queue_s=queue_s,preload_s=preload_s,neural_s=neural_s,decoder_s=decode_s,compute_wall_s=compute_wall_s,
            neural_steps_per_s=609/neural_s,combined_compute_steps_per_s=609/compute_wall_s,
            network_weights_unchanged=True,decoder_state_unchanged=True,all_finite=bool(np.isfinite(states).all() and np.isfinite(flow).all()),
            peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),PL_execution=False,FPGA_status='NOT_CONNECTED',
            camera_opened=False,LIVE_CAMERA_GPU_PASS='NOT_RUN',LIVE_INTERACTIVE_GUI_PASS='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN',
            central_global_ids=registry.data['central_global_ids'],types=registry.data['types'],binding=binding,completed_utc=utc())
        require(completed==609 and result['all_finite'],'INCOMPLETE')
        write(root/'result.json',result)
        pins={p.name:sha(p) for p in root.iterdir() if p.is_file() and p.name not in ('manifest.json','status.json','shutdown.json','process.log')}
        write(root/'manifest.json',dict(run_id=scope['run_id'],files_sha256=pins))
        success=True;status('COMPLETED',neural_s=neural_s,decoder_s=decode_s,compute_wall_s=compute_wall_s)
    except BaseException as exc:
        status('FAILED',error=repr(exc));raise
    finally:
        synced=False
        try:
            if torch is not None:torch.cuda.synchronize()
            synced=True
        except BaseException as exc:
            write(runner.own_path('runtime','RESOURCE_QUARANTINE.json'),dict(reason='RECORDED_CUDA_COMPLETION_UNKNOWN',error=repr(exc),run_id=scope['run_id']))
            raise
        finally:
            if handle:handle.close()
            write(root/'shutdown.json',dict(run_id=scope['run_id'],GPU_work_completion_confirmed=synced,
                shared_lock_handle_closed=handle is not None,status='COMPLETED' if success else 'FAILED',utc=utc()))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--run')
    args=parser.parse_args()
    if args.prepare:prepare()
    elif args.run:run(args.run)
    else:parser.error('choose --prepare or --run')
