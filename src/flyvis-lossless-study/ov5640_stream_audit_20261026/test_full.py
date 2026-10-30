from pathlib import Path
import json,sys,threading,time,subprocess,os,statistics,shutil
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
from live_protocol import Store,atomic,canonical,sha
from stream_audit import run,LOW_PRIORITY
T=E/'cpu';T.mkdir(exist_ok=False)
results=[]
for index,sid in enumerate(['cbf41bf542ec5303af29bb11ad398fb5','7fa0282e80fd55e9973790fe05060eb2']):
 source=P/'pc/rounds'/sid;r=source/'records';config=json.loads((source/'session.json').read_text());d=T/str(index);d.mkdir();records=d/'records';store=Store(records,config);job=d/'config.json';job.write_bytes(canonical(config));output=d/'audit'
 def launch():
  log=(d/'process.log').open('wb')
  cmd=[sys.executable,'-B',str(P/'pc/stream_audit.py'),'--records',str(records),'--config',str(job),'--bundle',str(P/'bundle'),'--output',str(output),'--parent',str(os.getpid())]
  child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=LOW_PRIORITY);return child,log
 f=json.loads((r/'FINISH.json').read_text());count=f['completed_steps'];times=[];start=time.monotonic();child=log=None
 if index==1:child,log=launch()
 for k in range(count):
  if index==1:
   target=start+k*.055
   if target>time.monotonic():time.sleep(target-time.monotonic())
  raw=(r/('%06d.packet'%k)).read_bytes();t=time.monotonic();receipt=store.accept(raw);elapsed=(time.monotonic()-t)*1000;times.append(elapsed)
  atomic(records/('%06d_receive.json'%k),canonical(dict(receipt,receive_to_commit_ms=elapsed)))
  if k in (0,16):assert store.accept(raw)['duplicate'] and len(store.meta)==k+1
  if k in (300,600,900):print('CPU_REPLAY',index+1,k+1,flush=True)
  if index==1 and k==30:
   # Missing data for a short interval must not finish or duplicate calculation.
   time.sleep(.35);assert not (output/'RESULT.json').exists()
 assert not (output/'RESULT.json').exists()
 progress=records/'AUDIT_PROGRESS.json';before_finish=json.loads(progress.read_text()) if progress.exists() else {}
 store.finish(f);finish_at=time.monotonic()
 if index==0:child,log=launch()
 child.wait(timeout=120);log.close();assert child.returncode==0,(d/'process.log').read_text()
 result=json.loads((output/'RESULT.json').read_text());assert result['status']=='PASS_ALL_SAVED_STATES' and result['steps']==count and result['mismatch_words']==0
 old=json.loads((r/'audit/RESULT.json').read_text());assert [x['expected_state_sha256'] for x in result['rows']]==[x['expected_state_sha256'] for x in old['rows']]
 for path in (r/'audit').glob('*_expected.bin'):assert (output/path.name).read_bytes()==path.read_bytes()
 commands=json.loads((output/'COMMANDS.json').read_text());prev=sha((P/'bundle/initial_state.bin').read_bytes())
 for c in commands:
  assert c['initial_expected_sha256']==prev;prev=sha((output/('%06d_expected.bin'%c['first_step'])).read_bytes()[-182676:])
 q=sorted(times);results.append(dict(mode='complete_source' if index==0 else 'paced_CPU_receiver_55ms',steps=count,state_words=count*45669,all_expected_outputs_identical=True,active_s=result['active_seconds'],audit_elapsed_s=result['elapsed_s'],wait_after_finish_s=time.monotonic()-finish_at,progress_before_finish=before_finish.get('steps',0),receive_accept_mean_ms=statistics.mean(times),receive_accept_p95_ms=q[int(.95*(len(q)-1))],pressure_yield_s=result['pressure_yield_seconds']))
 print('CPU_FULL_RUN_PASS',index+1,json.dumps(results[-1]),flush=True)
(E/'FULL_REPLAY_RESULT.json').write_text(json.dumps(dict(status='PASS_TWO_FULL_CPU_REFERENCE_REPLAYS',runs=results,physical_speed_claim=False,board_actions=0),indent=2))
