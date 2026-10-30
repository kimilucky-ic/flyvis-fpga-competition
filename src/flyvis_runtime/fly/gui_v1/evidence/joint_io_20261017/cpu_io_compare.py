"""One bounded CPU storage/loopback comparison. No physical connections.

Replays original bytes/checkpoints; protocol peer is explicitly CPU-only and
never computes or claims a hardware candidate. All sockets bind 127.0.0.1.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import statistics
import sys
import tempfile
import threading
import time
import uuid

OUT=Path(__file__).resolve().parent;GUI=OUT.parents[1];sys.path.insert(0,str(GUI))
from live_protocol import load,sha
from joint_camera_control import hardware_module
from joint_camera_io import tune_client,NativePCJournal
from joint_diagnostics import JointDiagnostics

def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2),encoding='utf8')
def stats(rows):
    rows=sorted(rows)
    return dict(count=len(rows),p50_ms=statistics.median(rows),p95_ms=rows[int(.95*(len(rows)-1))],max_ms=max(rows))

def storage():
    h=load(GUI/'runtime/joint/7f111da4437843539eeffef2c6c2546e/hardware_handoff.json')
    mod=hardware_module(h,'evidence_journal')
    source=GUI/'runtime/joint/7f111da4437843539eeffef2c6c2546e/pc/evidence.fvej'
    original=source.read_bytes();reader=mod.JournalReader(source)
    # Replay exact complete batch packets and every original fsync boundary.
    packets=[];offset=0
    while offset<len(original):
        _,mlen,plen,_=mod.PREFIX.unpack(original[offset:offset+mod.PREFIX.size])
        end=offset+mod.PREFIX.size+mlen+plen
        packets.append(original[offset:end]);offset=end
    assert len(packets)==len(reader.batches)==164 and b''.join(packets)==original
    rows=[];final=[];expected=hashlib.sha256(original).hexdigest()
    native=Path(tempfile.mkdtemp(prefix='line2-native-io-'))
    for iteration in range(2):
        for mode in (('windows','native') if iteration==0 else ('native','windows')):
            path=(OUT if mode=='windows' else native)/('cpu_replay_'+str(iteration))
            path.mkdir(exist_ok=False);target=path/'evidence.fvej';writes=[];syncs=[]
            began=time.perf_counter_ns()
            with target.open('xb',buffering=0) as f:
                for raw in packets:
                    tick=time.perf_counter_ns();view=memoryview(raw)
                    while view:
                        n=f.write(view);assert n and n>0;view=view[n:]
                    f.flush();writes.append((time.perf_counter_ns()-tick)/1e6)
                    tick=time.perf_counter_ns();os.fsync(f.fileno());syncs.append((time.perf_counter_ns()-tick)/1e6)
            elapsed=(time.perf_counter_ns()-began)/1e6
            assert sha(target)==expected
            rows.append(dict(mode=mode,iteration=iteration,total_ms=elapsed,write_ms=stats(writes),
                fsync_ms=stats(syncs),write_sum_ms=sum(writes),fsync_sum_ms=sum(syncs),
                bytes=len(original),fsync_calls=len(syncs),sha256=expected))
    # Real production NativePCJournal, original JournalWriter and verified export.
    export_root=OUT/'cpu_native_export';export_root.mkdir(exist_ok=False)
    d=JointDiagnostics('CPU_IO_EXPORT')
    store=NativePCJournal(export_root,uuid.uuid4().hex,uuid.uuid4().hex,native_base=native/'managed',diagnostics=d)
    w=mod.JournalWriter(store.directory,dict(role='CPU_NO_NEURAL_COMPUTATION'))
    store.attach(w)
    # Same 44MB scale, original durable checkpoints retained; no model update.
    for k in range(32):
        w.add('saved_bytes_%d.bin'%k,original[k*1_300_000:(k+1)*1_300_000]);w.checkpoint('CPU_SAVED_BYTES')
    w.close('CPU_STORAGE_ONLY',completed=0)
    tick=time.perf_counter_ns();receipt=store.export_closed();export_ms=(time.perf_counter_ns()-tick)/1e6
    assert sha(export_root/'pc/evidence.fvej')==receipt['sha256'] and store.source.exists()
    save('CPU_STORAGE_COMPARE.json',dict(status='PASS_CPU_REPLAY_STORAGE_ONLY',source_sha256=expected,
        rows=rows,summary={m:dict(total_ms=stats([r['total_ms'] for r in rows if r['mode']==m])) for m in ('windows','native')},
        production_export=dict(receipt,elapsed_ms=export_ms),native_directory=str(native),
        neural_steps=0,board_connections=0,limits='Warm-cache replay; two alternating trials per path; not physical PC/PS latency or power-loss proof'))

def network():
    r=load(GUI/'hybrid_joint_registry.json')['pins']['v2_protocol']
    path=Path(r['path'].replace('C:\\','/mnt/c/').replace('\\','/'))
    assert sha(path)==r['sha256']
    spec=importlib.util.spec_from_file_location('cpu_io_pinned_protocol',path);w=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=w;spec.loader.exec_module(w)
    server=socket.socket();server.bind(('127.0.0.1',0));server.listen(2);port=server.getsockname()[1]
    received=[];errors=[]
    def peer():
        try:
            for variant in range(2):
                s,_=server.accept();s.settimeout(3)
                with s:
                    for k in range(33):
                        h,p=w.recv_frame(s)
                        if h.op==w.HELLO:
                            a=dict(bit_sha256=w.BIT_SHA,hwh_sha256=w.HWH_SHA,config_sha256=w.CONFIG.hex(),
                                image_pair_sha256=w.IMAGE_PAIR.hex(),asid=h.asid.hex(),hello_txn=h.txn.hex(),
                                pynq_is_loaded=True,boot_id='CPU_ONLY_NO_BOARD',server_session='CPU_LOOPBACK_NO_PL')
                            raw=json.dumps(a).encode()
                            import dataclasses
                            rh=dataclasses.replace(h,op=w.ATTEST,payload_bytes=len(raw),payload_sha=w.digest(raw))
                            w.send_frame(s,rh,raw)
                        elif h.op==w.STEP:
                            assert len(p)==w.INPUT_BYTES;received.append(hashlib.sha256(p).hexdigest())
                            candidate=b'\0'*w.WORD_BYTES
                            import dataclasses
                            rh=dataclasses.replace(h,op=w.RESULT,payload_bytes=len(candidate),payload_sha=w.digest(candidate),compute_cycles=10*w.N+1)
                            w.send_frame(s,rh,candidate)
                        else:raise AssertionError('Unexpected CPU test opcode')
        except BaseException as e:errors.append(repr(e))
        finally:server.close()
    t=threading.Thread(target=peer,daemon=True);t.start();rows=[]
    for variant in ('default','tuned'):
        c=w.Client('127.0.0.1',port);d=JointDiagnostics('CPU_LOOPBACK');proxy=tune_client(c,d) if variant=='tuned' else None
        elapsed=[]
        try:
            for k in range(32):
                # Clear protocol candidate only via original commit/ACK would
                # add extra packets; use independent request/response transport
                # exchanges directly here, explicitly no Coordinator/PL claim.
                h=w.Header(w.STEP,c.asid,uuid.uuid4().bytes,k,bytes(32),w.digest(b'\0'*w.INPUT_BYTES),w.INPUT_BYTES)
                tick=time.perf_counter_ns();result,p=c._exchange(h,b'\0'*w.INPUT_BYTES)
                elapsed.append((time.perf_counter_ns()-tick)/1e6)
                assert result.identity()==h.identity() and result.op==w.RESULT and len(p)==w.WORD_BYTES
            rows.append(dict(variant=variant,summary=stats(elapsed),socket=proxy.summary() if proxy else None))
        finally:c.close()
    t.join(5);assert not t.is_alive() and not errors and len(received)==64 and len(set(received))==1
    save('CPU_TRANSPORT_COMPARE.json',dict(status='PASS_PINNED_PROTOCOL_CPU_LOOPBACK_ONLY',rows=rows,
        requests_per_variant=32,verified_received_payloads=64,neural_steps=0,board_connections=0,
        limits='CPU peer returns zero fixture bytes, no PL or GPU. Loopback transport timing cannot predict physical-network speedup.'))

if __name__=='__main__':
    assert os.name=='posix','Run software-only in WSL; CUDA_VISIBLE_DEVICES=-1'
    storage();network()
    print(json.dumps(dict(storage=load(OUT/'CPU_STORAGE_COMPARE.json')['summary'],
        export_ms=load(OUT/'CPU_STORAGE_COMPARE.json')['production_export']['elapsed_ms'],
        transport=load(OUT/'CPU_TRANSPORT_COMPARE.json')['rows'],torch_imported='torch' in sys.modules),indent=2))
