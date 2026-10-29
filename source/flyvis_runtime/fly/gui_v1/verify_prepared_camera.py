"""CPU-only original/ prepared input equality on already saved actual frames."""
from pathlib import Path
import json,time
import numpy as np
from live_protocol import HERE,write,sha
import sys
sys.path.insert(0,str(HERE.parent))
from camera_pipeline.adapter import render_bgr_frames
from prepared_camera_input import PreparedCameraInput

def main():
    from PIL import Image
    prepared=PreparedCameraInput();rows=[]
    folder=HERE/'runtime/live/457060aac35041eabe99ee8f39a7a95f/stream/sources'
    files=[folder/f'{k:06d}.png' for k in (0,1,10,50,100,200,400,700)]
    digital=HERE/'runtime/live/b872bc4816bc4004ab9bfef9eead9008/stream/sources/000000.png'
    if digital.exists():files.append(digital)
    for f in files:
        bgr=np.asarray(Image.open(f).convert('RGB'))[:,:,::-1].copy()
        # The first preparation is reported separately, never as steady state.
        prepared.prepare(*bgr.shape[:2])
        start=time.perf_counter();original,coords,meta=render_bgr_frames(bgr[None],spatial_policy='full-field',chunk_frames=1);old_ms=(time.perf_counter()-start)*1000
        start=time.perf_counter();actual,coords2,meta2=prepared.render(bgr);new_ms=(time.perf_counter()-start)*1000
        assert np.array_equal(original,actual) and coords==coords2
        assert {k:v for k,v in meta.items() if k!='preprocessing_elapsed_s'}=={k:v for k,v in meta2.items() if k not in ('preprocessing_elapsed_s','prepared_geometry','preprocessing_backend')}
        rows.append(dict(file=str(f),source_sha256=sha(f),values_sha256=__import__('hashlib').sha256(actual.tobytes()).hexdigest(),original_ms=old_ms,prepared_ms=new_ms,bitwise_equal=True,shape=list(bgr.shape)))
    result=dict(status='PASS_ORIGINAL_OFFICIAL_INPUT_BITWISE_EQUAL',frames=len(rows),rows=rows,
        original_p50_ms=float(np.median([r['original_ms'] for r in rows])),prepared_p50_ms=float(np.median([r['prepared_ms'] for r in rows])),
        camera_started=False,neural_updates=0,CUDA_used=False,original_adapter_sha256=sha(HERE.parent/'camera_pipeline/adapter.py'))
    write(HERE/'evidence/latency_headroom_20261015/input_equality.json',result);print(json.dumps({k:result[k] for k in ('status','frames','original_p50_ms','prepared_p50_ms')}))

if __name__=='__main__':main()
