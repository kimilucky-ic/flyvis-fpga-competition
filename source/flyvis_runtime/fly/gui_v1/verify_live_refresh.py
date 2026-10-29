"""Read-only measured stream/evidence audit; never launches GPU, camera or board."""
import argparse,csv,hashlib,json
from pathlib import Path
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,Registry,load,require,sha,utc,write
from spatial_state import SpatialRegistry

OUT=HERE/'evidence/live_refresh_20261014'
def preserve():
    registry=Registry();evidence=HERE/'evidence';checked={}
    # app.js was intentionally changed by the accepted Oct 13 explanatory home.
    # Its Oct 11 hash is not a valid current baseline. Do not rewrite old receipts.
    ui={str(HERE/'server.py'),str(HERE.parent/'viewer/index.html'),str(HERE.parent/'viewer/app.js')}
    for folder,key in [('phase4','protected_files'),('scientific_sparse_20261012','owned_files_SHA256')]:
        for path,digest in load(evidence/folder/'closeout.json')[key].items():
            if path in ui or Path(path).stat().st_size>8*1024*1024:continue
            require(sha(path)==digest,'PRESERVED_SOURCE_CHANGED '+path);checked[path]=digest
    receipts={}
    for folder in ('scientific_sparse_20261012','scientific_pilot_20261011','phase4_unified_20261011'):
        for file,digest in load(evidence/folder/'closeout.json')['evidence_SHA256'].items():
            require(sha(evidence/folder/file)==digest,'ACCEPTANCE_CHANGED '+file);receipts[folder+'/'+file]=digest
    for entry in load(evidence/'demo_home_20261013/manifest.json'):
        path=entry['path']
        if path.startswith('gui_v1/evidence/'):
            require(sha(HERE.parent/path)==entry['sha256'],'OCT13_ACCEPTANCE_CHANGED '+path);receipts[path]=entry['sha256']
    require(all(load(evidence/'phase4_unified_20261011'/name)['status']=='PASS' for name in ('offline38_regression.json','camera_bar11_regression.json','controlled6_regression.json')),'OLD55_RECEIPTS')
    return dict(status='PASS_SOURCE_AND_PRIOR_ACCEPTANCE_PRESERVATION',source_pins_verified=len(registry.pins),old55_previous_receipts='PASS_PRESERVED_NOT_RERUN',preserved_code=checked,preserved_receipts=receipts,authorized_UI_exceptions=sorted(ui),exception_reason='server/index current integration; app.js accepted Oct13 guide, unchanged in this task')

def audit(sid):
    root=HERE/'runtime/live'/sid;p=root/'stream';r=load(p/'result.json');control=load(p/'control.json');spatial=SpatialRegistry()
    commits=[json.loads(x) for x in (p/'step_commits.jsonl').read_text().splitlines()]
    require(all(x['step_id']==i and x['state_token']==i+1 and x['run_id']==r['run_id'] for i,x in enumerate(commits)),'COMMIT_CHAIN')
    missing=r['committed_steps']-len(commits)
    require(missing==0 or (missing==1 and not r['success'] and not r['result_valid'] and r['reason']=='EVIDENCE_QUEUE_FULL_NO_SILENT_LOSS'),'UNEXPLAINED_COMMIT_GAP')
    for file,digest in load(p/'manifest.json').items():require(sha(p/file)==digest,'ARTIFACT_CHANGED '+file)
    sources={}
    for f in sorted((p/'sources').glob('*.json')):
        s=load(f);x=np.load(f.with_name(f.stem+'_hex.npy'),allow_pickle=False)
        require(s['run_id']==r['run_id'] and sha(f.with_suffix('.png'))==s['png_sha256'],'SOURCE_IDENTITY')
        require(x.shape==(721,) and hashlib.sha256(x.tobytes()).hexdigest()==s['hex_values_sha256'],'HEX_IDENTITY');sources[s['sequence']]=s
    for row in commits:
        s=sources[row['source_sequence']]
        require(row['input_hex_values_sha256']==s['hex_values_sha256'] and s['relative_s']<=row['step_id']*.005,'CAUSAL_INPUT')
    snaps={}
    for f in sorted((p/'snapshots').glob('*.json')):
        m=load(f);a=np.load(f.with_suffix('.npz'),allow_pickle=False);k=m['step_id'];seq=m['source_sequence']
        require(m['run_id']==r['run_id'] and m['binding']==control['binding'] and m['PL_execution'] is False,'SNAPSHOT_RUN')
        require(a['full'].shape==(45669,) and a['flow'].shape==(2,721) and np.isfinite(a['full']).all() and np.isfinite(a['flow']).all(),'FULL_AND_FLOW')
        spatial.validate({**m['spatial'],'values':spatial.extract(a['full']).tolist()},r['run_id'],k,k*.005+.005,'Full')
        require(np.array_equal(a['input'],np.load(p/'sources'/f'{seq:06}_hex.npy')) and commits[k]['source_sequence']==seq,'SNAPSHOT_INPUT');snaps[m['serial']]=m
    draws=[json.loads(x) for x in (p/'display_receipts.jsonl').read_text().splitlines()]
    require(draws and all(d['run_id']==r['run_id'] and snaps[d['serial']]['step_id']==d['step_id'] for d in draws),'DRAW_BINDING')
    span=(draws[-1]['draw_server_monotonic_ns']-draws[0]['draw_server_monotonic_ns'])/1e9
    a=r['input_guard_adapter'];require(a['candidate_checks']==a['accepted_commits']==a['actual_original_updates']==r['committed_steps'],'EVERY_STEP_REQUIRED')
    require(load(root/'worker_shutdown.json')['CUDA_synchronized'] and load(root/'worker_shutdown.json')['shared_lock_closed'],'CUDA_SHUTDOWN')
    session=load(root/'session.json');require(session['camera_enabled'] is False and session['board_enabled'] is False,'DIGITAL_ONLY')
    return dict(run_id=r['run_id'],session_id=sid,steps=r['committed_steps'],durable_commit_records=len(commits),missing_terminal_commit_records=missing,evidence_integrity='FAIL_INCOMPLETE_COMMIT_EVIDENCE' if missing else 'PASS',wall_s=r['elapsed_s'],steps_per_s=r['inference_steps_per_s'],source_frames=len(sources),
        snapshots=len(snaps),draws=len(draws),draw_span_s=span,display_FPS=(len(draws)-1)/span,receipt_to_draw_p95_upper_ms=float(np.percentile([d['upper_ms'] for d in draws],95)),
        browser_draw_p50_ms=float(np.median([d['render_ms'] for d in draws])),browser_draw_p95_ms=float(np.percentile([d['render_ms'] for d in draws],95)),
        raf_wait_p50_ms=float(np.median([d['raf_wait_ms'] for d in draws])) if 'raf_wait_ms' in draws[0] else None,
        latest_packet_slot_age_p50_ms=float(np.median([d['packet_slot_age_ms'] for d in draws])) if 'packet_slot_age_ms' in draws[0] else None,
        converter_later_p50_ms=float(np.median([s['converter_elapsed_s']*1000 for i,s in sources.items() if i])),
        reason=r['reason'],manifest_sha256=sha(p/'manifest.json'),model=r['model'],original_weights_unchanged=r['original_weights_unchanged'],decoder_unchanged=r['decoder_unchanged'],
        LIVE_INTERACTIVE_GUI_PASS='NOT_PASSED_INCOMPLETE_EVIDENCE' if missing else ('ACTUAL_LIVE_OUTPUT_VERIFIED_OVERLOAD_STOPPED' if not r['success'] else 'PASS_BOUNDED_LIVE_DIGITAL_OUTPUT'),
        REALTIME_STREAM_PASS='NOT_MET',LIVE_CAMERA_GPU_PASS='NOT_RUN',PL_execution=False,stages=r['stages'],display_summary=load(p/'display_summary.json'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--sessions',nargs='+',required=True);p.add_argument('--benchmarks',nargs='+',required=True);args=p.parse_args()
    preserved=preserve()
    write(OUT/'preservation.json',preserved)
    rows=[audit(s) for s in args.sessions];write(OUT/'measurements.json',rows)
    benchmarks=[]
    for rid in args.benchmarks:
        folder=HERE/'runtime/benchmarks'/rid;b=load(folder/'result.json')
        require(b['reference_violations']==b['reference_flow_violations']==0 and b['reference_sample_count']>0,'BENCHMARK_PARITY')
        require(load(folder/'shutdown.json')['shared_lock_closed'] and load(folder/'launcher_result.json')['exit_code']==0,'BENCHMARK_SHUTDOWN')
        benchmarks.append(dict(run_id=rid,steps=b['model_steps'],wall_s=b['sample_wall_s'],steps_per_s=b['steps_per_s'],full_state_and_flow_samples=b['reference_sample_count'],reference_max_abs=b['reference_max_abs'],reference_flow_max_abs=b['reference_flow_max_abs'],input_rejections=len(b['input_rejection_tests']),result_sha256=sha(folder/'result.json')))
    write(OUT/'benchmarks.json',benchmarks)
    with (OUT/'performance_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        columns=['kind','run_id','steps','wall_s','steps_per_s','display_FPS','receipt_to_draw_p95_upper_ms','REALTIME_STREAM_PASS']
        out=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');out.writeheader()
        previous=load(HERE/'evidence/sync_optimization_20261012/measurements.json');out.writerow(dict(kind='HISTORICAL_20261012_NOT_PAIRED',**previous))
        for b in benchmarks:out.writerow(dict(kind='FROZEN_INPUT_GPU_BENCHMARK',REALTIME_STREAM_PASS='NOT_RUN',**b))
        for r in rows:out.writerow(dict(kind='NEW_DIGITAL_INPUT_GPU_GUI',**r))
    write(OUT/'verification.json',dict(status='VERIFIED_FINDINGS_NOT_ALL_RUNS_PASSED',utc=utc(),incomplete_evidence_runs=[r['run_id'] for r in rows if r['missing_terminal_commit_records']],original_source_pins=preserved['source_pins_verified'],old55='PASS_PRESERVED_NOT_RERUN',sessions=args.sessions,benchmarks=args.benchmarks,camera_operations=0,board_operations=0,REALTIME_STREAM_PASS='NOT_MET'))
    print(json.dumps([ {k:v for k,v in r.items() if k not in ('stages','display_summary','model')} for r in rows],indent=2))
if __name__=='__main__':main()
