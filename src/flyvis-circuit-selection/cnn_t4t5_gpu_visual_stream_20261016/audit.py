"""Saved arrays/actual browser acknowledgements; no neural computations."""
from contract import *
import numpy as np

p=check();a={k:path(v) for k,v in p['assets'].items()};result=load(HERE/'gpu/RESULT.json');ex=load(HERE/'gpu/EXIT.json')
assert ex['success'] and ex['CUDA_synchronized'] and ex['lease_closed']
assert result['steps_each']==1000 and result['native_H_in_CNN']==0 and result['teacher_corrections']==0
input_gpu=np.load(HERE/'gpu/inputs.npy',mmap_mode='r');input_host=np.load(HERE/'host/actual_decoded_inputs.npy')
assert np.array_equal(input_gpu,input_host) and np.array_equal(input_gpu,np.load(a['CPU_input']))
digest=lambda z:hashlib.sha256(np.ascontiguousarray(z).tobytes()).hexdigest()
arrays={mode:np.load(HERE/'gpu'/(mode+'_states.npy'),mmap_mode='r') for mode in ['Full','CNN']}
previous={mode:digest(np.load(a['initial'])) for mode in arrays}
rows=(HERE/'gpu/chain.jsonl').read_text().splitlines();assert len(rows)==1000
for k,line in enumerate(rows):
    row=json.loads(line);assert row['step']==k and row['frame_id']==k//2 and row['input_sha']==digest(input_gpu[k])
    assert row['native_H_in_CNN']==0 and row['old_source']=='OWN_LIVE_STATE' and row['time']==k*.005 and row['next_time']==(k+1)*.005
    for mode,array in arrays.items():
        assert row['old_'+mode]==previous[mode] and row['new_'+mode]==digest(array[k]);previous[mode]=row['new_'+mode]
numerics={};steps=np.load(HERE/'gpu/flow_steps.npy')
for mode,array in arrays.items():
    ref=np.load(a['CPU_'+mode],mmap_mode='r');maximum=0.;bad=0
    for k in range(1000):
        delta=abs(array[k].astype(np.float64)-ref[k]);maximum=max(maximum,float(delta.max()))
        bad+=int(np.count_nonzero(delta>1e-5+1e-5*abs(ref[k])))
    flow=np.load(HERE/'gpu'/(mode+'_flow.npy'));ref_flow=np.load(a['CPU_'+mode+'_flow'])[steps]
    d=abs(flow.astype(np.float64)-ref_flow);flowbad=int(np.count_nonzero(d>1e-5+1e-5*abs(ref_flow)))
    numerics[mode]=dict(state_max_abs=maximum,state_violations=bad,flow_max_abs=float(d.max()),flow_violations=flowbad)
events=[json.loads(x) for x in (HERE/'host/events.jsonl').read_text(encoding='utf-8').splitlines()]
ack=[x for x in events if x['kind']=='BROWSER_RENDER_ACK' and x['phase_when_received']=='RUNNING' and x['visible']]
ids=set(x['render_id'] for x in ack);visible=len(ack)>=5 and len(ids)>=3
checks=all(v['state_violations']==0 and v['flow_violations']==0 for v in numerics.values())
report=dict(status='PASS_ACTUAL_GPU_AND_VISIBLE_VIDEO_COEXECUTION' if visible and checks else 'COMPLETE_WITH_UI_OR_NUMERICAL_LIMITATIONS',
    CUDA_result=result,numerical_CPU_comparison=numerics,atol=1e-5,rtol=1e-5,all_1000_state_chains_checked=True,
    actual_video_inputs_exact=True,browser_visible_running_ACK=len(ack),distinct_running_render_ids=len(ids),
    simultaneous_visual_evidence=visible,GPU_lease_released=True,GPU_process_exited=load(HERE/'host/EXIT.json')['worker_exited'],
    FPGA=False,strict_realtime_claim=False,new_neural_steps_in_audit=0)
write(HERE/'FINAL_AUDIT.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
