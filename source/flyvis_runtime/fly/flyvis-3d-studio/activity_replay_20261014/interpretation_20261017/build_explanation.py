"""Saved ON60 results -> explanation metadata for the existing line-2 clock.

CPU arrays only. No inference, decoder execution, graphics, camera or board I/O.
Accuracy PASS is deliberately unavailable: no accuracy criterion was preregistered.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import numpy as np
import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PILOT = ROOT.parents[2] / 'fpga/flyvis-circuit-selection/t4t5_criticality_20261011'
RUN = '2041849d-b1f8-46ad-a059-49b598c19ab2'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def bearing(vector):
    return math.degrees(math.atan2(float(vector[1]), float(vector[0]))) % 360


def deviation(angle, target):
    return abs((angle-target+180) % 360-180)


def main():
    proc = psutil.Process()
    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    proc.cpu_affinity(proc.cpu_affinity()[:2])
    manifest = PILOT/'PILOT_DELIVERY_MANIFEST.json'
    assert sha(manifest) == '6e56aca55064c94a1bcbd28882b69e90f08c800f554ec35b9a11f7c9f309b6d9'
    seal = read(manifest)
    assert seal['run_id'] == RUN
    admitted = {item['path']:item for item in seal['files']}
    sources = [dict(path=str(manifest), sha256=sha(manifest))]
    def source(relative):
        path = PILOT/relative
        assert sha(path) == admitted[relative]['sha256'], relative
        sources.append(dict(path=str(path), sha256=sha(path)))
        return path
    identity = read(source('INPUT_IDENTITY.json'))
    condition = next(c for c in identity['conditions'] if c['condition_id']=='ON60')
    assert condition['polarity']=='ON' and condition['angle_deg']==60
    activity_path=source('artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy')
    assert sha(activity_path)=='6c0c41fb9162de306ab5c9bc1cdf0a16da0f354921ed7ecab4462161b3908234'
    flow = np.load(source('artifacts/pilot_gpu_r1/ON60/Full/flow.npy'), allow_pickle=False)[0].astype(np.float64)
    sham = np.load(source('artifacts/pilot_gpu_r1/ON60/Sham/flow.npy'), allow_pickle=False)[0].astype(np.float64)
    assert flow.shape==(485,2,721) and np.isfinite(flow).all() and np.array_equal(flow, sham)
    roi = np.load(source('cpu_preparation_r1/flow_ROI_hex_indices.npy'), allow_pickle=False)
    uv = np.load(source('cpu_preparation_r1/hex_coordinates.npy'), allow_pickle=False)
    assert roi.shape==(331,) and len(set(roi.tolist()))==331 and uv.shape==(721,2)
    center = int(np.flatnonzero(np.all(uv==0,axis=1))[0])
    input_time = np.load(source('artifacts/pilot_gpu_r1/time.npy'), allow_pickle=False)
    activity_time = np.load(source('artifacts/pilot_gpu_r1/activity_time.npy'), allow_pickle=False)
    assert np.array_equal(activity_time, input_time+.005)
    stimulus = np.load(source('cpu_preparation_r1/ON60_stimulus.npy'), allow_pickle=False)[0,:,0]
    changed = np.flatnonzero(np.any(stimulus[1:]!=stimulus[:-1],axis=1))+1
    assert (int(changed[0]),int(changed[-1]))==(200,284)
    assert np.all(stimulus[:200]==.5) and np.array_equal(stimulus[285:],np.broadcast_to(stimulus[284],(200,721)))
    metrics_path = source('artifacts/pilot_analysis_r1/functional_summary.csv')
    source('metrics.py')
    with metrics_path.open(encoding='utf-8',newline='') as stream:
        metric = next(row for row in csv.DictReader(stream) if row['condition']=='ON60' and row['mode']=='Full' and row['ROI']=='primary331' and row['window']=='primary')
    assert metric['active_step_range']=='[200, 285]' and metric['pre_step_range']=='[160, 199]'
    assert float(metric['angle_deg'])==0  # This compares Full to Sham, never to the 60-degree stimulus.
    sync = ROOT/'response_c_delivery_20261015/synchronization_contract.json'
    assert sha(sync)=='2fc7a360c6375cc21211416ae448fc76bb9c80665fe988640bafc247aa62010b'
    contract = read(sync)
    assert contract['run_id']==RUN and np.array_equal(contract['input_time_s'],input_time)
    assert np.array_equal(contract['activity_time_s'],activity_time)
    sources.append(dict(path=str(sync),sha256=sha(sync)))
    replay = ROOT/'replay.npz'
    assert sha(replay)=='2ee7daa99aca0789a14aaabb1c4eefd1a972a0e751f6d41e9970f8fb7fc713ce'
    sources.append(dict(path=str(replay),sha256=sha(replay)))
    with np.load(replay,allow_pickle=False) as data:
        means=data['activity'].copy()
        assert means.shape==(485,8) and np.array_equal(data['time'],activity_time)
    truth_path=ROOT.parents[1]/'upstream/flyvis/flyvis/utils/groundtruth_utils.py'
    tree=ast.parse(truth_path.read_text(encoding='utf-8'))
    directions=next(ast.literal_eval(item.value) for item in tree.body if isinstance(item,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='preferred_directions' for t in item.targets))
    sources.append(dict(path=str(truth_path),sha256=sha(truth_path)))
    types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
    labels={180:'向左',0:'向右',90:'向上',270:'向下'}
    roles=[]
    for name in types:
        on=name.startswith('T4')
        roles.append(dict(type=name,family=name[:2],contrast='ON' if on else 'OFF',
            function_zh='主要处理变亮边缘的运动' if on else '主要处理变暗边缘的运动',
            reference_preferred_direction_deg=directions[name],reference_display_direction_zh=labels[directions[name]],
            reference_is_this_model_measured_tuning=False,
            reference_note_zh='参考方向来自FlyVis官方标注；本次只有一个刺激方向，不能据此测出该模型完整方向调谐。'))
    baseline_activity=means[100:200].mean(axis=0)
    baseline_flow=sham[160:200].mean(axis=0)
    centered_roi=(flow-baseline_flow)[:,:,roi].mean(axis=2)
    noise=np.sqrt(np.mean(centered_roi[160:200]**2,axis=0).sum())
    minimum_signal=max(1e-4,5*float(noise))
    frames=[]
    for k in range(485):
        moving=200<=k<=284
        phase='PRE_STIMULUS' if k<200 else 'MOVING_EDGE' if moving else 'HELD_FINAL_INPUT'
        raw_center=flow[k,:,center]
        corrected=centered_roi[k]
        available=moving and float(np.linalg.norm(corrected))>=minimum_signal
        angle=bearing(corrected) if available else None
        raw_angle=bearing(raw_center) if moving and float(np.linalg.norm(raw_center))>=minimum_signal else None
        reason=None if available else 'NO_MOVING_STIMULUS' if not moving else 'DERIVED_VECTOR_TOO_SMALL'
        states=[dict(type=t,raw_mean=float(means[k,i]),delta_from_fixed_C_baseline=float(means[k,i]-baseline_activity[i]),
                     response='基线附近' if abs(means[k,i]-baseline_activity[i])<=.005 else '高于基线' if means[k,i]>baseline_activity[i] else '低于基线')
                for i,t in enumerate(types)]
        frames.append(dict(frame_index=k,input_time_s=float(input_time[k]),activity_time_s=float(activity_time[k]),phase=phase,
            known_input=dict(polarity='ON',direction_deg=60 if moving else None,source='FROZEN_STIMULUS_METADATA_NOT_MODEL_CLASSIFICATION'),
            raw_center_vector=raw_center.tolist(),raw_center_bearing_deg=raw_angle,
            raw_center_difference_from_input_deg=deviation(raw_angle,60) if raw_angle is not None else None,
            derived_baseline_subtracted_ROI_mean_vector=corrected.tolist(),derived_bearing_deg=angle,
            derived_difference_from_input_deg=deviation(angle,60) if angle is not None else None,
            direction_comparison_available=bool(available),unavailable_reason=reason,
            success_badge='NOT_DEFINED',type_states=states))
    raw_average=flow[200:286][:,:,roi].mean(axis=(0,2))
    derived_average=centered_roi[200:286].mean(axis=0)
    summary=dict(window_steps_inclusive=[200,285],window_source='Existing preregistered primary window, includes movement-ending boundary step285',
        ROI='primary331',raw_mean_vector=raw_average.tolist(),raw_mean_bearing_deg=bearing(raw_average),
        raw_mean_difference_from_input_deg=deviation(bearing(raw_average),60),
        derived_baseline_subtracted_mean_vector=derived_average.tolist(),derived_bearing_deg=bearing(derived_average),
        derived_difference_from_input_deg=deviation(bearing(derived_average),60),
        assessment='DESCRIPTIVE_POSTHOC_DIRECTION_COMPARISON_NOT_ACCURACY_PASS',
        available_after_frame=285,not_an_accuracy_percentage=True,
        caveat_zh='均值方向相近不代表每个位置、每一帧都正确；没有速度标定或识别率阈值。')
    payload=dict(schema='line10.motion_explanation.v1',version='20261017.1',language='zh-CN',run_id=RUN,condition='ON60',mode='Full',
        activity_sha256=contract['source_activity']['sha256'] if 'source_activity' in contract else '6c0c41fb9162de306ab5c9bc1cdf0a16da0f354921ed7ecab4462161b3908234',
        source_steps=485,model_dt_s=.005,evidence_level='SAVED_SOFTWARE_REPLAY_WITH_DESCRIPTIVE_POSTHOC_SUMMARY',PL_execution=False,
        type_roles=roles,
        UI_copy=dict(title_zh='亮边缘往哪移动？网络估计得怎样？',
            family_T4_zh='T4：亮边缘运动通道（ON）',family_T5_zh='T5：暗边缘运动通道（OFF）',
            network_zh='八类属于同一个视觉网络：两种明暗极性 × 四个参考方向。',
            brightness_zh='亮度看相对基线的变化幅度；＋表示升高，－表示降低。亮起来不等于识别正确。',
            output_zh='官方解码器从网络活动估计运动方向；方向偏差由输入方向与输出向量计算。',
            summary_zh='先看输入，再看T4/T5如何响应，最后比较真实运动方向与模型估计方向。'),
        definitions=dict(component_convention=['x_right_positive','y_up_positive'],angle='atan2(y,x) degrees counterclockwise from right, modulo360',
            C_activity_baseline_steps_half_open=[100,200],flow_baseline_steps_half_open=[160,200],
            flow_baseline_source='Identical-condition saved Sham, exactly equal to Full in this run',
            derived_vector='FP64 mean over fixed331 ROI of (raw Full flow[k] - fixed Sham flow baseline)',
            normalization='No vector renormalization, rescaling, value rewrite or inference. Angle is a derived display quantity.',
            signal_floor=minimum_signal,signal_floor_purpose='Numerical availability only, never success/confidence threshold',
            known_moving_input_steps_inclusive=[200,284],primary_summary_steps_inclusive=[200,285],
            accuracy_PASS_threshold=None,accuracy_percentage=None,GT_speed_available=False,
            intervention_metrics_warning='Existing Q/E/angle compare intervention to Sham/Full; never interpret Full E=0 or angle=0 as recognition accuracy.',
            camera_policy='Without externally verified input GT, direction comparison and success badge are unavailable. Do not apply this saved ON60 baseline/run to camera data.',
            clock_policy='Consume existing line2 committed/matching k; no independent clock. Render words only after the same matching image receipt.',
            phenotype_note='Type mean on representative real SWC, not individual biological recording; preferred directions are reference annotations, not a tuning measurement from this one stimulus.'),
        primary_window_summary=summary,frames=frames,sources=sources,
        scientific_sources=[dict(title='Maisak et al. 2013, ON/OFF and direction selective T4/T5',url='https://www.nature.com/articles/nature12320'),
            dict(title='Lappalainen et al. 2024, FlyVis task and official optic-flow decoder',url='https://www.nature.com/articles/s41586-024-07939-3'),
            dict(title='Official FlyVis reference preferred directions',url='https://github.com/TuragaLab/flyvis/blob/92b3845cc426dd309a1a0e1b3890156c42e14021/flyvis/utils/groundtruth_utils.py')])
    assert [r['frame_index'] for r in frames]==list(range(485))
    assert not frames[150]['direction_comparison_available'] and not frames[360]['direction_comparison_available']
    assert abs(frames[217]['raw_center_bearing_deg']-68.23349215027797)<1e-10
    assert abs(summary['derived_bearing_deg']-62.23759541293041)<1e-10
    output=HERE/'explanation.json'
    write(output,payload)
    write(HERE/'delivery.json',dict(status='READY_FOR_EXPLICIT_LINE2_ADMISSION_NOT_YET_GUI_INTEGRATED',
        schema=payload['schema'],version=payload['version'],run_id=RUN,
        payload_path=str(output),payload_sha256=sha(output),builder_sha256=sha(Path(__file__)),
        source_count=len(sources),source_hashes_verified=True,all485_steps_and_times_verified=True,
        primary_window_summary=summary,accuracy_PASS_threshold=None,
        scope='Explanatory metadata only; no GUI, old video, original arrays or frozen delivery changed.',
        GPU_used=False,neural_compute=False,camera_opened=False,PL_execution=False))
    print(json.dumps(dict(status='READY',sha256=sha(output),summary=summary),ensure_ascii=False))


if __name__=='__main__':main()
