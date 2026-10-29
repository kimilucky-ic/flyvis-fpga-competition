"""Bounded standard-library CPU I/O probe. No torch, sockets, GPU, camera or board.

Read the exact frozen source pins from the unused 2026-10-16 preparation.
Compare the same 26 source bytes through /mnt/c and a fresh WSL-native directory.
No model/parameter/state file is copied, changed or computed.
"""
import hashlib,json,os,statistics,tempfile,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
GUI=HERE.parents[1]
scope=json.loads((GUI/'runtime/joint/34e96b4d227f488bb3214190089569d1/scope.json').read_text())
assert os.name=='posix' and str(GUI).startswith('/mnt/c/'), 'Run this CPU-only probe in WSL'
native=Path(tempfile.mkdtemp(prefix='line2-cpu-source-probe-'))
pins=scope['source_sha256'];paths=[]
for name,digest in pins.items():
    original=GUI/name;data=original.read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest, 'SOURCE_CHANGED '+name
    target=native/name;target.write_bytes(data);paths.append((name,original,target,digest))

def case(kind,location):
    started=time.perf_counter_ns();cpu=time.thread_time_ns();reads=stats=resolves=0
    for name,original,target,digest in paths:
        path=original if location=='Windows_mnt_c' else target
        if kind=='resolve_and_SHA':
            path=path.resolve();resolves+=1
            assert hashlib.sha256(path.read_bytes()).hexdigest()==digest;reads+=1
        elif kind=='one_stat':
            stamp=path.stat();observed=(stamp.st_size,stamp.st_mtime_ns);stats+=1
            assert observed[0]>0
        else:
            observed=(path.stat().st_size,path.stat().st_mtime_ns);stats+=2
            assert observed[0]>0
    return dict(kind=kind,location=location,wall_ms=(time.perf_counter_ns()-started)/1e6,
        thread_cpu_ms=(time.thread_time_ns()-cpu)/1e6,reads=reads,stats=stats,resolves=resolves)

rows=[]
for iteration in range(6):
    for kind in ('resolve_and_SHA','two_stats','one_stat'):
        # Alternate order so the first filesystem is not always the same.
        order=('Windows_mnt_c','WSL_native') if iteration%2==0 else ('WSL_native','Windows_mnt_c')
        for location in order:rows.append(dict(iteration=iteration,**case(kind,location)))
summary=[]
for kind in ('resolve_and_SHA','two_stats','one_stat'):
    for location in ('Windows_mnt_c','WSL_native'):
        selected=[r for r in rows if r['kind']==kind and r['location']==location]
        summary.append(dict(kind=kind,location=location,count=len(selected),
            p50_ms=statistics.median(r['wall_ms'] for r in selected),max_ms=max(r['wall_ms'] for r in selected),
            p50_thread_cpu_ms=statistics.median(r['thread_cpu_ms'] for r in selected)))
for name,original,target,digest in paths:
    assert hashlib.sha256(original.read_bytes()).hexdigest()==hashlib.sha256(target.read_bytes()).hexdigest()==digest
result=dict(status='PASS_CPU_SOURCE_IO_MICROBENCH_ONLY',model_steps=0,source_files=len(paths),
    source_bytes=sum(p[1].stat().st_size for p in paths),native_copy=str(native),
    identical_source_bytes_before_and_after=True,production_files_modified=False,
    limits='Six warm-cache repetitions; source files only. Not an actual joint-run speedup or attribution of historical outliers.',
    summary=summary,rows=rows)
(HERE/'CPU_PATH_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2),flush=True)
