"""Bounded saved-data audit. Does not execute any neural steps."""
import time
from pathlib import Path
import numpy as np
from study import HERE,source,load,dump,digest,validate_frozen,feature_set,predict,old_predict,evaluate
from video_io import sha

start=time.perf_counter()
validate_frozen()
mapping=dict(np.load(HERE/'READOUT_MAP.npz'))
readouts=load(HERE/'READOUTS.json'); receipt=load(HERE/'READOUT_FREEZE.json')
assert sha(HERE/'READOUTS.json')==receipt['sha256']
design=load(HERE/'EXECUTION_design.json'); test=load(HERE/'EXECUTION_test.json')
assert design['time_ns']<receipt['time_ns']<test['time_ns']-test['wall_s']*1e9
assert design['steps']==43200 and test['steps']==52800
cases=load(HERE/'CASES.json'); manifest={r['id']:r['sha256'] for r in load(HERE/'VIDEO_MANIFEST.json')}
ar_pixels=np.load(source/'models/a_r4/model.npz')['input_hex_global_index']
initial={n:np.load(source/'initial'/n/'initial_state.npy') for n in ['Full','a_r4']}
step_count=0; complete=0; maxnorm=0
for c in cases:
    assert sha(HERE/'videos'/(c['id']+'.mp4'))==manifest[c['id']]
    inputs={}
    for name in ['Full','a_r4']:
        root=HERE/'runs'/c['split']/name/c['id']
        inputs[name]=np.load(root/'input.npy');activity=np.load(root/'activity488.npy')
        assert activity.shape==(400,488) and np.isfinite(activity).all()
        fs=np.load(root/'features.npz');derived=feature_set(activity,mapping)
        for key in derived:assert np.array_equal(fs[key],derived[key])
        states=np.load(root/'states.npy',mmap_mode='r') if name=='a_r4' else None
        if states is not None:
            assert states.shape==(400,3865) and np.isfinite(states).all()
            assert np.array_equal(activity,states[:,mapping[name]])
        previous=digest(initial[name]);lines=(root/'steps.jsonl').read_text().splitlines();assert len(lines)==400
        import json
        for k,line in enumerate(lines):
            r=json.loads(line); assert r['k']==k and r['old']==previous
            assert r['input']==digest(inputs[name][k])
            assert r['t_old']==k*.005 and r['t_new']==(k+1)*.005
            if states is not None:assert r['new']==digest(states[k])
            previous=r['new'];step_count+=1
        final=np.load(root/'final_state.npy');assert digest(final)==previous and np.isfinite(final).all()
        maxnorm=max(maxnorm,float(abs(final).max()));complete+=1
    assert np.array_equal(inputs['a_r4'],inputs['Full'][:,ar_pixels])
predictions=load(HERE/'PREDICTIONS.json');case_map={c['id']:c for c in cases}
for row in predictions:
    c=case_map[row['case']];p=row['probe']
    f=np.load(HERE/'runs/test'/row['model']/c['id']/'features.npz')[p]
    pr=old_predict(f,readouts[p]) if p=='legacy8' else predict(f,readouts[p])
    for k,v in pr.items():assert row[k]==v
    for k,v in evaluate(pr,c).items():assert row[k]==v
assert len(predictions)==660 and step_count==96000 and complete==240
dump(HERE/'FINAL_AUDIT.json',dict(status='PASS_EXECUTION_IDENTITY_AND_SAVED_DATA',new_neural_steps=0,
    checked_new_experiment_neural_steps=step_count,checked_model_runs=complete,predictions_recomputed=660,
    frozen_sources_unchanged=True,readout_frozen_before_test=True,input_subset_bitwise=True,
    all_120_A_R4_full_trajectories_rehashed=True,Full_saved='488 matched T4/T5 trajectories and complete final state plus full-state digest chain; NOT all intermediate full-network states',
    no_future_or_external_neural_state_input=True,maximum_final_state_abs=maxnorm,wall_s=time.perf_counter()-start,
    claim='Execution PASS is separate from preregistered functional gate',GPU=0,hardware_operations=0))
print('PASS_EXECUTION_IDENTITY_AND_SAVED_DATA 240 runs / 96000 steps; audit neural steps=0')
