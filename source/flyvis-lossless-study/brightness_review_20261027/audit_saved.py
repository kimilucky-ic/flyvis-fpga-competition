from pathlib import Path
import sys,json
base=Path('flyvis-lossless-study/ov5640_live_v261_20261026').resolve()
out=Path('flyvis-lossless-study/brightness_review_20261027').resolve()
sys.path.insert(0,str(base/'pc'))
from stream_audit import run
r=run(base/'pc/rounds/6bc6ac2081b14d4296dd007b5aae12f4/records',json.loads((base/'pc/rounds/6bc6ac2081b14d4296dd007b5aae12f4/session.json').read_text()),base/'bundle',out/'audit',out/'AUDIT_PROGRESS.json')
print(json.dumps({k:r[k] for k in ['status','steps','state_words_compared','mismatch_words','source_mapping_audited','elapsed_s']}),flush=True)
