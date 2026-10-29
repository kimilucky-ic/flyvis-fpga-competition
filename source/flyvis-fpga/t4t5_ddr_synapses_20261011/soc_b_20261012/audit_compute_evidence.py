"""Audit preserved system computation without promoting incomplete system tests."""
from pathlib import Path
import csv, json, hashlib
P=Path(__file__).resolve().parent
B=P/json.loads((P/'LATEST_BUILD.json').read_text())['build']
S=B/'stages/simulate_10'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
count=0
with (S/'system_edges.csv').open() as actual,(B/'rom/edges.mem').open() as image:
    for row, line in zip(csv.reader(actual),image,strict=True):
        record=int(line,16)
        assert int(row[0])==count and int(row[1],16)==record
        assert int(row[2])==record&((1<<21)-1)
        assert int(row[3])==(record>>36)&((1<<13)-1)
        count+=1
assert count==433880
count=0
with (S/'system_candidates.csv').open() as actual,(B/'rom/expected.mem').open() as expected:
    for row,line in zip(csv.reader(actual),expected,strict=True):
        v=int(line,16);v|=0x80000000 if v&0x40000000 else 0
        assert int(row[0])==count and int(row[1],16)==v
        count+=1
assert count==5768
result=dict(status='PASS_FULL_BD_COMPUTATION_ONLY_SYSTEM_ACCEPTANCE_INCOMPLETE',
            ordered_edges=433880,candidate_comparisons=5768,mismatches=0,
            remaining='Control backpressure stimulus was overwritten by the vendor read API; timeout test not yet reached',
            native_PS7_GP0_HP0=True,source_identity= json.loads((S/'IDENTITY.json').read_text())['source_sha256'],
            sha256={n:sha(S/n) for n in ['system_edges.csv','system_candidates.csv','simulate.log','RUNTIME.json']},
            synthesis_allowed=False,board_execution=False)
(S/'FULL_COMPUTATION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','ordered_edges','candidate_comparisons','mismatches']}))
