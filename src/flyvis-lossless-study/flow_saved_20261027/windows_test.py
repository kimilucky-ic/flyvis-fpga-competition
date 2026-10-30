from pathlib import Path
import sys,os,json,zipfile,hashlib,time,threading,urllib.request
import numpy as np
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';sys.path.insert(0,str(R/'pc'))
from flow_reader import FlowReader
f=FlowReader(R/'assets');maximum=0.;times=[];count=0
Z=Path(r'C:/Users/hzy72/Documents/xwechat_files/wxid_khlrd7p7q6j422_642a/temp/RWTemp/2026-10/8eaa68ae41247203942b7fc2b28636e7/交付_原始数据_精简版.zip')
with zipfile.ZipFile(Z) as z:
 for name in sorted(n for n in z.namelist() if n.endswith('/states.bin')):
  a=np.frombuffer(z.read(name),'<f4').reshape(-1,45669);gold=np.load(O/'repeat1'/(name.split('/')[0]+'_flow.npy'))
  for k,row in enumerate(a):
   bits=row.tobytes();start=time.perf_counter();p=f.packet(bits,hashlib.sha256(bits).hexdigest(),k);times.append((time.perf_counter()-start)*1000)
   actual=np.asarray(p['values'],np.float32);maximum=max(maximum,float(np.max(abs(actual-gold[k]))));assert np.allclose(actual,gold[k],atol=1e-5,rtol=1e-5);count+=1
  print(name,count,maximum,flush=True)
for bits,h in [(b'bad','bad'),(bytes(45669*4),'0'*64),(np.full(45669,np.nan,np.float32).tobytes(),None)]:
 if h is None:h=hashlib.sha256(bits).hexdigest()
 try:f.packet(bits,h,0);raise AssertionError('bad input accepted')
 except ValueError:pass
import live_server
live_server.FLOW=f
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];d=R/'pc/rounds'/sid
app=live_server.App(json.loads((d/'session.json').read_text()),d/'records');assert app.audit_result['status']=='PASS_ALL_SAVED_STATES'
packet=app.packet(len(app.store.meta)-1);(O/'TEST_PACKET.json').write_text(json.dumps(packet),encoding='utf-8')
assert packet['flow']['state_sha256']==packet['state_token']
# Optional decoder failure must preserve input/state display packet.
class Broken:
 def packet(self,*args):raise ValueError('injected')
live_server.FLOW=Broken();app.display_cache.clear();bad=app.packet(len(app.store.meta)-1);assert bad['flow']['status']=='UNAVAILABLE';assert {k:v for k,v in bad.items() if k!='flow'}=={k:v for k,v in packet.items() if k!='flow'}
# A stalled display decode holds no store/status lock and cannot stall status handler.
started=threading.Event();release=threading.Event()
class Slow:
 def packet(self,*args):started.set();assert release.wait(5);return f.packet(*args)
live_server.FLOW=Slow();app.display_cache.clear();server=live_server.make_server(app);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_address[1]);errors=[]
def fetch():
 try:urllib.request.urlopen(url+'/latest?after=-1',timeout=8).read()
 except Exception as e:errors.append(str(e))
t=threading.Thread(target=fetch);t.start();assert started.wait(3);s=time.perf_counter();status=json.load(urllib.request.urlopen(url+'/status',timeout=2));elapsed=time.perf_counter()-s;assert status['received']==len(app.store.meta);release.set();t.join(8);server.shutdown();assert not errors
result=dict(status='PASS_WINDOWS_CPU_OFFICIAL_EXPORT',interpreter=sys.executable,states=count,max_abs_error=maximum,atol=1e-5,rtol=1e-5,mean_packet_ms=float(np.mean(times)),p95_packet_ms=float(np.percentile(times,95)),invalid_size_hash_nan_rejected=True,decoder_failure_preserves_other_fields=True,status_s_while_decoder_blocked=elapsed,hardware_actions=0,gpu_runs=0)
(O/'WINDOWS_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(result,flush=True)
