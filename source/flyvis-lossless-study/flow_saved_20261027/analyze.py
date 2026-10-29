"""Predeclared image-window direction scoring; never fit component signs to data."""
from pathlib import Path
import json,csv,io,zipfile,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;R=O.parent
prior=json.loads((R/'edge_report_review_20261027/RESULT.json').read_text())
nodes=list(csv.DictReader(Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1/structure/nodes.csv').open()))[:721]
u=np.array([int(r['u']) for r in nodes]);v=np.array([int(r['v']) for r in nodes]);roi=np.maximum.reduce([abs(u),abs(v),abs(u+v)])<=3
assert roi.sum()==37
# Pixel sampling centers match the retained center-square input mapping.
cy=(np.trunc(13*(u+v/2)).astype(int)+208+.5)*48/417-.5;cx=(13*v+208+.5)*48/417-.5
yy=np.clip(np.rint(cy).astype(int),0,47);xx=np.clip(np.rint(cx).astype(int),0,47)
Z=Path('/mnt/c/Users/hzy72/Documents/xwechat_files/wxid_khlrd7p7q6j422_642a/temp/RWTemp/2026-10/8eaa68ae41247203942b7fc2b28636e7/交付_原始数据_精简版.zip')
directions={'left':np.array([-1.,0]),'right':np.array([1.,0]),'up':np.array([0,1.]),'down':np.array([0,-1.])}
def score(vector,expected):
 norm=float(np.linalg.norm(vector));cos=float(np.dot(vector,expected)/norm) if norm>1e-8 else 0
 return dict(vector=vector.tolist(),magnitude=norm,angle_error_deg=float(np.rad2deg(np.arccos(np.clip(cos,-1,1)))),passed=bool(norm>1e-8 and cos>=2**-.5))
result=[];fig,axs=plt.subplots(4,2,figsize=(13,11),sharex=True)
with zipfile.ZipFile(Z) as z:
 for ri,previous in enumerate(prior['rounds']):
  folder=previous['folder'];flow=np.load(O/'repeat1'/(folder+'_flow.npy'));st=np.load(O/'repeat1'/(folder+'_time.npy'))
  rows=list(csv.DictReader(io.StringIO(z.read(folder+'/steps.csv').decode('utf-8-sig'))));t=np.array([float(r['t_s']) for r in rows]);frames=np.frombuffer(z.read(folder+'/frames.bin'),np.uint8).reshape(len(t),48,80,3)
  for frame,row in zip(frames,rows):assert hashlib.sha256(frame.tobytes()).hexdigest()==row['frame_sha256']
  central=flow[:,:,roi].mean(axis=2,dtype=np.float64);whole=flow.mean(axis=2,dtype=np.float64);events=[]
  for e in previous['events']:
   s,end=e['start'],e['end'];direction=e['fit']['direction'];target=directions[direction];during=(st>=s)&(st<=end);before=(st>=s-1)&(st<s-.2);base=np.median(central[before],axis=0)
   # Secondary local edge-band selection comes only from image threshold arrival.
   a=np.argmin(abs(t-s));b=np.argmin(abs(t-end));bright=frames[a:b+1,:,16:64,:].mean(axis=3)>110;changed=bright if ri<4 else ~bright;hit=(~changed[0])&changed[-1];arrival=t[a+np.argmax(changed,axis=0)];local=[]
   for k in np.where(during)[0]:
    mask=hit[yy,xx]&(abs(arrival[yy,xx]-st[k])<=.25)
    if mask.any():local.append(flow[k][:,mask].mean(axis=1,dtype=np.float64))
   primary=score(central[during].mean(axis=0),target)
   per_frame=[score(q,target)['passed'] for q in central[during]]
   events.append(dict(start=s,end=end,image_direction=direction,image_fit_r2=e['fit']['r2'],retained_samples=int(during.sum()),primary=primary,all721=score(whole[during].mean(axis=0),target),edge_band=score(np.mean(local,axis=0),target) if local else None,baseline_subtracted_diagnostic=score((central[during]-base).mean(axis=0),target),pre_event_median_vector=base.tolist(),per_frame_correct_fraction=float(np.mean(per_frame))))
  correct=sum(e['primary']['passed'] for e in events);item=dict(folder=folder,polarity='bright' if ri<4 else 'dark',direction=events[0]['image_direction'],events=events,correct=correct,total=len(events),passed=bool(len(events)==3 and correct>=2));result.append(item)
  ax=axs[ri%4,ri//4];ax.plot(st,central[:,0],label='x: +right',color='#df8c30');ax.plot(st,central[:,1],label='y: +up',color='#3888c9');ax.axhline(0,color='gray',lw=.5)
  for e in events:ax.axvspan(e['start'],e['end'],alpha=.14,color='green' if e['primary']['passed'] else 'red')
  ax.set_title(f"{item['polarity']} {item['direction']}: {correct}/{len(events)} direction trials");ax.grid(alpha=.15);ax.set_xlim(4,50);ax.legend(fontsize=8)
  print(folder,item['polarity'],item['direction'],correct,'/',len(events),[(np.round(e['primary']['vector'],4).tolist(),round(e['primary']['angle_error_deg'])) for e in events],flush=True)
for ax in axs[-1]:ax.set_xlabel('Saved camera time (s)')
fig.suptitle('Official CPU flow decoder on FPGA states: raw central37 mean\nShading = image-derived forward sweep; green <=45deg, red >45deg; no baseline subtraction')
fig.tight_layout();fig.savefig(O/'direction_curves.png',dpi=150)
summary=dict(status='PASS_SAVED_DIRECTION_GATE' if all(r['passed'] for r in result) else 'FAIL_SAVED_DIRECTION_GATE',criteria=json.loads((O/'PROTOCOL.json').read_text(encoding='utf-8-sig')),conditions_passed=sum(r['passed'] for r in result),conditions=8,trials_correct=sum(r['correct'] for r in result),trials=24,rounds=result,hardware_actions=0)
(O/'DIRECTION_RESULT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(summary['status'],flush=True)
