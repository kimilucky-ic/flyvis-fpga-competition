"""Seal only this GUI consumer; preserve previous sources, code and acceptance."""
import argparse
from datetime import datetime,timezone
import json

from data_store import ROOT,read_json,sha256


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--session',type=int,required=True);args=parser.parse_args()
    folder=ROOT/'gui_v1/evidence/scientific_sparse_20261012'
    allowed={str(ROOT/p) for p in ('gui_v1/server.py','viewer/index.html','gui_v1/README.md','gui_v1/API_CONTRACT.md')}
    old=read_json(ROOT/'gui_v1/evidence/phase4/closeout.json');retained={}
    for group in ('source_files','protected_files'):
        for path,digest in old[group].items():assert sha256(path)==digest,(group,path)
        retained[group]=len(old[group])
    prior=[]
    for previous_name in ('phase4_unified_20261011','scientific_pilot_20261011'):
        previous=read_json(ROOT/f'gui_v1/evidence/{previous_name}/closeout.json')
        for path,digest in previous['owned_files_SHA256'].items():
            if path not in allowed:assert sha256(path)==digest,path
        for name,digest in previous['evidence_SHA256'].items():assert sha256(ROOT/f'gui_v1/evidence/{previous_name}'/name)==digest,name
        prior.append({'directory':previous_name,'preserved_evidence_files':len(previous['evidence_SHA256'])})
    for path,digest in old['new_evidence_SHA256'].items():assert sha256(path)==digest,path
    assert sha256(ROOT/'deliverables/FlyVis_3D_Handoff_v1_20261010.zip')==old['packaging_archive_SHA256']
    software=read_json(folder/'software_acceptance.json');browser=read_json(folder/'browser_acceptance.json');runtime=read_json(folder/'runtime_acceptance.json')
    assert software['status']=='PASS_READ_ONLY_SCIENTIFIC_SPARSE' and browser['status']=='PASS_LIMITED_REAL_BROWSER_SPARSE' and runtime['status']=='PASS_ORIGINAL_8771_ENTRY'
    for path,digest in software['sources_SHA256'].items():assert sha256(path)==digest,path
    names=['gui_v1/scientific_sparse.py','gui_v1/scientific_sparse.json','gui_v1/SCIENTIFIC_SPARSE_CONTRACT.md',
        'viewer/scientific_sparse.js','viewer/scientific_sparse.css','gui_v1/verify_scientific_sparse.py',
        'gui_v1/verify_sparse_browser.py','gui_v1/closeout_scientific_sparse.py',
        'gui_v1/server.py','viewer/index.html','gui_v1/README.md','gui_v1/API_CONTRACT.md']
    report={'status':'PASS_GUI_SCIENTIFIC_SPARSE_REPLAY_ONLY','utc':datetime.now(timezone.utc).isoformat(),
        'run_id':software['run_id'],'manifest_sha256':software['manifest_sha256'],'evidence_level':'SOFTWARE_SPARSE_RETAIN','display_kind':'OFFLINE_REPLAY',
        'preserved_old_files':retained,'preserved_previous_evidence':prior,'old55_source_acceptance_and_code_unchanged':True,
        'old_pilot_python_js_css_config_and_evidence_unchanged':True,'sealed_B_files_verified':software['sealed_files_verified'],
        'B_flow_values_bitwise':software['B_flow_values'],'primary_metric_values':software['primary_metric_values'],
        'independent_metric_max_error':software['metric_recomputation_max_error'],'browser_observations':len(browser['observations_verified']),
        'negative_checks':len(software['negative_checks']),
        'owned_files_SHA256':{str(ROOT/name):sha256(ROOT/name) for name in names},
        'evidence_SHA256':{p.name:sha256(p) for p in folder.iterdir() if p.is_file() and p.name!='closeout.json'},
        'new_GPU_runs':0,'new_decoder_calls':0,'new_training':False,'camera_operations':0,'board_operations':0,'PL_execution':False,'FPGA_status':'NOT_CONNECTED',
        'native_desktop_this_revision':'NOT_RUN','3D_packaging':'FROZEN_BY_USER',
        'runtime':{'url':'http://127.0.0.1:8771/','owned_exec_session':args.session,'test_8773_stopped':True},
        'stop_boundary':'Read-only B consumer, bounded software/HTTP/browser acceptance complete; no new experiment.',
        'next':'⑥actual board/bit/hwh/numeric/input/model/initial state/global IDs/candidate/check/COMMIT/raw activity/flow/cycles/latency/manifest; ①same-comparison software reference and result ABI; ④metrics/ROI/windows. Separate admission, no floating-B to physical-PL promotion.'}
    (folder/'closeout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('status','preserved_old_files','B_flow_values_bitwise','browser_observations','negative_checks')}))


if __name__=='__main__':main()
