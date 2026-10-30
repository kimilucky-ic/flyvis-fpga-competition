"""One bounded saved-data audit. No neural recomputation."""
import json
import numpy as np
from experiment import HERE,PRIOR,load,dump,check_frozen,digest_array
from video_io import sha
from direction_readout import features

check_frozen()
frozen=load(HERE/'FROZEN_READOUTS.json')
for filename,digest in frozen['readouts'].items():assert sha(HERE/filename)==digest
cases=load(HERE/'CASES.json')
clip_hash={c['id']:c['sha256'] for c in load(HERE/'VIDEO_MANIFEST.json')}
models={n:dict(np.load(HERE/'models'/n/'model.npz')) for n in ['Full','a_r4']}
readout_ids={n:np.load(HERE/'models'/n/'readout_local_ids.npy') for n in models}
types={n:np.load(HERE/'models'/n/'readout_type_index.npy') for n in models}
initial={n:np.load(HERE/'initial'/n/'initial_state.npy') for n in models}
records=[]
for spec in cases:
    cid=spec['id'];assert sha(HERE/'videos'/f'{cid}.mp4')==clip_hash[cid]
    inputs={n:np.load(HERE/'runs'/n/cid/'input.npy') for n in models}
    assert np.array_equal(inputs['a_r4'],inputs['Full'][:,models['a_r4']['input_hex_global_index']])
    for n in models:
        path=HERE/'runs'/n/cid;result=load(path/'result.json')
        journal=[json.loads(line) for line in (path/'steps.jsonl').read_text().splitlines()]
        assert len(journal)==400
        prior=digest_array(initial[n]);last_state=np.load(path/'final_state.npy')
        states=np.load(path/'states.npy',mmap_mode='r') if n=='a_r4' else None
        roi=np.load(path/'roi.npy')
        assert np.isfinite(roi).all() and np.isfinite(last_state).all()
        if states is not None:
            assert states.shape==(400,3865) and np.isfinite(states).all()
            assert np.array_equal(roi,states[:,readout_ids[n]])
        for k,entry in enumerate(journal):
            assert entry['step']==k and entry['old_sha256']==prior and entry['commit']=='COMMITTED'
            assert entry['input_sha256']==digest_array(inputs[n][k])
            assert abs(entry['time_s']-k*.005)<1e-12 and abs(entry['new_time_s']-(k+1)*.005)<1e-12
            if states is not None:assert entry['new_sha256']==digest_array(states[k])
            prior=entry['new_sha256']
        assert prior==digest_array(last_state)
        assert np.array_equal(features(roi,types[n]),np.load(path/'features.npy'))
        assert result['full_network_future_state_reads']==result['external_neural_input']==0
        assert result['model_sha']==sha(HERE/'models'/n/'model.npz')
        records.append(dict(model=n,clip=cid,commits=400,chain_and_inputs=True,all_states_saved_and_rehashed=n=='a_r4'))
    if spec['split']=='heldout':assert (HERE/'runs/a_r4'/cid/'result.json').stat().st_mtime_ns>=frozen['time_ns']
portable=HERE/'portable_check';original=HERE/'runs/a_r4/T_ON_022.5_v12'
assert np.array_equal(np.load(portable/'states.npy'),np.load(original/'states.npy'))
assert np.array_equal(np.load(portable/'initial_state.npy'),initial['a_r4'])
assert np.array_equal(np.load(portable/'input.npy'),np.load(original/'input.npy'))
accepted=[r for r in load(HERE/'PREDICTIONS.json') if r['branch']=='a_r4/shared' and r['clip']=='T_ON_022.5_v12'][0]
portable_result=load(portable/'result.json')
assert portable_result['prediction']['angle_deg']==accepted['angle_deg']
package=load(HERE/'portable_a_r4/PACKAGE_MANIFEST.json')
for name,record in package.items():assert sha(HERE/'portable_a_r4'/name)==record['sha256']
assert sha(HERE/'models/a_r4/model.npz')==sha(PRIOR/'models/a_r4/model.npz')
assert sha(HERE/'models/Full/model.npz')==sha(PRIOR/'models/CALIBRATION_FULL/model.npz')
assert sha(HERE/'independent_model.py')==sha(PRIOR/'independent_model.py')
assert sha(PRIOR/'DELIVERY_MANIFEST.json')==load(HERE/'PREREGISTRATION.json')['source_model_manifest_sha']
design=load(HERE/'DESIGN_EXECUTION.json');held=load(HERE/'HELDOUT_EXECUTION.json')
dump(HERE/'FINAL_AUDIT.json',dict(status='PASS_SAVED_DATA_AND_PORTABLE_VIDEO',
    clips=76,scientific_runs=152,movie_commits=60800,initial_warmup_steps=400,portable_steps=600,total_new_neural_steps=61800,
    original_model_and_core_bytes_unchanged=True,readouts_frozen_before_heldout=True,
    same_video_and_local_input_subset=True,portable_states_input_a0_prediction_bitwise_match=True,
    portable_result=portable_result['prediction'],state_chain_records=records,
    Full_evidence_limit='all step chains/inputs and final state verified; only central56 Full activities saved, not all Full intermediate states',
    no_neural_recompute_in_audit=True,GPU_runs=0,official_decoder_frames=0,hardware_operations=0,
    times=dict(design_s=design['wall_s'],heldout_s=held['wall_s'],portable_s=portable_result['time_s'])))
print(json.dumps(dict(status='PASS_SAVED_DATA_AND_PORTABLE_VIDEO',clips=76,scientific_runs=152,portable_prediction=portable_result['prediction'])))
