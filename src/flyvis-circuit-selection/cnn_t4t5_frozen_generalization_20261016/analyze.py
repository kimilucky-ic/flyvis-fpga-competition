"""Read saved valid states only; no model/decoder execution or fitting."""
from core import *


def main():
    check(); execution = load(HERE/'EXECUTION.json'); m = ref.mapping(); roi = np.load(ROI_PATH)
    center = np.maximum.reduce([abs(m['grid_uv'][0]), abs(m['grid_uv'][1]), abs(m['grid_uv'].sum(0))]) <= 1
    records = []; central = {}; all_step_columns = ['H_RMSE', 'R_RMSE', 'H_max', 'R_max', 'H_state_nRMSE', 'R_state_nRMSE', 'flow_component_RMSE']
    for case in load(HERE/'INPUTS.json'):
        path = HERE/'runs'/case['id']
        fr, cr = [load(path/mode/'RESULT.json') for mode in ['Full', 'CNN']]
        n = min(fr['valid_steps'], cr['valid_steps']); complete = n == case['steps']
        f, c = [np.load(path/mode/'states_raw.npy', mmap_mode='r')[:n] for mode in ['Full', 'CNN']]
        ff, cf = [np.load(path/mode/'flow.npy', mmap_mode='r')[:n] for mode in ['Full', 'CNN']]
        step = np.empty((n, len(all_step_columns)), np.float64)
        for k in range(n):
            hf = f[k, m['H']].astype(np.float64); rf = f[k, m['R']].astype(np.float64)
            dh = c[k, m['H']].astype(np.float64)-hf; dr = c[k, m['R']].astype(np.float64)-rf
            df = cf[k, :, roi].astype(np.float64)-ff[k, :, roi]
            step[k] = [np.sqrt(np.mean(dh*dh)), np.sqrt(np.mean(dr*dr)), abs(dh).max(), abs(dr).max(),
                       np.linalg.norm(dh)/max(np.linalg.norm(hf), 1e-12),
                       np.linalg.norm(dr)/max(np.linalg.norm(rf), 1e-12), np.sqrt(np.mean(df*df))]
        np.save(path/'STEP_ERRORS.npy', step)
        dump(path/'STEP_COLUMNS.json', all_step_columns)
        central[case['id']+'_Full'] = f[:, m['H_grid_ids'][:, center]]
        central[case['id']+'_CNN'] = c[:, m['H_grid_ids'][:, center]]
        row = dict(case=case['id'], group=case['group'], complete=complete, compared_steps=n,
                   final_full_state_max_error=float(np.abs(c[-1].astype(np.float64)-f[-1]).max()) if n else None,
                   maximum_step_H_RMSE=float(step[:, 0].max()) if n else None,
                   maximum_step_R_RMSE=float(step[:, 1].max()) if n else None)
        if not complete:
            row.update(status='FAIL_INCOMPLETE', pass_gate=False, windows={})
        elif case['group'] == 'gray':
            windows = {}
            for name, (start, stop) in case['windows'].items():
                z = step[start:stop]
                h = float(np.sqrt(np.mean(z[:, 0]**2))); r = float(np.sqrt(np.mean(z[:, 1]**2)))
                flow = float(np.sqrt(np.mean(z[:, 6]**2)))
                windows[name] = dict(H_absolute_RMSE=h, R_absolute_RMSE=r, flow_component_absolute_RMSE=flow,
                    pass_gate=bool(h <= .002 and r <= .002 and flow <= .002), model_units=True)
            passed = all(v['pass_gate'] for v in windows.values())
            row.update(status='PASS_STATIC_NUMERIC_GATE' if passed else 'FAIL_STATIC_NUMERIC_GATE',
                       pass_gate=passed, windows=windows)
        else:
            h_f = f[:, m['H']]; h_c = c[:, m['H']]
            windows = epoch_scores(case, h_f, h_c, ff, cf, roi)
            passed = all(v['pass_gate'] for v in windows.values())
            eligible = all(v['flow']['reference_eligible'] and v['H_reference_response_rms'] >= 1e-6 for v in windows.values())
            row.update(status='PASS_FUNCTIONAL_GATE' if passed else 'FAIL_FUNCTIONAL_GATE' if eligible else 'NOT_ALL_WINDOWS_EVALUABLE',
                       pass_gate=passed, all_references_eligible=eligible, windows=windows)
        records.append(row); print(json.dumps(dict(stage='ANALYZED', case=row['case'], status=row['status'])), flush=True)
    np.savez(HERE/'CENTRAL_ACTIVITY.npz', global_ids=m['H_grid_ids'][:, center], **central)
    first = load(HERE/'INPUTS.json')[0]['id']; sham_path = HERE/'runs'/first
    sham = np.load(sham_path/'Sham/states_raw.npy', mmap_mode='r')
    full = np.load(sham_path/'Full/states_raw.npy', mmap_mode='r')
    sham_equal = np.array_equal(sham, full)
    sham_flow_diff = float(abs(np.load(sham_path/'Sham/flow.npy')-np.load(sham_path/'Full/flow.npy')).max())
    summary = dict(status='PASS_ALL_PREREGISTERED_GATES' if all(r['pass_gate'] for r in records) else 'COMPLETED_WITH_LIMITATIONS_OR_FAILURES',
        passed=sum(r['pass_gate'] for r in records), total=len(records),
        by_group={group:dict(passed=sum(r['pass_gate'] for r in records if r['group'] == group),
                             total=sum(r['group'] == group for r in records)) for group in ['short', 'long', 'gray']},
        records=records, Sham_all_states_bitwise_equal=sham_equal, Sham_flow_max_abs_difference=sham_flow_diff,
        model_sha=sha(MODEL), model_parameters=31168, training_updates=0, GPU=0, board=0,
        actual_neural_wall_s=execution['wall_s'], actual_commits=execution['valid_commits'])
    dump(HERE/'SUMMARY.json', summary)
    rows = []
    for record in records:
        for name, value in record['windows'].items():
            flow = value.get('flow', {})
            rows.append(dict(case=record['case'], group=record['group'], window=name, status=record['status'],
                H_response_L2=value.get('H_response_relative_L2'), E=flow.get('field_error_E'), M=flow.get('magnitude_ratio'),
                Q=flow.get('Q'), field_angle_deg=flow.get('angle_deg'), reference_eligible=flow.get('reference_eligible'),
                H_absolute_RMSE=value.get('H_absolute_RMSE'), R_absolute_RMSE=value.get('R_absolute_RMSE'),
                flow_absolute_RMSE=value.get('flow_component_absolute_RMSE'), pass_gate=value['pass_gate']))
    with (HERE/'METRICS.csv').open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


if __name__ == '__main__': main()
