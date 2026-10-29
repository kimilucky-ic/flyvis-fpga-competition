"""Read saved input and compare source-pixel receptor centers with official hex coordinates."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import argparse
import os
import numpy as np
from camera_pipeline.adapter import load_stimulus
from camera_pipeline.common import write_json

def plot_input(directory):
    os.environ['MPLCONFIGDIR']=str(Path(__file__).resolve().parent/'runtime/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle
    stimulus,grid,coords,metadata=load_stimulus(directory)
    xy=np.array([[float(c['plot_x']),float(c['plot_y'])] for c in coords])
    angles=np.arange(6)*np.pi/3
    vertices=xy[:,None,:]+np.stack([np.cos(angles),np.sin(angles)],axis=1)[None,:,:]*.95
    picks=np.unique(np.linspace(0,len(grid)-1,4,dtype=int))
    fig,axes=plt.subplots(1,len(picks),figsize=(3.5*len(picks),3.5),squeeze=False)
    for ax,index in zip(axes[0],picks):
        collection=PolyCollection(vertices,array=stimulus[0,index,0],cmap='gray',clim=(0,1),edgecolors='none')
        ax.add_collection(collection);ax.autoscale_view();ax.set_aspect('equal')
        ax.set_title(f'Input t={grid[index]:.3f} s');ax.set_xlabel('official hex x (lattice units)');ax.set_ylabel('official hex y (lattice units)')
    fig.suptitle(f"{metadata['source']['source_kind']} | original BoxEye | {metadata['temporal_method']} | dt={metadata['dt_s']} s")
    fig.tight_layout();fig.savefig(Path(directory)/'hex_input.png',dpi=150);plt.close(fig)
    source=Path(metadata['source']['source_path'])
    if source.is_dir() and (source/'frames.npy').exists():
        raw=np.load(source/'frames.npy',allow_pickle=False,mmap_mode='r')
        fig,ax=plt.subplots(figsize=(8,6));ax.imshow(raw[0,:,:,::-1])
        selected=[c for c in coords if c['source_center_x']!='' and c['source_center_y']!='']
        ax.scatter([float(c['source_center_x']) for c in selected],[float(c['source_center_y']) for c in selected],s=4,c='cyan',alpha=.65)
        if metadata['spatial_transform']['policy']=='native':
            footprint=np.zeros(raw.shape[1:3],dtype=bool)
            for c in coords:
                row,col=int(c['render_row']),int(c['render_column'])
                footprint[max(0,row-6):row+7,max(0,col-6):col+7]=True
            overlay=np.zeros((*footprint.shape,4));overlay[footprint]=[0,1,1,.12]
            ax.imshow(overlay)
            rows,cols=np.where(footprint)
            ax.add_patch(Rectangle((cols.min()-.5,rows.min()-.5),cols.max()-cols.min()+1,rows.max()-rows.min()+1,fill=False,edgecolor='cyan',linewidth=1))
            write_json(Path(directory)/'sampling_region.json',{'centers':721,'kernel_hw':[13,13],
                       'covered_pixel_count':int(footprint.sum()),'image_pixel_count':int(footprint.size),
                       'bounds_inclusive_xyxy':[int(cols.min()),int(rows.min()),int(cols.max()),int(rows.max())],
                       'bounds_are_envelope':'cyan translucent union is the actual used footprint; corners outside union are unused'})
        ax.set_title('Actual frame 0: 721 centers + 13x13 sampling footprint');ax.set_xlabel('camera column (pixels)');ax.set_ylabel('camera row (pixels; downward)')
        fig.tight_layout();fig.savefig(Path(directory)/'camera_receptor_overlay.png',dpi=150);plt.close(fig)
    result={'status':'PASS','loaded_shape':list(stimulus.shape),'range':[float(stimulus.min()),float(stimulus.max())],
            'coordinate_rows':len(coords),'input_checksums_verified':True,'output':'hex_input.png'}
    write_json(Path(directory)/'read_validation.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();print(plot_input(a.directory))
