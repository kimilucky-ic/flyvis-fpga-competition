from pathlib import Path
import ast,hashlib,json,sys
from unittest.mock import patch
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026');E=P.parent/'ov5640_fixed_environment_fix_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
import fixed_entry
fixed_entry.prepare(P)
nb=json.loads((P/fixed_entry.NAME).read_text());code=''.join(nb['cells'][1]['source']);old=''.join(json.loads((E/'before'/fixed_entry.NAME).read_text())['cells'][1]['source'])
a="if not Path('/proc/device-tree/model').exists():raise RuntimeError('Board-only entry; no LOAD')\n"
b="import platform\nfrom importlib.util import find_spec\nif not (platform.system()=='Linux' and platform.machine()=='armv7l' and find_spec('pynq') is not None and Path('/home/xilinx/jupyter_notebooks').is_dir()):raise RuntimeError('Board-only entry; expected ARMv7 PYNQ environment; no LOAD')\n"
assert code==old.replace(a,b);assert '/proc/device-tree' not in code
prefix=code.split('_sid,_payload,_code=fetch_round(',1)[0];ast.parse(code,feature_version=(3,8));cases=[]
for name,system,machine,package,directory,expected in [('reported_pynq_without_device_tree','Linux','armv7l',True,True,True),('windows','Windows','AMD64',True,True,False),('linux_pc','Linux','x86_64',True,True,False),('missing_pynq','Linux','armv7l',False,True,False),('missing_board_directory','Linux','armv7l',True,False,False)]:
 scope={}
 with patch('platform.system',return_value=system),patch('platform.machine',return_value=machine),patch('importlib.util.find_spec',return_value=object() if package else None),patch.object(Path,'is_dir',return_value=directory):
  try:exec(prefix,scope);accepted=True
  except RuntimeError as exc:assert 'Board-only' in str(exc);accepted=False
  assert accepted==expected,name
  try:exec(prefix,scope)
  except RuntimeError as exc:assert 'Restart kernel' in str(exc)
  else:raise AssertionError('repeat allowed')
 cases.append(dict(name=name,accepted=accepted))
seal=json.loads((E/'before/FINAL_MANIFEST_SHA256.json').read_text());changes=['pc\\fixed_entry.py','LINE11_START_60S.ipynb'];unchanged=0
for n,h in seal.items():
 if n not in changes:assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n;unchanged+=1
for n in changes:seal[n]=hashlib.sha256((P/n).read_bytes()).hexdigest()
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
result=dict(status='PASS_CPU_ENVIRONMENT_GUARD_FIX_PHYSICAL_PENDING',cases=cases,repeat_guard_preserved=True,only_guard_changed=True,python38_parse=True,unchanged_sealed_files=unchanged,notebook_sha256=seal['LINE11_START_60S.ipynb'],hardware_actions=0)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
