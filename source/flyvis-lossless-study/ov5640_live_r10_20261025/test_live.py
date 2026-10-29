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
from direct_input import DirectAreaInput
from camera_config import WIDTH,HEIGHT
import live_board
T=P/'evidence'/('cpu_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir(exist_ok=False)
config=json.loads((P/'pc/session.json').read_text());config=dict(config,minimum_period_s=0)
results=[]
def ok(name):results.append(name);print('PASS',name,flush=True)
def reject(fn,label):
 try:fn()
 except (ValueError,RuntimeError,urllib.error.HTTPError,IndexError,FileNotFoundError):ok(label)
 else:raise AssertionError('not rejected: '+label)
accepted=P.parent/'ov5640_live_r2_20261025'
accepted_config=json.loads((accepted/'pc/session.json').read_text())
accepted_store=Store(accepted/'pc/records',accepted_config)
assert accepted_store.final['run_id']=='RUN_80ee7d3a1f6d4b909b5064754f1ef9b0' and len(accepted_store.meta)==32
# CPU fixture: derive 400x240 images from old retained frames. This is NOT a
# claim that the physical OV5640 scaler produces these exact pixels.
frames=[];inputs=[];expected=bytearray();mapper=DirectAreaInput(HEIGHT,WIDTH,'BGR')
for k in range(32):
 m,source,r=accepted_store.read(k)
 source=np.frombuffer(source,np.uint8).reshape(HEIGHT,480//HEIGHT,WIDTH,800//WIDTH,3).astype(np.uint32)
 frame=((source.sum(axis=(1,3))+(480//HEIGHT)*(800//WIDTH)//2)//((480//HEIGHT)*(800//WIDTH))).astype(np.uint8)
 frames.append(frame);inputs.append(mapper.render(frame).astype('<f4').tobytes())
r8=P.parent/'ov5640_live_r8_20261025'
r8run=Path((r8/'evidence/latest_cpu.txt').read_text())
r8result=json.loads((r8run/'RESULT.json').read_text())
r8store=Store(Path(r8result['accepted_records']),json.loads((r8/'pc/session.json').read_text()))
expected_parts=[]
for k in range(32):
    _,_,r=r8store.read(k);assert inputs[k]==r.input_bits;expected_parts.append(r.state_bits)
expected=b''.join(expected_parts)
(T/'FIXTURE_SOURCE.json').write_text(json.dumps(dict(source=str(r8run),kind='reused accepted R8 CPU input/state fixtures; independent full oracle still runs after transport')))
# Reuse previously accepted fake-MMIO/cache test mechanics, never execute the old test module.
old=(P.parent/'ov5640_official_release_r2_20261024/test_continuous.py').read_text()
classes='\n\n'.join(ast.get_source_segment(old,node) for node in ast.parse(old).body if isinstance(node,ast.ClassDef))
classes=classes.replace('self.k>=3','self.k>=len(frames)').replace('self.steps==3','self.steps==len(frames)')
classes=classes.replace("assert (d/'input.bin').read_bytes()==actual and (d/'PREPARED.json').exists()","assert __import__('capture_binding').read_capsule(d/'PREPARED.bin',2884)[1][-2884:]==actual")
CYCLES=2199975;events=[];O=None;mem=None
exec(compile(classes,'accepted_cpu_fake_devices','exec'),globals())
original_mmio_write=MMIO.write
bulk_calls=[]
def write_including_bytes(self,a,v):
 if isinstance(v,bytes):
  assert a==0x400 and len(v)==2884;bulk_calls.append(v)
  for i,(word,) in enumerate(struct.iter_unpack('<I',v)):original_mmio_write(self,a+4*i,word)
 else:original_mmio_write(self,a,v)
MMIO.write=write_including_bytes
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,root,out):
  global O
  O=out;self.out=out;self.owner={};self.mm=MMIO();self.video=Video()
 def prepare(self):events.append('prepare')
 def load(self):events.append('fake_load')
 def inspect(self):return {'FCLK0':100,'FCLK1':100}
 def control(self):self.c=DdrControl(self.mm,bulk_input=True);return self.c
 def memory(self,slots=1):
  global mem
  mem=OwnedDdr(lambda shape,**k:Buffer(shape[0]),lambda:None,slots);self.m=mem;return mem
 def start_camera(self,memory):return CheckedVideo(self.video,memory,lambda:None,self.out)
def offline(*a,**k):raise ConnectionError('CPU injected PC disconnection')
out=live_board.execute(B,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000001',runtime_factory=Runtime,send=offline,upload_wait=0)
rt=next(iter(live_board._RETAINED.values()));assert rt.mm.steps==32 and rt.video.k==32 and events.count('close')==0
assert all(not any(n.startswith('fsync:') or n.startswith('write:') for n in json.loads(f.read_text())['producer_profile']) for f in out.glob('capture/bound/*/PACKET_TIMING.json'))
assert not list(out.glob('capture/bound/*/PACKET_TIMING.json')) and not list(out.glob('CAMERA_BUFFER*.json'))
assert len(json.loads((out/'FINISH.json').read_text())['packet_timings'])==32
ok('no per-step diagnostics;32prepared inputs and authoritative single-build full-state packets flushed at end')
assert len(list((out/'transport').glob('*.packet')))==32 and not list((out/'transport').glob('*.ready.json')) and len(list((out/'capture/bound').glob('*/COMMITTED.bin')))==0
assert rt.m.size==32*188416 and json.loads((out/'TRANSFER.json').read_text())['acked']==0
assert len(bulk_calls)==32 and bulk_calls==inputs
finish=json.loads((out/'FINISH.json').read_text());assert len(finish['worker_timings'])==32
assert all('whole_iteration_ms' in x and 'console_output_ms' in x for x in finish['packet_timings'].values())
ok('32 bulk submissions match all inputs; worker and complete iteration timing retained')
ok('32 neural steps and all records complete while PC entirely disconnected')
reject(lambda:rt.owner['bridge'].step(),'capacity blocks capture and STEP 33');assert rt.mm.steps==32 and rt.video.k==32
raws=[load_packet(out,k) for k in range(32)]
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
reply=request(http_config,'/finish',(out/'TRANSFER_FINISH.json').read_bytes());assert reply['durable']
end=time.monotonic()+90
while app.audit_running and time.monotonic()<end:time.sleep(.1)
assert app.audit_result and app.audit_result['mismatch_words']==0 and app.audit_result['state_words_compared']==1461408
ok('all32 full-state audits, expected-only feedback across eleven oracle chunks')
# Missing/reordered/unauthorized control endpoints cannot trigger board operations.
reject(lambda:request(http_config,'/step',b'{}'),'no remote STEP endpoint')
reject(lambda:request(dict(http_config,token='bad'),'/ingest',b'{}'),'wrong authorization rejected')
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
finish=json.loads((out/'FINISH.json').read_text());finish.update(completed_steps=4,hardware_completed_steps=4,packet_sha256=bad_store.digests)
bad_store.finish(finish);bad_result=audit(bad_store,B,T/'bad_numeric_audit')
assert bad_result['status']=='FAIL_NUMERICAL_MISMATCH' and bad_result['mismatch_words']==1
ok('last-neuron corruption with valid transport checksum rejected numerically after chunk boundary')
result=dict(status='PASS_CPU_TRANSPORT_AND_FULL_STATE_INTEGRATION_ONLY',tests=results,steps=32,state_words=1461408,
 mismatch_words=0,board_actions=0,gpu_actions=0,vivado_actions=0,real_HTTP_loopback=True,native_ARM=False,
 independent_RTL_math=False,real_time=False,fixture_source=accepted_store.final['run_id'],producer_output=str(out),accepted_records=str(T/'receiver'))
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_cpu.txt').write_text(str(T))
print('RESULT',T,flush=True)
