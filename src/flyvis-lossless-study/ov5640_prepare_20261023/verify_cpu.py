"""Bounded x86 CPU comparison. Never opens a camera or board."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['PYTHON_DOTENV_DISABLED']='1'
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
from PIL import Image
from ps_input import PsInput, receptor_centers, rgb565_to_rgb, rgb_luminance
HERE=Path(__file__).resolve().parent
FLY=HERE.parents[2]/'fly'
# Source tree is a sibling of fpga, without changing any shared source.
FLY=Path('C:/Users/hzy72/Documents/ChatGPT/fly')
sys.path.insert(0,str(FLY))
from camera_pipeline.adapter import render_bgr_frames, official_components

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    start=time.perf_counter()
    rng=np.random.default_rng(20261023)
    sample=rng.integers(0,256,(256,256,3),dtype=np.uint8)
    assert np.array_equal(rgb_luminance(sample),np.asarray(Image.fromarray(sample).convert('L')))
    words=np.array([[0,0xf800,0x07e0,0x001f,0xffff]],dtype=np.uint16)
    assert rgb565_to_rgb(words).tolist()==[[[0,0,0],[248,0,0],[0,252,0],[0,0,248],[248,252,248]]]
    torch,flyvis,BoxEye,*_=official_components()
    eye=BoxEye(extent=15,kernel_size=13)
    assert np.array_equal(receptor_centers(),eye.receptor_centers.cpu().numpy()+208)
    result=dict(evidence='X86_CPU_PORTABLE_PS_MAPPING_COMPARISON_ONLY',board_result=False,
                hardware_actions=0,vivado_runs=0,model_modified=False,torch_device=str(flyvis.device),
                python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,cases=[],
                tolerance_absolute=3e-6,bitwise_equivalence_required=False,
                grayscale_pixels_exact=65536,receptor_centers_exact=721,negative_tests=0)
    for h,w in [(480,640),(600,800)]:
        y,x=np.indices((h,w))
        frames=[np.zeros((h,w,3),np.uint8), np.full((h,w,3),255,np.uint8),
                np.broadcast_to(np.array([255,0,0],np.uint8),(h,w,3)).copy(),
                np.stack(((x*255//(w-1)).astype(np.uint8),(y*255//(h-1)).astype(np.uint8),((x+y)%256).astype(np.uint8)),axis=-1),
                np.repeat((((x//7+y//7)%2)*255).astype(np.uint8)[...,None],3,axis=2),
                rng.integers(0,256,(h,w,3),dtype=np.uint8)]
        labels=['black','white','red','xy_gradient','checkerboard','seeded_random']
        reference=render_bgr_frames(np.stack(frames)[...,::-1].copy(),spatial_policy='full-field',chunk_frames=1)[0]
        mapper=PsInput(h,w,'RGB')
        for label,frame,ref in zip(labels,frames,reference):
            t=time.perf_counter();actual=mapper.render(frame);elapsed=time.perf_counter()-t
            err=np.abs(actual-ref)
            case=dict(hw=[h,w],pattern=label,max_abs_error=float(err.max()),mean_abs_error=float(err.mean()),
                      differing_fp32_words=int(np.count_nonzero(actual.view(np.uint32)!=ref.view(np.uint32))),
                      portable_x86_seconds=elapsed,output_sha256=hashlib.sha256(actual.tobytes()).hexdigest())
            result['cases'].append(case)
            np.save(HERE/(str(h)+'_'+label+'_actual.npy'),actual,allow_pickle=False)
            np.save(HERE/(str(h)+'_'+label+'_official.npy'),ref,allow_pickle=False)
            if err.max()>result['tolerance_absolute']:
                raise AssertionError(case)
        for order in ('BGR','GBR'):
            permutation=['RGB'.index(c) for c in order]
            assert np.array_equal(PsInput(h,w,order).render(frames[3][...,permutation]),mapper.render(frames[3]))
        for bad in (np.zeros((h,w,3),np.float32),np.zeros((h,w),np.uint8),np.zeros((h+1,w,3),np.uint8)):
            try: mapper.render(bad)
            except ValueError: result['negative_tests']+=1
            else: raise AssertionError('bad frame accepted')
    for args in ((0,640,'RGB'),(480,640,'AUTO'),(2049,640,'RGB')):
        try: PsInput(*args)
        except ValueError: result['negative_tests']+=1
        else: raise AssertionError('bad configuration accepted')
    result['sources']={str(p):digest(p) for p in (HERE/'ps_input.py',Path(__file__),FLY/'camera_pipeline/adapter.py',FLY/'upstream/flyvis/flyvis/datasets/rendering/eye.py')}
    result['elapsed_seconds']=time.perf_counter()-start
    result['status']='PASS_CPU_GEOMETRY_AND_TOLERANCE_ONLY'
    (HERE/'CPU_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],cases=len(result['cases']),max_abs_error=max(c['max_abs_error'] for c in result['cases']),negative_tests=result['negative_tests'],elapsed_seconds=result['elapsed_seconds'])))
if __name__=='__main__': main()
