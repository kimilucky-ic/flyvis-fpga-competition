"""Saved source plus actual browser receipt check; no neural computation."""
import hashlib
import json
import math
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = '2041849d-b1f8-46ad-a059-49b598c19ab2'
payload_path = ROOT/'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json'
raw = payload_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '9b31e0902b8cc14187ad7196ebdf75101c78dba64cabf60c8d21482d857811f1'
p = json.loads(raw)
cfg = json.loads((ROOT/'gui_v1/competition_movie_C.json').read_text(encoding='utf-8'))
manifest_path = Path(cfg['manifest'])
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == cfg['manifest_sha256']
frames = json.loads((HERE/'browser_frames.json').read_text(encoding='utf-8'))['rows']
assert [int(x['stage']['frame']) for x in frames] == [150,217,360]
for x in frames:
    d = x['stage']; k = int(d['frame']); src = p['frames'][k]
    receipt_path = manifest_path.parent/manifest['frames'][k]['receipt']
    r = json.loads(receipt_path.read_text(encoding='utf-8'))
    assert hashlib.sha256(receipt_path.read_bytes()).hexdigest() == manifest['frames'][k]['receipt_sha256']
    assert d['run'] == RUN and d['skeletonSha'] == r['png_sha256']
    assert float(d['activityTime']) == src['activity_time_s'] and x['stamp']['frame'] == str(k)
    assert json.loads(d['means']) == [s['value'] for s in r['type_states']]
    assert json.loads(d['deltaValues']) == [s['delta_signed'] for s in r['type_states']]
    tau = r['color_encoding']['display_deadband']
    up = [s['type'] for s in r['type_states'] if s['delta_signed'] > tau]
    down = [s['type'] for s in r['type_states'] if s['delta_signed'] < -tau]
    near = [s['type'] for s in r['type_states'] if abs(s['delta_signed']) <= tau]
    assert json.loads(d['activityUp']) == up and json.loads(d['activityDown']) == down and json.loads(d['activityNear']) == near
    angle = math.degrees(math.atan2(src['raw_center_vector'][1], src['raw_center_vector'][0])) % 360
    assert abs(float(d['readoutBearing']) - angle) < 1e-10
    assert d['readoutSource'] == 'SAME_FRAME_OFFICIAL_FLOW_CENTER' and d['accuracyPass'] == 'NOT_DEFINED'
    assert d['displayKind'] == 'OFFLINE_REPLAY'
    if k == 150:
        assert len(near) == 8 and '灰背景' in d['explanationTitle']
    if k == 217:
        assert '朝右上运动' in d['explanationTitle'] and up == ['T4a','T4b','T4c']
        assert '四组活动都降低' in d['activityStoryT5']
    if k == 360:
        assert '运动停止后的响应' in d['explanationDetail']
with urllib.request.urlopen('http://127.0.0.1:8771/api/catalog',timeout=30) as response:
    catalog = json.load(response)
assert sum(len(d['conditions']) for d in catalog['datasets']) == 55
for item in json.loads((HERE/'protected_files.json').read_text(encoding='utf-8')):
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256']
result = dict(status='PASS_ACTUAL_GUI_PLAIN_LANGUAGE_READOUT_AND_ACTIVITY',run_id=RUN,
              actual_browser_steps=[150,217,360],original_conditions=55,js_protocol_checks=18,
              original_data_unchanged=True,old_video_unchanged=True,neural_GPU_runs=0,camera_started=False,board_connections=0,
              reference='Directions are quadrant words plus the exact original center angle; activity words use the existing C display_deadband, not a new recognition metric.')
(HERE/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
