"""Read back the actual C GUI export; does not recompute any neural activity."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from PIL import Image
import imageio_ffmpeg

folder=Path(sys.argv[1]).resolve()
evidence=Path(__file__).parent
m=json.loads((folder/'movie_manifest.json').read_text(encoding='utf-8'))
assert m['brightness_variant']=='C' and m['display_kind']=='OFFLINE_REPLAY'
assert m['run_id']=='2041849d-b1f8-46ad-a059-49b598c19ab2'
assert m['frame_pack_sha256']=='0dd6266e155fb7f87e53e31e9557ff6c83a3cd6ef4cef87108e815d84b630d04'
assert m['model_dt_s']==.005 and m['PL_execution'] is False
assert len(m['frames'])==485 and m['source_for_video_frame']==[n*485//1200 for n in range(1200)]
source=json.loads(Path(m['frame_pack_path']).read_text(encoding='utf-8'))
assert hashlib.sha256(Path(m['frame_pack_path']).read_bytes()).hexdigest()==m['frame_pack_sha256']
for k,row in enumerate(m['frames']):
    assert row['frame_index']==k and row['activity_time_s']==row['input_time_s']+.005
    assert row['skeleton_sha256']==source['frames'][k]['png_sha256']
    assert row['source_receipt_sha256']==source['frames'][k]['receipt_sha256']
    assert hashlib.sha256((folder/row['png']).read_bytes()).hexdigest()==row['png_sha256']
samples={0,100,199,200,212,213,250,284,285,350,470,484}
indices={m['source_for_video_frame'].index(k):k for k in samples}
reader=imageio_ffmpeg.read_frames(str(folder/'ON60_40s_1080p.mp4'))
meta=next(reader)
assert meta['size']==(1920,1080) and meta['fps']==30 and abs(meta['duration']-40)<.02
checks=[];count=0
for n,pixels in enumerate(reader):
    count+=1
    if n not in indices:continue
    k=indices[n];image=Image.frombytes('RGB',(1920,1080),pixels)
    with Image.open(folder/m['frames'][k]['png']) as original:
        mae=float(np.abs(np.asarray(image).astype(np.int16)-np.asarray(original.convert('RGB')).astype(np.int16)).mean())
    assert mae<3,(k,mae)
    checks.append(dict(video_frame=n,source_frame=k,mean_absolute_pixel_error=mae))
    if k==213:image.save(evidence/'decoded_video_frame213.png')
assert count==1200
result=dict(status='PASS',export_directory=str(folder),gui_frames_verified=485,video_frames=count,
            decoded_metadata=meta,exact_saved_states=True,interpolated_states=0,video_samples=checks,
            note='Pixel error is lossy video encoding, not neural numerical error',
            video_sha256=hashlib.sha256((folder/'ON60_40s_1080p.mp4').read_bytes()).hexdigest())
(evidence/'video_readback.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
