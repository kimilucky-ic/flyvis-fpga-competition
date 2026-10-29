"""a_r4 standalone MP4 direction inference; Python + NumPy + OpenCV."""
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
