from pathlib import Path
s=Path(__file__).with_name('test_live.py').read_text()
s=s[:s.index('import builtins')].replace("'cpu_'+time.strftime","'cpu_disk_guard_'+time.strftime")
exec(compile(s,'CPU_disk_guard_setup','exec'),globals())
class FaultRuntime(Runtime):
 def control(self):
  c=super().control();write=c.write_inputs
  def stage_then_disk_failure(*a,**kw):
   result=write(*a,**kw)
   self.owner['record_worker'].error=OSError('CPU injected asynchronous disk failure after721 writes')
   return result
  c.write_inputs=stage_then_disk_failure;return c
out=live_board.execute(B,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000003',runtime_factory=FaultRuntime,send=offline,upload_wait=0,window_factory=virtual_window)
rt=next(iter(live_board._RETAINED.values()))
assert rt.mm.steps==0 and rt.mm.read(0x18)==721 and rt.video.k==1
assert not events.count('close') and rt.owner['bridge'].failed
assert (out/'capture/bound/000000/PREPARED.bin').exists()
assert json.loads((out/'RESULT.json').read_text())['status']=='STOPPED_KEEP_KERNEL_AND_BUFFERS'
result=dict(status='PASS_CPU_ASYNC_DISK_FAILURE_PREVENTS_STEP_AFTER_INPUT_STAGING',fake_steps=0,staged_words=721,
 prepared_input_retained=True,board_actions=0,reset_retry_close=False)
(T/'RESULT.json').write_text(json.dumps(result,indent=2));(P/'evidence/latest_disk_guard.txt').write_text(str(T));print(json.dumps(result,indent=2))
