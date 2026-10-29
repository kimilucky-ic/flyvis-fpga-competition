"""Camera609 bindings and reused reference helpers; no neural implementation."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys
import numpy as np

HERE=Path(__file__).resolve().parent
BUNDLE=HERE/'input_bundle'
STATIC=BUNDLE/'static_boundary_gpu_native.npz'
sys.path.insert(0,str(HERE/'dependencies/b_core'))
sys.path.insert(0,str(HERE/'dependencies/a_snapshot'))
from h_step import HUpdater,StepError,file_hash,array_hash,frozen
from run_closed_loop import manifest_verify,validate_parameters,native_full_forbidden,errors
CID='camera_rectB_c5689ab635cc425ea672029502d0d402'
CONDITION='selected_100_190'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def host_path(value):
    text=str(value)
    if os.name=='nt' and text.startswith('/mnt/') and len(text)>7 and text[6]=='/' and text[5].isalpha():
        text=text[5].upper()+':/'+text[7:]
    if os.name!='nt' and len(text)>2 and text[1:3] in (':\\',':/'):
        text='/mnt/'+text[0].lower()+'/'+text[3:].replace('\\','/')
    return Path(text)
def verify_reference(root):
    manifest=load(root/'artifact_manifest.json')
    if isinstance(manifest['files'],dict):
        for name,digest in manifest['files'].items():assert file_hash(root/name)==digest,name
    else:manifest_verify(root)
    return file_hash(root/'artifact_manifest.json')
def seal(root):
    dump(root/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=file_hash(p))
        for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']))
def make_input(frame,ids):
    x=np.zeros(45669,dtype=np.float32);x[ids.reshape(-1)]=np.tile(frame,8);return x
def read_input():
    agreement=load(HERE/'A_ACCEPTED_REFERENCE.json');assert agreement['status']=='PASS_SAME_CAMERA_MODEL_STATE_INPUT_IDENTITY'
    entries=manifest_verify(BUNDLE);model=load(BUNDLE/'identity_manifest.json')
    h=HUpdater(STATIC);inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
    stim=np.load(BUNDLE/'stimulus.npy');initial=np.load(BUNDLE/'initial_state_full.npy').reshape(-1)
    t=np.load(BUNDLE/'time.npy');a=np.load(BUNDLE/'activity_time.npy');n=len(t)
    assert stim.shape==(1,n,1,721) and n==609 and stim.dtype==initial.dtype==np.float32
    assert initial.shape==(45669,) and np.isfinite(initial).all() and np.isfinite(stim).all()
    assert np.array_equal(t,np.arange(n)*.005) and np.array_equal(a,t+.005)
    assert file_hash(BUNDLE/'initial_state_full.npy')==model['initial_state_sha256']==agreement['initial_state_sha256']
    assert agreement['comparison_id']==CID and agreement['expanded_parameters_sha256']==file_hash(BUNDLE/'expanded_parameters.npz')
    return agreement,model,h,inputs,stim,initial,t,a,entries
def require_camera_slot():
    ticket=load(HERE/'CAMERA_GPU_COORDINATION_ACCEPTED.json')
    assert ticket['status']=='CONFIRMED_SHORT_CAMERA_SLOT' and ticket['owner']=='A_GPU'
    assert ticket['comparison_id']==CID and ticket['conflict_free'] is True
    assert file_hash(host_path(ticket['source_path']))==ticket['source_sha256']
    now=datetime.now(timezone.utc)
    start=datetime.fromisoformat(ticket['start']);end=datetime.fromisoformat(ticket['end'])
    assert start.tzinfo is not None and end.tzinfo is not None and start<=now<end
    assert (end-start).total_seconds()<=600 and ticket['Full_completed'] is True
    return ticket
def require_step_time(ticket):
    if datetime.now(timezone.utc)>=datetime.fromisoformat(ticket['end']):
        raise StepError('SLOT_EXPIRED','camera GPU window expired; no new commit')
def configure_gpu():
    os.environ.update(CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR='/tmp/flyvis-camera-hreplacement-20261011-r1',
        MPLBACKEND='Agg',MPLCONFIGDIR=str(HERE/'runtime/matplotlib'),NUMBA_CACHE_DIR=str(HERE/'runtime/numba'),
        CUBLAS_WORKSPACE_CONFIG=':4096:8',TIMEZONE='Asia/Shanghai',PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode=True
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    if not torch.cuda.is_available():raise StepError('NOT_READY','no required CUDA runtime; no fallback')
    probe=2*(torch.arange(4,device='cuda',dtype=torch.float32)+1)
    assert np.array_equal(probe.cpu().numpy(),np.array([2,4,6,8],dtype=np.float32))
    return torch
