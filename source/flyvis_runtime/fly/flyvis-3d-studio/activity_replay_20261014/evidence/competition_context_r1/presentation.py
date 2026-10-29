"""Scientific labels and signed color scale shared by native and embedded views."""
from pathlib import Path
import hashlib, json
import numpy as np

NEGATIVE = '#63b8ff'
ZERO = '#354451'
POSITIVE = '#ffcd73'
BOUNDARY = '真实重建骨架；颜色为同类型模型节点均值。非单个生物神经元测量，非 FPGA 实板结果。'

def sha(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def activity_colors(values, limit):
    """Common symmetric signed scale; magnitude sets luminance, sign sets hue."""
    values = np.asarray(values, dtype=float)
    strength = np.clip(np.abs(values) / limit, 0, 1)
    neutral = np.array([.208, .267, .318])
    ends = np.where((values >= 0)[..., None], [1., .804, .451], [.388, .722, 1.])
    return neutral + strength[..., None] * (ends - neutral)

def scale_info(activity):
    # One fixed domain for every type and frame; no independent normalization.
    limit = float(np.max(np.abs(activity))) or 1.
    return dict(min=-limit, zero=0., max=limit, units='original_model_units',
                negative=NEGATIVE, zero_color=ZERO, positive=POSITIVE,
                mode='shared_symmetric_signed',
                explanation='八类共用固定标尺；蓝色负值、暗色零、橙色正值。越亮表示离零越远；正负不直接代表兴奋或抑制。',
                comparison='可比较本次同一模型、同一单位的类型均值；不能据此比较生物神经元强弱或方向选择性。')

def describe(objects, activity, times, frame, selected):
    o = objects[selected]
    value = float(activity[frame, selected])
    delta = float(value - activity[max(frame - 1, 0), selected])
    trend = '这是第一步' if frame == 0 else ('正在上升' if delta > 1e-9 else '正在下降' if delta < -1e-9 else '与上一保存步基本相同')
    group = ''.join(c for c in o['type'] if c.isdigit() or c.isupper())
    sign = '正值' if value > 0 else '负值' if value < 0 else '零'
    return dict(type=o['type'], body_id=o['body_id'], value=value, previous_step_delta=delta,
                model_node_count=o['count'], units='original_model_units',
                explanation=f"{o['type']} 属于 {group} 组，是同一个 FlyVis 视觉网络中的一种细胞类型。当前均值 {value:+.4f}（{sign}），{trend}。",
                mapping=f"这条真实骨架只代表 {o['type']} 的形态；颜色来自 {o['count']} 个同类型模型节点的均值。",
                change=f"相对上一保存步 {delta:+.5f}；一步 5 毫秒。" if frame else '活动曲线来自已保存的软件实验。',
                curve=dict(time_s=times.tolist(), values=activity[:, selected].tolist()), boundary=BOUNDARY)

def verified_identity(model_path):
    """Verify retained sources, raw times and full-ID aggregation before binding."""
    model_path = Path(model_path)
    model = json.loads(model_path.read_text(encoding='utf-8'))
    sources = {Path(s['path']).name: s for s in model['sources']}
    for s in model['sources']:
        if sha(s['path']) != s['sha256']:
            raise ValueError('Source SHA256 mismatch: ' + Path(s['path']).name)
    replay_path = model_path.parent / model['activity_file']
    if sha(replay_path) != model['replay_sha256']:
        raise ValueError('Adapted activity SHA256 mismatch')
    with np.load(replay_path) as data:
        activity, times = data['activity'], data['time']
    original_time = np.load(sources['activity_time.npy']['path'])
    if not np.array_equal(times, original_time):
        raise ValueError('Activity time mismatch')
    raw = np.load(sources['activities_full.npy']['path'], mmap_mode='r')[0]
    for i, o in enumerate(model['objects']):
        if sha(o['swc']) != o['swc_sha256']:
            raise ValueError('Skeleton SHA256 mismatch: ' + o['type'])
        ids = o['model_node_ids']
        mean = raw[:, ids].mean(axis=1, dtype=np.float64)
        if not np.array_equal(mean, activity[:, i]):
            raise ValueError('Type aggregation mismatch: ' + o['type'])
    for roi in model['rois']:
        if sha(roi['path']) != roi['sha256']:
            raise ValueError('Brain region SHA256 mismatch')
    run = json.loads(Path(sources['run_identity.json']['path']).read_text(encoding='utf-8'))
    input_time_path = Path(sources['run_identity.json']['path']).parent/'time.npy'
    input_times = np.load(input_time_path)
    dt = float(np.median(np.diff(times)))
    if input_times.shape!=times.shape or not np.allclose(times-input_times,dt,rtol=0,atol=1e-12):
        raise ValueError('Input / post-Euler activity time alignment mismatch')
    mapping = [dict(type=o['type'], body_id=o['body_id'], swc_sha256=o['swc_sha256'],
                    model_node_ids=o['model_node_ids'], mapping=o['mapping']) for o in model['objects']]
    mapping_sha = hashlib.sha256(json.dumps(mapping, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(schema='line10.octarine.v1', run_id=run['run_id'],
                activity_sha256=sources['activities_full.npy']['sha256'],
                activity_time_sha256=sources['activity_time.npy']['sha256'],
                replay_sha256=model['replay_sha256'], mapping_sha256=mapping_sha,
                model=model['model'], frame_count=len(times), activity_time_s=times.tolist(),
                input_time_s=input_times.tolist(),input_time_sha256=sha(input_time_path),
                dt_s=dt, condition='ON60', mode='Full',
                time_semantics='activity[k] is post-Euler state after input[k]; input time is activity time minus dt',
                filters=['all', 'T4', 'T5'] + [o['type'] for o in model['objects']],
                type_summary=[dict(type=o['type'], body_id=o['body_id'], count=o['count']) for o in model['objects']],
                scale=scale_info(activity), boundary=BOUNDARY, verification='all source SHA256, raw time equality, full-ID type means exact equality, SWC and ROI SHA256',
                evidence_level='OFFLINE_SOFTWARE_REPLAY', PL_execution=False)
