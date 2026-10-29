import sys,platform,json
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
