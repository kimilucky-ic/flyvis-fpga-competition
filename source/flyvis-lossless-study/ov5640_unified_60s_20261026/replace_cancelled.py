from pathlib import Path
import sys,json,uuid,secrets,hashlib,ast
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(R/'bundle'),str(R/'pc')]
from round_sessions import notebook
from live_protocol import Store,atomic,canonical
pointer=R/'pc/ACTIVE_ROUND.json';old=json.loads(pointer.read_text());sid=old['session_id'];assert sid=='b98f33556ff659bf886d5c63be7a9cd4'
p=R/'pc/rounds'/sid;cfg=json.loads((p/'session.json').read_text());s=Store(p/'records',cfg)
assert not s.meta and not s.final and not s.camera_close,'Not empty; do not change session'
assert hashlib.sha256((p/'LINE11_OFFICIAL_LIVE_V261_60S.ipynb').read_bytes()).hexdigest()==old['notebook_sha256']
newid=uuid.uuid4().hex;newcfg=dict(cfg,session_id=newid,token=secrets.token_hex(32),motion_condition='capture');nb,base=notebook(R,newcfg)
q=R/'pc/rounds'/newid;q.mkdir(exist_ok=False)
atomic(q/'session.json',canonical(newcfg));atomic(q/'LINE11_OFFICIAL_LIVE_V261_60S.ipynb',nb)
receipt=dict(schema='line11-active-round/v1',session_id=newid,parent_session_id=sid,previous_records=str((p/'records').resolve()),notebook_sha256=hashlib.sha256(nb).hexdigest(),board_directory=base,board_actions=0,replacement_reason='Operator reported cancellation before hardware authorization; replace empty pending round with unified capture',operator_cancel_independently_observed=False)
atomic(q/'ROUND.json',canonical(receipt));atomic(pointer,canonical(receipt));atomic(O/'REPLACEMENT.json',canonical(receipt))
print('Unified 60s session prepared:',newid[:8],'; old round retained; no board action')
