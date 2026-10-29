"""Focused producer stop paths; inject only control/camera boundary fakes."""
import json,sys,time
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
import live_board
from live_protocol import sha
T=P/'evidence'/('stop_paths_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
c=json.loads((P/'pc/session.json').read_text());c=dict(c,minimum_period_s=0)
results=[]
class Control:
 def init__(self):self.failed=False;self.commands=[]
 def _r(self,a):return 0
 def _w(self,a,v):self.commands.append((a,v))
 def restore_initial(self):pass
 def configure(self,*a):pass
 def publication(self):pass
 def advance(self,x):self.commands.append('STEP');raise TimeoutError('uncertain command completion')
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,r,o):self.owner={};self.c=Control();self.closed=False
 def prepare(self):pass
 def load(self):pass
 def inspect(self):return {'FCLK0':100}
 def control(self):return self.c
 def memory(self,slots=1):return SimpleNamespace(pin_before_configure=lambda:None,base=0x1000000,size=slots*188416,copy_record=lambda r:b'')
 def start_camera(self,m):return SimpleNamespace(readframe=lambda:None,close=lambda:None)
class Bridge:
 def init__(self,v,c,m,out,cap,evidence):
  self.control=c;self.mapper=SimpleNamespace(render=lambda x:b'');self.binding=SimpleNamespace(next=0);self.failed=False
 def step(self):self.control.advance(b'input')
 def close_success(self):raise AssertionError('must not close uncertain camera')
def disconnected(*a,**k):raise ConnectionError('offline')
with patch.object(live_board,'OfficialBridge',Bridge):
 out=live_board.execute(B,T/'uncertain',c,authorized=True,boot_id='1',runtime_factory=Runtime,send=disconnected,upload_wait=0)
rt=list(live_board._RETAINED.values())[-1]
assert rt.c.commands==['STEP'] and rt.c.failed and (out/'IN_DOUBT.json').exists()
assert json.loads((out/'RESULT.json').read_text())['completed_steps']==0
try:live_board.execute(B,T/'retry',c,authorized=True,runtime_factory=Runtime)
except RuntimeError:pass
else:raise AssertionError('retry admitted')
results.append('uncertain STEP attempted once, no close/retry, owner retained')
# A persistent binding failure before STEP must stop the producer, not skip ahead.
live_board._RETAINED.clear() # test-only fake owners, never production recovery
class DiskFail(Bridge):
 def step(self):raise OSError('injected evidence disk failure before STEP')
with patch.object(live_board,'OfficialBridge',DiskFail):
 out=live_board.execute(B,T/'disk',c,authorized=True,boot_id='2',runtime_factory=Runtime,send=disconnected,upload_wait=0)
rt=list(live_board._RETAINED.values())[-1];assert rt.c.commands==[] and rt.c.failed
results.append('disk failure before STEP prevents all neural commands')
(T/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_STOP_PATHS_ONLY',tests=results,hardware_actions=0),indent=2))
print('PASS',results,T)
