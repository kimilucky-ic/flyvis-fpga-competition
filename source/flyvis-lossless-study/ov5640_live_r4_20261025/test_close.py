"""CPU only: block/fail camera close; never import a real board runtime."""
from pathlib import Path
# Reuse the accepted CPU fake-device setup; no hardware imports or old test execution.
setup=Path(__file__).with_name('test_live.py').read_text().split('def offline(*a,**k):')[0]
setup=setup.replace("'cpu_'+time.strftime", "'close_'+time.strftime")
exec(compile(setup,'cpu_setup','exec'),globals())
entered=threading.Event();release=threading.Event();holder={}
class BlockingRuntime(Runtime):
 def init__(self,root,out):
  super().init__(root,out)
  def close():
   events.append('close');entered.set()
   if not release.wait(25):raise RuntimeError('CPU test release timeout')
  self.video.close=close
receiver=Store(T/'receiver',config)
def send(c,route,data=None):
 if route=='/ingest':return receiver.accept(data)
 if route=='/finish':return receiver.finish(json.loads(data))
 if route=='/camera-close':return receiver.record_camera_close(json.loads(data))
 raise AssertionError(route)
def produce():
 try:holder['out']=live_board.execute(B,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000002',runtime_factory=BlockingRuntime,send=send,upload_wait=10)
 except BaseException as e:holder['error']=repr(e)
th=threading.Thread(target=produce);th.start()
try:
 assert entered.wait(30),'close not reached'
 out=next((T/'producer').glob('RUN_*'));rt=next(iter(live_board._RETAINED.values()))
 assert th.is_alive() and rt.mm.steps==32 and len(receiver.meta)==32 and receiver.final is not None
 assert receiver.final['camera_closed'] is False and receiver.camera_close is None
 assert Path(str(out)+'_NEURAL_RESULT.zip').is_file()
 a=audit(receiver,B,T/'audit_while_camera_blocked');assert a['mismatch_words']==0 and a['state_words_compared']==1461408
 ok('all32 files and full-state oracle finish while camera close remains blocked')
 reject(lambda:receiver.record_camera_close(dict(schema='line11-camera-close/v1')),'unbound close receipt rejected')
finally:release.set();th.join(30)
assert not th.is_alive() and 'error' not in holder,holder
assert receiver.camera_close['status']=='CLOSED' and rt.mm.steps==32
receipt=json.loads((out/'CAMERA_CLOSE.json').read_text())
assert receiver.record_camera_close(receipt)['durable']
assert Store(T/'receiver',config).camera_close==receipt
bad=dict(receipt,camera_closed=False,status='FAILED',error='fake');reject(lambda:receiver.record_camera_close(bad),'conflicting close receipt rejected')
ok('close success saved separately, duplicate receipt idempotent, restart preserves both statuses')
# Test actual authenticated file-only HTTP route; no board-control endpoint.
app=App(config,T/'receiver');server=make_server(app);st=threading.Thread(target=server.serve_forever,daemon=True);st.start()
try:
 hc=dict(config,pc_url='http://127.0.0.1:'+str(server.server_address[1]))
 assert request(hc,'/camera-close',canonical(receipt))['status']=='CLOSED'
 reject(lambda:request(dict(hc,token='wrong'),'/camera-close',b'{}'),'camera receipt route requires authorization')
 assert app.status()['camera_close_status']=='CLOSED'
finally:server.shutdown();server.server_close();st.join()
# Synchronous close raises: numerical completion must remain immutable and separately valid.
live_board._RETAINED.clear();receiver=Store(T/'failure_receiver',config)
class FailingRuntime(Runtime):
 def init__(self,root,out):
  super().init__(root,out)
  def fail():raise RuntimeError('CPU injected close failure')
  self.video.close=fail
out2=live_board.execute(B,T/'failure_producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000003',runtime_factory=FailingRuntime,send=send,upload_wait=10)
assert len(receiver.meta)==32 and receiver.final['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING'
assert receiver.camera_close['status']=='FAILED' and receiver.camera_close['camera_closed'] is False
assert (out2/'IN_DOUBT.json').exists() and next(iter(live_board._RETAINED.values())).mm.steps==32
ok('close exception preserves all records and reports FAILED without changing neural completion')
result=dict(status='PASS_CPU_CLOSE_ORDERING_ONLY',tests=results,board_actions=0,native_driver_deadlock_reproduced=False,words_checked=1461408,mismatch_words=0)
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_close.txt').write_text(str(T));print('RESULT',T)
