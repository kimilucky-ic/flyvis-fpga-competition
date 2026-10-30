"""Execute actual exported cell on CPU with only output path and declined prompt injected."""
import json,subprocess,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/'evidence/notebook_cpu';O.mkdir(exist_ok=False)
nb=json.loads((R/'LINE11_OFFICIAL_FULL_20261024.ipynb').read_text(encoding='utf-8'))
assert len(nb['cells'])==2 and sum(c['cell_type']=='code' for c in nb['cells'])==1
code=''.join(nb['cells'][1]['source']);delivery=json.loads((R/'DELIVERY.json').read_text())
assert hashlib.sha256((R/'LINE11_OFFICIAL_FULL_20261024.ipynb').read_bytes()).hexdigest()==delivery['notebook_sha256']
# The ZIP and extraction/integrity code are identical; no fake PYNQ is imported.
base=O/'extracted';adapted=code.replace("Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_FULL_20261024')",'Path('+repr(str(base.resolve()))+')')
adapted=adapted.replace('operator_entry.run(_root)',"operator_entry.run(_root,ask=lambda _: '取消',base=Path("+repr(str(base.resolve()))+"),boot='00000000-1111-2222-3333-444444444444')")
(O/'cell_cpu.py').write_text(adapted,encoding='utf-8')
runner='''import sys,platform,json
from pathlib import Path
platform.machine=lambda:'armv7l'
p=Path(sys.argv[1]);g={};exec(compile(p.read_text(encoding='utf-8'),'exported_notebook_cell','exec'),g)
assert 'pynq' not in sys.modules
assert not list(Path(sys.argv[2]).glob('ATTEMPT*'))
try:exec(compile(p.read_text(encoding='utf-8'),'exported_notebook_cell','exec'),g)
except RuntimeError as e:assert 'Already attempted' in str(e)
else:raise AssertionError('repeat accepted')
from offline_check import verify
verify(g['_root'])
(g['_root']/'reference.cpp').write_text('tamper')
try:exec(compile(p.read_text(encoding='utf-8'),'exported_notebook_cell','exec'),{})
except RuntimeError as e:assert 'Existing file differs' in str(e)
else:raise AssertionError('changed extracted member accepted')
print('PASS_EXPORTED_CELL_EXTRACTION_CANCEL_REPEAT_TAMPER_CPU_ONLY')
'''
(O/'runner.py').write_text(runner)
p=subprocess.run([sys.executable,'-B',str(O/'runner.py'),str(O/'cell_cpu.py'),str(base)],capture_output=True,timeout=30)
(O/'notebook.log').write_bytes(p.stdout+p.stderr);p.check_returncode()
# Restore the intentional test mutation only in the new CPU extraction, then use
# this newly extracted package's real PC verifier on saved fake-device evidence.
pkg=next(base.glob('package_*'));(pkg/'reference.cpp').write_bytes((R/'bundle/reference.cpp').read_bytes())
good=Path((R/'evidence/cpu_r4/good_run.txt').read_text())
cmd=[sys.executable,'-X','utf8','-B',str(pkg/'verify_result.py'),str(good)+'_RESULT.zip',str(O/'fresh_pc_acceptance')]
p=subprocess.run(cmd,capture_output=True,timeout=60);(O/'fresh_pc.log').write_bytes(p.stdout+p.stderr);p.check_returncode()
bad=adapted.replace("hexdigest()!='"+delivery['zip_sha256']+"'","hexdigest()!='"+'0'*64+"'",1)
assert bad!=adapted
(O/'bad_payload.py').write_text(bad,encoding='utf-8')
p=subprocess.run([sys.executable,'-X','utf8','-B',str(O/'bad_payload.py')],capture_output=True,timeout=30)
(O/'bad_payload.log').write_bytes(p.stdout+p.stderr)
assert p.returncode!=0 and b'Payload hash mismatch' in p.stderr
result=dict(status='PASS_EXPORTED_NOTEBOOK_AND_FRESH_PACKAGE_CPU_ONLY',checks=['payload extraction/member hashes','operator decline no marker/no hardware import','same-kernel repeat refused','existing changed member refused','corrupt payload refused','fresh-extracted PC CLI checks all45669 states'],state_words_compared=45669,board_operations=0,notebook_sha256=delivery['notebook_sha256'],injections='CPU output path/platform and declined prompt only; full device flow tested separately with fake MMIO/DMA')
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
