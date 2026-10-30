"""Preserve old acceptance/source identities and seal this GUI-only addition."""
from datetime import datetime,timezone
import json
from data_store import ROOT,read_json,sha256


def main():
    evidence=ROOT/'gui_v1/evidence/scientific_pilot_20261011'
    old=read_json(ROOT/'gui_v1/evidence/phase4/closeout.json')
    retained={}
    for group in ('source_files','protected_files'):
        for path,digest in old[group].items():assert sha256(path)==digest,(group,path)
        retained[group]=len(old[group])
    previous=read_json(ROOT/'gui_v1/evidence/phase4_unified_20261011/closeout.json')
    permitted={str(ROOT/path) for path in ('gui_v1/server.py','viewer/index.html','gui_v1/README.md','gui_v1/API_CONTRACT.md')}
    for path,digest in previous['owned_files_SHA256'].items():
        if path not in permitted:assert sha256(path)==digest,path
    for name,digest in previous['evidence_SHA256'].items():
        assert sha256(ROOT/'gui_v1/evidence/phase4_unified_20261011'/name)==digest,name
    for path,digest in old['new_evidence_SHA256'].items():assert sha256(path)==digest,path
    software=read_json(evidence/'software_acceptance.json')
    assert software['status']=='PASS_READ_ONLY_SOFTWARE_PILOT'
    for path,digest in software['sources_SHA256'].items():assert sha256(path)==digest,path
    config=read_json(ROOT/'gui_v1/scientific_pilot.json')
    ar=config['autorunner'][0]
    assert sha256(ROOT/'deliverables/FlyVis_3D_Handoff_v1_20261010.zip')==old['packaging_archive_SHA256']
    files=['gui_v1/scientific_pilot.py','gui_v1/scientific_pilot.json','gui_v1/verify_scientific_pilot.py',
           'gui_v1/verify_scientific_browser.py','gui_v1/closeout_scientific_pilot.py','gui_v1/SCIENTIFIC_PILOT_CONTRACT.md',
           'viewer/scientific_pilot.js','viewer/scientific_pilot.css','gui_v1/server.py','viewer/index.html',
           'gui_v1/README.md','gui_v1/API_CONTRACT.md']
    browser=read_json(evidence/'browser_acceptance.json');assert browser['status']=='PASS_LIMITED_REAL_BROWSER'
    report={'status':'PASS_GUI_SCIENTIFIC_PILOT_REPLAY_ONLY','utc':datetime.now(timezone.utc).isoformat(),
        'preserved_old_files':retained,'old55_source_and_acceptance_unchanged':True,
        'previous_unified_evidence_files_unchanged':len(previous['evidence_SHA256']),
        'pilot_run_id':config['run_id'],'pilot_manifest_sha256':config['manifest_sha256'],
        'pilot_sealed_files_verified':software['sealed_pilot_files_verified'],
        'actual_flow_values_bitwise_verified':software['actual_flow_values'],
        'actual_browser_observations':len(browser['observations_verified']),
        'negative_checks':len(software['negative_checks']),
        'owned_files_SHA256':{str(ROOT/name):sha256(ROOT/name) for name in files},
        'evidence_SHA256':{p.name:sha256(p) for p in evidence.iterdir() if p.is_file() and p.name!='closeout.json'},
        'autorunner_registered_job':ar['job_id'],'autorunner_snapshot_only':True,
        'current_execution_service':'NOT_CONNECTED','FPGA_status':'NOT_CONNECTED','PL_execution':False,
        'new_neural_computation':False,'new_decoder_calls':0,'camera_capture':False,'board_operations':0,
        'software_pilot_independent_replication':'NOT_RUN','scientific_B':'NOT_AVAILABLE',
        'native_desktop_this_revision':'NOT_RUN','3D_packaging':'FROZEN_BY_USER',
        'runtime':{'url':'http://127.0.0.1:8771/','owned_exec_session':84680,'test_8773_stopped':True},
        'next':'④accepted sparse-recovery source/actual retained IDs/counts/flow/metrics/report/manifest; explicit read-only admission, no automatic compute.'}
    (evidence/'closeout.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','preserved_old_files','actual_flow_values_bitwise_verified','actual_browser_observations','negative_checks')}))


if __name__=='__main__':main()
