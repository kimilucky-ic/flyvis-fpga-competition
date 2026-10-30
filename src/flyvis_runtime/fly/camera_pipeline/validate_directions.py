"""Known raw-image motion direction, independent of neural preference. Synthetic inputs clearly labeled."""
from pathlib import Path
import sys
import os
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import numpy as np
from camera_pipeline.adapter import render_bgr_frames,resample_hex
from camera_pipeline.common import ROOT,write_json

def main():
    os.environ['MPLCONFIGDIR']=str(ROOT/'runtime/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=ROOT/'results/direction_mapping_validation'
    out.mkdir(exist_ok=False)
    h,w=480,640
    conditions=[('right',1,220,420,1),('left',1,420,220,-1),
                ('down',0,140,340,1),('up',0,340,140,-1)]
    records=[];inputs={}
    fig,axes=plt.subplots(2,2,figsize=(10,8))
    for ax,(name,axis,start,end,sign) in zip(axes.flat,conditions):
        positions=np.linspace(start,end,17)
        coordinate=np.indices((h,w))[axis]
        gray=np.stack([np.where(coordinate>=position,255,0).astype(np.uint8) for position in positions])
        frames=np.repeat(gray[:,:,:,None],3,axis=-1)
        rendered,coords,transform=render_bgr_frames(frames,spatial_policy='native')
        inputs[name]=rendered
        source_coordinate=np.array([c['render_column' if axis==1 else 'render_row'] for c in coords])
        selected=(source_coordinate>min(start,end)+20)&(source_coordinate<max(start,end)-20)
        change=np.abs(np.diff(rendered,axis=0))
        crossing=np.argmax(change,axis=0)+.5
        correlation=float(np.corrcoef(source_coordinate[selected],crossing[selected])[0,1])
        assert sign*correlation>.97,(name,correlation)
        # Every input has the expected camera position correspondence, beyond just a correlation.
        expected=np.stack([[gray[i,c['render_row']-6:c['render_row']+7,c['render_column']-6:c['render_column']+7].mean()/255
                            for c in coords] for i in range(len(gray))]).astype(np.float32)
        np.testing.assert_allclose(rendered,expected,atol=1e-6,rtol=0)
        stimulus,t,alignment=resample_hex(rendered,np.arange(17)/30,method='zoh')
        np.save(out/f'{name}_source_hex.npy',rendered,allow_pickle=False)
        np.save(out/f'{name}_stimulus.npy',stimulus,allow_pickle=False)
        ax.scatter(source_coordinate[selected],crossing[selected]/30,s=8)
        ax.set_title(f'{name}: correlation={correlation:+.5f}');ax.set_xlabel('raw camera '+('column' if axis==1 else 'row')+' (pixels)');ax.set_ylabel('edge crossing time (s; synthetic 30 FPS)')
        records.append({'condition':name,'raw_motion_axis':'column' if axis==1 else 'row',
                        'expected_direction_sign':sign,'coordinate_crossing_correlation':correlation,
                        'source_frames':17,'source_fps':30,'dt_s':.005,'stimulus_shape':list(stimulus.shape),
                        'max_abs_against_direct_box_mean':float(np.abs(rendered-expected).max()),'status':'PASS'})
    np.testing.assert_array_equal(inputs['right'],inputs['left'][::-1])
    np.testing.assert_array_equal(inputs['down'],inputs['up'][::-1])
    fig.suptitle('Synthetic known-direction edges: original BoxEye native 640x480; input mapping only')
    fig.tight_layout();fig.savefig(out/'direction_validation.png',dpi=150);plt.close(fig)
    result={'status':'PASS','source_kind':'synthetic_direction_fixture','conditions':records,
            'opposite_directions_are_exact_time_reversals':True,'neural_inference_executed':False,
            'interpretation':'raw right/left and down/up are preserved. Official plot y increases upward, camera row downward; this is coordinate convention, not an image flip.'}
    write_json(out/'result.json',result)
    print(result)

if __name__=='__main__':main()
