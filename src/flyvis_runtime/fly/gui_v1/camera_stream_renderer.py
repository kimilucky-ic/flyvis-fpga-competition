"""WSL CPU-only bridge: call unchanged official standard-A renderer; no USB/GPU."""
import argparse
import hashlib
import io
import sys
import time
from pathlib import Path
import numpy as np
from live_protocol import HERE,host_path,load,require,sha,utc,write
from camera_stream_protocol import HEX_CAPACITY,dependencies


def run(root):
    root=host_path(root);control=load(root/'control.json');dependencies()
    sys.path.insert(0,str(HERE.parent))
    from camera_pipeline.adapter import official_components,render_bgr_frames
    official_components() # CPU imports only; no synthetic image/warmup or neural model.
    write(root/'renderer_ready.json',{'run_id':control['run_id'],'device':'cpu','conversion':'ORIGINAL_STANDARD_A','utc':utc()})
    frames=[];expected=0;(root/'hex').mkdir(exist_ok=True)
    while not (root/'STOP_REQUEST.json').exists() and not (root.parent/'STOP_REQUEST.json').exists():
        if not (root/'source_ring.json').exists():time.sleep(.005);continue
        source=load(root/'source_ring.json');pending=[f for f in source['frames'] if f['sequence']>=expected]
        if not pending:time.sleep(.003);continue
        require(pending[0]['sequence']==expected,'SOURCE_QUEUE_OVERRUN_RENDERER_NO_SKIP')
        frame=pending[0];bridge_begin=time.monotonic();blob=(root/frame['path']).read_bytes()
        if hashlib.sha256(blob).hexdigest()!=frame['sha256']:time.sleep(.002);continue
        bgr=np.load(io.BytesIO(blob),allow_pickle=False);read_s=time.monotonic()-bridge_begin;tick=time.monotonic()
        values,coordinates,transform=render_bgr_frames(bgr[None],spatial_policy='full-field',chunk_frames=1)
        require(values.shape==(1,721) and values.dtype==np.float32,'OFFICIAL_BOXEYE_SCHEMA')
        render_s=time.monotonic()-tick;write_begin=time.monotonic()
        path=root/'hex'/f'{expected%HEX_CAPACITY:02}.npy';temp=path.with_suffix('.tmp.npy');np.save(temp,values[0],allow_pickle=False);temp.replace(path)
        item={**frame,'hex_path':str(path.relative_to(root)),'hex_sha256':sha(path),
            'hex_values_sha256':hashlib.sha256(values[0].tobytes()).hexdigest(),'render_elapsed_s':render_s,
            'renderer_bridge_read_hash_s':read_s,'renderer_save_hash_s':time.monotonic()-write_begin}
        frames.append(item);frames=frames[-HEX_CAPACITY:]
        if expected==0:write(root/'spatial_identity.json',{'run_id':control['run_id'],'transform':transform,'coordinates':coordinates})
        write(root/'hex_ring.json',{'run_id':control['run_id'],'frames':frames});write(root/'renderer_progress.json',{'last_sequence':expected,'utc':utc()});expected+=1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);args=parser.parse_args()
    try:run(args.root)
    except BaseException as exc:
        write(host_path(args.root)/'renderer_error.json',{'error':str(exc),'utc':utc()});raise
