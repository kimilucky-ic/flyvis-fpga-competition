from pathlib import Path
import sys,json,threading,ast,base64,io,zipfile,hashlib
from types import SimpleNamespace
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from offline_check import verify
from live_protocol import Store
from round_sessions import Rounds,notebook
S=P.parent/'ov5640_live_v261_20261026';a=json.loads((S/'pc/ACTIVE_ROUND.json').read_text());d=S/'pc/rounds'/a['session_id'];cfg=json.loads((d/'session.json').read_text());store=Store(d/'records',cfg)
old=SimpleNamespace(store=store,config=cfg,audit_running=False,audit_result=json.loads((d/'records/audit/RESULT.json').read_text()))
r=Rounds.__new__(Rounds);r.root=P;r.pc=P/'evidence/round_test';r.pc.mkdir(exist_ok=False);r.pointer=r.pc/'ACTIVE_ROUND.json';r.lock=threading.RLock();r.current=old
r.factory=lambda c,p:SimpleNamespace(config=c,store=Store(p,c))
result=r.advance(cfg['session_id'],'white_black');fresh=r.current
assert fresh.config['motion_condition']=='white_black';assert not fresh.store.meta
assert r.advance(cfg['session_id'],'white_black')['duplicate']
try:r.advance(cfg['session_id'],'black_white')
except ValueError:pass
else:raise AssertionError('mode change on retry must reject')
payload=notebook(P,fresh.config)[0];assert payload==(r.directory(fresh.config['session_id'])/'LINE11_OFFICIAL_LIVE_V261_60S.ipynb').read_bytes()
tree=ast.parse(''.join(json.loads(payload)['cells'][1]['source']),feature_version=(3,8))
raw=base64.b64decode(ast.literal_eval(next(x.value.args[0] for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='_raw')))
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 manifest=json.loads(z.read('release_manifest.json'))
 for name,v in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==v['sha256']
 assert b'source_pixels_retained=True' in z.read('live_protocol.py')
 assert b'line11-batch-save' in z.read('batch_records.py')
checked=verify(P/'bundle')
(P/'evidence/ROUND_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ROUND_AND_PACKAGE',same_mode_retry_idempotent=True,different_mode_retry_rejected=True,deterministic_payload=True,package=checked,board_actions=0),indent=2))
print('PASS round mode selection, retry protection, archive seal, same firmware and network dimensions')
