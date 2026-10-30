"""Read-only local operator evidence audit. No board/network/oracle execution."""
from pathlib import Path
import sys,json,hashlib,statistics as st
import numpy as np
P=Path(__file__).resolve().parent;root=P.parent
release=root/'ov5640_live_60s_r3_20261026';receiver=root/'ov5640_live_60s_20261026'
records=receiver/'pc/records';audit=records/'audit';sys.path.insert(0,str(release/'bundle'))
from live_protocol import Store,sha
sources=sorted([*records.glob('*.packet'),records/'FINISH.json',records/'CAMERA_CLOSE.json',audit/'RESULT.json',audit/'COMMANDS.json',*audit.glob('*_inputs.bin'),*audit.glob('*_expected.bin')])
before={str(f):sha(f.read_bytes()) for f in sources}
config=json.loads((receiver/'pc/session.json').read_text());store=Store(records,config)
f=store.final;close=store.camera_close;n=len(store.meta);assert n==494
assert f['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' and close['status']=='CLOSED' and f['error'] is None
assert f['hardware_completed_steps']==n and f['duration']['stop_reason']=='DURATION_REACHED'
assert f['duration']['elapsed_seconds']>=60 and f['duration']['last_frame_start_seconds']<60
ctx=f['context'];after=ctx['NEURAL_AFTER.json'];assert after=={'0x10':38,'0x14':494,'0x18':0,'0x24':0}
assert ctx['DDR_OWNERSHIP.json']['bytes']==100614144 and ctx['DDR_OWNERSHIP.json']['slots']==534
for field,name in [('bit_sha256','flyvis_official.bit'),('hwh_sha256','flyvis_official.hwh')]:
 assert ctx['RUN_CONTEXT.json']['identity'][field]==sha((release/'bundle'/name).read_bytes())==config[field]
cmds=json.loads((audit/'COMMANDS.json').read_text());previous=sha((release/'bundle/initial_state.bin').read_bytes());next_k=0;mismatches=0;input_words=0
for cmd in cmds:
 first,count=cmd['first_step'],cmd['steps'];assert first==next_k and 1<=count<=3 and cmd['returncode']==0
 assert cmd['initial_expected_sha256']==previous
 inputs=(audit/('%06d_inputs.bin'%first)).read_bytes();expected=(audit/('%06d_expected.bin'%first)).read_bytes()
 assert len(inputs)==count*2884 and len(expected)==count*182676
 for j in range(count):
  k=first+j;m,source,r=store.read(k);assert source is None
  assert r.input_bits==inputs[j*2884:(j+1)*2884]
  e=expected[j*182676:(j+1)*182676];diff=int(np.count_nonzero(np.frombuffer(e,'<u4')!=np.frombuffer(r.state_bits,'<u4')))
  mismatches+=diff;input_words+=721
 previous=sha(expected[-182676:]);next_k+=count
assert next_k==n and mismatches==0
old_audit=json.loads((audit/'RESULT.json').read_text());assert old_audit['mismatch_words']==mismatches and old_audit['steps']==n
assert sha((audit/'oracle_bundle/initial_state.bin').read_bytes())==previous
assert set(f['packet_timings'])==set(f['worker_timings'])=={'%06d'%k for k in range(n)}
assert set(f['transfer_timings'])=={str(k) for k in range(n)}
for k in range(n):
 t=f['transfer_timings'][str(k)];assert t['step_id']==k and t['durable'] is True and t['sha256']==store.digests[k]
rows=list(f['packet_timings'].values());workers=list(f['worker_timings'].values())
def stats(v):
 v=sorted(v);return dict(mean=st.mean(v),median=st.median(v),p95=v[int(.95*(len(v)-1))],maximum=max(v),total=sum(v))
fields=('whole_iteration_ms','between_iterations_ms','packet_enqueue_ms','bridge_step_and_ram_record_ms','capture_and_cache_ms','ps_mapping_ms','input_721_mmio_write_ms','input_upload_step_and_publication_ms','step_command_to_completed_check_ms','ddr_copy_and_cache_ms','console_output_ms')
step_stats={k:stats([x[k] for x in rows]) for k in fields}
profile_stats={k:stats([x['producer_profile'][k]['ms'] for x in rows]) for k in ('ddr_record_decode','decode_payload_sha256','decode_native_checksums_and_finite')}
batches=ctx['RAM_FLUSH.json']['batches'];last=0
for b in batches:
 assert b['first_step']==last and 1<=b['last_step']-b['first_step']+1<=16
 last=b['last_step']+1
assert last==n and len(batches)==31 and ctx['RAM_FLUSH.json']['persisted_steps']==n
seconds=f['duration']['elapsed_seconds'];period=f['duration']['minimum_period_s'];nominal_rate=1/period
slow=[dict(step_id=int(k),human_step=int(k)+1,iteration_ms=x['whole_iteration_ms'],enqueue_ms=x['packet_enqueue_ms'],bridge_ms=x['bridge_step_and_ram_record_ms']) for k,x in f['packet_timings'].items() if x['packet_enqueue_ms']>5]
last_batch=batches[-1];assert last_batch['last_step']-last_batch['first_step']+1==14
stats_workers={k:stats([x[k] for x in workers]) for k in ('queue_wait_ms','total_worker_ms','batch_persist_ms')}
assert before=={str(x):sha(x.read_bytes()) for x in sources}
# Read-only verification of all sealed R3 members, including the Notebook.
manifest=json.loads((release/'FINAL_MANIFEST_SHA256.json').read_text())
for name,digest in manifest.items():assert sha((release/name).read_bytes())==digest,name
result=dict(status='PASS_OPERATOR_SAVED_60S_494_STEPS_REVERIFIED',evidence='OFFLINE_AUDIT_OF_OPERATOR_PHYSICAL_RECORDS',
 run_id=f['run_id'],boot_id=f['boot_id'],steps=n,state_words=n*45669,input_words=input_words,mismatch_words=mismatches,
 independent_oracle_rerun=False,expected_feedback_chunks=len(cmds),actual_inputs_match_saved_oracle_inputs=True,
 deadline=f['duration'],elapsed_loop_seconds=seconds,actual_loop_ms_per_step=seconds*1000/n,model_steps_per_second=n/seconds,
 configured_rate_ceiling=nominal_rate,throughput_below_ceiling_percent=100*(1-(n/seconds)/nominal_rate),
 camera_close=close['status'],camera_close_ms=close['close_duration_ms'],final_registers=after,DDR=ctx['DDR_OWNERSHIP.json'],
 step_statistics=step_stats,decode_statistics=profile_stats,worker_statistics=stats_workers,
 batch_count=len(batches),batch_ms=stats([x['persist_ms'] for x in batches]),
 batch_time_scope='batch ZIP_STORED creation/write/fsync/rename/directorysync;not isolatedSD I/O',
 slow_enqueue_steps=slow,foreground_enqueue_total_ms=step_stats['packet_enqueue_ms']['total'],
 record_journal_peak_MiB=ctx['RAM_FLUSH.json']['peak_ram_bytes']/1048576,
 tail=dict(last_partial_batch_ms=last_batch['persist_ms'],remaining_metadata_flush_ms=ctx['RAM_FLUSH.json']['flush_ms'],worker_drain_ms=ctx['LOOP_TAIL.json']['worker_drain_ms'],
 measured_partial_batch_plus_metadata_ms=last_batch['persist_ms']+ctx['RAM_FLUSH.json']['flush_ms'],PC_audit_seconds=old_audit['elapsed_s']),
 transport_ms={k:stats([x[k]*1000 for x in f['transfer_timings'].values()]) for k in ('round_trip_seconds','rebuild_seconds')},
 clock='same design100MHz;register-derived nominal,not independently frequency-measured',
 board_actions=0,network_calls=0,GPU_actions=0,Vivado_actions=0,runtime_edits=0,source_files_unchanged=len(before),release_files_unchanged=len(manifest),
 conclusions=['60s met;494contiguous records/all22560486states pass;separate camera CLOSED receipt',
 '121.5ms/step wholeloop includes explicit capacity pacing;whole_iteration excludes gate waiting',
 'batch worker queue capacity2 creates measured producer backpressure;do not add all14.56s batch work or25.32s worker-queue wait to loop wall time',
 'finish.camera_closed=false precedes separate CLOSED receipt and is not evidence of close failure',
 'source image mapping not re-audited;browserFPS/longer stability and no-pacing speed not measured'])
(P/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'SOURCE_SHA256.json').write_text(json.dumps(before,indent=2)+'\n')
(P/'COMMANDS_AND_FORMULAS.json').write_text(json.dumps(dict(command=['python','-X','utf8','-B',str(Path(__file__).resolve())],
 formulas=['ms_per_step=1000*duration.elapsed_seconds/494','steps_per_second=494/duration.elapsed_seconds','all_state_words=494*45669',
 'batch_total=sum(RAM_FLUSH.batches.persist_ms);overlaps producer','foreground_enqueue_total=sum(packet_timings.packet_enqueue_ms);includes snapshot/queue wait',
 'tail_measured=last_partial_batch.persist_ms+RAM_FLUSH.flush_ms;does not include all finalize phases'],
 reference='existing saved expected chunks only;commands inspected,never executed',read_only_source=True),indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','steps','state_words','input_words','mismatch_words','elapsed_loop_seconds','actual_loop_ms_per_step','model_steps_per_second','camera_close','source_files_unchanged','release_files_unchanged')},indent=2))
print('tail',result['tail']);print('batch mean/max/total',result['batch_ms']);print('slow enqueue count',len(slow))
