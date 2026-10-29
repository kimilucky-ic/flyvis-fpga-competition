"""Single shared-lease CUDA worker; no GPU import before resource admission."""
from contract import *
import sys,base64,select,traceback

def emit(event,**values):print('FV4 '+json.dumps(dict(event=event,**values),separators=(',',':')),flush=True)

def main():
    started=time.monotonic();p=check();a={k:path(v) for k,v in p['assets'].items()};run=p['run_id']
    runner=imported('line4_shared_lease',a['runner_lease'])
    class SessionLease(runner.Lease):
        def init__(self):
            self.job=HERE/'gpu';self.job.mkdir(exist_ok=True)
            self.config=dict(campaign_id='LINE4_STREAM_'+run,stage='FULL_AND_CNN_GPU_VISUAL',queue_s=15)
            self.ticket=dict(config=self.config,identity_key=sha(HERE/'PLAN.json'),job_dir=str(self.job),scope='one user-requested visual GPU experiment')
        def check(self,phase='check'):
            if time.monotonic()-started>300:raise TimeoutError('GPU_SCOPE_DEADLINE')
            if (HERE/'STOP.json').exists():raise RuntimeError('USER_OR_HOST_STOP')
            if runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists():raise RuntimeError('SHARED_RESOURCE_QUARANTINE')
    lease=SessionLease();handle=None;torch=None;success=False
    try:
        emit('STAGE',text='等待共享GPU锁');handle,queued=lease.acquire()
        write(HERE/'gpu/LEASE.json',dict(run_id=run,queue_s=queued,pid=os.getpid(),shared_lock=str(runner.own_path('runtime','gpu.lock'))))
        scratch=Path('/tmp')/('flyvis-line4-stream-'+run);scratch.mkdir()
        os.environ.update(CUDA_VISIBLE_DEVICES='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='1',
            MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',
            FLYVIS_ROOT_DIR='/opt/flyvis-gpu-data',TMPDIR=str(scratch))
        emit('STAGE',text='加载CUDA与原始模型')
        import numpy as np
        import torch as t
        torch=t;torch.set_num_threads(1);assert torch.cuda.is_available()
        torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
        torch.cuda.set_device(0);assert float((torch.ones(4,device='cuda')*2).sum().item())==8
        full_module=imported('line4_original_full',a['full'])
        oracle=full_module.FullNetworkOracle(a['identity'],model_path=p['runtime']['model_path'],device='cuda')
        rmod=imported('line4_original_R',a['r_only'])
        r=rmod.RStepService(a['parameters'],a['identity'],a['R_manifest'],device='cuda')
        cmod=imported('line4_frozen_CNN',a['CNN_source']);m=dict(np.load(a['mapping']))
        model=cmod.HexCNN(23,m['offsets'],m['grid_uv'],m['h_channels']).to('cuda')
        expected=torch.load(a['CNN_weights'],map_location='cpu',weights_only=True)
        model.load_state_dict(expected);model.eval();assert sum(v.numel() for v in model.parameters())==31168
        H=torch.as_tensor(m['H_grid_ids'].reshape(-1),device='cuda');R=torch.as_tensor(m['R'],device='cuda')
        assert torch.equal(r._r,R) and np.array_equal(r.h_indices,m['H'])
        field=torch.as_tensor(np.maximum(m['field_ids'],0),device='cuda');valid=torch.as_tensor(m['field_ids']>=0,device='cuda')
        emit('STAGE',text='加载官方光流解码器')
        decoder=imported('line4_official_decoder',a['decoder']).OfficialDecoderService(p['runtime']['model_path'],a['decoder_contract'],device='cuda',check_scope=lease.check)
        initial=np.load(a['initial']);sf=torch.as_tensor(initial.copy(),device='cuda');sc=sf.clone()
        state_f=np.lib.format.open_memmap(HERE/'gpu/Full_states.npy',mode='w+',dtype=np.float32,shape=(1000,45669))
        state_c=np.lib.format.open_memmap(HERE/'gpu/CNN_states.npy',mode='w+',dtype=np.float32,shape=(1000,45669))
        inputs=np.lib.format.open_memmap(HERE/'gpu/inputs.npy',mode='w+',dtype=np.float32,shape=(1000,721))
        digest=lambda value:hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()
        prev_f=prev_c=digest(initial);guard_calls=0;full_calls=cnn_calls=0;flows_f=[];flows_c=[];flow_steps=[]
        original=[(oracle,'step',oracle.step),(oracle.net,'_next_state',oracle.net._next_state),
                  (oracle.net.dynamics,'write_state_velocity',oracle.net.dynamics.write_state_velocity)]
        def forbidden(*args,**kwargs):
            nonlocal guard_calls
            guard_calls+=1;raise RuntimeError('NATIVE_H_FORBIDDEN_IN_CNN')
        emit('READY',device=torch.cuda.get_device_name(0),torch=torch.__version__,parameters=31168,
             preload_s=time.monotonic()-started,FPGA=False,run_id=run)
        def read():
            while not select.select([sys.stdin],[],[],.2)[0]:lease.check('wait_input')
            line=sys.stdin.readline()
            if not line:raise EOFError('HOST_DISCONNECTED')
            packet=json.loads(line);assert packet['run_id']==run
            return packet
        assert read()['op']=='START';active=time.monotonic()
        with (HERE/'gpu/chain.jsonl').open('x',encoding='utf-8') as chain,torch.no_grad():
            for j in range(500):
                lease.check('frame');packet=read();assert packet['op']=='FRAME' and packet['frame_id']==j
                values=np.frombuffer(base64.b64decode(packet['pixels_b64']),dtype=np.float32).copy()
                assert values.shape==(721,) and np.isfinite(values).all() and values.min()>=0 and values.max()<=1
                assert digest(values)==packet['input_sha'];pixels=torch.as_tensor(values,device='cuda')
                for repeat in range(2):
                    k=2*j+repeat;vf,vc=sf._version,sc._version
                    nf=oracle.step(sf,pixels);full_calls+=1
                    try:
                        for obj,name,_ in original:setattr(obj,name,forbidden)
                        rr=r.step(sc,pixels,step_id=k,run_id=run,condition_id='MP4_ON75')
                        hh=model((sc[field]*valid)[None])[0].reshape(-1);cnn_calls+=1
                        assert rr.step_id==k and torch.equal(rr.global_node_indices,R)
                        nc=torch.empty_like(sc);nc[H]=hh;nc[R]=rr.activity
                    finally:
                        for obj,name,method in original:setattr(obj,name,method)
                    assert sf._version==vf and sc._version==vc
                    assert torch.isfinite(nf).all() and torch.isfinite(nc).all() and max(float(nf.abs().max()),float(nc.abs().max()))<=100
                    sf,sc=nf,nc;cf=sf.cpu().numpy();cc=sc.cpu().numpy()
                    state_f[k]=cf;state_c[k]=cc;inputs[k]=values
                    new_f,new_c=digest(cf),digest(cc)
                    chain.write(json.dumps(dict(step=k,frame_id=j,input_sha=digest(values),old_Full=prev_f,new_Full=new_f,
                        old_CNN=prev_c,new_CNN=new_c,time=k*.005,next_time=(k+1)*.005,native_H_in_CNN=0,old_source='OWN_LIVE_STATE'))+'\n')
                    prev_f,prev_c=new_f,new_c
                message=dict(frame_id=j,steps=2*j+2,Full_hash=prev_f,CNN_hash=prev_c)
                if (j+1)%5==0:
                    ff=decoder.decode(cf[None,None],chunk_frames=1)[0,0]
                    fc=decoder.decode(cc[None,None],chunk_frames=1)[0,0]
                    flows_f.append(ff);flows_c.append(fc);flow_steps.append(2*j+1)
                    message.update(flow_Full=ff.tolist(),flow_CNN=fc.tolist(),
                        H_mean_Full=cf[m['H_grid_ids']].mean(1).tolist(),H_mean_CNN=cc[m['H_grid_ids']].mean(1).tolist())
                emit('COMMIT',**message)
        torch.cuda.synchronize();oracle.assert_weights_unchanged();decoder.assert_weights_unchanged()
        assert guard_calls==0 and all(torch.equal(v.cpu(),expected[k]) for k,v in model.state_dict().items())
        state_f.flush();state_c.flush();inputs.flush()
        np.save(HERE/'gpu/Full_flow.npy',np.array(flows_f));np.save(HERE/'gpu/CNN_flow.npy',np.array(flows_c));np.save(HERE/'gpu/flow_steps.npy',flow_steps)
        result=dict(status='ACTUAL_FULL_AND_CNN_CUDA_STREAM_COMPLETE',run_id=run,steps_each=1000,source_frames=500,
            Full_calls=full_calls,CNN_calls=cnn_calls,native_H_in_CNN=guard_calls,teacher_corrections=0,
            decoder_frames_each=len(flow_steps),stream_wall_s=time.monotonic()-active,total_worker_s=time.monotonic()-started,
            GPU=torch.cuda.get_device_name(0),torch=torch.__version__,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
            peak_reserved_bytes=torch.cuda.max_memory_reserved(),model_and_decoder_unchanged=True,FPGA=False)
        write(HERE/'gpu/RESULT.json',result);success=True;emit('COMPLETE',**result)
    except BaseException as exc:
        write(HERE/'gpu/FAILURE.json',dict(error=repr(exc),traceback=traceback.format_exc(),retry=False));emit('ERROR',error=repr(exc));raise
    finally:
        synchronized=False
        if torch is not None and torch.cuda.is_initialized():torch.cuda.synchronize();synchronized=True
        if handle is not None:handle.close()
        write(HERE/'gpu/EXIT.json',dict(success=success,CUDA_synchronized=synchronized,lease_closed=handle is not None,pid=os.getpid()))

if __name__=='__main__':main()
