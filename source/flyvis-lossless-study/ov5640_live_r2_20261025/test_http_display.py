import io,json,sys,threading,urllib.request,urllib.error,time
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from live_server import App,make_server
from live_protocol import canonical
from live_transport import request
T=Path((P/'evidence/latest_cpu.txt').read_text());c=json.loads((P/'pc/session.json').read_text());app=App(c,T/'receiver')
s=make_server(app);thread=threading.Thread(target=s.serve_forever,daemon=True);thread.start()
c=dict(c,pc_url='http://127.0.0.1:'+str(s.server_address[1]));opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(route):
 with opener.open(c['pc_url']+route,timeout=5) as r:return r.read()
checks=[]
try:
 assert '官方 OV5640'.encode() in get('/');checks.append('fixed PC HTML entry')
 assert get('/fixed_skeleton.js')==(P/'assets/fixed_skeleton.js').read_bytes()
 assert get('/api/competition-live/cache')==(P/'assets/projection.bin').read_bytes();checks.append('original renderer/cache endpoints byte identical')
 assert get('/notebook')==(P/'LINE11_OFFICIAL_LIVE_R2.ipynb').read_bytes();checks.append('downloaded single-file Notebook exact')
 latest=json.loads(get('/latest'));assert latest['packet']['step_id']==31 and latest['status']['received']==32
 for k in (0,31):
  m,source,_=app.store.read(k);raw=get('/frame.png?step=%s&state=%s'%(k,m['state_sha256']))
  pixel=np.asarray(Image.open(io.BytesIO(raw)));assert np.array_equal(pixel,np.frombuffer(source,np.uint8).reshape(480,800,3)[:,:,::-1])
 checks.append('frame0 and31 source PNG exactly bound to each state')
 try:get('/frame.png?step=0&state='+app.store.meta[31]['state_sha256'])
 except urllib.error.HTTPError as e:assert e.code==400
 else:raise AssertionError('cross-frame mixing')
 checks.append('cross-step image/state rejected')
 f=T/'receiver/000000_receive.json';before=f.read_bytes();a=request(c,'/ingest',(T/'receiver/000000.packet').read_bytes());assert a['duplicate'] and f.read_bytes()==before
 checks.append('duplicate keeps first receipt timing unchanged')
 finish=dict(app.store.final,packet_timings={d.parent.name:json.loads(d.read_text()) for d in Path(json.loads((T/'RESULT.json').read_text())['producer_output']).glob('capture/bound/*/PACKET_TIMING.json')})
 assert len(canonical(finish))<131072;checks.append('final context including all32 packet timings fits finish bound')
finally:s.shutdown();s.server_close();thread.join()
result=dict(status='PASS_CPU_HTTP_DISPLAY_AND_DOWNLOAD_ENDPOINTS',checks=checks,real_loopback=True,board_contact=False,native_browser=False)
(P/'evidence/HTTP_DISPLAY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
