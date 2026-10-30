from pathlib import Path
s=Path(__file__).with_name('test_live.py').read_text()
s=s[:s.index('import builtins')].replace("'cpu_'+time.strftime","'cpu_close_'+time.strftime")
s=s.replace('virtual.now+=1.875','virtual.now+=60')
exec(compile(s,'CPU_close_setup','exec'),globals())
receiver=Store(T/'receiver',config)
def local_send(c,route,data=None):
 if route=='/ingest':return receiver.accept(data)
 if route=='/finish':return receiver.finish(json.loads(data))
 if route=='/camera-close':return receiver.record_camera_close(json.loads(data))
 raise AssertionError(route)
out=live_board.execute(B,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000002',runtime_factory=Runtime,send=local_send,upload_wait=5,window_factory=virtual_window)
rt=next(iter(live_board._RETAINED.values()))
assert rt.mm.steps==1 and rt.video.k==1 and events.count('close')==1
assert receiver.final['completed_steps']==1 and receiver.final['duration']['elapsed_seconds']==60
assert receiver.camera_close['status']=='CLOSED' and receiver.camera_close['completed_steps']==1
assert len(list((out/'spool').glob('*.zip')))==1
assert not list(out.parent.glob('*.zip'))
restart=Store(T/'receiver',config);assert restart.camera_close['status']=='CLOSED'
result=dict(status='PASS_CPU_TIMED_PARTIAL_CAPACITY_NORMAL_CLOSE',steps=1,capacity=41,virtual_seconds=60,board_actions=0,
 final_partial_batch_durable=True,durable_finish_before_close=True,exactly_one_close=True,restart_reads_final_receipts=True,no_duplicate_full_archives=True)
(T/'RESULT.json').write_text(json.dumps(result,indent=2));(P/'evidence/latest_normal_close.txt').write_text(str(T));print(json.dumps(result,indent=2))
