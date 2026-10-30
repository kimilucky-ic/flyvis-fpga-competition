"""Localhost only: real receiver, retained packets, lost ACK and latest display."""
from pathlib import Path
import sys,json,threading,urllib.request,urllib.error,time,struct,zipfile
from unittest.mock import patch
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
import live_server,audit_saved_run,ram_records
from live_protocol import Store,sha,canonical
from live_transport import Uploader,request
T=P/'evidence'/('transport_cpu_'+str(time.time_ns()));T.mkdir(exist_ok=False)
source=Path((P/'evidence/latest_cpu.txt').read_text());r=json.loads((source/'RESULT.json').read_text());run=Path(r['output']);n=r['fixture_steps'];saved=source/'receiver'
cfg=dict(max_steps=256,ring_slots=64,duration_s=60.,minimum_period_s=0.,transfer_mode='live_compact',session_id='cpu_ring',token='cpu-local-test-only',bit_sha256='CPU_ONLY_NO_RING_BIT',hwh_sha256='CPU_ONLY_NO_RING_HWH',initial_state_sha256=sha((P/'bundle/initial_state.bin').read_bytes()))
# Saved-only audit reads batches after producer memory is gone, checks every
# prepared input and all state bytes against independently saved R3 oracle.
(T/'pc').mkdir();(T/'pc/session.json').write_text(json.dumps(cfg));counts=[]
def cached_oracle(store,bundle,out):
 for k in range(n):
  m,source,rec=store.read(k);first=k//3*3
  expected=(P.parent/'ov5640_live_60s_20261026/pc/records/audit'/('%06d_expected.bin'%first)).read_bytes()
  assert rec.state_bits==expected[(k-first)*182676:(k-first+1)*182676]
 counts.append(len(store.meta));return dict(status='PASS_CACHED_REFERENCE_REPLAY_ONLY',steps=len(store.meta),state_words_compared=len(store.meta)*45669,mismatch_words=0)
ram_records.CURRENT=None
with patch.object(audit_saved_run,'P',T),patch.object(audit_saved_run,'audit',cached_oracle):
 audited=audit_saved_run.audit_saved(run,T/'saved_audit')
assert counts==[n] and audited['camera_close_status']=='CLOSED'
app=live_server.App(cfg,T/'http_records');server=live_server.make_server(app,'127.0.0.1',0)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
cfg['pc_url']='http://127.0.0.1:'+str(server.server_address[1])
open_local=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(route):
 with open_local.open(cfg['pc_url']+route,timeout=5) as response:return response.read()
try:
 assert request(cfg,'/hello')['received']==0
 nb=get('/notebook');assert sha(nb)==sha((P/'LINE11_OFFICIAL_LIVE_RING_60S.ipynb').read_bytes())
 assert b'64' in get('/') and json.loads(get('/latest'))['packet'] is None
 outgoing=T/'outgoing';(outgoing/'transport').mkdir(parents=True)
 for k in range(3):(outgoing/'transport'/('%06d.packet'%k)).write_bytes((saved/('%06d.packet'%k)).read_bytes())
 attempts=[]
 def lose_ack(c,route,data=None):
  reply=request(c,route,data);attempts.append(route)
  if len(attempts)==1:raise ConnectionResetError('CPU injected lost ACK after durable receive')
  return reply
 uploader=Uploader(outgoing,cfg,send=lose_ack)
 try:uploader.attempt()
 except ConnectionResetError:pass
 else:raise AssertionError('lost ACK injection missing')
 assert uploader.next==0 and len(app.store.meta)==1
 # Reopen receiver store to exercise persisted duplicate recognition.
 app.store=Store(T/'http_records',cfg)
 assert uploader.attempt() and uploader.next==1 and len(app.store.meta)==1
 assert uploader.attempt() and uploader.attempt() and uploader.next==3 and len(app.store.meta)==3
 latest=json.loads(get('/latest?after=0'));assert latest['packet']['step_id']==2 and len(latest['packet']['input_721'])==721
 builds=app.display_builds
 assert json.loads(get('/latest?after=2'))['packet'] is None and app.display_builds==builds
 state=latest['packet']['state_token'];assert get('/frame.png?step=2&state='+state).startswith(b'\x89PNG')
 before=len(app.store.meta);damaged=bytearray((saved/'000002.packet').read_bytes());damaged[-10000]^=1
 try:request(cfg,'/ingest',bytes(damaged))
 except urllib.error.HTTPError as exc:assert exc.code==409
 else:raise AssertionError('corruption must reject')
 try:request(cfg,'/step',b'{}')
 except urllib.error.HTTPError as exc:assert exc.code==404
 else:raise AssertionError('board control route must not exist')
 assert len(app.store.meta)==before
finally:
 server.shutdown();server.server_close();thread.join(5)
result=dict(status='PASS_CPU_LOCALHOST_TRANSPORT_AND_SAVED_BATCH_AUDIT',offline_steps=n,offline_state_words=n*45669,cached_oracle_only=True,HTTP_records=3,lost_ACK_preserved=True,receiver_reopened=True,display_skipped_to_step=2,display_cache_reused=True,corruption_rejected=True,no_board_control_route=True,exact_notebook_served=True,server_closed=True,board_operations=0)
(P/'evidence/TRANSPORT_CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
