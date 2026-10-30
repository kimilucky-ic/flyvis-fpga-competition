"""Fixed CPU pilot: cached supervised training, fresh live Full/R/CNN rollouts."""
import argparse
import time
import uuid
import importlib.util
from common import *
from cnn import HexCNN,CNNService,restore
from decoder_cpu import CPUDecoder

class OriginalTargets:
    """Original expanded continuous equation, restricted to explicit targets.

    Used ONLY for Full references/Sham. Never passed to CNN engine.
    """
    def init__(self,p,targets):
        self.targets=torch.as_tensor(targets,dtype=torch.long)
        inverse=np.full(45669,-1,np.int64);inverse[targets]=np.arange(len(targets))
        selected=inverse[p['target_global']]>=0
        self.source=torch.from_numpy(p['source_global'][selected].copy())
        self.target=torch.from_numpy(inverse[p['target_global'][selected]].copy())
        self.weight=torch.from_numpy(p['effective_weight'][selected].copy())
        self.bias=torch.from_numpy(p['bias'][targets].copy())
        self.inv_tau=1/torch.maximum(torch.from_numpy(p['time_const'][targets].copy()),torch.tensor(.005))
        inputs=p['input_node_index'].reshape(-1);valid=inverse[inputs]>=0
        self.input_target=torch.from_numpy(inverse[inputs[valid]].copy())
        self.input_pixel=torch.from_numpy(np.tile(np.arange(721),8)[valid])
        self.calls=0

    @torch.no_grad()
    def step(self,old,pixels):
        chemical=torch.zeros(len(self.targets),dtype=torch.float32)
        chemical.scatter_add_(0,self.target,self.weight*torch.relu(old[self.source]))
        external=torch.zeros_like(chemical);external[self.input_target]=pixels[self.input_pixel]
        a=old[self.targets]
        self.calls+=1
        return a+(self.inv_tau*(((-a+self.bias)+chemical)+external))*.005

class ClosedLoop:
    """The production object owns only R-only and learned CNN services.

    There is no native-H updater, reference trajectory or teacher in this API.
    """
    def init__(self,r,cnn,initial,mapping,run_id):
        self.r=r;self.cnn=cnn;self.state=initial.clone();self.step_id=0
        self.h=torch.as_tensor(mapping['H_grid_ids'].reshape(-1));self.R=torch.as_tensor(mapping['R'])
        self.run_id=run_id;self.busy=False

    def step(self,pixels,step_id):
        if type(step_id)!=int or step_id!=self.step_id or self.busy:raise ValueError('STEP_ID_OR_REENTRANCY')
        if pixels.shape!=(721,) or pixels.dtype!=torch.float32 or not bool(torch.isfinite(pixels).all()):raise ValueError('PIXELS')
        old=self.state;before=digest(old);self.busy=True
        try:
            rr=self.r.step(old,pixels,step_id=step_id,run_id=self.run_id,condition_id='CNN')
            hh=self.cnn.step(old)
            if rr.step_id!=step_id or not torch.equal(rr.global_node_indices,self.R):raise ValueError('R_ORDER_OR_STEP')
            if hh.shape!=(5768,) or not bool(torch.isfinite(hh).all()):raise ValueError('H_SHAPE_OR_FINITE')
            candidate=torch.empty_like(old);candidate[self.h]=hh;candidate[self.R]=rr.activity
            if not bool(torch.isfinite(candidate).all()) or candidate.abs().max()>100:raise ValueError('NO_COMMIT_STABILITY_ENVELOPE')
            if digest(old)!=before:raise ValueError('OLD_STATE_MUTATED')
            # Single complete commit after both services and validation succeed.
            self.state=candidate;self.step_id+=1
            return candidate,dict(step=step_id,old=before,input=digest(pixels),new=digest(candidate),
                time=step_id*.005,next_time=(step_id+1)*.005,committed=True,
                old_source='OWN_LIVE_STATE',native_H_updates=0,R_targets=39901,H_CNN_outputs=5768)
        finally:self.busy=False

def train():
    check_frozen();start=time.perf_counter();torch.manual_seed(2026101604)
    rng=np.random.default_rng(2026101604);mapping=read_mapping();pr=load(HERE/'PREREGISTRATION.json')
    root=HERE/'training';root.mkdir()
    c=mapping['field_ids'].shape[0];x=np.empty((4*485,c,722),np.float32);x[:,:,-1]=0
    y=np.empty((4*485,8,721),np.float32);initial=np.load(BUNDLE/'initial_state_full.npy')
    ids=mapping['field_ids'];valid=ids>=0
    for ci,record in enumerate(pr['training']):
        path=Path(record['path']);assert sha(path)==record['sha256']
        state=np.load(path,mmap_mode='r')[0]
        old=np.concatenate([initial[None],state[:-1]],axis=0)
        x[ci*485:(ci+1)*485,:,:721]=old[:,np.maximum(ids,0)]*valid[None]
        y[ci*485:(ci+1)*485]=state[:,mapping['H_grid_ids']]-old[:,mapping['H_grid_ids']]
    np.save(root/'teacher_fields.npy',x);np.save(root/'target_delta.npy',y)
    model=HexCNN(c,mapping['offsets'],mapping['grid_uv'],mapping['h_channels'])
    with torch.no_grad():
        model.input_scale.copy_(torch.from_numpy(np.maximum(np.sqrt((np.maximum(x[:,:,:721],0).astype(np.float64)**2).mean((0,2))),.01).astype(np.float32)))
        model.h_scale.copy_(torch.from_numpy(np.maximum(np.sqrt((x[:,mapping['h_channels'],:721].astype(np.float64)**2).mean((0,2))),.01).astype(np.float32)))
        model.output_scale.copy_(torch.from_numpy(np.maximum(y.astype(np.float64).std((0,2)),.001).astype(np.float32)))
    xt=torch.from_numpy(x);yt=torch.from_numpy(y)
    neighbors=torch.as_tensor(np.where(mapping['neighbors']>=0,mapping['neighbors'],721))
    channels=torch.arange(c)[None,:,None];hc=torch.as_tensor(mapping['h_channels'])[None,:]
    opt=torch.optim.Adam(model.parameters(),lr=.005,weight_decay=1e-6)
    history=[]
    with (root/'optimizer_steps.jsonl').open('x',encoding='utf-8') as stream:
        for update in range(700):
            if time.perf_counter()-start>600:raise TimeoutError('TRAINING_BUDGET')
            if update==500:
                for group in opt.param_groups:group['lr']=.001
            ci=rng.integers(0,4,1024);k=np.where(rng.random(1024)<.25,rng.integers(0,200,1024),rng.integers(200,485,1024))
            f=torch.from_numpy(ci*485+k);pixel=torch.from_numpy(rng.integers(0,721,1024))
            patch=xt[f[:,None,None],channels,neighbors[pixel,None,:]]
            old_h=xt[f[:,None],hc,pixel[:,None]]
            target=yt[f[:,None],torch.arange(8)[None,:],pixel[:,None]]
            prediction=model.patch_delta(patch,old_h)
            loss=(((prediction-target)/model.output_scale)**2).mean()
            if not bool(torch.isfinite(loss)):raise FloatingPointError('TRAINING_LOSS_NONFINITE')
            opt.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),10);opt.step()
            rec=dict(update=update,loss=float(loss.detach()),wall_s=time.perf_counter()-start)
            stream.write(json.dumps(rec)+'\n');history.append(rec)
            if (update+1)%50==0:print(json.dumps(rec),flush=True)
    model.eval();torch.save(model.state_dict(),root/'cnn.pt')
    dump(root/'RESULT.json',dict(status='TRAINED_NOT_CLOSED_LOOP_ACCEPTED',updates=700,wall_s=time.perf_counter()-start,
        parameters=sum(p.numel() for p in model.parameters()),architecture='HexCNN-AR1',history=history,
        original_H_parameters_copied=False,training_neural_rollouts=0,training_source='four accepted GPU Full caches',GPU=0))
    dump(HERE/'MODEL_FREEZE.json',dict(sha256=sha(root/'cnn.pt'),time_ns=time.time_ns(),test_used=False,training_result_sha=sha(root/'RESULT.json')))

def bind_model():
    check_frozen();assert sha(HERE/'training/cnn.pt')==load(HERE/'MODEL_FREEZE.json')['sha256']
    mapping=read_mapping();model=restore(HERE/'training/cnn.pt',mapping)
    return mapping,model

def controls():
    mapping,model=bind_model();r=r_service();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    original_r_step=r.step;diagnostic_r_calls=[0]
    def counted_r_step(*args,**kwargs):
        value=original_r_step(*args,**kwargs);diagnostic_r_calls[0]+=1;return value
    r.step=counted_r_step
    pixels=torch.from_numpy(np.load(load(HERE/'TEST_CASES.json')[0]['path'])[0])
    results=[]
    for kind in ['wrong_step','NaN_input','duplicate_step','CNN_failure','CNN_NaN','CNN_wrong_shape','R_order']:
        engine=ClosedLoop(r,CNNService(model,mapping),initial,mapping,'fault-'+kind)
        if kind=='duplicate_step':engine.step(pixels,0)
        old=engine.state.clone();old_step=engine.step_id
        if kind=='CNN_failure':
            def fail(x):raise RuntimeError('injected CNN failure')
            engine.cnn.step=fail
        if kind=='CNN_NaN':engine.cnn.step=lambda x:torch.full((5768,),float('nan'))
        if kind=='CNN_wrong_shape':engine.cnn.step=lambda x:torch.zeros(8)
        if kind=='R_order':engine.R=engine.R.flip(0)
        supplied=pixels.clone()
        if kind=='NaN_input':supplied[0]=float('nan')
        try:engine.step(supplied,99 if kind=='wrong_step' else 0)
        except (ValueError,RuntimeError) as exc:failure=repr(exc)
        else:raise AssertionError('FAULT_ACCEPTED '+kind)
        assert engine.step_id==old_step and torch.equal(engine.state,old)
        results.append(dict(fault=kind,rejected=True,state_unchanged=True,no_R_only_commit=True,error=failure))
    # Concrete learned/live bidirectional path, not Full trajectory replay.
    types,u,v,p=source();src=p['source_global'];dst=p['target_global'];w=p['effective_weight']
    Hmask=np.isin(np.arange(45669),mapping['H']);Rmask=~Hmask
    hr=np.flatnonzero(Hmask[src]&Rmask[dst]&(w!=0));rh=np.flatnonzero(Rmask[src]&Hmask[dst]&(w!=0))
    mids=np.intersect1d(dst[hr],src[rh]);assert len(mids)>0
    # Choose largest nonzero outgoing edge on a real return path, before any test score.
    options=hr[np.isin(dst[hr],mids)&(initial[dst[hr]].numpy()>.1)]
    assert len(options)>0
    ei=options[np.argmax(abs(w[options]))];hnode=int(src[ei]);rnode=int(dst[ei])
    changed=initial.clone();changed[hnode]=torch.maximum(changed[hnode],torch.tensor(.05))+.1
    a=r.step(initial,pixels,step_id=0,run_id='feedback',condition_id='base').activity
    b=r.step(changed,pixels,step_id=0,run_id='feedback',condition_id='H_perturbed').activity
    live_a=initial.clone();live_b=initial.clone();live_a[mapping['R']]=a;live_b[mapping['R']]=b
    cnn=CNNService(model,mapping);h_difference=float(abs(cnn.step(live_b)-cnn.step(live_a)).max())
    # Independent R perturbation of the identified live upstream neuron.
    rp=initial.clone();rp[rnode]+=.1;rh_difference=float(abs(cnn.step(rp)-cnn.step(initial)).max())
    feedback=dict(H_global_id=hnode,R_global_id=rnode,H_R_original_edge=int(ei),
        H_perturb_changes_R=float(abs(b-a).max()),R_perturb_changes_CNN_H=rh_difference,
        H_to_R_to_CNN_H_max_difference=h_difference,original_H_updates=0,
        all_bidirectional_nonzero=bool(float(abs(b-a).max())>0 and rh_difference>0 and h_difference>0))
    status='PASS_TRANSACTION_AND_LIVE_FEEDBACK' if feedback['all_bidirectional_nonzero'] else 'PASS_TRANSACTION_FEEDBACK_NOT_DEMONSTRATED'
    dump(HERE/'FAULT_AND_FEEDBACK.json',dict(status=status,faults=results,feedback=feedback,
        new_R_only_steps=diagnostic_r_calls[0],new_CNN_calls='diagnostic only; separate from science rollout',GPU=0))
    print(status,feedback)

def run():
    mapping,model=bind_model();start=time.perf_counter();decoder=CPUDecoder()
    _,_,_,p=source();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    full=OriginalTargets(p,np.arange(45669));exactH=OriginalTargets(p,mapping['H']);r=r_service()
    root=HERE/'runs';root.mkdir();results=[];case_list=load(HERE/'TEST_CASES.json')
    # CPU/source calibration on a short accepted original stimulus, no training.
    cached=LANE/'t4t5_confirm_20261011/artifacts/gpu_r1/ON60/Full'
    stimulus=np.load(LANE/'t4t5_criticality_20261011/cpu_preparation_r1/ON60_stimulus.npy')[0,:32,0]
    ref=np.load(cached/'activities_full.npy',mmap_mode='r')[0,:32]
    state=initial.clone();maxerr=0
    for k in range(32):
        state=full.step(state,torch.from_numpy(stimulus[k]))
        maxerr=max(maxerr,float(abs(state.numpy()-ref[k]).max()))
        assert np.allclose(state.numpy(),ref[k],atol=1e-5,rtol=1e-5)
    dump(HERE/'SOURCE_CPU_CALIBRATION.json',dict(status='PASS',steps=32,all45669_compared=True,max_abs=maxerr,actual_CPU=True))
    for case in case_list:
        assert sha(case['path'])==case['sha256']
        frames=torch.from_numpy(np.load(case['path']));modes=['Full','CNN']
        if case['group']=='base':modes.append('HOLD')
        if case==case_list[0]:modes.insert(1,'Sham')
        for mode in modes:
            before=time.perf_counter();folder=root/case['id']/mode;folder.mkdir(parents=True)
            states=np.lib.format.open_memmap(folder/'states.npy',mode='w+',dtype=np.float32,shape=(485,45669))
            state=initial.clone();count=0;failure=None;max_abs=0.;native_before=exactH.calls;full_before=full.calls
            cnn=CNNService(model,mapping)
            engine=ClosedLoop(r,cnn,initial,mapping,str(uuid.uuid4())) if mode=='CNN' else None
            with (folder/'steps.jsonl').open('x',encoding='utf-8') as log:
                for k in range(485):
                    if time.perf_counter()-start>900:raise TimeoutError('ROLLOUT_BUDGET')
                    if mode=='CNN':
                        try:state,record=engine.step(frames[k],k)
                        except (ValueError,RuntimeError) as exc:
                            failure=dict(step=k,error=repr(exc),committed_steps=engine.step_id,no_fallback=True);break
                    else:
                        old=state;old_hash=digest(old)
                        if mode=='Full':state=full.step(old,frames[k])
                        else:
                            rr=r.step(old,frames[k],step_id=k,run_id='control',condition_id=case['id'])
                            hh=exactH.step(old,frames[k]) if mode=='Sham' else initial[mapping['H']]
                            state=torch.empty_like(old);state[mapping['R']]=rr.activity;state[mapping['H']]=hh
                        if not torch.isfinite(state).all():raise FloatingPointError('REFERENCE_NONFINITE')
                        record=dict(step=k,old=old_hash,input=digest(frames[k]),new=digest(state),
                            time=k*.005,next_time=(k+1)*.005,committed=True,mode=mode)
                    max_abs=max(max_abs,float(abs(state).max()));states[k]=state.numpy();count+=1
                    log.write(json.dumps(record)+'\n')
            states.flush()
            if mode=='CNN':assert exactH.calls==native_before and full.calls==full_before and count<=cnn.calls<=count+1
            if mode=='Sham':
                reference=np.load(root/case['id']/'Full/states.npy',mmap_mode='r')
                assert np.allclose(states,reference,atol=1e-5,rtol=1e-5)
            # No future/teacher state is passed to CNN; decode only committed states.
            flow=decoder.decode(np.asarray(states[:count])) if count else np.empty((0,2,721),np.float32)
            np.save(folder/'flow.npy',flow);np.save(folder/'final_state.npy',state.numpy())
            rec=dict(case=case['id'],mode=mode,complete=count==485,steps=count,failure=failure,max_abs=max_abs,
                wall_s=time.perf_counter()-before,original_H_updates=(full.calls-full_before)+(exactH.calls-native_before),
                CNN_calls=cnn.calls if mode=='CNN' else 0,CNN_truth_corrections=0,actual_CPU=True,decoder_frames=count)
            dump(folder/'RESULT.json',rec);results.append(rec)
            print(json.dumps(rec),flush=True)
    decoder.assert_unchanged()
    dump(HERE/'EXECUTION.json',dict(status='COMPLETE_BOUNDED_PILOT',results=results,wall_s=time.perf_counter()-start,
        neural_steps=sum(r['steps'] for r in results)+32,decoder_frames=sum(r['decoder_frames'] for r in results),
        GPU=0,board=0,official_decoder_unchanged=True,torch=torch.__version__,device='cpu'))

def analyze():
    check_frozen();execution=load(HERE/'EXECUTION.json');mapping=read_mapping()
    roi=np.load(LANE/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy')
    spec=importlib.util.spec_from_file_location('frozenmetrics',LANE/'t4t5_criticality_20261011/metrics.py')
    metric=importlib.util.module_from_spec(spec);spec.loader.exec_module(metric)
    records=[];overall=True;one_step=[]
    model=restore(HERE/'training/cnn.pt',mapping);service=CNNService(model,mapping)
    for case in load(HERE/'TEST_CASES.json'):
        root=HERE/'runs'/case['id'];ref=np.load(root/'Full/states.npy',mmap_mode='r');flow=np.load(root/'Full/flow.npy')
        # Teacher-forced single-step error is scored OFFLINE after closed loop;
        # it is never used to repair this run or select/modify the checkpoint.
        sq=0.;num=0
        old=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
        for k in range(485):
            y=service.step(old).numpy();target=ref[k,mapping['H']]
            sq+=float(np.sum((y.astype(np.float64)-target)**2));num+=5768
            old=torch.from_numpy(np.array(ref[k],copy=True))
        one_step.append(dict(case=case['id'],RMSE=float(np.sqrt(sq/num)),teacher_forced=True,posthoc_only=True))
        for mode in ['Sham','CNN','HOLD']:
            folder=root/mode
            if not folder.exists():continue
            result=load(folder/'RESULT.json');n=result['steps']
            state=np.load(folder/'states.npy',mmap_mode='r')[:n];delta=state.astype(np.float64)-ref[:n].astype(np.float64)
            perstep=[]
            for k in range(n):
                row=dict(step=k,H_RMSE=float(np.sqrt(np.mean(delta[k,mapping['H']]**2))),
                    R_RMSE=float(np.sqrt(np.mean(delta[k,mapping['R']]**2))),
                    H_max=float(abs(delta[k,mapping['H']]).max()),R_max=float(abs(delta[k,mapping['R']]).max()))
                perstep.append(row)
            dump(folder/'STEP_ERRORS.json',perstep)
            full_errors=dict(final_max=float(abs(delta[-1]).max()) if n else None,
                H_all_RMSE=float(np.sqrt(np.mean(delta[:,mapping['H']]**2))) if n else None,
                R_all_RMSE=float(np.sqrt(np.mean(delta[:,mapping['R']]**2))) if n else None)
            rec=dict(case=case['id'],mode=mode,complete=result['complete'],neural=full_errors,
                source_group=case['group'],direction=case['angle'],polarity=case['polarity'])
            if n==485:
                h=np.array(state[:,mapping['H']]).astype(np.float64).reshape(485,8,721)
                href=np.array(ref[:,mapping['H']]).astype(np.float64).reshape(485,8,721)
                baseline=href[160:200].mean(0);hr=href[200:]-baseline;hv=h[200:]-baseline
                h_rel=float(np.linalg.norm(hv-hr)/max(np.linalg.norm(hr),1e-12))
                subtype={t:dict(relative_L2=float(np.linalg.norm(hv[:,i]-hr[:,i])/max(np.linalg.norm(hr[:,i]),1e-12)),
                    RMSE=float(np.sqrt(np.mean((h[:,i]-href[:,i])**2)))) for i,t in enumerate(TYPES)}
                value=np.load(folder/'flow.npy')
                fmetrics={name:metric.vector_metrics(flow,value,roi,window=window) for name,window in [('primary',slice(200,286)),('allpost',slice(200,485))]}
                passed=bool(h_rel<=.2 and all(m['reference_eligible'] and m['field_error_E']<=.2 and .8<=m['magnitude_ratio']<=1.2 and m['angle_deg'] is not None and m['angle_deg']<=15 for m in fmetrics.values()))
                rec.update(H_response_relative_L2=h_rel,subtype=subtype,flow=fmetrics,gate_pass=passed)
            else:rec.update(gate_pass=False,reason='INCOMPLETE_NO_PADDING_OR_FALLBACK')
            if mode=='CNN':overall=overall and rec['gate_pass']
            records.append(rec)
    dump(HERE/'ONE_STEP_ONLY_DIAGNOSTIC.json',one_step)
    dump(HERE/'RESULTS.json',dict(status='FUNCTIONAL_PASS' if overall else 'FUNCTIONAL_NOT_PASS',
        execution='ACTUAL_CPU_CLOSED_LOOP',primary_all8_pass=overall,records=records,
        limitations='Eight controlled cases, four cached train movies, one learned convolution; no biological equivalence, natural-video accuracy, FPGA or optimal-architecture claim'))
    print(json.dumps([dict(case=r['case'],mode=r['mode'],complete=r['complete'],H=r.get('H_response_relative_L2'),
        E=None if 'flow' not in r else r['flow']['allpost']['field_error_E'],pass_gate=r['gate_pass']) for r in records]),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['train','controls','run','analyze']);args=ap.parse_args()
    try:globals()[args.stage]()
    except BaseException as exc:
        dump(HERE/f'FAILURE_{args.stage}_{time.time_ns()}.json',dict(error=repr(exc),retry=False));raise
