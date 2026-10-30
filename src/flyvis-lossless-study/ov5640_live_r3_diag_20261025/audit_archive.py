"""Audit only received prefix, never fabricate a normal completion receipt."""
from pathlib import Path
import sys,json,shutil,subprocess,statistics,hashlib
import numpy as np
P=Path(__file__).resolve().parent;R=P.parent/'ov5640_live_r3_20261025';B=R/'bundle'
sys.path.insert(0,str(B));from live_protocol import load_packet,unpack,sha
from ps_input import PsInput
c=json.loads((R/'pc/session.json').read_text());count=32
raw=P/'archive_fcf094ea/raw';O=P/'archive_fcf094ea/full_audit';O.mkdir();work=O/'oracle_bundle';work.mkdir()
for name in ['edges.bin','meta.hex','initial_state.bin']:shutil.copyfile(B/name,work/name)
previous=sha((B/'initial_state.bin').read_bytes());matched_pc=0
mapper=PsInput(480,800,'BGR');inputs=[];states=[];rows=[];commands=[]
for k in range(count):
 wire=load_packet(raw,k);m,s,r=unpack(wire,c)
 assert m['run_id']=='RUN_dcd2298f2d084619be2b202d457f23db'
 assert m['previous_state_sha256']==previous
 previous=sha(r.state_bits)
 d=raw/'capture/bound'/('%06d'%k)
 assert (d/'input.bin').read_bytes()==(d/'actual_input.bin').read_bytes()==r.input_bits
 assert (d/'actual_state.bin').read_bytes()==r.state_bits
 pc=R/'pc/records'/('%06d.packet'%k)
 if pc.exists():
  assert pc.read_bytes()==wire
  matched_pc+=1
 x=mapper.render(np.frombuffer(s,np.uint8).reshape(480,800,3)).astype('<f4').tobytes()
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
r=dict(status='PASS_SAVED32_ALL_STATES_CLOSE_NOT_COMPLETED' if mismatch==0 else 'FAIL_NUMERICAL',
 run_id=m['run_id'],saved_steps=count,expected_steps=32,state_words_compared=count*45669,mismatch_words=mismatch,
 input_words_compared=count*721,matching_previously_received_packets=matched_pc,
 final_receipt_available=(raw/'FINISH.json').exists(),normal_camera_close_verified=False,
 evidence='OFFLINE_CPU_AUDIT_OF_OPERATOR_PHYSICAL_RECORDS',automatic_full_run_PASS=False,rows=rows,
 missing='Normal camera close and final transfer receipts; step32 recovered from read-only export',board_operations=0,
 archive_sha256=sha((P/'archive_fcf094ea/RUN_dcd2298f2d084619be2b202d457f23db_READONLY_fcf094ea.zip').read_bytes()),
 trusted_oracle_sha256=sha((B/'reference.exe').read_bytes()),expected_feedback='Previous oracle result, never substituted board output')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(O/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
