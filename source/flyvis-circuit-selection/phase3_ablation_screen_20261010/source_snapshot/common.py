from pathlib import Path
import json,os,sys,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent
BUNDLE=HERE/'input_bundle_r2'
sys.path.insert(0,str(HERE/'dependencies/b_core'))
sys.path.insert(0,str(HERE/'dependencies/a_snapshot'))
from h_step import HUpdater,StepError,array_hash,file_hash,frozen
from run_closed_loop import manifest_verify,validate_parameters,native_full_forbidden,errors

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def host_path(value):
    value=str(value)
    if os.name!='nt' and len(value)>2 and value[1:3] in (':\\',':/'):value='/mnt/'+value[0].lower()+'/'+value[3:].replace('\\','/')
    return Path(value)
def seal(path):dump(path/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(path).as_posix(),bytes=p.stat().st_size,sha256=file_hash(p)) for p in sorted(path.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def configure_gpu():
    os.environ.update(CUDA_VISIBLE_DEVICES='0',FLYVIS_ROOT_DIR='/tmp/flyvis-ablation-screen-20261010',MPLBACKEND='Agg',
        MPLCONFIGDIR=str(HERE/'runtime/matplotlib'),NUMBA_CACHE_DIR=str(HERE/'runtime/numba'),CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
    sys.dont_write_bytecode=True
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    if not torch.cuda.is_available():raise StepError('NOT_READY','CUDA required; no silent CPU switch')
    return torch
def input_full(frame,inputs):
    x=np.zeros(45669,dtype=np.float32);x[inputs.reshape(-1)]=np.tile(frame,8);return x
