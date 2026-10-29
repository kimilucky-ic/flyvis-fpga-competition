"""Read-only final audit of the completed camera run; never starts inference."""
import csv
import hashlib
import json
from pathlib import Path
import socket
import sys
import numpy as np
import psutil
from PIL import Image

FLY=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(FLY/'gui_v1'))
from competition_live import verify_source_receipt

OUT=Path(__file__).resolve().parent
SID='b8704765c95149ccb0546ab6de61aaea'
root=FLY/'gui_v1/runtime/live'/SID
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def stats(values):return dict(p50_ms=float(np.percentile(values,50)),p95_ms=float(np.percentile(values,95)))
ready=load(root/'skeleton/ready.json');verify_source_receipt(ready)
rows=[json.loads(s) for s in (root/'skeleton/frames.jsonl').read_text(encoding='utf-8').splitlines()]
for row in rows:
    verify_source_receipt(row)
    assert row['fixed_cpu_projection_sha256']==ready['fixed_cpu_projection_sha256']
    assert row['rendering_method']=='fixed_SWCs_CPU_projection_composite' and row['draw_performed'] is False
base=FLY/'flyvis-3d-studio/activity_replay_20261014/live_fixed_cpu_20261015'
folder=base/'evidence'/('gui_'+SID)/'fixed_projection'
cache=load(folder/'fixed_projection.json');cache_sha=cache.pop('sha256')
assert cache==ready['fixed_cpu_projection']
assert hashlib.sha256(json.dumps(cache,sort_keys=True,separators=(',',':')).encode()).hexdigest()==cache_sha==ready['fixed_cpu_projection_sha256']
with Image.open(folder/'fixed_background.png') as im:
    assert hashlib.sha256(np.asarray(im).tobytes()).hexdigest()==cache['background_sha256']
with np.load(folder/'fixed_masks.npz',allow_pickle=False) as z:
    for mask,cell in zip(z['masks'],cache['types']):
        assert hashlib.sha256(mask.tobytes()).hexdigest()==cell['mask_sha256']
v=load(OUT/'live_verification.json');result=load(root/'stream/result.json')
save('live_identity.json',dict(status='PASS_SOURCE_PINS_CACHE_AND_ALL_FRAME_IDENTITIES',session_id=SID,run_id=result['run_id'],frames=len(rows),
    projection_sha256=cache_sha,projection_cache_files={p.name:digest(p) for p in folder.iterdir()},
    rendering_method='fixed_SWCs_CPU_projection_composite',occlusion_policy=cache['occlusion_policy'],
    fixed_cpu_compose_ms=stats([r['fixed_cpu_compose_ms'] for r in rows]),
    total_render_raw_ms=stats([r['total_render_raw_ms'] for r in rows]),
    device=result['device'],asset_writer=result['asset_writer'],model=result['model'],
    capture=v['camera_evidence'],all_means_exact=v['all_means_exact'],FPGA_status='NOT_CONNECTED'))
old=load(FLY/'gui_v1/evidence/source_path_fix_20261015/verification.json')
with (OUT/'before_after.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['session_id','graphics','computed_steps','wall_s','model_time_s','display_FPS','receipt_to_draw_p95_upper_ms','processing_p50_ms','comparison_scope']
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for value,graphics,timing in [(old,'CPU_full_scene_redraw','total_render_raw_ms'),(v,'CPU_fixed_projection_brightness','total_render_raw_ms')]:
        s=value['summary'];writer.writerow(dict(session_id=s['session_id'],graphics=graphics,computed_steps=s['computed_steps'],wall_s=s['compute_wall_s'],model_time_s=s['model_time_s'],display_FPS=s['display_FPS'],receipt_to_draw_p95_upper_ms=s['receipt_to_draw_p95_upper_ms'],processing_p50_ms=value['timings'][timing]['p50_ms'],comparison_scope='Separate actual camera runs, not identical-input controlled benchmark'))
active=load(FLY/'gui_v1/runtime/demo_active.json');assert active['session_id']==SID and active['state']=='STOPPED'
alive=[c for c in active['children'] if psutil.pid_exists(c['pid'])]
renderer_alive=psutil.pid_exists(ready['pid']) and abs(psutil.Process(ready['pid']).create_time()-ready['pid_create_time'])<.00001
renderer_parent_alive=psutil.pid_exists(ready['parent_pid']) and abs(psutil.Process(ready['parent_pid']).create_time()-ready['parent_create_time'])<.00001
launcher_alive=psutil.pid_exists(active['pid'])
with socket.socket() as s:s.settimeout(1);port_closed=s.connect_ex(('127.0.0.1',8771))!=0
ack=load(root/'worker_shutdown.json')
assert not alive and not renderer_alive and not renderer_parent_alive and not launcher_alive and port_closed and ack['CUDA_synchronized'] and ack['shared_lock_closed']
save('owned_shutdown.json',dict(state=active['state'],session_id=SID,exit_codes=active['exit_codes'],owned_children_alive=alive,owned_renderer_alive=renderer_alive,owned_server_parent_alive=renderer_parent_alive,owned_launcher_alive=launcher_alive,port8771_closed=port_closed,CUDA_ack=ack,camera_closed=v['camera_evidence']['capture']['closed']))
paths=['gui_v1/competition_live.py','viewer/competition_live.js','viewer/competition_stage.js','viewer/live_camera.js','viewer/skeleton_wire.js','gui_v1/verify_fixed_cpu.py','gui_v1/test_live_read_retry.js','gui_v1/test_competition_live.py']
paths += ['flyvis-3d-studio/activity_replay_20261014/live_fixed_cpu_20261015/'+name for name in ('service.py','research_guard.py','fixed_cpu.py')]
save('delivery_sources.json',{p:digest(FLY/p) for p in paths})
print(json.dumps(dict(status='PASS',frames=len(rows),compose_ms=stats([r['fixed_cpu_compose_ms'] for r in rows]),shutdown='STOPPED')))
