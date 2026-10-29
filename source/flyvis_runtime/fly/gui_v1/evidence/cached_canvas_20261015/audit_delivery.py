"""Final read-only performance/identity/cleanup audit; no services or inference."""
import csv,hashlib,json,pathlib,socket,sys
import numpy as np
import psutil
OUT=pathlib.Path(__file__).resolve().parent;FLY=OUT.parents[2];sys.path.insert(0,str(FLY/'gui_v1'))
from live_protocol import load,write,sha
from competition_live import verify_source_receipt
from cached_skeleton import CachedSkeleton
sid='2b77968f1e234ebb81f4454cd07cba37';root=FLY/'gui_v1/runtime/live'/sid
v=load(OUT/'verification.json');result=load(root/'stream/result.json');h=load(root/'skeleton/ready.json');verify_source_receipt(h)
cached=CachedSkeleton((root/'skeleton/projection.cache').read_bytes(),h)
rows=[json.loads(x) for x in (root/'skeleton/frames.jsonl').read_text(encoding='utf-8').splitlines()]
draws=[json.loads(x) for x in (root/'stream/display_receipts.jsonl').read_text(encoding='utf-8').splitlines()]
for r,d in zip(rows,draws):
    verify_source_receipt(r)
    assert r['projection_cache_sha256']==cached.sha256==d['skeleton_cache_sha256']
    assert d['skeleton_wire']=='FIXED_CPU_CACHE_V1' and d['skeleton_bytes']==0
    assert r['request_id']==d['skeleton_request_id'] and r['raw_sha256']==d['skeleton_raw_sha256']
assert len(rows)==len(draws)
log=(root/'gui.log').read_text(encoding='utf-8');assert 'POST /api/competition-live/frame ' not in log
def stats(key,data):
    x=[r[key] for r in data];return dict(p50=float(np.percentile(x,50)),p95=float(np.percentile(x,95)))
source0=load(root/'stream/sources/000000.json')
write(OUT/'performance.json',dict(session=sid,run=result['run_id'],summary=v['summary'],
    browser_cpu_compose_ms=stats('browser_cpu_compose_ms',draws),server_after_draw_pixel_audit_ms=stats('total_render_raw_ms',rows),
    browser_draw_ms=stats('skeleton_draw_ms',draws),cache_bytes=len(cached.blob),cache_sha256=cached.sha256,
    per_frame_skeleton_network_bytes=0,old_frame_endpoint_requests=0,actual_camera_first_converter_ms=source0['converter_elapsed_s']*1000,
    converter_warmup=load(root/'converter_warmup.json'),asset_writer=result['asset_writer'],capture=v['camera_evidence'],
    note='One-time geometry cache; source/721/full spatial/flow packets and small draw ACKs still transferred. CPU audit follows paint. Different camera scenes, browser hosts and viewports: not a controlled A/B.'))
fields=['session','host','viewport','steps','FPS','latency_p95_upper_ms','status']
with (OUT/'before_after.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for path in [FLY/'gui_v1/evidence/user_camera_20261015_2137/verification.json',FLY/'gui_v1/evidence/fixed_cpu_20261015/live_verification.json',OUT/'verification.json']:
        s=load(path)['summary'];env=s['browser_environment'];writer.writerow(dict(session=s['session_id'],host='/'.join(s['display_hosts']),viewport=str(env['width'])+'x'+str(env['height']),steps=s['computed_steps'],FPS=s['display_FPS'],latency_p95_upper_ms=s['receipt_to_draw_p95_upper_ms'],status=s['status']))
a=load(FLY/'gui_v1/runtime/demo_active.json');assert a['session_id']==sid and a['state']=='STOPPED'
alive=[x['pid'] for x in a['children'] if psutil.pid_exists(x['pid'])]
renderer=psutil.pid_exists(h['pid']) and abs(psutil.Process(h['pid']).create_time()-h['pid_create_time'])<1e-5
parent=psutil.pid_exists(h['parent_pid']) and abs(psutil.Process(h['parent_pid']).create_time()-h['parent_create_time'])<1e-5
with socket.socket() as s:s.settimeout(1);closed=s.connect_ex(('127.0.0.1',8771))!=0
ack=load(root/'worker_shutdown.json');assert not alive and not renderer and not parent and closed and ack['CUDA_synchronized'] and ack['shared_lock_closed']
write(OUT/'owned_shutdown.json',dict(state=a['state'],session=sid,exit_codes=a['exit_codes'],owned_children_alive=alive,renderer_alive=renderer,parent_alive=parent,port8771_closed=closed,CUDA_ack=ack,camera_closed=v['camera_evidence']['capture']['closed']))
sources=['gui_v1/cached_skeleton.py','gui_v1/competition_live.py','gui_v1/server.py','gui_v1/stream_renderer.py','gui_v1/demo_launcher.py','gui_v1/live_worker.py','gui_v1/verify_fixed_cpu.py','gui_v1/test_cached_skeleton.py','gui_v1/test_cached_skeleton.js','viewer/fixed_skeleton.js','viewer/competition_live.js','viewer/index.html']
sources += ['flyvis-3d-studio/activity_replay_20261014/live_canvas_cpu_20261015/'+x for x in ['service.py','research_guard.py','fixed_cpu.py']]
write(OUT/'delivery_sources.json',{p:sha(FLY/p) for p in sources})
print(json.dumps(dict(status='PASS',browser_compose_ms=stats('browser_cpu_compose_ms',draws),first_conversion_ms=source0['converter_elapsed_s']*1000,cache_bytes=len(cached.blob),shutdown=a['state'])))
