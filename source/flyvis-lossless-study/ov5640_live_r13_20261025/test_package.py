"""Verify delivery without importing any hardware entry."""
import ast,base64,hashlib,json,subprocess,sys,time,zipfile,io
from pathlib import Path
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
from offline_check import verify
T=P/'evidence'/('package_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
identity=verify(B)
nb=json.loads((P/'LINE11_OFFICIAL_LIVE_R13.ipynb').read_text(encoding='utf-8'));cells=[x for x in nb['cells'] if x['cell_type']=='code'];assert len(cells)==1
code=''.join(cells[0]['source']);tree=ast.parse(code,feature_version=(3,8));values={}
for n in tree.body:
 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):
  try:values[n.targets[0].id]=ast.literal_eval(n.value)
  except ValueError:pass
raw_node=next(n.value.args[0] for n in tree.body if isinstance(n,ast.Assign) and n.targets[0].id=='_raw')
raw=base64.b64decode(ast.literal_eval(raw_node));assert raw==(P/'LINE11_OFFICIAL_LIVE_R13_OFFLINE.zip').read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert len(z.namelist())==len(values['_hashes'])
 for name,h in values['_hashes'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
 assert z.read('flyvis_official.bit')==(B/'flyvis_official.bit').read_bytes()
 assert z.read('flyvis_official.hwh')==(B/'flyvis_official.hwh').read_bytes()
config=json.loads((P/'pc/session.json').read_text());assert values['_config']==config
# Execute the real cell extraction in a fresh process; replace only final board import with a capture stub.
sandbox=T/'notebook_files';sandbox.mkdir()
patched=code.replace('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R13',str(sandbox.resolve()).replace('\\','/'))
runner='''import builtins,json,types
from pathlib import Path
original_import=builtins.__import__
context={}
def importer(name,*a,**k):
 if name=='live_board':
  def run(root,config):
   context['called']=True;context['root']=str(root);context['config']=config
  return types.SimpleNamespace(__file__=str(context['scope']['_root']/'live_board.py'),run=run)
 return original_import(name,*a,**k)
builtins.__import__=importer
scope={};context['scope']=scope
code=%r
exec(code,scope)
assert context['called']
try:exec(code,scope)
except RuntimeError as e:assert 'Already attempted' in str(e)
else:raise AssertionError('repeat allowed')
print('PASS_REAL_NOTEBOOK_EXTRACTION_ENTRY_INTERCEPT_AND_REPEAT_GUARD')
'''%patched
(T/'execute_cell_cpu.py').write_text(runner,encoding='utf-8')
p=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'execute_cell_cpu.py')],capture_output=True,timeout=30)
(T/'cell.log').write_bytes(p.stdout+p.stderr);p.check_returncode()

old=P.parent/'ov5640_live_r12_20261025'
frozen=json.loads((P/'BASELINE_PRESERVED.json').read_text())
for name,digest in frozen.items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==digest,name
unchanged=['flyvis_official.bit','flyvis_official.hwh','edges.bin','meta.hex','initial_state.bin','reference.exe',
           'ddr_memory.py','live_transport.py','live_protocol.py']
for name in unchanged:assert (B/name).read_bytes()==(old/'bundle'/name).read_bytes(),name
import live_board,step_profile as prof
try:live_board.execute(B,T,config,authorized=False)
except RuntimeError:pass
else:raise AssertionError('missing authorization accepted')
assert not live_board._RETAINED and not prof.ENABLED
from camera_diagnostic import source_excerpts
source='def readframe():\n    return 1\n'
excerpt=source_excerpts({'vdma.py':dict(source=source,sha256=hashlib.sha256(source.encode()).hexdigest())})
assert excerpt['files']['vdma.py']['functions'][0]['name']=='readframe'
# Actual optional capture diagnostic with CPU ndarray frame and fake video only.
import numpy as np
from board_runtime import CheckedVideo
class Frame(np.ndarray):
    def __new__(cls):
        x=np.zeros((48,80,3),np.uint8).view(cls);x.physical_address=0x2000000;x.coherent=False;return x
    def invalidate(self):pass
class Video:
    def readframe(self):return Frame()
mem=type('Memory',(),dict(base=0x100000, size=188416*32))()
cv=CheckedVideo(Video(),mem,lambda:None,T,diagnostics=True)
cv.readout_count=3;cv.readframe();assert not list(T.glob('CAMERA_CALLTREE*'))
cv.readframe();d=json.loads((T/'CAMERA_CALLTREE_000004.json').read_text());assert d['function_count'] and len(d['functions'])<=128
assert not list(T.glob('CAMERA_BUFFER*')) and not prof.ENABLED
assert config['diagnostics'] is False and config['camera_diagnostics'] is True
assert config['camera_width']==80 and config['camera_height']==48 and config['port']==8794
assert 'VIDEO_DRIVER_SOURCE.json' in (B/'live_board.py').read_text()
for f in B.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
# Timing wrapper adds only clocks; MMIO addresses/values/order unchanged.
class Control:
    def init__(self):self.writes=[]
    def _w(self,a,v):self.writes.append((a,v))
    def publication(self):return 7
    def write_inputs(self):
        for k in range(721):self._w(0x400+4*k,k)
    def advance(self):
        self.write_inputs()
        self._w(0,1);return self.publication()
c=Control();timing=live_board.Timings();timing.control(c);assert c.advance()==7
assert c.writes==[(0x400+4*k,k) for k in range(721)]+[(0,1)]
assert 'input_721_mmio_write_ms' in timing.values and 'publication_read_ms' in timing.values
r=dict(status='PASS_R13_OPERATOR_PACKAGE_CPU_ONLY',identity=identity,single_cell=True,
 fresh_extraction_and_repeat_guard=True,no_authorization_no_runtime=True,
 camera_diagnostic_only_selected_frames=True,full_profiler_default=False,old_cpu_files_unchanged=len(frozen),
 unchanged_critical_members=unchanged,board_actions=0,native_ARM_executed=False)
(T/'RESULT.json').write_text(json.dumps(r,indent=2));(P/'evidence/latest_package.txt').write_text(str(T));print(json.dumps(r,indent=2))
