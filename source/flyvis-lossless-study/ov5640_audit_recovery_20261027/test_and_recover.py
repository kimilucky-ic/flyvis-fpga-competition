from pathlib import Path
import sys,json,hashlib,shutil
from unittest.mock import patch
import numpy as np
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';D=R/'pc/rounds/6bc6ac2081b14d4296dd007b5aae12f4';sys.path.insert(0,str(R/'pc'))
from stream_audit import retry_read,refresh
from live_protocol import Store,sha,canonical,atomic
from round_sessions import admission
config=json.loads((D/'session.json').read_text());rec=D/'records';audit=O.parent/'brightness_review_20261027/audit'
# Bounded transient / permanent / non-permission cases.
waits=[];calls=[]
def transient():
 calls.append(1)
 if len(calls)<3:raise PermissionError('injected temporary lock')
 return b'exact'
assert retry_read(transient,waits.append)==b'exact' and waits==[.05,.1]
waits=[];calls=[]
def permanent():calls.append(1);raise PermissionError('persistent')
try:retry_read(permanent,waits.append);raise AssertionError('must stop')
except PermissionError:pass
assert len(calls)==5 and sum(waits)==.75
try:retry_read(lambda:(_ for _ in ()).throw(ValueError('bad record')),waits.append);raise AssertionError('must stop')
except ValueError:pass
# Real packet refresh: transient lock does not skip or duplicate a step.
fixture=O/'fixture';fixture.mkdir(exist_ok=False);st=Store(fixture,config)
for k in range(3):shutil.copy2(rec/f'{k:06d}.packet',fixture/f'{k:06d}.packet')
original=Path.read_bytes;hits=[0]
def locked(p):
 if p==fixture/'000001.packet' and hits[0]<2:hits[0]+=1;raise PermissionError('injected')
 return original(p)
with patch.object(Path,'read_bytes',locked):assert refresh(st)==3
assert [m['step_id'] for m in st.meta]==[0,1,2] and refresh(st)==3
# Recheck persisted independent audit against every current immutable source packet.
store=Store(rec,config);a=json.loads((audit/'RESULT.json').read_text());assert a['status']=='PASS_ALL_SAVED_STATES' and a['steps']==len(store.meta)==1015 and a['mismatch_words']==0
rows=a['rows'];commands=json.loads((audit/'COMMANDS.json').read_text());last=(R/'bundle/initial_state.bin').read_bytes()
for name in ['edges.bin','meta.hex']:assert (audit/'oracle_bundle'/name).read_bytes()==(R/'bundle'/name).read_bytes()
for cmd in commands:
 first=cmd['first_step'];n=cmd['steps'];assert cmd['initial_expected_sha256']==sha(last) and cmd['returncode']==0
 expected=(audit/f'{first:06d}_expected.bin').read_bytes();assert len(expected)==n*182676
 inputs=[]
 for j in range(n):
  k=first+j;m,source,r=store.read(k);row=rows[k];e=expected[j*182676:(j+1)*182676]
  assert row['step_id']==k and row['input_sha256']==sha(r.input_bits) and row['actual_state_sha256']==sha(r.state_bits)==row['expected_state_sha256']==sha(e)
  assert r.state_bits==e and row['mismatch_words']==0 and row['mapping_max_abs']==0
  inputs.append(r.input_bits)
 assert b''.join(inputs)==(audit/f'{first:06d}_inputs.bin').read_bytes()
 last=expected[-182676:]
from types import SimpleNamespace
allowed,reason=admission(SimpleNamespace(store=store,config=config,audit_result=a,audit_running=False));assert allowed,reason
# Add a provenance receipt; never delete/replace the failed audit or its logs.
target=rec/'audit/RESULT.json';assert not target.exists(),target
receipt=dict(status='VERIFIED_EXISTING_INDEPENDENT_AUDIT',session_id=config['session_id'],source_result=str(audit/'RESULT.json'),source_result_sha256=sha((audit/'RESULT.json').read_bytes()),packet_sha256=store.digests,steps=1015,state_words_compared=46354035,mismatch_words=0,original_online_error_preserved=True,board_actions=0)
atomic(O/'RECOVERY_RECEIPT.json',canonical(receipt));atomic(rec/'AUDIT_RECOVERY_RECEIPT.json',canonical(receipt));atomic(target,canonical(dict(a,recovery_receipt=str(rec/'AUDIT_RECOVERY_RECEIPT.json'))))
atomic(O/'CPU_TEST_RESULT.json',canonical(dict(status='PASS',transient_attempts=3,permanent_attempts=5,max_wait_seconds=.75,invalid_data_not_retried=True,real_packet_refresh_exact3=True,recovery_source_and_expected_feedback_rechecked=True,admission_allowed=True,board_actions=0)))
print('PASS bounded read fault tests;1015steps source and expected feedback rechecked; recovery receipt published')
