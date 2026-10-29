"""Verify delivery without importing any hardware entry."""
import ast,base64,hashlib,json,subprocess,sys,time,zipfile,io
from pathlib import Path
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
from offline_check import verify
T=P/'evidence'/('package_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
identity=verify(B)
nb=json.loads((P/'LINE11_OFFICIAL_LIVE_R2.ipynb').read_text(encoding='utf-8'));cells=[x for x in nb['cells'] if x['cell_type']=='code'];assert len(cells)==1
code=''.join(cells[0]['source']);tree=ast.parse(code,feature_version=(3,8));values={}
for n in tree.body:
 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):
  try:values[n.targets[0].id]=ast.literal_eval(n.value)
  except ValueError:pass
raw_node=next(n.value.args[0] for n in tree.body if isinstance(n,ast.Assign) and n.targets[0].id=='_raw')
raw=base64.b64decode(ast.literal_eval(raw_node));assert raw==(P/'LINE11_OFFICIAL_LIVE_R2_OFFLINE.zip').read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert len(z.namelist())==len(values['_hashes'])
 for name,h in values['_hashes'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
 assert z.read('flyvis_official.bit')==(B/'flyvis_official.bit').read_bytes()
 assert z.read('flyvis_official.hwh')==(B/'flyvis_official.hwh').read_bytes()
config=json.loads((P/'pc/session.json').read_text());assert values['_config']==config
# Execute the real cell extraction in a fresh process; replace only final board import with a capture stub.
sandbox=T/'notebook_files';sandbox.mkdir()
patched=code.replace('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R2',str(sandbox.resolve()).replace('\\','/'))
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
# Frozen accepted release and original software stay byte-identical.
old=P.parent/'ov5640_official_release_r2_20261024';m=json.loads((old/'FINAL_MANIFEST_SHA256.json').read_text())['files']
for n,v in m.items():
 f=old/n;assert f.stat().st_size==v['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256'],n
reuse=json.loads((P/'REUSE.json').read_text())
external_changes=[];verified_reused=0
for n,h in reuse['files'].items():
 actual=hashlib.sha256(Path(n).read_bytes()).hexdigest()
 if actual!=h:
  # Shared main GUI can advance in another lane; it is not used by this isolated entry.
  assert Path(n).name in ('server.py','line11_stream.py'),n
  external_changes.append(dict(path=n,prior_sha256=h,current_sha256=actual,used_by_candidate=False))
 else:verified_reused+=1
frozen=json.loads((P/'BASELINE_PRESERVED.json').read_text())
for n,v in frozen['files'].items():
 data=(Path(frozen['source'])/n).read_bytes();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256'],n
unchanged=['flyvis_official.bit','flyvis_official.hwh','initial_state.bin','edges.bin','meta.hex','reference.exe','reference.cpp','host_reference.cpp','official_iic21.py','ddr_control.py','ddr_memory.py']
for n in unchanged:assert (B/n).read_bytes()==(old/'bundle'/n).read_bytes(),n
for f in B.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
s=json.loads((P/'assets/spatial.json').read_text());assert len(s['ids'])==len(set(s['ids']))==5768 and min(s['ids'])>=0 and max(s['ids'])<45669
assert (P/'.cmd_32295f30.cmd').is_file()
r=dict(status='PASS_EXPORTED_NOTEBOOK_AND_PRESERVATION_CPU_ONLY',members=len(values['_hashes']),old_release_files_unchanged=len(m),
 original_software_files_matching_prior_snapshot=verified_reused,external_unused_gui_changes=external_changes,
 accepted_live_r1_files_unchanged=len(frozen['files']),unchanged_critical_members=unchanged,notebook_single_code_cell=True,
 fresh_process_extraction=True,repeated_cell_rejected=True,arm_python38_syntax=True,actual_ARM_executed=False,board_actions=0,identity=identity)
(T/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(P/'evidence/latest_package.txt').write_text(str(T));print(json.dumps(r,indent=2))
