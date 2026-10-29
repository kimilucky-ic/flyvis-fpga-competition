"""Summarize EVERY frozen gate without executing models or selecting cases."""
from pathlib import Path
import json,statistics

HERE=Path(__file__).resolve().parent
load=lambda name:json.loads((HERE/name).read_text(encoding='utf-8-sig'))
summary=load('SUMMARY.json'); execution=load('EXECUTION.json'); failures=[]
for case in summary['records']:
    for name,value in case['windows'].items():
        reasons=[]
        if 'flow' in value:
            if value['H_response_relative_L2'] is None or value['H_reference_response_rms']<1e-6:
                reasons.append('H_REFERENCE_NOT_EVALUABLE')
            elif value['H_response_relative_L2']>.2: reasons.append('H_RESPONSE_L2_GT_0.20')
            for scope in ['flow','foreground_flow']:
                if scope not in value: continue
                f=value[scope]
                if not f['reference_eligible']: reasons.append(scope+':REFERENCE_NOT_EVALUABLE'); continue
                if f['field_error_E']>.2: reasons.append(scope+':E_GT_0.20')
                if not .8<=f['magnitude_ratio']<=1.2: reasons.append(scope+':M_OUTSIDE_0.8_1.2')
                if f['angle_deg'] is None or f['angle_deg']>15: reasons.append(scope+':FIELD_ANGLE_GT_15_OR_UNDEFINED')
        else:
            for key in ['H_absolute_RMSE','R_absolute_RMSE','flow_component_absolute_RMSE']:
                if value[key]>.002: reasons.append(key+':GT_0.002')
        if reasons: failures.append(dict(case=case['case'],window=name,reasons=reasons))
motion=[r for r in summary['records'] if r['group']=='motion']
ranges={}
for name in ['active','stopped','allpost']:
    z=[r['windows'][name] for r in motion if name in r['windows']]
    ranges[name]={}
    for key in ['field_error_E','magnitude_ratio','angle_deg']:
        finite=[r['flow'][key] for r in z if r['flow'][key] is not None]
        ranges[name][key]=[min(finite),max(finite)] if finite else None
    finite=[r['H_response_relative_L2'] for r in z if r['H_response_relative_L2'] is not None]
    ranges[name]['H_response_L2']=[min(finite),max(finite)] if finite else None
local=[dict(case=r['case'],**r['windows']['active']['foreground_flow']) for r in motion if 'foreground_flow' in r['windows'].get('active',{})]
medians={mode:statistics.median(r['wall_s'] for r in execution['records'] if r['mode']==mode) for mode in ['Full','CNN']}
result=dict(status=summary['status'],passed=summary['passed'],total=summary['total'],by_group=summary['by_group'],
    all_motion_window_ranges=ranges,local_foreground=local,failure_and_weak_reference_windows=failures,
    median_5s_trajectory_wall_s=medians,neural_experiment_wall_s=execution['wall_s'],
    video_preparation_wall_s=load('VIDEO_PREPARATION.json')['wall_s'],
    CPU_CNN_valid_commits=sum(r['valid_steps'] for r in execution['records'] if r['mode']=='CNN'),
    functional_failures_are_not_neural_crashes=True,new_neural_steps=0)
with (HERE/'REPORT_DATA.json').open('x',encoding='utf-8') as stream: json.dump(result,stream,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False,indent=2))
