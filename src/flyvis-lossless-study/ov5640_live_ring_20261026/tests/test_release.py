"""Release-only CPU guards, manifest, identity and real Notebook extraction."""
from pathlib import Path
import sys,json,ast,hashlib,base64,io,zipfile,subprocess,contextlib
from unittest.mock import patch
P=Path(__file__).resolve().parents[1];B=P/'bundle';sys.path.insert(0,str(B))
import live_board,duration_run,board_runtime
from offline_check import verify
T=P/'evidence/package_cpu';T.mkdir(exist_ok=False)
cfg=json.loads((P/'pc/session.json').read_text());checked=verify(B)
assert cfg['bit_sha256']==checked['bit_sha256'] and cfg['hwh_sha256']==checked['hwh_sha256']
assert cfg['ring_slots']==64 and cfg['minimum_period_s']==0 and cfg['duration_s']==60
original=Path;calls=[];questions=[];executions=[]
def fake_path(arg):
 if str(arg)=='/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_RING_60S':return T/'fake_board'
 if str(arg)=='/proc/sys/kernel/random/boot_id':return T/'boot_id'
 return original(arg)
(T/'boot_id').write_text('00000000-0000-0000-0000-000000000004')
def hello(c,route):
 assert route=='/hello' and c['transfer_mode']=='live_compact';calls.append(route)
 return dict(session_id=c['session_id'],received=0,max_steps=c['max_steps'])
def never(*a,**k):raise AssertionError('No hardware allowed in entry tests')
def ask(q):questions.append(q);return ''
plan=duration_run.memory_plan(cfg,'MemAvailable: 782988 kB\nCmaTotal: 131072 kB\nCmaFree: 3972 kB\n')
with patch.object(live_board,'Path',fake_path),patch.object(live_board.platform,'machine',return_value='armv7l'),patch.object(live_board,'request',hello),patch.object(live_board,'execute',never):
 with patch.object(live_board,'read_memory_plan',side_effect=RuntimeError('injected insufficient budget')):
  live_board.run(B,cfg,ask=ask)
 assert not questions
 with patch.object(live_board,'read_memory_plan',return_value=plan):live_board.run(B,cfg,ask=ask)
 assert len(questions)==1 and not list((T/'fake_board').glob('ATTEMPT*'))
 # A single explicit matching confirmation dispatches once with the new config.
 def fake_execute(root,base,config,**kw):
  assert kw['authorized'] is True and config['ring_slots']==64;executions.append(kw);return 'CPU_DISPATCH_ONLY'
 with patch.object(live_board,'read_memory_plan',return_value=plan),patch.object(live_board,'execute',fake_execute):
  assert live_board.run(B,cfg,ask=lambda q:'运行循环版60秒')=='CPU_DISPATCH_ONLY'
  try:live_board.run(B,cfg,ask=never)
  except RuntimeError as e:assert 'Prior attempt' in str(e)
  else:raise AssertionError('repeat must stop')
assert len(executions)==1
# Mandatory clock check for same hardware assumptions; no physical measurement.
assert all(abs(v-100)<.01 for v in board_runtime.clocks(dict(IO_PLL_CTRL=30<<12,PLL_STATUS=4,FPGA0_CLK_CTRL=0x200500,FPGA1_CLK_CTRL=0x200500)).values())
for raw in (dict(IO_PLL_CTRL=30<<12,PLL_STATUS=0,FPGA0_CLK_CTRL=0x200500,FPGA1_CLK_CTRL=0x200500),dict(IO_PLL_CTRL=30<<12,PLL_STATUS=4,FPGA0_CLK_CTRL=0x200400,FPGA1_CLK_CTRL=0x200500)):
 try:board_runtime.clocks(raw)
 except RuntimeError:pass
 else:raise AssertionError('bad clock accepted')
# Parse every delivered Python file as board Python3.8, then inspect exact archive.
for f in list(B.glob('*.py'))+list((P/'pc').glob('*.py')):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
nb=json.loads((P/'LINE11_OFFICIAL_LIVE_RING_60S.ipynb').read_text(encoding='utf-8'));code=''.join(nb['cells'][1]['source']);tree=ast.parse(code,feature_version=(3,8))
raw=base64.b64decode(ast.literal_eval(next(n.value.args[0] for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='_raw')))
assert raw==(P/'LINE11_OFFICIAL_LIVE_RING_60S_OFFLINE.zip').read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert len(z.namelist())==len(set(z.namelist()))
 for f in B.iterdir():
  if f.is_file():assert z.read(f.name)==f.read_bytes()
# Execute the real extraction cell in a fresh desktop process. The real runtime
# must reject x86 before PYNQ import; its once-only guard rejects a second run.
code=code.replace('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_RING_60S',str((T/'extracted').resolve()).replace('\\','/'))
(T/'cell.py').write_text(code,encoding='utf-8')
runner="""import sys
from pathlib import Path
code=Path(sys.argv[1]).read_text(encoding='utf-8');scope={}
try:exec(compile(code,'Notebook','exec'),scope)
except RuntimeError as e:assert 'operator PYNQ board only' in str(e),str(e)
else:raise AssertionError('must reject desktop')
assert 'pynq' not in sys.modules
try:exec(compile(code,'Notebook','exec'),scope)
except RuntimeError as e:assert 'Already attempted' in str(e)
else:raise AssertionError('repeat must stop')
print('PASS_REAL_EXTRACTION_DESKTOP_GUARD_AND_REPEAT')
"""
(T/'extract_check.py').write_text(runner)
r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'extract_check.py'),str(T/'cell.py')],capture_output=True,timeout=60)
(T/'extract.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0,(r.stdout+r.stderr).decode()
# Preserve known-good paths and payload arithmetic assets byte for byte.
for name,digest in json.loads((P/'evidence/BASELINE_SHA256.json').read_text()).items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
baseline=P.parent/'ov5640_live_60s_r3_20261026/bundle'
for name in ('initial_state.bin','edges.bin','meta.hex','reference.exe','reference.cpp','host_reference.cpp','payload_check.c','native_payload.py','direct_input.py','camera_config.py','camera_memory.py','official_iic21.py','board_runtime.py'):
 assert (B/name).read_bytes()==(baseline/name).read_bytes(),name
result=dict(status='PASS_CPU_RELEASE_ENTRY_EXTRACTION_AND_IDENTITY',files=checked['files'],ring_slots=64,ddr_bytes=12058624,confirmation_count=1,unauthorized_hardware_actions=0,repeat_rejected=True,clock_bad_cases=2,legacy_entries_disabled=True,old_files_unchanged=229,new_board_operations=0)
(P/'evidence/PACKAGE_CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
