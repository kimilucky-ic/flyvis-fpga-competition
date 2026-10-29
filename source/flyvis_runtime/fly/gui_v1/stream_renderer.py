"""Original official BoxEye in an isolated CPU conversion process; GPU core stays CUDA."""
import time
PROCESS_BEGIN=time.perf_counter()
import argparse
import base64
import hashlib
import io
import sys
import numpy as np
from live_protocol import HERE,host_path,load
from stream_transport import RPC
from input_preparation import wait_for_stream_endpoint,preparation_stopped

def run(root):
    root=host_path(root);session=load(root/'session.json');client=None
    sys.path.insert(0,str(HERE.parent))
    imports=time.perf_counter()
    from prepared_camera_input import PreparedCameraInput
    from PIL import Image
    imports_s=time.perf_counter()-imports;construct=time.perf_counter();converter=PreparedCameraInput()
    construct_s=time.perf_counter()-construct
    # Initialize the unmodified official conversion before allowing acquisition.
    # Warm-up pixels are never sent as input, saved as camera evidence or inferred.
    warm=time.perf_counter()
    converter.render(np.full((480,640,3),127,dtype=np.uint8))
    from live_protocol import write
    write(root/'converter_warmup.json',dict(schema='flyvis-input-converter-startup/v1',session_id=session['session_id'],
        elapsed_s=time.perf_counter()-warm,process_elapsed_s=time.perf_counter()-PROCESS_BEGIN,
        helper_import_s=imports_s,official_converter_construct_s=construct_s,
        published_source_frames=0,neural_updates=0,clock='WSL_process_perf_counter_intervals',
        semantics='Process entry to prepared official CPU converter; excludes interpreter launch before script entry'))
    try:
        endpoint=wait_for_stream_endpoint(root,session);client=RPC(endpoint,'renderer');client.call('ready')
        while not preparation_stopped(root):
            body=client.call('raw',{'wait_ms':100})
            if body is None:time.sleep(.002);continue
            t=time.perf_counter();bgr=np.asarray(Image.open(io.BytesIO(base64.b64decode(body['png']))).convert('RGB'))[:,:,::-1].copy()
            values,coordinates,transform=converter.render(bgr)
            body.update(values=values[0].tolist(),transform=transform)
            body['source'].update(hex_values_sha256=hashlib.sha256(values[0].tobytes()).hexdigest(),converter_elapsed_s=time.perf_counter()-t)
            client.call('converted',body)
    except (OSError,ValueError,ConnectionError):
        if not preparation_stopped(root):raise
    finally:
        if client:client.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);run(p.parse_args().root)
