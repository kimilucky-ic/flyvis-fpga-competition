from pathlib import Path
import sys,json,ast,base64,io,zipfile,hashlib,contextlib
from unittest.mock import patch
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
import live_board,duration_run
config=json.loads((P/'pc/session.json').read_text());actual_Path=Path
base=P/'evidence/fake_board_directory'
def map_path(arg):
 return base if str(arg)=='/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_60S' else actual_Path(arg)
requests=[];questions=[]
def request(c,route):
 assert route=='/hello' and c['transfer_mode']=='live_compact'
 requests.append(route);return dict(session_id=c['session_id'],received=0,max_steps=c['max_steps'])
def ask(q):questions.append(q);return ''
def never_execute(*a,**k):raise AssertionError('hardware execution reached')
low='MemTotal: 512000 kB\nMemAvailable: 300000 kB\nCmaTotal: 65536 kB\nCmaFree: 60000 kB\n'
low_diag=io.StringIO()
with patch.object(live_board,'Path',map_path),patch.object(live_board.platform,'machine',return_value='armv7l'),patch.object(live_board,'request',request),patch.object(live_board,'execute',never_execute),patch.object(duration_run,'Path') as proc,contextlib.redirect_stdout(low_diag):
 proc.return_value.read_text.return_value=low
 assert live_board.run(B,config,ask=ask) is None
assert questions==[] and requests==['/hello'] and not list(base.glob('ATTEMPT*'))
assert 'LINE11_MEMORY_DIAGNOSTIC' in low_diag.getvalue() and 'candidate_slots=' in low_diag.getvalue() and 'LINE11_MEMORY_PREFLIGHT_STOP' in low_diag.getvalue()
high='MemTotal: 512000 kB\nMemAvailable: 400000 kB\nCmaTotal: 262144 kB\nCmaFree: 262144 kB\n'
high_diag=io.StringIO()
with patch.object(live_board,'Path',map_path),patch.object(live_board.platform,'machine',return_value='armv7l'),patch.object(live_board,'request',request),patch.object(live_board,'execute',never_execute),patch.object(duration_run,'Path') as proc,contextlib.redirect_stdout(high_diag):
 proc.return_value.read_text.return_value=high
 assert live_board.run(B,dict(config,transfer_mode='after_run'),ask=ask) is None
assert len(questions)==1 and '运行60秒相机完整网络' in questions[0] and '输出方式' not in questions[0]
assert not list(base.glob('ATTEMPT*')) and not live_board._RETAINED
# All three snapshots have identical planning capacity, not an allocation claim.
plans=[]
for free in (3972,21504,0):
 raw='MemAvailable: 782988 kB\nCmaTotal: 131072 kB\nCmaFree: %d kB\n'%free
 plan=duration_run.memory_plan(config,raw);plans.append(plan)
 assert plan['slots']==534 and plan['ddr_bytes']==100614144
 assert plan['contiguous_allocation_not_proven'] and plan['actual_allocation_attempts']==1
 assert abs(plan['maximum_start_rate_hz']-533/60)<1e-10
assert len({x['minimum_period_s'] for x in plans})==1
# Deadline and loop implementation are unchanged, not another neural architecture.
previous=P.parent/'ov5640_live_60s_r2_20261026/bundle/live_board.py'
def function_source(text,name):
 return ast.get_source_segment(text,next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name))
assert function_source(previous.read_text(encoding='utf-8'),'execute')==function_source((B/'live_board.py').read_text(encoding='utf-8'),'execute')

# Delivery contents and Python3.8 grammar; unchanged neural/control assets.
nb=json.loads((P/'LINE11_OFFICIAL_LIVE_60S_R3.ipynb').read_text(encoding='utf-8'));code=''.join(nb['cells'][1]['source']);tree=ast.parse(code,feature_version=(3,8))
rawnode=next(n.value.args[0] for n in tree.body if isinstance(n,ast.Assign) and n.targets[0].id=='_raw');raw=base64.b64decode(ast.literal_eval(rawnode))
assert raw==(P/'LINE11_OFFICIAL_LIVE_60S_R3_OFFLINE.zip').read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 for f in B.iterdir():
  if f.is_file():assert z.read(f.name)==f.read_bytes()
for f in B.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
old=P.parent/'ov5640_live_60s_r2_20261026';frozen=json.loads((P/'BASELINE_RELEASE_SHA256.json').read_text())
for name,h in frozen.items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==h
changes=[f.name for f in B.iterdir() if f.is_file() and f.read_bytes()!=(old/'bundle'/f.name).read_bytes()]
assert set(changes)=={'live_board.py','duration_run.py','release_manifest.json'},changes
# No new session/token/port, so the already-running fresh PC receiver remains compatible.
assert (P/'pc/session.json').read_bytes()==(old/'pc/session.json').read_bytes()
(P/'evidence/low_memory_cpu.log').write_text(low_diag.getvalue(),encoding='utf-8')
(P/'evidence/sufficient_memory_cancel_cpu.log').write_text(high_diag.getvalue(),encoding='utf-8')
r=dict(status='PASS_CPU_R3_SINGLE_CONFIRM_AND_CMA_BUDGET',low_memory_asks=0,sufficient_memory_asks=1,
 no_output_mode_question=True,default_mode='live_compact',no_hardware_execution=True,board_operations=0,
 CmaFree_not_a_hard_limit=True,actual_allocation_still_required=True,existing_PC_receiver_compatible=True,
 changed_runtime_files=['live_board.py','duration_run.py'],old_release_files_preserved=len(frozen))
(P/'evidence/RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
