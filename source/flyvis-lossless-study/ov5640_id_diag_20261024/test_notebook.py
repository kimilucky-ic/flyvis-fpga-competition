import builtins,hashlib,json,sys,tempfile,types
from pathlib import Path
P=Path(__file__).resolve().parent
nb=json.loads((P/'OV5640_ID_ONLY_20261024.ipynb').read_text(encoding='utf-8'))
code=''.join(nb['cells'][1]['source'])
base=Path(tempfile.mkdtemp(dir=P,prefix='notebook_extract_'));calls=[]
original=builtins.__import__;oldpath=list(sys.path)
def mapped_path(p):
 if str(p)=='/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG':return base
 return Path(p)
def intercepted(name,*args,**kwargs):
 if name=='pathlib':return types.SimpleNamespace(Path=mapped_path)
 if name=='id_diag':
  root=next(base.glob('package_*'))
  def run(p):
   assert p==root
   assert hashlib.sha256((p/'flyvis_ov5640.bit').read_bytes()).hexdigest()=='781981526e8cc9916c096ff46b92046d90021d56c9438718fe5566cfdf1df7d7'
   calls.append(str(p))
  return types.SimpleNamespace(__file__=str(root/'id_diag.py'),run=run)
 return original(name,*args,**kwargs)
ns={'__builtins__':dict(vars(builtins),__import__=intercepted)}
try:
 exec(compile(code,'actual_exported_notebook','exec'),ns)
 assert len(calls)==1
 try:exec(compile(code,'repeat','exec'),ns)
 except RuntimeError as e:assert 'already used' in str(e)
 else:raise AssertionError('repeat admitted')
 root=next(base.glob('package_*'));(root/'id_diag.py').write_text('corrupted fixture',encoding='utf-8')
 fresh={'__builtins__':dict(vars(builtins),__import__=intercepted)}
 try:exec(compile(code,'corrupt','exec'),fresh)
 except RuntimeError as e:assert 'not overwritten' in str(e)
 else:raise AssertionError('corruption admitted')
 assert (root/'id_diag.py').read_text()=='corrupted fixture'
finally:sys.path[:]=oldpath
r=dict(status='PASS_CPU_NOTEBOOK_EXTRACTION_ONLY',checks=['actual exported cell reaches stub entry with original bit hash','same-cell repeat stopped','changed extracted file stopped without overwrite'],hardware_entry='STUB_NOT_EXECUTED',board_operations=0)
(P/'NOTEBOOK_CPU_RESULT.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
