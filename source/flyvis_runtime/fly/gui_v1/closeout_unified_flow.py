"""Seal GUI-only evidence and verify previously accepted artifacts remain unchanged."""
from datetime import datetime,timezone
import json

from data_store import ROOT,read_json,sha256


def main():
    evidence=ROOT/'gui_v1/evidence/phase4_unified_20261011'
    prior=read_json(ROOT/'gui_v1/evidence/phase4/closeout.json')
    checked={}
    for group in ('source_files','protected_files'):
        changed=[path for path,digest in prior[group].items() if sha256(path)!=digest]
        assert not changed,(group,changed)
        checked[group]=len(prior[group])
    preparation=ROOT/'camera_pipeline/phase4_phone_camera_20261010_r1'
    seal=read_json(preparation/'manifest.json')
    assert sha256(preparation/'manifest.json')=='3732df799028cca136816f1f72b49828d34c04ee6b129635cf967a3baff933b5'
    for name,digest in seal['files'].items():assert sha256(preparation/name)==digest,name
    frozen_archive=ROOT/'deliverables/FlyVis_3D_Handoff_v1_20261010.zip'
    assert sha256(frozen_archive)==prior['packaging_archive_SHA256']
    for name,digest in prior['new_evidence_SHA256'].items():assert sha256(name)==digest,name
    files=['gui_v1/unified_flow.py','gui_v1/verify_unified_flow.py','gui_v1/verify_unified_browser.py',
           'gui_v1/closeout_unified_flow.py','gui_v1/UNIFIED_FLOW_CONTRACT.md','gui_v1/server.py',
           'gui_v1/README.md','gui_v1/API_CONTRACT.md','viewer/index.html','viewer/workbench.js',
           'viewer/unified_flow.js','viewer/unified_flow.css']
    reports={p.name:read_json(p) for p in evidence.glob('*regression.json')}
    assert len(reports)==5
    software=read_json(evidence/'software_acceptance.json');browser=read_json(evidence/'browser_acceptance.json')
    assert software['status']=='PASS_SOFTWARE_STRUCTURE_ONLY' and len(software['negative_checks'])==14
    assert browser['status']=='PASS_SOFTWARE_BROWSER_ONLY'
    report={'schema':'flyvis-unified-GUI-closeout-v1','utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS_GUI_SOFTWARE_FLOW_AND_REPLAY_ONLY','historical_conditions':55,
        'preserved_files_SHA256':checked,'phone_preparation_files_SHA256_unchanged':len(seal['files']),
        'previous_phase4_evidence_SHA256_unchanged':len(prior['new_evidence_SHA256']),
        'packaging_status':'FROZEN_BY_USER','packaging_archive_SHA256':prior['packaging_archive_SHA256'],
        'owned_files_SHA256':{str(ROOT/name):sha256(ROOT/name) for name in files},
        'evidence_SHA256':{p.name:sha256(p) for p in evidence.iterdir() if p.is_file() and p.name!='closeout.json'},
        'software_negative_checks':14,'actual_browser_readouts_verified':11,
        'no_new_capture':True,'no_new_neural_computation':True,'no_board_operations':True,
        'new_interactive_721_export':'NOT_AVAILABLE','new_phone_input_e2e':'NOT_RUN',
        'formal_job_service_e2e':'NOT_RUN','new_ablation_result':'NOT_AVAILABLE',
        'actual_board_result':'NOT_AVAILABLE','native_desktop_this_revision':'NOT_RUN',
        'runtime':{'final_url':'http://127.0.0.1:8771/','owned_exec_session':68855,
                   'test_8773_stopped':True,'kept_running_for_user':True},
        'next':'⑤ real frozen capture/direct721 exporter and preview state; ① accepted job/result service. GUI admits exact new input before any activity.'}
    (evidence/'closeout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':report['status'],'preserved':checked,'phone_preparation_files':len(seal['files']),
                      'old_phase4_reports':len(prior['new_evidence_SHA256'])}))


if __name__=='__main__':main()
