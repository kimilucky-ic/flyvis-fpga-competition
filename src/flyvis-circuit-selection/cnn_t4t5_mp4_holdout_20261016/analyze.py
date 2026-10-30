"""Saved-state analysis only. New local ROI gates are fixed before the run."""
from core import *


def main():
    check(); execution=load(HERE/'EXECUTION.json'); m=ref.mapping(); roi=np.load(ROI_PATH)
    center=np.maximum.reduce([abs(m['grid_uv'][0]),abs(m['grid_uv'][1]),abs(m['grid_uv'].sum(0))])<=1
    columns=['H_RMSE','R_RMSE','H_max','R_max','H_state_nRMSE','R_state_nRMSE','flow_component_RMSE']
    records=[]; central={}; csvrows=[]
    for case in load(HERE/'INPUTS.json'):
        root=HERE/'runs'/case['id']; rr=[load(root/mode/'RESULT.json') for mode in ['Full','CNN']]
        n=min(z['valid_steps'] for z in rr); complete=n==case['steps']
        full,cnn=[np.load(root/mode/'states_raw.npy',mmap_mode='r')[:n] for mode in ['Full','CNN']]
        ff,cf=[np.load(root/mode/'flow.npy',mmap_mode='r')[:n] for mode in ['Full','CNN']]
        step=np.empty((n,7),np.float64)
        for k in range(n):
            hf=full[k,m['H']].astype(np.float64); rf=full[k,m['R']].astype(np.float64)
            dh=cnn[k,m['H']].astype(np.float64)-hf; dr=cnn[k,m['R']].astype(np.float64)-rf
            df=cf[k,:,roi].astype(np.float64)-ff[k,:,roi]
            step[k]=[np.sqrt(np.mean(dh*dh)),np.sqrt(np.mean(dr*dr)),abs(dh).max(),abs(dr).max(),
                np.linalg.norm(dh)/max(np.linalg.norm(hf),1e-12),np.linalg.norm(dr)/max(np.linalg.norm(rf),1e-12),
                np.sqrt(np.mean(df*df))]
        np.save(root/'STEP_ERRORS.npy',step); dump(root/'STEP_COLUMNS.json',columns)
        central[case['id']+'_Full']=full[:,m['H_grid_ids'][:,center]]
        central[case['id']+'_CNN']=cnn[:,m['H_grid_ids'][:,center]]
        row=dict(case=case['id'],group=case['group'],background=case.get('background'),local=case.get('local',False),
            complete=complete,compared_steps=n,final_full_state_max_error=float(abs(cnn[-1].astype(np.float64)-full[-1]).max()) if n else None,
            maximum_step_H_RMSE=float(step[:,0].max()) if n else None,maximum_step_R_RMSE=float(step[:,1].max()) if n else None)
        if not complete: row.update(status='FAIL_INCOMPLETE',pass_gate=False,windows={})
        elif case['group']=='static':
            windows={}
            for name,(start,stop) in case['windows'].items():
                z=step[start:stop]; h,r,flow=[float(np.sqrt(np.mean(z[:,i]**2))) for i in [0,1,6]]
                windows[name]=dict(H_absolute_RMSE=h,R_absolute_RMSE=r,flow_component_absolute_RMSE=flow,
                    pass_gate=bool(h<=.002 and r<=.002 and flow<=.002),model_units=True)
            passed=all(v['pass_gate'] for v in windows.values())
            row.update(status='PASS_STATIC_NUMERIC_GATE' if passed else 'FAIL_STATIC_NUMERIC_GATE',pass_gate=passed,windows=windows)
        else:
            windows=score_motion(case,full[:,m['H']],cnn[:,m['H']],ff,cf,roi,m)
            eligible=[]; failed_eligible=False
            for value in windows.values():
                sources=[value['flow']]+([value['foreground_flow']] if 'foreground_flow' in value else [])
                valid=bool(value['H_reference_response_rms']>=1e-6 and all(z['reference_eligible'] for z in sources))
                eligible.append(valid)
                failed_eligible=bool(failed_eligible or (valid and not value['pass_gate']))
            passed=all(v['pass_gate'] for v in windows.values())
            status='PASS_FUNCTIONAL_GATE' if passed else 'FAIL_FUNCTIONAL_GATE' if failed_eligible else 'NOT_ALL_WINDOWS_EVALUABLE'
            row.update(status=status,pass_gate=passed,windows=windows,all_references_eligible=all(eligible))
        records.append(row)
        print(json.dumps(dict(stage='ANALYZED',case=case['id'],status=row['status'])),flush=True)
        for name,value in row['windows'].items():
            for scope in ['flow','foreground_flow'] if 'flow' in value else ['static']:
                if scope=='foreground_flow' and scope not in value: continue
                v=value.get(scope,{})
                csvrows.append(dict(case=case['id'],window=name,scope=scope,status=row['status'],
                    H_response_L2=value.get('H_response_relative_L2'),E=v.get('field_error_E'),M=v.get('magnitude_ratio'),Q=v.get('Q'),
                    field_angle_deg=v.get('angle_deg'),eligible=v.get('reference_eligible'),
                    H_absolute_RMSE=value.get('H_absolute_RMSE'),R_absolute_RMSE=value.get('R_absolute_RMSE'),
                    flow_absolute_RMSE=value.get('flow_component_absolute_RMSE'),window_pass=value['pass_gate']))
    np.savez(HERE/'CENTRAL_ACTIVITY.npz',global_ids=m['H_grid_ids'][:,center],**central)
    first=load(HERE/'INPUTS.json')[0]['id']; root=HERE/'runs'/first
    same=np.array_equal(np.load(root/'Full/states_raw.npy',mmap_mode='r'),np.load(root/'Sham/states_raw.npy',mmap_mode='r'))
    flowdiff=float(abs(np.load(root/'Full/flow.npy')-np.load(root/'Sham/flow.npy')).max())
    summary=dict(status='PASS_ALL_PREREGISTERED_GATES' if all(r['pass_gate'] for r in records) else 'COMPLETED_WITH_LIMITATIONS_OR_FAILURES',
        passed=sum(r['pass_gate'] for r in records),total=len(records),records=records,
        by_group={g:dict(passed=sum(r['pass_gate'] for r in records if r['group']==g),total=sum(r['group']==g for r in records)) for g in ['motion','static']},
        Sham_all_states_bitwise_equal=same,Sham_flow_max_abs_difference=flowdiff,model_sha=sha(MODEL),model_parameters=31168,
        training_updates=0,GPU=0,board=0,actual_neural_wall_s=execution['wall_s'],actual_commits=execution['valid_commits'])
    dump(HERE/'SUMMARY.json',summary)
    with (HERE/'METRICS.csv').open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(csvrows[0])); writer.writeheader(); writer.writerows(csvrows)


if __name__=='__main__': main()
