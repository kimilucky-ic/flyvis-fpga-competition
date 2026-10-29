"""Saved-data analysis; fixes output field collision in frozen harness only.

Ground truth and predicted angle have distinct JSON keys. Frozen feature,
prediction, evaluation formulas, cases, readouts, thresholds and runs unchanged.
No neural recurrence, refit, GPU or further stimuli are performed here.
"""
import csv
import json
import numpy as np
from experiment import HERE,check_frozen,load,dump
from direction_readout import predict,evaluate


def metric(rs):
    errors=[r['angle_error_deg'] for r in rs if r['accepted']]
    return dict(n=len(rs),direction_hit_30=float(np.mean([r['direction_hit_30'] for r in rs])),
        four_way_accuracy=float(np.mean([r['four_way_correct'] for r in rs])),coverage=float(np.mean([r['accepted'] for r in rs])),
        accepted_MAE_deg=None if not errors else float(np.mean(errors)),
        accepted_median_deg=None if not errors else float(np.median(errors)),
        accepted_p95_deg=None if not errors else float(np.percentile(errors,95)),
        penalized_MAE_deg=float(np.mean([r['penalized_error_deg'] for r in rs])))


def main():
    check_frozen();load(HERE/'HELDOUT_EXECUTION.json')
    rows=[];branches=['Full/shared','a_r4/shared','a_r4/own']
    for spec in load(HERE/'CASES.json'):
        for branch in branches:
            name,profile=branch.split('/')
            readout=load(HERE/f"readout_{name if profile=='own' else 'Full'}.json")
            f=np.load(HERE/'runs'/name/spec['id']/'features.npy')
            p=predict(f,readout);e=evaluate(p,spec)
            row=dict(branch=branch,clip=spec['id'],split=spec['split'],kind=spec['kind'],
                polarity=spec.get('polarity'),truth_angle_deg=spec.get('angle_deg'),speed_hex_s=spec.get('speed_hex_s'))
            row.update(p);row.update(e);rows.append(row)
    dump(HERE/'PREDICTIONS.json',rows)
    fields=['branch','clip','split','kind','polarity','truth_angle_deg','speed_hex_s','status','angle_deg','raw_angle_deg','motion_feature_rms','vector_norm','is_motion','accepted','angle_error_deg','penalized_error_deg','direction_hit_30','four_way_correct','false_motion']
    with (HERE/'PREDICTIONS.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    summaries=[]
    for branch in branches:
        test=[r for r in rows if r['branch']==branch and r['split']=='heldout']
        motion=[r for r in test if r['kind']=='motion'];static=[r for r in test if r['kind'] in ['static','gray']];flash=[r for r in test if r['kind']=='flash']
        overall=metric(motion)
        speed={str(s):metric([r for r in motion if r['speed_hex_s']==s]) for s in [12,6,24]}
        polarity={p:metric([r for r in motion if r['polarity']==p]) for p in ['ON','OFF']}
        static_fp=sum(r['false_motion'] for r in static);flash_fp=sum(r['false_motion'] for r in flash)
        gate=bool(overall['direction_hit_30']>=.8 and all(m['direction_hit_30']>=.75 for m in speed.values())
            and all(m['direction_hit_30']>=.75 for m in polarity.values()) and overall['coverage']>=.9
            and overall['accepted_MAE_deg'] is not None and overall['accepted_MAE_deg']<=20 and static_fp==0)
        design=[r for r in rows if r['branch']==branch and r['split']=='design' and r['kind']=='motion']
        summaries.append(dict(branch=branch,overall=overall,by_speed=speed,by_polarity=polarity,
            static_false_motion=f'{static_fp}/{len(static)}',flash_false_motion=f'{flash_fp}/{len(flash)}',engineering_gate_pass=gate,
            design_fit_only=metric(design)))
    result=dict(status='COMPLETED_FIXED_BATCH',primary_comparison='Full/shared vs a_r4/shared',
        summaries=summaries,heldout_inputs_not_used_for_fit=True,GPU_runs=0,official_decoder=False,
        interpretation='local two-second single-edge readout; no natural-video, speed estimation, dense optical-flow or hardware proof')
    dump(HERE/'SUMMARY.json',result)
    dump(HERE/'ANALYSIS_FIELD_CORRECTION.json',dict(reason='pre-execution code inspection: original analyze dict specified angle_deg both for truth and prediction; use separate truth_angle_deg',
        original_frozen_harness_unchanged=True,original_analyze_not_executed=True,new_entry='analyze_results.py',
        neural_runs_repeated=0,features_or_prediction_or_evaluation_formulas_changed=False,readout_refit=False,threshold_changes=False))
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
