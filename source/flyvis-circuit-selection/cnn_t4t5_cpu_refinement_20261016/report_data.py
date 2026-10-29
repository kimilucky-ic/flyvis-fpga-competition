"""Compact result aggregation, no training or neural execution."""
from shared import *
result=load(HERE/'RESULTS.json');rows=result['records'];short=load(HERE/'short_checks/ridge/RESULT.json')
old=load(HERE/'training/BASELINE_VALIDATION.json');fit=load(HERE/'training/RIDGE.json')
mode='ON30_base';root=HERE/'test_runs'/mode
full=[json.loads(s)['new'] for s in (root/'Full/chain.jsonl').read_text().splitlines()]
sham=[json.loads(s)['new'] for s in (root/'Sham/chain.jsonl').read_text().splitlines()]
assert full==sham
flow_diff=float(abs(np.load(root/'Full/flow.npy')-np.load(root/'Sham/flow.npy')).max())
assert flow_diff==0
def span(vals):return [min(vals),max(vals)]
summary=dict(status=result['status'],passed=result['passed'],total=result['total'],parameters=31168,
    prior_one_step_nRMSE=old['overall_increment_nRMSE'],refined_one_step_nRMSE=fit['validation']['overall_increment_nRMSE'],
    maximum_one_step_subtype_nRMSE=max(fit['validation']['subtype_increment_nRMSE']),
    short_windows=13,short_steps_each=128,max_short_H_nRMSE=max(r['H_nRMSE'] for r in short['records']),
    max_short_R_nRMSE=max(r['R_nRMSE'] for r in short['records']),BPTT_updates=0,
    holdout_H_response_L2=span([r['H_response_relative_L2'] for r in rows]),
    holdout_flow_E=span([r['flow']['allpost']['field_error_E'] for r in rows]),
    holdout_flow_M=span([r['flow']['allpost']['magnitude_ratio'] for r in rows]),
    holdout_field_angle=span([r['flow']['allpost']['angle_deg'] for r in rows]),
    max_final_state_difference=max(r['final_state_max_error'] for r in rows),
    primary_and_allpost_references_eligible=all(v['reference_eligible'] for r in rows for v in r['flow'].values()),
    Sham=dict(all485_full_state_hashes_bitwise_equal=True,flow_max_abs_difference=flow_diff),
    timings=dict(data_s=load(HERE/'training/DATA.json')['wall_s'],fit_s=fit['wall_s'],short_s=short['wall_s'],test_s=load(HERE/'TEST_EXECUTION.json')['wall_s']),
    model=load(HERE/'MODEL_FREEZE.json'),new_tests_used_for_training=False,GPU=0,board=0)
dump(HERE/'SUMMARY.json',summary);print(json.dumps(summary,indent=2))
