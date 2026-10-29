"""Small meaningful IO/metric checks; no neural experiments or GPU."""
import tempfile
import json
from pathlib import Path
import numpy as np
from video_io import make_video,decode_video,geometry
from direction_readout import circular_error,evaluate,features,predict


def main():
    checks={}
    checks['wrap_359_1']=circular_error(359,1)==2
    checks['opposite_180']=circular_error(10,190)==180
    rejected=dict(status='NO_CONFIDENT_MOTION',angle_deg=None)
    e=evaluate(rejected,dict(kind='motion',angle_deg=22.5))
    checks['rejection_counts_as_miss']=not e['direction_hit_30'] and e['penalized_error_deg']==180
    checks['static_fp']=evaluate(dict(status='DIRECTION',angle_deg=0),dict(kind='static'))['false_motion']
    x=np.zeros((400,56),np.float32);types=np.repeat(np.arange(8),7)
    x[150,types==3]=2
    expected=np.zeros(8);expected[3]=2
    checks['known_feature_channel']=np.array_equal(features(x,types),expected)
    try:features(np.full((400,56),np.nan),types);checks['reject_nan']=False
    except ValueError:checks['reject_nan']=True
    xx,yy=geometry(np.array([0,1]),np.array([0,0]));checks['hex_identity_orientation']=bool(xx[0]==xx[1] and yy[1]>yy[0])
    with tempfile.TemporaryDirectory(prefix='io_check_',dir=Path(__file__).resolve().parent) as tmp:
        path=Path(tmp)/'constant.mp4';make_video(path,dict(kind='gray',level=.5))
        a,m=decode_video(path,dict(x_pixel=xx,y_pixel=yy))
        checks['actual_video_encode_decode']=a.shape==(400,2) and np.isfinite(a).all() and .4<float(a.mean())<.6
        checks['same_frame_held_for_two_steps']=m['input_frame_index'][:6]==[0,0,1,1,2,2] and m['input_frame_index'][-1]==199
        checks['no_future_input']=all(j/100<=t+1e-9 for j,t in zip(m['input_frame_index'],m['input_time_s']))
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,neural_steps=0,GPU=False)
    Path(__file__).with_name('CONTRACT_TESTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True);assert all(checks.values())


if __name__=='__main__':main()
