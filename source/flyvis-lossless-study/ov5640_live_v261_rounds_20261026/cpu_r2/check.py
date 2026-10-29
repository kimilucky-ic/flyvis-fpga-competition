import sys
from pathlib import Path
scope={};code=Path(sys.argv[1]).read_text(encoding='utf-8')
try:exec(code,scope)
except RuntimeError as e:assert 'operator PYNQ board only' in str(e)
else:raise AssertionError('desktop allowed')
assert 'pynq' not in sys.modules
try:exec(code,scope)
except RuntimeError as e:assert 'Already attempted' in str(e)
else:raise AssertionError('repeat allowed')
