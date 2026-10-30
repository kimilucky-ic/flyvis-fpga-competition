"""CPU tests specific to R6 low-resolution capture and volatile records."""
from pathlib import Path
setup=Path(__file__).with_name('test_live.py').read_text().split('def offline(*a,**k):')[0]
setup=setup.replace("'cpu_'+time.strftime", "'r6_'+time.strftime")
exec(compile(setup,'r6_fake_setup','exec'),globals())
import ram_records,os,importlib.util
from capture_binding import read_capsule,BoundSteps
from official_bridge import start_official
from types import SimpleNamespace
# Independent older scalar-output mapping; no expected800x480 input reuse.
old=P.parent/'ov5640_live_20261024/bundle/ps_input.py'
spec=importlib.util.spec_from_file_location('scalar_mapper_reference',old);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
scalar=ref.PsInput(240,400,'BGR')
for k in (0,7,19,31):assert scalar.render(frames[k]).astype('<f4').tobytes()==inputs[k]
ok('400x240 mapping agrees bitwise with retained scalar-output implementation')
# Observe official API arguments without using any hardware library.
call=[]
class Sensor:
 def init__(self,*a):pass
 def init(self):call.append('sensor.init')
 def set_outsize(self,*a):call.append(('size',a))
video=SimpleNamespace(configure=lambda x:call.append(('configure',x)),start=lambda:call.append('start'))
start_official(SimpleNamespace(ip_dict={'cam_iic':{}},video=SimpleNamespace(video_in=video)),lambda _:None,Sensor,lambda *a:a)
assert ('size',(400,240,1800,1000)) in call and ('configure',(400,240,24)) in call
ok('official sensor and VDMA API configure matching400x240, no physical call')
summaries={}
real_fsync=os.fsync
for mode in ['after_run','local_only']:
 live_board._RETAINED.clear();receiver=Store(T/(mode+'_receiver'),config);calls=[];sync_during=[]
 def guard(fd):
  j=ram_records.CURRENT
  if j and j.active:
   rt=next(iter(live_board._RETAINED.values()))
   if rt.mm.steps<32:sync_during.append(rt.mm.steps)
  return real_fsync(fd)
 def send(c,route,data=None):
  assert mode!='local_only','local mode contacted network'
  assert next(iter(live_board._RETAINED.values())).mm.steps==32
  calls.append(route)
  if route=='/ingest':return receiver.accept(data)
  if route=='/finish':return receiver.finish(json.loads(data))
  if route=='/camera-close':return receiver.record_camera_close(json.loads(data))
  raise AssertionError(route)
 os.fsync=guard
 try:out=live_board.execute(B,T/mode,dict(config,transfer_mode=mode),authorized=True,boot_id='00000000-0000-0000-0000-000000000006',runtime_factory=Runtime,send=send,upload_wait=10)
 finally:os.fsync=real_fsync
 rt=next(iter(live_board._RETAINED.values()));assert rt.mm.steps==32 and not sync_during
 for k in range(32):
  d=out/'capture/bound'/('%06d'%k);pre,ib=read_capsule(d/'PREPARED.bin',2884);post,record=read_capsule(d/'COMMITTED.bin',188416)
  assert ib==inputs[k] and record[128:3012]==inputs[k] and record[4096:186772]==expected[k*182676:(k+1)*182676]
  assert pre['source_pixels_retained'] is False
  profile=json.loads((d/'PACKET_TIMING.json').read_text())['producer_profile']
  assert not any(n.startswith('write:') or n.startswith('fsync:') for n in profile)
 assert not list(out.rglob('source_frame.bin'))
 if mode=='local_only':assert not calls and json.loads((out/'RESULT.json').read_text())['numerical_acceptance']=='NOT_RUN_LOCAL_ONLY'
 else:assert len(receiver.meta)==32 and receiver.camera_close['status']=='CLOSED'
 summaries[mode]=dict(output=str(out),network_calls=len(calls),journal=json.loads((out/'RAM_FLUSH.json').read_text()))
 ok(mode+' no in-loop fsync;32 saved input/state pairs exact after flush')
# Batch flush failure must leave RAM and hardware state owned; no close/no rerun.
live_board._RETAINED.clear();orig=ram_records.RamRecords.flush
ram_records.RamRecords.flush=lambda self:(_ for _ in ()).throw(OSError('CPU batch persistence failure'))
try:
 try:live_board.execute(B,T/'flush_failure',dict(config,transfer_mode='local_only'),authorized=True,boot_id='00000000-0000-0000-0000-000000000007',runtime_factory=Runtime,send=lambda *a:(_ for _ in ()).throw(AssertionError('network')),upload_wait=0)
 except OSError:pass
 else:raise AssertionError('batch failure ignored')
 rt=next(iter(live_board._RETAINED.values()));j=rt.owner['ram_records'];assert rt.mm.steps==32 and j.active
 assert len([k for k in j.files if k.endswith('COMMITTED.bin')])==32
 assert not (rt.out/'FINISH.json').exists() and not (rt.out/'CAMERA_CLOSE.json').exists()
 before=rt.mm.steps
 reject(lambda:rt.owner['bridge'].step(),'capacity blocks STEP after batch failure');assert rt.mm.steps==before
finally:ram_records.RamRecords.flush=orig
ok('batch disk failure retains all32 RAM records and skips camera close')
# Journal bound prevents unbounded memory growth and does not discard prior data.
j=ram_records.RamRecords(T/'small',limit=4);j.start();j.put(j.root/'a',b'1234')
try:j.put(j.root/'b',b'5')
except MemoryError:pass
else:raise AssertionError('memory bound ignored')
assert j.files=={'a':b'1234'}
ok('RAM capacity failure keeps previous immutable records')
r=dict(status='PASS_CPU_R6_LOWRES_VOLATILE_BATCH_ONLY',tests=results,modes=summaries,board_actions=0,physical400x240_verified=False,ARM_speed_verified=False,oracle_words=1461408)
(T/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(P/'evidence/latest_r6.txt').write_text(str(T));print('RESULT',T)
