import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',FLYVIS_ROOT_DIR='/opt/flyvis-visual-experiments-data',MPLBACKEND='Agg')
from pathlib import Path
import json,hashlib,numpy as np,xarray as xr
import flyvis
from flyvis.analysis.moving_bar_responses import peak_responses
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;z=np.load(O/'responses.npz');cfg=json.loads((O/'PROTOCOL.json').read_text())['config'];a=z['activity'];names=list(z['types']);t=z['time'];angles=z['angle'];intensities=z['intensity']
ds=xr.Dataset({'responses':(['network_id','sample','frame','neuron'],a)},coords={'network_id':[0],'sample':np.arange(24),'frame':np.arange(len(t)),'neuron':np.arange(65),'time':('frame',t),'cell_type':('neuron',names),'angle':('sample',angles),'intensity':('sample',intensities),'width':('sample',np.full(24,80)),'speed':('sample',np.full(24,19))},attrs={'config':cfg})
p=peak_responses(ds).values.squeeze();rows=[]
for n in ['T4a','T4b','T4c','T4d']:
 j=names.index(n);on=p[intensities==1,j];off=p[intensities==0,j];theta=np.deg2rad(angles[intensities==1]);v=abs((on*np.exp(1j*theta)).sum());rows.append(dict(type=n,ON_peak=float(on.max()),OFF_peak=float(off.max()),ON_peak_sum=float(on.sum()),OFF_peak_sum=float(off.sum()),ON_only_vector_ratio=float(v/(on.sum()+1e-15)),official_DSI=float(v/(max(on.sum(),off.sum())+1e-15))))
(O/'AMPLITUDE.json').write_text(json.dumps(rows,indent=2));fig,axes=plt.subplots(1,5,figsize=(17,4))
for ax,n in zip(axes,['T4a','T4b','T4c','T4d','T4d']):
 j=names.index(n)
 for k in np.where(intensities==1)[0]:ax.plot(t,a[0,k,:,j],color=plt.cm.hsv(float(angles[k])/360),label=str(int(angles[k])),lw=1)
 ax.set_xlim(0,.65);ax.grid(alpha=.2);ax.set_title(n);ax.set_xlabel('Model time (s)')
for ax in axes[:4]:ax.set_ylim(-.4,1.4)
axes[-1].set_title('T4d: separate y-scale');axes[0].set_ylabel('Raw state (not baseline-subtracted)');axes[-1].legend(ncol=3,fontsize=6)
fig.suptitle('Original model / official ON edges: first four panels use identical y-axis');fig.tight_layout();fig.savefig(O/'T4_shared_scale.png',dpi=140)
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in O.iterdir() if f.is_file() and f.name not in ['SHA256.json']};(O/'SHA256.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(rows))
