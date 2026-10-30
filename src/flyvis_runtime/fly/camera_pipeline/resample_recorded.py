"""Export offline linear candidate from frozen official source_hex, with no re-render drift."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import argparse
import csv
import json
import numpy as np
from camera_pipeline.adapter import StimulusBundle,load_stimulus,resample_hex,save_stimulus
from camera_pipeline.common import utc_now

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path)
    p.add_argument('--method',choices=['zoh','linear'],required=True);a=p.parse_args()
    _,_,_,metadata=load_stimulus(a.source)
    source_hex=np.load(a.source/'source_hex.npy',allow_pickle=False)
    source_time=np.load(a.source/'source_time.npy',allow_pickle=False)
    stimulus,grid,alignment=resample_hex(source_hex,source_time,dt_s=metadata['dt_s'],method=a.method)
    with (a.source/'input_hex_coordinates.csv').open(encoding='utf-8') as handle:coordinates=list(csv.DictReader(handle))
    metadata={k:v for k,v in metadata.items() if k!='data_sha256'}
    metadata.update(temporal_method=a.method,causal=a.method=='zoh',created_utc=utc_now(),
                    temporal_source=str(a.source.resolve()),neural_inference_executed=False)
    result=save_stimulus(StimulusBundle(stimulus,grid,source_hex,source_time,coordinates,alignment,metadata),a.destination)
    print(json.dumps({'output':str(result),'shape':list(stimulus.shape),'method':a.method}))
