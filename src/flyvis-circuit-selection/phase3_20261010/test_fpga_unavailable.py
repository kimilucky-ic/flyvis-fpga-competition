"""No board backend means explicit failure before R or state/output creation."""
import subprocess,sys
from common import *

target=HERE/'artifacts/fpga_unavailable_attempt'
assert not target.exists()
command=[sys.executable,str(HERE/'run_video.py'),'--mode','FPGAReplacement','--run',target.name]
result=subprocess.run(command,capture_output=True,text=True,timeout=30)
assert result.returncode!=0 and 'NOT_READY' in result.stderr and not target.exists()
out=HERE/'artifacts/fpga_unavailable_r1';out.mkdir()
(out/'stderr.log').write_text(result.stderr,encoding='utf-8')
dump(out/'result.json',dict(status='PASS_UNAVAILABLE_MODE_FAIL_CLOSED',mode='FPGAReplacement',
    command=command,exit_code=result.returncode,R_started=False,H_started=False,committed_steps=0,
    output_created=False,software_fallback=False,board_access=False,evidence_level='SOFTWARE_MODE_GATE_NEGATIVE_TEST'))
seal(out);print('FPGA_UNAVAILABLE_FAIL_CLOSED_PASS')
