"""Audit only received prefix, never fabricate a normal completion receipt."""
from pathlib import Path
import sys,json,shutil,subprocess,statistics,hashlib
import numpy as np
P=Path(__file__).resolve().parent;R=P.parent/'ov5640_live_r3_20261025';B=R/'bundle'
sys.path.insert(0,str(B));from live_protocol import Store,sha
from ps_input import PsInput
c=json.loads((R/'pc/session.json').read_text());store=Store(R/'pc/records',c);count=len(store.meta)
assert store.meta[0]['run_id']=='RUN_dcd2298f2d084619be2b202d457f23db'
O=P/'prefix_audit';O.mkdir();work=O/'oracle_bundle';work.mkdir()
for n in ['edges.bin','meta.hex','initial_state.bin']:shutil.copyfile(B/n,work/n)
mapper=PsInput(480,800,'BGR');inputs=[];states=[];rows=[];commands=[]
for k in range(count):
 m,s,r=store.read(k);x=mapper.render(np.frombuffer(s,np.uint8).reshape(480,800,3)).astype('<f4').tobytes()
 assert x==r.input_bits,(k,'mapping')
 inputs.append(r.input_bits);states.append(r.state_bits);rows.append(dict(step_id=k,input_sha256=sha(r.input_bits),state_sha256=sha(r.state_bits),mapping_bitwise_equal=True))
mismatch=0
for first in range(0,count,3):
 n=min(3,count-first);inp=O/('%06d_input.bin'%first);out=O/('%06d_expected.bin'%first);inp.write_bytes(b''.join(inputs[first:first+n]))
 cmd=[str((B/'reference.exe').resolve()),str(work.resolve()),str(inp.resolve()),str(out.resolve())]
 proc=subprocess.run(cmd,capture_output=True,timeout=60);(O/('%06d_oracle.log'%first)).write_bytes(proc.stdout+proc.stderr);proc.check_returncode();commands.append(cmd)
 expected=out.read_bytes();assert len(expected)==n*182676
 for j in range(n):
  k=first+j;e=expected[j*182676:(j+1)*182676];d=int(np.count_nonzero(np.frombuffer(e,'<u4')!=np.frombuffer(states[k],'<u4')))
  rows[k].update(mismatch_words=d,expected_sha256=sha(e));mismatch+=d
 (work/'initial_state.bin').write_bytes(expected[-182676:])
r=dict(status='PASS_RECEIVED_PREFIX_ONLY_NOT_FULL_RUN' if mismatch==0 else 'FAIL_RECEIVED_PREFIX',
 run_id=store.meta[0]['run_id'],received_steps=count,expected_steps=32,state_words_compared=count*45669,mismatch_words=mismatch,
 final_receipt_available=store.final is not None,normal_camera_close_verified=False,
 evidence='OFFLINE_OPERATOR_RECORD_PREFIX_AUDIT',automatic_full_run_PASS=False,rows=rows,
 missing='Step32 and completion receipt; user output ends at NORMAL_CAMERA_CLOSE',board_operations=0)
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(O/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
