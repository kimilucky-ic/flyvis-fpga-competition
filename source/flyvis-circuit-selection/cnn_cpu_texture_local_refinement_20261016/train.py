from core import *

def build_data(model,plan):
    tick=time.perf_counter();m=ref.mapping();initial=np.load(BUNDLE/'initial_state_full.npy')
    sources=[]
    for name,file in plan['legacy_paths'].items():
        sources.append(dict(id=name,kind='motion',group='motion',states=file,states_batch=True,steps=485,
            path=str(LANE/'t4t5_criticality_20261011/cpu_preparation_r1'/(name+'_stimulus.npy')),inputs_batch=True))
    old={c['id']:c for c in load(OLD/'INPUTS.json')}
    for name in ['STATIC_TEXTURE5s','OFF345_local_moving_background']:
        sources.append(dict(id=name,kind=old[name]['kind'],group=old[name]['group'],states=str(OLD/'runs'/name/'Full/states_raw.npy'),
            states_batch=False,steps=1000,path=old[name]['path'],inputs_batch=False))
    _,_,_,params=ref.source()
    for case in load(HERE/'training/INPUTS.json'):
        out=HERE/'training/teacher'/case['id'];out.mkdir(parents=True)
        x=np.load(case['path']);assert sha(case['path'])==case['sha256']
        full=ref.OriginalTargets(params,np.arange(45669));state=torch.from_numpy(initial.copy())
        values=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(1000,45669))
        with (out/'chain.jsonl').open('x',encoding='utf-8') as journal:
            for k in range(1000):
                new=full.step(state,torch.from_numpy(x[k]));assert torch.isfinite(new).all() and new.abs().max()<=100
                journal.write(json.dumps(dict(step=k,old=digest(state),input=digest(x[k]),new=digest(new),time=k*.005,next_time=(k+1)*.005))+'\n')
                state=new;values[k]=state.numpy()
        values.flush();del values
        sources.append(dict(id=case['id'],kind=case['kind'],group=case['group'],states=str(out/'states.npy'),
            states_batch=False,steps=1000,path=case['path'],inputs_batch=False))
        print(json.dumps(dict(stage='TRAIN_TEACHER',case=case['id'],commits=1000)),flush=True)
    n=sum(s['steps'] for s in sources);N=n+128
    fields=np.lib.format.open_memmap(HERE/'training/fields.npy',mode='w+',dtype=np.float32,shape=(N,23,722));fields[:,:,-1]=0
    target=np.lib.format.open_memmap(HERE/'training/delta.npy',mode='w+',dtype=np.float32,shape=(N,8,721))
    index=0
    for s in sources:
        a=np.load(s['states'],mmap_mode='r');a=a[0] if s['states_batch'] else a
        s['first_row']=index
        for k in range(s['steps']):
            old=initial if k==0 else a[k-1]
            fields[index,:,:721]=old[m['field_ids']]
            target[index]=a[k,m['H_grid_ids']]-old[m['H_grid_ids']]
            index+=1
    rng=np.random.default_rng(2026101647)
    augmented=np.empty((128,45669),np.float32);native=ref.OriginalTargets(params,m['H'])
    for j in range(128):
        old=initial.copy();old[m['field_ids']]=(rng.normal(size=(23,721)).astype(np.float32)*model.input_scale.numpy()[:,None])
        nxt=native.step(torch.from_numpy(old),torch.zeros(721)).numpy()
        augmented[j]=old;fields[n+j,:,:721]=old[m['field_ids']];target[n+j]=nxt.reshape(8,721)-old[m['H_grid_ids']]
    fields.flush();target.flush();np.save(HERE/'training/augmented_old_states.npy',augmented)
    data=dict(sources=sources,sensory_rows=n,augmented_rows=128,teacher_new_Full_steps=4000,
        teacher_augmented_H_calls=native.calls,wall_s=time.perf_counter()-tick,train_only=True)
    dump(HERE/'training/DATA.json',data)
    del fields,target,params,augmented;gc.collect()
    return data


def sampled_indices(data):
    rng=np.random.default_rng(2026101648);n=data['sensory_rows']
    valid_times=[];train_times=[];steady=[]
    for s in data['sources']:
        k=np.arange(s['steps']);train_times.extend((s['first_row']+k[k%5!=4]).tolist());valid_times.extend((s['first_row']+k[k%5==4]).tolist())
        if s['group']=='static':steady.extend((s['first_row']+k[(k>=400)&(k%5!=4)]).tolist())
    f=np.concatenate([rng.integers(n,n+96,12288),rng.choice(train_times,6144),rng.choice(steady,2048),np.zeros(721,dtype=np.int64)])
    p=np.concatenate([rng.integers(0,721,20480),np.arange(721)])
    weights=np.ones(len(f));weights[-2769:-721]=2;weights[-721:]=np.sqrt(8)
    val=dict(sensory=(rng.choice(valid_times,4096),rng.integers(0,721,4096)),
        augmented=(rng.integers(n+96,n+128,4096),rng.integers(0,721,4096)))
    assert set(f[f<n]) .isdisjoint(valid_times)
    assert not np.any((f>=n+96)&(f<n+128))
    np.savez(HERE/'training/design_indices.npz',frame=f,pixel=p,weights=weights,
        sensory_validation_frame=val['sensory'][0],sensory_validation_pixel=val['sensory'][1],
        augmented_validation_frame=val['augmented'][0],augmented_validation_pixel=val['augmented'][1])
    return f,p,weights,val


def validate(model,x,y,val):
    m=ref.mapping();results={}
    with torch.no_grad():
        for name,(frames,pixels) in val.items():
            sq=np.zeros(8);energy=np.zeros(8)
            for k in range(0,len(frames),256):
                f=torch.as_tensor(frames[k:k+256]);p=torch.as_tensor(pixels[k:k+256]);X=feature_rows(x,f,p,model,m)
                pred=(X[:,:-8]@model.kernel.flatten(1).T+X[:,-8:]@model.recurrent.T+model.offset)*model.output_scale
                truth=y[f[:,None],torch.arange(8)[None,:],p[:,None]]
                sq+=((pred-truth).double().square().sum(0)).numpy();energy+=(truth.double().square().sum(0)).numpy()
            ratio=np.sqrt(sq/np.maximum(energy,1e-24));overall=float(np.sqrt(sq.sum()/energy.sum()))
            results[name]=dict(points=len(frames),increment_nRMSE=overall,subtype_increment_nRMSE=ratio.tolist(),
                absolute_increment_RMSE=float(np.sqrt(sq.sum()/(len(frames)*8))),pass_gate=bool(overall<=.10 and ratio.max()<=.20))
    return dict(pass_gate=all(v['pass_gate'] for v in results.values()),groups=results)


def fit(model,data,plan):
    began=time.perf_counter();m=ref.mapping();f,p,weights,val=sampled_indices(data)
    x=torch.from_numpy(np.load(HERE/'training/fields.npy',mmap_mode='c'))
    y=torch.from_numpy(np.load(HERE/'training/delta.npy',mmap_mode='c'))
    baseline=validate(model,x,y,val);dump(HERE/'training/BASELINE_VALIDATION.json',baseline)
    X=torch.empty((len(f),3895),dtype=torch.float64);Y=torch.empty((len(f),8),dtype=torch.float64)
    prior=torch.cat([model.kernel.flatten(1),model.recurrent],1).T.detach().double().clone()
    prior_offset=model.offset.detach().double().clone()
    with torch.no_grad():
        for k in range(0,len(f),256):
            ff=torch.as_tensor(f[k:k+256]);pp=torch.as_tensor(p[k:k+256]);v=feature_rows(x,ff,pp,model,m).double()
            X[k:k+256]=v
            Y[k:k+256]=(y[ff[:,None],torch.arange(8)[None,:],pp[:,None]]/model.output_scale).double()-v@prior-prior_offset
    del x,y;gc.collect()
    w=torch.from_numpy(weights).double();total=w.square().sum()
    mean=torch.zeros(3895,dtype=torch.float64);second=mean.clone();ym=torch.zeros(8,dtype=torch.float64)
    for k in range(0,len(f),512):
        ww=w[k:k+512].square()[:,None];z=X[k:k+512]
        mean+=(z*ww).sum(0);second+=(z.square()*ww).sum(0);ym+=(Y[k:k+512]*ww).sum(0)
    mean/=total;ym/=total;scale=(second/total-mean.square()).clamp_min(1e-8).sqrt()
    for k in range(0,len(f),512):
        X[k:k+512].sub_(mean).div_(scale).mul_(w[k:k+512,None])
        Y[k:k+512].sub_(ym).mul_(w[k:k+512,None])
    ridge=plan['fit']['ridge'];beta=torch.zeros((3895,8),dtype=torch.float64)
    rhs=X.T@Y/total;residual=rhs.clone();direction=residual.clone();rs=residual.square().sum(0);norm=rs.sqrt().clamp_min(1e-30)
    rows=[];converged=False
    with (HERE/'training/cg_steps.jsonl').open('x',encoding='utf-8') as journal:
        for iteration in range(plan['fit']['max_iterations']):
            if time.perf_counter()-began>plan['fit']['max_wall_s']:raise TimeoutError('BOUNDED_CPU_FIT')
            product=X.T@(X@direction)/total+ridge*direction
            alpha=rs/(direction*product).sum(0).clamp_min(1e-30);beta+=direction*alpha;residual-=product*alpha
            newrs=residual.square().sum(0);relative=float((newrs.sqrt()/norm).max())
            row=dict(iteration=iteration,maximum_relative_normal_equation_residual=relative,wall_s=time.perf_counter()-began)
            journal.write(json.dumps(row)+'\n');rows.append(row)
            if (iteration+1)%25==0:print(json.dumps(dict(stage='CPU_RESIDUAL_CG',**row)),flush=True)
            if relative<plan['fit']['stopping_relative_normal_equation_residual']:converged=True;break
            direction=residual+direction*(newrs/rs.clamp_min(1e-30));rs=newrs
    coefficient=beta/scale[:,None];intercept=ym-mean@coefficient
    with torch.no_grad():
        final=prior+coefficient;model.kernel.copy_(final[:-8].T.reshape_as(model.kernel).float())
        model.recurrent.copy_(final[-8:].T.float());model.offset.copy_((prior_offset+intercept).float())
    del X,Y;gc.collect()
    x=torch.from_numpy(np.load(HERE/'training/fields.npy',mmap_mode='c'));y=torch.from_numpy(np.load(HERE/'training/delta.npy',mmap_mode='c'))
    result=validate(model,x,y,val);del x,y;gc.collect()
    torch.save(model.state_dict(),HERE/'training/model.pt')
    dump(HERE/'training/FIT.json',dict(status='FITTED_SAME_31168_PARAMETER_MODEL',iterations=len(rows),converged_normal_equation=converged,
        residual_last=rows[-1]['maximum_relative_normal_equation_residual'],wall_s=time.perf_counter()-began,baseline=baseline,
        validation=result,original_H_coefficients_copied=False,training_data_includes_counterfactual_neuronal_states=True))
    print(json.dumps(dict(stage='ONE_STEP_GATE',result=result,iterations=len(rows),wall_s=time.perf_counter()-began)),flush=True)
    return result


def short_check(model,data):
    began=time.perf_counter();m=ref.mapping();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    decoder=ref.CPUDecoder();records=[];guard_calls=0
    def forbidden(*a,**kw):
        nonlocal guard_calls
        guard_calls+=1;raise RuntimeError('NATIVE_H_FORBIDDEN_IN_SHORT_PRODUCTION')
    original=ref.OriginalTargets.step
    for source in data['sources']:
        reference=np.load(source['states'],mmap_mode='r');reference=reference[0] if source['states_batch'] else reference
        frames=np.load(source['path']);frames=frames[0,:,0] if source['inputs_batch'] else frames
        for start in [0,196,320] if source['steps']==485 else [0,320,800]:
            length=128;old=initial if start==0 else torch.from_numpy(np.array(reference[start-1],copy=True))
            engine=fresh_loop(model,m,old,source['id']+str(start));out=HERE/'training/short'/(source['id']+'_k'+str(start));out.mkdir(parents=True)
            states=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(length,45669))
            failure=None;count=0;ref.OriginalTargets.step=forbidden
            try:
                with (out/'chain.jsonl').open('x',encoding='utf-8') as journal:
                    for j in range(length):
                        try:new,chain=engine.step(torch.from_numpy(frames[start+j]),j)
                        except (ValueError,RuntimeError) as exc:failure=repr(exc);break
                        states[j]=new.numpy();journal.write(json.dumps(chain)+'\n');count+=1
            finally:ref.OriginalTargets.step=original;states.flush()
            truth=np.asarray(reference[start:start+count]);value=states[:count]
            dh=value[:,m['H']].astype(np.float64)-truth[:,m['H']];dr=value[:,m['R']].astype(np.float64)-truth[:,m['R']]
            hr=float(np.linalg.norm(dh)/max(np.linalg.norm(truth[:,m['H']]),1e-12));rr=float(np.linalg.norm(dr)/max(np.linalg.norm(truth[:,m['R']]),1e-12))
            sub=np.sqrt(np.sum(dh.reshape(-1,8,721)**2,axis=(0,2))/np.maximum(np.sum(truth[:,m['H']].reshape(-1,8,721).astype(np.float64)**2,axis=(0,2)),1e-24))
            passed=bool(count==128 and hr<=.05 and rr<=.01 and sub.max()<=.10)
            static=None
            if source['group']=='static' and count:
                ff=decoder.decode(truth);cf=decoder.decode(value);roi=np.load(accepted.ROI_PATH)
                h=float(np.sqrt(np.mean(dh**2)));r=float(np.sqrt(np.mean(dr**2)));flow=float(np.sqrt(np.mean((cf[:,:,roi].astype(np.float64)-ff[:,:,roi])**2)))
                static=dict(H_RMSE=h,R_RMSE=r,flow_RMSE=flow);passed=passed and max(h,r,flow)<=.002
                np.savez(out/'flow.npz',Full=ff,CNN=cf)
            row=dict(source=source['id'],start=start,length=count,pass_gate=passed,H_nRMSE=hr,R_nRMSE=rr,subtype_nRMSE=sub.tolist(),
                static=static,failure=failure,native_H_updates=0,teacher_corrections_during_window=0)
            dump(out/'RESULT.json',row);records.append(row);del states
    # Existing gray reference is a training control, not a new holdout.
    gray=np.load(LANE/'cnn_t4t5_cpu_refinement_20261016/gray_reference.npy',mmap_mode='r')
    engine=fresh_loop(model,m,initial,'gray_training');errors=[];ref.OriginalTargets.step=forbidden
    try:
        for j in range(128):
            state,_=engine.step(torch.full((721,),.5),j);errors.append(state.numpy()-gray[j])
    finally:ref.OriginalTargets.step=original
    errors=np.asarray(errors,dtype=np.float64);h=float(np.sqrt(np.mean(errors[:,m['H']]**2)))
    records.append(dict(source='GRAY',start=0,length=128,H_RMSE=h,pass_gate=h<=.002,native_H_updates=0,teacher_corrections_during_window=0))
    decoder.assert_unchanged()
    result=dict(pass_gate=all(r['pass_gate'] for r in records),records=records,commits=sum(r['length'] for r in records),
        native_H_guard_violations=guard_calls,wall_s=time.perf_counter()-began)
    dump(HERE/'training/SHORT_GATE.json',result)
    print(json.dumps(dict(stage='SHORT_GATE',passed=result['pass_gate'],windows=len(records),commits=result['commits'],wall_s=result['wall_s'])),flush=True)
    return result


def main():
    p=check(deep=True);assert not (HERE/'training/DATA.json').exists(),'ONE_ATTEMPT'
    began=time.perf_counter();model=ref.model_from(MODEL);assert sum(t.numel() for t in model.parameters())==31168
    data=build_data(model,p);one=fit(model,data,p);short=short_check(model,data)
    passed=bool(one['pass_gate'] and short['pass_gate']);path=HERE/'training/model.pt'
    dump(HERE/'TRAINING_GATE.json',dict(status='PASS_TRAINING_GATES' if passed else 'TRAINING_GATES_NOT_PASS',pass_gate=passed,
        one_step=one,short_pass=short['pass_gate'],wall_s=time.perf_counter()-began,parameters=31168,GPU=0,board=0))
    check(deep=True)
    if passed:dump(HERE/'MODEL_FREEZE.json',dict(path=str(path),sha256=sha(path),time_ns=time.time_ns(),
        gate_sha256=sha(HERE/'TRAINING_GATE.json'),new_test_generated=False))
    print(json.dumps(dict(stage='TRAINING_FINISHED',pass_gate=passed,wall_s=time.perf_counter()-began,model_sha=sha(path))),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        dump(HERE/('FAILURE_train_'+str(time.time_ns())+'.json'),dict(error=repr(exc),automatic_retry=False,GPU=0,board=0));raise
