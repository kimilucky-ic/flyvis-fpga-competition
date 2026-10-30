import json,sys,copy
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from live_protocol import Store,packet_from_committed
old=P.parent/'ov5640_live_20261024';c=json.loads((old/'pc/session.json').read_text());store=Store(old/'pc/records',c)
m,raw,r=store.read(0);record=(old/'pc/records/000000.packet').read_bytes()[-188416:]
context={k:m[k] for k in ('run_id','boot_id','evidence')}
def fresh():return SimpleNamespace(failed=False,binding=SimpleNamespace(failed=False,next=1,
 last_committed=(raw,r,json.dumps(m['prepared']).encode(),json.dumps(m['committed']).encode())),last_record_bytes=record)
def call(b):return packet_from_committed(b,0,c,context,m['previous_state_sha256'],m['timing'])
assert call(fresh())==(old/'pc/records/000000.packet').read_bytes()
checks=[]
for name in ('failed_bridge','failed_binding','stale_step','source_corruption','state_corruption','receipt_corruption'):
 b=fresh()
 if name=='failed_bridge':b.failed=True
 if name=='failed_binding':b.binding.failed=True
 if name=='stale_step':b.binding.next=2
 if name=='source_corruption':b.binding.last_committed=(bytes([raw[0]^1])+raw[1:],)+b.binding.last_committed[1:]
 if name=='state_corruption':
  data=bytearray(record);data[4096]^=1;b.last_record_bytes=bytes(data)
 if name=='receipt_corruption':
  v=dict(m['committed'],state_sha256='0'*64);b.binding.last_committed=b.binding.last_committed[:3]+(json.dumps(v).encode(),)
 try:call(b)
 except ValueError:checks.append(name)
 else:raise AssertionError(name)
(P/'evidence/COMMITTED_CACHE_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_COMMITTED_CACHE_GUARDS',tests=checks,board_actions=0),indent=2))
print('PASS_COMMITTED_CACHE_GUARDS',checks)
