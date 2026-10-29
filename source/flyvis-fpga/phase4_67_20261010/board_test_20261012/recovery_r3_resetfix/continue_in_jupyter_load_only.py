"""Continue the unused exact load authorization in Jupyter; no serial re-execution."""
from pathlib import Path
import ast
import hashlib
import json
import os

BASE = Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1')
SCRIPT = BASE / 'run_resetfix_serial_once.py'
if hashlib.sha256(SCRIPT.read_bytes()).hexdigest() != 'cf85b41e59b4e952b91cf2e519843a83bf5848a015c3e6b988e1c65bba64bcce':
    raise RuntimeError('STOP: uploaded operator script identity differs')
if Path('/proc/sys/kernel/random/boot_id').read_text().strip() != '894292a3-1b60-4abf-aba3-e7b18b9e75c8':
    raise RuntimeError('STOP: board boot changed')
xrt_root = os.environ.get('XILINX_XRT', '')
print('JUPYTER_XILINX_XRT:', xrt_root or 'MISSING', flush=True)
if not xrt_root or not (Path(xrt_root) / 'lib/libxrt_core.so').is_file():
    raise RuntimeError('STOP: Jupyter XRT environment is unavailable; no BIT load')

PREVIOUS_SERIAL_SESSION = BASE / 'unpacked_resetfix_6d686a21b53a4303821311d7395becdd/row0_resetfix_894292a3_attempt3'
fault = json.loads((PREVIOUS_SERIAL_SESSION / '99_LOAD_FAULT.json').read_text())
if fault.get('error') != "RuntimeError('No Devices Found')":
    raise RuntimeError('STOP: previous failure differs from reviewed pre-download failure')
if (PREVIOUS_SERIAL_SESSION / '03_BEFORE_OVERLAY_DOWNLOAD.json').exists():
    raise RuntimeError('STOP: prior programming intent exists; do not retry')
sources = {}
for node in ast.parse(SCRIPT.read_text()).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in ('LOAD_SOURCE', 'ROW0_SOURCE'):
                sources[target.id] = ast.literal_eval(node.value)
LOAD_SOURCE = sources['LOAD_SOURCE'].replace(
    '"row0_resetfix_894292a3_attempt3"', '"row0_resetfix_894292a3_attempt3_jupyter"')
start = LOAD_SOURCE.index('ps_report = ')
end = LOAD_SOURCE.index('review = json.loads(', start)
reuse = '''ps_report = json.loads((PREVIOUS_SERIAL_SESSION / "ps_precheck.json").read_text())
if (ps_report.get("boot_id") != BOOT or ps_report.get("status") != "READ_ONLY_CURRENT_BOOT_HP0_64BIT_OBSERVED"
        or ps_report.get("register_reads") != 4 or ps_report.get("register_writes") != 0
        or ps_report.get("hp0_read_width_bits") != 64 or ps_report.get("hp0_write_width_bits") != 64):
    raise RuntimeError("STOP: saved current-boot PS observation differs")
durable_json(R3 / "ps_precheck_carried_forward.json", ps_report)
print("00_REUSE_SAME_BOOT_PS_CHECK; NO_NEW_PS_READS", flush=True)

'''
LOAD_SOURCE = LOAD_SOURCE[:start] + reuse + LOAD_SOURCE[end:]
SERIAL_ROW0_SOURCE = sources['ROW0_SOURCE']
exec(compile(LOAD_SOURCE, 'R3_jupyter_load_only', 'exec'), globals())
