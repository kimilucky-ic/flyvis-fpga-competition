"""Read-only audit of saved operator R10 and R9 records. No board/network/process launch."""
from pathlib import Path
import sys,json,hashlib,statistics as st
import numpy as np
P=Path(__file__).resolve().parent;B=P.parent;R10=B/'ov5640_live_r10_20261025';R9=B/'ov5640_live_r9_board_20261025'
sys.path.insert(0,str(R10/'bundle'))
from live_protocol import Store
sha=lambda b:hashlib.sha256(b).hexdigest()
source_files=[p for root in (R9/'pc/records',R10/'pc/records') for p in root.rglob('*') if p.is_file()]
before={str(p):sha(p.read_bytes()) for p in source_files}
S={n:Store(root/'pc/records',json.loads((root/'pc/session.json').read_text())) for n,root in [('R9',R9),('R10',R10)]}
s=S['R10'];assert len(s.meta)==32 and s.camera_close['status']=='CLOSED'
audit=R10/'pc/records/audit';a=json.loads((audit/'RESULT.json').read_text());commands=json.loads((audit/'COMMANDS.json').read_text())
assert a['status']=='PASS_ALL_SAVED_STATES' and a['mismatch_words']==0
prev=sha((R10/'bundle/initial_state.bin').read_bytes());mismatches=0
for cmd in commands:
 first=cmd['first_step'];n=cmd['steps'];assert cmd['initial_expected_sha256']==prev and cmd['returncode']==0
 expected=(audit/('%06d_expected.bin'%first)).read_bytes();assert len(expected)==n*182676
 actual_inputs=b''
 for j in range(n):
  k=first+j;meta,source,rec=s.read(k);assert source is None
  exp=expected[j*182676:(j+1)*182676];mismatches+=int(np.count_nonzero(np.frombuffer(exp,'<u4')!=np.frombuffer(rec.state_bits,'<u4')))
  assert sha(rec.input_bits)==a['rows'][k]['input_sha256'] and sha(exp)==a['rows'][k]['expected_state_sha256']
  actual_inputs+=rec.input_bits
 assert actual_inputs==(audit/('%06d_inputs.bin'%first)).read_bytes()
 prev=sha(expected[-182676:])
assert mismatches==0
for n in ('edges.bin','meta.hex'):assert (audit/'oracle_bundle'/n).read_bytes()==(R10/'bundle'/n).read_bytes()
sel=[k for k in range(32) if k not in (0,4,16)]
def stats(values):return dict(mean=st.mean(values),median=st.median(values),minimum=min(values),maximum=max(values),sum=sum(values))
runs={}
for name,store in S.items():
 f=store.final;c=f['context'];ts=f['packet_timings'];loop=(c['PHASE_CHECK_COMPLETE.json']['monotonic_ns']-c['PHASE_BOUNDED_CAPTURE_AND_STEPS.json']['monotonic_ns'])/1e6
 phase={key:stats([ts['%06d'%k][key] for k in sel]) for key in ts['000001'] if key.endswith('_ms')}
 residual=[ts['%06d'%k]['bridge_step_and_ram_record_ms']-sum(ts['%06d'%k][x] for x in ('capture_and_cache_ms','ps_mapping_ms','input_upload_step_and_publication_ms','ddr_copy_and_cache_ms')) for k in sel]
 phase['unseparated_bridge_residual_ms']=stats(residual)
 runs[name]=dict(run_id=f['run_id'],boot_id=f['boot_id'],steps=32,matched29_phase_ms=phase,whole_loop_ms=loop,whole_loop_ms_per_step=loop/32,whole_loop_steps_per_s=32000/loop,final_flush=c['RAM_FLUSH.json'],loop_plus_flush_ms=loop+c['RAM_FLUSH.json']['flush_ms'])
f=s.final;c=f['context'];ts=f['packet_timings'];worker={key:stats([t[key] for t in f['worker_timings'].values()]) for key in f['worker_timings']['000000']}
transfer={key:stats([v[key]*1000 for v in f['transfer_timings'].values()]) for key in ('rebuild_seconds','round_trip_seconds')}
reconcile={key:sum(t[key] for t in ts.values()) for key in ('whole_iteration_ms','between_iterations_ms','console_output_ms','pacing_ms','full_iteration_before_pacing_ms')}
reconcile['worker_drain_ms']=c['LOOP_TAIL.json']['worker_drain_ms']
reconcile['unseparated_boundary_ms']=runs['R10']['whole_loop_ms']-reconcile['whole_iteration_ms']-reconcile['between_iterations_ms']-reconcile['worker_drain_ms']
traces={}
for k in (4,16):
 t=c['CAMERA_CALLTREE_%06d.json'%k];assert not t['truncated']
 absent={word:not any(word in name for name in t['functions']) for word in ('default_memory','mem_dict',':wait')}
 traces[str(k)]=dict(total_ms=t['total_ms'],functions=t['functions'],absent=absent)
 assert absent['default_memory'] and absent['mem_dict']
assert c['CAMERA_MEMORY_FINAL.json']['frame_allocations']==32 and not c['CAMERA_MEMORY_FINAL.json']['failed']
assert c['NEURAL_AFTER.json']=={'0x10':46,'0x14':32,'0x18':0,'0x24':0}
def change(old,new):return dict(old=old,new=new,time_reduction_percent=(1-new/old)*100,speed_ratio=old/new)
comparison=dict(whole_loop=change(runs['R9']['whole_loop_ms'],runs['R10']['whole_loop_ms']))
for key in ('full_iteration_before_pacing_ms','capture_and_cache_ms','input_721_mmio_write_ms','ps_mapping_ms'):
 comparison[key]=change(runs['R9']['matched29_phase_ms'][key]['mean'],runs['R10']['matched29_phase_ms'][key]['mean'])
assert all(sha(Path(p).read_bytes())==h for p,h in before.items())
result=dict(status='PASS_SAVED_OPERATOR_R10_32_ALL_STATES_AND_CLOSE',evidence='READ_ONLY_SAVED_OPERATOR_PHYSICAL_RUN_RECORDS',state_words=1461408,mismatch_words=0,source_mapping_independently_audited=False,clock_physically_measured=False,steps=32,runs=runs,comparison=comparison,worker_all32_ms=worker,transfer_all32_ms=transfer,loop_reconciliation_ms=reconcile,camera_memory_final=c['CAMERA_MEMORY_FINAL.json'],camera_trace_checks={k:dict(total_ms=v['total_ms'],absent=v['absent']) for k,v in traces.items()},camera_close_ms=s.camera_close['close_duration_ms'],source_file_count_rehashed_unchanged=len(before),agent_board_operations=0,network_operations=0,oracle_rerun=False,limitations=['same29 ordinals excludes startup0 and diagnostic4,16; different live stimuli, not controlled repeated benchmark','worker and network timings overlap producer; do not add to whole step','print duration is wall time including possible thread/GIL/scheduling delays, not isolated terminal cost','two untruncated traces prove no default_memory/mem_dict calls in sampled readframes, other frames supported by scoped implementation and32 allocation count','camera active flag in FINISH predates separate CLOSED receipt'])
(P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'CAMERA_TRACES.json').write_text(json.dumps(traces,indent=2)+'\n')
(P/'SOURCE_SHA256.json').write_text(json.dumps(before,indent=2)+'\n')
(P/'COMMANDS_AND_FORMULAS.json').write_text(json.dumps(dict(command='python -X utf8 -B analyze.py',formulas=dict(whole_loop='(CHECK_COMPLETE.monotonic_ns - BOUNDED_CAPTURE_AND_STEPS.monotonic_ns)/1e6',per_step='whole_loop_ms/32',throughput='32000/whole_loop_ms',reduction='100*(1-R10/R9)',worker='mean of all32 worker timings; queue wait separate from service time'),indices=sel,oracle_source=str(audit/'COMMANDS.json')),indent=2)+'\n')
print(json.dumps(dict(comparison=comparison,worker=worker,reconciliation=reconcile,residual=runs['R10']['matched29_phase_ms']['unseparated_bridge_residual_ms'],transfer=transfer),indent=2))
