"""Read saved PC/PS journals. No sockets, devices, model or NumPy computation."""
import collections,hashlib,importlib.util,json,statistics,struct
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1]
ROOT=G/'runtime/joint/7f111da4437843539eeffef2c6c2546e'
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stats(v):
    a=sorted(v);return dict(count=len(a),p50=statistics.median(a),p95=a[int(.95*(len(a)-1))],max=max(a))
h=load(ROOT/'hardware_handoff.json');a=load(G/'evidence/camera_joint32_20261016/actual_32step/FINAL_AUDIT.json')
f=Path(h['software_package'])/'a3latency485/evidence_journal.py'
assert sha(f)==h['software_sha256']['a3latency485/evidence_journal.py']
spec=importlib.util.spec_from_file_location('step_saved_reader',f);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
pcfile=ROOT/'pc/evidence.fvej';psfile=ROOT/'ps_retrieved_authorized/evidence.fvej'
assert sha(pcfile)==a['PC_capture_sha256'] and sha(psfile)==a['PS_capture_sha256']
pc,ps=mod.JournalReader(pcfile),mod.JournalReader(psfile)
events=[json.loads(b) for b in ps.read('events.jsonl').splitlines()]
rows=[];wire_groups=collections.defaultdict(dict)
for i,e in enumerate(events):
    if e['event'] in ('WIRE_RX','WIRE_TX_INTENT'):
        raw=ps.read(e['file']);op=struct.unpack_from('<H',raw,6)[0];step=struct.unpack_from('<Q',raw,48)[0]
        if op in (1,2,3,5):wire_groups[step][op]=(i,e,raw)
for k in range(32):
    rx=wire_groups[k][1];result=wire_groups[k][2];commit=wire_groups[k][3];ack=wire_groups[k][5]
    section=events[rx[0]:commit[0]]
    def event(name):return next(e for e in section if e['event']==name and e.get('step',k)==k)
    accepted,ready,sent=(event(n) for n in ('REQUEST_ACCEPTED','CANDIDATE_READY','CANDIDATE_SENT'))
    snap=json.loads(pc.read('committed_step_%d.json'%k));tx=snap['transaction']
    ns=lambda e:e['monotonic_ns']
    row=dict(step=k,PC_STEP_inclusive_ms=tx['PC_STEP_roundtrip_ns']/1e6,
        PS_STEP_rx_to_request_accepted_ms=(ns(accepted)-ns(rx[1]))/1e6,
        PS_request_accepted_to_candidate_ready_ms=(ns(ready)-ns(accepted))/1e6,
        PS_candidate_ready_to_RESULT_intent_ms=(ns(result[1])-ns(ready))/1e6,
        PS_RESULT_intent_to_sent_ms=(ns(sent)-ns(result[1]))/1e6,
        PS_STEP_rx_to_candidate_sent_ms=(ns(sent)-ns(rx[1]))/1e6,
        PC_STEP_minus_PS_envelope_ms=tx['PC_STEP_roundtrip_ns']/1e6-(ns(sent)-ns(rx[1]))/1e6,
        PC_COMMIT_inclusive_ms=tx['PC_COMMIT_roundtrip_ns']/1e6,
        PS_COMMIT_rx_to_ACK_intent_ms=(ns(ack[1])-ns(commit[1]))/1e6,
        PS_driver_timing=ready,
        PS_events_in_STEP=collections.Counter(e['event'] for e in section),
        STEP_wire_bytes=len(rx[2]),RESULT_wire_bytes=len(result[2]))
    batches=[b for b in pc.batches if any(r['name'].startswith('wire_') and r['kind']=='file'
        and len(v:=pc.read(r['name']))>=256 and struct.unpack_from('<H',v,6)[0]==1
        and struct.unpack_from('<Q',v,48)[0]==k for r in b['records'])]
    assert len(batches)==1
    row['PC_STEP_before_send_batch']=dict(barrier=batches[0]['barrier'],
        bytes=sum(r['size'] for r in batches[0]['records']),records=[dict(name=r['name'],size=r['size']) for r in batches[0]['records']])
    # Pair same-host event timestamps. These intervals include intent logging;
    # they are not precise AXI read/write bus latency measurements.
    mmio=[]
    for before,after in zip(section,section[1:]):
        if (before['event'] in ('MMIO_READ_INTENT','MMIO_WRITE_INTENT')
                and after['event']==before['event'].replace('INTENT','RETURNED')
                and before['bank']==after['bank'] and before['offset']==after['offset']):
            mmio.append(dict(kind=before['event'],bank=before['bank'],offset=before['offset'],
                elapsed_ms=(ns(after)-ns(before))/1e6))
    row['PS_MMIO_intent_to_return_intervals']=mmio
    row['PS_MMIO_intent_to_return_sum_ms']=sum(x['elapsed_ms'] for x in mmio)
    row['PS_driver_events']=len([e for e in section if ns(accepted)<=ns(e)<=ns(ready)])
    rows.append(row)
summary={name:stats([r[name] for r in rows]) for name in rows[0] if name.endswith('_ms')}
result=dict(evidence='SAVED_REAL_RUN_CLOCK_LOCAL_DURATION_EXTRACTION_NOT_NEW_EXECUTION',run_id=a['run_id'],
    PC_capture_sha256=sha(pcfile),PS_capture_sha256=sha(psfile),rows=rows,summary=summary,
    time_limits='PS spans use PS monotonic only; PC uses PC perf_counter only. Difference of local elapsed envelopes is mixed PC/transport/scheduling residual, not a one-way network latency. CANDIDATE_SENT is after socket send returns and can overlap PC return; no cross-host timestamp subtraction.',
    new_GPU_runs=0,camera_starts=0,board_connections=0,GUI_starts=0)
(P/'SAVED_STEP_BREAKDOWN.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(dict(summary=summary,first_PC_batch=rows[0]['PC_STEP_before_send_batch'],
    first_PS_driver_events=rows[0]['PS_events_in_STEP']),indent=2))
