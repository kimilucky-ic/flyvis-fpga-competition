from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import argparse
import json
from camera_pipeline.adapter import video_to_flyvis_stimulus,save_stimulus

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Use original BoxEye and actual temporal resampling; spatial policy is explicit.')
    p.add_argument('source',type=Path)
    p.add_argument('destination',type=Path)
    p.add_argument('--spatial-policy',choices=['native','full-field'],required=True)
    p.add_argument('--method',choices=['zoh','linear'],default='zoh')
    p.add_argument('--dt',type=float,default=.005)
    p.add_argument('--fps-override',type=float)
    a=p.parse_args()
    bundle=video_to_flyvis_stimulus(a.source,spatial_policy=a.spatial_policy,method=a.method,dt_s=a.dt,fps_override=a.fps_override)
    result=save_stimulus(bundle,a.destination)
    print(json.dumps({'output':str(result),'shape':bundle.stimulus.shape,'source_frames':len(bundle.source_time),'method':a.method,'causal':a.method=='zoh'}))
