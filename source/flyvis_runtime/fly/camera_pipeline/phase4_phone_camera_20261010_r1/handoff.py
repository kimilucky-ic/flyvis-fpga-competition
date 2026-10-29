"""Read-only input/status API. No neural result is invented or loaded from other runs."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import sha256

def load_input(folder):
    folder=Path(folder).resolve();manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if manifest['schema']!='phase4-frozen-input-seal-v1':raise ValueError('Unknown seal')
    for name,digest in manifest['files'].items():
        path=(folder/name).resolve()
        if not path.is_relative_to(folder) or sha256(path)!=digest:raise ValueError('Input identity mismatch: '+name)
    identity=json.loads((folder/'INPUT_IDENTITY.json').read_text(encoding='utf-8'))
    if identity['schema']!='flyvis-real-screen-input-v1' or identity['source_kind']!='real_camera_recapture_of_phone':
        raise ValueError('Wrong source type')
    x=np.load(folder/'stimulus.npy',mmap_mode='r',allow_pickle=False)
    t=np.load(folder/'time.npy',allow_pickle=False);activity=np.load(folder/'activity_time.npy',allow_pickle=False)
    if x.dtype!=np.float32 or x.shape!=(1,len(t),1,721) or not np.isfinite(x).all() or x.min()<0 or x.max()>1:
        raise ValueError('Invalid frozen receptors')
    if not np.array_equal(activity,t+.005) or not np.allclose(np.diff(t),.005,rtol=0,atol=1e-12):raise ValueError('Time alignment mismatch')
    x.flags.writeable=False
    return identity,x,t,activity

def read_step(folder,index):
    identity,x,t,activity=load_input(folder)
    if not 0<=index<len(t):raise IndexError(index)
    import csv
    with (Path(folder)/'three_clock_alignment.csv').open(encoding='utf-8',newline='') as stream: rows=list(csv.DictReader(stream))
    return {'comparison_id':identity['comparison_id'],'input_id':identity['input_id'],'model_step':index,
            'source_frame':int(rows[index]['source_frame']),'source_received_utc':rows[index]['source_received_utc'],
            'source_received_monotonic_ns':int(rows[index]['source_received_monotonic_ns']),
            'input_time_s':float(t[index]),'activity_after_update_time_s':float(activity[index]),
            'hex_intensity':np.asarray(x[0,index,0]).tolist(),'activity':None,'neural_status':'not_run',
            'board_status':'not_run','mode_availability':identity['modes']}

def read_source_frame(folder,index):
    identity,_,_,_=load_input(folder)
    name=f'frame_{index:06d}.png';digest=identity['raw_png_hashes'].get(name)
    if digest is None:raise IndexError(index)
    path=Path(identity['recording_path'])/'raw_frames'/name
    if sha256(path)!=digest:raise ValueError('Displayed source frame identity changed')
    from camera_pipeline.common import cv2_module
    image=cv2_module().imread(str(path))
    if image is None:raise ValueError('Source frame decode failed')
    return image

def check_backend_identity(input_folder,result_manifest):
    """Contract check, not an attestation that a board computation occurred."""
    identity,x,t,activity=load_input(input_folder)
    result_path=Path(result_manifest).resolve();result=json.loads(result_path.read_text(encoding='utf-8'))
    if result.get('schema')!='flyvis-phase4-backend-result-v1':raise ValueError('Unknown result schema')
    if result.get('status')!='complete' or result.get('mode') not in ('full_gpu','python_replacement','fpga_replacement'):
        raise ValueError('Incomplete or unknown backend result')
    for key in ('comparison_id','input_id'):
        if result.get(key)!=identity[key]:raise ValueError('Backend '+key+' mismatch; reject cached result from another experiment')
    input_folder=Path(input_folder)
    for key,name in [('stimulus_npy_sha256','stimulus.npy'),('input_time_npy_sha256','time.npy'),('activity_time_npy_sha256','activity_time.npy')]:
        if result.get(key)!=sha256(input_folder/name):raise ValueError('Backend clock/input hash mismatch: '+key)
    if result.get('source_commit')!=identity['source_commit'] or result.get('model_checkpoint_sha256')!='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f':
        raise ValueError('Original model identity mismatch')
    for key in ('a0_npy_sha256','expanded_parameters_sha256','node_map_sha256','numerical_profile_id'):
        if not isinstance(result.get(key),str) or not result[key]:raise ValueError('Missing backend shared identity: '+key)
    evidence=result.get('execution_evidence',{})
    required=('log_path','log_sha256','started_utc','finished_utc','runtime_device','compute_mode')
    if any(not evidence.get(key) for key in required):raise ValueError('Missing actual execution evidence')
    log=Path(evidence['log_path'])
    if not log.is_absolute():log=result_path.parent/log
    if sha256(log)!=evidence['log_sha256']:raise ValueError('Execution log hash mismatch')
    if evidence['compute_mode'] not in ('offline','buffered','real_time_measured'):raise ValueError('Unknown timing claim')
    if result['mode']=='fpga_replacement' and evidence.get('evidence_level')!='live_board_execution':
        raise ValueError('FPGA mode requires live board evidence; RTL/offline replay is not accepted')
    for name,digest in result.get('files_sha256',{}).items():
        path=Path(name);path=path if path.is_absolute() else result_path.parent/path
        if sha256(path)!=digest:raise ValueError('Backend file identity mismatch: '+name)
    for key in ('central_activity_file','central_node_ids_file','final_full_state_file'):
        if result.get(key) not in result.get('files_sha256',{}):raise ValueError('Missing hashed result '+key)
    activity_path=Path(result['central_activity_file']);activity_path=activity_path if activity_path.is_absolute() else result_path.parent/activity_path
    values=np.load(activity_path,mmap_mode='r',allow_pickle=False)
    ids_path=Path(result['central_node_ids_file']);ids_path=ids_path if ids_path.is_absolute() else result_path.parent/ids_path
    ids=np.load(ids_path,allow_pickle=False)
    if ids.ndim!=1 or len(ids)==0 or not np.issubdtype(ids.dtype,np.integer) or len(np.unique(ids))!=len(ids) or (ids<0).any() or (ids>=45669).any():
        raise ValueError('Central IDs must be unique original full-network node IDs')
    if values.shape!=(len(t),len(ids)) or not np.isfinite(values).all():raise ValueError('Backend activity step/node alignment invalid')
    final_path=Path(result['final_full_state_file']);final_path=final_path if final_path.is_absolute() else result_path.parent/final_path
    final=np.load(final_path,allow_pickle=False)
    if final.shape not in ((45669,),(1,45669)) or not np.isfinite(final).all():raise ValueError('Missing complete final network state')
    return {'contract_identity_pass':True,'comparison_id':identity['comparison_id'],'mode':result['mode'],
            'steps':len(t),'actual_execution_independently_verified':False,
            'numerical_comparison_acceptance_owned_by_AB':True,'result_manifest_sha256':sha256(result_path)}
