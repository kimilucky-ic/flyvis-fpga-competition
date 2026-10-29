from pathlib import Path
import sys,json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path('flyvis-lossless-study/ov5640_live_v261_20261026').resolve();O=R.parent/'biology_ec678d75_20261027';O.mkdir(exist_ok=True);sid='ec678d754b06595db3a4f9acd492159d';D=R/'pc/rounds'/sid/'records'
sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
from live_protocol import Store
from neuron_observer import Observer
s=Store(D,json.loads((D.parent/'session.json').read_text()));o=Observer(R/'assets/monitor.json');audit=json.loads((D/'audit/RESULT.json').read_text());assert audit['status']=='PASS_ALL_SAVED_STATES';references={r['step_id']:r for r in audit['rows']};rows=[];ims=[];allmeans=[]
for k in range(len(s.meta)):
 m,source,r=s.read(k);ref=references[k];assert hashlib.sha256(r.input_bits).hexdigest()==ref['input_sha256'];assert hashlib.sha256(r.state_bits).hexdigest()==ref['actual_state_sha256']==ref['expected_state_sha256']
 x=np.frombuffer(r.input_bits,'<f4');v=o.means(r.state_bits);row=dict(step=k,wall_s=m['experiment']['elapsed_ns']/1e9,model_s=(k+1)*.005,input_mean=float(x.mean()),input_roi=float(x[o.map['regions'][0]['receptor_ids']].mean()));row.update(zip(o.map['types'],v[0]));rows.append(row);ims.append(np.frombuffer(source,np.uint8).reshape(48,80,3)[:,:,::-1].copy());allmeans.append(v[1])
with (O/'curves.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,rows[0]);w.writeheader();w.writerows(rows)
t=np.array([r['wall_s'] for r in rows]);x=np.array([r['input_roi'] for r in rows]);g=np.array([r['input_mean'] for r in rows]);a=np.array([[r[n] for n in o.map['types']] for r in rows]);whole=np.asarray(allmeans)
np.savez(O/'series.npz',t=t,input_roi=x,input_all=g,central=a,all_cells=whole,types=o.map['types'])
fig,axs=plt.subplots(5,1,figsize=(13,11),sharex=True)
axs[0].plot(t,x,label='Central37 actual input');axs[0].plot(t,g,label='All721 actual input',alpha=.6);axs[0].legend(loc='upper right');axs[0].set_ylim(0,1.05)
for ax,ns in zip(axs[1:],[['L1','L2'],['Mi1','Tm3'],['Tm1','Tm2'],['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']]):
 for n in ns:ax.plot(t,a[:,o.map['types'].index(n)],label=n,lw=1)
 ax.legend(loc='upper right',ncol=4);ax.set_ylabel('Signed state')
for ax in axs:ax.grid(alpha=.2)
axs[-1].set_xlabel('Capture wall seconds (model advances 5 ms/step)');fig.suptitle('Saved FPGA run ec678d75: full-field black/white switching\nCentral37 means; separate panel scales; not a direction-selectivity assay');fig.tight_layout();fig.savefig(O/'responses.png',dpi=140);plt.close(fig)
fig,axs=plt.subplots(4,6,figsize=(14,8));
for ax,z in zip(axs.flat,np.linspace(0,t[-1],24)):
 k=int(np.argmin(abs(t-z)));ax.imshow(ims[k]);ax.set_title(f'{t[k]:.2f}s | input {x[k]:.2f}',fontsize=9);ax.axis('off')
fig.tight_layout();fig.savefig(O/'frames.png',dpi=130);plt.close(fig)
f=json.loads((D/'FINISH.json').read_text());summary=dict(session_id=sid,operator_stimulus='full-field black white switching',steps=len(rows),duration_s=f['duration']['elapsed_seconds'],state_words=audit['state_words_compared'],mismatch_words=audit['mismatch_words'],input_range=[float(x.min()),float(x.max())],bins=[dict(start=z,input=float(np.median(x[(t>=z)&(t<z+2)])),**{n:float(np.median(a[(t>=z)&(t<z+2),j])) for j,n in enumerate(o.map['types'])}) for z in range(0,60,2)])
(O/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
