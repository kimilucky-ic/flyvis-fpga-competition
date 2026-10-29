"""Bounded final evidence consistency and owned-renderer exit verification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1]
FLY=GUI.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
initial=read(OUT/'browser_initial.json')['receipt']
final=read(OUT/'browser_final.json')
r=final['receipt']
types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
assert r['frame_index']==213 and r['visible_types']==types and r['type_filter']=='all'
assert final['all_enabled'] and r['adapter']['adapter_type']=='CPU'
assert r['profile']=='light' and r['background_style']=='simplified_mesh' and r['rois_visible']
assert r['PL_execution'] is False and r['evidence_level']=='OFFLINE_SOFTWARE_REPLAY'
assert abs(r['camera_framing']['height_fraction']-.86)<1e-10
assert r['camera_framing']['cropped_node_count']==0
assert all(p['run']==r['run_id'] and p['frame']=='213' and
           float(p['activityTime'])==r['activity_time_s'] for p in final['panels'])
assert read(OUT/'reset_final.json')['reset_exact']
assert read(OUT/'idle_check.json')['unchanged']
assert read(OUT/'playback.json')['frame']==484
geometry=read(OUT/'background_check.json')
assert r['background_manifest_sha256']==geometry['background_manifest_sha256']
assert sum(p['rendered_faces'] for p in r['background_geometry'])==3600
owned=[]
for path in (GUI/'runtime/competition').glob('*/ready.json'):
    try: ready=read(path)
    except (ValueError,OSError): continue
    if ready.get('service_id') not in {initial['service_id'],r['service_id']}: continue
    pid=int(ready['pid'])
    result=subprocess.run(['powershell','-NoProfile','-Command',
                           f"Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}' | Select-Object -ExpandProperty ProcessId"],
                          capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=15)
    assert result.returncode==0,result.stderr
    assert not result.stdout.strip(),f'Owned renderer still alive: {pid}'
    owned.append(dict(service_id=ready['service_id'],pid=pid,exited=True))
assert len(owned)==2
port_probe=subprocess.run(['powershell','-NoProfile','-Command',
    "$taskConnections=@(Get-NetTCPConnection -State Listen -LocalPort 8771 -ErrorAction SilentlyContinue); Write-Output $taskConnections.Count; exit 0"],
    capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=15)
assert port_probe.returncode==0 and port_probe.stdout.strip()=='0',port_probe.stdout+port_probe.stderr
files=[GUI/'competition_policy.py',GUI/'competition_renderer.py',GUI/'test_competition_policy.py',
       GUI/'LIGHT_DEMO.md',GUI/'COMPETITION_3D_CONTRACT.md',FLY/'viewer/competition.js',FLY/'viewer/index.html',
       FLY/'flyvis-3d-studio/activity_replay_20261014/scene.py',
       FLY/'flyvis-3d-studio/activity_replay_20261014/bridge.py',OUT/'actual_final_home.jpg',OUT/'browser_final.json']
report=dict(status='PASS_OFFLINE_ALL_TYPES_FOCUS',utc=datetime.now(timezone.utc).isoformat(),
            final_frame=213,visible_types=types,skeleton_height_fraction=r['camera_framing']['height_fraction'],
            cropped_skeleton_nodes=0,background_source_faces=711654,background_rendered_faces=3600,
            owned_renderers=owned,user_existing_windows_not_operated=True,neural_inference_runs=0,board_operations=0,
            live_or_real_time_claim=False,qa_8771_closed=True,qa_port_probe='Windows TCP listener count = 0',
            files=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in files])
(OUT/'closeout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
