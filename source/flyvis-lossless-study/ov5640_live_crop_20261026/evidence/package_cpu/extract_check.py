import sys
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
