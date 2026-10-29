"""Local input-only evidence image; display crops do not alter frozen data."""
from pathlib import Path
import json
import csv
import sys
import os
import numpy as np
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'plot_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(HERE.parents[2]))
from camera_pipeline.common import cv2_module
cv=cv2_module()
folder=HERE/'frozen_selected_100_190'/'input'
identity=json.loads((folder/'INPUT_IDENTITY.json').read_text(encoding='utf-8'))
source=json.loads((folder/'source.json').read_text(encoding='utf-8'))
raw=np.load(source['frames_path'],mmap_mode='r',allow_pickle=False)
values=np.load(folder/'source_hex.npy',allow_pickle=False)
times=np.load(folder/'source_time.npy',allow_pickle=False)
with (folder/'input_hex_coordinates.csv').open(encoding='utf-8') as f: coords=list(csv.DictReader(f))
centers=np.array([[int(r['render_column']),int(r['render_row'])] for r in coords],np.float32)
projected=cv.perspectiveTransform(centers[None],np.asarray(identity['transform']['render_to_raw_homography']))[0]
fig,axes=plt.subplots(2,4,figsize=(13,7),layout='constrained')
for column,index in enumerate((0,40,60,90)):
    ax=axes[0,column]
    ax.imshow(np.asarray(raw[index])[:,:,::-1])
    ax.scatter(projected[:,0],projected[:,1],s=1,c='lime',alpha=.65)
    ax.set_xlim(260,510);ax.set_ylim(400,140)
    ax.set_title(f'Original frame {index+100} | local {times[index]:.3f}s')
    ax.set_xlabel('Raw x (display crop only)')
    ax.set_ylabel('Raw y, down')
    ax=axes[1,column]
    ax.set_facecolor('#edf2f7')
    scatter=ax.scatter(centers[:,0],centers[:,1],c=values[index],cmap='gray',vmin=0,vmax=1,s=25,marker='h',linewidths=.3,edgecolors='#889099')
    ax.set_xlim(110,530);ax.set_ylim(530,110);ax.set_aspect('equal')
    ax.set_title(f'721 receptor input | mean {values[index].mean():.3f}')
    ax.set_xlabel('BoxEye render column');ax.set_ylabel('BoxEye render row, down')
fig.colorbar(scatter,ax=axes[1,:].tolist(),label='Actual input luminance [0,1]',shrink=.7)
fig.suptitle('Actual phone -> computer camera | one fixed homography | original BoxEye(15,13)\n'
             'Input evidence only; phone wobble/exposure/reflections retained; neural activity not computed',fontsize=11)
fig.savefig(HERE/'selected_input_evidence.png',dpi=160)
plt.close(fig)
print(str(HERE/'selected_input_evidence.png'))
