"""Original official BoxEye in an isolated CPU conversion process; GPU core stays CUDA."""
import argparse
import base64
import hashlib
import io
import sys
import time
import numpy as np
from live_protocol import HERE,host_path,load
from stream_transport import RPC

def run(root):
    root=host_path(root);client=RPC(load(root/'stream_endpoint.json'),'renderer')
    sys.path.insert(0,str(HERE.parent))
    from camera_pipeline.adapter import official_components,render_bgr_frames
    from PIL import Image
    official_components()
    # Initialize the unmodified official conversion before allowing acquisition.
    # Warm-up pixels are never sent as input, saved as camera evidence or inferred.
    warm=time.perf_counter()
    render_bgr_frames(np.full((1,480,640,3),127,dtype=np.uint8),spatial_policy='full-field',chunk_frames=1)
    from live_protocol import write
    write(root/'converter_warmup.json',dict(elapsed_s=time.perf_counter()-warm,published_source_frames=0,neural_updates=0))
    client.call('ready')
    try:
        while not (root/'stream/STOP_REQUEST.json').exists():
            body=client.call('raw')
            if body is None:time.sleep(.002);continue
            t=time.perf_counter();bgr=np.asarray(Image.open(io.BytesIO(base64.b64decode(body['png']))).convert('RGB'))[:,:,::-1].copy()
            values,coordinates,transform=render_bgr_frames(bgr[None],spatial_policy='full-field',chunk_frames=1)
            body.update(values=values[0].tolist(),transform=transform)
            body['source'].update(hex_values_sha256=hashlib.sha256(values[0].tobytes()).hexdigest(),converter_elapsed_s=time.perf_counter()-t)
            client.call('converted',body)
    finally:client.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);run(p.parse_args().root)
