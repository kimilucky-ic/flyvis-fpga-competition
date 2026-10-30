"""Localhost release smoke check; no board connection or permanent server."""
from pathlib import Path
import sys,json,threading,urllib.request,hashlib
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from live_server import App,make_server
from live_transport import request
T=P/'evidence/http';T.mkdir(exist_ok=False)
c=json.loads((P/'pc/session.json').read_text());app=App(c,T/'records');server=make_server(app,'127.0.0.1',0)
th=threading.Thread(target=server.serve_forever,daemon=True);th.start();local=dict(c,pc_url='http://127.0.0.1:'+str(server.server_address[1]))
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(route):
 with opener.open(local['pc_url']+route,timeout=5) as response:return response.read()
try:
 assert request(local,'/hello')['received']==0
 nb=get('/notebook');assert nb==(P/'LINE11_OFFICIAL_LIVE_CROP_60S.ipynb').read_bytes()
 page=get('/').decode();assert 'LINE11_OFFICIAL_LIVE_CROP_60S.ipynb' in page and '中央48×48' in page
 assert json.loads(get('/latest'))['packet'] is None
finally:server.shutdown();server.server_close();th.join(5)
r=dict(status='PASS_CPU_LOCALHOST_CROP_NOTEBOOK_DELIVERY',notebook_sha256=hashlib.sha256(nb).hexdigest(),new_session=True,configured_port=c['port'],records_empty=True,server_closed=True,board_operations=0)
(P/'evidence/HTTP_RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
