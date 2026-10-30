import ast,json
from pathlib import Path
from types import SimpleNamespace
p=Path(__file__).parent
s=(p/'live_server.candidate.py').read_text(); tree=ast.parse(s)
ns={'json':json,'time':SimpleNamespace(sleep=lambda _:None)}
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['read_audit_json','read_audit_progress']:exec(compile(ast.Module(body=[n],type_ignores=[]),'candidate','exec'),ns)
class File:
 def init__(self,items):self.items=list(items);self.calls=0
 def read_text(self):
  self.calls+=1;v=self.items.pop(0)
  if isinstance(v,Exception):raise v
  return v
old={'steps':3};tests=[]
for e in [PermissionError(13,'busy'),FileNotFoundError()]:
 f=File([e]);assert ns['read_audit_progress'](f,old) is old;assert f.calls==1
 tests.append('advisory_'+type(e).__name__)
f=File([PermissionError()]*4+['{"status":"PASS_ALL_SAVED_STATES"}']);assert ns['read_audit_json'](f)['status']=='PASS_ALL_SAVED_STATES';assert f.calls==5;tests.append('result_recovers_within_bound')
f=File([PermissionError()]*5)
try:ns['read_audit_json'](f);raise AssertionError('not stopped')
except PermissionError:assert f.calls==5
tests.append('persistent_permission_fails_closed')
for name in ['read_audit_json','read_audit_progress']:
 try:ns[name](File(['broken']),old) if name.endswith('progress') else ns[name](File(['broken']));raise AssertionError('bad json accepted')
 except json.JSONDecodeError:pass
 tests.append(name+'_corruption_rejected')
f=File(['{"status":"FAIL_NUMERICAL_MISMATCH","mismatch_words":1}']);assert ns['read_audit_json'](f)['status']=='FAIL_NUMERICAL_MISMATCH';tests.append('mismatch_not_promoted')
# Only monitor-related App method differs; data/ACK/display/status handlers unchanged.
before=ast.parse((p/'live_server.before.py').read_text())
a=next(n for n in before.body if isinstance(n,ast.ClassDef) and n.name=='App');b=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='App')
for x,y in zip(a.body,b.body):
 if x.name!='audit_if_ready':assert ast.dump(x)==ast.dump(y),x.name
for name in ['make_server','main']:
 assert ast.dump(next(n for n in before.body if isinstance(n,ast.FunctionDef) and n.name==name))==ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name))
tests.append('ingest_ACK_display_and_startup_unchanged')
result={'status':'PASS_CPU_FAULT_INJECTION','tests':tests,'board_operations':0,'runtime_restart':False}
(p/'RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
