import sys,json,tempfile,zipfile,io,contextlib
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;B=P/'bundle';sys.path.insert(0,str(B))
import operator_entry as op,board_capture as bc
checks=[]
def setup():
 temp=Path(tempfile.mkdtemp(dir=P,prefix='entry_gate_'));(temp/'boot').write_text('CPU_FAKE_BOOT')
 prior=temp/'id'/op.REVIEWED_RUN;prior.mkdir(parents=True)
 with zipfile.ZipFile(P/'ID_R2_b6a46cee2e544e7ebcd7c135df5f1797_RESULT.zip') as z:(prior/'RESULT.json').write_bytes(z.read('RESULT.json'))
 def path(p):
  return {'/proc/sys/kernel/random/boot_id':temp/'boot','/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG':temp/'id','/home/xilinx/jupyter_notebooks/LINE11_OV5640_SINGLE_R2':temp/'single'}.get(str(p),Path(p))
 return temp,path
temp,path=setup();calls=[]
with patch.object(op,'Path',path),patch.object(op.platform,'machine',return_value='armv7l'),patch.object(bc,'run',side_effect=lambda *a,**k:calls.append(1)),contextlib.redirect_stdout(io.StringIO()):
 op.run(B,ask=lambda p:'取消')
assert not calls and not (temp/'single/SINGLE_FRAME_ATTEMPT.json').exists();checks.append('decline before hardware reservation or entry')
def fake_run(base,c,**kw):
 assert kw['authorize_load_and_one_step'] is True and c['operator_confirmation']=='同意单帧测试'
 assert (base/'SINGLE_FRAME_ATTEMPT.json').exists()
 calls.append(1);return base/'CPU_STUB_RUN'
with patch.object(op,'Path',path),patch.object(op.platform,'machine',return_value='armv7l'),patch.object(bc,'run',side_effect=fake_run),contextlib.redirect_stdout(io.StringIO()):
 op.run(B,ask=lambda p:'同意单帧测试')
 try:op.run(B,ask=lambda p:'同意单帧测试')
 except RuntimeError as e:assert 'already attempted' in str(e)
 else:raise AssertionError('repeat allowed')
assert len(calls)==1;checks.append('exact confirmation reaches stub once and preserves cross-kernel marker')
(P/'ENTRY_CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ENTRY_STUB_ONLY',checks=checks,board_operations=0),indent=2));print(checks)
