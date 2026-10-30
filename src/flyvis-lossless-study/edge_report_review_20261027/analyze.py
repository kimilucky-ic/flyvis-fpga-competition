from pathlib import Path
import zipfile,csv,io,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path('flyvis-lossless-study/edge_report_review_20261027').resolve(); ROOT=O.parent
Z=Path(r'C:/Users/hzy72/Documents/xwechat_files/wxid_khlrd7p7q6j422_642a/temp/RWTemp/2026-10/8eaa68ae41247203942b7fc2b28636e7/交付_原始数据_精简版.zip')
m=json.loads((ROOT/'ov5640_live_v261_20261026/assets/monitor.json').read_text());ids=np.array(m['regions'][0]['ids']);whole=np.array(m['regions'][1]['ids']);names=m['types']
result=[];fig,axs=plt.subplots(4,2,figsize=(14,12));mf,mas=plt.subplots(2,6,figsize=(12,5))
with zipfile.ZipFile(Z) as z:
 folders=sorted(n[:-len('/steps.csv')] for n in z.namelist() if n.endswith('/steps.csv'))
 for ri,f in enumerate(folders):
  rows=list(csv.DictReader(io.StringIO(z.read(f+'/steps.csv').decode('utf-8-sig'))));n=len(rows);t=np.array([float(r['t_s']) for r in rows]);has=np.array([int(r['has_full_state']) for r in rows],bool);st=t[has]
  x=np.frombuffer(z.read(f+'/inputs.bin'),'<f4').reshape(n,721);frames=np.frombuffer(z.read(f+'/frames.bin'),np.uint8).reshape(n,48,80,3);states=np.frombuffer(z.read(f+'/states.bin'),'<f4').reshape(has.sum(),45669)
  for j,r in enumerate(rows):
   assert hashlib.sha256(x[j].tobytes()).hexdigest()==r['input_sha256'];assert hashlib.sha256(frames[j].tobytes()).hexdigest()==r['frame_sha256']
  for j,r in enumerate(r for r,h in zip(rows,has) if h):assert hashlib.sha256(states[j].tobytes()).hexdigest()==r['state_sha256']
  values=states[:,ids].mean(axis=2,dtype=np.float64);av=states[:,whole].mean(axis=2,dtype=np.float64)
  bright=frames[:,:,16:64,:].mean(axis=3)>110;frac=bright.mean(axis=(1,2));v=frac if ri<4 else 1-frac;events=[];last=None;armed=False
  for k in range(n):
   if t[k]<4:continue
   if v[k]<.1:last=k;armed=True
   if not(armed and v[k]>.9 and last is not None):continue
   start=last;end=k;armed=False
   if t[end]-t[start]<.12:continue
   before=(st>=t[start]-1)&(st<t[start]-.2);during=(st>=t[start])&(st<=t[end]+.8)
   if not before.any() or not during.any():continue
   base=np.median(values[before],axis=0);delta=values[during]-base;block=bright[start:end+1];target=block if ri<4 else ~block;arrival=np.argmax(target,axis=0);yy,xx=np.indices((48,48));mask=(~target[0])&target[-1]&(xx>3)&(xx<44)&(yy>3)&(yy<44);fit=None
   if mask.sum()>100:
    tt=t[start+arrival[mask]];design=np.c_[xx[mask],yy[mask],np.ones(mask.sum())];b=np.linalg.lstsq(design,tt,rcond=None)[0];r2=1-float(((tt-design@b)**2).sum()/max(((tt-tt.mean())**2).sum(),1e-12));direction=['left' if b[0]<0 else 'right','up' if b[1]<0 else 'down'][int(abs(b[1])>abs(b[0]))];fit=dict(dt_dx=float(b[0]),dt_dy=float(b[1]),r2=r2,direction=direction)
   events.append(dict(start=float(t[start]),end=float(t[end]),fit=fit,baseline=base.tolist(),delta_mean=delta.mean(axis=0).tolist(),delta_min=delta.min(axis=0).tolist(),delta_max=delta.max(axis=0).tolist()))
  report=json.loads(z.read(f+'/meta/RESULT.json'));r=dict(folder=f,N=n,states_retained=int(has.sum()),hash_verified=True,reported_audit={k:report.get(k) for k in ['status','steps','state_words_compared','mismatch_words']},events=events,T4_full_run_range={name:[float(values[st>4,j].min()),float(values[st>4,j].max())] for j,name in enumerate(names) if name.startswith('T4')},T4_all721_range={name:[float(av[st>4,j].min()),float(av[st>4,j].max())] for j,name in enumerate(names) if name.startswith('T4')})
  j=names.index('T4d');sel=states[:,ids[j]];base=np.median(sel[(st>4)&(st<5)],axis=0);r['T4d_single_cell_delta_range_after4s']=[float((sel[st>4]-base).min()),float((sel[st>4]-base).max())];result.append(r)
  np.savez(O/(f+'_series.npz'),t=st,input_t=t,input_mean=x.mean(axis=1),bright_fraction=frac,central=values,all_cells=av,types=names)
  ax=axs[ri%4,ri//4]
  for j in (range(6,10) if ri<4 else range(10,14)):ax.plot(st,values[:,j],label=names[j],lw=1)
  for e in events:ax.axvspan(e['start'],e['end'],color='gray',alpha=.15)
  ax.set_title(f+': '+','.join(e['fit']['direction'] if e['fit'] else '?' for e in events));ax.legend(ncol=4,fontsize=7);ax.grid(alpha=.2);ax.set_xlim(4,45)
  if ri in [2,3] and events:
   e=events[0]
   for am,tm in zip(mas[ri-2],np.linspace(e['start']-.3,e['end']+.3,6)):
    k=np.argmin(abs(t-tm));am.imshow(frames[k,:,:,::-1]);am.set_title(f'{f[:2]} {t[k]:.2f}s');am.axis('off')
  print(f,n,'events',[(round(e['start'],2),round(e['end'],2),e['fit']) for e in events],flush=True)
  del states,frames
fig.suptitle('Raw signed central37 states; gray windows from image brightness (10%-90%)');fig.tight_layout();fig.savefig(O/'independent_curves.png',dpi=140);mf.tight_layout();mf.savefig(O/'vertical_frames.png',dpi=150)
(O/'RESULT.json').write_text(json.dumps(dict(evidence='READ_ONLY_RETAINED_SAMPLES_NOT_FULL_STEP_REAUDIT',state_sampling='every other step',types=names,rounds=result),indent=2),encoding='utf-8')
