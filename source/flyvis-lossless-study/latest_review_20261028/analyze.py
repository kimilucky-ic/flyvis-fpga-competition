from pathlib import Path
import sys,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
R=O.parent/'ov5640_live_v261_20261026'
sys.path.insert(0,str(R/'bundle'))
from live_protocol import unpack
mp=json.loads((R/'assets/monitor.json').read_text()); names=mp['types']; ids=np.array(mp['regions'][0]['ids']); whole=np.array(mp['regions'][1]['ids'])
sessions=['c0abc1b20dee5e16b601a90638e9659b','81b5f85945a95503b782dee60d519632','a97f17da4df6563484b1adff574f9fe4','77415dc30b9a520898b4dd12bd3aff02']
results=[]
for sid in sessions:
 d=R/'pc/rounds'/sid; cfg=json.loads((d/'session.json').read_text()); rec=d/'records'; packets=sorted(rec.glob('*.packet'))
 if not packets:continue
 frames=[]; ts=[]; means=[]; av=[]; dcell=[]; inp=[]
 for k,p in enumerate(packets):
  m,src,r=unpack(p.read_bytes(),cfg); assert m['step_id']==k
  st=np.frombuffer(r.state_bits,'<f4'); means.append(st[ids].mean(1));av.append(st[whole].mean(1));dcell.append(st[whole[names.index('T4d')]])
  frames.append(np.frombuffer(src,np.uint8).reshape(48,80,3).copy());ts.append(m['experiment']['elapsed_ns']/1e9);inp.append(np.frombuffer(r.input_bits,'<f4').mean())
 t=np.array(ts); frames=np.array(frames); v=np.array(means); av=np.array(av); dc=np.array(dcell);gray=frames[:,:,16:64].mean(3); frac=(gray>110).mean((1,2));events=[]
 for polarity in ['ON','OFF']:
  q=frac if polarity=='ON' else 1-frac; last=None
  for k in range(len(t)):
   if t[k]<4:continue
   if q[k]<.1:last=k
   if last is None or q[k]<=.9:continue
   a=last;b=k;last=None
   if t[b]-t[a]<.1:continue
   target=(gray[a:b+1]>110) if polarity=='ON' else (gray[a:b+1]<=110)
   yy,xx=np.indices((48,48)); mask=(~target[0])&target[-1]&(xx>3)&(xx<44)&(yy>3)&(yy<44)
   fit=None
   if mask.sum()>100:
    arrival=t[a+np.argmax(target,axis=0)[mask]];X=np.c_[xx[mask],yy[mask],np.ones(mask.sum())];coef=np.linalg.lstsq(X,arrival,rcond=None)[0];r2=1-((arrival-X@coef)**2).sum()/max(((arrival-arrival.mean())**2).sum(),1e-12)
    fit={'direction':('right' if coef[0]>0 else 'left') if abs(coef[0])>abs(coef[1]) else ('down' if coef[1]>0 else 'up'),'r2':float(r2)}
   base=(t>=t[a]-1)&(t<t[a]-.15); win=(t>=t[a])&(t<=t[b]+.5)
   if not base.any():continue
   delta=v[win]-np.median(v[base],axis=0)
   events.append(dict(polarity=polarity,start=float(t[a]),end=float(t[b]),fit=fit,peak=delta.max(0).tolist(),mean=delta.mean(0).tolist()))
 audit=json.loads((rec/'audit/RESULT.json').read_text()) if (rec/'audit/RESULT.json').exists() else {}
 keep=t>4
 report=dict(session=sid,steps=len(t),first_capture_s=float(t[0]),last_capture_s=float(t[-1]),mean_capture_interval_ms=float(np.diff(t).mean()*1000),audit={k:audit.get(k) for k in ['status','steps','state_words_compared','mismatch_words']},packet_bindings_verified=True,events=events,central37_range={n:[float(v[keep,j].min()),float(v[keep,j].max())] for j,n in enumerate(names)},T4d_cell_temporal_range_p50_p95_max=np.percentile(np.ptp(dc[keep],axis=0),[50,95,100]).tolist())
 results.append(report)
 fig,axs=plt.subplots(4,1,figsize=(14,10),sharex=True)
 axs[0].plot(t,gray.mean((1,2))/255,label='camera crop mean');axs[0].plot(t,frac,label='bright fraction >110');axs[0].legend()
 for ax,inds in zip(axs[1:],[range(6),range(6,10),range(10,14)]):
  for j in inds:ax.plot(t,v[:,j],label=names[j],lw=1)
  ax.legend(ncol=6);ax.grid(alpha=.2);ax.set_ylabel('Raw state / central37')
 for ax in axs:
  for e in events:ax.axvspan(e['start'],e['end'],alpha=.08,color='orange' if e['polarity']=='ON' else 'blue')
 axs[-1].set_xlabel('Wall time (s); model time = step * 0.005s');fig.suptitle(sid[:8]+' actual saved camera and neural states');fig.tight_layout();fig.savefig(O/(sid[:8]+'_curves.png'),dpi=130);plt.close(fig)
 fig,axs=plt.subplots(3,8,figsize=(16,6))
 for ax,sec in zip(axs.flat,np.linspace(2,t[-1],24)):
  k=np.argmin(abs(t-sec));ax.imshow(frames[k,:,:,::-1]);ax.axvline(16,color='cyan',lw=.5);ax.axvline(63,color='cyan',lw=.5);ax.set_title(f'{t[k]:.1f}s');ax.axis('off')
 fig.suptitle(sid[:8]+' original frames; cyan = used crop');fig.tight_layout();fig.savefig(O/(sid[:8]+'_frames.png'),dpi=120);plt.close(fig)
 np.savez_compressed(O/(sid[:8]+'_series.npz'),time=t,central=v,all721=av,bright_fraction=frac,types=names)
 print(sid[:8],len(t),report['audit'], 'events',[(e['polarity'],round(e['start'],1),round(e['end'],1),e['fit']) for e in events],flush=True)
(O/'RESULT.json').write_text(json.dumps(dict(evidence='READ_ONLY_SAVED_RECORD_ANALYSIS_EXISTING_AUDITS_NOT_NEW_BOARD_RUN',types=names,threshold=110,event_limitations='10-90 percent full-field crossings only; direction is image arrival plane fit, not calibrated subtype preference; manual motion and exposure confounded',rounds=results),indent=2),encoding='utf8')
