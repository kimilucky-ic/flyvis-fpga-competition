"""CPU encoding only, using saved real PS MMIO event scalars."""
import importlib.util,json,statistics,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
from ps_commit_evidence import encoded_mmio,MMIO_EVENTS
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
root=G/'runtime/joint/7f111da4437843539eeffef2c6c2546e'
h=load(root/'hardware_handoff.json');f=Path(h['software_package'])/'a3latency485/evidence_journal.py'
spec=importlib.util.spec_from_file_location('encoding_saved_reader',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.JournalReader(root/'ps_retrieved_authorized/evidence.fvej')
records=[json.loads(x) for x in r.read('events.jsonl').splitlines() if json.loads(x)['event'] in MMIO_EVENTS]
values=[(r['event'],r['monotonic_ns'],{k:v for k,v in r.items() if k not in ('event','monotonic_ns')}) for r in records]
original=lambda e,t,v:(json.dumps(dict(event=e,monotonic_ns=t,**v))+'\n').encode('utf8')
assert all(encoded_mmio(*v)==original(*v) for v in values)
rows=[]
for repeat in range(6):
    for fast in ((False,True) if repeat%2==0 else (True,False)):
        fn=encoded_mmio if fast else original;start=time.perf_counter_ns();total=0
        for args in values:total+=len(fn(*args))
        rows.append(dict(repeat=repeat,fast=fast,elapsed_ms=(time.perf_counter_ns()-start)/1e6,bytes=total))
medians={str(f):statistics.median(x['elapsed_ms'] for x in rows if x['fast']==f) for f in (False,True)}
v=dict(evidence='CPU_SAVED_SCALAR_JSON_ENCODING_ONLY',records=len(records),all_bytes_identical=True,rows=rows,median_ms=medians,
    cpu_speedup=medians['False']/medians['True'],limits='PC CPU encoder microbenchmark, not ARM timing or joint speed. Original register accesses and checks unchanged.',
    board_connections=0,GPU_runs=0)
(P/'CPU_COMPARISON.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps({k:v[k] for k in ('evidence','records','all_bytes_identical','median_ms','cpu_speedup')},indent=2))
