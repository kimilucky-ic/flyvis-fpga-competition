"""Bounded saved-array checks; no re-execution of neurons or readout fitting."""
import json
import numpy as np
from p0_study import HERE,source,check,load,dump,digest
from video_io import sha
from direction_readout import features

check();cases=load(HERE/'CASES.json');load(HERE/'EXECUTION.json')
pins=load(HERE/'PREREGISTRATION.json')['source_pins']
video_hashes={x['id']:x['sha256'] for x in load(HERE/'VIDEO_MANIFEST.json')}
with np.load(source/'models/a_r4/model.npz') as d:input_ids=d['input_hex_global_index']
params={n:dict(initial=np.load(source/'initial'/n/'initial_state.npy'),
    roi=np.load(source/'models'/n/'readout_local_ids.npy'),types=np.load(source/'models'/n/'readout_type_index.npy')) for n in ['Full','a_r4']}
records=[]
for case in cases:
    cid=case['id'];assert sha(HERE/'videos'/(cid+'.mp4'))==video_hashes[cid]
    inputs={n:np.load(HERE/'runs'/n/cid/'input.npy') for n in params}
    assert np.array_equal(inputs['a_r4'],inputs['Full'][:,input_ids])
    for n,p in params.items():
        path=HERE/'runs'/n/cid
        roi=np.load(path/'roi.npy');feat=np.load(path/'features.npy');final=np.load(path/'final_state.npy')
        assert np.array_equal(features(roi,p['types']),feat)
        assert np.isfinite(roi).all() and np.isfinite(final).all()
        states=np.load(path/'states.npy',mmap_mode='r') if n=='a_r4' else None
        if states is not None:assert np.array_equal(states[:,p['roi']],roi) and np.isfinite(states).all()
        history=[json.loads(x) for x in (path/'steps.jsonl').read_text().splitlines()]
        assert len(history)==400;old=digest(p['initial'])
        for k,r in enumerate(history):
            assert r['step']==k and r['old']==old and r['input']==digest(inputs[n][k])
            assert abs(r['time']-k*.005)<1e-12 and abs(r['next_time']-(k+1)*.005)<1e-12
            if states is not None:assert r['new']==digest(states[k])
            old=r['new']
        assert old==digest(final)
        records.append(dict(model=n,clip=cid,steps=400,chain_and_input_pass=True,all_neural_states_verified=n=='a_r4'))
    assert (HERE/'runs/a_r4'/cid/'result.json').stat().st_mtime_ns>load(HERE/'FREEZE_RECEIPT.json')['time_ns']
rows=load(HERE/'PREDICTIONS.json');paired=[]
for branch in ['Full/shared','a_r4/shared','a_r4/own']:
    groups={g:[r for r in rows if r['branch']==branch and r['group']==g] for g in ['reference_timing','local_center','local_minus2','local_plus2']}
    for a,b,meaning in [('reference_timing','local_center','aperture/shape change at center'),('local_center','local_minus2','translation holding aperture shape and crossing time'),('local_center','local_plus2','translation holding aperture shape and crossing time')]:
        for ra,rb in zip(groups[a],groups[b]):
            assert ra['truth_angle_deg']==rb['truth_angle_deg'] and ra['polarity']==rb['polarity']
            paired.append(dict(branch=branch,reference_group=a,changed_group=b,interpretation=meaning,
                truth_angle_deg=ra['truth_angle_deg'],polarity=ra['polarity'],
                reference_hit=ra['direction_hit_30'],changed_hit=rb['direction_hit_30'],
                penalized_error_change_deg=rb['penalized_error_deg']-ra['penalized_error_deg']))
dump(HERE/'PAIRED_SPATIAL_EFFECTS.json',paired)
dump(HERE/'FINAL_AUDIT.json',dict(status='PASS_FROZEN_P0_EXECUTION_AND_SAVED_DATA',
    scientific_status='see SUMMARY.json; execution pass does not imply generalization pass',
    clips=80,runs=160,new_neural_steps=64000,initialization='exact prior own-gray a0 only',
    source_and_readouts_unchanged=True,all_a_r4_states_verified=True,Full_intermediate_state_scope='56 ROI + input and full-state digest chains + final state',
    readout_refits=0,threshold_or_window_changes=0,new_GPU_runs=0,hardware_operations=0,records=records))
print(json.dumps(dict(status='PASS_FROZEN_P0_EXECUTION_AND_SAVED_DATA',runs=160,steps=64000)))
