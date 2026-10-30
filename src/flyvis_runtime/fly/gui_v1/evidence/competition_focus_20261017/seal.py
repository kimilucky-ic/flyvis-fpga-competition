"""Bounded read-only source/identity preservation audit and delivery seal."""
from pathlib import Path
import hashlib
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()
def write(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

changed={'viewer/competition.js','viewer/competition_stage.js','viewer/competition_explanation.js','viewer/competition.css'}
source_records=[]
for row in load(HERE/'before.json'):
    actual=sha(ROOT/row['path']);same=actual==row['sha256']
    assert same or row['path'] in changed,row['path']
    source_records.append(dict(**row,current_sha256=actual,unchanged=same))
prior=load(ROOT/'gui_v1/evidence/startup_fast_20261017/DELIVERY_MANIFEST.json')
preserved=['gui_v1/data_store.py','gui_v1/desktop_runtime.py','gui_v1/scientific_pilot.py',
           'gui_v1/scientific_sparse.py','gui_v1/phase3_adapter.py','gui_v1/competition_frames.py',
           'gui_v1/competition_explanation.py','gui_v1/competition_response.py','gui_v1/server.py',
           'gui_v1/startup_cache.py','start_gui.ps1','viewer/app.js','viewer/scientific_pilot.js',
           'viewer/scientific_sparse.js','viewer/phase3.js','viewer/workbench.js','viewer/unified_flow.js']
prior_map={str(Path(r['path'])):r['sha256'] for r in prior['files']}
previous_delivery=[]
for name in preserved:
    actual=sha(ROOT/name);expected=prior_map[str(ROOT/name)];assert actual==expected,name
    previous_delivery.append(dict(path=name,sha256=actual,unchanged_from_startup_delivery=True))
payload=load(ROOT/'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json')
frames=[]
for k in [150,217,218,360]:
    result=load(HERE/f'guide_k{k}.json');d=result['stage'];g=result['dialog'];r=payload['frames'][k]
    assert d['run']==g['run']==payload['run_id']
    assert int(d['frame'])==int(g['frame'])==k
    assert float(d['activityTime'])==float(g['activityTime'])==r['activity_time_s']
    assert float(d['inputTime'])==float(g['inputTime'])==r['input_time_s']
    assert json.loads(d['means'])==[s['raw_mean'] for s in r['type_states']]
    assert all(abs(a-b['delta_from_fixed_C_baseline'])<1e-12 for a,b in zip(json.loads(d['deltaValues']),r['type_states']))
    x,y=r['raw_center_vector'];bearing=(math.degrees(math.atan2(y,x))+360)%360
    assert abs(float(d['readoutBearing'])-bearing)<1e-10
    frames.append(dict(k=k,run=d['run'],input_time_s=r['input_time_s'],activity_time_s=r['activity_time_s'],
                       same_real_means_and_signed_delta=True,center_bearing_deg=bearing,
                       original_C_PNG_sha256=d['skeletonSha']))
assert load(HERE/'existing_18_final.json')['count']==18
assert load(HERE/'guide_tests_final.json')['count']==8
assert load(HERE/'browser_result.json')['status'].startswith('PASS')
assert load(HERE/'browser_console.json')==[]
write('VERIFICATION.json',dict(status='PASS_INCREMENTAL_OFFLINE_SCIENCE_GUIDE_AND_LAYOUT',
    source_preservation=source_records,previous_delivery_preservation=previous_delivery,
    real_browser_frames=frames,tests=dict(existing_JS=18,new_saved_result_JS=8,
    actual_browser=load(HERE/'browser_result.json')),
    layout=dict(old_viewport=[1322,526],new_viewport=[1472,584],
                viewport_area_increase_percent=(1472*584/(1322*526)-1)*100,
                old_numeric_height=110,new_numeric_height=54,original_image_aspect_preserved=True),
    neural_GPU_runs=0,camera_captures=0,board_operations=0,new_video_exports=0,
    limitations=['No full desktop graphical-window test','No new actual live GPU/camera/board validation',
                 '55/P0/science were not recalculated; original consumers/data remain preserved']))
sources=[ROOT/p for p in changed]+[ROOT.parent/'fpga/docs/workstreams/flyvis-display.md']
artifacts=[p for p in HERE.rglob('*') if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
write('DELIVERY_MANIFEST.json',dict(schema='gui-explanation-layout-delivery/v1',
    scope='Changed original viewer files, lane checkpoint, CPU and actual offline-browser evidence',
    files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(sources+artifacts))]))
print(json.dumps(dict(status='PASS',before_protected=sum(r['unchanged'] for r in source_records),
                     preserved_prior_delivery=len(previous_delivery),actual_frames=len(frames),
                     browser_errors=0,neural_runs=0)))
