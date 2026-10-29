from core import *

def main():
    check(deep=True);freeze=load(HERE/'MODEL_FREEZE.json');assert load(HERE/'TRAINING_GATE.json')['pass_gate']
    assert sha(freeze['path'])==freeze['sha256'];cases=make_inputs('testing')
    assert load(HERE/'testing/INPUT_GENERATION.json')['time_ns']>freeze['time_ns']
    model=ref.model_from(freeze['path']);m=ref.mapping();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    decoder=ref.CPUDecoder();_,_,_,params=ref.source();began=time.perf_counter();run=uuid.uuid4().hex;records=[];guard=0
    def forbidden(*a,**kw):
        nonlocal guard
        guard+=1;raise RuntimeError('NATIVE_H_FORBIDDEN_IN_FORMAL_CNN')
    for i,case in enumerate(cases):
        x=np.load(case['path']);assert sha(case['path'])==case['sha256']
        for mode in ['Full','CNN']+(['Sham'] if i==0 else []):
            tick=time.perf_counter();out=HERE/'testing/runs'/case['id']/mode;out.mkdir(parents=True)
            values=np.lib.format.open_memmap(out/'states_raw.npy',mode='w+',dtype=np.float32,shape=(1000,45669))
            state=initial.clone();engine=fresh_loop(model,m,initial,run+case['id']) if mode=='CNN' else None
            native=ref.OriginalTargets(params,np.arange(45669) if mode=='Full' else m['H']) if mode!='CNN' else None
            r=ref.r_service() if mode=='Sham' else None;count=0;failure=None
            original=ref.OriginalTargets.step
            if mode=='CNN':ref.OriginalTargets.step=forbidden
            try:
                with (out/'chain.jsonl').open('x',encoding='utf-8') as stream:
                    for k in range(1000):
                        if time.perf_counter()-began>360:raise TimeoutError('FORMAL_CPU_TIME_BOUND')
                        pixels=torch.from_numpy(x[k])
                        try:
                            if mode=='CNN':candidate,chain=engine.step(pixels,k)
                            else:
                                if mode=='Full':candidate=native.step(state,pixels)
                                else:
                                    rr=r.step(state,pixels,step_id=k,run_id=run,condition_id=case['id']);hh=native.step(state,pixels)
                                    assert np.array_equal(rr.global_node_indices.numpy(),m['R'])
                                    candidate=torch.empty_like(state);candidate[m['H']]=hh;candidate[m['R']]=rr.activity
                                if not torch.isfinite(candidate).all() or candidate.abs().max()>100:raise ValueError('STABILITY_ENVELOPE')
                                chain=dict(step=k,old=digest(state),input=digest(pixels),new=digest(candidate),time=k*.005,next_time=(k+1)*.005,committed=True)
                        except (ValueError,RuntimeError) as exc:failure=dict(step=k,error=repr(exc));break
                        values[k]=candidate.numpy();state=candidate;count+=1;stream.write(json.dumps(chain)+'\n')
            finally:ref.OriginalTargets.step=original;values.flush()
            np.save(out/'final.npy',state.numpy())
            dump(out/'VALIDITY.json',dict(valid_rows=count,allocated_rows=1000,invalid_range=[count,1000],failure=failure))
            ff=decoder.decode(values[:count]);np.save(out/'flow.npy',ff);del values
            row=dict(case=case['id'],mode=mode,run_uuid=run,valid_steps=count,complete=count==1000,failure=failure,
                native_H_updates=0 if mode=='CNN' else native.calls,CNN_calls=engine.cnn.calls if engine else 0,
                teacher_corrections=0,wall_s=time.perf_counter()-tick,actual_CPU=True)
            dump(out/'RESULT.json',row);records.append(row);print(json.dumps(dict(stage='ACTUAL_NEW_TEST',**row)),flush=True)
    decoder.assert_unchanged();assert sha(freeze['path'])==freeze['sha256'];check(deep=True)
    dump(HERE/'TEST_EXECUTION.json',dict(status='ACTUAL_NEW_CPU_TEST_COMPLETE',records=records,
        commits=sum(r['valid_steps'] for r in records),wall_s=time.perf_counter()-began,
        model_unchanged=True,decoder_unchanged=True,training_updates_during_test=0,native_H_guard_violations=guard,GPU=0,board=0))

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        dump(HERE/('FAILURE_test_'+str(time.time_ns())+'.json'),dict(error=repr(exc),automatic_retry=False,GPU=0,board=0));raise
