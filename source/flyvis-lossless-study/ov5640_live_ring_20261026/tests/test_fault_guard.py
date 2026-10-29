from pathlib import Path
import sys,ast,json,time
P=Path(__file__).resolve().parents[1]
s=(P/'tests/test_ring.py').read_text();s=s[:s.index('# Control and model negatives;')]
s=s.replace("'cpu_'+time.strftime","'cpu_fault_'+time.strftime")
exec(compile(s,str(P/'tests/test_ring.py'),'exec'),globals())
virtual=Clock()
class FaultRuntime(Runtime):
 def control(self):
  c=super().control();original=c.write_inputs
  def stage_and_fail(*a,**kw):
   result=original(*a,**kw);self.owner['record_worker'].error=OSError('injected worker failure after721staged');return result
  c.write_inputs=stage_and_fail;return c
fixture=T/'fixture';fixture.mkdir();shutil.copy2(BASE/'initial_state.bin',fixture/'initial_state.bin')
config['max_steps']=256
with patch('offline_check.verify',return_value={'evidence':'CPU_FIXTURE_ONLY'}),patch('direct_input.DirectAreaInput.render',return_value=np.frombuffer(raw_records[0][128:3012],'<f4').copy()):
 out=live_board.execute(fixture,T/'producer',config,authorized=True,boot_id='00000000-0000-0000-0000-000000000002',runtime_factory=FaultRuntime,send=lambda *a:None,window_factory=lambda c:RunWindow(c,virtual.clock,virtual.sleep))
rt=next(iter(live_board._RETAINED.values()));result=json.loads((out/'RESULT.json').read_text())
assert rt.mm.read(0x14)==0 and rt.mm.read(0x18)==721 and rt.mm.read(0x4c)==0 and not rt.mm.acks
assert result['status']=='STOPPED_KEEP_KERNEL_AND_BUFFERS' and not rt.video.closed and rt.video.frames==1
assert (out/'capture/bound/000000/PREPARED.bin').exists()
# An old append-only buffer-free convenience must never be used for ring reuse.
from ddr_memory import OwnedDdr
rejects(lambda:OwnedDdr.release_after_verified_full(object(),None,64))
record=dict(status='PASS_CPU_ASYNC_WORKER_FAILURE_AFTER_STAGING_NO_STEP_NO_RELEASE',fake_steps=0,staged_words=721,releases=0,prepared_input_saved=True,board_operations=0,buffer_free_disabled=True)
(T/'RESULT.json').write_text(json.dumps(record,indent=2));(P/'evidence/latest_fault.txt').write_text(str(T));print(json.dumps(record))
