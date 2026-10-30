"""Saved state/input chains and frozen identity only. Zero neural steps."""
from core import *

start = time.perf_counter(); check(deep=True)
registration = load(HERE/'PREREGISTRATION.json'); frozen = load(HERE/'FREEZE.json')
assert frozen['time_ns'] < (HERE/'INPUTS.json').stat().st_mtime_ns
inputs_by_id = {c['id']:c for c in load(HERE/'INPUTS.json')}
execution = load(HERE/'EXECUTION.json'); m = ref.mapping()
initial_digest = digest(np.load(BUNDLE/'initial_state_full.npy'))
total = cnn_total = failures = 0
for record in execution['records']:
    case = inputs_by_id[record['case']]; out = HERE/'runs'/case['id']/record['mode']
    assert sha(case['path']) == case['sha256']
    inputs_array = np.load(case['path'], mmap_mode='r')
    validity = load(out/'VALIDITY.json'); n = validity['valid_rows']
    assert n == record['valid_steps'] and validity['allocated_rows'] == case['steps']
    states = np.load(out/'states_raw.npy', mmap_mode='r')
    assert states.shape == (case['steps'], 45669) and states.dtype == np.float32
    lines = (out/'chain.jsonl').read_text(encoding='utf-8').splitlines(); assert len(lines) == n
    previous = initial_digest
    for k, line in enumerate(lines):
        row = json.loads(line)
        assert row['step'] == k and row['old'] == previous and row['input'] == digest(inputs_array[k])
        assert row['time'] == k*DT and row['next_time'] == (k+1)*DT and row['new'] == digest(states[k])
        assert row['committed'] and np.isfinite(states[k]).all() and np.abs(states[k]).max() <= 100
        if record['mode'] == 'CNN':
            assert row['old_source'] == 'OWN_LIVE_STATE' and row['native_H_updates'] == 0
            assert row['R_targets'] == 39901 and row['H_CNN_outputs'] == 5768
        previous = row['new']
    assert previous == digest(np.load(out/'final.npy'))
    flow = np.load(out/'flow.npy', mmap_mode='r'); assert flow.shape == (n, 2, 721) and np.isfinite(flow).all()
    if record['mode'] == 'CNN':
        assert record['native_H_guard_active'] and record['native_H_updates'] == 0 and record['teacher_corrections'] == 0
        assert record['CNN_calls'] >= n
        cnn_total += n
    if not record['complete']:
        assert record['failure'] and validity['invalid_range'] == [n, case['steps']]
        failures += 1
    total += n
assert total == execution['valid_commits']
assert execution['native_H_guard_violations'] == 0 and execution['training_updates'] == 0
assert execution['model_unchanged'] and execution['decoder_recursive_eval_and_state_unchanged']
summary = load(HERE/'SUMMARY.json')
assert summary['Sham_all_states_bitwise_equal'] and summary['Sham_flow_max_abs_difference'] == 0
assert sum(r['pass_gate'] for r in summary['records']) == summary['passed']
assert sha(MODEL) == MODEL_SHA
dump(HERE/'FINAL_AUDIT.json', dict(status='PASS_SAVED_VALID_PREFIX_AND_FROZEN_IDENTITY',
    functional_status=summary['status'], all_state_rows_rehashed=total, CNN_commits=cnn_total,
    failed_run_valid_prefixes=failures, raw_invalid_tails_excluded=True, all_inputs_old_new_time_chains=True,
    shared_a0_all_runs=True, model_SHA_unchanged=True, source_pins_unchanged=True, native_H_updates_in_CNN=0,
    teacher_corrections=0, Sham_bitwise_equal=True, inherited_fault_feedback_suite_repeated=False,
    new_neural_steps=0, wall_s=time.perf_counter()-start, GPU=0, board=0))
print(json.dumps(dict(stage='AUDIT_PASS', state_rows=total, CNN_commits=cnn_total, new_neural_steps=0)), flush=True)
