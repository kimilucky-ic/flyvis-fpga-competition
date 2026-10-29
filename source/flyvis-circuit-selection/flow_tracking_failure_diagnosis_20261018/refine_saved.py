"""One targeted ranking counterfactual plus correct input-geometry check.

Exploratory saved-data diagnosis, NOT a new validation of the frozen tracker.
No torch, network, decoder, GPU, or board code is imported.
"""
from diagnose import *

def nearest_prediction_tracker(flow,threshold,xy,roi,neighbors):
    scores=original.saliency(flow);p=v=None;gaps=0;rows=[]
    for k in range(9,len(flow),10):
        cc=candidates(scores[k],threshold,xy,roi,neighbors)
        prediction=None if p is None else p+v*.05
        eligible=cc if prediction is None else [c for c in cc if np.linalg.norm(c['center']-prediction)<=4]
        if eligible:
            chosen=max(eligible,key=lambda c:c['mass']) if prediction is None else min(
                eligible,key=lambda c:(float(np.linalg.norm(c['center']-prediction)),-c['mass']))
            measurement=chosen['center']
            if p is None:p=measurement.copy();v=np.zeros(2)
            else:
                old=p.copy();p=.8*measurement+.2*prediction
                v=.8*v+.2*(measurement-old)/.05
            gaps=0;rows.append([k,1,*p,*measurement,chosen['mass'],len(chosen['ids'])])
        else:
            rows.append([k,0,np.nan,np.nan,np.nan,np.nan,0,0]);gaps+=1
            if p is not None:p=prediction
            if gaps>=4:p=v=None
    return np.asarray(rows)

def main():
    dump('SUPPLEMENT_PLAN.json',dict(reason='Stage trace showed correct candidates present, energy-ranked association unstable; original zero-background input centroid ignored MP4 white offset.',
        chosen_after_original_diagnosis=True,unseen_validation=False,
        changes='one candidate ranking substitution only; all saliency, calibration,4hex gate,filter,windows,original gates unchanged',
        geometry='subtract actual decoded blank input before estimating disk center; raw1-pixels centroid is biased by non-255 encoded white',
        new_neural_steps=0,GPU=False,script_sha256=sha(__file__)))
    pr=load(OLD/'PREREGISTRATION.json');result=load(HERE/'RESULT.json');grid=np.load(OLD/'GRID.npz')
    xy,roi=grid['xy'],grid['roi'];d=np.linalg.norm(xy[:,None]-xy[None],axis=2)
    neighbors=[np.flatnonzero(np.isclose(d[i],1,atol=1e-8)) for i in range(721)]
    threshold=load(OLD/'CALIBRATION.json')['threshold'];steps=np.arange(9,1000,10)
    blank=np.load(OLD/'inputs/CAL_BLANK.npy').astype(float)
    output=[];examples=[];controls=[]
    for case in pr['cases']:
        name=case['id'];flow=np.load(OLD/'runs'/name/'flow.npy')
        variant=nearest_prediction_tracker(flow,threshold,xy,roi,neighbors)
        np.save(HERE/(name+'_nearest_prediction_counterfactual.npy'),variant)
        if case['kind']!='motion':
            controls.append(dict(id=name,calibration_false_fraction=float(variant[steps>=200,1].mean())));continue
        truth=np.load(OLD/'truth'/(name+'.npz'));pos=truth['position'];vel=truth['velocity']
        pixels=np.load(OLD/'inputs'/(name+'.npy')).astype(float)
        dark=np.maximum(blank-pixels,0)
        sampled_center=(dark[:,:,None]*xy).sum(1)/dark.sum(1)[:,None]
        err=np.linalg.norm(sampled_center-pos,axis=1)
        pred,scores,traces=trace_tracker(flow,threshold,xy,roi,neighbors)
        active=(steps>=200)&(steps<800)
        final_good=np.linalg.norm(pred[:,2:4]-pos[steps],axis=1)<=3
        raw_good=np.linalg.norm(pred[:,4:6]-pos[steps],axis=1)<=3
        oracle_good=np.array([any(np.linalg.norm(c['center']-pos[tr['k']])<=3 for c in tr['groups']) for tr in traces])
        bad=active&~final_good
        categories=dict(fail_count=int(bad.sum()),no_component=int(sum(not tr['groups'] for tr,b in zip(traces,bad) if b)),
            gated_out_despite_good_component=int(sum(tr['chosen'] is None and good for tr,good,b in zip(traces,oracle_good,bad) if b)),
            chosen_wrong_despite_good_component=int(sum(tr['chosen'] is not None and good and not raw for tr,good,raw,b in zip(traces,oracle_good,raw_good,bad) if b)),
            final_filter_only_failure=int(sum(raw and not final for raw,final,b in zip(raw_good,final_good,bad) if b)))
        metrics=evaluate(variant[:,2:4],pos,steps)
        # Compare vectors in moving true disk to renderer-defined direction.
        phase_flow={}
        for phase,select in [('forward_settled',(steps>=240)&(steps<490)),('reverse_settled',(steps>=540)&(steps<790))]:
            vectors=[]
            for k in steps[select]:
                inside=np.linalg.norm(xy-pos[k],axis=1)<=2
                vectors.append(flow[k][:,inside].mean(1))
            phase_flow[phase]=direction_info(np.array(vectors),vel[steps[select]])
        output.append(dict(id=name,corrected_input_geometry=dict(MAE_hex=float(err.mean()),max_hex=float(err.max()),
            MAE_pixels=float(err.mean()*6),blank_pixel_value_range=[float(blank.min()),float(blank.max())],
            explanation='Subtracting decoded blank removes codec white-floor mass; initial geometry metric in RESULT.json is superseded.'),
            failure_categories=categories,nearest_prediction_ranking=metrics,
            true_disk_flow_by_phase=phase_flow))
        # First three settled failures per case, chosen by time, not benefit.
        ids=np.flatnonzero(bad&(steps>=240)&(steps<490))[:3]
        for j in ids:
            tr=traces[j];k=tr['k']
            examples.append(dict(case=name,step=int(k),truth=pos[k],prediction=tr['prediction'],
                selected=None if tr['chosen'] is None else tr['chosen']['center'],
                components=[dict(center=c['center'],mass=c['mass'],
                    prediction_distance=None if tr['prediction'] is None else float(np.linalg.norm(c['center']-tr['prediction'])),
                    truth_distance=float(np.linalg.norm(c['center']-pos[k]))) for c in tr['groups']]))
    dump('REFINED_RESULT.json',clean(dict(status='EXPLORATORY_SAVED_DATA_DIAGNOSIS_NOT_NEW_PASS',
        geometry_metric_correction=True,cases=output,controls=controls,examples=examples,
        neural_steps=0,GPU=False,board=False)))
    # Pairs of failures and good candidate centers for horizontal cases.
    fig,axs=plt.subplots(2,3,figsize=(12,8))
    chosen=[e for e in examples if e['case'] in ['HORIZONTAL','HORIZONTAL_SLOW']]
    for ax,e in zip(axs.flat,chosen):
        k=e['step'];name=e['case'];score=np.load(OLD/'tracking'/(name+'_saliency.npy'))[k]
        ax.scatter(xy[roi,0],xy[roi,1],c=score[roi],cmap='viridis',s=12)
        ax.add_patch(plt.Circle(e['truth'],2,color='limegreen',fill=False,lw=1.7))
        if e['prediction'] is not None:ax.plot(*e['prediction'],'k+',ms=10,label='Previous-state prediction')
        for i,c in enumerate(e['components']):
            ax.plot(*c['center'],'wx',ms=9,mew=2)
            ax.annotate(f"{i}:mass{c['mass']:.1f}",c['center'],fontsize=6)
        if e['selected'] is not None:ax.plot(*e['selected'],'rx',ms=11,mew=2,label='Chosen center')
        ax.set_title(name+f' t={k*.005:.3f}s');ax.set_aspect('equal');ax.set(xlim=(-11,11),ylim=(-11,11))
    fig.suptitle('First three settled failures per horizontal case: existing candidates\nGreen=true disk; white=candidates; red=selected; offline diagnostic only')
    fig.tight_layout();fig.savefig(HERE/'candidate_failures.png',dpi=150);plt.close(fig)
    print(json.dumps(clean(output),indent=2))

if __name__=='__main__':main()
