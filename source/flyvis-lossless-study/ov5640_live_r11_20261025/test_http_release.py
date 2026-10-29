import sys,json,threading,urllib.request,hashlib,time
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from live_server import App,make_server
T=P/'evidence'/('http_release_'+time.strftime('%H%M%S'));T.mkdir(exist_ok=False)
cfg=json.loads((P/'pc/session.json').read_text());app=App(cfg,T/'records');server=make_server(app)
th=threading.Thread(target=server.serve_forever,daemon=True);th.start();base='http://127.0.0.1:'+str(server.server_address[1])
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def get(route,auth=False):
        q=urllib.request.Request(base+route,headers={'Authorization':'Bearer '+cfg['token']} if auth else {})
        with opener.open(q,timeout=10) as r:return r.read()
    page=get('/').decode();assert 'R11' in page and '80×48' in page
    nb=get('/notebook');assert nb==(P/'LINE11_OFFICIAL_LIVE_R11.ipynb').read_bytes()
    hello=json.loads(get('/hello',True));assert hello['session_id']==cfg['session_id'] and hello['received']==0
    assert json.loads(get('/latest'))['packet'] is None
    result=dict(status='PASS_LOCAL_HTTP_RELEASE_ONLY',notebook_bytes=len(nb),notebook_sha256=hashlib.sha256(nb).hexdigest(),fresh_receiver=True,board_actions=0)
    (T/'RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:server.shutdown();server.server_close();th.join()
