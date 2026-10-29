from pathlib import Path
import sys,json,time
P=Path(__file__).resolve().parents[1]
s=(P/'tests/test_ring.py').read_text();s=s[:s.index('# Control and model negatives;')]
s=s.replace("'cpu_'+time.strftime", "'cpu_writer_fault_'+time.strftime")
exec(compile(s,str(P/'tests/test_ring.py'),'exec'),globals())
virtual=Clock()
class FaultRuntime(Runtime):
 def control(self):
  c=super().control();original=c.write_inputs
  def stage_and_fail(*a,**kw):
   result=original(*a,**kw)
   self.owner['ram_records']._fail(OSError('injected disk writer failure after721staged'))
   return result
  c.write_inputs=stage_and_fail;return c
fixture=T/'fixture';fixture.mkdir();shutil.copy2(BASE/'initial_state.bin',fixture/'initial_state.bin')
with patch('offline_check.verify',return_value={'evidence':'CPU_FIXTURE_ONLY'}),patch('direct_input.DirectAreaInput.render',return_value=np.frombuffer(raw_records[0][128:3012],'<f4').copy()):
 try:live_board.execute(fixture,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000002',runtime_factory=FaultRuntime,send=lambda *a:None,window_factory=lambda c:RunWindow(c,virtual.clock,virtual.sleep))
 except RuntimeError as e:assert 'batch writer failed' in str(e)
 else:raise AssertionError('writer failure must stop finalization')
name,rt=next(iter(live_board._RETAINED.items()));out=T/'producer'/name
assert rt.mm.read(0x14)==0 and rt.mm.read(0x18)==721 and rt.mm.read(0x4c)==0 and not rt.mm.acks
assert not rt.video.closed and rt.video.frames==1 and rt.control_obj.failed
j=rt.owner['ram_records'];assert j.get(out/'capture/bound/000000/PREPARED.bin')
assert json.loads(j.get(out/'IN_DOUBT.json'))['automatic_retry'] is False
assert not (out/'FINISH.json').exists() and not (out/'CAMERA_CLOSE.json').exists()
result=dict(status='PASS_CPU_WRITER_FAILURE_AFTER_INPUT_STAGING',steps=0,staged_words=721,releases=0,retained_prepared_input=True,camera_close_attempted=False,finish_published=False,board_operations=0)
(P/'evidence/STAGING_FAULT_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
