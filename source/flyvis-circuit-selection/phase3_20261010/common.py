"""Identity/paths for the one frozen animation; no new neuron implementation."""
from pathlib import Path
import json, os, sys
import numpy as np

HERE=Path(__file__).resolve().parent
BUNDLE=HERE/'input_bundle'
STATIC=BUNDLE/'static_boundary_gpu_native.npz'
sys.path.insert(0,str(HERE/'dependencies/b_core'))
sys.path.insert(0,str(HERE/'dependencies/a_snapshot'))
from h_step import HUpdater, StepError, file_hash, array_hash, frozen
from run_closed_loop import manifest_verify, validate_parameters, native_full_forbidden, errors


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def host_path(value):
    """Evidence stores canonical Windows paths; WSL reads the same mount bytes."""
    value=str(value)
    if os.name!='nt' and len(value)>2 and value[1:3] in (':\\',':/'):
        value='/mnt/'+value[0].lower()+'/'+value[3:].replace('\\','/')
    return Path(value)


def configure_gpu():
    os.environ.update(CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR='/tmp/flyvis-circuit-selection-phase3-20261010',
        MPLBACKEND='Agg',MPLCONFIGDIR=str(HERE/'runtime/matplotlib'),NUMBA_CACHE_DIR=str(HERE/'runtime/numba'),
        TIMEZONE='Asia/Shanghai',CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode=True
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    if not torch.cuda.is_available():raise StepError('NOT_READY','required CUDA runtime unavailable; no CPU fallback')
    return torch


def read_input():
    entries=manifest_verify(BUNDLE)
    meta=load(BUNDLE/'video_manifest.json');model=load(BUNDLE/'identity_manifest.json')
    h=HUpdater(STATIC)
    inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
    stimulus=np.load(BUNDLE/'stimulus.npy',allow_pickle=False)
    initial=np.load(BUNDLE/'initial_state_full.npy',allow_pickle=False).reshape(-1)
    time=np.load(BUNDLE/'time.npy',allow_pickle=False)
    activity_time=np.load(BUNDLE/'activity_time.npy',allow_pickle=False)
    assert stimulus.shape==(1,800,1,721) and stimulus.dtype==np.float32 and stimulus.flags.c_contiguous
    assert np.isfinite(stimulus).all() and ((stimulus>=0)&(stimulus<=1)).all()
    assert initial.shape==(45669,) and initial.dtype==np.float32 and np.isfinite(initial).all()
    assert np.array_equal(time,np.arange(800)*.005) and np.array_equal(activity_time,time+.005)
    assert file_hash(BUNDLE/'initial_state_full.npy')==model['initial_state_sha256']
    return meta,model,h,inputs,stimulus,initial,time,activity_time,entries


def parameters_paths():
    return (BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',BUNDLE/'candidates/B_T5c/candidate_manifest.json')


def make_input(frame,input_ids):
    x=np.zeros(45669,dtype=np.float32)
    x[input_ids.reshape(-1)]=np.tile(frame,8)
    return x


def unchanged(entries):
    return all(file_hash(BUNDLE/entry['path'])==entry['sha256'] for entry in entries)


def seal(directory):
    dump(directory/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(directory).as_posix(),
        bytes=p.stat().st_size,sha256=file_hash(p)) for p in sorted(directory.rglob('*'))
        if p.is_file() and p.name!='artifact_manifest.json']))
