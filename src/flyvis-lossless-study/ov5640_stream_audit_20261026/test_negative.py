from pathlib import Path
import json,sys,copy,threading,time,ast
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
from live_protocol import Store,canonical,atomic,sha
from stream_audit import run,reception_busy
from round_sessions import admission
S=P/'pc/rounds/cbf41bf542ec5303af29bb11ad398fb5';config=json.loads((S/'session.json').read_text());source=S/'records';T=E/'negative_r3';T.mkdir(exist_ok=False);passed=[]
def fixture(name,finish=True,count=6):
 p=T/name;p.mkdir();s=Store(p/'records',config)
 for k in range(count):s.accept((source/('%06d.packet'%k)).read_bytes())
 if finish:
  f=json.loads((source/'FINISH.json').read_text());f.update(completed_steps=count,hardware_completed_steps=count,packet_sha256=s.digests);f['duration']['completed_steps']=count;s.finish(f)
 return p,s

def cached(first,n,work,i,o):
 assert i.read_bytes()==(source/'audit'/('%06d_inputs.bin'%first)).read_bytes()
 o.write_bytes((source/'audit'/('%06d_expected.bin'%first)).read_bytes())
# All output tests are CPU fixtures with saved-reference adapter, not physical results.
p,s=fixture('waiting',False);ticks=[0]
def stopsoon():ticks[0]+=1;return ticks[0]<4
try:run(s.path,config,P/'bundle',p/'audit',p/'progress.json',stopsoon,cached)
except InterruptedError:pass
else:raise AssertionError('Missing FINISH accepted')
assert not (p/'audit/RESULT.json').exists();assert json.loads((p/'progress.json').read_text())['steps']==6;passed.append('no PASS before FINISH and interruption retains outputs')
# Resume is a fresh CPU recomputation from original initial state, not a board retry.
f=json.loads((source/'FINISH.json').read_text());f.update(completed_steps=6,hardware_completed_steps=6,packet_sha256=s.digests);f['duration']['completed_steps']=6;s.finish(f)
r=run(s.path,config,P/'bundle',p/'audit_resume',p/'progress2.json',oracle=cached);assert r['status']=='PASS_ALL_SAVED_STATES';passed.append('resume from original initial state')
p,s=fixture('mismatch');feedback=[]
def changed(first,n,work,i,o):
 feedback.append(sha((work/'initial_state.bin').read_bytes()));cached(first,n,work,i,o)
 if first==0:
  b=bytearray(o.read_bytes());b[-1]^=1;o.write_bytes(b)
r=run(s.path,config,P/'bundle',p/'audit',p/'progress.json',oracle=changed);assert r['status']=='FAIL_NUMERICAL_MISMATCH' and r['mismatch_words']==1
assert feedback[1]==sha((p/'audit/000000_expected.bin').read_bytes()[-182676:]) and feedback[1]!=s.meta[2]['state_sha256'];passed.append('mismatch cannot PASS and expected feedback retained')
p,s=fixture('failed',False);f=json.loads((source/'FINISH.json').read_text());f.update(status='STOPPED_KEEP_KERNEL_AND_BUFFERS',completed_steps=6,hardware_completed_steps=6,packet_sha256=s.digests,error='fixture failure');s.finish(f)
try:run(s.path,config,P/'bundle',p/'audit',p/'progress.json',oracle=cached)
except ValueError:passed.append('failed producer rejected')
else:raise AssertionError('failed producer')
p,s=fixture('pressure',False);atomic(s.path/'000005_receive.json',canonical({'receive_to_commit_ms':150}));assert reception_busy(s);ticks=[0]
try:run(s.path,config,P/'bundle',p/'audit',p/'progress.json',stopsoon,cached)
except InterruptedError:pass
else:raise AssertionError('pressure test stop')
a=json.loads((p/'progress.json').read_text());assert a['status']=='YIELDING_TO_RECEIVER' and a['steps']==0;passed.append('slow receiver pauses oracle')
p,s=fixture('gap',False);(s.path/'000002.packet').rename(s.path/'saved_000002.bin')
try:Store(s.path,config)
except ValueError:passed.append('gap rejected')
else:raise AssertionError('gap')
p,s=fixture('corrupt',False);b=bytearray((s.path/'000003.packet').read_bytes());b[len(b)-188416+4096]^=1;(s.path/'000003.packet').write_bytes(b)
try:Store(s.path,config)
except ValueError:passed.append('corrupt packet rejected')
else:raise AssertionError('corrupt')
for name in ['pc/stream_audit.py','pc/live_server.py']:ast.parse((P/name).read_text(encoding='utf-8-sig'),feature_version=(3,8))
# Handler's scheduling occurs after the successful reply, never before ACK.
src=(P/'pc/live_server.py').read_text();assert "self.reply(200,result)\n                if route in ('/ingest','/finish'):app.audit_if_ready()" in src
# Existing CLOSE plus all-states admission still governs next round.
p,s=fixture('gate');s.final['context']['NEURAL_AFTER.json']={'0x10':38,'0x14':6,'0x18':0,'0x24':0,'0x4c':6,'0x50':0}
from types import SimpleNamespace
app=SimpleNamespace(store=s,config=config,audit_running=False,audit_result={'status':'PASS_ALL_SAVED_STATES','steps':6,'state_words_compared':6*45669,'mismatch_words':0})
assert not admission(app)[0];passed.append('PASS without CLOSED cannot start next round')
(E/'NEGATIVE_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_STREAM_NEGATIVES',cases=passed,oracle='saved reference adapter for fault injection',board_actions=0),indent=2));print(json.dumps(passed))
