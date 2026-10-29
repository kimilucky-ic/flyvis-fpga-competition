from pathlib import Path
import sys,json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=Path('flyvis-lossless-study/ov5640_live_v261_20261026').resolve();out=Path('flyvis-lossless-study/brightness_review_20261027').resolve()
sys.path.insert(0,str(base/'pc'));sys.path.insert(0,str(base/'bundle'))
from live_protocol import Store
from neuron_observer import Observer
config=json.loads((base/'pc/rounds/6bc6ac2081b14d4296dd007b5aae12f4/session.json').read_text())
s=Store(base/'pc/rounds/6bc6ac2081b14d4296dd007b5aae12f4/records',config)
o=Observer(base/'assets/monitor.json');types=o.map['types'];receptors=o.map['regions'][0]['receptor_ids'];rows=[];images=[]
for k in range(len(s.meta)):
 m,source,r=s.read(k);x=np.frombuffer(r.input_bits,'<f4');v=np.asarray(o.means(r.state_bits))[0];im=np.frombuffer(source,np.uint8).reshape(48,80,3)
 row=dict(step=k,wall_s=m['experiment']['elapsed_ns']/1e9,model_s=(k+1)*.005,input_mean=float(x.mean()),input_roi=float(x[receptors].mean()),input_p10=float(np.quantile(x,.1)),input_p90=float(np.quantile(x,.9)),input_bright_fraction=float((x>.9).mean()))
 row.update(zip(types,v));rows.append(row);images.append(im.copy())
with (out/'input_and_neuron_curves.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
t=np.array([r['wall_s'] for r in rows]);x=np.array([r['input_roi'] for r in rows]);g=np.array([r['input_mean'] for r in rows]);a=np.array([[r[n] for n in types] for r in rows]);smooth=np.convolve(x,np.ones(9)/9,mode='same');d=smooth[8:]-smooth[:-8];candidates=np.argsort(abs(d))[::-1];picked=[]
for q in candidates:
 k=int(q+4)
 if t[k]<2 or t[k]>t[-1]-1 or abs(d[q])<.12:continue
 if all(abs(t[k]-t[j])>2 for j in picked):picked.append(k)
picked.sort();events=[]
for k in picked:
 before=(t>t[k]-1)&(t<t[k]-.3);after=(t>t[k]+.3)&(t<t[k]+1)
 if not before.any() or not after.any():continue
 delta=float(np.median(x[after])-np.median(x[before]));events.append(dict(step=k,wall_s=float(t[k]),input_before=float(np.median(x[before])),input_after=float(np.median(x[after])),input_delta=delta,kind='BRIGHTENING' if delta>0 else 'DARKENING',state_delta={n:float(np.median(a[after,types.index(n)])-np.median(a[before,types.index(n)])) for n in ['Mi1','Tm3','Tm1','Tm2']}))
f=json.loads((s.path/'FINISH.json').read_text());close=json.loads((s.path/'CAMERA_CLOSE.json').read_text());dur=f['duration'];timings=list(f['packet_timings'].values())
timing={key:dict(mean=float(np.mean([v[key] for v in timings if key in v])),p95=float(np.quantile([v[key] for v in timings if key in v],.95))) for key in ['full_iteration_before_pacing_ms','capture_and_cache_ms','ps_mapping_ms','input_721_mmio_write_ms','input_upload_step_and_publication_ms','ddr_copy_and_cache_ms','between_iterations_ms'] if any(key in v for v in timings)}
summary=dict(run_id=close['run_id'],steps=len(rows),duration=dur,average_ms=dur['elapsed_seconds']*1000/len(rows),fps=len(rows)/dur['elapsed_seconds'],camera_close=close['status'],hardware_completed_steps=f['hardware_completed_steps'],neural_after=f['context']['NEURAL_AFTER.json'],input_range=dict(roi_min=float(x.min()),roi_max=float(x.max()),global_min=float(g.min()),global_max=float(g.max())),events=events,timing=timing,events_are_image_derived_candidates=True,biological_pass=False)
# Two-second bins describe observed stimulation without assuming paper labels.
summary['bins']=[dict(start=z,input=float(np.median(x[(t>=z)&(t<z+2)])),**{n:float(np.median(a[(t>=z)&(t<z+2),types.index(n)])) for n in ['Mi1','Tm3','Tm1','Tm2']}) for z in range(0,60,2) if ((t>=z)&(t<z+2)).any()]
(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
fig,axes=plt.subplots(5,1,figsize=(13,10),sharex=True)
axes[0].plot(t,g,label='All 721 mean',alpha=.6);axes[0].plot(t,x,label='Central 37 mean');axes[0].set_ylabel('Actual input');axes[0].legend(loc='upper right')
for ax,n in zip(axes[1:],['Mi1','Tm3','Tm1','Tm2']):ax.plot(t,a[:,types.index(n)],label=n);ax.set_ylabel(n+' state');ax.axhline(0,color='grey',lw=.5)
for ax in axes:
 ax.grid(alpha=.2)
 for e in events:ax.axvline(e['wall_s'],color='orange' if e['input_delta']>0 else 'purple',alpha=.35,lw=.8)
axes[-1].set_xlabel('Capture wall time (seconds); model dt=5 ms per step');fig.suptitle('Saved FPGA records: actual grayscale input and signed central-37 state means\nLines mark image-derived transition candidates, not manual paper annotations');fig.tight_layout();fig.savefig(out/'brightness_response.png',dpi=150);plt.close(fig)
chosen=sorted(set([0,len(rows)-1]+[int(np.argmin(x)),int(np.argmax(x))]+[min(len(rows)-1,max(0,int(np.searchsorted(t,z)))) for z in range(5,60,5)]))
fig,axes=plt.subplots(3,5,figsize=(13,7));
for ax in axes.flat:ax.axis('off')
for ax,k in zip(axes.flat,chosen[:15]):ax.imshow(images[k][:,:,::-1]);ax.set_title('%.2fs | ROI %.3f'%(t[k],x[k]),fontsize=9)
fig.suptitle('Original saved 80x48 camera frames (BGR interpreted as RGB)');fig.tight_layout();fig.savefig(out/'camera_samples.png',dpi=140);plt.close(fig)
print(json.dumps({k:v for k,v in summary.items() if k not in ['bins','timing']},ensure_ascii=False))
print('BINS',json.dumps(summary['bins']))
