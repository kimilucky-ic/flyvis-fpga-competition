"""All preregistered populations/windows, signed float64 analysis; no node selection."""
import csv,time
from common import *

NAMES=['B_T5c','A_T4c','C_T4T5_all_centers']
WINDOWS=dict(primary=(200,485),motion=(200,286),post=(286,485))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def norm_metrics(u,v,floor):
    ru,rv=rms(u),rms(v);resolved=ru>10*floor
    return dict(Full_direction_RMS=ru,direction_floor=floor,resolved=resolved,S=float(np.sum(v*u)/np.sum(u*u)) if resolved else None,
        E=rms(v-u)/ru if resolved else None,cosine=float(np.sum(v*u)/np.sqrt(np.sum(v*v)*np.sum(u*u))) if resolved and rv>10*floor else None)

def main():
    out=HERE/'artifacts/formal_analysis'
    if out.exists():raise SystemExit('Preserve analysis')
    out.mkdir(parents=True);started=time.monotonic();spec=load(HERE/'spec_snapshot/spec_config.json');meta=load(BUNDLE/'screen_manifest.json')
    full=np.load(host_path(meta['Full_reference_path'])/'activities_full.npy',mmap_mode='r')
    rois={key:np.load(HERE/'spec_snapshot'/host_path(v['path']).name) for key,v in spec['readouts'].items()}
    nodes=list(csv.DictReader((BUNDLE/'nodes_full.csv').open(encoding='utf-8')))
    assert [int(row['global_node_index']) for row in nodes]==list(range(45669))
    types=np.array([row['cell_type'] for row in nodes]);timegrid=np.load(BUNDLE/'time.npy');initial=np.load(BUNDLE/'initial_state_full.npy')
    # eta is fixed from Full alone, not from intervention outcomes.
    eta=1e-5+1e-5*np.max(np.abs(full),axis=(0,1)).astype(np.float64);np.save(out/'eta_Full.npy',eta)
    directions=[];responses=[];aux=[];twocontrast=[];feedback=[];validity=[];summaries=[];predrift=[]
    with np.load(BUNDLE/'expanded_parameters.npz') as z:edges={key:z[key] for key in ['source_global','target_global','effective_weight']}
    for name in NAMES:
        h=HUpdater(BUNDLE/'candidates'/name/'static_boundary_gpu_native.npz');r=np.setdiff1d(np.arange(45669),h.h_ids)
        candidate=spec['candidates'][name];direct=np.load(HERE/'spec_snapshot'/(name+'_direct_R_targets.npy'))
        groups=dict(H=h.h_ids,R=r,full=np.arange(45669),own_direct_R=direct,**rois)
        with np.load(BUNDLE/'candidates'/name/'validated_partition_ids.npz') as z:rh=z['RH'].copy();hr=z['HR'].copy()
        rh_source=edges['source_global'][rh];rh_target=np.searchsorted(h.h_ids,edges['target_global'][rh]);rh_w=edges['effective_weight'][rh]
        for repeat in ['formal_r1','formal_r2']:
            base=HERE/'artifacts'/repeat/name;sham=np.load(base/'Sham/activities_full.npy',mmap_mode='r');ab=np.load(base/'Ablation/activities_full.npy',mmap_mode='r')
            dest=out/repeat/name;dest.mkdir(parents=True)
            traces=[];stepstats=[];local_summary=[]
            for c,condition in enumerate(spec['fixture']['conditions']):
                for comparison,left,right in [('Ablation-Sham',ab,sham),('Sham-Full',sham,full)]:
                    drift=left[c,160:200].astype(np.float64).mean(axis=0)-right[c,160:200].astype(np.float64).mean(axis=0)
                    for group,ids in groups.items():predrift.append(dict(repeat=repeat,candidate=name,condition=c,comparison=comparison,group=group,baseline_mean_delta=float(np.mean(drift[ids])),baseline_max_abs_delta=float(np.max(np.abs(drift[ids]))),baseline_RMSE_delta=rms(drift[ids])))
                changed=np.zeros(45669,bool);maxnode=np.zeros(45669,np.float64);comparison_accum={kind:{g:dict(abs_sum=0.,square_sum=0.,max_abs=0.,changed=np.zeros(len(ids),bool)) for g,ids in groups.items()} for kind in ['Ablation-Sham','Sham-Full']}
                rh_rows=[]
                for k in range(485):
                    a=ab[c,k].astype(np.float64);s=sham[c,k].astype(np.float64);f=full[c,k].astype(np.float64)
                    for comparison,delta in [('Ablation-Sham',a-s),('Sham-Full',s-f)]:
                        for group,ids in groups.items():
                            d=delta[ids];acc=comparison_accum[comparison][group];acc['abs_sum']+=np.abs(d).sum();acc['square_sum']+=np.square(d).sum();acc['max_abs']=max(acc['max_abs'],float(np.max(np.abs(d))));acc['changed']|=np.abs(d)>eta[ids]
                            stepstats.append(dict(repeat=repeat,candidate=name,condition=c,polarity=condition['polarity'],angle=condition['angle'],step_id=k,state_before_time=float(timegrid[k]),state_after_time=float(timegrid[k]+.005),comparison=comparison,group=group,n_nodes=len(ids),
                                max_abs=float(np.max(np.abs(d))),MAE=float(np.mean(np.abs(d))),RMSE=rms(d),nodes_above_eta=int((np.abs(d)>eta[ids]).sum())))
                    if k<200:assert np.array_equal(ab[c,k],sham[c,k])
                    if k==200:assert np.array_equal(ab[c,k,h.h_ids],sham[c,k,h.h_ids])
                    assert np.isfinite(a).all() and np.isfinite(s).all()
                    assert np.all(np.abs(s-f)<=1e-5+1e-5*np.abs(f))
                    delta=a-s;maxnode[:]=np.maximum(maxnode,np.abs(delta));changed|=np.abs(delta)>eta
                    olda=initial if k==0 else ab[c,k-1]
                    olds=initial if k==0 else sham[c,k-1]
                    jrha=rh_w*np.maximum(olda[rh_source],np.float32(0));jrhs=rh_w*np.maximum(olds[rh_source],np.float32(0))
                    ca=np.zeros(len(h.h_ids),np.float32);cs=np.zeros_like(ca);np.add.at(ca,rh_target,jrha);np.add.at(cs,rh_target,jrhs)
                    rd=ca.astype(np.float64)-cs.astype(np.float64)
                    rh_rows.append(dict(condition=c,step_id=k,live_RH_current_difference_max=float(np.max(np.abs(rd))),live_RH_current_difference_RMSE=rms(rd),
                        live_R_boundary_activity_difference_max=float(np.max(np.abs(olda[h.source_ids].astype(np.float64)-olds[h.source_ids].astype(np.float64)))),
                        H_new_difference_max=float(np.max(np.abs(delta[h.h_ids]))),R_new_difference_max=float(np.max(np.abs(delta[r])))))
                write_csv(dest/f'condition_{c:02d}_live_feedback.csv',rh_rows);np.save(dest/f'condition_{c:02d}_A_minus_S_per_node_max.npy',maxnode)
                for comparison,table in comparison_accum.items():
                    for group,acc in table.items():
                        ids=groups[group];left=ab[c,-1] if comparison=='Ablation-Sham' else sham[c,-1];right=sham[c,-1] if comparison=='Ablation-Sham' else full[c,-1];final=left[ids].astype(np.float64)-right[ids].astype(np.float64)
                        row=dict(repeat=repeat,candidate=name,condition=c,polarity=condition['polarity'],angle=condition['angle'],comparison=comparison,group=group,n_nodes=len(ids),steps=485,
                            max_abs=acc['max_abs'],MAE=float(acc['abs_sum']/(485*len(ids))),RMSE=float(np.sqrt(acc['square_sum']/(485*len(ids)))),nodes_ever_above_eta=int(acc['changed'].sum()),
                            final_max_abs=float(np.max(np.abs(final))),final_MAE=float(np.mean(np.abs(final))),final_RMSE=rms(final),final_nodes_above_eta=int((np.abs(final)>eta[ids]).sum()))
                        aux.append(row);local_summary.append(row)
                feedback.append(dict(repeat=repeat,candidate=name,condition=c,first_R_change_step=next((q['step_id'] for q in rh_rows if q['R_new_difference_max']>0),None),
                    first_RH_current_change_step=next((q['step_id'] for q in rh_rows if q['live_RH_current_difference_max']>0),None),
                    first_H_change_step=next((q['step_id'] for q in rh_rows if q['H_new_difference_max']>0),None),
                    first_H_intervention_step_unchanged=rh_rows[200]['H_new_difference_max']==0,
                    max_live_RH_current_difference=max(q['live_RH_current_difference_max'] for q in rh_rows),
                    HR_positive=int((edges['effective_weight'][hr]>0).sum()),HR_negative=int((edges['effective_weight'][hr]<0).sum()),HR_zero=int((edges['effective_weight'][hr]==0).sum())))
            write_csv(dest/'all_population_step_differences.csv',stepstats);write_csv(dest/'all_population_summary.csv',local_summary)
            # Main direction axis is immutable Full; concatenate the two polarities.
            for group in ['primary_visual_readout','common_direct_downstream_R']:
                ids=groups[group];data={m:np.asarray(v[:,:,ids],dtype=np.float64) for m,v in dict(Full=full,Sham=sham,Ablation=ab).items()}
                z={m:a-a[:,160:200].mean(axis=1,keepdims=True) for m,a in data.items()}
                vectors={m:{pol:z[m][pair[0],200:]-z[m][pair[1],200:] for pol,pair in spec['primary_metric']['polarity_pairs'].items()} for m in z}
                for m in vectors:vectors[m]['JOINT']=np.concatenate([vectors[m]['OFF'],vectors[m]['ON']],axis=0)
                for polarity in ['OFF','ON','JOINT']:
                    for mode in ['Full','Sham','Ablation']:
                        metric=norm_metrics(vectors['Full'][polarity],vectors[mode][polarity],rms(4*eta[ids]))
                        shmetric=norm_metrics(vectors['Full'][polarity],vectors['Sham'][polarity],rms(4*eta[ids]))
                        s=metric['S'];classification='UNRESOLVED_BASELINE' if s is None else ('direction_reversal' if s<0 else 'direction_enhancement' if s>1 else 'direction_weakening')
                        if mode=='Full':classification='REFERENCE'
                        if mode=='Sham':classification='NUMERICAL_CONTROL'
                        directions.append(dict(repeat=repeat,candidate=name,population=group,n_nodes=len(ids),polarity=polarity,mode=mode,**metric,one_minus_S=1-s if s is not None else None,
                            S_minus_Sham=s-shmetric['S'] if s is not None else None,classification=classification,
                            RMS_A_minus_S=float(rms(np.concatenate([data['Ablation'][c,200:]-data['Sham'][c,200:] for c in ([0,2] if polarity=='OFF' else [1,3] if polarity=='ON' else [0,1,2,3])],axis=0))),
                            RMS_S_minus_F=float(rms(np.concatenate([data['Sham'][c,200:]-data['Full'][c,200:] for c in ([0,2] if polarity=='OFF' else [1,3] if polarity=='ON' else [0,1,2,3])],axis=0))),eta_RMS=rms(eta[ids])))
                for c,condition in enumerate(spec['fixture']['conditions']):
                    den=rms(z['Full'][c,200:]);floor=rms(2*eta[ids]);num=rms(data['Ablation'][c,200:]-data['Sham'][c,200:])
                    responses.append(dict(repeat=repeat,candidate=name,condition=c,population=group,response_RMS_Full=den,response_floor=floor,RMS_A_minus_S=num,normalized_response_change=num/den if den>10*floor else None,resolved=den>10*floor))
            readouts={g:groups[g] for g in ['primary_visual_readout','common_R_T4_T5','all_8_T4_T5_centers','all_65_centers']}
            for ct in ['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd']:
                readouts['all_type_'+ct]=np.flatnonzero(types==ct)
                readouts['common_R_type_'+ct]=np.intersect1d(readouts['all_type_'+ct],groups['common_R'])
            for node in groups['all_65_centers']:readouts['center_'+str(node)+'_'+str(types[node])]=np.array([node])
            for ct in np.unique(types[h.h_ids]):readouts['H_type_'+str(ct)]=h.h_ids[types[h.h_ids]==ct]
            for group,ids in readouts.items():
                pop_eta=rms(eta[ids]);q={}
                for mode,array in dict(Full=full,Sham=sham,Ablation=ab).items():
                    a=np.asarray(array[:,:,ids],dtype=np.float64);baselevel=a[:,160:200].mean(axis=1);z=a-baselevel[:,None,:];meantrace=z.mean(axis=2)
                    for c,condition in enumerate(spec['fixture']['conditions']):
                        for k in range(485):traces.append(dict(condition=c,step_id=k,state_after_time=float(timegrid[k]+.005),mode=mode,group=group,signed_mean_response=float(meantrace[c,k])))
                        for window,(lo,hi) in WINDOWS.items():
                            response=z[c,lo:hi];mean=float(response.mean());q[mode,c,window]=mean
                            responses.append(dict(repeat=repeat,candidate=name,condition=c,population=group,window=window,mode=mode,n_nodes=len(ids),
                                H_members=int(np.isin(ids,h.h_ids).sum()),R_members=int(np.isin(ids,r).sum()),signed_mean_response=mean,
                                signed_AUC=float(.005*np.sum(response,axis=0).mean()),absolute_AUC=float(.005*np.sum(np.abs(response),axis=0).mean()),
                                max_excitation_shift=float(np.max(response)),min_inhibition_shift=float(np.min(response)),baseline_mean=float(baselevel[c].mean())))
                    for polarity,pair in spec['primary_metric']['polarity_pairs'].items():
                        for window in WINDOWS:
                            q0,q180=q[mode,pair[0],window],q[mode,pair[1],window];den=abs(q0)+abs(q180)
                            twocontrast.append(dict(repeat=repeat,candidate=name,population=group,mode=mode,polarity=polarity,window=window,q0=q0,q180=q180,signed_mean_difference=q0-q180,
                                two_angle_contrast=(q0-q180)/den if den>10*4*pop_eta else None,denominator=den,minimum_denominator=10*4*pop_eta,H_members=int(np.isin(ids,h.h_ids).sum())))
            write_csv(dest/'signed_readout_traces.csv',traces)
            validity.append(dict(repeat=repeat,candidate=name,status='PASS_SHAM_AND_ONSET_ALL_NODE_GATES',pre_Ablation_Sham_bitwise=True,first_H_after_200_bitwise=True))
            print('ANALYZED',repeat,name,flush=True)
    # Mixed row schemas intentionally normalized before CSV.
    def unioncsv(path,rows):
        keys=list(dict.fromkeys(k for row in rows for k in row));write_csv(path,[{k:row.get(k) for k in keys} for row in rows])
    write_csv(out/'direction_metrics.csv',directions);unioncsv(out/'signed_response_and_normalization_metrics.csv',responses)
    write_csv(out/'prebaseline_drift.csv',predrift)
    write_csv(out/'two_angle_contrast_metrics.csv',twocontrast);write_csv(out/'all_condition_population_differences.csv',aux);write_csv(out/'live_feedback_summary.csv',feedback)
    for name in NAMES:
        select=lambda repeat,pol:next(row for row in directions if row['repeat']==repeat and row['candidate']==name and row['population']=='primary_visual_readout' and row['polarity']==pol and row['mode']=='Ablation')
        first=select('formal_r1','JOINT');row=dict(candidate=name,n_H=spec['candidates'][name]['n_H'],HH=spec['candidates'][name]['partition_counts']['HH'],HR=spec['candidates'][name]['partition_counts']['HR'],
            V_joint_S=first['S'],V_joint_E=first['E'],V_joint_cosine=first['cosine'])
        eligible=[]
        for pol in ['OFF','ON']:
            a,b=select('formal_r1',pol),select('formal_r2',pol)
            metric_repeat=abs(a['S']-b['S'])<=.01 and abs(a['E']-b['E'])<=.01 if a['S'] is not None and b['S'] is not None else False
            qualifies=all(q['resolved'] and (abs(1-q['S'])>=.20 or q['E']>=.20) and q['RMS_A_minus_S']>10*max(q['RMS_S_minus_F'],q['eta_RMS']) for q in [a,b]) and metric_repeat
            eligible.append(qualifies);row.update({f'V_{pol}_S':a['S'],f'V_{pol}_E':a['E'],f'V_{pol}_classification':a['classification'],f'{pol}_effect_branch':qualifies})
        rrows=[a for a in aux if a['repeat']=='formal_r1' and a['candidate']==name and a['group']=='R' and a['comparison']=='Ablation-Sham']
        row.update(R_max_abs_change=max(a['max_abs'] for a in rrows),R_changed_nodes_max=max(a['nodes_ever_above_eta'] for a in rrows),effect_branch=any(eligible),
            coverage_branch='COVERAGE_INSUFFICIENT_HISTORICAL_TARGET_DIRECTION',extension_execution='REQUIRES_ARCHITECT_USER_REVIEW')
        summaries.append(row)
    write_csv(out/'three_candidate_function_comparison.csv',summaries)
    dump(out/'result.json',dict(status='PASS_PRE_REGISTERED_METRIC_ANALYSIS',candidates=summaries,numerical_gates=validity,spec_sha256=load(HERE/'PRE_RUN_REGISTRATION.json')['spec_sha256'],
        code_sha256=file_hash(Path(__file__)),wall_s=time.monotonic()-started,FPGA_execution=False,biological_significance_test=False,DSI_or_preferred_direction_estimated=False))
    seal(out);print(json.dumps(summaries,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
