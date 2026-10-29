from pathlib import Path
import json,hashlib,shutil,sys,difflib
P=Path('flyvis-lossless-study/ov5640_async_persist_20261026').resolve();R=P.parent/'ov5640_live_v261_20261026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((P/'before/FINAL_MANIFEST_SHA256.json').read_text())
assert all(sha(R/n)==v for n,v in old.items()),'release changed since backup; stop'
assert json.loads((R/'pc/ACTIVE_ROUND.json').read_text())==json.loads((P/'evidence/ACTIVE_BEFORE.json').read_text())
assert json.loads((P/'evidence/FAULT_RESULT.json').read_text())['status']=='PASS_CPU_ONLY'
assert json.loads((P/'evidence/STAGING_FAULT_RESULT.json').read_text())['status'].startswith('PASS_')
replay=Path((P/'evidence/latest_cpu.txt').read_text());rr=json.loads((replay/'RESULT.json').read_text());assert rr['status'].startswith('PASS_')
changed=('batch_records.py','record_worker.py','live_board.py','release_manifest.json')
diff=''
for name in changed:
 if name.endswith('.py'):
  diff+=''.join(difflib.unified_diff((P/'before/bundle'/name).read_text().splitlines(True),(P/'bundle'/name).read_text().splitlines(True),fromfile='before/'+name,tofile='candidate/'+name))
(P/'evidence/CHANGE.diff').write_text(diff,encoding='utf-8')
for name in changed:shutil.copyfile(P/'bundle'/name,R/'bundle'/name)
new=dict(old)
for name in changed:
 key=next(k for k in old if Path(k)==Path('bundle')/name);new[key]=sha(R/key)
assert [n for n in old if old[n]!=new[n]] and len([n for n in old if old[n]!=new[n]])==4
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(new,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert all(sha(R/n)==v for n,v in new.items())
sys.path[:0]=[str(R/'bundle'),str(R/'pc')]
from offline_check import verify
verify(R/'bundle')
from round_sessions import notebook
cfg=dict(session_id='0'*31+'1',token='CPU_PACKAGE_CHECK_ONLY')
# Actual full config from existing session is used only in memory; never print credentials.
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id']
cfg=json.loads((R/'pc/rounds'/sid/'session.json').read_text());cfg.update(session_id='0'*31+'1',token='CPU_PACKAGE_CHECK_ONLY')
assert notebook(R,cfg)[0]==(P/'evidence/CPU_CANDIDATE_NOTEBOOK.ipynb').read_bytes()
result=dict(status='CPU_VALIDATED_CANDIDATE_ENABLED_FOR_NEXT_ROUND_ONLY',board_actions=0,physical_speedup_measured=False,
 changed_runtime_sources=list(changed[:3]),unchanged_sealed_files=len(old)-4,firmware_changed=False,
 active_round=sid,active_round_notebook_unchanged=True,fixed_notebook_unchanged=True,receiver_restart=False,
 queue=dict(pack_jobs=32,pending_batches=2,one_writer_in_flight=True,batch_steps=16,ram_bytes_limit=32*1024*1024,ddr_slots_max=64),
 acceptance=dict(fault_tests=9,writer_failure_after_input_staging='PASS_NO_STEP_NO_RELEASE',replay_steps=rr['fixture_steps'],state_words=rr['state_words_checked'],state_mismatches=0,reference='existing accepted saved expected states, no neural recomputation'),
 evidence=dict(fault='evidence/FAULT_RESULT.json',staging='evidence/STAGING_FAULT_RESULT.json',replay=str(replay/'RESULT.json'),package='evidence/PACKAGE_RESULT.json'),
 rollback='Restore the four bundle files from before/bundle and the saved FINAL_MANIFEST_SHA256.json before creating a further round; retain all existing round directories.',
 limitations=['CPU threads and mocked I/O failures do not measure ARM performance','Windows real file fsync tested; Linux directory barrier fault/order injected','Persistent slow storage still causes bounded backpressure','Actual operator60s/browser timing and complete state acceptance pending'])
(P/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
