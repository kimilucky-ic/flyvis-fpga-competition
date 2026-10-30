"""Read existing environments and write their dependency locks; no installation."""
import json,platform,subprocess,sys
from pathlib import Path
work=Path(__file__).resolve().parents[1];out=work/'environment';out.mkdir(exist_ok=True)
record=dict(os=platform.platform(),kernel=platform.release(),environment_reinstalled=False)
for name,python in [('cpu','/opt/flyvis-venv/bin/python'),('gpu','/opt/flyvis-gpu-venv/bin/python')]:
    freeze=subprocess.check_output([python,'-m','pip','freeze'],text=True)
    (out/f'requirements-{name}-lock.txt').write_text(freeze)
    record[name]=dict(python=python,version=subprocess.check_output([python,'--version'],text=True).strip())
record['gpu_driver']=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'],text=True).strip()
(out/'environment.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record))
