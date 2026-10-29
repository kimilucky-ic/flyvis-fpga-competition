import os,sys,time,json,hashlib,signal
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='-1',FLYVIS_ROOT_DIR='/opt/flyvis-visual-experiments-data',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',MPLBACKEND='Agg')
import numpy as np
import torch
torch.set_num_threads(1);torch.set_num_interop_threads(1)
import flyvis,xarray as xr
from flyvis import NetworkView
from flyvis.datasets.moving_bar import MovingEdge
from flyvis.analysis.moving_bar_responses import direction_selectivity_index,preferred_direction,correlation_to_known_tuning_curves
O=Path(__file__).resolve().parent; started=time.monotonic()
def dump(name,data):(O/name).write_text(json.dumps(data,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fail(kind,value,tb):
 dump('FAILURE.json',dict(error=repr(value),elapsed=time.monotonic()-started));sys.__excepthook__(kind,value,tb)
sys.excepthook=fail
signal.signal(signal.SIGALRM,lambda *args: (_ for _ in ()).throw(TimeoutError('CPU experiment 900s bound')));signal.alarm(900)
assert flyvis.device.type=='cpu'
view=NetworkView('/opt/flyvis-visual-experiments-data/results/flow/0000/000')
ck=Path(view.get_checkpoint('best')); expected_sha=json.loads((O.parent/'ov5640_live_v261_20261026/bundle/original_model_provenance.json').read_text())['checkpoint_sha256'];assert sha(ck)==expected_sha
model=view.network(checkpoint='best',lazy=True);model.recover();net=model.network;net.eval()
expected=torch.load(ck,map_location='cpu',weights_only=False)['network']
def unchanged():return all(torch.equal(v,expected[k]) for k,v in net.state_dict().items())
assert unchanged() and net.n_nodes==45669 and net.n_edges==1513231
cfg=dict(offsets=[-10,11],intensities=[0,1],speeds=[19],height=80,post_pad_mode='continue',t_pre=1.,t_post=1.,dt=.005,angles=list(range(0,360,30)))
dump('PROTOCOL.json',dict(evidence='OFFICIAL_CPU_MODEL_SYNTHETIC_STIMULUS_NOT_FPGA',checkpoint_sha256=sha(ck),config=cfg,batch_size=1,steady_state_t_pre=1.,t_fade_in=0.,max_seconds=900,threads=1,torch=torch.__version__,flyvis=flyvis.__version__,argv=sys.argv))
print('CHECKPOINT_MATCH; building original MovingEdge',flush=True)
dataset=MovingEdge(**cfg);print('STIMULUS_READY',len(dataset),flush=True)
idx=net.connectome.central_cells_index[:];types=net.connectome.nodes.type[:].astype(str)[idx]
out=[];inputs=[]
with torch.no_grad():
 for k,(stim,res) in enumerate(net.stimulus_response(dataset,.005,t_pre=1.,t_fade_in=0.,batch_size=1)):
  central=np.take(res,idx,axis=-1);assert np.isfinite(central).all();out.append(central);inputs.append(stim)
  np.save(O/f'central_{k:02d}.npy',central);print('SAMPLE',k+1,'/24',round(time.monotonic()-started,1),'s',flush=True)
assert unchanged()
a=np.concatenate(out)[None];s=np.concatenate(inputs);nf=a.shape[2]
ds=xr.Dataset({'responses':(['network_id','sample','frame','neuron'],a),'stimulus':(['sample','frame','channel','hex_pixel'],s)},coords={'sample':np.arange(len(dataset)),'frame':np.arange(nf),'time':('frame',np.arange(nf)*.005-1),'neuron':np.arange(len(idx)),'cell_type':('neuron',types),'u':('neuron',net.connectome.nodes.u[:][idx]),'v':('neuron',net.connectome.nodes.v[:][idx]),'network_id':[0],**{col:('sample',dataset.arg_df[col].values) for col in dataset.arg_df.columns}},attrs={'config':cfg})
np.savez_compressed(O/'responses.npz',activity=a,stimulus=s,types=types,time=ds.time.values,angle=ds.angle.values,intensity=ds.intensity.values)
dsis=direction_selectivity_index(ds);pds=preferred_direction(ds);corr=correlation_to_known_tuning_curves(ds)
rows=[]
for name in ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']:
 sel=dict(cell_type=name,intensity=1 if name.startswith('T4') else 0)
 rows.append(dict(type=name,DSI=float(dsis.custom.where(**sel).item()),preferred_degrees=float(pds.custom.where(**sel).item()*180/np.pi),tuning_correlation=float(corr.custom.where(**sel).item())))
dump('RESULT.json',dict(status='COMPLETED_OFFICIAL_CPU_EXPERIMENT',checkpoint_sha256=sha(ck),weights_unchanged=unchanged(),elapsed_s=time.monotonic()-started,results=rows))
import matplotlib.pyplot as plt
fig,axes=plt.subplots(2,4,figsize=(16,7),sharex=True)
for ax,row in zip(axes.flat,rows):
 j=list(types).index(row['type']);intensity=1 if row['type'].startswith('T4') else 0
 for k in np.where(ds.intensity.values==intensity)[0]:ax.plot(ds.time.values,a[0,k,:,j],label=str(ds.angle.values[k]),lw=.8)
 ax.set_title(row['type']+' DSI='+str(round(row['DSI'],3)));ax.set_xlim(-.2,.9);ax.grid(alpha=.2)
axes[0,0].legend(ncol=3,fontsize=6);fig.suptitle('Official MovingEdge: raw central-cell state, model time (s)');fig.tight_layout();fig.savefig(O/'curves.png',dpi=130)
print(json.dumps(rows),flush=True)
