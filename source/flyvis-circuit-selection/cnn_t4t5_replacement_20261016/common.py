"""CPU-only paths, immutable identities and exact retained R service binding."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import csv
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
torch.use_deterministic_algorithms(True)
HERE=Path(__file__).resolve().parent
LANE=HERE.parent
ROOT=LANE.parent
FLY=ROOT.parent/'fly'
BUNDLE=LANE/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
SUPPORT=ROOT/'flyvis-gpu-validation/t4t5_decoder_support_20261011'
UPSTREAM=FLY/'upstream/flyvis/flyvis'
CHECKPOINT=FLY/'data_cpu/results/flow/0000/000/chkpts/chkpt_00000'
TYPES=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
TRAIN=['ON60','ON240','OFF90','OFF270']
sys.path.insert(0,str(FLY/'gpu_phase2'))
from r_only import RStepService,array_sha

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def dump(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()

def digest(a):
    if isinstance(a,torch.Tensor):a=a.detach().cpu().numpy()
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def source():
    with (BUNDLE/'nodes_full.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    types=np.array([r['cell_type'] for r in rows])
    u=np.array([int(r['u']) for r in rows]);v=np.array([int(r['v']) for r in rows])
    p=dict(np.load(BUNDLE/'expanded_parameters.npz'))
    return types,u,v,p

def read_mapping():return dict(np.load(HERE/'mapping.npz'))

def r_service():return RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',HERE/'R_CANDIDATE.json',device='cpu')

def check_frozen():
    p=load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json')==load(HERE/'FREEZE.json')['sha256']
    for path,value in p['pins'].items():assert sha(path)==value,path
    return p
