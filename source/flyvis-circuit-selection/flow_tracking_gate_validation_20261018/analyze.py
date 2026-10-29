"""Predict first, score all preregistered new cases, no post-test tuning."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MPLBACKEND='Agg',PYTHONDONTWRITEBYTECODE='1')
from prepare import *
import importlib.util,csv

def mod(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def score(pred,position,mask):
    k=pred[:,0].astype(int);valid=(pred[:,1]>0)&np.isfinite(pred[:,2:4]).all(1)
    err=np.linalg.norm(pred[:,2:4]-position[k],axis=1);good=mask&valid;n=int(mask.sum());assert n
    e=err[good];median=float(np.median(e)*6) if len(e) else None
    return dict(n=n,valid=int(good.sum()),coverage=float(good.sum()/n),within18px=int((good&(err<=3)).sum()),
        within18px_fraction=float((good&(err<=3)).sum()/n),median_valid_px=median,
        MAE_valid_px=float(e.mean()*6) if len(e) else None,p95_valid_px=float(np.percentile(e,95)*6) if len(e) else None,
        pass_gate=bool(good.sum()/n>=.9 and (good&(err<=3)).sum()/n>=.8 and median is not None and median<=12))

def after_stop(pred,stop):
    t=pred[:,0]*.005;valid=pred[:,1]>0;tail=np.flatnonzero(t>=stop);late=t>=stop+.2
    triggers=tail[valid[tail]];last=int(triggers[-1]) if len(triggers) else None
    quiet=(last+1 if last is not None else int(tail[0])) if len(tail) else len(t)
    return dict(late_outputs=int(late.sum()),late_triggers=int(valid[late].sum()),late_fraction=float(valid[late].mean()),
        last_trigger_delay_s=None if last is None else float(t[last]-stop),
        first_sustained_quiet_delay_s=float(t[quiet]-stop) if quiet<len(t) else None,
        quiet_right_censored=bool(quiet>=len(t)))

def main():
    start=time.perf_counter();p=load(HERE/'PREREGISTRATION.json');frozen=load(HERE/'ALGORITHM_FREEZE.json')
    assert sha(HERE/'PREREGISTRATION.json')==frozen['prereg_sha256']
    for rel,h in p['pins'].items():assert sha(PROJECT/rel)==h,rel
    assert load(HERE/'INPUT_GENERATION.json')['time_ns']>frozen['time_ns']
    execution=load(HERE/'EXECUTION.json');assert execution['neural_steps']==17000 and not execution['GPU']
    gate=mod(HERE/'input_verified_tracker.py','new_frozen_gate');base=mod(PREVIOUS/'tracker.py','original_frozen_tracker')
    g=np.load(LANE/'flow_tracking_pilot_20261018/GRID.npz');xy,roi=g['xy'],g['roi'];cal=dict(np.load(PREVIOUS/'CALIBRATION.npz'))
    (HERE/'predictions').mkdir();preds={};original={};prediction_hashes=[]
    # No truth or trajectory generator is consulted during this pass.
    for c in p['cases']:
        name=c['id'];flow=np.load(HERE/'runs'/name/'flow.npy');x=np.load(HERE/'inputs'/(name+'.npy'))
        pred=gate.run(flow,x,xy,roi,cal);old,_=base.run(flow,xy,roi,cal)
        kept=pred[:,1]>0;assert np.array_equal(pred[kept,2:6],old[kept,2:6]);assert not np.any(kept&~(old[:,1]>0))
        preds[name]=pred;original[name]=old
        np.save(HERE/'predictions'/(name+'.npy'),pred);np.save(HERE/'predictions'/(name+'_without_veto.npy'),old)
        prediction_hashes.append(dict(id=name,sha256=sha(HERE/'predictions'/(name+'.npy'))))
    dump('PREDICTIONS_FROZEN.json',dict(time_ns=time.time_ns(),truth_opened=False,gate_sha256=sha(HERE/'input_verified_tracker.py'),files=prediction_hashes))
    rows=[];controls=[];failures=[];false_events=[];pooled_errors=[]
    perm=np.random.default_rng(2026101804).permutation(721)
    permcal={k:v.copy() for k,v in cal.items()};permcal['background_prefix']=permcal['background_prefix'][:,:,perm];permcal['background_steady']=permcal['background_steady'][:,perm]
    for c in p['cases']:
        name=c['id'];pred=preds[name];old=original[name];steps=pred[:,0].astype(int);t=steps*.005;valid=pred[:,1]>0
        if c['kind']!='motion':
            scored=steps>=200;startup=steps<200
            r=dict(id=name,kind=c['kind'],noise_sigma=c['noise_sigma'],brightness_depth=c['brightness_depth'],
                scored_outputs=int(scored.sum()),triggers=int(valid[scored].sum()),fraction=float(valid[scored].mean()),
                pass_gate=bool(valid[scored].mean()<=.05),without_veto_triggers=int(old[scored,1].sum()),
                startup_outputs=int(startup.sum()),startup_triggers=int(valid[startup].sum()),
                without_veto_startup_triggers=int(old[startup,1].sum()),unknown_outputs=int((pred[:,12]==0).sum()),
                post1s_input_change_fraction=float((pred[scored,11]>0).mean()))
            controls.append(r)
            for j in np.flatnonzero(valid):false_events.append(dict(id=name,step_id=int(steps[j]),input_t=float(t[j]),scored=bool(scored[j]),reason='STATIONARY_SCENE_REPORTED_MOVING_LOCATION'))
            continue
        truth=np.load(HERE/'truth'/(name+'.npz'));pos=truth['position'];active=(t>=c['onset'])&(t<c['stop'])
        metric=score(pred,pos,active);oldmetric=score(old,pos,active)
        flow=np.load(HERE/'runs'/name/'flow.npy');x=np.load(HERE/'inputs'/(name+'.npy'))
        null=gate.run(flow[:,:,perm],x[:,perm],xy,roi,permcal);np.save(HERE/'predictions'/(name+'_spatial_null.npy'),null)
        nm=score(null,pos,active);origin=float(np.mean(np.linalg.norm(pos[steps[active]],axis=1)<=3))
        atstart=float(np.mean(np.linalg.norm(pos[steps[active]]-pos[0],axis=1)<=3))
        pre=t<c['onset'];post=t>=c['stop']+.2
        r=dict(id=name,angle=c['angle'],speed=c['speed'],noise_sigma=c['noise_sigma'],brightness_depth=c['brightness_depth'],
            primary=metric,without_veto_primary=oldmetric,spatial_null=nm,fixed_origin_fraction=origin,
            fixed_initial_target_position_fraction=atstart,stationary_start_baseline_is_descriptive_only=True,
            before_onset_outputs=int(pre.sum()),before_onset_triggers=int(valid[pre].sum()),
            without_veto_before_onset_triggers=int(old[pre,1].sum()),stop=after_stop(pred,c['stop']),without_veto_stop=after_stop(old,c['stop']),
            stopped_input_change_fraction=float((pred[post,11]>0).mean()),primary_vetoed_outputs=int(((old[:,1]>0)&~valid&active).sum()))
        rows.append(r);e=np.linalg.norm(pred[:,2:4]-pos[steps],axis=1);pooled_errors.extend((e[active&valid]*6).tolist())
        for j in np.flatnonzero(active&(~valid|(e>3))):
            failures.append(dict(id=name,step_id=int(steps[j]),input_t=float(t[j]),valid=bool(valid[j]),
                error_px=float(e[j]*6) if valid[j] else None,reason='MISS' if not valid[j] else 'POSITION_OVER18PX'))
        print('SCORED',name,metric['pass_gate'],flush=True)
    normal=float(np.mean([r['primary']['within18px_fraction'] for r in rows]));null=float(np.mean([r['spatial_null']['within18px_fraction'] for r in rows]));origin=float(np.mean([r['fixed_origin_fraction'] for r in rows]))
    passed=all(r['primary']['pass_gate'] for r in rows) and all(r['pass_gate'] for r in controls) and normal-null>=.2 and normal-origin>=.2
    counts=dict(primary_outputs=sum(r['primary']['n'] for r in rows),valid=sum(r['primary']['valid'] for r in rows),within18px=sum(r['primary']['within18px'] for r in rows),
        control_scored_outputs=sum(r['scored_outputs'] for r in controls),control_triggers=sum(r['triggers'] for r in controls),
        late_stop_outputs=sum(r['stop']['late_outputs'] for r in rows),late_stop_triggers=sum(r['stop']['late_triggers'] for r in rows),
        without_veto_late_stop_triggers=sum(r['without_veto_stop']['late_triggers'] for r in rows))
    summary=dict(status='PASS_FROZEN_GATE_NEW_VIDEOS' if passed else 'FAIL_FROZEN_GATE_NEW_VIDEOS',
        motion_passes=sum(r['primary']['pass_gate'] for r in rows),motion_conditions=len(rows),control_passes=sum(r['pass_gate'] for r in controls),control_conditions=len(controls),
        counts=counts,pooled_coverage=counts['valid']/counts['primary_outputs'],pooled_within18px=counts['within18px']/counts['primary_outputs'],
        pooled_valid_MAE_px=float(np.mean(pooled_errors)) if pooled_errors else None,mean_per_condition_within18px=normal,
        mean_null=null,mean_fixed_origin=origin,motion=rows,controls=controls,
        unchanged_algorithm=True,unchanged_gates=True,new_inputs_after_freeze=True,predictions_before_truth_scoring=True,
        no_outcome_exclusions=True,no_retraining=True,analysis_seconds=time.perf_counter()-start,GPU=False,board=False,
        scope='controlled input+FlyVis optical-flow postprocessor; not camera/real-time/biological validation')
    dump('SUMMARY.json',summary);dump('FAILURES.json',dict(motion_events=failures,stationary_scene_emissions=false_events,
        motion_event_count=len(failures),stationary_emission_count=len(false_events),all_conditions_retained=True))
    with (HERE/'MOTION_METRICS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        data=[dict(id=r['id'],speed=r['speed'],**r['primary'],late_stop_fraction=r['stop']['late_fraction'],fixed_start_fraction=r['fixed_initial_target_position_fraction']) for r in rows]
        w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
    with (HERE/'CONTROL_METRICS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=controls[0]);w.writeheader();w.writerows(controls)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['motion','controls']},indent=2))

if __name__=='__main__':main()
