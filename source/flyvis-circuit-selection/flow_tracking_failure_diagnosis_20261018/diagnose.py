"""CPU saved-data diagnosis only. Never imports a neuron/decoder implementation.

Ground truth is used to evaluate and construct explicitly ORACLE diagnostics,
not supplied to ordinary candidate extraction or counterfactual locators.
"""
from pathlib import Path
import hashlib,importlib.util,json,csv,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'flow_tracking_pilot_20261018'
spec=importlib.util.spec_from_file_location('frozen_flow_readout',OLD/'readout.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(name,d):
    with (HERE/name).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False)

def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
    if isinstance(x,(np.integer,)):return int(x)
    return x

def evaluate(pred,truth,steps):
    valid=np.isfinite(pred).all(1);err=np.linalg.norm(pred-truth[steps],axis=1)
    sel=(steps>=200)&(steps<800)
    def one(s):
        good=s&valid;e=err[good]
        return dict(n=int(s.sum()),valid=int(good.sum()),coverage=float(good.sum()/s.sum()),
            within3=float(np.sum(good&(err<=3))/s.sum()),
            median=float(np.median(e)) if len(e) else None,MAE=float(np.mean(e)) if len(e) else None,
            penalized_MAE=float(np.where(valid,err,20)[s].mean()))
    return dict(primary=one(sel),forward=one((steps>=240)&(steps<490)),
        reverse=one((steps>=540)&(steps<790)))

def candidates(s,threshold,xy,roi,neighbors):
    mask=np.zeros(721,bool);mask[roi]=s[roi]>=max(threshold,.5*s[roi].max())
    result=[]
    for ids in original.components(mask,neighbors):
        mass=s[ids].sum()
        if mass>0:result.append(dict(mass=float(mass),center=(s[ids,None]*xy[ids]).sum(0)/mass,ids=ids))
    return result

def trace_tracker(flow,threshold,xy,roi,neighbors):
    scores=original.saliency(flow);p=v=None;gaps=0;rows=[];pred=[]
    for k in range(9,len(flow),10):
        groups=candidates(scores[k],threshold,xy,roi,neighbors)
        prediction=None if p is None else p+v*.05
        eligible=groups if prediction is None else [c for c in groups if np.linalg.norm(c['center']-prediction)<=4]
        chosen=max(eligible,key=lambda c:c['mass']) if eligible else None
        if chosen is not None:
            measurement=chosen['center']
            if p is None:p=measurement.copy();v=np.zeros(2)
            else:
                old=p.copy();p=.8*measurement+.2*prediction
                v=.8*v+.2*(measurement-old)/.05
            gaps=0;pred.append([k,1,*p,*measurement,chosen['mass'],len(chosen['ids'])])
        else:
            pred.append([k,0,np.nan,np.nan,np.nan,np.nan,0,0]);gaps+=1
            if p is not None:p=prediction
            if gaps>=4:p=v=None
        rows.append(dict(k=k,groups=groups,eligible=eligible,chosen=chosen,
            prediction=None if prediction is None else prediction.copy()))
    return np.asarray(pred),scores,rows

def raw_difference(flow,lag):
    f=flow.astype(float);out=np.zeros((len(f),721))
    out[lag:]=np.linalg.norm(f[lag:]-f[:-lag],axis=1)
    return out

def instantaneous_locator(scores,threshold,xy,roi,neighbors):
    pred=np.full((100,2),np.nan)
    for j,k in enumerate(range(9,1000,10)):
        cc=candidates(scores[k],threshold,xy,roi,neighbors)
        if cc:pred[j]=max(cc,key=lambda c:c['mass'])['center']
    return pred

def direction_info(vector,velocity):
    norm=np.linalg.norm(vector,axis=1);speed=np.linalg.norm(velocity,axis=1)
    valid=(norm>1e-8)&(speed>0)
    error=np.abs((np.degrees(np.arctan2(vector[valid,1],vector[valid,0])-np.arctan2(velocity[valid,1],velocity[valid,0]))+180)%360-180)
    return dict(valid=int(valid.sum()),MAE_deg=float(error.mean()) if len(error) else None,
                within30=float(np.mean(error<=30)) if len(error) else None,
                mean_model_vector_norm=float(norm[valid].mean()) if valid.any() else None)

def lag_diagnostic(pred,truth,steps):
    # Positive lag: predicted current position resembles an older true position.
    # Comparison to future truth for negative lag is ORACLE diagnostic only.
    good=np.isfinite(pred).all(1)&(((steps>=280)&(steps<450))|((steps>=580)&(steps<750)))
    lags=np.arange(-80,81,10)
    values=[float(np.sqrt(np.mean(np.sum((pred[good]-truth[steps[good]-lag])**2,axis=1)))) for lag in lags]
    best=int(np.argmin(values))
    return dict(scope='ORACLE_TIME_ALIGNMENT_NOT_ONLINE_CORRECTION',lag_s=float(lags[best]*.005),
        RMS_at_best=float(values[best]),RMS_at_zero=float(values[8]),
        lags_s=(lags*.005).tolist(),RMS=values)

def main():
    start=time.perf_counter();pr=load(OLD/'PREREGISTRATION.json');oldsummary=load(OLD/'SUMMARY.json')
    assert sha(OLD/'PREREGISTRATION.json')==load(OLD/'FREEZE.json')['sha256']
    manifest=load(OLD/'DELIVERY_MANIFEST.json');pins={r['path'].replace('\\','/'):r['sha256'] for r in manifest['files']}
    paths=['readout.py','PREREGISTRATION.json','GRID.npz','CALIBRATION.json','SUMMARY.json','EXECUTION.json']
    for c in pr['cases']:
        paths.extend(['runs/'+c['id']+'/flow.npy','inputs/'+c['id']+'.npy','truth/'+c['id']+'.npz','tracking/'+c['id']+'.npy'])
    for rel in paths:assert sha(OLD/rel)==pins[rel],rel
    dump('SOURCE_IDENTITY.json',dict(source=str(OLD),source_manifest_sha256=sha(OLD/'DELIVERY_MANIFEST.json'),
        verified={rel:pins[rel] for rel in paths},neural_steps=0))
    plan=dict(scope='Saved flow/state/input data CPU diagnosis; original gates unchanged',
        hypotheses=['input/coordinate/time mismatch','decoded flow motion direction and spatial support',
                    'saliency component/centroid error','association selection/gate','smoothing bias and memory'],
        fixed_counterfactuals=['original selected centroid without final smoothing','largest component without association/smoothing',
            '100ms difference without50ms EMA, largest component','20ms difference without EMA, largest component'],
        calibration='same controls-only 3*q.999 formula independently per score, no motion labels',
        oracle='nearest detected component to truth, truth-masked flow directions, temporal lag scan[-.4,.4] at.05s; never online',
        immutable_scoring='all[200,800), plus original forward/reverse settled windows; no retuned functional PASS',
        warning='slow case changes both speed and path extent, so not a pure speed ablation',
        max_new_neural_steps=0,GPU=False,board=False,script_sha256=sha(__file__))
    dump('DIAGNOSTIC_PLAN.json',plan)
    g=np.load(OLD/'GRID.npz');xy,roi=g['xy'],g['roi'];d=np.linalg.norm(xy[:,None]-xy[None],axis=2)
    neighbors=[np.flatnonzero(np.isclose(d[i],1,atol=1e-8)) for i in range(721)]
    threshold=load(OLD/'CALIBRATION.json')['threshold'];steps=np.arange(9,1000,10)
    flows={c['id']:np.load(OLD/'runs'/c['id']/'flow.npy') for c in pr['cases']}
    thresholds={}
    for lag in [20,4]:
        scores=np.stack([raw_difference(flows[c['id']],lag)[200:,roi] for c in pr['cases'][:2]])
        thresholds[lag]=max(1e-5,float(np.quantile(scores,.999))*3)
    cases=[];saved={};frame_rows=[]
    for case in pr['cases'][2:]:
        name=case['id'];flow=flows[name];truthfile=np.load(OLD/'truth'/(name+'.npz'))
        truth,velocity=truthfile['position'],truthfile['velocity']
        old=np.load(OLD/'tracking'/(name+'.npy'));reproduced,scores,traces=trace_tracker(flow,threshold,xy,roi,neighbors)
        assert np.allclose(old,reproduced,atol=0,rtol=0,equal_nan=True),'TRACE_REPRODUCTION '+name
        pixels=np.load(OLD/'inputs'/(name+'.npy')).astype(float)
        dark=1-pixels;input_center=(dark[:,:,None]*xy).sum(1)/dark.sum(1)[:,None]
        input_err=np.linalg.norm(input_center-truth,axis=1)
        raw=old[:,4:6];filtered=old[:,2:4]
        largest=np.full_like(raw,np.nan);oracle=np.full_like(raw,np.nan);peak=np.empty_like(raw)
        stage_counts=dict(no_components=0,all_components_gated_out=0,association_chose_worse_than_largest=0,
            oracle_centroid_within3_but_selected_not=0,final_filter_turns_hit_to_miss=0,
            final_filter_turns_miss_to_hit=0,original_bad_frames=0,any_component_overlaps_true_disk=0,
            any_component_centroid_within3=0)
        ordinary=[];foreground=[];annulus=[];bg=[];aligned_bias=[];largest_bias=[]
        for j,tr in enumerate(traces):
            k=tr['k'];cc=tr['groups'];true=truth[k]
            peak[j]=xy[roi[np.argmax(scores[k,roi])]]
            if cc:
                largest[j]=max(cc,key=lambda c:c['mass'])['center']
                oracle[j]=min(cc,key=lambda c:np.linalg.norm(c['center']-true))['center']
            r=np.linalg.norm(xy-true,axis=1);inside=r<=2;ring=(r>=4)&(r<=8)
            # Raw vector in the true disk: diagnostic use of GT, no locator input.
            foreground.append(flow[k][:,inside].mean(1));ordinary.append(flow[k][:,r<=3].mean(1))
            residual=flow[k].astype(float)-flows['CAL_BLANK'][k]
            mag=np.linalg.norm(residual,axis=0)
            annulus.append([mag[inside].mean(),mag[ring].mean(),float(scores[k,inside].sum()/max(scores[k,roi].sum(),1e-12)),
                float(np.mean(inside[roi]))])
            bg.append(residual[:,inside].mean(1))
            active=200<=k<800
            if not active:continue
            raw_e=float(np.linalg.norm(raw[j]-true));final_e=float(np.linalg.norm(filtered[j]-true))
            large_e=float(np.linalg.norm(largest[j]-true));oracle_e=float(np.linalg.norm(oracle[j]-true))
            chosen=tr['chosen'];cause='SUCCESS'
            if not cc:stage_counts['no_components']+=1;cause='NO_COMPONENT'
            elif chosen is None:stage_counts['all_components_gated_out']+=1;cause='ALL_GATED'
            elif not final_e<=3:cause='POSITION_ERROR'
            if not final_e<=3:stage_counts['original_bad_frames']+=1
            if chosen is not None and raw_e>large_e+1e-9:stage_counts['association_chose_worse_than_largest']+=1
            if oracle_e<=3 and not raw_e<=3:stage_counts['oracle_centroid_within3_but_selected_not']+=1
            if raw_e<=3 and not final_e<=3:stage_counts['final_filter_turns_hit_to_miss']+=1
            if final_e<=3 and not raw_e<=3:stage_counts['final_filter_turns_miss_to_hit']+=1
            if any(np.any(np.linalg.norm(xy[c['ids']]-true,axis=1)<=2) for c in cc):stage_counts['any_component_overlaps_true_disk']+=1
            if oracle_e<=3:stage_counts['any_component_centroid_within3']+=1
            vv=velocity[k]/np.linalg.norm(velocity[k]);perp=np.array([-vv[1],vv[0]])
            if chosen is not None:aligned_bias.append([(raw[j]-true)@vv,(raw[j]-true)@perp])
            if np.isfinite(largest[j]).all():largest_bias.append([(largest[j]-true)@vv,(largest[j]-true)@perp])
            frame_rows.append(dict(case=name,step=k,phase='forward' if k<500 else 'reverse',
                final_error=final_e,raw_error=raw_e,largest_error=large_e,oracle_error=oracle_e,
                component_count=len(cc),eligible_count=len(tr['eligible']),reason=cause))
        proposed={'original':filtered,'selected_raw_no_final_filter':raw,'largest_no_association_or_filter':largest,
            'diff100ms_no_EMA_locator':instantaneous_locator(raw_difference(flow,20),thresholds[20],xy,roi,neighbors),
            'diff20ms_no_EMA_locator':instantaneous_locator(raw_difference(flow,4),thresholds[4],xy,roi,neighbors),
            'ORACLE_nearest_component':oracle,'peak_original_saliency':peak}
        scored={n:evaluate(pos,truth,steps) for n,pos in proposed.items()}
        # Cross-check unchanged baseline against the already sealed summary.
        old_row=next(c for c in oldsummary['cases'] if c['id']==name)['primary']
        assert np.isclose(scored['original']['primary']['within3'],old_row['within3_fraction'])
        active=(steps>=200)&(steps<800);settled=((steps>=240)&(steps<490))|((steps>=540)&(steps<790))
        fore=np.asarray(foreground);wide=np.asarray(ordinary);res=np.asarray(bg);ann=np.asarray(annulus)
        one=dict(id=name,input_geometry_check=dict(MAE_hex=float(input_err.mean()),max_hex=float(input_err.max()),
            end_state_time_vs_input='flow[k] post Euler at(k+1)dt; scored against input[k] center; unchanged original convention'),
            stages=stage_counts,readout_diagnostics=scored,
            true_location_raw_flow=dict(primary=direction_info(fore[active],velocity[steps[active]]),
                settled=direction_info(fore[settled],velocity[steps[settled]]),
                primary_radius3=direction_info(wide[active],velocity[steps[active]]),
                blank_subtracted_primary=direction_info(res[active],velocity[steps[active]])),
            spatial_response=dict(blank_subtracted_mean_disk_magnitude=float(ann[active,0].mean()),
                blank_subtracted_mean_annulus_magnitude=float(ann[active,1].mean()),
                mean_disk_to_annulus_ratio=float(ann[active,0].mean()/ann[active,1].mean()),
                mean_original_saliency_fraction_in_true_disk=float(ann[active,2].mean()),
                mean_disk_ROI_area_fraction=float(ann[active,3].mean())),
            selected_centroid_error_motion_axes=dict(mean_along_hex=float(np.mean(np.asarray(aligned_bias)[:,0])),
                mean_cross_hex=float(np.mean(np.asarray(aligned_bias)[:,1]))),
            lags=dict(selected_raw=lag_diagnostic(raw,truth,steps),filtered=lag_diagnostic(filtered,truth,steps)))
        cases.append(one);saved[name]=dict(truth=truth,steps=steps,positions=proposed,score=scores)
        np.savez(HERE/(name+'_stages.npz'),steps=steps,truth=truth[steps],**proposed)
    dump('RESULT.json',clean(dict(status='SAVED_DATA_DIAGNOSIS_COMPLETE_NOT_TRACKER_VALIDATION',cases=cases,
        counterfactual_calibration_thresholds=thresholds,original_threshold=threshold,
        neural_steps=0,GPU=False,board=False,wall_s=time.perf_counter()-start)))
    with (HERE/'FRAME_DIAGNOSIS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=frame_rows[0]);writer.writeheader();writer.writerows(frame_rows)
    flat=[]
    for c in cases:
        for variant,row in c['readout_diagnostics'].items():flat.append(dict(case=c['id'],variant=variant,**row['primary']))
    with (HERE/'STAGE_METRICS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=flat[0]);writer.writeheader();writer.writerows(flat)
    fig,axs=plt.subplots(4,2,figsize=(13,13),sharex=True)
    for i,(name,data) in enumerate(saved.items()):
        t=data['steps']*.005;truth=data['truth'][data['steps']]
        for j in range(2):
            ax=axs[i,j];ax.plot(t,truth[:,j],color='black',lw=1.7,label='Ground truth (diagnosis only)')
            for label,color in [('original','crimson'),('selected_raw_no_final_filter','darkorange'),
                ('largest_no_association_or_filter','royalblue')]:
                ax.plot(t,data['positions'][label][:,j],'.-',ms=2,lw=.7,color=color,label=label)
            ax.axvspan(1,4,color='green',alpha=.05);ax.axvline(2.5,color='gray',ls=':')
            ax.set_title(name+(' x' if j==0 else ' y'));ax.set_ylabel('Neighbor spacings')
    axs[0,0].legend(fontsize=7);fig.suptitle('Frozen predictions: optical-flow locator vs final tracker\nSaved CPU data only; stage removals are diagnostic, not held-out validation')
    fig.tight_layout();fig.savefig(HERE/'stage_timecourses.png',dpi=150);plt.close(fig)
    print(json.dumps(clean([{ 'case':c['id'],'stages':c['stages'],
        'flow':c['true_location_raw_flow']['primary'],'results':{k:v['primary'] for k,v in c['readout_diagnostics'].items()},
        'lag':{k:v['lag_s'] for k,v in c['lags'].items()}} for c in cases]),indent=2))

if __name__=='__main__':main()
