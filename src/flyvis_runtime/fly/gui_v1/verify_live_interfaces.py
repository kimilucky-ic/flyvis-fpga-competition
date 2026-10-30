"""Lightweight CPU/AST preflight; no port binding, model import, or neural updates."""
import ast
import importlib.util
import sys
from pathlib import Path
from live_protocol import HERE,Registry,load,require,sha,utc,write


def verify():
    registry=Registry();signatures={}
    for key,names in {'full':['FullNetworkOracle','step'],'r_only':['RStepService','step'],'decoder':['OfficialDecoderService','decode'],
        'intervention':['InterventionAdapter','step'],'sparse':['SparseRetainAdapter','step'],'runner_lease':['Lease','acquire'],
        'coordinator':['Coordinator','prepare','commit'],'h_step':['HUpdater','step']}.items():
        tree=ast.parse(registry.path_for(key).read_text(encoding='utf-8-sig'))
        found={node.name:ast.unparse(node.args) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) else 'class'
            for node in ast.walk(tree) if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names}
        require(set(found)==set(names),'PUBLIC_INTERFACE_MISSING '+key);signatures[key]=found
    # Original reader hashes recorded frame/input assets and validates causal ZOH. Never opens a device.
    spec=importlib.util.spec_from_file_location('gui_frozen_camera_reader',registry.path_for('camera_reader'))
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    identity,x,t,a=reader.load_frozen_input(registry.data['camera']['folder'])
    require(x.shape==(1,609,1,721) and not x.flags.writeable,'CAMERA_READONLY_SCHEMA')
    require('torch' not in sys.modules and 'flyvis' not in sys.modules and 'cv2' not in sys.modules,'FORBIDDEN_RUNTIME_IMPORT')
    # Preserve small original code / receipts, reusing prior hashes. Do not re-audit 1917 bulk files.
    evidence=HERE/'evidence';old=load(evidence/'phase4/closeout.json');preserved={}
    allowed={str(HERE/'server.py'),str(HERE.parent/'viewer/index.html')}
    for path,digest in old['protected_files'].items():
        target=Path(path)
        if str(target) in allowed:continue
        if target.stat().st_size>8*1024*1024:continue
        require(sha(target)==digest,'OLD_PROTECTED_CHANGED '+path);preserved[path]=digest
    sparse=load(evidence/'scientific_sparse_20261012/closeout.json')
    for path,digest in sparse['owned_files_SHA256'].items():
        if path in allowed:continue
        require(sha(path)==digest,'OLD_SPARSE_CHANGED '+path);preserved[path]=digest
    receipts={}
    for name in ('scientific_sparse_20261012','scientific_pilot_20261011','phase4_unified_20261011'):
        prior=load(evidence/name/'closeout.json')
        for file,digest in prior['evidence_SHA256'].items():
            require(sha(evidence/name/file)==digest,'OLD_ACCEPTANCE_CHANGED '+file);receipts[name+'/'+file]=digest
    old38=load(evidence/'phase4_unified_20261011/offline38_regression.json')
    old11=load(evidence/'phase4_unified_20261011/camera_bar11_regression.json')
    old6=load(evidence/'phase4_unified_20261011/controlled6_regression.json')
    require(all(r['status']=='PASS' for r in (old38,old11,old6)),'OLD55_RECEIPTS')
    report={'status':'PASS_CPU_STATIC_INTERFACE_PREFLIGHT','utc':utc(),'source_pins_verified':len(registry.pins),'public_interfaces':signatures,
        'camera_read_api':{'comparison_id':identity['comparison_id'],'shape':list(x.shape),'read_only':True,'input_time_range_s':[float(t[0]),float(t[-1])],
            'activity_time_range_s':[float(a[0]),float(a[-1])],'source_kind':'recorded_camera_frozen','new_job_binding':'NOT_AVAILABLE'},
        'preserved_small_code_SHA256':preserved,'preserved_acceptance_SHA256':receipts,'old55_previous_receipts':'PASS_PRESERVED_NOT_RERUN',
        'new_GPU_runs':0,'new_neural_steps':0,'new_decoder_calls':0,'camera_operations':0,'board_operations':0,'GUI_service_started':False,
        'LIVE_INTERACTIVE_GUI_PASS':'NOT_RUN','REALTIME_STREAM_PASS':'NOT_RUN'}
    write(evidence/'live_interface_20261012/static_preflight.json',report)
    return report


if __name__=='__main__':
    report=verify();print({k:report[k] for k in ('status','source_pins_verified','old55_previous_receipts','new_GPU_runs','GUI_service_started')})
