"""All32 R2 wire records rebuilt from original retained files; corruption and retry cases."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json,sys,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
from live_protocol import *
from live_transport import Uploader
import live_transport
old=P.parent/'ov5640_live_r2_20261025';config=json.loads((old/'pc/session.json').read_text());source_store=Store(old/'pc/records',config)
T=P/'evidence'/('index_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir();out=T/'producer';(out/'transport').mkdir(parents=True)
old_bytes=new_bytes=0
for k in range(32):
 m,source,r=source_store.read(k);packet=(old/'pc/records'/('%06d.packet'%k)).read_bytes();record=packet[-188416:]
 d=out/'capture/bound'/('%06d'%k);d.mkdir(parents=True)
 for name,data in [('source_frame.bin',source),('record.bin',record),('PREPARED.json',canonical(m['prepared'])),('COMMITTED.json',canonical(m['committed']))]:atomic(d/name,data)
 bridge=SimpleNamespace(failed=False,binding=SimpleNamespace(failed=False,next=k+1,last_committed=(source,r,canonical(m['prepared']),canonical(m['committed']))),last_record_bytes=record)
 index=index_from_committed(bridge,k,config,m,m['previous_state_sha256'],m['timing'])
 encoded=canonical(index);atomic(out/'transport'/('%06d.ready.json'%k),encoded)
 assert load_packet(out,k)==packet and index['packet_sha256']==sha(packet)
 old_bytes+=len(packet);new_bytes+=len(encoded)
assert not list((out/'transport').glob('*.packet'));tests=[]
def reject(label,fn):
 try:fn()
 except (ValueError,FileNotFoundError):tests.append(label)
 else:raise AssertionError(label)
# Restore only test fixtures after each injected error; baseline is read-only.
d=out/'capture/bound/000000';source=(d/'source_frame.bin').read_bytes();commit=(d/'COMMITTED.json').read_bytes();prep=(d/'PREPARED.json').read_bytes()
(d/'source_frame.bin').write_bytes(bytes([source[0]^1])+source[1:]);reject('source corruption',lambda:load_packet(out,0));(d/'source_frame.bin').write_bytes(source)
(d/'source_frame.bin').write_bytes(source[:-1]);reject('truncated source',lambda:load_packet(out,0));(d/'source_frame.bin').write_bytes(source)
(d/'COMMITTED.json').write_bytes(b'{}');reject('changed committed receipt',lambda:load_packet(out,0));(d/'COMMITTED.json').write_bytes(commit)
(d/'PREPARED.json').write_bytes(b'{}');reject('changed prepared receipt',lambda:load_packet(out,0));(d/'PREPARED.json').write_bytes(prep)
ready=out/'transport/000000.ready.json';idx=ready.read_bytes();ready.rename(ready.with_suffix('.json.pending'))
assert load_packet(out,0) is None;tests.append('partial ready marker is not publishable');ready.with_suffix('.json.pending').rename(ready)
x=json.loads(idx);x['step_id']=1;ready.write_bytes(canonical(x));reject('wrong index step',lambda:load_packet(out,0));ready.write_bytes(idx)
# ACK lost: retain one immutable assembled packet; re-create uploader to model sender restart.
receiver=Store(T/'receiver',config);calls=[];reads=[];lost=[True];loader=load_packet

def send(c,route,data):
 calls.append(sha(data))
 if route=='/finish':return receiver.finish(json.loads(data))
 a=receiver.accept(data)
 if lost[0]:lost[0]=False;raise TimeoutError('ACK lost after durable receiver save')
 return a

def counted(out,k):reads.append(k);return loader(out,k)
u=Uploader(out,config,send)
with patch.object(live_transport,'load_packet',counted):
 try:u.attempt()
 except TimeoutError:pass
 assert u.next==0 and len(receiver.meta)==1
 assert u.attempt() and reads==[0] and u.next==1
restart=Uploader(out,config,send);assert restart.attempt() and len(receiver.meta)==1
assert len(set(calls))==1;tests.append('lost ACK and sender restart reuse identical packet without duplicate record')
# Finish timing snapshot is durable and remains identical after a sender restart.
(out/'FINISH.json').write_bytes(canonical(source_store.final))
for k in range(1,32):assert u.attempt()
u.done.set();u.attempt();assert u.finish_sent and len(receiver.final['transfer_timings'])==32
frozen_finish=(out/'TRANSFER_FINISH.json').read_bytes()
resume=Uploader(out,config,send)
for k in range(32):assert resume.attempt()
resume.done.set();resume.attempt();assert resume.finish_sent
assert (out/'TRANSFER_FINISH.json').read_bytes()==frozen_finish and canonical(receiver.final)==frozen_finish
tests.append('final32 transfer timing receipt immutable across sender restart')
result=dict(status='PASS_CPU_DURABLE_INDEX_ACTUAL32_AND_FAILURES',source_run=source_store.final['run_id'],
 packets_byte_identical=32,old_duplicate_packet_bytes=old_bytes,new_ready_index_bytes=new_bytes,
 eliminated_duplicate_write_bytes=old_bytes-new_bytes,retained_source_and_record_files=True,negative_and_retry_cases=tests,
 one_packet_cache_on_retry=True,network_neural_commands=0,board_actions=0)
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_index.txt').write_text(str(T));print(json.dumps(result,indent=2))
