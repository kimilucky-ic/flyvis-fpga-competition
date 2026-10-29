"""One saved-state audit, inherited source checks and live feedback probe."""
from shared import *
start=time.perf_counter();freezecheck(deep=True)
base.check_frozen()  # unchanged original R/decoder/metric and map identities
gate=load(HERE/'TRAINING_GATE.json');assert gate['pass_gate']
identity=load(HERE/'MODEL_FREEZE.json');assert identity['gate_sha']==sha(HERE/'TRAINING_GATE.json')
assert sha(identity['path'])==identity['sha256']
assert identity['time_ns']<(HERE/'TEST_INPUTS.json').stat().st_mtime_ns
assert not list((HERE/'training').glob('bptt_*.pt')),'BPTT was not used in this accepted path'
execution=load(HERE/'TEST_EXECUTION.json');m=mapping();initial=np.load(BUNDLE/'initial_state_full.npy')
all_commits=cnn_commits=0;short_commits=0
for result in execution['records']:
    out=HERE/'test_runs'/result['case']/result['mode'];states=np.load(out/'states.npy',mmap_mode='r')
    case=next(c for c in load(HERE/'TEST_INPUTS.json') if c['id']==result['case'])
    assert sha(case['path'])==case['sha256'];inputs=np.load(case['path'])
    n=result['steps'];assert n==485 and states.shape==(485,45669)
    flow=np.load(out/'flow.npy',mmap_mode='r');assert flow.shape==(485,2,721) and np.isfinite(flow).all()
    lines=(out/'chain.jsonl').read_text().splitlines();assert len(lines)==n
    previous=digest(initial)
    for k,line in enumerate(lines):
        row=json.loads(line)
        assert row['step']==k and row['old']==previous and row['new']==digest(states[k]) and row['input']==digest(inputs[k])
        assert row['time']==k*.005 and row['next_time']==(k+1)*.005 and row['committed']
        assert np.isfinite(states[k]).all()
        if result['mode']=='CNN':assert row['native_H_updates']==0 and row['old_source']=='OWN_LIVE_STATE'
        previous=row['new'];all_commits+=1
    assert previous==digest(np.load(out/'final.npy'))
    if result['mode']=='CNN':
        assert result['native_H_updates']==0 and result['teacher_corrections']==0 and result['CNN_calls']==485
        cnn_commits+=485
short=load(HERE/'short_checks/ridge/RESULT.json')
assert short['pass_gate']
for w in short['records']:
    assert w['pass_gate'] and w['commits']==128 and w['teacher_corrections']==0
    path=HERE/'short_checks/ridge'/(w['id']+'_chain.jsonl')
    lines=path.read_text().splitlines();previous=None
    for k,line in enumerate(lines):
        row=json.loads(line);assert row['step']==k and row['native_H_updates']==0
        if previous is not None:assert row['old']==previous
        previous=row['new'];short_commits+=1
    assert previous==digest(np.load(path.parent/(w['id']+'_final.npy')))
assert all_commits==12125 and cnn_commits==5820 and short_commits==1664
# Same predeclared physical edge path used in the first pilot, with NEW CNN.
model=model_from(identity['path']);cnn=CNNService(model,m);r=r_service()
hnode,rnode=26218,44229;pixels=torch.full((721,),.5);a0=torch.from_numpy(initial.copy())
changed=a0.clone();changed[hnode]=torch.maximum(changed[hnode],torch.tensor(.05))+.1
ra=r.step(a0,pixels,step_id=0,run_id='new_feedback',condition_id='base').activity
rb=r.step(changed,pixels,step_id=0,run_id='new_feedback',condition_id='perturbed_H').activity
aa=a0.clone();bb=a0.clone();aa[m['R']]=ra;bb[m['R']]=rb
returned=float((cnn.step(bb)-cnn.step(aa)).abs().max())
rp=a0.clone();rp[rnode]+=.1
feedback=dict(H=hnode,R=rnode,H_to_R_max=float((rb-ra).abs().max()),
    R_to_CNN_H_max=float((cnn.step(rp)-cnn.step(a0)).abs().max()),H_to_R_to_CNN_H_max=returned)
assert all(feedback[k]>0 for k in ['H_to_R_max','R_to_CNN_H_max','H_to_R_to_CNN_H_max'])
# Direction diagnostics are supplementary; they do not alter any acceptance gate.
uv=m['grid_uv'];center=np.maximum.reduce([abs(uv[0]),abs(uv[1]),abs(uv[0]+uv[1])])<=1
direction=[];central=[];csvrows=[]
results=load(HERE/'RESULTS.json')
for case in load(HERE/'TEST_INPUTS.json'):
    casecentral=[];flows=[]
    for mode in ['Full','CNN']:
        root=HERE/'test_runs'/case['id']/mode;state=np.load(root/'states.npy',mmap_mode='r')
        h=state[:,m['H_grid_ids']][:,:,center];casecentral.append(h)
        flows.append(np.load(root/'flow.npy'))
    central.append(casecentral)
    baseline=flows[0][160:200].mean(0)
    roi=np.load(LANE/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy')
    unit=np.array([np.cos(np.deg2rad(case['angle'])),np.sin(np.deg2rad(case['angle']))])
    for mode,flow in zip(['Full','CNN'],flows):
        val=(flow-baseline)[200:286][:,:,roi];mean=val.mean((0,2))
        direction.append(dict(case=case['id'],mode=mode,mean_vector=mean.tolist(),
            mean_stimulus_projection=float(mean@unit),
            mean_vector_angle_deg=None if np.linalg.norm(mean)<1e-4 else float(np.rad2deg(np.arctan2(mean[1],mean[0]))%360),
            note='supplementary model output diagnostic, not ground-truth direction classification accuracy'))
    rcase=next(z for z in results['records'] if z['case']==case['id'])
    csvrows.append(dict(case=case['id'],variant=case['variant'],H_response_L2=rcase['H_response_relative_L2'],
        flow_E=rcase['flow']['allpost']['field_error_E'],M=rcase['flow']['allpost']['magnitude_ratio'],
        Q=rcase['flow']['allpost']['Q'],field_angle_deg=rcase['flow']['allpost']['angle_deg'],pass_gate=rcase['pass_gate']))
np.savez(HERE/'CENTRAL_T4T5_ACTIVITY.npz',case_ids=np.array([c['id'] for c in load(HERE/'TEST_INPUTS.json')]),
    modes=np.array(['Full','CNN']),types=np.array(TYPES),activity=np.array(central),global_ids=m['H_grid_ids'][:,center])
dump(HERE/'DIRECTION_DIAGNOSTICS.json',direction)
with (HERE/'COMPARISON.csv').open('x',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
dump(HERE/'FINAL_AUDIT.json',dict(status='PASS_SAVED_STATES_AND_FROZEN_GATE',functional=results['status'],
    formal_complete_commits=all_commits,formal_CNN_commits=cnn_commits,training_short_CNN_commits=short_commits,
    full_formal_state_rows_rehashed=True,short_checks='H trajectories + full-state digest chains/final states; not all intermediate R states saved',
    original_H_updates_in_CNN=0,teacher_corrections_in_formal_CNN=0,model_frozen_before_new_inputs=True,
    source_code_unchanged=True,model_parameters=31168,BPTT_updates=0,extra_feedback_R_candidates=2,
    feedback=feedback,new_neural_rollout_steps_in_this_audit=0,wall_s=time.perf_counter()-start,GPU=0,board=0))
print('PASS_FINAL_AUDIT',all_commits,cnn_commits,feedback)
