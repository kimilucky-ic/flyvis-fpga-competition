from pathlib import Path
import hashlib,json,ast,sys,zipfile,io,base64
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';B=R/'bundle'
m=json.loads((O/'before/bundle/release_manifest.json').read_text())
for name,v in m.items():
 raw=(B/name).read_bytes();digest=hashlib.sha256(raw).hexdigest()
 if name in ['ram_records.py','live_board.py']:m[name]=dict(bytes=len(raw),sha256=digest)
 else:assert digest==v['sha256'],name
(B/'release_manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
s=json.loads((O/'before/FINAL_MANIFEST_SHA256.json').read_text('utf-8'));changed=['bundle/ram_records.py','bundle/live_board.py','bundle/release_manifest.json']
for k,v in s.items():
 digest=hashlib.sha256((R/Path(k)).read_bytes()).hexdigest()
 if k.replace('\\','/') in changed:s[k]=digest
 else:assert digest==v,k
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
sys.path[:0]=[str(R/'pc'),str(B)]
from offline_check import verify
from round_sessions import notebook
check=verify(B);sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];config=json.loads((R/'pc/rounds'/sid/'session.json').read_text());config['session_id']='00000000000000000000000000000000'
raw,base=notebook(R,config);nb=json.loads(raw);code=''.join(nb['cells'][1]['source']);ast.parse(code,feature_version=(3,8));encoded=next(x for x in code.splitlines() if x.startswith('_raw='));data=base64.b64decode(ast.literal_eval(encoded.split('(',1)[1][:-1]))
with zipfile.ZipFile(io.BytesIO(data)) as z:
 assert z.read('ram_records.py')==(B/'ram_records.py').read_bytes()
 expected=(B/'live_board.py').read_bytes().decode('utf-8').replace("base=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_V261_60S')","base=Path(%r)"%base).encode()
 assert z.read('live_board.py')==expected
 assert z.read('flyvis_official.bit')==(B/'flyvis_official.bit').read_bytes()
(O/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(dict(status='PASS_OFFLINE_PACKAGE_AND_NEXT_NOTEBOOK',changed=changed,sealed_files=len(s),unchanged_sealed_files=len(s)-len(changed),bundle_files=check['files'],bit_sha256=check['bit_sha256'],hwh_sha256=check['hwh_sha256'],next_notebook_generated_in_memory_only=True,board_actions=0),indent=2));print('PASS package; next-round Notebook contains startup optimization; same BIT/HWH')
