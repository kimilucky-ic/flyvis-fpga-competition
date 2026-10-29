from pathlib import Path
import ast,json,sys,time
from types import SimpleNamespace
from unittest.mock import patch
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
import live_board
from capture_binding import save_new,save_json
from live_protocol import Store,canonical
T=P/'evidence'/('ready_failure_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
c=json.loads((P/'pc/session.json').read_text());old=P.parent/'ov5640_live_r2_20261025'
s=Store(old/'pc/records',json.loads((old/'pc/session.json').read_text()));m,source,r=s.read(0)
raw=(old/'pc/records/000000.packet').read_bytes()[-188416:]
code=(P/'test_stop_paths.py').read_text();classes='\n'.join(ast.get_source_segment(code,n) for n in ast.parse(code).body if isinstance(n,ast.ClassDef) and n.name in ('Control','Runtime'))
exec(compile(classes,'accepted_cpu_test_runtime','exec'))
class SuccessfulStep:
 def init__(self,v,control,memory,out,capacity,evidence):
  self.control=control;self.output=Path(out);self.failed=False;self.last_record_bytes=raw
  self.binding=SimpleNamespace(next=0,failed=False,last_committed=(source,r,canonical(m['prepared']),canonical(m['committed'])))
  self.mapper=SimpleNamespace(render=lambda x:b'');self.output.mkdir();(self.output/'bound/000000').mkdir(parents=True)
 def step(self):
  d=self.output/'bound/000000'
  for name,data in [('source_frame.bin',source),('input.bin',r.input_bits),('PREPARED.json',canonical(m['prepared']))]:save_new(d/name,data)
  self.control.commands.append('STEP')
  for name,data in [('record.bin',raw),('actual_input.bin',r.input_bits),('actual_state.bin',r.state_bits),('COMMITTED.json',canonical(m['committed']))]:save_new(d/name,data)
  self.binding.next=1
  return SimpleNamespace(frame_id=0,sequence=1,cycles=r.cycles,address=0x1000000,cookie=1)
 def close_success(self):raise AssertionError('must not close on publication uncertainty')
def disconnected(*a,**k):raise ConnectionError('offline')
original=live_board.atomic

def fail_ready(path,data):
 if str(path).endswith('.ready.json'):raise OSError('injected index fsync failure')
 return original(path,data)
with patch.object(live_board,'OfficialBridge',SuccessfulStep),patch.object(live_board,'atomic',fail_ready):
 out=live_board.execute(B,T/'producer',c,authorized=True,boot_id='1',runtime_factory=Runtime,send=disconnected,upload_wait=0)
runtime=list(live_board._RETAINED.values())[-1]
assert runtime.c.commands==['STEP'] and runtime.c.failed and (out/'IN_DOUBT.json').exists()
assert (out/'capture/bound/000000/actual_state.bin').read_bytes()==r.state_bits
assert (out/'capture/bound/000000/record.bin').read_bytes()==raw
assert not list((out/'transport').glob('*.ready.json'))
f=json.loads((out/'FINISH.json').read_text());assert f['hardware_completed_steps']==1 and f['completed_steps']==0
try:live_board.execute(B,T/'retry',c,authorized=True,runtime_factory=Runtime)
except RuntimeError:pass
else:raise AssertionError('retry allowed')
(T/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_READY_PUBLICATION_FAILURE',neural_steps=1,second_step_blocked=True,
 full_state_and_source_preserved=True,no_fake_transfer_completion=True,automatic_retry=False,board_operations=0),indent=2))
print('PASS_READY_FAILURE',T)
