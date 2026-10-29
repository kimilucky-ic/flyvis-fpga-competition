"""Saved telemetry analysis only. No CUDA, model inference, or FPGA calls."""
from pathlib import Path
import csv
import hashlib
import json
from datetime import datetime, timezone
import numpy as np

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))


def write(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def interval(t, y, a, b):
    assert len(t) == len(y) and np.all(np.diff(t) > 0)
    assert t[0] <= a < b <= t[-1], 'NO_BRACKETING_SAMPLES'
    assert np.isfinite(y).all(), 'INVALID_POWER_SAMPLE'
    mask = (t > a) & (t < b)
    xx = np.r_[a, t[mask], b]
    yy = np.r_[np.interp(a, t, y), y[mask], np.interp(b, t, y)]
    return float(np.trapz(yy, xx)), int(mask.sum()), float(yy.min()), float(yy.max())


def self_test():
    assert interval(np.arange(5.), np.ones(5)*10, .5, 3.5)[0] == 30
    assert interval(np.arange(5.), np.arange(5.), .5, 3.5)[0] == 6
    for t, y, a, b in [(np.arange(3.), np.ones(3), -1, 1),
                       (np.array([0, 1, 1]), np.ones(3), 0, 1),
                       (np.arange(3.), np.array([1, np.nan, 1]), 0, 2)]:
        try:
            interval(t, y, a, b)
        except AssertionError:
            continue
        raise AssertionError('NEGATIVE_CASE_DID_NOT_REJECT')
    write('ANALYSIS_TESTS.json', dict(constant_integral=True, ramp_integral=True,
        missing_bracket_rejected=True, duplicate_time_rejected=True, NaN_rejected=True,
        neural_steps=0, GPU=False))


def main():
    self_test()
    raw = [json.loads(line) for line in (HERE / 'POWER_RAW.jsonl').read_text().splitlines()]
    windows, rounds = load('WINDOWS.json'), load('ROUNDS.json')
    result, identity = load('RUN_RESULT.json'), load('IDENTITY.json')
    assert result['status'] == 'COMPLETE_REAL_GPU_BENCHMARK'
    assert load('SAMPLER_EXIT.json')['exitcode'] == 0
    assert len(rounds) == 36 and all(r['steps'] == 485 for r in rounds)
    assert sum(r['steps'] for r in rounds) == 17460
    ref_ns = raw[0]['midpoint_ns']
    t = np.array([(s['midpoint_ns']-ref_ns)/1e9 for s in raw])
    instant = np.array([s['fields'][1]['watts'] for s in raw], dtype=float)
    average = np.array([s['fields'][0]['watts'] for s in raw], dtype=float)
    energy = np.array([s['energy_counter_mJ'] for s in raw], dtype=float)/1000
    assert np.isfinite(instant).all() and (instant > 0).all()
    assert all(s['fields'][1]['field_id'] == 186 and s['fields'][1]['return_code'] == 0 for s in raw)
    assert np.all(np.diff(energy) >= 0), 'DEVICE_ENERGY_COUNTER_RESET'
    start = lambda w: (w['start_ns']-ref_ns)/1e9
    end = lambda w: (w['end_ns']-ref_ns)/1e9
    metrics = []
    for w in windows:
        a, b = start(w), end(w)
        # Sampler stops just after the last idle. Its final <100ms idle tail
        # may lack a following sample. Crop idle only, never compute windows.
        nominal_a, nominal_b = a, b
        if w['kind'] != 'compute':
            a, b = max(a, t[0]), min(b, t[-1])
        joules, count, lo, hi = interval(t, instant, a, b)
        averaged_joules = interval(t, average, a, b)[0]
        counter_joules = float(np.interp(b, t, energy)-np.interp(a, t, energy))
        row = dict(**w, duration_s=b-a, power_W=joules/(b-a), energy_J=joules,
            integration_start_s=a, integration_end_s=b,
            idle_only_cropped_s=(nominal_b-nominal_a)-(b-a),
            instant_min_W=lo, instant_max_W=hi, samples_inside=count,
            average_field_power_W=averaged_joules/(b-a), counter_energy_J=counter_joules)
        if w['steps']:
            row.update(steps_per_s=w['steps']/(b-a), ms_per_step=1000*(b-a)/w['steps'],
                mJ_per_step=1000*joules/w['steps'], counter_mJ_per_step=1000*counter_joules/w['steps'])
        metrics.append(row)
    compute = [r for r in metrics if r['kind'] == 'compute']
    baseline = next(r['power_W'] for r in metrics if r['kind'] == 'idle_model_resident')
    pre = next(r['power_W'] for r in metrics if r['kind'] == 'idle_before_context')
    post = next(r for r in windows if r['kind'] == 'idle_after_compute')
    post_end = min(end(post), t[-1])
    post_tail = interval(t, instant, post_end-5, post_end)[0]/5
    seconds = sum(r['duration_s'] for r in compute)
    joules = sum(r['energy_J'] for r in compute)
    counter_joules = sum(r['counter_energy_J'] for r in compute)
    steps = sum(r['steps'] for r in compute)
    avg_joules = sum(r['average_field_power_W']*r['duration_s'] for r in compute)
    compute_mask = np.zeros(len(t), dtype=bool)
    for w in windows:
        if w['kind'] == 'compute':
            compute_mask |= (t >= start(w)) & (t <= end(w))
    gaps = np.diff(t)
    field_epoch = np.array([s['fields'][1]['sensor_timestamp_us']/1e6 for s in raw])
    epoch_mid = np.array([s['epoch_ns']/1e9 for s in raw])
    summary = dict(status='PASS_REAL_GPU_POWER_MEASUREMENT', measured_steps=steps,
        compute_seconds=seconds, steps_per_s=steps/seconds, ms_per_step=1000*seconds/steps,
        average_GPU_domain_W=joules/seconds, GPU_domain_energy_J=joules,
        GPU_domain_mJ_per_model_step=1000*joules/steps,
        idle_resident_W=baseline, idle_before_context_W=pre, idle_after_last5s_W=post_tail,
        baseline_subtracted_W=joules/seconds-baseline,
        baseline_subtracted_mJ_per_step=1000*(joules-baseline*seconds)/steps,
        counter_energy_J=counter_joules, counter_mJ_per_step=1000*counter_joules/steps,
        counter_relative_difference=counter_joules/joules-1,
        average_field_W=avg_joules/seconds, average_vs_instant_relative=avg_joules/joules-1,
        per_group=compute, all_windows=metrics,
        telemetry=dict(rows=len(raw), compute_sample_count=int(compute_mask.sum()),
            target_poll_s=.1, observed_median_poll_s=float(np.median(gaps)),
            observed_p95_poll_s=float(np.percentile(gaps,95)), max_poll_s=float(gaps.max()),
            max_call_duration_s=max((s['request_end_ns']-s['request_begin_ns'])/1e9 for s in raw),
            instantaneous_field=186, average_field=185, scope_id=0,
            field_vs_request_epoch_abs_p95_s=float(np.percentile(abs(field_epoch-epoch_mid),95)),
            changed_instant_values=int(np.count_nonzero(np.diff(instant))),
            temperature_compute_range_C=[min(s['temperature_C'] for s,m in zip(raw,compute_mask) if m),
                                         max(s['temperature_C'] for s,m in zip(raw,compute_mask) if m)]),
        numerical=load('NUMERICAL_CHECK.json'),
        formulas=dict(energy='sum over exact compute windows integral P_instant(t) dt, trapezoid with endpoint interpolation',
            mean_power='total joules / total aligned compute seconds',
            energy_per_step='total joules / 17460 completed whole-network steps',
            incremental='(total joules - model-resident idle watts * compute seconds)/17460',
            throughput='17460 / aligned compute seconds',
            nominal_FPGA_break_even='GPU joules per step / provided 0.02201418 seconds per FPGA step; scope alignment required'),
        boundary='NVML GPU plus associated circuitry such as device memory; not bare GPU silicon, not laptop/system/wall',
        excluded='x86 CPU, system RAM, SSD, display, fans, AC conversion; no decoder/rendering in timed benchmark',
        limits=['Single laptop/driver/thermal/desktop state, one bounded session, three serial groups.',
                'NVML INSTANT is driver sensor telemetry, not externally calibrated high-bandwidth rail measurement.',
                '100 ms polling does not imply independent 100 ms sensor readings; average field uses 1-second averaging.',
                'Desktop/compositor GPU loads remain present. Shared lock excludes cooperative neural jobs only.',
                'Idle subtraction is an approximate incremental estimate, not direct attribution of process watts.',
                'Original 2.509 s historical API timing includes initialization/adaptation/host packaging and differs in scope.',
                'No FPGA analysis/board measurement; no system-level energy ratio can be concluded.'])
    reference_fpga_time = .02201418
    summary['nominal_break_even_FPGA_W'] = (joules/steps)/reference_fpga_time
    summary['nominal_break_even_incremental_W'] = ((joules-baseline*seconds)/steps)/reference_fpga_time
    summary['counter_implied_average_W'] = counter_joules/seconds
    summary['counter_implied_nominal_break_even_FPGA_W'] = (counter_joules/steps)/reference_fpga_time
    summary['confidence'] = 'MODERATE_DRIVER_TELEMETRY_NOT_EXTERNAL_CALIBRATION'
    summary['counter_disagreement_note'] = 'Counter is 7.52% below instantaneous-power integration. Cause not isolated; report both, not a calibrated uncertainty interval.'
    # These are explicit hypothetical sensitivity scenarios, NOT sensor accuracy bounds.
    summary['hypothetical_power_scale_sensitivity'] = [dict(power_scale=p,
        GPU_domain_W=joules/seconds*p, GPU_domain_mJ_step=1000*joules/steps*p,
        nominal_break_even_FPGA_W=(joules/steps*p)/reference_fpga_time) for p in [.9,1.,1.1]]
    write('SUMMARY.json', summary)
    write('GPU_POWER_HANDOFF.json', dict(schema='line4.measured_gpu_power.v1',
        status=summary['status'], GPU=identity['gpu'], nodes=45669, edges=1513231,
        precision='FP32 states/parameters/recurrence; original float64 saved stimulus through official FP32 input buffer',
        checkpoint_sha256=identity['checkpoint_sha256'], original_run='flyvis-gpu-validation/artifacts/moving_edge_cuda_t1_r1',
        stimulus='ON angle0 speed19 height80 offsets[-10,11], t_pre=t_post=1, dt=.005',
        steps=steps, rounds=36, seconds=seconds, steps_per_s=steps/seconds,
        GPU_domain_W=joules/seconds, GPU_domain_J_per_step=joules/steps,
        counter_implied_W=counter_joules/seconds, counter_J_per_step=counter_joules/steps,
        counter_relative_difference=counter_joules/joules-1,
        confidence=summary['confidence'], counter_disagreement=summary['counter_disagreement_note'],
        initial_state_sha256=identity['initial_state_sha256'], identity='IDENTITY.json', pins='PLAN.json',
        sample_target_s=.1, sample_actual_median_s=float(np.median(gaps)),
        idle_resident_W=baseline, incremental_J_per_step=(joules-baseline*seconds)/steps,
        power_boundary=summary['boundary'], system_energy='NOT_MEASURED',
        nominal_FPGA_step_s=reference_fpga_time,
        nominal_FPGA_break_even_W=summary['nominal_break_even_FPGA_W'],
        counter_implied_nominal_FPGA_break_even_W=summary['counter_implied_nominal_break_even_FPGA_W'],
        FPGA_power='NOT_ANALYZED_BY_LINE4', comparable_to_bare_Zynq_silicon=False,
        limitations=summary['limits'], report='REPORT.md', raw='POWER_RAW.jsonl'))
    flat = [dict(group=r['group'], steps=r['steps'], duration_s=r['duration_s'],
        power_W=r['power_W'], energy_J=r['energy_J'], steps_per_s=r['steps_per_s'],
        mJ_per_step=r['mJ_per_step'], counter_mJ_per_step=r['counter_mJ_per_step']) for r in compute]
    with (HERE/'GROUP_METRICS.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12,4.4))
    ax.plot(t, instant, linewidth=.8, label='NVML INSTANT field186')
    ax.plot(t, average, linewidth=.8, alpha=.7, label='NVML 1s AVERAGE field185')
    ax.axhline(baseline, color='gray', linestyle='--', label='Model-resident idle mean')
    for w in windows:
        if w['kind']=='compute':
            ax.axvspan(start(w),end(w),color='green',alpha=.12)
            ax.text((start(w)+end(w))/2,ax.get_ylim()[1]*.93,f"Group {w['group']+1}\n5820 steps",ha='center')
    ax.set(xlabel='Monotonic seconds from first telemetry sample',ylabel='Reported GPU-domain power (W)',
        title='Original complete FlyVis: 3 x (12 x 485 steps); green = exact compute windows')
    ax.legend(loc='lower right',fontsize=8);fig.tight_layout();fig.savefig(HERE/'power_timeline.png',dpi=160);plt.close(fig)
    print(json.dumps({k:summary[k] for k in ['status','average_GPU_domain_W','GPU_domain_mJ_per_model_step',
        'steps_per_s','idle_resident_W','baseline_subtracted_mJ_per_step','counter_relative_difference',
        'nominal_break_even_FPGA_W']},indent=2))


if __name__ == '__main__':
    main()
