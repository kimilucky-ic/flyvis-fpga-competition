"""Portable candidate-only CPU run; requires only model.npz and local input.npy.

No original FlyVis installation, full graph, full a0, decoder or recorded states.
Use a new output directory. All initialization and movie states are computed.
"""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import hashlib
import json
import time
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from independent_model import IndependentModel


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('new output directory required')
    model=IndependentModel(args.model)
    frames=np.load(args.input,allow_pickle=False)
    if frames.dtype!=np.float32 or frames.ndim!=2 or frames.shape[1]!=model.n_pixels:
        raise ValueError('local frozen retina input required')
    if not np.isfinite(frames).all() or np.any((frames<0)|(frames>1)):
        raise ValueError('input domain')
    args.output.mkdir(parents=True)
    state=model.p['bias'].copy();start=time.perf_counter()
    gray=np.full(model.n_pixels,.5,np.float32)
    for k in range(200):state=model.step(state,gray)
    np.save(args.output/'initial_state.npy',state)
    states=np.lib.format.open_memmap(args.output/'states.npy',mode='w+',dtype=np.float32,shape=(len(frames),model.n))
    for k,frame in enumerate(frames):
        if time.perf_counter()-start>180:raise TimeoutError('CPU bound')
        candidate=model.step(state,frame)
        if float(abs(candidate).max())>100:raise FloatingPointError('stability bound')
        state=candidate;states[k]=state
    states.flush();np.save(args.output/'final_state.npy',state)
    time_axis=np.arange(len(frames),dtype=np.float64)*.005-1
    np.save(args.output/'input_time.npy',time_axis)
    np.save(args.output/'activity_time.npy',time_axis+.005)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(status='PASS_PORTABLE_CANDIDATE_ONLY_CPU',nodes=model.n,edges=len(model.p['weight']),
        input_pixels=model.n_pixels,warmup_steps=200,movie_steps=len(frames),wall_s=time.perf_counter()-start,
        full_network_calls=0,external_neural_state_reads=0,GPU_execution=False,
        model_sha256=digest(args.model),input_sha256=digest(args.input),
        states_sha256=digest(args.output/'states.npy'),initial_state_sha256=digest(args.output/'initial_state.npy'))
    (args.output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
