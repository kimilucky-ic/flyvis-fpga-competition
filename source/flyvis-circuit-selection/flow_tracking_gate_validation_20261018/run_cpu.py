"""One bounded native official CPU run; no decoder/model substitutions or GPU."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
    FLYVIS_ROOT_DIR='/opt/flyvis-gpu-data',MPLBACKEND='Agg',PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import hashlib,json,time,traceback,subprocess,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PROJECT=ROOT.parent

def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):
    with (HERE/n).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,allow_nan=False)

def main():
    dump('RUN_STARTED.json',dict(time_ns=time.time_ns(),GPU=False))
    p=load('PREREGISTRATION.json');assert sha(HERE/'PREREGISTRATION.json')==load('ALGORITHM_FREEZE.json')['prereg_sha256']
    for rel,h in p['pins'].items():assert sha(PROJECT/rel)==h,rel
    import numpy as np
    import psutil
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    assert not torch.cuda.is_initialized() and shutil.disk_usage(HERE).free>5*2**30
    assert psutil.virtual_memory().available>2*2**30
    import flyvis
    from flyvis import NetworkView
    from flyvis.utils.tensor_utils import AutoDeref
    assert flyvis.device.type=='cpu'
    view=NetworkView('/opt/flyvis-gpu-data/results/flow/0000/000')
    checkpoint=Path(view.get_checkpoint('best'))
    assert sha(checkpoint)=='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
    expected=torch.load(checkpoint,map_location='cpu',weights_only=False)
    w=view.network(checkpoint='best',lazy=True);w.recover();net=w.network
    assert net.n_nodes==45669 and net.n_edges==1513231 and not net._state_hooks
    assert type(net.dynamics).__name__=='PPNeuronIGRSynapses'
    decoder=view.init_decoder(checkpoint='best')['flow'];decoder.eval()
    before={k:v.detach().clone() for k,v in decoder.state_dict().items()}
    assert not any(m.training for m in decoder.modules())
    assert all(torch.equal(v,expected['decoder']['flow'][k]) for k,v in before.items())
    grid=np.load(HERE.parent/'flow_tracking_pilot_20261018/GRID.npz');uv=grid['uv']
    assert np.array_equal(np.asarray(decoder.u)-15,uv[0]) and np.array_equal(np.asarray(decoder.v)-15,uv[1])
    bundle=HERE.parent/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
    initial_np=np.load(bundle/'initial_state_full.npy')
    initial=net._state_api(AutoDeref(nodes=AutoDeref(activity=torch.from_numpy(initial_np.copy()).reshape(1,-1)),edges=AutoDeref()))
    assert initial.nodes.activity.dtype==torch.float32
    np.save(HERE/'INITIAL_STATE.npy',initial_np)
    params=net._param_api()
    np.savez(HERE/'EFFECTIVE_MODEL.npz',bias=params.nodes.bias.numpy(force=True),time_const=params.nodes.time_const.numpy(force=True),
        weight=params.edges.weight.numpy(force=True),source=net.connectome.edges.source_index[:],target=net.connectome.edges.target_index[:])
    (HERE/'runs').mkdir();records=[];start=time.perf_counter()
    try:
        with torch.no_grad():
            for c,entry in zip(p['cases'],load('INPUT_MANIFEST.json')):
                if time.perf_counter()-start>300:raise TimeoutError('BOUNDED_CPU_CAP')
                f=HERE/'inputs'/(c['id']+'.npy');assert sha(f)==entry['input_sha256']
                pixels=np.load(f);movie=torch.from_numpy(pixels)[None,:,None,:]
                folder=HERE/'runs'/c['id'];folder.mkdir()
                ts=time.perf_counter();activity=net.simulate(movie,.005,initial_state=initial)
                neural_s=time.perf_counter()-ts
                assert activity.shape==(1,c['steps'],45669) and activity.dtype==torch.float32
                data=activity.numpy();assert np.isfinite(data).all() and np.array_equal(initial.nodes.activity.numpy()[0],initial_np)
                np.save(folder/'states.npy',data[0]);flow=np.empty((c['steps'],2,721),np.float32)
                td=time.perf_counter()
                for k in range(0,c['steps'],32):flow[k:k+32]=decoder(activity[:,k:k+32])[0].numpy()
                decoder_s=time.perf_counter()-td
                assert np.isfinite(flow).all()
                assert not any(m.training for m in decoder.modules())
                assert all(torch.equal(v,before[k]) for k,v in decoder.state_dict().items())
                np.save(folder/'flow.npy',flow)
                row=dict(id=c['id'],steps=c['steps'],neural_s=neural_s,decoder_s=decoder_s,full_state_sha256=sha(folder/'states.npy'),
                    flow_sha256=sha(folder/'flow.npy'),input_sha256=entry['input_sha256'],
                    own_old_state=True,output_t='(k+1)*.005; consumes input[k]',full_original_native_update=True)
                dump('runs/'+c['id']+'/RESULT.json',row);records.append(row)
                print('CASE_DONE',json.dumps(row),flush=True)
                del activity,data
        assert all(torch.equal(v.detach(),expected['network'][k]) for k,v in net.state_dict().items())
        assert not torch.cuda.is_initialized()
        dump('EXECUTION.json',dict(status='COMPLETE_REAL_CPU_INFERENCE',cases=records,neural_steps=sum(r['steps'] for r in records),decoder_frames=sum(r['steps'] for r in records),
            wall_s=time.perf_counter()-start,network_weights_unchanged=True,decoder_state_unchanged=True,
            GPU=False,board=False,precision='FP32',torch=torch.__version__,flyvis=flyvis.__version__,
            source_commit=subprocess.check_output(['git','-C',str(PROJECT/'fly/upstream/flyvis'),'rev-parse','HEAD'],text=True).strip()))
    except BaseException:
        dump('FAILURE.json',dict(error=traceback.format_exc(),completed_cases=records));raise

if __name__=='__main__':main()


