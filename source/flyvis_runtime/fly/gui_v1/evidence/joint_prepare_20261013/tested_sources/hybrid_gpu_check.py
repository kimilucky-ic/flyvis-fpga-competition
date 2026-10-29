"""Three-step software GPU preflight; no Client, board request, GUI or video.

Full.step is used only as an independent R/float32 comparison. Production-side
H integration is prohibited. Scalar Q24 reference is explicitly SOFTWARE_ONLY.
"""
import argparse,json,os,subprocess,time,uuid
from datetime import datetime,timezone,timedelta
from pathlib import Path
import numpy as np
from live_protocol import HERE,Registry,canonical,host_path,load,require,sha,utc,write
from live_worker import import_file
from hybrid_v2 import V2Contract
from realtime_timing import Timings


def worker(root):
    root=host_path(root).resolve();scope=load(root/'scope.json');reg=Registry();c=V2Contract()
    require(root.parent==HERE/'runtime/hybrid_software_checks','OUTPUT_SCOPE')
    require(scope['kind']=='GPU_SOFTWARE_PREFLIGHT_ONLY' and scope['steps']==3 and scope['board_enabled'] is False,'SCOPE')
    require(scope['source_sha256']=={p:sha(HERE/p) for p in scope['source_sha256']},'ADAPTER_CHANGED')
    runner=import_file('gui_existing_hybrid_lease',reg.path_for('runner_lease'))
    class ShortLease(runner.Lease):
        def init__(self):
            self.job=root;self.config={'campaign_id':scope['run_id'],'stage':'HYBRID_GPU_SOFTWARE_3','queue_s':10}
            self.ticket={'config':self.config,'identity_key':canonical(scope),'job_dir':str(root),'scope':'3 software GPU steps; no board'}
        def check(self,phase='check'):
            require(datetime.now(timezone.utc)<datetime.fromisoformat(scope['end_utc']),'DEADLINE')
            require(not (root/'STOP_REQUEST.json').exists(),'STOP_REQUESTED')
            require(not runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists(),'RESOURCE_QUARANTINE')
    lease=ShortLease();handle=None;torch=None;start=time.perf_counter();rows=[];result=None
    try:
        handle,queue_s=lease.acquire();lease.check('before_import')
        scratch=Path('/tmp')/('hybrid-gpu-'+scope['run_id']);scratch.mkdir()
        os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR=str(scratch/'flyvis'),
            MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'mpl'),NUMBA_CACHE_DIR=str(scratch/'numba'))
        import torch as t
        torch=t;torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        require(torch.cuda.is_available(),'CUDA_REQUIRED_NO_FALLBACK')
        probe=torch.tensor([1.],device='cuda');require(probe.add(1).item()==2,'CUDA_TENSOR_PROBE')
        Full=import_file('gui_hybrid_reference_full',reg.path_for('full')).FullNetworkOracle
        oracle=Full(reg.path_for('identity'),model_path=reg.data['runtime']['model_path'],device='cuda')
        Decode=import_file('gui_hybrid_official_decoder',reg.path_for('decoder')).OfficialDecoderService
        decoder=Decode(reg.data['runtime']['model_path'],reg.path_for('decoder_contract'),device='cuda',check_scope=lease.check)
        from hybrid_gpu import GPUCandidates
        timing=Timings();producer=GPUCandidates(reg,c,oracle,torch,timing)
        a,old_words,raw=c.initial();np.save(root/'initial_mixed.npy',a);np.save(root/'initial_full_reference.npy',raw)
        frames=np.array(reg.input('ON60')[0,200:203,0],copy=True);np.save(root/'stimulus_721.npy',frames)
        arrays=dict(np.load(reg.path_for('parameters'),allow_pickle=False));mask=np.isin(arrays['target_global'],c.h)
        local=np.full(45669,-1,dtype=np.int64);local[c.h]=np.arange(5768)
        src=arrays['source_global'][mask];dst=local[arrays['target_global'][mask]];weight=arrays['effective_weight'][mask]
        states=[];flows=[];reference_flows=[];previous_H=None
        state=torch.as_tensor(a.copy(),device='cuda');reference=torch.as_tensor(a.copy(),device='cuda')
        for j,k in enumerate(range(200,203)):
            lease.check('step');step_start=time.perf_counter();old=a.copy();frame=torch.as_tensor(frames[j].copy(),device='cuda')
            output=producer.produce(state,frame,run_id=scope['run_id'],step_id=k)
            independent=np.zeros(5768,dtype=np.float32);np.add.at(independent,dst,weight*np.maximum(old[src],np.float32(0)))
            require(np.allclose(output['chemical_H'],independent,atol=1e-5,rtol=1e-5),'ORIGINAL_CHEMICAL_COMPARISON')
            # The independent Full reference cannot supply a hybrid H candidate.
            full_same_old=oracle.step(state,frame).detach().cpu().numpy()
            require(np.allclose(output['new_R'],full_same_old[c.r],atol=1e-5,rtol=1e-5),'R_ONLY_REFERENCE')
            payload=old_words+c.wire.encode_activity(output['chemical_H'])+c.wire.encode_activity(output['x_full'][c.h])
            software_words,_=c.expected_H(payload)
            row=dict(step_id=k,execution_kind='GPU_R_PLUS_SOFTWARE_Q24_REFERENCE',PL_execution=False,
                old_full_sha256=__import__('hashlib').sha256(old.tobytes()).hexdigest(),
                old_H_sha256=c.wire.digest(old_words).hex(),payload_sha256=c.wire.digest(payload).hex(),
                chemical_vs_CPU_max_abs=float(np.max(np.abs(output['chemical_H']-independent))),
                R_vs_original_Full_max_abs=float(np.max(np.abs(output['new_R']-full_same_old[c.r]))),native_H_production_updates=0)
            if previous_H is not None:
                counter=old.copy();counter[c.h]=previous_H
                rr=producer.r.step(torch.as_tensor(counter,device='cuda'),frame,step_id=k,run_id=scope['run_id'],condition_id='ON60')
                row['software_feedback_counterfactual_R_max_abs']=float(np.max(np.abs(rr.activity.cpu().numpy()-output['new_R'])))
                row['feedback_test_kind']='SOFTWARE_REFERENCE_ONLY_NOT_PL_PROOF'
            previous_H=old[c.h].copy()
            a=np.empty(45669,dtype=np.float32);a[c.h]=c.decode(software_words);a[c.r]=output['new_R']
            old_words=software_words;state=torch.as_tensor(a.copy(),device='cuda')
            reference=oracle.step(reference,frame)
            with timing.measure('official_decoder_mixed_and_Full_reference'):
                flow=decoder.decode(a[None,None],chunk_frames=1)[0,0]
                ref_flow=decoder.decode(reference.detach().cpu().numpy()[None,None],chunk_frames=1)[0,0]
            row.update(Full_trajectory_max_abs=float(np.max(np.abs(a-reference.cpu().numpy()))),
                Full_flow_max_abs=float(np.max(np.abs(flow-ref_flow))),elapsed_s=time.perf_counter()-step_start)
            states.append(a.copy());flows.append(flow);reference_flows.append(ref_flow);rows.append(row)
            np.savez(root/f'candidates_{k}.npz',old_full=old,**output)
            (root/f'software_reference_request_{k}.bin').write_bytes(payload)
            (root/f'software_reference_H_{k}.bin').write_bytes(software_words)
            write(root/'progress.json',{'completed':len(rows),'rows':rows,'PL_execution':False})
        producer.check_unchanged();decoder.assert_weights_unchanged();torch.cuda.synchronize();reg.unchanged();c.unchanged()
        np.save(root/'software_mixed_states.npy',np.array(states));np.save(root/'official_flow.npy',np.array(flows));np.save(root/'Full_reference_flow.npy',np.array(reference_flows))
        result=dict(status='PASS_GPU_SOFTWARE_PREFLIGHT_ONLY',run_id=scope['run_id'],rows=rows,steps=3,
            candidate_source='CURRENT_GPU_ORIGINAL_CHEMICAL_AND_ORIGINAL_R_ONLY',H_source='CPU_SCALAR_Q24_REFERENCE_NOT_PL',
            official_decoder_frames=6,device=torch.cuda.get_device_name(),torch_version=torch.__version__,
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),queue_s=queue_s,total_s=time.perf_counter()-start,
            model=reg.data['model'],input_sha256=reg.pins['stimulus_ON60']['sha256'],tolerance=c.tolerance,
            PL_execution=False,board_operations=0,GUI_launches=0,FPGA_closed_loop='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN',timing=timing.summary())
        write(root/'result.json',result)
    except BaseException as exc:
        write(root/'result.json',dict(status='FAILED_GPU_SOFTWARE_PREFLIGHT',error=repr(exc),completed=len(rows),rows=rows,PL_execution=False,board_operations=0));raise
    finally:
        if torch is not None and torch.cuda.is_available():torch.cuda.synchronize()
        if handle is not None:handle.close()
        write(root/'exit.json',dict(utc=utc(),GPU_inflight_waited=torch is not None,lease_closed=handle is not None,board_operations=0))
        files={str(p.relative_to(root)):sha(p) for p in root.iterdir() if p.is_file() and p.name not in ('worker.log','manifest.json')}
        write(root/'manifest.json',{'files':files,'evidence_level':'SOFTWARE_GPU_PREFLIGHT_ONLY'})


def launch():
    require(os.name=='nt','WINDOWS_ENTRY');c=V2Contract();reg=Registry();c.initial();reg.input('ON60')
    rid=uuid.uuid4().hex;root=HERE/'runtime/hybrid_software_checks'/rid;root.mkdir(parents=True)
    now=datetime.now(timezone.utc)
    spec=dict(kind='GPU_SOFTWARE_PREFLIGHT_ONLY',run_id=rid,steps=3,start_step=200,board_enabled=False,
        authorization_reference='2026-10-13 user requested GPU coordinator preparation and short joint experiment; software preflight only',
        start_utc=now.isoformat(),end_utc=(now+timedelta(seconds=180)).isoformat(),
        source_sha256={n:sha(HERE/n) for n in ['hybrid_gpu_check.py','hybrid_gpu.py','hybrid_v2.py','hybrid_joint_registry.json']})
    write(root/'scope.json',spec)
    def linux(p):return '/mnt/'+str(p)[0].lower()+'/'+str(p)[3:].replace('\\','/')
    print(str(root),flush=True)
    with (root/'worker.log').open('xb') as log:
        proc=subprocess.Popen(['wsl.exe','-d','FlyVisCPU','--exec',reg.data['runtime']['python'],'-B','-u',linux(Path(__file__)),'--worker',linux(root)],
            stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while proc.poll() is None:time.sleep(.5)
        except BaseException:
            write(root/'STOP_REQUEST.json',{'reason':'CONTROLLER_STOP','utc':utc()});proc.wait(timeout=30);raise
    require(proc.returncode==0,'SOFTWARE_GPU_CHECK_FAILED '+str(root));print(json.dumps(load(root/'result.json')))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run-gpu',action='store_true');ap.add_argument('--worker');a=ap.parse_args()
    if a.worker:worker(a.worker)
    elif a.run_gpu:launch()
    else:print(json.dumps(V2Contract().readiness(),indent=2))
