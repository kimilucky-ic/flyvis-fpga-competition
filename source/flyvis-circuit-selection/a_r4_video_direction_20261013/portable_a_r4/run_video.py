"""Independent a_r4 MP4-to-direction CPU CLI. No labels or Full network access."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
import json
import time
from pathlib import Path
import numpy as np
from independent_model import IndependentModel
from video_io import decode_video,sha
from direction_readout import features,predict


def main():
    p=argparse.ArgumentParser()
    for name in ['video','model','sampler','readout','roi','types','output']:p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError('new output directory required')
    start=time.perf_counter();model=IndependentModel(args.model)
    with np.load(args.sampler) as d:sampler={k:d[k] for k in d.files}
    frames,metadata=decode_video(args.video,sampler)
    if frames.shape!=(400,model.n_pixels):raise ValueError('input/model mismatch')
    ids=np.load(args.roi);types=np.load(args.types)
    if ids.shape!=(56,) or types.shape!=(56,) or np.any(ids<0) or np.any(ids>=model.n):raise ValueError('local ROI')
    readout=json.loads(args.readout.read_text(encoding='utf-8'))
    args.output.mkdir(parents=True);np.save(args.output/'input.npy',frames)
    state=model.p['bias'].copy()
    for k in range(200):state=model.step(state,np.full(model.n_pixels,.5,np.float32))
    np.save(args.output/'initial_state.npy',state)
    states=np.lib.format.open_memmap(args.output/'states.npy',mode='w+',dtype=np.float32,shape=(400,model.n))
    for k,frame in enumerate(frames):
        if time.perf_counter()-start>180:raise TimeoutError('180s CPU bound')
        state=model.step(state,frame)
        if float(abs(state).max())>100:raise FloatingPointError('state magnitude bound')
        states[k]=state
    states.flush();f=features(states[:,ids],types);pred=predict(f,readout)
    result=dict(execution='ACTUAL_INDEPENDENT_CPU_VIDEO',prediction=pred,features=f.tolist(),
        time_s=time.perf_counter()-start,model_sha=sha(args.model),readout_sha=sha(args.readout),
        input_metadata=metadata,neural_steps=600,external_neural_states=0,full_network_calls=0,GPU=False,
        limitations='first two seconds only; fixed baseline .3-.5s and readout .5-2s; controlled single-edge scope')
    (args.output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
