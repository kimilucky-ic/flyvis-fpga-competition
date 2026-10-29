from pathlib import Path
import json,sys,threading,time,urllib.request,urllib.error,copy
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
from live_server import App,make_server
from round_sessions import admission
S=P/'pc/rounds/cbf41bf542ec5303af29bb11ad398fb5';cfg=json.loads((S/'session.json').read_text());r=S/'records';T=E/'http';T.mkdir(exist_ok=False)
a=App(cfg,T/'records');server=make_server(a);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_address[1]);op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def req(path,data=None):
 headers={'Authorization':'Bearer '+cfg['token']};request=urllib.request.Request(url+path,data=data,headers=headers)
 with op.open(request,timeout=10) as response:return json.loads(response.read())
try:
 for k in range(6):
  raw=(r/('%06d.packet'%k)).read_bytes();res=req('/ingest',raw);assert res['durable'] and res['step_id']==k
 assert req('/ingest',raw)['duplicate'] and len(a.store.meta)==6
 deadline=time.monotonic()+15
 while a.audit_progress.get('steps',0)<6 and time.monotonic()<deadline:time.sleep(.1)
 assert a.audit_progress.get('steps')==6 and a.audit_result is None and a.audit_running
 status=req('/status');assert status['audited_steps']==6 and not status['next_round_allowed']
 f=json.loads((r/'FINISH.json').read_text());f.update(completed_steps=6,hardware_completed_steps=6,packet_sha256=a.store.digests);f['duration']['completed_steps']=6;f['context']['NEURAL_AFTER.json']={'0x10':38,'0x14':6,'0x18':0,'0x24':0,'0x4c':6,'0x50':0}
 req('/finish',json.dumps(f).encode());deadline=time.monotonic()+10
 while a.audit_running and time.monotonic()<deadline:time.sleep(.1)
 assert a.audit_result['status']=='PASS_ALL_SAVED_STATES' and not admission(a)[0]
 close=json.loads((r/'CAMERA_CLOSE.json').read_text());close.update(completed_steps=6,packet_sha256=a.store.digests)
 req('/camera-close',json.dumps(close).encode());assert admission(a)[0]
 reloaded=App(cfg,T/'records');assert not reloaded.audit_running and reloaded.audit_result['steps']==6 and admission(reloaded)[0]
 result=dict(status='PASS_HTTP_INCREMENTAL_RECEIVER',partial_progress_before_FINISH=6,duplicate_no_extra_step=True,no_early_PASS=True,PASS_needs_CLOSED_for_next_round=True,saved_PASS_reloaded_without_recompute=True,board_actions=0,fixture='six saved records with CPU-only shortened completion receipt')
 (E/'HTTP_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:server.shutdown();server.server_close();thread.join(3)
