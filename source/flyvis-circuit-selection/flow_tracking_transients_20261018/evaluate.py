"""One saved-data comparison, fixed numeric gates, no fresh neural computation."""
from analyze import *
from input_verified_tracker import InputVerifiedTracker,run,WINDOW_STEPS,INPUT_EPSILON

def score(pred,truth,mask):
    valid=pred[:,1]>0;k=pred[:,0].astype(int);e=np.linalg.norm(pred[:,2:4]-truth[k],axis=1)
    good=valid&mask;n=int(mask.sum());m=float(np.median(e[good])) if good.any() else None
    return dict(n=n,valid=int(good.sum()),within18px=int((good&(e<=3)).sum()),
        coverage=float(good.sum()/n),within18px_fraction=float((good&(e<=3)).sum()/n),
        median_valid_px=None if m is None else m*6,
        pass_gate=bool(good.sum()/n>=.9 and (good&(e<=3)).sum()/n>=.8 and m is not None and m<=2))

def focused_tests(f,x,xy,roi,cal):
    pred=run(f,x,xy,roi,cal);prefix=run(f[:500],x[:500],xy,roi,cal)
    assert np.allclose(pred[:50],prefix,atol=0,rtol=0,equal_nan=True)
    tests={'causal_prefix_exact':True};t=InputVerifiedTracker(xy,roi,cal)
    bad=[('wrong_step',f[0],x[0],1,1),('misaligned_input',f[0],x[0],0,1),
        ('NaN_flow',np.full((2,721),np.nan),x[0],0,0),('NaN_input',f[0],np.full(721,np.nan),0,0),
        ('input_shape',f[0],x[0,:720],0,0),('input_range',f[0],np.full(721,1.01),0,0),
        ('flow_shape',f[0,:,:720],x[0],0,0)]
    for key,ff,xx,k,ik in bad:
        try:t.step(ff,xx,k,ik)
        except ValueError:tests[key+'_rejected']=True
        else:raise AssertionError(key)
        assert t.original.next_step==0 and not t.inputs
    tests['bad_input_does_not_advance_either_history']=True
    # Sensor change by itself cannot generate any location: flow must still pass original gate.
    z=np.zeros_like(f);a=run(z,x,xy,roi,cal);assert not a[:,1].any()
    tests['changing_input_without_neural_motion_abstains']=True
    b=run(f,np.repeat(x[:1],len(x),axis=0),xy,roi,cal);assert not b[:,1].any()
    tests['constant_input_vetoes_even_transient_neural_motion']=True
    return tests

def main():
    started=time.perf_counter();p=load(source/'PREREGISTRATION.json');grid=np.load(PILOT/'GRID.npz');xy,roi=grid['xy'],grid['roi']
    cal=dict(np.load(source/'CALIBRATION.npz'));steps=np.arange(9,1000,10);times=steps*.005
    dump('CANDIDATE_SPEC.json',dict(frozen_before_candidate_comparison_ns=time.time_ns(),algorithm_sha256=sha(HERE/'input_verified_tracker.py'),
        original_tracker_sha256=sha(source/'tracker.py'),window_steps=WINDOW_STEPS,dt=.005,input_epsilon=INPUT_EPSILON,
        epsilon_source='half one mean-of9 unsigned8bit gray quantum; no outcome fitting',
        unknown_first100ms='abstain, explicitly not counted as a verified stationary observation',
        fixed_rule='original motion validity AND any sensor change within last100ms',
        coordinate_source='unchanged original flow-only tracker, no sensor-derived centroid or velocity',
        unchanged_primary_gates='each coverage>=.9, all motion frames within18px>=.8, valid median<=12px; controls<=.05 after1sec; original ROI331',
        status='retrospective data now seen, not a new heldout experiment',variants=1,
        neural_calls=0,decoder_calls=0,GPU=False,board=False))
    (HERE/'predictions').mkdir();rows=[];static=[];failures=[]
    for c in p['cases']:
        name=c['id'];f=np.load(source/'runs'/name/'flow.npy');x=np.load(source/'inputs'/(name+'.npy'))
        orig=np.load(source/'predictions'/(name+'.npy'));candidate=run(f,x,xy,roi,cal)
        series=np.load(HERE/'series'/(name+'.npz'));np.save(HERE/'predictions'/(name+'.npy'),candidate)
        assert np.array_equal(candidate[:,8:10],orig[:,8:10])
        good=candidate[:,1]>0
        assert np.array_equal(candidate[good,2:6],orig[good,2:6])
        assert not np.any(good&~(orig[:,1]>0))
        if c['kind']=='motion':
            truth=np.load(source/'truth'/(name+'.npz'))['position'];mask=(times>=c['onset'])&(times<c['stop'])
            tail=times>=c['stop'];late=times>=c['stop']+.2;pre=times<c['onset']
            # Counterfactual validity-only ablations, not newly stateful tracker implementations.
            alternatives={}
            for key,col in [('noEMA','noema_valid'),('white_temporal_correction','white_corrected_valid')]:
                a=orig.copy();a[:,1]=series[col];a[~series[col],2:6]=np.nan
                alternatives[key]=score(a,truth,mask)
            q=score(candidate,truth,mask)
            last=last_on(good,tail,times)
            oldlast=last_on(orig[:,1]>0,tail,times)
            row=dict(id=name,original=score(orig,truth,mask),candidate=q,flow_only_ablations=alternatives,
                motion_outputs_blocked=int(((orig[:,1]>0)&~good&mask).sum()),
                late_stop_outputs=int(late.sum()),original_late_stop=int(orig[late,1].sum()),candidate_late_stop=int(good[late].sum()),
                original_startup_premotion=int(orig[pre,1].sum()),candidate_startup_premotion=int(good[pre].sum()),
                original_last_trigger_after_stop_s=None if oldlast is None else oldlast-c['stop'],
                candidate_last_trigger_after_stop_s=None if last is None else last-c['stop'],
                coordinates_and_motion_threshold_unchanged=True)
            rows.append(row)
            err=np.linalg.norm(candidate[:,2:4]-truth[steps],axis=1)
            for i in np.flatnonzero(mask&(~good|(err>3))):
                failures.append(dict(id=name,step_id=int(steps[i]),valid=bool(good[i]),error_px=float(err[i]*6) if good[i] else None))
        else:
            static.append(dict(id=name,startup_outputs=int((steps<200).sum()),original_startup=int(orig[steps<200,1].sum()),
                candidate_startup=int(good[steps<200].sum()),scored_outputs=int((steps>=200).sum()),
                original_scored=int(orig[steps>=200,1].sum()),candidate_scored=int(good[steps>=200].sum()),
                unknown_outputs=int((candidate[:,12]==0).sum())))
        print('COMPARED',name,flush=True)
    # Old pilot motion data are development-only, retained as a regression, not fresh validation.
    oldrows=[]
    for c in load(PILOT/'PREREGISTRATION.json')['cases']:
        if c['kind']!='motion':continue
        name=c['id'];pred=run(np.load(PILOT/'runs'/name/'flow.npy'),np.load(PILOT/'inputs'/(name+'.npy')),xy,roi,cal)
        np.save(HERE/'predictions'/('old_'+name+'.npy'),pred)
        truth=np.load(PILOT/'truth'/(name+'.npz'))['position'];oldrows.append(dict(id=name,score=score(pred,truth,(steps>=200)&(steps<800))))
    tests=focused_tests(np.load(source/'runs/NEW_DIR20_V3/flow.npy'),np.load(source/'inputs/NEW_DIR20_V3.npy'),xy,roi,cal)
    dump('FOCUSED_TESTS.json',tests)
    dump('RESULT.json',dict(status='SAVED_DATA_INPUT_STILLNESS_VETO_IMPROVES_TRANSIENTS_NOT_FRESH_VALIDATION',
        motion=rows,static=static,old_development_regression=oldrows,failures=failures,
        all6_candidate_motion_gates=all(r['candidate']['pass_gate'] for r in rows),
        candidate_pooled_within18px=sum(r['candidate']['within18px'] for r in rows),
        primary_outputs=sum(r['candidate']['n'] for r in rows),
        original_late_stop_triggers=sum(r['original_late_stop'] for r in rows),
        candidate_late_stop_triggers=sum(r['candidate_late_stop'] for r in rows),
        late_stop_outputs=sum(r['late_stop_outputs'] for r in rows),
        new_data=False,neural_calls=0,decoder_calls=0,GPU=False,board=False,
        seconds=time.perf_counter()-started,
        limits=['runtime API now additionally requires synchronized current721 sampled input',
            'input veto aids motion confidence, not spatial position; no image tracker or truth access',
            'static-after1sec gate unchanged; first100ms unready is abstention, not confirmed stillness',
            'aliasing/subsampled motion, noisy camera, illumination flicker, unknown input quantization untested',
            'no fresh generalization claim; existing clips cannot be reused as unseen tests']))
    with (HERE/'COMPARISON.csv').open('x',encoding='utf-8-sig',newline='') as f:
        fields=['id','primary_outputs','old_hits','candidate_hits','old_late_stop','candidate_late_stop','late_stop_outputs','old_stop_tail_s','candidate_stop_tail_s']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow(dict(zip(fields,[r['id'],r['candidate']['n'],r['original']['within18px'],r['candidate']['within18px'],r['original_late_stop'],r['candidate_late_stop'],r['late_stop_outputs'],r['original_last_trigger_after_stop_s'],r['candidate_last_trigger_after_stop_s']])))
    print(json.dumps(dict(motion=rows,static=static,tests=tests),indent=2))

if __name__=='__main__':main()
