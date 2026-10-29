"""Saved-state audit and declared normalized metrics; zero neural recomputation."""
import time
from common import *

start=time.perf_counter();check_frozen();mapping=read_mapping()
execution=load(HERE/'EXECUTION.json');freeze=load(HERE/'MODEL_FREEZE.json')
assert sha(HERE/'training/cnn.pt')==freeze['sha256']
assert freeze['test_used'] is False
initial=np.load(BUNDLE/'initial_state_full.npy');commits=0;cnn_commits=0;records=[]
for result in execution['results']:
    root=HERE/'runs'/result['case']/result['mode'];n=result['steps']
    state=np.load(root/'states.npy',mmap_mode='r');flow=np.load(root/'flow.npy',mmap_mode='r')
    lines=(root/'steps.jsonl').read_text().splitlines();assert len(lines)==n and flow.shape==(n,2,721)
    case=next(c for c in load(HERE/'TEST_CASES.json') if c['id']==result['case'])
    inputs=np.load(case['path']);previous=digest(initial)
    for k,line in enumerate(lines):
        r=load_line=json.loads(line)
        assert r['step']==k and r['old']==previous and r['new']==digest(state[k]) and r['input']==digest(inputs[k])
        assert r['time']==k*.005 and r['next_time']==(k+1)*.005 and r['committed']
        assert np.isfinite(state[k]).all()
        if result['mode']=='CNN':assert r['native_H_updates']==0 and r['old_source']=='OWN_LIVE_STATE'
        previous=r['new'];commits+=1
    assert digest(np.load(root/'final_state.npy'))==previous
    if result['mode']=='CNN':
        assert result['original_H_updates']==0 and result['CNN_truth_corrections']==0
        cnn_commits+=n
    if n<485:
        # Preserve the raw preallocated failed-attempt file. Export a separate,
        # exact-length activity array so unwritten storage can never be mistaken
        # for a completed or zero-filled continuation.
        np.save(root/'committed_states.npy',np.asarray(state[:n]))
    dump(root/'VALIDITY.json',dict(valid_steps=n,raw_preallocated_shape=list(state.shape),
        activity_file='states.npy' if n==485 else 'committed_states.npy',
        uncommitted_raw_rows=None if n==485 else [n,484],uncommitted_rows_never_decoded=True,
        no_padding_no_fallback=True))
    reference=np.load(HERE/'runs'/result['case']/'Full/states.npy',mmap_mode='r')[:n]
    if result['mode']!='Full':
        normalized=[]
        for k in range(n):
            diff=state[k].astype(np.float64)-reference[k].astype(np.float64)
            def value(ids):return float(np.linalg.norm(diff[ids])/max(np.linalg.norm(reference[k,ids].astype(np.float64)),1e-12))
            normalized.append(dict(step=k,H_nRMSE=value(mapping['H']),R_nRMSE=value(mapping['R']),
                definition='RMSE(error)/RMS(same-step Full state); not baseline-subtracted response error'))
        dump(root/'NORMALIZED_STEP_ERRORS.json',normalized)
    records.append(dict(case=result['case'],mode=result['mode'],valid_steps=n,complete=result['complete']))
assert commits==sum(r['steps'] for r in execution['results']) and cnn_commits==3794
# All original edge IDs included by R-only are precisely the complement of
# H-targeted edges. This validates source/partition identity, not a new rollout.
r=r_service();_,_,_,p=source()
expected=np.flatnonzero(~np.isin(p['target_global'],mapping['H']))
assert np.array_equal(r.original_edge_ids,expected) and len(expected)==1079351
cal=load(HERE/'SOURCE_CPU_CALIBRATION.json');faults=load(HERE/'FAULT_AND_FEEDBACK.json')
assert cal['status']=='PASS' and all(f['state_unchanged'] for f in faults['faults'])
offline=[]
for one in load(HERE/'ONE_STEP_ONLY_DIAGNOSTIC.json'):
    ref=np.load(HERE/'runs'/one['case']/'Full/states.npy',mmap_mode='r')[:,mapping['H']]
    old=np.concatenate([initial[mapping['H']][None],ref[:-1]],axis=0)
    drms=float(np.sqrt(np.mean((ref.astype(np.float64)-old.astype(np.float64))**2)))
    offline.append(dict(case=one['case'],teacher_forced_RMSE=one['RMSE'],true_increment_RMS=drms,
        error_over_increment_RMS=one['RMSE']/max(drms,1e-12)))
dump(HERE/'ONE_STEP_NORMALIZED.json',offline)
# Fixed central56 readout and signed opposite-direction contrast, not biological DSI.
uv=mapping['grid_uv'];center=np.maximum.reduce([abs(uv[0]),abs(uv[1]),abs(uv[0]+uv[1])])<=1
direction=[]
for polarity in ['ON','OFF']:
    for mode in ['Full','CNN','HOLD']:
        responses=[]
        for angle in [0,180]:
            case=f'{polarity}{angle}_base';root=HERE/'runs'/case/mode;count=load(root/'RESULT.json')['steps']
            activity=np.load(root/'states.npy',mmap_mode='r')[:count,mapping['H_grid_ids']][:,:,center].astype(np.float64)
            # Even failed399-step run has complete pre and primary windows.
            baseline=activity[160:200].mean(0)
            responses.append(np.maximum(activity[200:286]-baseline,0).max(0).mean(1))
        for i,t in enumerate(TYPES):
            a,b=float(responses[0][i]),float(responses[1][i])
            direction.append(dict(polarity=polarity,mode=mode,type=t,response0=a,response180=b,
                signed_opposite_contrast=(a-b)/max(a+b,1e-12),
                definition='positive peak over primary window after own prebaseline; fixed center7 per type; not DSI across all directions'))
dump(HERE/'DIRECTION_RESPONSE.json',direction)
dump(HERE/'FINAL_AUDIT.json',dict(status='PASS_SAVED_EXECUTION_AND_IDENTITY',wall_s=time.perf_counter()-start,
    checked_complete_state_commits=commits,checked_CNN_commits=cnn_commits,CNN_native_H_updates=0,CNN_teacher_corrections=0,
    R_targets=39901,R_only_edges=len(expected),H_target_edges_evaluated_in_CNN=0,all_valid_rows_rehashed=True,
    partial_attempt='OFF180_base/CNN:399 valid steps, step399 candidate refused; remaining preallocated rows excluded, exact-length export created',
    source_and_model_frozen=True,source_calibration=cal,negative_tests=len(faults['faults']),feedback=faults['feedback'],
    runs=records,new_neural_steps=0,GPU=0,board=0,functional_status=load(HERE/'RESULTS.json')['status']))
print('PASS_SAVED_EXECUTION_AND_IDENTITY',commits,cnn_commits)
