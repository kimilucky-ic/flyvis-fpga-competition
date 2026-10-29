"""Read-only acceptance of the bounded sync optimization; never launches GPU/UI."""
import csv
import hashlib
import json
import subprocess
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,Registry,load,require,sha,utc,write
from spatial_state import SpatialRegistry

OUT=HERE/'evidence/sync_optimization_20261012'
ROOT=HERE/'runtime/live/b872bc4816bc4004ab9bfef9eead9008'
BENCHMARKS=('996b10559b9f4d419d9c7490ca77569f','585952e207bf40c9a5894e436c109158','ee07c7224b014593979dce23652735c1')

def main():
    import verify_live_interfaces
    with patch.object(verify_live_interfaces,'write'):preserved=verify_live_interfaces.verify()
    write(OUT/'preservation.json',preserved)
    cpu=(OUT/'cpu_tests.log').read_text();require('Ran 101 tests' in cpu and '\nOK\n' in cpu,'CPU_REGRESSION_REQUIRED')
    js=subprocess.run([r'C:\Program Files\nodejs\node.exe',str(HERE/'test_spatial_view.cjs')],capture_output=True,text=True,check=True)
    js=json.loads(js.stdout);write(OUT/'javascript_behavior.json',js)
    p=ROOT/'stream';r=load(p/'result.json');control=load(p/'control.json');spatial=SpatialRegistry()
    commits=[json.loads(x) for x in (p/'step_commits.jsonl').read_text().splitlines()]
    require(len(commits)==r['committed_steps'] and all(x['step_id']==i and x['state_token']==i+1 and x['run_id']==r['run_id'] for i,x in enumerate(commits)),'COMMIT_CHAIN')
    for file,digest in load(p/'manifest.json').items():require(sha(p/file)==digest,'ARTIFACT_CHANGED '+file)
    sources={}
    for f in sorted((p/'sources').glob('*.json')):
        s=load(f);x=np.load(f.with_name(f.stem+'_hex.npy'),allow_pickle=False)
        require(s['run_id']==r['run_id'] and sha(f.with_suffix('.png'))==s['png_sha256'],'SOURCE_IDENTITY')
        require(x.shape==(721,) and hashlib.sha256(x.tobytes()).hexdigest()==s['hex_values_sha256'],'HEX_IDENTITY');sources[s['sequence']]=s
    for row in commits:
        s=sources[row['source_sequence']]
        require(row['input_hex_values_sha256']==s['hex_values_sha256'] and s['relative_s']<=row['step_id']*.005,'COMMIT_SOURCE_ALIGNMENT')
    snaps={}
    for f in sorted((p/'snapshots').glob('*.json')):
        m=load(f);a=np.load(f.with_suffix('.npz'),allow_pickle=False);k=m['step_id'];seq=m['source_sequence']
        require(m['run_id']==r['run_id'] and m['binding']==control['binding'] and m['PL_execution'] is False,'SNAPSHOT_RUN')
        require(a['full'].shape==(45669,) and a['flow'].shape==(2,721) and np.isfinite(a['full']).all() and np.isfinite(a['flow']).all(),'FULL_AND_FLOW')
        spatial.validate({**m['spatial'],'values':spatial.extract(a['full']).tolist()},r['run_id'],k,k*.005+.005,'Full')
        require(np.array_equal(a['input'],np.load(p/'sources'/f'{seq:06}_hex.npy')) and commits[k]['source_sequence']==seq,'SNAPSHOT_INPUT')
        snaps[m['serial']]=m
    draws=[json.loads(x) for x in (p/'display_receipts.jsonl').read_text().splitlines()]
    require(all(d['run_id']==r['run_id'] and snaps[d['serial']]['step_id']==d['step_id'] for d in draws),'DRAW_BINDING')
    span=(draws[-1]['draw_server_monotonic_ns']-draws[0]['draw_server_monotonic_ns'])/1e9
    a=r['input_guard_adapter'];require(a['candidate_checks']==a['accepted_commits']==len(commits),'CANDIDATE_CHECKS_NOT_EVERY_STEP')
    require(a['actual_original_updates']==len(commits) and a['reused_old_finite_steps']==len(commits)-1,'ORIGINAL_UPDATES_OR_PROOF')
    metrics=dict(run_id=r['run_id'],session_id=r['session_id'],source_kind=r['source_kind'],steps=len(commits),wall_s=r['elapsed_s'],steps_per_s=r['inference_steps_per_s'],
        snapshots=len(snaps),draws=len(draws),draw_span_s=span,display_FPS=(len(draws)-1)/span,
        receipt_to_draw_p95_upper_ms=float(np.percentile([d['upper_ms'] for d in draws],95)),
        browser_draw_p50_ms=float(np.median([d['render_ms'] for d in draws])),browser_draw_p95_ms=float(np.percentile([d['render_ms'] for d in draws],95)),
        converter_first_ms=sources[0]['converter_elapsed_s']*1000,converter_later_p50_ms=float(np.median([s['converter_elapsed_s']*1000 for i,s in sources.items() if i])),
        source_frames=len(sources),reason=r['reason'],power_mode_user_label='performance',power_mode_program_verified=False,
        LIVE_INTERACTIVE_GUI_PASS='PARTIAL_GPU_OUTPUT_AND_DRAW_RECEIPTS_OVERLOAD_STOPPED',REALTIME_STREAM_PASS='NOT_MET',LIVE_CAMERA_GPU_PASS='NOT_RUN',PL_execution=False,
        input_guard_adapter=a,stages=r['stages'])
    write(OUT/'measurements.json',metrics)
    benchmarks=[]
    for rid in BENCHMARKS:
        folder=HERE/'runtime/benchmarks'/rid;b=load(folder/'result.json')
        require(b['reference_max_abs']==b['reference_flow_max_abs']==0 and b['reference_violations']==b['reference_flow_violations']==0,'BENCHMARK_NUMERICAL_PARITY')
        require(load(folder/'shutdown.json')['shared_lock_closed'] and load(folder/'launcher_result.json')['exit_code']==0,'BENCHMARK_SHUTDOWN')
        benchmarks.append(dict(run_id=rid,variant=b['spec']['variant'],steps=b['model_steps'],wall_s=b['sample_wall_s'],steps_per_s=b['steps_per_s'],
            full_state_and_flow_samples=b['reference_sample_count'],sampled_max_abs=0.,input_rejections=len(b['input_rejection_tests']),
            result_sha256=sha(folder/'result.json'),result_path=str(folder/'result.json')))
    write(OUT/'benchmarks.json',benchmarks)
    with (OUT/'performance_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        columns=['kind','run_id','steps','wall_s','steps_per_s','display_FPS','receipt_to_draw_p95_upper_ms','REALTIME_STREAM_PASS']
        out=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');out.writeheader()
        for b in benchmarks:out.writerow(dict(kind='FROZEN_GPU_BENCHMARK_'+b['variant'],REALTIME_STREAM_PASS='NOT_RUN',**b))
        previous=load(HERE/'evidence/efficiency_20261012/measurements.json');out.writerow(dict(kind='PREVIOUS_DIGITAL_FULL_CHAIN',**previous))
        out.writerow(dict(kind='CURRENT_DIGITAL_FULL_CHAIN',**metrics))
    require(load(ROOT/'worker_shutdown.json')['CUDA_synchronized'] and load(ROOT/'worker_shutdown.json')['shared_lock_closed'],'CUDA_SHUTDOWN')
    require(load(HERE/'runtime/demo_active.json')['state']=='STOPPED','GUI_NOT_STOPPED')
    for name,digest in load(ROOT/'session.json')['stream_adapter_sha256'].items():require(sha(HERE/name)==digest,'LIVE_ADAPTER_CHANGED')
    names=['checked_full.py','decoder_audit.py','realtime_benchmark.py','stream_runtime.py','demo_launcher.py','live_worker.py','test_checked_full.py','verify_sync_optimization.py']
    write(OUT/'verification.json',dict(utc=utc(),CPU_tests=101,JS_tests=js,actual_GPU_guard_negative_tests=17,source_frames=len(sources),committed_steps=len(commits),snapshots=len(snaps),draw_receipts=len(draws),
        original_core_pins=preserved['source_pins_verified'],old55='PASS_PRESERVED_NOT_RERUN',model=Registry().data['model'],
        manifest_sha256=sha(p/'manifest.json'),original_weights_unchanged=r['original_weights_unchanged'],decoder_unchanged=r['decoder_unchanged'],
        files_sha256={str(HERE/n):sha(HERE/n) for n in names},launcher_sha256=sha(HERE.parent/'start_flyvis_demo.ps1'),GUI_and_worker='STOPPED',
        camera_operations=0,board_operations=0,REALTIME_STREAM_PASS='NOT_MET',live_running_screenshot=False,actual_stop_screenshot='actual_stop_revocation.jpg'))
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('stages','input_guard_adapter')},indent=2))

if __name__=='__main__':main()
