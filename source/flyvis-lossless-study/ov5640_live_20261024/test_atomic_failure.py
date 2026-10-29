import json,sys,time
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
import live_protocol as lp
T=P/'evidence'/('atomic_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
c=json.loads((P/'pc/session.json').read_text());old=Path((P/'evidence/latest_cpu.txt').read_text());raw=(old/'receiver/000000.packet').read_bytes()
s=lp.Store(T/'records',c);real=lp.atomic

def failed_ack_storage(path,data):real(path,data);raise OSError('injected after durable rename, before in-memory commit')
with patch.object(lp,'atomic',failed_ack_storage):
 try:s.accept(raw)
 except OSError:pass
 else:raise AssertionError('not injected')
assert len(s.meta)==0 and (T/'records/000000.packet').read_bytes()==raw
m,source,r=lp.unpack(raw,c);m['timing']={'different':1};conflict=lp.pack(m,source,raw[-lp.RECORD_BYTES:])
try:s.accept(conflict)
except ValueError:pass
else:raise AssertionError('durable record overwritten')
assert (T/'records/000000.packet').read_bytes()==raw
s.accept(raw);assert len(s.meta)==1 and s.accept(raw)['duplicate']
assert len(lp.Store(T/'records',c).meta)==1
(T/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_DURABLE_RENAME_FAILURE_IDEMPOTENCE',
 existing_record_not_overwritten=True,same_packet_retry_recovers=True,receiver_restart_recovers=True,hardware_actions=0),indent=2))
print('PASS_ATOMIC_FAILURE',T)
