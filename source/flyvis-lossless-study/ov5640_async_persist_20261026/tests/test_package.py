from pathlib import Path
import sys,json,hashlib,ast,io,zipfile,base64,uuid
P=Path('flyvis-lossless-study/ov5640_async_persist_20261026').resolve();R=P.parent/'ov5640_live_v261_20261026'
sha=lambda b:hashlib.sha256(b).hexdigest()
# Canonicalize source text, then seal candidate without changing accepted release.
for p in (P/'bundle').glob('*.py'):
 ast.parse(p.read_text(encoding='utf-8-sig'),feature_version=(3,8))
for name in ('batch_records.py','record_worker.py','live_board.py'):
 p=P/'bundle'/name;p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf-8')
m={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted((P/'bundle').iterdir()) if p.is_file() and p.name!='release_manifest.json'}
(P/'bundle/release_manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
sys.path[:0]=[str(P/'bundle'),str(R/'pc')]
from offline_check import verify
checked=verify(P/'bundle')
from round_sessions import notebook,NOTEBOOK
# Use actual fixed-round builder on this isolated bundle; no board, no session creation.
(P/NOTEBOOK).write_bytes((R/NOTEBOOK).read_bytes())
active=json.loads((R/'pc/ACTIVE_ROUND.json').read_text());sid=active['session_id']
cfg=json.loads((R/'pc/rounds'/sid/'session.json').read_text())
cfg.update(session_id='0'*31+'1',token='CPU_PACKAGE_CHECK_ONLY')
nb,base=notebook(P,cfg);assert notebook(P,cfg)[0]==nb
(P/'evidence/CPU_CANDIDATE_NOTEBOOK.ipynb').write_bytes(nb)
code=''.join(json.loads(nb)['cells'][1]['source']);tree=ast.parse(code,feature_version=(3,8))
raw=base64.b64decode(ast.literal_eval(next(n.value.args[0] for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='_raw')))
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 zm=json.loads(z.read('release_manifest.json'))
 assert set(z.namelist())==set(zm)|{'release_manifest.json'}
 for name,v in zm.items():assert len(z.read(name))==v['bytes'] and sha(z.read(name))==v['sha256']
 for name in m:
  if name!='live_board.py':assert z.read(name)==(P/'bundle'/name).read_bytes()
 assert b'journal.drain()' in z.read('live_board.py')
 assert b'persistence_queue_batches=2' in z.read('live_board.py')
 assert b'line11-batch-save' in z.read('batch_records.py')
changed=[p.name for p in (P/'bundle').iterdir() if p.is_file() and p.read_bytes()!=(P/'before/bundle'/p.name).read_bytes()]
assert set(changed)=={'batch_records.py','record_worker.py','live_board.py','release_manifest.json'}
next_id=uuid.uuid5(uuid.NAMESPACE_URL,'line11-next:'+sid).hex
assert not (R/'pc/rounds'/next_id/NOTEBOOK).exists(),'successor already prepared: do not overwrite it'
result=dict(status='PASS_CPU_PACKAGE_IDENTITY_ONLY',package=checked,changed=sorted(changed),syntax='Python3.8',deterministic_notebook=True,active_round_unchanged=sid,next_round_not_created=True,firmware_changed=False,board_actions=0)
(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(P/'evidence/ACTIVE_BEFORE.json').write_text(json.dumps(active,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
