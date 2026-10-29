"""Seal a bounded UI-only delivery; all scientific input is saved and read-only."""
import ast
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')

edits={'viewer/competition_stage.js','viewer/competition.css'}
protection=[]
for row in read(HERE/'before.json'):
    actual=sha(ROOT/row['path']);same=actual==row['sha256']
    assert same or row['path'] in edits,row['path']
    protection.append(dict(**row,current_sha256=actual,unchanged=same))
payload=read(ROOT/'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json')
source=ast.parse((ROOT/'upstream/flyvis/flyvis/utils/groundtruth_utils.py').read_text(encoding='utf-8'))
official={node.targets[0].id:ast.literal_eval(node.value) for node in source.body
          if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name)
          and node.targets[0].id in ('polarity','preferred_directions')}
for role in payload['type_roles']:
    assert official['preferred_directions'][role['type']]==role['reference_preferred_direction_deg']
    assert official['polarity'][role['type']]==(1 if role['family']=='T4' else -1)
frames=[]
for name,k in [('wide_final_k293.json',293),('default_k0.json',0),('default_k217.json',217)]:
    result=read(HERE/name);d=result['stage'];p=result['primer'];r=payload['frames'][k]
    assert d['run']==p['run']==payload['run_id']
    assert int(d['frame'])==int(p['frame'])==k
    assert float(d['activityTime'])==float(p['activityTime'])==r['activity_time_s']
    assert json.loads(d['means'])==[s['raw_mean'] for s in r['type_states']]
    assert all(abs(a-b['delta_from_fixed_C_baseline'])<1e-12 for a,b in zip(json.loads(d['deltaValues']),r['type_states']))
    x,y=r['raw_center_vector'];bearing=(math.degrees(math.atan2(y,x))+360)%360
    assert abs(float(d['readoutBearing'])-bearing)<1e-10
    assert d['inFrameGlossary']=='VISIBLE'
    assert json.loads(d['neuronViewport'])==dict(x=398,y=288,w=1472,h=584)
    refs=json.loads(d['referenceDirections'])
    assert [row['deg'] for row in refs]==[official['preferred_directions']['T4'+t] for t in 'abcd']
    frames.append(dict(k=k,run=d['run'],activity_time_s=r['activity_time_s'],
                       exact_real_means=True,signed_delta_preserved=True,
                       center_bearing_deg=bearing,original_C_PNG_sha256=d['skeletonSha']))
wide=read(HERE/'wide_final_k293.json');initial_wide=read(HERE/'wide_k293.json');default=read(HERE/'default_k0.json')
assert wide['layout']=='rails' and default['layout']=='below'
assert wide['canvasRect']['width']==initial_wide['canvasRect']['width']==1472
assert default['scrollWidth']==default['documentWidth']
c=wide['canvasRect'];left,right=wide['railRects']
assert left['right']<=c['left'] and right['left']>=c['right']
assert read(HERE/'existing_18_final.json')['count']==18
assert read(HERE/'existing_8_final.json')['count']==8
assert read(HERE/'primer_tests_final.json')['count']==5
assert read(HERE/'browser_console.json')==[]
write('VERIFICATION.json',dict(status='PASS_OFFLINE_PERSISTENT_SCIENCE_PRIMER',
    source_preservation=protection,official_reference_matches_all_8_frozen_types=True,
    actual_saved_frames=frames,layout=dict(unchanged_neuron_viewport=[1472,584],
        unchanged_wide_canvas_width=1472,expanded_host_width=wide['hostRect']['width'],
        outside_rails_do_not_overlap_canvas=True,default_no_horizontal_overflow=True),
    tests=dict(existing_JS=26,new_CPU=5,actual_browser=read(HERE/'BROWSER_RESULT.json')),
    neural_GPU_runs=0,camera_captures=0,board_operations=0,new_video_exports=0,
    limits=['Not a new live or real-time/PL result','No full desktop graphical-window retest',
            'Historical 55/P0/science not recomputed; frozen consumers and data preserved']))
sources=[ROOT/p for p in edits]+[ROOT.parent/'fpga/docs/workstreams/flyvis-display.md']
artifacts=[p for p in HERE.rglob('*') if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
write('DELIVERY_MANIFEST.json',dict(schema='gui-persistent-primer-delivery/v1',
    files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(sources+artifacts))]))
print(json.dumps(dict(status='PASS',protected=sum(r['unchanged'] for r in protection),
                     changed=len(edits),actual_frames=len(frames),CPU_checks=31,devices_started=0)))
