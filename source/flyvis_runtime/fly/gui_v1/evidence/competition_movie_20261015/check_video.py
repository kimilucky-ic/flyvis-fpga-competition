"""Read back this delivered movie, not a new scientific experiment."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import imageio_ffmpeg

folder=Path(__file__).resolve().parents[2]/'exports/ON60_40s_a3968d273f374b27a42348a245bc120c'
evidence=Path(__file__).parent
m=json.loads((folder/'movie_manifest.json').read_text(encoding='utf-8'))
assert len(m['frames'])==485 and len(m['source_for_video_frame'])==1213
assert sorted(set(m['source_for_video_frame']))==list(range(485))
for k,row in enumerate(m['frames']):
    assert row['frame_index']==k and row['activity_time_s']==row['input_time_s']+.005
    assert hashlib.sha256((folder/row['png']).read_bytes()).hexdigest()==row['png_sha256']
samples={0,200,212,213,250,285,350,484}
indices={m['source_for_video_frame'].index(k):k for k in samples}
reader=imageio_ffmpeg.read_frames(str(folder/'ON60_40s_1080p.mp4'))
meta=next(reader);assert meta['size']==(1920,1080) and meta['fps']==30
checks=[];count=0
for n,pixels in enumerate(reader):
    count+=1
    if n not in indices:continue
    k=indices[n];image=Image.frombytes('RGB',(1920,1080),pixels)
    with Image.open(folder/m['frames'][k]['png']) as original:
        mae=float(np.abs(np.asarray(image).astype(np.int16)-np.asarray(original.convert('RGB')).astype(np.int16)).mean())
    assert mae<3, (k,mae)
    checks.append(dict(video_frame=n,source_frame=k,mean_absolute_pixel_error=mae))
    if k==213:image.save(evidence/'decoded_video_frame213.png')
assert count==1213
result=dict(status='PASS',gui_frames_verified=485,video_frames=count,decoded_metadata=meta,
            exact_saved_states=True,interpolated_states=0,video_samples=checks,
            note='Pixel error is lossy video encoding, not neural numerical error',
            video_sha256=hashlib.sha256((folder/'ON60_40s_1080p.mp4').read_bytes()).hexdigest())
(evidence/'video_readback.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
