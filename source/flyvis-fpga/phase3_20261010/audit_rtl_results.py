from pathlib import Path
import argparse
import csv
import json
import numpy as np
from prepare_hls_fixtures import sha256


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', type=Path, required=True)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    run = args.run_dir.resolve()
    trace = run / 'artifacts/rtl_animation_q22_request_trace.csv'
    dump = run / 'artifacts/rtl_animation_q22_output.mem'
    with trace.open(newline='') as f:
        rows = list(csv.DictReader(f))
    valid = [r for r in rows if r['comparison'] == 'EXACT_INTEGER_ORACLE']
    if len(valid) != 801 or [int(r['request_id']) for r in valid] != list(range(801)):
        raise ValueError('RTL did not complete all 801 valid requests')
    if any(int(r['status'], 16) != 0 for r in valid):
        raise ValueError('RTL reported a failed valid request')
    negative = {r['request_id']: int(r['status'], 16) for r in rows if r['comparison'] == 'FAIL_CLOSED'}
    if negative != {'negative_1': 1, 'negative_2': 4, 'negative_3': 8}:
        raise ValueError(f'Incomplete RTL failure evidence: {negative}')
    actual_u = np.asarray([int(s, 16) for s in dump.read_text().splitlines()], dtype=np.uint32)
    actual = actual_u.view(np.int32).reshape(801, 67)
    expected = np.fromfile(here / 'testdata_animation_q22/expected_i32le.bin', dtype='<i4').reshape(801, 67)
    if not np.array_equal(actual, expected):
        raise ValueError('Post-simulation bit-true output mismatch')
    raw = np.load(here.parents[1] / 'flyvis-circuit-selection/phase3_20261010/c_reference/SOURCE_RAW_step_io.npz', allow_pickle=False)
    errors = np.abs(actual[:800].astype(np.float64)/(1 << 22) - raw['new_H_expected'].astype(np.float64))
    cycles = sorted({int(r['compute_cycles']) for r in valid})
    xsim_log = run / 'xsim.log'
    if 'PASS RTL total 801 valid requests' not in xsim_log.read_text(errors='replace'):
        raise ValueError('RTL simulator final PASS marker missing')
    fixture = json.loads((here / 'testdata_animation_q22/fixture_manifest.json').read_text())
    report = {
        'status': 'PASS_ACTUAL_ANIMATION_800_RTL_STATELESS_STEP_REPLAY',
        'evidence_level': 'VIVADO_XSIM_RTL_SIMULATION_ONLY',
        'tool': 'Vivado 2026.1.1 xsim, SW build 6605303',
        'device_for_synthesis': 'xc7z020clg400-2 (not synthesized in this report)',
        'comparison_id': fixture['comparison_id'], 'condition_id': '01_off_right',
        'animation_requests': 800, 'boundary_perturb_requests': 1,
        'H_values_checked': 53600, 'bit_true_mismatches': 0,
        'failure_controls': negative,
        'compute_cycles_unique': cycles,
        'nominal_compute_us_at_100MHz': [c / 100 for c in cycles],
        'timing_scope': 'clock cycles measured in RTL simulation; placed/routed frequency and host/link latency unmeasured',
        'max_abs_vs_B_float32_H_reference': float(errors.max()),
        'mae_vs_B_float32_H_reference': float(errors.mean()),
        'scientific_acceptance': 'PENDING_ARCHITECTURE_REVIEW; this is reference-step replay with explicit old_H, not a live GPU-R/PL closed loop',
        'run_directory': str(run),
        'source_sha256': {p.name: sha256(p) for p in (here / 'rtl').glob('*.sv')},
        'evidence_sha256': {str(p.relative_to(run)): sha256(p) for p in (trace, dump, xsim_log, run/'xvlog.log', run/'xelab.log')},
        'synthesis': False, 'SoC_implementation': False, 'board_execution': False,
    }
    out = run / 'artifacts/RTL_ANIMATION_Q22_REPORT.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    (here / 'artifacts/LATEST_RTL_RUN.json').write_text(json.dumps({'report': str(out)}, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
