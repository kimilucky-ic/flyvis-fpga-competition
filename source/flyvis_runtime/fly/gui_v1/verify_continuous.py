"""Bounded read-only closeout: CPU tests, preserved receipts and actual stream artifacts.
Never launches a neural worker, camera, GUI or board.
"""
import ast
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,Registry,load,require,sha,utc,write
from spatial_state import SpatialRegistry

OUT=HERE/'evidence/continuous_20261012'
LATEST=HERE/'runtime/live/11e08322d3e74f4399b108a879447a4e/stream'

def main():
    OUT.mkdir(exist_ok=True)
    from test_realtime_prepare import Realtime
    from test_live_protocol import Protocol
    from test_camera_stream import CameraProtocol
    from test_stream import StreamTests
    log=io.StringIO();suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (Realtime,Protocol,CameraProtocol,StreamTests))
    result=unittest.TextTestRunner(stream=log,verbosity=1).run(suite);(OUT/'cpu_tests.log').write_text(log.getvalue(),encoding='utf-8')
    require(result.wasSuccessful(),'CPU_TEST_FAILED');require(not any(n in sys.modules for n in ('torch','flyvis','cv2')),'DEVICE_IMPORT_IN_CPU_CHECK')
    node=subprocess.run([r'C:\Program Files\nodejs\node.exe',str(HERE/'test_spatial_view.cjs')],cwd=HERE,capture_output=True,text=True,check=True)
    write(OUT/'javascript_behavior.json',json.loads(node.stdout))
    for name in ('live_camera.js','spatial_view.js','live_experiment.js'):
        subprocess.run([r'C:\Program Files\nodejs\node.exe','--check',str(HERE.parent/'viewer'/name)],capture_output=True,check=True)
    syntax=[]
    for pattern in ('stream_*.py','live_*.py','camera_stream_*.py','realtime_*.py','spatial_state.py','demo_launcher.py','server.py'):
        for p in HERE.glob(pattern):ast.parse(p.read_text(encoding='utf-8-sig'));syntax.append(p.name)
    # Reuse the established lightweight verifier without overwriting its old receipt.
    import verify_live_interfaces
    with patch.object(verify_live_interfaces,'write'):old=verify_live_interfaces.verify()
    write(OUT/'preservation.json',old)
    spatial=SpatialRegistry();control=load(LATEST/'control.json');run=load(LATEST/'result.json')
    require(run['model']==Registry().data['model'] and run['source_kind']=='digital_direct' and run['PL_execution'] is False,'STREAM_ACTUAL_IDENTITY')
    commits=[json.loads(line) for line in (LATEST/'step_commits.jsonl').read_text().splitlines()]
    require(len(commits)==run['committed_steps'] and all(r['step_id']==i and r['state_token']==i+1 and r['run_id']==run['run_id'] for i,r in enumerate(commits)),'COMMIT_CONTINUITY')
    checked=[];source_hashes={}
    for path in sorted((LATEST/'snapshots').glob('*.json')):
        p=load(path);a=np.load(path.with_suffix('.npz'),allow_pickle=False);k=p['step_id'];source=p['source'];seq=source['sequence']
        require(p['run_id']==run['run_id'] and p['binding']==control['binding'] and p['device']['type']=='cuda','SNAPSHOT_IDENTITY')
        require(a['full'].shape==(45669,) and a['flow'].shape==(2,721) and a['input'].shape==(721,),'SNAPSHOT_ARRAYS')
        require(all(np.isfinite(a[n]).all() for n in ('full','flow','input')),'NONFINITE_SNAPSHOT')
        values=spatial.extract(a['full']);spatial.validate({**p['spatial'],'values':values.tolist()},run['run_id'],k,k*.005+.005,'Full')
        saved=np.load(LATEST/'sources'/f'{seq:06}_hex.npy',allow_pickle=False)
        require(np.array_equal(a['input'],saved) and commits[k]['source_sequence']==seq,'COMMITTED_INPUT_ALIGNMENT')
        require(source['relative_s']<=k*.005 and p['activity_time_s']==k*.005+.005,'SOURCE_EULER_ALIGNMENT')
        png=LATEST/'sources'/f'{seq:06}.png';require(sha(png)==source['png_sha256'],'SOURCE_PNG_IDENTITY');source_hashes[str(png)]=sha(png)
        checked.append(dict(serial=p['serial'],step=k,source_sequence=seq,array_sha256=sha(path.with_suffix('.npz')),metadata_sha256=sha(path)))
    receipts=[json.loads(x) for x in (LATEST/'display_receipts.jsonl').read_text().splitlines()]
    lookup={x['serial']:x for x in checked}
    require(all(r['run_id']==run['run_id'] and lookup[r['serial']]['step']==r['step_id'] for r in receipts),'DRAW_COMMIT_IDENTITY')
    span=(receipts[-1]['draw_server_monotonic_ns']-receipts[0]['draw_server_monotonic_ns'])/1e9
    require(load(LATEST.parent/'worker_shutdown.json')['shared_lock_closed'],'GPU_LOCK_RELEASE_NOT_ACKNOWLEDGED')
    require(load(HERE/'runtime/demo_active.json')['state']=='STOPPED','LAUNCHER_STILL_ACTIVE')
    browser=dict(status='PARTIAL_LIVE_DIGITAL_DISPLAY_THEN_OVERLOAD_REVOKED',run_id=run['run_id'],actual_draws=len(receipts),draw_span_s=span,
        FPS_between_first_last_draw=(len(receipts)-1)/span,p95_receipt_to_draw_upper_ms=float(np.percentile([r['upper_ms'] for r in receipts],95)),
        observed_all_eight_maps_last_step=181,nodes_per_type=721,source_image_cleared_after_failure=True,
        actual_stop_ack_text='已停止 · CUDA在途工作完成，读数已撤销',screenshot='actual_stop_revocation.jpg',
        browser_console_errors_observed=0,LIVE_INTERACTIVE_GUI_PASS='NOT_PASSED_EARLY_OVERLOAD',REALTIME_STREAM_PASS='NOT_MET',
        ten_second_stream_acceptance=False,camera_acceptance='NOT_RUN_USER_MUST_START',FPGA_status='NOT_CONNECTED')
    write(OUT/'browser_acceptance.json',browser)
    rows=[]
    for rid in ('e869e084a9444ef2bbf820d818397afa','afcfddf914314b70928ca65a483b413b'):
        p=HERE/'runtime/benchmarks'/rid;r=load(p/'result.json')
        rows.append(dict(kind='FROZEN_INPUT_COMPUTE_BENCHMARK',run_id=rid,power_mode='current_unconfirmed',steps=r['model_steps'],wall_s=r['sample_wall_s'],steps_per_s=r['steps_per_s'],
            display_samples=r['display_samples'],GUI_FPS='',receipt_to_draw_p95_ms='',state_samples_checked=r['reference_sample_count'],state_max_abs=r['reference_max_abs'],
            flow_max_abs=r.get('reference_flow_max_abs',''),launcher='EXIT_0' if (p/'launcher_result.json').exists() else 'FAILED_WINDOWS_HEARTBEAT_REPLACE',REALTIME_STREAM_PASS='NOT_RUN'))
    for sid in ('d3e8ab1f731141b2b346b478f1723d7b','11e08322d3e74f4399b108a879447a4e'):
        p=HERE/'runtime/live'/sid/'stream';r=load(p/'result.json')
        rows.append(dict(kind='ACTUAL_LIVE_DIGITAL_THEN_OVERLOAD',run_id=r['run_id'],power_mode='current_unconfirmed',steps=r['committed_steps'],wall_s=r['elapsed_s'],steps_per_s=r['inference_steps_per_s'],
            display_samples=r['snapshots'],GUI_FPS=browser['FPS_between_first_last_draw'] if p==LATEST else '',receipt_to_draw_p95_ms=load(p/'display_summary.json')['stages']['receipt_to_render_upper_bound']['p95_ms'],
            state_samples_checked='',state_max_abs='',flow_max_abs='',launcher='COOPERATIVE_STOP_ACK',REALTIME_STREAM_PASS='NOT_MET'))
    with (OUT/'performance_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write(OUT/'verification.json',dict(status='PASS_CPU_AND_RECORDED_EVIDENCE_CHECKS_LIVE_PERFORMANCE_NOT_MET',utc=utc(),
        CPU_tests=result.testsRun,JS_behavior_tests=9,syntax_files=sorted(set(syntax)),preserved_old55=True,original_core_pins=39,
        snapshot_count=len(checked),verified_full_state_values=len(checked)*45669,verified_spatial_values=len(checked)*5768,
        verified_official_flow_values=len(checked)*1442,committed_steps=len(commits),checked_snapshots=checked,selected_source_SHA256=source_hashes,
        note='Read-only checks of failed-but-actually-executed digital run. This verifier runs no neural computation.',
        camera_operations=0,board_operations=0,LIVE_INTERACTIVE_GUI_PASS='NOT_PASSED_EARLY_OVERLOAD',REALTIME_STREAM_PASS='NOT_MET'))
    print(json.dumps(dict(CPU_tests=result.testsRun,JS_tests=9,actual_snapshots=len(checked),actual_draws=len(receipts),GUI_FPS=browser['FPS_between_first_last_draw'],p95_ms=browser['p95_receipt_to_draw_upper_ms'])))

if __name__=='__main__':main()
