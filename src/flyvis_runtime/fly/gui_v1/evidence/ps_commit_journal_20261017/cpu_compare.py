"""Two alternating saved32 CPU/dummy-MMIO trials per PS evidence policy."""
import json,statistics,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
from test_ps_commit_evidence import PSCommitTests
PSCommitTests.setUpClass();rows=[]
for trial in range(2):
    for policy in ((False,True) if trial==0 else (True,False)):
        t=PSCommitTests('test_32_steps_have_64_barriers_and_bounded_pending');c=t.make(n=32,policy=policy)
        before=c.e.journal.snapshot();began=time.perf_counter_ns()
        try:
            t.run_service(c);elapsed=(time.perf_counter_ns()-began)/1e6;after=c.e.journal.snapshot()
            assert c.d.requests==c.d.commits==32 and c.d.pending is None
            # Exclude the strict HELLO RX and ATTEST TX, common to both.
            expected=64 if policy else 128
            assert after['fsync_calls']-before['fsync_calls']-2==expected
            rows.append(dict(policy='TWO_COMMIT_ACK' if policy else 'FOUR_WIRE',trial=trial,
                software_replay_ms=elapsed,normal_step_fsync_calls=expected,handshake_fsync_calls=2,
                fsync_ms=(after['phase_ns'].get('fsync',0)-before['phase_ns'].get('fsync',0))/1e6,
                max_pending_bytes=c.e.max_pending_bytes if policy else None,
                source='saved actual32 payload/candidate, unchanged original service/driver, dummy MMIO',capture_path=str(c.e.journal.path)))
            t.finish(c)
        finally:t.doCleanups()
v=dict(status='PASS_CPU_ONLY_NOT_PS_SPEED_MEASUREMENT',rows=rows,
    summary={p:dict(count=2,p50_software_replay_ms=statistics.median([r['software_replay_ms'] for r in rows if r['policy']==p])) for p in ('FOUR_WIRE','TWO_COMMIT_ACK')},
    board_connections=0,real_MMIO=0,GPU_runs=0,camera_starts=0,new_neural_computations=0,
    limits='Host filesystem and fake registers; cannot predict SD card latency or actual joint speed. No artificial delay.')
(P/'CPU_COMPARISON.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v['summary'],indent=2))
