"""CPU failure/retry tests. No PYNQ, camera or board connection."""
from pathlib import Path
import sys,json,copy,shutil,hashlib,ast,base64,io,zipfile,subprocess
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
import live_server,round_sessions as rs
from offline_check import verify
cfg=json.loads((P/'pc/session.json').read_text());actual=live_server.App(cfg,P/'pc/records');assert rs.admission(actual)[0]
negative=[]
for name,change in [
 ('unfinished',lambda x:setattr(x.store,'final',None)),
 ('camera_failed',lambda x:x.store.camera_close.update(status='FAILED',camera_closed=False)),
 ('audit_pending',lambda x:setattr(x,'audit_result',None)),
 ('mismatch',lambda x:x.audit_result.update(mismatch_words=1)),
 ('audit_count',lambda x:x.audit_result.update(steps=1)),
 ('DDR_not_released',lambda x:x.store.final['context']['NEURAL_AFTER.json'].update({'0x50':1})),
 ('wrong_session',lambda x:x.store.camera_close.update(session_id='wrong'))]:
 x=copy.copy(actual);x.store=copy.copy(actual.store);x.store.final=copy.deepcopy(actual.store.final);x.store.camera_close=copy.deepcopy(actual.store.camera_close);x.audit_result=copy.deepcopy(actual.audit_result);change(x);assert not rs.admission(x)[0],name;negative.append(name)
T=E/'cpu_r2';T.mkdir(exist_ok=False);shutil.copytree(P/'bundle',T/'bundle');shutil.copy2(P/rs.NOTEBOOK,T/rs.NOTEBOOK);(T/'pc').mkdir();shutil.copy2(P/'pc/session.json',T/'pc/session.json')
def factory(config,records):
 if records==T/'pc/records':return actual
 return live_server.App(config,records)
r=rs.Rounds(T,factory);old=cfg['session_id'];original_atomic=rs.atomic
# Failure before pointer publication must retain the old receiver; retry reuses pending files.
def fail_pointer(path,data):
 if Path(path)==r.pointer:raise OSError('injected pointer disk failure')
 return original_atomic(path,data)
with patch.object(rs,'atomic',fail_pointer):
 try:r.advance(old)
 except OSError:pass
 else:raise AssertionError('disk failure not surfaced')
assert r.current is actual and not r.pointer.exists();pending=list((T/'pc/rounds').iterdir());assert len(pending)==1
r=rs.Rounds(T,factory)
with ThreadPoolExecutor(max_workers=4) as ex:replies=list(ex.map(lambda _:r.advance(old),range(4)))
assert len({x['session_id'] for x in replies})==1 and sum(not x['duplicate'] for x in replies)==1
sid=replies[0]['session_id'];assert r.current.config['token']!=cfg['token'] and len(r.current.store.meta)==0
assert not rs.admission(r.current)[0]
try:r.advance(sid)
except ValueError:pass
else:raise AssertionError('unfinished successor can be skipped')
reopened=rs.Rounds(T,factory);assert reopened.current.config['session_id']==sid and reopened.advance(old)['duplicate']
nb=json.loads(reopened.notebook_path(reopened.current).read_text(encoding='utf-8'));code=''.join(nb['cells'][1]['source']);tree=ast.parse(code,feature_version=(3,8))
assign={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
assert ast.literal_eval(assign['_config'])==reopened.current.config
raw=base64.b64decode(ast.literal_eval(assign['_raw'].args[0]));B=T/'extracted';B.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert set(z.namelist())=={p.name for p in (P/'bundle').iterdir() if p.is_file()}
 for name in z.namelist():assert Path(name).name==name; (B/name).write_bytes(z.read(name))
assert verify(B)['bit_sha256']==cfg['bit_sha256']
base=rs.BOARD_BASE+'/SESSION_'+sid
assert "base=Path('"+base+"')" in (B/'live_board.py').read_text();assert base in code
for p in (P/'bundle').iterdir():
 if p.is_file() and p.name not in ['live_board.py','release_manifest.json']:assert p.read_bytes()==(B/p.name).read_bytes(),p.name
for text in ["if list(base.glob('ATTEMPT_*.json'))","h.get('received')!=0","authorized=True"]:assert text in (B/'live_board.py').read_text()
# Execute real new Notebook on desktop; must stop before importing hardware drivers.
cell=code.replace(base,(T/'notebook_extract').as_posix());(T/'cell.py').write_text(cell,encoding='utf-8')
check="""import sys
from pathlib import Path
scope={};code=Path(sys.argv[1]).read_text(encoding='utf-8')
try:exec(code,scope)
except RuntimeError as e:assert 'operator PYNQ board only' in str(e)
else:raise AssertionError('desktop allowed')
assert 'pynq' not in sys.modules
try:exec(code,scope)
except RuntimeError as e:assert 'Already attempted' in str(e)
else:raise AssertionError('repeat allowed')
"""
(T/'check.py').write_text(check);proc=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'check.py'),str(T/'cell.py')],capture_output=True,timeout=60);assert proc.returncode==0,(proc.stdout+proc.stderr).decode()
for p in (P/'pc').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),feature_version=(3,8))
result=dict(status='PASS_CPU_NEXT_ROUND_GATES_IDEMPOTENCE_RECOVERY_NOTEBOOK',negative_admission_cases=negative,disk_failure_before_publish_recovered=True,concurrent_requests=4,created_successors=1,restart_and_lost_response_idempotent=True,new_pending_round_cannot_skip=True,notebook_firmware_same=True,only_board_base_path_changed=True,real_notebook_desktop_and_repeat_guards=True,board_actions=0)
(E/'CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
