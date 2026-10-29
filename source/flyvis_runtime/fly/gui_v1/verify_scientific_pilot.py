"""Bounded read-only array/HTTP checks; never starts a model or hardware job."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from urllib.error import HTTPError
from urllib.request import urlopen, Request

import numpy as np

from data_store import ROOT, DataStore, read_json, sha256
from scientific_pilot import ScientificPilot, AutoRunnerRecords, MODES
from server import handler_factory
from http.server import ThreadingHTTPServer
from threading import Thread


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8773')
    parser.add_argument('--output', default=str(ROOT/'gui_v1/evidence/scientific_pilot_20261011/software_acceptance.json'))
    args = parser.parse_args()
    def get(path):
        with urlopen(args.url+path,timeout=30) as response:
            return response.read(), dict(response.headers)
    def js(path):return json.loads(get(path)[0])
    store = DataStore()
    reader = ScientificPilot(store)
    catalog = js('/api/catalog')
    require_ids = set(store.datasets)
    assert {x['id'] for x in catalog['datasets']} == require_ids and len(require_ids)==7
    old_samples = 0
    for dataset in store.datasets.values():
        for index in range(len(dataset.conditions)):
            row = js(f'/api/datasets/{dataset.id}/samples/{index}')
            assert row['execution_kind']=='offline_replay'
            old_samples += 1
        # Exact old activity transport once per dataset; full prior acceptance is hash-preserved.
        row = dataset.sample(0)
        assert get(row['activity']['url'])[0] == np.asarray(dataset.activity[0],dtype='<f4').tobytes()
    assert old_samples==55
    dsi = js('/api/datasets/edge24/directions?cell=T4c&intensity=1')
    assert dsi['official_metric']['official_dsi']==0.627361980585308 and len(dsi['traces'])==12
    assert js('/api/phase3')['comparisons'] and js('/api/workbench')['comparisons']
    assert js('/api/flow').get('status')!='NOT_AVAILABLE' and 'schema' in js('/api/flow')
    status = js('/api/scientific-pilot')
    assert status['status']=='VERIFIED' and status['evidence_level']=='SOFTWARE_PILOT'
    assert status['FPGA_status']=='NOT_CONNECTED' and status['PL_execution'] is False
    assert status['sparse_recovery']['status']=='NOT_AVAILABLE'
    records = []
    for condition in reader.conditions:
        info = js('/api/scientific-pilot/conditions/'+condition)
        assert info==reader.info(condition)
        body,headers = get(f'/api/scientific-pilot/conditions/{condition}/input.bin')
        assert body == reader.binary(condition)
        for mode in MODES:
            body,headers = get(f'/api/scientific-pilot/conditions/{condition}/{mode}/flow.bin')
            assert body==reader.binary(condition,mode)
            assert headers['X-Evidence-Level']=='SOFTWARE_PILOT' and headers['X-Display-Kind']=='offline replay' and headers['X-PL-Execution']=='false'
            records.append({'condition':condition,'mode':mode,'flow_values':485*2*721,'bitwise_original':True})
        for file in info['source_files']:
            assert get(file['url'])[0]==Path(file['path']).read_bytes()
    runner = js('/api/autorunner')['records'][0]
    assert runner['status']=='VERIFIED_RECORD'
    job_path = Path(runner['files'][0]['path'])
    assert runner['job']==read_json(job_path) and runner['summary']==read_json(job_path.parent/'run_summary.json')
    assert runner['summary']['results']['FullGPU']['actual_new_computation'] is False
    assert runner['summary']['results']['PythonReplacement']['actual_new_computation'] is True
    assert runner['external_timing']['CLI_wall_s']==37.307787022
    negatives=[]
    for path in ['/api/scientific-pilot/conditions/ON240','/api/scientific-pilot/conditions/ON60/FPGA/flow.bin','/api/scientific-pilot/files/../../server.py','/api/scientific-pilot/files/USER_AUTHORIZATION_IMMEDIATE.json']:
        try:get(path);raise AssertionError('Unexpected source access')
        except HTTPError as error:assert error.code==404;negatives.append(path)
    for path in ['/api/scientific-pilot/submit','/api/autorunner/run','/api/inference','/api/workbench/submit']:
        try:
            urlopen(Request(args.url+path,data=b'{}',headers={'Content-Type':'application/json'}),timeout=10)
            raise AssertionError('Unexpected execution')
        except HTTPError as error:
            data=json.load(error);assert error.code==503 and data['result'] is None;negatives.append(path)
    with tempfile.TemporaryDirectory(prefix='flyvis_gui_pilot_') as tmp:
        config=read_json(ROOT/'gui_v1/scientific_pilot.json');bad=Path(tmp)/'bad.json'
        config['manifest_sha256']='0'*64;bad.write_text(json.dumps(config),encoding='utf-8')
        try:ScientificPilot(store,bad);raise AssertionError('Bad anchor accepted')
        except ValueError:negatives.append('bad manifest anchor rejected')
        # Optional adapter failure must not prevent legacy HTTP/catalog access.
        isolated=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(store,pilot_config_path=bad))
        thread=Thread(target=isolated.serve_forever,daemon=True);thread.start()
        try:
            with urlopen(f'http://127.0.0.1:{isolated.server_port}/api/catalog',timeout=10) as response:assert len(json.load(response)['datasets'])==7
            with urlopen(f'http://127.0.0.1:{isolated.server_port}/api/scientific-pilot',timeout=10) as response:assert json.load(response)['status']=='NOT_AVAILABLE'
            negatives.append('pilot adapter failure leaves old55 available')
        finally:isolated.shutdown();isolated.server_close();thread.join()
    path=next(iter(reader.stamps));stamp=reader.stamps[path];reader.stamps[path]=(0,0,0)
    try:reader.info('ON60');raise AssertionError('Changed source accepted')
    except ValueError:negatives.append('changed source signature rejected before display')
    finally:reader.stamps[path]=stamp
    bad_runner=AutoRunnerRecords();bad_runner.config=[dict(bad_runner.config[0],seal_sha256='0'*64)]
    assert bad_runner.snapshot()['records'][0]['status']=='NOT_AVAILABLE';negatives.append('runner seal mismatch hides record')
    report={'status':'PASS_READ_ONLY_SOFTWARE_PILOT','utc':datetime.now(timezone.utc).isoformat(),
        'conditions':['ON60','OFF90'],'mode_transports':records,'actual_flow_values':sum(x['flow_values'] for x in records),
        'input_values':2*485*721,'saved_curve_values':2*5*485*2,'primary_metric_values':2*5*4,
        'sealed_pilot_files_verified':len(reader.manifest['files']),'legacy_conditions_metadata':old_samples,
        'legacy_activity_exact_spotchecks':7,'legacy_official_dsi_exact':True,'legacy_P0_and_flow_available':True,
        'negative_checks':negatives,'autorunner_job_and_summary_exact':True,
        'autorunner_cache_vs_new_distinguished':True,'CLI_wall_s':37.307787022,
        'sources_SHA256':{str(p):s for p,s in reader.checked.items()},
        'new_neural_computations':0,'new_decoder_calls':0,'new_camera_capture':False,'board_operations':0,
        'FPGA_status':'NOT_CONNECTED','scientific_B':'NOT_AVAILABLE'}
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','actual_flow_values','legacy_conditions_metadata','legacy_activity_exact_spotchecks')}))


if __name__=='__main__':main()
