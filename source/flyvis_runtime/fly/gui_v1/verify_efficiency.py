"""Read-only evidence checks and CPU regression; never starts a device or service."""
import ast
import hashlib
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,Registry,load,require,sha,utc,write
from spatial_state import SpatialRegistry

OUT=HERE/'evidence/efficiency_20261012'
ROOT=HERE/'runtime/live/71e7d2467d5e4dc0985e48c65ad9cf0c'

def main():
    OUT.mkdir(exist_ok=True)
    from test_live_protocol import Protocol
    from test_camera_stream import CameraProtocol
    from test_realtime_prepare import Realtime
    from test_stream import StreamTests
    from test_stream_efficiency import Efficiency
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (Protocol,CameraProtocol,Realtime,StreamTests,Efficiency))
    output=io.StringIO();tested=unittest.TextTestRunner(stream=output).run(suite)
    (OUT/'cpu_tests.log').write_text(output.getvalue(),encoding='utf-8');require(tested.wasSuccessful(),'CPU_TEST_FAILURE')
    import verify_live_interfaces
    with patch.object(verify_live_interfaces,'write'):preservation=verify_live_interfaces.verify()
    write(OUT/'preservation.json',preservation)
    js=subprocess.run([r'C:\Program Files\nodejs\node.exe',str(HERE/'test_spatial_view.cjs')],cwd=HERE,capture_output=True,text=True,check=True)
    write(OUT/'javascript_behavior.json',json.loads(js.stdout))
    names=['stream_runtime.py','realtime_timing.py','demo_launcher.py','realtime_benchmark.py','test_stream_efficiency.py','verify_efficiency.py']
    for name in names:ast.parse((HERE/name).read_text(encoding='utf-8'))
    p=ROOT/'stream';r=load(p/'result.json');control=load(p/'control.json');spatial=SpatialRegistry()
    commits=[json.loads(x) for x in (p/'step_commits.jsonl').read_text().splitlines()]
    require(len(commits)==r['committed_steps'] and all(x['step_id']==i and x['state_token']==i+1 and x['run_id']==r['run_id'] for i,x in enumerate(commits)),'COMMIT_CHAIN')
    manifest=load(p/'manifest.json')
    for file,digest in manifest.items():require(sha(p/file)==digest,'STREAM_ARTIFACT_CHANGED '+file)
    sources={}
    for f in sorted((p/'sources').glob('*.json')):
        source=load(f);seq=source['sequence'];x=np.load(f.with_name(f.stem+'_hex.npy'),allow_pickle=False)
        require(source['run_id']==r['run_id'] and sha(f.with_suffix('.png'))==source['png_sha256'],'SOURCE_IDENTITY')
        require(hashlib.sha256(x.tobytes()).hexdigest()==source['hex_values_sha256'],'HEX_IDENTITY');sources[seq]=source
    for row in commits:
        s=sources[row['source_sequence']]
        require(row['input_hex_values_sha256']==s['hex_values_sha256'] and s['relative_s']<=row['step_id']*.005,'COMMIT_INPUT_IDENTITY')
    snapshots={}
    for f in sorted((p/'snapshots').glob('*.json')):
        m=load(f);a=np.load(f.with_suffix('.npz'),allow_pickle=False);k=m['step_id'];seq=m['source_sequence']
        require(m['run_id']==r['run_id'] and m['binding']==control['binding'] and m['PL_execution'] is False,'SNAPSHOT_RUN')
        require(a['full'].shape==(45669,) and a['flow'].shape==(2,721) and np.isfinite(a['full']).all() and np.isfinite(a['flow']).all(),'FULL_AND_FLOW')
        spatial.validate({**m['spatial'],'values':spatial.extract(a['full']).tolist()},r['run_id'],k,k*.005+.005,'Full')
        require(np.array_equal(a['input'],np.load(p/'sources'/f'{seq:06}_hex.npy')) and commits[k]['source_sequence']==seq,'SNAPSHOT_INPUT')
        snapshots[m['serial']]=m
    draws=[json.loads(x) for x in (p/'display_receipts.jsonl').read_text().splitlines()]
    require(all(d['run_id']==r['run_id'] and snapshots[d['serial']]['step_id']==d['step_id'] for d in draws),'DRAW_BINDING')
    span=(draws[-1]['draw_server_monotonic_ns']-draws[0]['draw_server_monotonic_ns'])/1e9
    metrics=dict(run_id=r['run_id'],session_id=r['session_id'],steps=r['committed_steps'],wall_s=r['elapsed_s'],steps_per_s=r['inference_steps_per_s'],
        snapshots=len(snapshots),draws=len(draws),draw_span_s=span,display_FPS=(len(draws)-1)/span,
        receipt_to_draw_p95_upper_ms=float(np.percentile([d['upper_ms'] for d in draws],95)),
        browser_draw_p50_ms=float(np.median([d['render_ms'] for d in draws])),browser_draw_p95_ms=float(np.percentile([d['render_ms'] for d in draws],95)),
        power_mode_user_label=load(ROOT/'session.json')['power_mode_user_label'],power_mode_program_verified=False,
        converter_first_ms=sources[0]['converter_elapsed_s']*1000,
        converter_later_p50_ms=float(np.median([s['converter_elapsed_s']*1000 for i,s in sources.items() if i])),
        status='EARLY_OVERLOAD_STOPPED',REALTIME_STREAM_PASS='NOT_MET',LIVE_CAMERA_GPU_PASS='NOT_RUN')
    metrics['stages']=r['stages'];write(OUT/'measurements.json',metrics)
    require(load(ROOT/'worker_shutdown.json')['shared_lock_closed'] and load(HERE/'runtime/demo_active.json')['state']=='STOPPED','STOP_NOT_ACKNOWLEDGED')
    failed_graph={}
    for rid in ('074eddd9e0994a70999906d460f68a74','ecb73c7ffb9643c1a0200016dfb7d927'):
        f=HERE/'runtime/benchmarks'/rid;v=load(f/'failure.json')
        require(v['step']==0 and load(f/'shutdown.json')['shared_lock_closed'],'FAILED_CAPTURE_NOT_CLOSED')
        failed_graph[rid]=dict(failure=v,files={n:sha(f/n) for n in ('scope.json','failure.json','worker.log','shutdown.json','launcher_result.json')})
    require(not any(x in sys.modules for x in ('torch','flyvis','cv2')),'DEVICE_LOADED_BY_CPU_VERIFIER')
    write(OUT/'verification.json',dict(utc=utc(),CPU_tests=tested.testsRun,JS_tests=json.loads(js.stdout),
        source_frames=len(sources),committed_steps=len(commits),snapshots=len(snapshots),draw_receipts=len(draws),
        complete_original_model=True,original_core_pins=39,preserved_old55=True,model=Registry().data['model'],
        manifest_sha256=sha(p/'manifest.json'),weights_and_decoder_unchanged=r['original_weights_unchanged'] and r['decoder_unchanged'],
        graph_trials=failed_graph,graph_status='REJECTED_NOT_IN_PRODUCTION',new_graph_output_steps=0,
        files_sha256={str(HERE/n):sha(HERE/n) for n in names},launcher_sha256=sha(HERE.parent/'start_flyvis_demo.ps1'),
        GUI_and_worker='STOPPED',camera_operations=0,board_operations=0,REALTIME_STREAM_PASS='NOT_MET'))
    print(json.dumps({k:v for k,v in metrics.items() if k!='stages'}))

if __name__=='__main__':main()
