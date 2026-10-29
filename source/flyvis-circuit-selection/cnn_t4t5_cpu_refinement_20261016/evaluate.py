"""New holdout opens only after same-model single-step+short-loop gates PASS."""
import importlib.util
from shared import *

def generate_inputs():
    m=mapping();p=freezecheck();raw=np.load(p['stimulus_source'],mmap_mode='r')
    assert raw.shape==(24,485,1,721)
    uv=m['grid_uv'];lookup={(int(a),int(b)):i for i,(a,b) in enumerate(uv.T)}
    x=np.sqrt(3)/2*uv[1];y=-(uv[0]+uv[1]/2);records=[]
    for case in load(HERE/'TEST_PLAN.json'):
        value=np.array(raw[case['original_sample'],:,0],copy=True);kind=case['variant']
        if kind=='speed_075':value[200:]=value[200+np.floor(np.arange(285)*.75).astype(int)]
        if kind=='shift_v_minus3':
            source=np.array([lookup.get((int(a),int(b+3)),-1) for a,b in uv.T]);shifted=np.full_like(value,0 if case['polarity']=='ON' else 1)
            shifted[:,source>=0]=value[:,source[source>=0]];value=shifted
        if kind.startswith('local_'):
            cx=-5 if kind=='local_left' else 5
            aperture=.5*(1+np.tanh(3*(5-np.sqrt((x-cx)**2+y*y))))
            value=(.5+aperture[None]*(value-.5)).astype(np.float32)
        path=HERE/'inputs'/(case['id']+'.npy');path.parent.mkdir(exist_ok=True)
        np.save(path,value);records.append(dict(**case,path=str(path),sha256=sha(path)))
    dump(HERE/'TEST_INPUTS.json',records);return records

def run():
    freezecheck();gate=load(HERE/'TRAINING_GATE.json')
    if not gate['pass_gate']:
        dump(HERE/'HOLDOUT_NOT_RUN.json',dict(reason='TRAINING_GATES_NOT_PASS',new_test_neural_steps=0,holdout_inputs_opened=False));return
    identity=load(HERE/'MODEL_FREEZE.json');assert sha(identity['path'])==identity['sha256']
    assert sha(HERE/'TRAINING_GATE.json')==identity['gate_sha']
    cases=generate_inputs();start=time.perf_counter();m=mapping();model=model_from(identity['path'])
    _,_,_,p=source();full=OriginalTargets(p,np.arange(45669));exactH=OriginalTargets(p,m['H']);r=r_service();decoder=CPUDecoder()
    initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'));records=[]
    for ci,case in enumerate(cases):
        pixels=torch.from_numpy(np.load(case['path']));modes=['Full','CNN']+(['Sham'] if ci==0 else [])
        for mode in modes:
            tick=time.perf_counter();out=HERE/'test_runs'/case['id']/mode;out.mkdir(parents=True)
            state=initial.clone();cnn=CNNService(model,m)
            engine=ClosedLoop(r,cnn,initial,m,case['id']) if mode=='CNN' else None
            buffer=np.empty((485,45669),np.float32);count=0;failure=None;maximum=0.;nf=full.calls;nh=exactH.calls
            with (out/'chain.jsonl').open('x',encoding='utf-8') as stream:
                for k in range(485):
                    if time.perf_counter()-start>600:raise TimeoutError('TEST_CPU_BUDGET')
                    if mode=='CNN':
                        try:state,row=engine.step(pixels[k],k)
                        except (ValueError,RuntimeError) as exc:failure=dict(step=k,error=repr(exc));break
                    else:
                        old=state
                        if mode=='Full':state=full.step(old,pixels[k])
                        else:
                            rr=r.step(old,pixels[k],step_id=k,run_id='Sham',condition_id=case['id'])
                            hh=exactH.step(old,pixels[k]);state=torch.empty_like(old);state[m['H']]=hh;state[m['R']]=rr.activity
                        row=dict(step=k,old=digest(old),input=digest(pixels[k]),new=digest(state),time=k*.005,next_time=(k+1)*.005,committed=True)
                    if not torch.isfinite(state).all():raise FloatingPointError('NONFINITE')
                    buffer[k]=state.numpy();count+=1;maximum=max(maximum,float(state.abs().max()));stream.write(json.dumps(row)+'\n')
            if mode=='CNN':assert full.calls==nf and exactH.calls==nh
            np.save(out/'states.npy',buffer[:count]);np.save(out/'final.npy',state.numpy())
            if mode=='Sham':
                reference=np.load(out.parent/'Full/states.npy',mmap_mode='r')
                assert np.allclose(buffer[:count],reference,atol=1e-5,rtol=1e-5)
            flow=decoder.decode(buffer[:count]);np.save(out/'flow.npy',flow)
            result=dict(case=case['id'],mode=mode,steps=count,complete=count==485,failure=failure,
                maximum_abs=maximum,wall_s=time.perf_counter()-tick,native_H_updates=full.calls-nf+exactH.calls-nh,
                CNN_calls=cnn.calls if mode=='CNN' else 0,teacher_corrections=0,actual_CPU=True)
            dump(out/'RESULT.json',result);records.append(result);print(json.dumps(result),flush=True)
    assert sha(identity['path'])==identity['sha256'];decoder.assert_unchanged()
    dump(HERE/'TEST_EXECUTION.json',dict(status='ACTUAL_NEW_HOLDOUT_CPU_EXECUTION',records=records,
        commits=sum(r['steps'] for r in records),wall_s=time.perf_counter()-start,GPU=0,model_state_unchanged=True,decoder_state_unchanged=True))

def analyze():
    if not (HERE/'TEST_EXECUTION.json').exists():return
    spec=importlib.util.spec_from_file_location('fixed_flow_metrics',LANE/'t4t5_criticality_20261011/metrics.py')
    metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
    m=mapping();roi=np.load(LANE/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy')
    results=[]
    for case in load(HERE/'TEST_INPUTS.json'):
        root=HERE/'test_runs'/case['id'];ref=np.load(root/'Full/states.npy',mmap_mode='r');a=np.load(root/'CNN/states.npy',mmap_mode='r')
        n=len(a);records=[]
        for k in range(n):
            dh=a[k,m['H']].astype(np.float64)-ref[k,m['H']];dr=a[k,m['R']].astype(np.float64)-ref[k,m['R']]
            records.append(dict(step=k,H_RMSE=float(np.sqrt(np.mean(dh*dh))),R_RMSE=float(np.sqrt(np.mean(dr*dr))),
                H_max=float(abs(dh).max()),R_max=float(abs(dr).max()),
                H_nRMSE=float(np.linalg.norm(dh)/max(np.linalg.norm(ref[k,m['H']].astype(np.float64)),1e-12)),
                R_nRMSE=float(np.linalg.norm(dr)/max(np.linalg.norm(ref[k,m['R']].astype(np.float64)),1e-12))))
        dump(root/'STEP_ERRORS.json',records)
        row=dict(case=case['id'],variant=case['variant'],angle=case['angle'],polarity=case['polarity'],complete=n==485,
            final_state_max_error=float(abs(a[-1].astype(np.float64)-ref[n-1]).max()))
        if n==485:
            hr=ref[:,m['H_grid_ids']].astype(np.float64);hv=a[:,m['H_grid_ids']].astype(np.float64)
            baseline=hr[160:200].mean(0);delta=hv[200:]-hr[200:]
            relative=float(np.linalg.norm(delta)/max(np.linalg.norm(hr[200:]-baseline),1e-12))
            subtype={t:float(np.linalg.norm(delta[:,i])/max(np.linalg.norm(hr[200:,i]-baseline[i]),1e-12)) for i,t in enumerate(TYPES)}
            f=np.load(root/'Full/flow.npy');g=np.load(root/'CNN/flow.npy')
            fm={name:metrics.vector_metrics(f,g,roi,window=window) for name,window in [('primary',slice(200,286)),('allpost',slice(200,485))]}
            passed=bool(relative<=.2 and all(v['reference_eligible'] and v['field_error_E']<=.2 and .8<=v['magnitude_ratio']<=1.2 and v['angle_deg'] is not None and v['angle_deg']<=15 for v in fm.values()))
            row.update(H_response_relative_L2=relative,subtype_response_relative_L2=subtype,flow=fm,pass_gate=passed)
        else:row.update(pass_gate=False,reason='INCOMPLETE')
        results.append(row)
    dump(HERE/'RESULTS.json',dict(status='PASS_FIXED_HOLDOUT_FUNCTIONAL_GATE' if all(r['pass_gate'] for r in results) else 'HOLDOUT_FUNCTIONAL_NOT_PASS',
        passed=sum(r['pass_gate'] for r in results),total=len(results),records=results,model_parameters=31168,GPU=0))
    print(json.dumps(results),flush=True)

if __name__=='__main__':
    try:run();analyze()
    except BaseException as exc:
        dump(HERE/f'FAILURE_evaluate_{time.time_ns()}.json',dict(error=repr(exc),retry=False));raise
