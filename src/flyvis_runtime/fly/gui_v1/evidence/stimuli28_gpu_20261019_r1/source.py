"""One bounded Full GPU campaign. Reuses original FlyVis and DecoderGAVP.

No neuronal equations, board/camera operations, training, or response cache.
Each of the 28 conditions independently starts from the same frozen bias a0.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import uuid

import numpy as np

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent.parent/'fpga/flyvis-circuit-selection/controlled_stimuli_20261019_v1'
PACK_SHA = '7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
MANIFEST_SHA = 'a398175a2f9080d5a1aaa49ceb57ee3fe57dcbe282521e55cc373fa0669302c1'
BIAS_SHA = 'd276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def raw_sha(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def prepare(dest):
    assert sha(PACK_ROOT/'PACK.json') == PACK_SHA
    assert sha(PACK_ROOT/'DELIVERY_MANIFEST.json') == MANIFEST_SHA
    pack = read(PACK_ROOT/'PACK.json')
    assert len(pack['conditions']) == 28 and pack['all_backends_status'] == 'NOT_RUN'
    a0 = np.load(PACK_ROOT/pack['initial_state_assets']['original_bias_fp32']['path'],allow_pickle=False)
    assert a0.shape == (45669,) and a0.dtype == np.float32 and raw_sha(a0) == BIAS_SHA
    assert shutil.disk_usage(dest.parent).free > 6*1024**3
    dest.mkdir(exist_ok=False)
    scope = dict(schema='flyvis-stimuli28-full-gpu-scope/v1',campaign_id=uuid.uuid4().hex,
                 confirmed_by_current_user=True,
                 authorization='Current user: GPU run all28 frozen conditions with fixed initial state/model/dt; save real T4T5 and official flow. No board.',
                 PACK_sha256=PACK_SHA,manifest_sha256=MANIFEST_SHA,
                 condition_ids=[c['condition_id'] for c in pack['conditions']],
                 maximum_conditions=28,steps_per_condition=485,total_steps=13580,dt_s=.005,
                 initial_kind='original_bias_fp32',initial_raw_sha256=BIAS_SHA,
                 script_sha256=sha(__file__),GPU_required=True,board_operations=False,camera=False,
                 numerical_validation=dict(atol=1e-5,rtol=1e-5,scope='independent saved-state/flow audit; not universal bitwise equivalence'),
                 deadline_s=1200,retries=0)
    write(dest/'SCOPE.json',scope)
    shutil.copyfile(__file__,dest/'source.py')
    print('PREPARED',dest,flush=True)


def run(dest):
    from live_protocol import Registry, host_path, canonical
    scope = read(dest/'SCOPE.json'); start = time.monotonic()
    assert scope['confirmed_by_current_user'] and scope['script_sha256'] == sha(__file__)
    assert scope['maximum_conditions'] == 28 and scope['total_steps'] == 13580
    write(dest/'ATTEMPT.json',dict(pid=os.getpid(),epoch_ns=time.time_ns(),command=[sys.executable,*sys.argv]))
    registry = Registry()
    runner = module('stimuli28_original_lease',registry.path_for('runner_lease'))
    def check(operation='check'):
        assert time.monotonic()-start < scope['deadline_s'], 'GPU_CAMPAIGN_DEADLINE'
        assert not (dest/'STOP_REQUEST.json').exists(), 'USER_STOP_REQUEST'
        for marker in ('RESOURCE_QUARANTINE.json','EXTERNAL_GPU_BUSY.json','BOARD_RESERVED.json'):
            assert not runner.own_path('runtime',marker).exists(), marker
    class Lease(runner.Lease):
        def init__(self):
            self.job=dest;self.config=dict(campaign_id=scope['campaign_id'],stage='STIMULI28_FULL_GPU',queue_s=15)
            self.ticket=dict(config=self.config,identity_key=canonical(scope),job_dir=str(dest),scope=scope)
        def check(self,operation='check'):check(operation)
    handle=None; torch=None; completed=[]
    try:
        handle,queue_s=Lease().acquire()
        assert sha(PACK_ROOT/'PACK.json')==PACK_SHA and sha(PACK_ROOT/'DELIVERY_MANIFEST.json')==MANIFEST_SHA
        pack=read(PACK_ROOT/'PACK.json');manifest=read(PACK_ROOT/'DELIVERY_MANIFEST.json')
        for entry in manifest['files']:
            path=(PACK_ROOT/entry['path']).resolve();assert path.is_relative_to(PACK_ROOT.resolve())
            assert path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256'],entry['path']
        assert [c['condition_id'] for c in pack['conditions']]==scope['condition_ids']
        scratch=Path('/tmp')/('flyvis-stimuli28-'+scope['campaign_id']);scratch.mkdir(exist_ok=False)
        os.environ.update(CUDA_VISIBLE_DEVICES='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',
            OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
            FLYVIS_ROOT_DIR=str(scratch/'flyvis'),MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'mpl'),
            NUMBA_CACHE_DIR=str(scratch/'numba'),PYTHONDONTWRITEBYTECODE='1')
        from static_connectome import prepare_static_connectome,confirm_static_connectome
        graph=prepare_static_connectome(registry,scratch/'flyvis/connectome',scope['campaign_id'])
        import torch as torch_module
        torch=torch_module;torch.set_num_threads(1);torch.set_num_interop_threads(1)
        torch.manual_seed(0);np.random.seed(0);torch.set_default_device('cuda')
        torch.set_flush_denormal(False);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        assert torch.cuda.is_available()
        assert torch.tensor([2.,3.],device='cuda').square().sum().item()==13.
        sys.path.insert(0,str(HERE.parent/'gpu_phase2'))
        Full=module('stimuli28_unchanged_full',registry.path_for('full')).FullNetworkOracle
        oracle=Full(registry.path_for('identity'),model_path=registry.data['runtime']['model_path'],device='cuda')
        confirm_static_connectome(oracle,graph)
        Decode=module('stimuli28_unchanged_decoder',registry.path_for('decoder')).OfficialDecoderService
        decoder=Decode(registry.data['runtime']['model_path'],registry.path_for('decoder_contract'),device='cuda',check_scope=check)
        a0_path=PACK_ROOT/pack['initial_state_assets']['original_bias_fp32']['path']
        a0=np.load(a0_path,allow_pickle=False)
        assert raw_sha(a0)==BIAS_SHA
        assert np.array_equal(a0,oracle.params.nodes.bias.detach().cpu().numpy())
        initial_tensor=torch.as_tensor(a0.copy(),device='cuda')
        ids=np.load(PACK_ROOT/pack['T4T5_global_ids']['path'],allow_pickle=False)
        assert ids.shape==(8,721) and len(np.unique(ids))==5768
        np.save(dest/'initial_state.npy',a0);np.save(dest/'T4T5_global_ids.npy',ids)
        numeric=dict(name='ORIGINAL_FLYVIS_FP32_CUDA',dtype='float32',model_dt_s=.005,TF32=False,
            autocast=False,deterministic_algorithms=True,flush_denormal=False,threads=1,
            initial_kind='original_bias_fp32',initial_raw_sha256=BIAS_SHA,
            initialization='Each condition clones exact common45669 bias a0; no implicit grey adaptation',
            calculation='Unchanged Network.simulate -> forward -> _next_state',
            FPGA_order_bitwise_equivalence='NOT_CLAIMED_GPU_SUMMATION_ORDER_MAY_DIFFER',
            comparison_tolerance=scope['numerical_validation'])
        write(dest/'NUMERICAL_PROFILE.json',numeric)
        write(dest/'MODEL_IDENTITY.json',dict(model={k:v for k,v in registry.data['model'].items() if k!='initial_state_sha256'},
            actual_initial_raw_sha256=BIAS_SHA,source_pins={k:registry.pins[k] for k in ('full','identity','decoder','decoder_contract','nodes','parameters')},
            graph=graph,decoder_state_sha256=decoder.contract['decoder_state_sha256'],recursive_eval=True,
            device=dict(type='cuda',name=torch.cuda.get_device_name(),torch=torch.__version__,cuda=torch.version.cuda),
            official_source_status=subprocess.check_output(['git','-C',str(HERE.parent/'upstream/flyvis'),'status','--porcelain','--untracked-files=no'],text=True)))
        print('GPU_MODEL_READY',torch.cuda.get_device_name(),'28x485',flush=True)
        preload_s=time.monotonic()-start
        for index,c in enumerate(pack['conditions']):
            check('before_condition');oracle.assert_weights_unchanged();decoder.assert_weights_unchanged()
            cid=c['condition_id'];run_id=uuid.uuid4().hex;folder=dest/'conditions'/cid;folder.mkdir(parents=True)
            x=np.load(PACK_ROOT/c['paths']['input']['path'],allow_pickle=False)
            assert x.shape==(485,721) and x.dtype==np.float32 and raw_sha(x)==c['input_raw_sha256']
            movie=torch.as_tensor(x.copy()[None,:,None],device='cuda')
            state=oracle.net._state_api(oracle.AutoDeref(nodes=oracle.AutoDeref(activity=initial_tensor.clone()[None]),edges=oracle.AutoDeref()))
            torch.cuda.synchronize();a=time.perf_counter();e0,e1=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
            e0.record()
            with torch.no_grad():trajectory=oracle.net.simulate(movie,.005,initial_state=state)
            e1.record();torch.cuda.synchronize();neural_s=time.perf_counter()-a
            assert trajectory.shape==(1,485,45669) and trajectory.dtype==torch.float32
            a=time.perf_counter();full=trajectory.detach().cpu().numpy()[0].copy();copy_s=time.perf_counter()-a
            assert np.isfinite(full).all() and torch.equal(state.nodes.activity[0],initial_tensor)
            a=time.perf_counter();flow=decoder.decode(full[None],chunk_frames=32)[0];torch.cuda.synchronize();decode_s=time.perf_counter()-a
            assert flow.shape==(485,2,721) and flow.dtype==np.float32 and np.isfinite(flow).all()
            spatial=full[:,ids.reshape(-1)];means=spatial.reshape(485,8,721).mean(axis=2,dtype=np.float64)
            a=time.perf_counter()
            for name,array in [('input.npy',x),('states.npy',full),('spatial.npy',spatial),('means.npy',means),('flow.npy',flow)]:np.save(folder/name,array)
            for role,name in [('input_time','input_time.npy'),('state_time','activity_time.npy')]:shutil.copyfile(PACK_ROOT/c['paths'][role]['path'],folder/name)
            file_info={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(folder.iterdir())}
            result=dict(schema='flyvis-stimuli28-full-gpu-condition/v1',status='COMPLETED_ACTUAL_GPU',run_id=run_id,
                campaign_id=scope['campaign_id'],condition_id=cid,PACK_sha256=PACK_SHA,
                input_raw_sha256=c['input_raw_sha256'],input_source_file_sha256=c['paths']['input']['sha256'],
                initial_raw_sha256=BIAS_SHA,initial_file_sha256=sha(dest/'initial_state.npy'),
                numeric_profile_sha256=sha(dest/'NUMERICAL_PROFILE.json'),model_checkpoint_sha256=pack['model_checkpoint_sha256'],
                steps=485,dt_s=.005,input_time_offset_s=0,backend='original_FlyVis_Full_GPU',
                device='cuda',device_name=torch.cuda.get_device_name(),decoder='official_DecoderGAVP',recursive_eval=True,
                decoder_state_sha256=decoder.contract['decoder_state_sha256'],
                display_kind='OFFLINE_REPLAY',actual_GPU_neural_steps=485,actual_decoder_frames=485,
                PL_execution=False,FPGA_status='NOT_CONNECTED',files=file_info,
                timing=dict(neural_host_synchronized_s=neural_s,neural_cuda_stream_ms=e0.elapsed_time(e1),
                            device_to_host_s=copy_s,official_decode_host_s=decode_s,save_and_hash_s=time.perf_counter()-a),
                execution_completed_epoch_ns=time.time_ns(),numerical_audit='PENDING_SEPARATE_AUDIT',functional_acceptance='NOT_EVALUATED')
            write(folder/'run.json',result);completed.append(result)
            with (dest/'PROGRESS.json').open('w',encoding='utf-8') as f:json.dump(dict(completed=index+1,total=28,last=cid,elapsed_s=time.monotonic()-start),f)
            print('CONDITION_COMPLETE',index+1,cid,'neural_s',round(neural_s,3),'decode_s',round(decode_s,3),flush=True)
            del trajectory,full,flow,spatial,movie,state
        oracle.assert_weights_unchanged();decoder.assert_weights_unchanged();registry.unchanged()
        assert sha(PACK_ROOT/'PACK.json')==PACK_SHA and sha(PACK_ROOT/'DELIVERY_MANIFEST.json')==MANIFEST_SHA
        assert scope['script_sha256']==sha(__file__) and scope==read(dest/'SCOPE.json')
        campaign=dict(schema='flyvis-stimuli28-gpu-result/v1',status='COMPLETED_ACTUAL_GPU_PENDING_AUDIT',
            campaign_id=scope['campaign_id'],conditions=completed,total_neural_steps=13580,total_decoder_frames=13580,
            common_initial_raw_sha256=BIAS_SHA,PACK_sha256=PACK_SHA,numeric_profile_sha256=sha(dest/'NUMERICAL_PROFILE.json'),
            model_checkpoint_sha256=pack['model_checkpoint_sha256'],network_weights_unchanged=True,decoder_state_unchanged=True,
            total_wall_s=time.monotonic()-start,queue_s=queue_s,preload_s=preload_s,
            peak_GPU_allocated_bytes=torch.cuda.max_memory_allocated(),peak_GPU_reserved_bytes=torch.cuda.max_memory_reserved(),
            GPU=True,PL_execution=False,FPGA_status='NOT_CONNECTED',display_kind='OFFLINE_REPLAY')
        write(dest/'RESULT.json',campaign)
        files=[]
        for p in sorted(dest.rglob('*')):
            if p.is_file() and p.suffix not in ('.log',):files.append(dict(path=str(p.relative_to(dest)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)))
        write(dest/'RESULT_MANIFEST.json',dict(schema='flyvis-stimuli28-gpu-manifest/v1',files=files))
        print('ALL_28_COMPLETE_PENDING_AUDIT',round(campaign['total_wall_s'],3),flush=True)
    except BaseException as error:
        write(dest/'FAILURE.json',dict(error=repr(error),traceback=traceback.format_exc(),completed_conditions=len(completed),evidence='No incomplete campaign admitted'))
        raise
    finally:
        if torch is not None and torch.cuda.is_initialized():torch.cuda.synchronize()
        if handle is not None:
            import fcntl
            fcntl.flock(handle,fcntl.LOCK_UN);handle.close()
        write(dest/'PROCESS_CLEANUP.json',dict(shared_lease_closed=True,epoch_ns=time.time_ns()))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run']);p.add_argument('output',type=Path)
    args=p.parse_args();prepare(args.output) if args.action=='prepare' else run(args.output)
