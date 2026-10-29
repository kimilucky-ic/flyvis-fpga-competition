from core import *

p=check(deep=True);initial=np.load(BUNDLE/'initial_state_full.npy');count=0
freeze=load(HERE/'MODEL_FREEZE.json');assert sha(freeze['path'])==freeze['sha256']
assert load(HERE/'testing/INPUT_GENERATION.json')['time_ns']>freeze['time_ns']
assert load(HERE/'testing/INPUT_GENERATION.json')['model_sha']==freeze['sha256']
for case in load(HERE/'testing/INPUTS.json'):
    assert sha(case['path'])==case['sha256'] and sha(case['video_path'])==case['video_sha256']
    x=np.load(case['path']);root=HERE/'testing/runs'/case['id']
    for mode in ['Full','CNN']+(['Sham'] if (root/'Sham').exists() else []):
        out=root/mode;n=load(out/'VALIDITY.json')['valid_rows'];states=np.load(out/'states_raw.npy',mmap_mode='r')
        rows=(out/'chain.jsonl').read_text(encoding='utf-8').splitlines();assert len(rows)==n
        previous=digest(initial)
        for k,line in enumerate(rows):
            r=json.loads(line);assert r['step']==k and r['old']==previous and r['input']==digest(x[k]) and r['new']==digest(states[k])
            assert r['time']==k*.005 and r['next_time']==(k+1)*.005 and r['committed'] and np.isfinite(states[k]).all()
            if mode=='CNN':assert r['native_H_updates']==0 and r['old_source']=='OWN_LIVE_STATE'
            previous=r['new'];count+=1
        assert np.array_equal(states[n-1],np.load(out/'final.npy'))
idx=dict(np.load(HERE/'training/design_indices.npz'));n=load(HERE/'training/DATA.json')['sensory_rows']
assert set(idx['frame'][idx['frame']<n]).isdisjoint(idx['sensory_validation_frame'])
assert not np.any((idx['frame']>=n+96)&(idx['frame']<n+128))
fit=load(HERE/'training/FIT.json');assert fit['original_H_coefficients_copied'] is False
result=dict(status='PASS_SAVED_SAME_SIZE_CPU_REFINEMENT_EVIDENCE',formal_commits_checked=count,
    model_frozen_before_test_generation=True,training_validation_rows_disjoint=True,
    all_formal_state_and_input_time_chains_checked=True,native_H_production_updates=0,teacher_corrections=0,
    new_neural_steps_in_audit=0,GPU=0,board=0)
dump(HERE/'FINAL_AUDIT.json',result);print(json.dumps(result),flush=True)
