"""Re-decode MP4 input custody, then use accepted saved-state auditor unchanged."""
from core import *
import video_io

start_video=time.perf_counter(); check(deep=True); sampling=dict(np.load(HERE/'SAMPLER.npz')); video_records=[]
assert load(HERE/'FREEZE.json')['time_ns']<(HERE/'INPUTS.json').stat().st_mtime_ns
for case in load(HERE/'INPUTS.json'):
    assert sha(case['video_path'])==case['video_sha256'] and sha(case['path'])==case['sha256']
    value,metadata=video_io.decode(case['video_path'],sampling)
    assert np.array_equal(value,np.load(case['path']))
    saved=load(HERE/'inputs'/(case['id']+'_time.json'))
    assert saved['video_frame_ids']==metadata['video_frame_ids'] and saved['input_times']==metadata['input_times']
    assert metadata['video_frame_ids']==np.repeat(np.arange(500),2).tolist()
    assert metadata['input_times']==(np.arange(1000)*DT).tolist() and metadata['output_times']==((np.arange(1000)+1)*DT).tolist()
    video_records.append(dict(case=case['id'],actual_MP4_redecode_equal=True,frames=500,points=721,
                              model_steps=1000,causal_frame_map=True))
dump(HERE/'VIDEO_INPUT_AUDIT.json',dict(status='PASS_ACTUAL_VIDEO_TO_COMMON_INPUT',records=video_records,
    wall_s=time.perf_counter()-start_video,frames_redecoded=5000,new_neural_steps=0,GPU=0))
execute_accepted_audit(globals())
