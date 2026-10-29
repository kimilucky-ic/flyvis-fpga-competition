from pathlib import Path
import hashlib,json
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026');E=P.parent/'ov5640_display_pacing_20261026';seal=json.loads((E/'before/FINAL_MANIFEST_SHA256.json').read_text());changed=['assets\\ui.js','assets\\index.html']
for name,digest in seal.items():
 if name not in changed:assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
for name in changed:seal[name]=hashlib.sha256((P/name).read_bytes()).hexdigest()
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
b=json.loads((E/'BROWSER_TIMING.json').read_text());paints=[r for r in b['rows'] if r['painted']];assert len(paints)==189;assert all(x['step_id']<y['step_id'] for x,y in zip(paints,paints[1:]));assert len({x['session_id'] for x in paints})==1
result=dict(status='PASS_CPU_AND_OFFLINE_BROWSER_DISPLAY_PACING',changed_files=changed,unchanged_sealed_files=len(seal)-2,board_notebook_firmware_receiver_unchanged=True,board_actions=0,neural_calculation_runs=0,offline_replay=dict(duration_s=12,source_frames=219,old_displayed=56,new_displayed=189,new_mean_interval_ms=b['summary']['mean_interval_ms'],new_browser_stage_means=b['summary'],strictly_increasing_display_steps=True,same_frame_identity=True,source='existing saved records via temporary local read-only replay server',limits=['Single local browser trial; viewport/fullscreen transition occurred,not a controlled universal speed ratio','No live board FPS or camera-to-screen latency claim','Board packaging queues unchanged']),temporary_service_stopped=True,production_page_refreshed=True,next_step='Operator uses unchanged fixed Notebook for next60s; keep display page open for timing export',rollback='before/index.html and before/ui.js plus original manifest')
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
