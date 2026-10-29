from pathlib import Path
import argparse
import csv
import json
import numpy as np
from prepare_hls_fixtures import sha256

ap = argparse.ArgumentParser()
ap.add_argument('--run-dir', type=Path, required=True)
args = ap.parse_args()
here = Path(__file__).resolve().parent
run = args.run_dir.resolve()
trace = run/'artifacts/axi_animation_trace.csv'
dump = run/'artifacts/axi_animation_output.mem'
with trace.open(newline='') as f:
    rows = list(csv.DictReader(f))
valid = [r for r in rows if r['comparison']=='EXACT_INTEGER_ORACLE']
assert len(valid)==801 and [int(r['request_id']) for r in valid]==list(range(801))
assert all(int(r['status'],16)==0 for r in valid)
assert len(rows)==802 and rows[-1]['request_id']=='incomplete' and int(rows[-1]['status'],16)==8
actual = np.asarray([int(s,16) for s in dump.read_text().splitlines()],dtype=np.uint32).view(np.int32).reshape(801,67)
expected = np.fromfile(here/'testdata_animation_q22/expected_i32le.bin',dtype='<i4').reshape(801,67)
assert np.array_equal(actual,expected)
assert 'PASS AXI total 801 valid requests' in (run/'xsim.log').read_text(errors='replace')
report = {
    'status':'PASS_AXI_RTL_ANIMATION_800_STATELESS_REPLAY',
    'evidence_level':'VIVADO_2026_1_1_XSIM_AXI_RTL_SIMULATION_ONLY',
    'animation_requests':800,'boundary_perturb_requests':1,'bit_true_mismatches':0,
    'compute_cycles_unique':sorted({int(r['compute_cycles']) for r in valid}),
    'protocol_checks':['AW before W','W before AW','B backpressure','R backpressure',
                       'read-only/unmapped register SLVERR','invalid control SLVERR',
                       'incomplete request status 8','failed candidate read SLVERR'],
    'run_directory':str(run),'board_execution':False,'full_SoC_implementation':False,
    'source_sha256':{p.name:sha256(p) for p in [here/'rtl/flyvis_source_raw_core.sv',here/'rtl/flyvis_source_raw_axil.sv',here/'rtl/tb_flyvis_axil.sv']},
    'evidence_sha256':{str(p.relative_to(run)):sha256(p) for p in [trace,dump,run/'xvlog.log',run/'xelab.log',run/'xsim.log']},
}
out=run/'artifacts/AXI_RTL_REPORT.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
(here/'artifacts/LATEST_AXI_RUN.json').write_text(json.dumps({'report':str(out)},indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
