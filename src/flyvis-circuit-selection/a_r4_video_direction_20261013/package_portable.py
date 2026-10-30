"""Package the frozen a_r4 video runtime; no neural computation."""
import json
import shutil
from pathlib import Path
from video_io import sha

HERE=Path(__file__).resolve().parent
out=HERE/'portable_a_r4'
out.mkdir()
for f in ['independent_model.py','video_io.py','direction_readout.py','run_video.py','readout_Full.json','readout_A_R4.json']:
    shutil.copyfile(HERE/f,out/f)
for f in ['model.npz','sampler.npz','readout_local_ids.npy','readout_type_index.npy']:
    shutil.copyfile(HERE/'models/a_r4'/f,out/f)
# First heldout case, selected by protocol order, not by measured performance.
shutil.copyfile(HERE/'videos/T_ON_022.5_v12.mp4',out/'demo.mp4')
wrapper='''"""a_r4 standalone MP4 direction inference; Python + NumPy + OpenCV."""
import argparse
import sys
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
from run_video import main
p=argparse.ArgumentParser()
p.add_argument('--video',type=Path,default=root/'demo.mp4')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--profile',choices=['shared','own'],default='shared')
a=p.parse_args()
sys.argv=[str(root/'run_video.py'),'--video',str(a.video),'--output',str(a.output),
    '--model',str(root/'model.npz'),'--sampler',str(root/'sampler.npz'),
    '--roi',str(root/'readout_local_ids.npy'),'--types',str(root/'readout_type_index.npy'),
    '--readout',str(root/('readout_Full.json' if a.profile=='shared' else 'readout_A_R4.json'))]
main()
'''
(out/'predict_video.py').write_text(wrapper,encoding='utf-8')
(out/'readme.txt').write_text('''a_r4 independent video-to-local-direction CPU package

Requires Python, NumPy and OpenCV (cv2). No PyTorch, FlyVis install, GPU,
original Full network, full-network a0, or saved neural trajectory is required.

From this directory:
  python -I -B predict_video.py --video demo.mp4 --output new_result
  python -I -B predict_video.py --video YOUR_CLIP.mp4 --output another_result --profile own

shared (default): frozen readout calibrated on Full design data; primary comparison.
own: preregistered separate calibration on a_r4 design data; secondary usability.
Both are new local readouts, not official DecoderGAVP and not optical flow.
Original neural parameters are unchanged. No automatic fallback or profile selection.

Contract: constant-frame-rate decodable video >=2s. Only the first two seconds
are used. 224x224 grayscale conversion, aspect-preserving gray letterbox if needed,
3x3 mean at fixed61 retinal positions, 5ms causal zero-order-hold input.
Clip design has a static first0.5s; fixed baseline outputs[60:100], response[100:400].
200 gray warmup +400 movie steps all computed on own3865 states,110794 edges.
One direction is produced after the2s clip. It is not a per-frame live tracker.

Angle0=right,90=up,180=left,270=down, in the displayed image coordinate frame.
NO_CONFIDENT_MOTION is abstention; it does not prove that the scene is static.
Vector norm is not probability. The output directory must not already exist.
The included demo is the FIRST heldout clip by preregistered order, not a best case.

Validated scope: synthetic single moving luminance edge and listed controls only.
Natural video, camera shake, multiple objects, occlusion, other sizes/contrasts,
variable frame rates, arbitrary onset time, speed estimation and hardware are untested.
Changing field of view or rescaling an object changes the stimulus domain.
See parent REPORT.md and SUMMARY.json for actual failures and retained limitations.
''',encoding='utf-8')
manifest={f.name:dict(sha256=sha(f),bytes=f.stat().st_size) for f in out.iterdir() if f.is_file()}
(out/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PACKAGED_FROZEN_CPU_RUNTIME',directory=str(out),files=len(manifest))))
