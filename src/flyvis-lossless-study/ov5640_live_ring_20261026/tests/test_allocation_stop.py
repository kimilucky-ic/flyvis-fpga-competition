from pathlib import Path
import sys,json,time
P=Path(__file__).resolve().parents[1];B=P/'bundle';sys.path.insert(0,str(B))
import live_board,board_runtime
from unittest.mock import patch
from ddr_memory import OwnedDdr
from duration_run import memory_plan
config=json.loads((P/'pc/session.json').read_text())
plan=memory_plan(config,'MemAvailable: 782988 kB\nCmaTotal: 131072 kB\nCmaFree: 21504 kB\n')
config['transfer_mode']='local_only'
events=[]
class Control:
 failed=False
 def _r(self,a):return 0
 def restore_initial(self):raise AssertionError('must not restore')
 def configure(self,*a):raise AssertionError('must not configure DDR target')
class Runtime:
 evidence='CPU_MOCK_ONLY'
 def init__(self,root,out):self.owner={}
 def prepare(self):events.append('prepare')
 def load(self):events.append('fake_load')
 def inspect(self):events.append('fake_inspect')
 def control(self):return Control()
 def memory(self,slots):
  assert slots==64
  def fail(**kw):
   events.append('allocate_once');assert kw['shape']==(12058624,)
   raise MemoryError('CPU injected contiguous allocation failure')
  return OwnedDdr(fail,lambda:None,slots)
 def start_camera(self,*a):raise AssertionError('must not start camera')
def offline(*a,**k):raise ConnectionError('CPU no PC transport')
T=P/'evidence'/('allocation_fail_'+time.strftime('%H%M%S'));T.mkdir()
with patch.object(board_runtime,'PynqRuntime',Runtime),patch.object(live_board,'read_memory_plan',return_value=plan):
 out=live_board.execute(B,T,config,authorized=True,boot_id='00000000-0000-0000-0000-000000000003',send=offline,upload_wait=0)
r=json.loads((out/'RESULT.json').read_text());failure=json.loads((out/'IN_DOUBT.json').read_text())
assert events==['prepare','fake_load','fake_inspect','allocate_once'] and failure['phase']=='ALLOCATE_RESTORE'
assert r['completed_steps']==0 and r['status']=='STOPPED_KEEP_KERNEL_AND_BUFFERS'
assert not list(out.glob('PHASE_OFFICIAL*')) and not list(out.glob('PHASE_NORMAL_CAMERA_CLOSE*'))
result=dict(status='PASS_CPU_ONE_ALLOCATION_FAILURE_STOPS_BEFORE_RESTORE_CAMERA_STEP',events=events,neural_steps=0,board_actions=0,automatic_retry=False,output=str(out))
(P/'evidence/ALLOCATION_STOP_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
