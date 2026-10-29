from pathlib import Path
import json,sys,shutil,threading,urllib.request,urllib.error
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
from live_server import App,make_server
from round_sessions import Rounds,NOTEBOOK
T=E/'http';T.mkdir(exist_ok=False);shutil.copytree(P/'bundle',T/'bundle');shutil.copy2(P/NOTEBOOK,T/NOTEBOOK);(T/'pc').mkdir();shutil.copy2(P/'pc/session.json',T/'pc/session.json')
config=json.loads((T/'pc/session.json').read_text());baseline=App(config,P/'pc/records')
def factory(c,r):return baseline if r==T/'pc/records' else App(c,r)
rounds=Rounds(T,factory);server=make_server(baseline,'127.0.0.1',0,rounds);th=threading.Thread(target=server.serve_forever,daemon=True);th.start();url='http://127.0.0.1:'+str(server.server_address[1]);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(route,data=None,headers=None):
 req=urllib.request.Request(url+route,data=None if data is None else (data if isinstance(data,bytes) else json.dumps(data).encode()),headers=headers or {})
 try:
  with opener.open(req,timeout=30) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
try:
 status,raw=request('/status');assert status==200 and json.loads(raw)['next_round_allowed']
 assert request('/next-round',{'session_id':config['session_id']})[0]==403
 headers={'Content-Type':'application/json','X-Line11-UI':'1','Origin':url}
 assert request('/next-round',{'session_id':config['session_id']},dict(headers,Origin='http://untrusted.example'))[0]==403
 status,raw=request('/next-round',{'session_id':config['session_id']},headers);assert status==200,raw
 nxt=json.loads(raw);current=rounds.current.config
 assert nxt['session_id']==current['session_id'] and not nxt['duplicate']
 status,raw=request('/next-round',{'session_id':config['session_id']},headers);assert status==200 and json.loads(raw)['duplicate']
 assert request('/hello',headers={'Authorization':'Bearer '+config['token']})[0]==403
 status,raw=request('/hello',headers={'Authorization':'Bearer '+current['token']});assert status==200 and json.loads(raw)['received']==0
 status,raw=request('/notebook');assert status==200 and raw==rounds.notebook_path(rounds.current).read_bytes()
 assert request('/ingest',(P/'pc/records/000000.packet').read_bytes(),{'Authorization':'Bearer '+config['token']})[0]==403
 assert request('/ingest',(P/'pc/records/000000.packet').read_bytes(),{'Authorization':'Bearer '+current['token']})[0]==409
 assert request('/next-round',{'session_id':current['session_id']},headers)[0]==409
 status,raw=request('/latest');body=json.loads(raw);assert body['packet'] is None and body['status']['received']==0
 assert not list(rounds.current.store.path.glob('*.packet'))
finally:server.shutdown();server.server_close();th.join(5)
r=dict(status='PASS_HTTP_NEXT_ROUND_SWITCH_RETRY_OLD_SESSION_REJECTION',session_created_once=True,old_auth_rejected=True,old_packet_new_auth_rejected=True,wrong_origin_rejected=True,missing_UI_header_rejected=True,new_notebook_download_matches=True,new_receiver_empty=True,pending_round_rejected=True,server_closed=True,board_actions=0)
(E/'HTTP_RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
