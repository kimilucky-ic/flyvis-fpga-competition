"""Bounded CPU integration with fake devices; real files/HTTP/renderer/oracle."""
import ast,copy,json,shutil,struct,subprocess,sys,threading,time,urllib.error
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path[:0]=[str(B),str(P/'pc')]
from live_protocol import *
from live_transport import Uploader,request
from live_server import App,make_server
from full_audit import audit
from ddr_control import DdrControl
from ddr_memory import OwnedDdr
from board_runtime import CheckedVideo
from snapshot_records import rolling
from ps_input import PsInput
import live_board
T=P/'evidence'/('cpu_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir(exist_ok=False)
config=json.loads((P/'pc/session.json').read_text());config=dict(config,minimum_period_s=0)
results=[]
def ok(name):results.append(name);print('PASS',name,flush=True)
def reject(fn,label):
 try:fn()
 except (ValueError,RuntimeError,urllib.error.HTTPError,IndexError,FileNotFoundError):ok(label)
 else:raise AssertionError('not rejected: '+label)
source=(P.parent/'ov5640_official_audit_20261024_b0a5/raw/capture/bound/000000/source_frame.bin').read_bytes()
f=np.frombuffer(source,np.uint8).reshape(480,800,3);patterns=[f.copy(),f[:,::-1,:].copy(),np.zeros_like(f)]
frames=[patterns[k%3] for k in range(32)];inputs=[PsInput(480,800,'BGR').render(x).astype('<f4').tobytes() for x in frames]
work=T/'fixture_oracle';work.mkdir()
for name in ('edges.bin','meta.hex','initial_state.bin'):shutil.copyfile(B/name,work/name)
expected=bytearray();commands=[]
for first in range(0,32,3):
 inp=work/('%02d_input.bin'%first);out=work/('%02d_expected.bin'%first);inp.write_bytes(b''.join(inputs[first:first+3]))
 cmd=[str((B/'reference.exe').resolve()),str(work.resolve()),str(inp.resolve()),str(out.resolve())]
 proc=subprocess.run(cmd,capture_output=True,timeout=60);(work/('%02d.log'%first)).write_bytes(proc.stdout+proc.stderr);proc.check_returncode()
 data=out.read_bytes();expected+=data;(work/'initial_state.bin').write_bytes(data[-182676:]);commands.append(cmd)
(T/'FIXTURE_COMMANDS.json').write_text(json.dumps(commands,indent=2))
expected=bytes(expected);assert len(expected)==32*182676
# Reuse previously accepted fake-MMIO/cache test mechanics, never execute the old test module.
old=(P.parent/'ov5640_official_release_r2_20261024/test_continuous.py').read_text()
classes='\n\n'.join(ast.get_source_segment(old,node) for node in ast.parse(old).body if isinstance(node,ast.ClassDef))
classes=classes.replace('self.k>=3','self.k>=len(frames)').replace('self.steps==3','self.steps==len(frames)')
CYCLES=2199975;events=[];O=None;mem=None
exec(compile(classes,'accepted_cpu_fake_devices','exec'),globals())
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,root,out):
  global O
  O=out;self.out=out;self.owner={};self.mm=MMIO();self.video=Video()
 def prepare(self):events.append('prepare')
 def load(self):events.append('fake_load')
 def inspect(self):return {'FCLK0':100,'FCLK1':100}
 def control(self):self.c=DdrControl(self.mm);return self.c
 def memory(self,slots=1):
  global mem
  mem=OwnedDdr(lambda shape,**k:Buffer(shape[0]),lambda:None,slots);self.m=mem;return mem
 def start_camera(self,memory):return CheckedVideo(self.video,memory,lambda:None,self.out)
def offline(*a,**k):raise ConnectionError('CPU injected PC disconnection')
out=live_board.execute(B,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000001',runtime_factory=Runtime,send=offline,upload_wait=0)
rt=next(iter(live_board._RETAINED.values()));assert rt.mm.steps==32 and rt.video.k==32 and events.count('close')==1
assert len(list((out/'transport').glob('*.packet')))==32 and len(list((out/'capture/bound').glob('*/COMMITTED.json')))==32
assert rt.m.size==32*188416 and json.loads((out/'TRANSFER.json').read_text())['acked']==0
ok('32 neural steps and all records complete while PC entirely disconnected')
reject(lambda:rt.owner['bridge'].step(),'capacity blocks capture and STEP 33');assert rt.mm.steps==32 and rt.video.k==32
raws=[(out/'transport'/('%06d.packet'%k)).read_bytes() for k in range(32)]
store=Store(T/'negative',config)
reject(lambda:store.accept(raws[1]),'out of order rejected')
reject(lambda:store.accept(raws[0][:-1]),'truncated record rejected')
m,s,r=unpack(raws[0],config)
bad=dict(m,session_id='wrong');reject(lambda:store.accept(pack(bad,s,raws[0][-RECORD_BYTES:])),'wrong session rejected')
bad=dict(m,previous_state_sha256='0'*64);reject(lambda:store.accept(pack(bad,s,raws[0][-RECORD_BYTES:])),'wrong previous state rejected')
corrupt=bytearray(raws[0]);corrupt[-10000]^=1;reject(lambda:store.accept(bytes(corrupt)),'payload corruption rejected')
a=store.accept(raws[0]);assert store.accept(raws[0])['duplicate'] and len(store.meta)==1;ok('identical duplicate ACK without added journal entry')
bad=dict(m,timing={'changed':1});reject(lambda:store.accept(pack(bad,s,raws[0][-RECORD_BYTES:])),'conflicting duplicate rejected')
(T/'negative/000001.packet.pending').write_bytes(b'partial')
assert len(Store(T/'negative',config).meta)==1;ok('restart ignores incomplete temporary file')
# Real loopback HTTP, ACK lost after durable receipt, and receiver process-state restart.
app=App(config,T/'receiver');server=make_server(app);port=server.server_address[1]
http_config=dict(config,pc_url='http://127.0.0.1:'+str(port))
th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
assert request(http_config,'/hello')['received']==0
up=Uploader(out,http_config);up.done.set();lost=[False]
def lost_ack(c,route,data=None):
 reply=request(c,route,data)
 if route=='/ingest' and not lost[0]:lost[0]=True;raise TimeoutError('ACK lost after durable save')
 return reply
up.send=lost_ack
try:up.attempt()
except TimeoutError:pass
else:raise AssertionError('lost ACK not injected')
assert up.next==0 and len(app.store.meta)==1
up.attempt();assert up.next==1 and len(app.store.meta)==1 and rt.mm.steps==32;ok('lost ACK retries identical file without duplicate STEP')
for k in range(1,9):up.attempt()
assert len(app.store.meta)==9
server.shutdown();server.server_close();th.join()
try:up.attempt()
except (ConnectionError,urllib.error.URLError,OSError):pass
else:raise AssertionError('expected refused connection')
assert up.next==9 and rt.mm.steps==32
app=App(config,T/'receiver');assert len(app.store.meta)==9
server=make_server(app,port=port);th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
for k in range(9,32):assert up.attempt()
assert up.next==32;up.attempt();assert up.finish_sent
ok('receiver restart resumes durable step 9 through32; finish idempotent')
reply=request(http_config,'/finish',(out/'FINISH.json').read_bytes());assert reply['durable']
end=time.monotonic()+90
while app.audit_running and time.monotonic()<end:time.sleep(.1)
assert app.audit_result and app.audit_result['mismatch_words']==0 and app.audit_result['state_words_compared']==1461408
ok('all32 full-state audits, expected-only feedback across eleven oracle chunks')
# Missing/reordered/unauthorized control endpoints cannot trigger board operations.
reject(lambda:request(http_config,'/step',b'{}'),'no remote STEP endpoint')
reject(lambda:request(dict(http_config,token='bad'),'/ingest',raws[0]),'wrong authorization rejected')
packet0=app.packet(0);packet31=app.packet(31)
(T/'display_packets.json').write_text(json.dumps([packet0,packet31]))
server.shutdown();server.server_close();th.join()
# Counterfeit last state with internally corrected wire checksum must fail the full oracle.
bad_store=Store(T/'bad_numeric',dict(config,max_steps=4));previous=config['initial_state_sha256']
for k in range(4):
 m,s,r=unpack(raws[k],config);record=bytearray(raws[k][-RECORD_BYTES:])
 if k==3:
  record[4096+182676-4]^=1;state=bytes(record[4096:4096+182676]);struct.pack_into('<I',record,13*4,rolling(state))
  m=copy.deepcopy(m);m['state_sha256']=sha(state);m['record_sha256']=sha(record);m['committed']['state_sha256']=sha(state)
 bad_store.accept(pack(m,s,record))
finish=json.loads((out/'FINISH.json').read_text());finish.update(completed_steps=4,packet_sha256=bad_store.digests)
bad_store.finish(finish);bad_result=audit(bad_store,B,T/'bad_numeric_audit')
assert bad_result['status']=='FAIL_NUMERICAL_MISMATCH' and bad_result['mismatch_words']==1
ok('last-neuron corruption with valid transport checksum rejected numerically after chunk boundary')
result=dict(status='PASS_CPU_TRANSPORT_AND_FULL_STATE_INTEGRATION_ONLY',tests=results,steps=32,state_words=1461408,
 mismatch_words=0,board_actions=0,gpu_actions=0,vivado_actions=0,real_HTTP_loopback=True,native_ARM=False,
 independent_RTL_math=False,real_time=False,producer_output=str(out),accepted_records=str(T/'receiver'))
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_cpu.txt').write_text(str(T))
print('RESULT',T,flush=True)
