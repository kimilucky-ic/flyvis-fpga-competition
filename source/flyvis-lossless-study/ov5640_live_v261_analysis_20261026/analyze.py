"""Read-only local operator evidence audit. No board/network/oracle execution."""
from pathlib import Path
import sys,json,hashlib,statistics as st
import numpy as np
P=Path(__file__).resolve().parent;root=P.parent
release=root/'ov5640_live_v261_20261026';receiver=release
records=receiver/'pc/records';audit=records/'audit';sys.path.insert(0,str(release/'bundle'))
from live_protocol import Store,sha
from direct_input import DirectAreaInput
from board_runtime import clocks
padding_mask=DirectAreaInput(48,80,'BGR').bias==.5;padding_bad=0
assert not padding_mask.any()
input_min=np.full(721,np.inf);input_max=np.full(721,-np.inf);input_half_counts=np.zeros(721,dtype=np.int64)
sources=sorted([*records.glob('*.packet'),records/'FINISH.json',records/'CAMERA_CLOSE.json',audit/'RESULT.json',audit/'COMMANDS.json',*audit.glob('*_inputs.bin'),*audit.glob('*_expected.bin')])
before={str(f):sha(f.read_bytes()) for f in sources}
config=json.loads((receiver/'pc/session.json').read_text());store=Store(records,config)
f=store.final;close=store.camera_close;n=len(store.meta);assert n==1090
assert f['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' and close['status']=='CLOSED' and f['error'] is None
assert f['hardware_completed_steps']==n and f['duration']['stop_reason']=='DURATION_REACHED'
assert f['duration']['elapsed_seconds']>=60 and f['duration']['last_frame_start_seconds']<60
ctx=f['context'];assert ctx['RUN_CONTEXT.json']['input_mapping']=='direct-grey-center-square-area/v2';clocks(ctx['CLOCK.json']['raw']);assert ctx['HP_WIDTH.json']['HP0_HP1_64bit_verified'];after=ctx['NEURAL_AFTER.json'];assert after=={'0x10':38,'0x14':1090,'0x18':0,'0x24':0,'0x4c':1090,'0x50':0}
assert ctx['DDR_OWNERSHIP.json']['bytes']==12058624 and ctx['DDR_OWNERSHIP.json']['slots']==64
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
  words=np.frombuffer(r.input_bits,'<u4');values=words.view('<f4')
  input_min=np.minimum(input_min,values);input_max=np.maximum(input_max,values);input_half_counts+=(words==0x3f000000)
  padding_bad+=int(np.count_nonzero(words[padding_mask]!=0x3f000000))
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
fields=('whole_iteration_ms','between_iterations_ms','packet_enqueue_ms','bridge_step_and_ram_record_ms','capture_and_cache_ms','ps_mapping_ms','input_721_mmio_write_ms','input_upload_step_and_publication_ms','step_command_to_completed_check_ms','ddr_copy_and_cache_ms','console_output_ms','ring_credit_wait_ms','ps_mapping_thread_cpu_ms','bridge_thread_cpu_ms')
step_stats={k:stats([x[k] for x in rows]) for k in fields}
profile_stats={k:stats([x['producer_profile'][k]['ms'] for x in rows]) for k in ('ddr_record_decode','decode_header_and_slice','decode_payload_sha256','decode_native_checksums_and_finite','binding_path_setup','binding_input_checks','binding_prepare_metadata_and_ram','binding_commit_checks_and_ram')}
batches=ctx['RAM_FLUSH.json']['batches'];last=0
for b in batches:
 assert b['first_step']==last and 1<=b['last_step']-b['first_step']+1<=16
 last=b['last_step']+1
assert last==n and len(batches)==69 and ctx['RAM_FLUSH.json']['persisted_steps']==n
seconds=f['duration']['elapsed_seconds'];period=f['duration']['minimum_period_s'];assert period==0;nominal_rate=None
slow=[dict(step_id=int(k),human_step=int(k)+1,iteration_ms=x['whole_iteration_ms'],enqueue_ms=x['packet_enqueue_ms'],bridge_ms=x['bridge_step_and_ram_record_ms']) for k,x in f['packet_timings'].items() if x['packet_enqueue_ms']>5]
last_batch=batches[-1];assert last_batch['last_step']-last_batch['first_step']+1==2
stats_workers={k:stats([x[k] for x in workers]) for k in ('queue_wait_ms','total_worker_ms','batch_persist_ms','pack_ms','wire_hash_ms','store_and_retire_ms','thread_cpu_ms')}
assert before=={str(x):sha(x.read_bytes()) for x in sources}
# Read-only verification of all sealed R3 members, including the Notebook.
manifest=json.loads((release/'FINAL_MANIFEST_SHA256.json').read_text())
for name,digest in manifest.items():assert sha((release/name).read_bytes())==digest,name
result=dict(status='PASS_OPERATOR_VIVADO2026_1_CROP_60S_1090_STEPS_REVERIFIED',evidence='OFFLINE_AUDIT_OF_OPERATOR_PHYSICAL_RECORDS',
 run_id=f['run_id'],boot_id=f['boot_id'],steps=n,state_words=n*45669,input_words=input_words,mismatch_words=mismatches,
 independent_oracle_rerun=False,expected_feedback_chunks=len(cmds),actual_inputs_match_saved_oracle_inputs=True,
 deadline=f['duration'],elapsed_loop_seconds=seconds,actual_loop_ms_per_step=seconds*1000/n,model_steps_per_second=n/seconds,
 configured_rate_ceiling=nominal_rate,throughput_below_ceiling_percent=None,
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
 conclusions=['60s met;1090contiguous records/all49779210states pass;separate camera CLOSED receipt',
 'No fixed pacing;64DDR slots reused across17complete wraps plus2records;all1090released and0occupied atfinish',
 'Worker and upload overlap producer;their total times are not additive with loop elapsed',
 'finish.camera_closed=false precedes separate CLOSED receipt and is not a close failure',
 'source image mapping not re-audited;browserFPS and longer stability not measured'])
baseline=json.loads((root/'ov5640_live_crop_analysis_20261026/RESULT.json').read_text())
result['comparison_previous_crop']=dict(old_steps=baseline['steps'],old_ms_per_step=baseline['actual_loop_ms_per_step'],new_ms_per_step=result['actual_loop_ms_per_step'],latency_reduction_percent=100*(1-result['actual_loop_ms_per_step']/baseline['actual_loop_ms_per_step']),throughput_ratio=result['model_steps_per_second']/baseline['model_steps_per_second'],same_stimulus_controlled=False)
result['ring']=dict(slots=64,completed=n,complete_wraps=n//64,tail_slots=n%64,durably_released=after['0x4c'],occupied=after['0x50'],credit_wait=stats([x['ring_credit_wait_ms'] for x in rows]))
result['foreground_bridge_residual_ms']=stats([x['bridge_step_and_ram_record_ms']-x['capture_and_cache_ms']-x['ps_mapping_ms']-x['input_upload_step_and_publication_ms']-x['ddr_copy_and_cache_ms'] for x in rows])
result['timing_accounting']=dict(sum_whole_iteration_ms=sum(x['whole_iteration_ms'] for x in rows),sum_between_iteration_ms=sum(x['between_iterations_ms'] for x in rows),unassigned_boundary_ms=seconds*1000-sum(x['whole_iteration_ms']+x['between_iterations_ms'] for x in rows),ring_credit_wait_nested_in_between_iteration=True)
result['mapping_wall_minus_thread_cpu_ms']=stats([x['ps_mapping_ms']-x['ps_mapping_thread_cpu_ms'] for x in rows])
result['slow_steps_top10']=sorted([dict(step_id=int(k),whole_ms=x['whole_iteration_ms'],enqueue_ms=x['packet_enqueue_ms'],bridge_ms=x['bridge_step_and_ram_record_ms'],credit_wait_ms=x['ring_credit_wait_ms']) for k,x in f['packet_timings'].items()],key=lambda x:x['whole_ms'],reverse=True)[:10]

result['actual_input_padding_check']=dict(fully_padded_receptors=int(padding_mask.sum()),steps_checked=n,words_checked=n*int(padding_mask.sum()),not_half_gray_words=padding_bad,raw_image_audit=False)

result['ARM_preprocess_comparison']=dict(old_wall_ms=baseline['step_statistics']['ps_mapping_ms']['mean'],new_wall_ms=step_stats['ps_mapping_ms']['mean'],old_thread_CPU_ms=baseline['step_statistics']['ps_mapping_thread_cpu_ms']['mean'],new_thread_CPU_ms=step_stats['ps_mapping_thread_cpu_ms']['mean'])
result['ARM_preprocess_comparison']['wall_reduction_percent']=100*(1-result['ARM_preprocess_comparison']['new_wall_ms']/result['ARM_preprocess_comparison']['old_wall_ms'])
result['ARM_preprocess_comparison']['CPU_reduction_percent']=100*(1-result['ARM_preprocess_comparison']['new_thread_CPU_ms']/result['ARM_preprocess_comparison']['old_thread_CPU_ms'])
from ps_input import receptor_centers
cy=receptor_centers()[:,0];old_padded=(cy+6<83)|(cy-6>=333)
assert int(old_padded.sum())==110
result['input_field_observation']=dict(mapping_revision=ctx['RUN_CONTEXT.json']['input_mapping'],new_geometric_padding_count=int(padding_mask.sum()),old_padding_sites=110,old_padding_sites_that_changed_over_run=int(np.count_nonzero((input_max>input_min)[old_padded])),old_padding_sites_always_half=int(np.count_nonzero((input_half_counts==n)[old_padded])),all_sites_changed=int(np.count_nonzero(input_max>input_min)),all_sites_always_half=int(np.count_nonzero(input_half_counts==n)),raw_source_image_audit=False)
result['timing_change_ms']={k:step_stats[k]['mean']-baseline['step_statistics'][k]['mean'] for k in step_stats if k in baseline['step_statistics']}

(P/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'SOURCE_SHA256.json').write_text(json.dumps(before,indent=2)+'\n')
(P/'COMMANDS_AND_FORMULAS.json').write_text(json.dumps(dict(command=['python','-X','utf8','-B',str(Path(__file__).resolve())],
 formulas=['ms_per_step=1000*duration.elapsed_seconds/1090','steps_per_second=1090/duration.elapsed_seconds','all_state_words=1090*45669',
 'batch_total=sum(RAM_FLUSH.batches.persist_ms);overlaps producer','foreground_enqueue_total=sum(packet_timings.packet_enqueue_ms);includes snapshot/queue wait',
 'tail_measured=last_partial_batch.persist_ms+RAM_FLUSH.flush_ms;does not include all finalize phases'],
 reference='existing saved expected chunks only;commands inspected,never executed',read_only_source=True),indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','steps','state_words','input_words','mismatch_words','elapsed_loop_seconds','actual_loop_ms_per_step','model_steps_per_second','camera_close','source_files_unchanged','release_files_unchanged')},indent=2))
print('tail',result['tail']);print('batch mean/max/total',result['batch_ms']);print('slow enqueue count',len(slow))

print('comparison',result['comparison_previous_crop'])
print('step means',{k:round(v['mean'],4) for k,v in step_stats.items()})
print('decode means',{k:round(v['mean'],4) for k,v in profile_stats.items()})
print('worker means',{k:round(v['mean'],4) for k,v in stats_workers.items()})
print('ring',result['ring'])
print('timing accounting',result['timing_accounting'])

print('ARM preprocessing comparison',result['ARM_preprocess_comparison'])
print('input field',result['input_field_observation'])
print('phase changes',result['timing_change_ms'])
