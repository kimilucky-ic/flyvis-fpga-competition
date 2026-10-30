import sys,json,time,threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
import live_protocol as lp,live_transport as lt,record_worker as rw,ram_records,step_profile as prof
from capture_binding import save_capsule
from snapshot_records import decode_record
T=P/'evidence'/('lean_'+time.strftime('%Y%m%d_%H%M%S'));T.mkdir()
run=Path((P/'evidence/latest_cpu.txt').read_text());result=json.loads((run/'RESULT.json').read_text());out=Path(result['producer_output'])
cfg=json.loads((P/'pc/session.json').read_text());ctx=json.loads((out/'RUN_CONTEXT.json').read_text())
blob=lp.load_packet(out,0);m,_,r=lp.unpack(blob,cfg);raw=blob[-188416:]
bridge=SimpleNamespace(failed=False,last_record_bytes=raw,binding=SimpleNamespace(failed=False,next=1,
    last_committed=(bytes(80*48*3),r,m['prepared'],m['committed'])))
checks=[]
with patch.object(lp,'sha',wraps=lp.sha) as h:
    wire=lp.packet_from_committed(bridge,0,cfg,ctx,cfg['initial_state_sha256'],m['timing'])
    assert h.call_count==0
assert wire==blob
checks.append('packing reuses decoded payload hashes; no image or record SHA; byte-identical immutable packet')
# Known digest reused for ACK and retransmission. File reader does not rebuild packet.
up=lt.Uploader(out,cfg,send=lambda c,route,data:dict(step_id=0,sha256=lp.sha(data),durable=True))
up.digests[0]=lp.sha(blob)
with patch.object(lt,'sha',side_effect=AssertionError('redundant sender hash')):
    assert up.attempt() and up.next==1
checks.append('sender reuses saved digest; no repeated ACK hash')
# Event wake waits without a poll timeout, then processes newly available data.
w=lt.Uploader(T/'wake',cfg);w.out.mkdir();waiting=threading.Event();available=threading.Event();calls=[];timeouts=[]
old_wait=w.wake.wait
def observe_wait(timeout=None):timeouts.append(timeout);waiting.set();return old_wait(timeout)
w.wake.wait=observe_wait
def attempt():
    calls.append(1)
    if available.is_set():w.finish_sent=True
    return False
w.attempt=attempt;w.start();assert waiting.wait(2);assert len(calls)==1
available.set();w.wake.set();w.thread.join(2);assert not w.thread.is_alive() and w.finish_sent and timeouts==[None]
checks.append('idle uploader has event wait with no200ms timer; new record wakes it')
# Authoritative packet replaces duplicate commit only after exact payload present.
root=T/'records';root.mkdir();j=ram_records.RamRecords(root);j.start();ram_records.CURRENT=j
d=root/'capture/bound/000000';save_capsule(d/'PREPARED.bin',m['prepared'],r.input_bits);save_capsule(d/'COMMITTED.bin',m['committed'],raw)
worker=rw.RecordWorker(root,cfg,ctx,[])
worker.submit(bridge,0,cfg['initial_state_sha256'],m['timing'],{});worker.drain()
assert j.key(d/'COMMITTED.bin') not in j.files and j.get(root/'transport/000000.packet')==blob
assert j.key(d/'PREPARED.bin') in j.files
checks.append('one full-state representation retained after successful packet build; prepared inputs retained')
# Failure before packet is ready retains original full record and prevents further work.
root2=T/'fail';root2.mkdir();j2=ram_records.RamRecords(root2);j2.start();ram_records.CURRENT=j2
d2=root2/'capture/bound/000000';save_capsule(d2/'COMMITTED.bin',m['committed'],raw)
with patch.object(rw,'packet_from_committed',side_effect=ValueError('injected packing failure')):
    f=rw.RecordWorker(root2,cfg,ctx,[])
    try:f.submit(bridge,0,cfg['initial_state_sha256'],m['timing'],{})
    except RuntimeError:pass
    try:f.drain()
    except RuntimeError:pass
    else:raise AssertionError('failed packing admitted')
assert j2.get(d2/'COMMITTED.bin').endswith(raw) and f.failed_job is not None
checks.append('failed packing keeps raw complete record and stops progression')
ram_records.CURRENT=None
# Wrong proposed replacement must not remove retained source.
j3=ram_records.RamRecords(T/'bounds');j3.start();d3=j3.root/'COMMITTED.bin';p3=j3.root/'a.packet';j3.put(d3,b'original');j3.put(p3,b'wrong')
try:j3.retire_duplicate_commit(d3,p3,b'original')
except RuntimeError:pass
else:raise AssertionError('incorrect replacement accepted')
assert j3.get(d3)==b'original'
checks.append('duplicate retirement rejects mismatched full-state replacement')
prof.begin();prof.add('unused',prof.tick());assert prof.snapshot()=={}
assert not list(out.glob('CAMERA_BUFFER*.json')) and not list(out.glob('capture/bound/*/TIMING.json'))
checks.append('lean profile disabled; no per-step diagnostic sidecars')
# On-disk recovery needs only original prepared input + authoritative packet.
s=lp.Store(T/'offline_receiver',cfg)
for k in range(32):
    data=lp.load_packet(out,k);s.accept(data)
    from capture_binding import read_capsule
    pre,inp=read_capsule(out/'capture/bound'/('%06d'%k)/'PREPARED.bin',2884)
    meta,_,rr=s.read(k);assert meta['prepared']==pre and rr.input_bits==inp
assert len(s.meta)==32
checks.append('offline reload binds all32 prepared inputs to all saved state packets')
flush=json.loads((out/'RAM_FLUSH.json').read_text())
(T/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_LEAN_NEGATIVE_AND_RETENTION_ONLY',tests=checks,flush=flush,board_actions=0),indent=2))
(P/'evidence/latest_lean.txt').write_text(str(T));print(json.dumps(dict(tests=checks,flush=flush),indent=2))
