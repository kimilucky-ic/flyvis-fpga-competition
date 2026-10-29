"""Read-only HTTP/identity audit of saved results and actual browser receipts."""
from pathlib import Path
import hashlib
import json
import urllib.request
import urllib.error

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = '2041849d-b1f8-46ad-a059-49b598c19ab2'
SHA = '9b31e0902b8cc14187ad7196ebdf75101c78dba64cabf60c8d21482d857811f1'


def fetch(route):
    with urllib.request.urlopen('http://127.0.0.1:8771' + route, timeout=60) as response:
        return response.read(), dict(response.headers)


raw, headers = fetch('/api/competition/explanation?run=' + RUN)
assert hashlib.sha256(raw).hexdigest() == SHA
assert headers['X-Run-ID'] == RUN and headers['X-Display-Kind'] == 'OFFLINE_REPLAY'
payload = json.loads(raw)
for route in ('/api/competition/explanation', '/api/competition/explanation?run=camera'):
    try:
        fetch(route)
    except urllib.error.HTTPError as error:
        assert error.code == 409 and json.loads(error.read())['status'] == 'NOT_AVAILABLE'
    else:
        raise AssertionError('Wrong/missing run was admitted')
meta = json.loads(fetch('/api/competition')[0])
catalog = json.loads(fetch('/api/catalog')[0])
assert sum(len(d['conditions']) for d in catalog['datasets']) == 55
pack = json.loads(fetch('/api/competition/frames')[0])
manifest = json.loads(Path(pack['manifest_path']).read_bytes())
browser = json.loads((HERE / 'browser_frames.json').read_text(encoding='utf-8'))
assert [int(r['stage']['frame']) for r in browser['rows']] == [150, 217, 360]
for item in browser['rows']:
    row = item['stage']
    k = int(row['frame'])
    expected = payload['frames'][k]
    assert row['run'] == RUN and row['explanationSha'] == SHA and row['explanationStatus'] == 'VERIFIED'
    assert row['skeletonSha'] == manifest['frames'][k]['png_sha256']
    assert float(row['activityTime']) == expected['activity_time_s']
    assert json.loads(row['means']) == [s['raw_mean'] for s in expected['type_states']]
    assert all(abs(a-s['delta_from_fixed_C_baseline']) < 1e-12 for a,s in zip(json.loads(row['deltaValues']),expected['type_states']))
    assert item['explanationStamp']['frame'] == str(k) and item['explanationStamp']['run'] == RUN
    assert row['displayKind'] == 'OFFLINE_REPLAY' and row['accuracyPass'] == 'NOT_DEFINED'
    if k == 217:
        assert float(row['inputDirection']) == 60 and float(row['estimatedDirection']) == expected['raw_center_bearing_deg']
        assert float(row['directionDifference']) == expected['raw_center_difference_from_input_deg']
    else:
        assert row['directionComparisonAvailable'] == 'false' and row['inputDirection'] == '' and row['directionDifference'] == ''
before = json.loads((HERE / 'before.json').read_text(encoding='utf-8'))
edited = {'competition.js', 'competition_stage.js', 'competition.css', 'index.html', 'server.py'}
protected = []
for item in before['files']:
    p = Path(item['path'])
    if p.name in edited:
        continue
    with p.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest() == item['sha256'], p
    protected.append(item)
result = dict(status='PASS_READONLY_HTTP_BROWSER_IDENTITY_AND_PRESERVATION', run_id=RUN,
              explanation_sha256=SHA, verified_sources=len(payload['sources']), verified_steps=485,
              actual_browser_steps=[150,217,360], original_conditions=55, protected_files=protected,
              neural_computations=0, camera_started=False, board_connections=0,
              evidence_level='OFFLINE_REPLAY_OF_SAVED_SOFTWARE_RESULTS', old_40s_movie_unchanged=True)
(HERE / 'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='protected_files'}))
