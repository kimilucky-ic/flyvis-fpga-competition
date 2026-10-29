"""Portable target CPU check: no PYNQ, Torch, camera, MMIO or GPU.

Run on ARM later with: python3 verify_target.py result_arm.json
This script itself does not authorize any board connection or hardware action.
"""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
from ps_input import PsInput
HERE=Path(__file__).resolve().parent

def main():
    if len(sys.argv)!=2: raise SystemExit('provide a NEW result JSON path')
    output=Path(sys.argv[1])
    if output.exists(): raise SystemExit('refusing to overwrite result')
    mapper=PsInput(480,640,'RGB')
    y,x=np.indices((480,640))
    frame=np.stack(((x*255//639).astype(np.uint8),(y*255//479).astype(np.uint8),((x+y)%256).astype(np.uint8)),axis=-1)
    reference=np.load(HERE/'480_xy_gradient_official.npy',allow_pickle=False)
    timings=[]
    for i in range(4):
        start=time.perf_counter(); actual=mapper.render(frame); duration=time.perf_counter()-start
        if i: timings.append(duration)
        if np.max(np.abs(actual-reference))>3e-6: raise RuntimeError('mapping tolerance failed')
    result=dict(status='PASS_PORTABLE_CPU_MAPPING_ONLY',machine=platform.machine(),
                platform=platform.platform(),python=platform.python_version(),numpy=np.__version__,
                arm_execution=platform.machine().lower() in ('armv7l','aarch64','arm64'),
                board_capture_tested=False,neural_steps=0,hardware_actions=0,
                times_seconds=timings,max_abs_error=float(np.max(np.abs(actual-reference))),
                actual_sha256=hashlib.sha256(actual.tobytes()).hexdigest(),
                source_sha256=hashlib.sha256((HERE/'ps_input.py').read_bytes()).hexdigest())
    with output.open('x',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps(result))
if __name__=='__main__': main()
