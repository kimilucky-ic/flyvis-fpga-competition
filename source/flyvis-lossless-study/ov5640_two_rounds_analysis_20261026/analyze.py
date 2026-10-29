"""Read saved operator records and oracle outputs; no board or oracle execution."""
from pathlib import Path
import sys,json,hashlib,statistics,time
import numpy as np
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from live_protocol import Store,sha
from board_runtime import clocks
results=[];sealed={};started=time.monotonic()
for sid in ['cbf41bf542ec5303af29bb11ad398fb5','7fa0282e80fd55e9973790fe05060eb2']:
 root=P/'pc/rounds'/sid;r=root/'records';au=r/'audit';config=json.loads((root/'session.json').read_text());s=Store(r,config);f=s.final;c=s.camera_close;ctx=f['context'];a=json.loads((au/'RESULT.json').read_text());n=len(s.meta)
 assert n==f['completed_steps']==f['hardware_completed_steps']==c['completed_steps']==a['steps']
 assert f['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' and f['error'] is None and c['status']=='CLOSED' and c['camera_closed'] and c['error'] is None
 assert a['status']=='PASS_ALL_SAVED_STATES' and a['state_words_compared']==n*45669 and a['mismatch_words']==0
 for x in [f,c]:
  assert x['session_id']==sid and x['run_id']==s.meta[0]['run_id'] and x['boot_id']==s.meta[0]['boot_id'] and x['packet_sha256']==s.digests
 d=f['duration'];assert d['elapsed_seconds']>=60 and d['last_frame_start_seconds']<60 and d['stop_reason']=='DURATION_REACHED' and d['minimum_period_s']==0
 assert ctx['NEURAL_AFTER.json']=={'0x10':38,'0x14':n,'0x18':0,'0x24':0,'0x4c':n,'0x50':0}
 clocks(ctx['CLOCK.json']['raw']);assert ctx['HP_WIDTH.json']['HP0_HP1_64bit_verified']
 for field,name in [('bit_sha256','flyvis_official.bit'),('hwh_sha256','flyvis_official.hwh')]:assert ctx['RUN_CONTEXT.json']['identity'][field]==config[field]==sha((P/'bundle'/name).read_bytes())
 cmds=json.loads((au/'COMMANDS.json').read_text());previous=sha((P/'bundle/initial_state.bin').read_bytes());pos=0;mismatch=0
 for cmd in cmds:
  first,count=cmd['first_step'],cmd['steps'];assert first==pos and cmd['returncode']==0 and cmd['initial_expected_sha256']==previous
  ip=au/('%06d_inputs.bin'%first);ep=au/('%06d_expected.bin'%first);inputs=ip.read_bytes();expected=ep.read_bytes();sealed[str(ip)]=sha(inputs);sealed[str(ep)]=sha(expected)
  assert len(inputs)==2884*count and len(expected)==182676*count
  for j in range(count):
   k=first+j;meta,source,rec=s.read(k);assert source is None and rec.input_bits==inputs[j*2884:(j+1)*2884]
   e=expected[j*182676:(j+1)*182676];diff=int(np.count_nonzero(np.frombuffer(e,'<u4')!=np.frombuffer(rec.state_bits,'<u4')));mismatch+=diff
   assert a['rows'][k]['input_sha256']==sha(rec.input_bits) and a['rows'][k]['actual_state_sha256']==sha(rec.state_bits) and a['rows'][k]['expected_state_sha256']==sha(e)
   assert meta['timing']['core_counter_nominal_ms']==21.99975
  previous=sha(expected[-182676:]);pos+=count
 assert pos==n and mismatch==0 and sha((au/'oracle_bundle/initial_state.bin').read_bytes())==previous
 for path in [*r.glob('*.packet'),r/'FINISH.json',r/'CAMERA_CLOSE.json',au/'RESULT.json',au/'COMMANDS.json',root/'ROUND.json']:sealed[str(path)]=sha(path.read_bytes())
 assert set(f['transfer_timings'])=={str(k) for k in range(n)}
 for k in range(n):assert f['transfer_timings'][str(k)]['durable'] and f['transfer_timings'][str(k)]['sha256']==s.digests[k]
 batches=ctx['RAM_FLUSH.json']['batches'];last=0
 for b in batches:assert b['first_step']==last;last=b['last_step']+1
 assert last==n==ctx['RAM_FLUSH.json']['persisted_steps']
 phases=['PREPARE','LOAD','CLOCK_HP','FRESH_ABI','ALLOCATE_RESTORE','OFFICIAL_SENSOR_AND_VIDEO_START','BOUNDED_CAPTURE_AND_STEPS'];ts=[ctx['PHASE_'+x+'.json']['monotonic_ns'] for x in phases]
 phase_s={phases[i]:(ts[i+1]-ts[i])/1e9 for i in range(len(phases)-1)}
 rows=list(f['packet_timings'].values());worker=list(f['worker_timings'].values())
 fields=['whole_iteration_ms','ps_mapping_ms','capture_and_cache_ms','input_721_mmio_write_ms','input_upload_step_and_publication_ms','ddr_copy_and_cache_ms','packet_enqueue_ms','console_output_ms','ring_credit_wait_ms']
 means={key:statistics.mean(x[key] for x in rows) for key in fields}
 native=ctx['NATIVE_PAYLOAD.json'];tail=ctx['LOOP_TAIL.json'];flush=ctx['RAM_FLUSH.json']
 results.append(dict(session_id=sid,run_id=f['run_id'],boot_id=f['boot_id'],steps=n,elapsed_s=d['elapsed_seconds'],last_admission_s=d['last_frame_start_seconds'],ms_per_step=1000*d['elapsed_seconds']/n,steps_per_second=n/d['elapsed_seconds'],input_words=n*721,state_words=n*45669,mismatch_words=mismatch,oracle_chunks=len(cmds),saved_audit_s=a['elapsed_s'],startup_measured_s=(ts[-1]-ts[0])/1e9,startup_phase_seconds=phase_s,authorization_to_prepare_seconds=None,final_registers=ctx['NEURAL_AFTER.json'],camera_status=c['status'],camera_close_ms=c['close_duration_ms'],tail=tail,metadata_flush_ms=flush['flush_ms'],last_batch_ms=batches[-1]['persist_ms'],batch_count=len(batches),batch_mean_ms=statistics.mean(b['persist_ms'] for b in batches),batch_max_ms=max(b['persist_ms'] for b in batches),means_ms=means,worker_means_ms={key:statistics.mean(x[key] for x in worker) for key in ['queue_wait_ms','pack_ms','wire_hash_ms','total_worker_ms']},first_record_path_prechecks=config['max_steps']*13,source_file=str(r/'FINISH.json'),timing_limits=['Pre-PREPARE authorization gap has no recorded timestamp','PC audit elapsed includes sequential oracle and file/parse work; no per-component measurement','Tail components may overlap; do not blindly sum','Camera close receipt reports call duration; not entire transfer/close gap','Model-step throughput is not browser FPS']))
assert len({x['run_id'] for x in results})==2
for path,digest in sealed.items():assert sha(Path(path).read_bytes())==digest
manifest=json.loads((P/'FINAL_MANIFEST_SHA256.json').read_text())
for name,digest in manifest.items():assert sha((P/name).read_bytes())==digest,name
out=dict(status='PASS_TWO_OPERATOR_60S_RUNS_SAVED_FULL_STATES_REVERIFIED',evidence='OFFLINE_RECHECK_OF_OPERATOR_PHYSICAL_RECORDS_AND_EXISTING_ORACLE_OUTPUTS',runs=results,total_steps=sum(x['steps'] for x in results),total_state_words=sum(x['state_words'] for x in results),total_input_words=sum(x['input_words'] for x in results),new_oracle_runs=0,hardware_actions=0,runtime_edits=0,unchanged_source_files=len(sealed),unchanged_release_files=len(manifest),analysis_wall_s=time.monotonic()-started)
(E/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');(E/'SOURCE_SHA256.json').write_text(json.dumps(sealed,indent=2)+'\n');(E/'COMMANDS_AND_FORMULAS.json').write_text(json.dumps(dict(command='python -X utf8 -B '+str(Path(__file__).resolve()),formulas={'ms_per_step':'elapsed_s*1000/completed_steps','steps_per_second':'completed_steps/elapsed_s','phase_seconds':'(next_phase.monotonic_ns-current_phase.monotonic_ns)/1e9'},oracle_execution=False),indent=2)+'\n')
print(json.dumps(out))
