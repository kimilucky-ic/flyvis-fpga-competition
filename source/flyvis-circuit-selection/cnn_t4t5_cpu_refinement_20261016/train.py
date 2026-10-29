"""Same-model CPU identification, explicit validation, then bounded short BPTT."""
from shared import *

def feature_rows(x,frame,pixel,model,m):
    frame=torch.as_tensor(frame,dtype=torch.long);pixel=torch.as_tensor(pixel,dtype=torch.long)
    n=torch.as_tensor(np.where(m['neighbors']>=0,m['neighbors'],721))
    patch=x[frame[:,None,None],torch.arange(x.shape[1])[None,:,None],n[pixel,None,:]]
    raw_h=x[frame[:,None],model.h_channels[None,:],pixel[:,None]]
    return torch.cat([(torch.relu(patch)/model.input_scale[None,:,None]).flatten(1),raw_h/model.h_scale],1)

def validation(model,x,y,indices):
    m=mapping();frames,pixels=indices
    error=torch.zeros(8,dtype=torch.float64);energy=torch.zeros(8,dtype=torch.float64)
    with torch.no_grad():
        for start in range(0,len(frames),512):
            f=torch.as_tensor(frames[start:start+512]);p=torch.as_tensor(pixels[start:start+512])
            design=feature_rows(x,f,p,model,m)
            pred=(design[:,:-8]@model.kernel.flatten(1).T+design[:,-8:]@model.recurrent.T+model.offset)*model.output_scale
            truth=y[f[:,None],torch.arange(8)[None,:],p[:,None]]
            error+=((pred-truth).double()**2).sum(0);energy+=(truth.double()**2).sum(0)
    ratio=np.sqrt(error.numpy()/np.maximum(energy.numpy(),1e-24));overall=float(torch.sqrt(error.sum()/energy.sum()))
    return dict(overall_increment_nRMSE=overall,subtype_increment_nRMSE=ratio.tolist(),
        pass_gate=bool(overall<=.10 and ratio.max()<=.20),points=len(frames),new_neural_steps=0)

def build_training_data(model):
    start=time.perf_counter();m=mapping();_,_,_,params=source();H=OriginalTargets(params,m['H'])
    assert len(H.input_target)==0
    initial=np.load(BUNDLE/'initial_state_full.npy');references=train_references()
    rng=np.random.default_rng(2026101607);ids=m['field_ids'];valid=ids>=0
    augmented=np.empty((256,45669),np.float32);xf=np.empty((256,23,722),np.float32);yf=np.empty((256,8,721),np.float32)
    train_time=np.flatnonzero(np.arange(485)%5!=4);names=list(references)
    for j in range(256):
        condition=names[int(rng.integers(4))];k=int(rng.choice(train_time))
        a=initial.copy() if j%4==0 or k==0 else np.array(references[condition][k-1],copy=True)
        noise=rng.normal(size=ids.shape).astype(np.float32)*model.input_scale.numpy()[:,None]*np.float32(.1)
        a[ids[valid]]+=noise[valid]
        nxt=H.step(torch.from_numpy(a),torch.zeros(721)).numpy()
        augmented[j]=a;xf[j,:,:721]=a[np.maximum(ids,0)]*valid;xf[j,:,-1]=0
        yf[j]=nxt.reshape(8,721)-a[m['H_grid_ids']]
    np.save(HERE/'training/augmented_old_states.npy',augmented)
    np.save(HERE/'training/augmented_delta.npy',yf)
    x=torch.from_numpy(np.concatenate([np.load(OLD/'training/teacher_fields.npy'),xf]))
    y=torch.from_numpy(np.concatenate([np.load(OLD/'training/target_delta.npy'),yf]))
    # A true gray trajectory is a training stability reference, not a test.
    full=OriginalTargets(params,np.arange(45669));state=torch.from_numpy(initial.copy());grey=[]
    for k in range(128):state=full.step(state,torch.full((721,),.5));grey.append(state.numpy().copy())
    np.save(HERE/'gray_reference.npy',np.array(grey))
    dump(HERE/'training/DATA.json',dict(original_training_conditions=names,cached_transitions=1940,
        new_training_only_H_teacher_steps=H.calls,new_Full_gray_steps=full.calls,
        augmentation='counterfactual neuronal-state perturbations, NOT extra sensory videos',
        no_native_H_in_production=True,wall_s=time.perf_counter()-start))
    return x,y

def fit_linear(model,x,y,val_indices):
    start=time.perf_counter();m=mapping();rng=np.random.default_rng(2026101608)
    train_time=np.flatnonzero(np.arange(485)%5!=4)
    f=np.concatenate([rng.integers(0,4,8192)*485+rng.choice(train_time,8192),rng.integers(1940,2196,8192),np.zeros(721,dtype=np.int64)])
    p=np.concatenate([rng.integers(0,721,16384),np.arange(721)])
    weights=torch.ones(len(f),dtype=torch.float64);weights[-721:]=np.sqrt(8)
    np.savez(HERE/'training/design_indices.npz',frame=f,pixel=p,validation_frame=val_indices[0],validation_pixel=val_indices[1])
    X=torch.empty((len(f),3895),dtype=torch.float64);Y=torch.empty((len(f),8),dtype=torch.float64)
    for k in range(0,len(f),512):
        ff=torch.as_tensor(f[k:k+512]);pp=torch.as_tensor(p[k:k+512]);X[k:k+512]=feature_rows(x,ff,pp,model,m).double()
        Y[k:k+512]=(y[ff[:,None],torch.arange(8)[None,:],pp[:,None]]/model.output_scale).double()
    total=weights.square().sum();mean=(X*weights.square()[:,None]).sum(0)/total
    ymean=(Y*weights.square()[:,None]).sum(0)/total
    X-=mean;scale=torch.sqrt((X.square()*weights.square()[:,None]).sum(0)/total).clamp_min(1e-4)
    X/=scale;X*=weights[:,None];Y=(Y-ymean)*weights[:,None]
    ridge=1e-6;beta=torch.zeros((3895,8),dtype=torch.float64)
    rhs=X.T@Y/total;residual=rhs.clone();direction=residual.clone();rs=(residual*residual).sum(0)
    norm0=torch.sqrt(rs).clamp_min(1e-30);history=[]
    with (HERE/'training/cg_steps.jsonl').open('x',encoding='utf-8') as stream:
        for iteration in range(400):
            if time.perf_counter()-start>600:raise TimeoutError('CPU_FIT_BUDGET')
            product=X.T@(X@direction)/total+ridge*direction
            denominator=(direction*product).sum(0).clamp_min(1e-30);alpha=rs/denominator
            beta+=direction*alpha;residual-=product*alpha
            next_rs=residual.square().sum(0);relative=float((torch.sqrt(next_rs)/norm0).max())
            row=dict(iteration=iteration,maximum_relative_normal_equation_residual=relative,wall_s=time.perf_counter()-start)
            stream.write(json.dumps(row)+'\n');history.append(row)
            if (iteration+1)%25==0:print(json.dumps(dict(stage='same_CNN_CG',**row)),flush=True)
            if relative<1e-8:break
            direction=residual+direction*(next_rs/rs.clamp_min(1e-30));rs=next_rs
    coefficient=beta/scale[:,None];intercept=ymean-mean@coefficient
    with torch.no_grad():
        model.kernel.copy_(coefficient[:-8].T.reshape_as(model.kernel).float())
        model.recurrent.copy_(coefficient[-8:].T.float());model.offset.copy_(intercept.float())
    val=validation(model,x,y,val_indices)
    torch.save(model.state_dict(),HERE/'training/ridge.pt')
    dump(HERE/'training/RIDGE.json',dict(status='FITTED_SAME_ARCHITECTURE',parameters=31168,iterations=len(history),
        wall_s=time.perf_counter()-start,validation=val,history=history,original_H_weights_copied=False))
    print(json.dumps(dict(stage='ridge_validation',**val)),flush=True)
    return val

def bptt(model,x,y,val_indices):
    """Autograd through frozen original R and own CNN H; no H teacher in forward."""
    start=time.perf_counter();m=mapping();_,_,_,params=source();r=OriginalTargets(params,m['R'])
    refs=train_references();frames=train_frames();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    rng=np.random.default_rng(2026101609);torch.manual_seed(2026101609)
    optimizer=torch.optim.Adam(model.parameters(),lr=1e-4)
    hids=torch.as_tensor(m['H']);rids=torch.as_tensor(m['R']);fieldids=torch.as_tensor(np.maximum(m['field_ids'],0));valid=torch.from_numpy(m['field_ids']>=0)
    names=list(refs);history=[]
    for update in range(100):
        if time.perf_counter()-start>600:raise TimeoutError('CPU_BPTT_BUDGET')
        name=names[update%4];k=int(rng.choice([0,144,192,208,240,288,352,432]))
        old=initial.clone() if k==0 else torch.from_numpy(np.array(refs[name][k-1],copy=True))
        optimizer.zero_grad(set_to_none=True);loss=0
        for j in range(16):
            # Both candidates use old. Gradient-enabled training R is identical
            # to canonical R-only forward. Only CNN parameters are optimized.
            next_r=OriginalTargets.step.__wrapped__(r,old,torch.from_numpy(frames[name][k+j]))
            next_h=model((old[fieldids]*valid)[None])[0].reshape(-1)
            candidate=torch.empty_like(old);candidate[hids]=next_h;candidate[rids]=next_r
            target=torch.from_numpy(np.array(refs[name][k+j],copy=True))
            loss=loss+(((candidate[hids]-target[hids]).reshape(8,721)/model.h_scale[:,None])**2).mean()
            loss=loss+.1*(candidate[rids]-target[rids]).square().mean()
            old=candidate
        loss/=16
        f=rng.integers(0,1940,256);pix=rng.integers(0,721,256)
        design=feature_rows(x,f,pix,model,m)
        aux=(design[:,:-8]@model.kernel.flatten(1).T+design[:,-8:]@model.recurrent.T+model.offset)*model.output_scale
        truth=y[torch.as_tensor(f)[:,None],torch.arange(8)[None,:],torch.as_tensor(pix)[:,None]]
        loss=loss+.1*(((aux-truth)/model.output_scale)**2).mean()
        if not torch.isfinite(loss):raise FloatingPointError('TRAINING_NONFINITE')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step()
        rec=dict(update=update,loss=float(loss.detach()),wall_s=time.perf_counter()-start)
        history.append(rec)
        if (update+1)%25==0:
            path=HERE/f'training/bptt_{update+1}.pt';torch.save(model.state_dict(),path)
            val=validation(model,x,y,val_indices);short=short_validation(model,f'bptt_{update+1}')
            dump(HERE/f'training/BPTT_{update+1}.json',dict(validation=val,short_pass=short['pass_gate'],history=history,
                training_R_steps=r.calls,native_H_training_forward_steps=0))
            if val['pass_gate'] and short['pass_gate']:return path,val,short
    return None,None,None

def main():
    freezecheck(deep=True);(HERE/'training').mkdir();model=fresh_model();x,y=build_training_data(model)
    rng=np.random.default_rng(2026101610);valid_times=np.flatnonzero(np.arange(485)%5==4)
    val_indices=(rng.integers(0,4,4096)*485+rng.choice(valid_times,4096),rng.integers(0,721,4096))
    dump(HERE/'training/BASELINE_VALIDATION.json',validation(model,x,y,val_indices))
    val=fit_linear(model,x,y,val_indices);short=short_validation(model,'ridge')
    path=HERE/'training/ridge.pt'
    if not (val['pass_gate'] and short['pass_gate']):
        chosen,newval,newshort=bptt(model,x,y,val_indices)
        if chosen is not None:path,val,short=chosen,newval,newshort
    passed=bool(val['pass_gate'] and short['pass_gate'])
    dump(HERE/'TRAINING_GATE.json',dict(status='PASS_TRAINING_GATES' if passed else 'TRAINING_GATES_NOT_PASS',
        pass_gate=passed,one_step=val,short_label=short['label'],short_pass=short['pass_gate'],model_path=str(path),
        old_test_cases_used=False,new_holdout_opened=False,parameters=31168,GPU=0))
    if passed:dump(HERE/'MODEL_FREEZE.json',dict(path=str(path),sha256=sha(path),time_ns=time.time_ns(),gate_sha=sha(HERE/'TRAINING_GATE.json')))
    print('TRAINING_GATE',passed,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        dump(HERE/f'FAILURE_train_{time.time_ns()}.json',dict(error=repr(exc),retry=False));raise
