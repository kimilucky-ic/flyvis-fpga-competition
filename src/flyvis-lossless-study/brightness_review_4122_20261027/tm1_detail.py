from pathlib import Path
import json,sys,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';D=R/'pc/rounds/4122b3a1c2d2509eb5d2bcd050b886d3/records';sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
from live_protocol import Store,sha
from neuron_observer import Observer
s=Store(D,json.loads((D.parent/'session.json').read_text()));o=Observer(R/'assets/monitor.json');a=json.loads((D/'audit/RESULT.json').read_text());assert a['status']=='PASS_ALL_SAVED_STATES' and a['steps']==1012 and a['mismatch_words']==0
rows=list(csv.DictReader((O/'input_and_neuron_curves.csv').open()));t=np.array([float(r['wall_s']) for r in rows]);x=np.array([float(r['input_roi']) for r in rows]);names=['Mi1','Tm3','Tm1','Tm2'];v=np.array([[float(r[n]) for n in names] for r in rows]);cells=[];allmeans=[]
for k in range(1012):
 m,_,r=s.read(k);audit=a['rows'][k];assert sha(r.state_bits)==audit['actual_state_sha256']==audit['expected_state_sha256'] and sha(r.input_bits)==audit['input_sha256'] and audit['mismatch_words']==0
 selected=np.frombuffer(r.state_bits,'<f4')[o.ids];cells.append(selected[0,4,:].copy());allmeans.append(selected[:,4,:].mean(1,dtype=np.float64))
cells=np.array(cells);allmeans=np.array(allmeans);summary=json.loads((O/'SUMMARY.json').read_text());events=[]
for e in summary['events']:
 tt=e['wall_s'];pre=(t>=tt-1)&(t<tt-.3);post=(t>=tt)&(t<=tt+3);baseline=np.median(v[pre],axis=0);trace=v[post]-baseline
 peaks={n:dict(baseline=float(baseline[j]),max=float(v[post,j].max()),min=float(v[post,j].min()),delta_max=float(trace[:,j].max()),delta_min=float(trace[:,j].min())) for j,n in enumerate(names)}
 local=np.flatnonzero(post);kp=local[np.argmax(v[post,2])] if e['kind']=='DARKENING' else local[np.argmin(v[post,2])]
 deltas=cells[kp]-np.median(cells[pre],axis=0);ratio=abs(float(deltas.mean()))/float(np.abs(deltas).mean())
 events.append(dict(time_s=tt,kind=e['kind'],peaks_first3seconds=peaks,Tm1_peak_time_s=float(t[kp]),Tm1_cell_change=dict(positive=int((deltas>0).sum()),negative=int((deltas<0).sum()),zero=int((deltas==0).sum()),mean_over_mean_absolute=ratio,min=float(deltas.min()),max=float(deltas.max())),Tm1_region_peak_change={reg['key']:float(allmeans[kp,j]-np.median(allmeans[pre,j])) for j,reg in enumerate(o.map['regions'])}))
valid=t>=3;rangeinfo={n:dict(min=float(v[valid,j].min()),max=float(v[valid,j].max()),span=float(np.ptp(v[valid,j]))) for j,n in enumerate(names)}
# Same automatic shared axis policy as live UI includes all14classes/all displayed times.
allrows=np.array([[float(row[n]) for n in o.map['types']] for row in rows]);domain=max(.05,float(np.max(abs(allrows)))*1.08)
result=dict(status='SAVED_RECORD_ANALYSIS_COMPLETE',session=s.config['session_id'],steps=1012,state_words=1012*45669,audit_status=a['status'],mismatch_words=0,rechecked_input_and_state_hashes_all_steps=True,range_after3seconds=rangeinfo,full_record_auto_axis_equivalent=domain,Tm1_span_fraction_of_full_signed_axis=rangeinfo['Tm1']['span']/(2*domain),events=events,window_definition='before median[-1,-0.3]s; extrema[0,3]s, identical for all6input transitions; descriptive posthoc, not biological selection test',biological_pass=False,board_actions=0)
(O/'TM1_DETAIL.json').write_text(json.dumps(result,indent=2))
fig,axs=plt.subplots(3,1,figsize=(12,9),sharex=True)
axs[0].plot(t,x,color='#586779');axs[0].set_ylabel('Actual input\ncentral37 mean');axs[0].set_ylim(0,1.03)
axs[1].plot(t,v[:,2],color='#ac5b7e',label='Tm1: original saved state, expanded axis');axs[1].set_ylim(.22,.36);axs[1].set_ylabel('Tm1 model state\nzoomed vertical axis');axs[1].legend(loc='upper left')
axs[2].plot(t,v[:,3],color='#7154a5',label='Tm2: original saved state');axs[2].set_ylim(-.38,.26);axs[2].set_ylabel('Tm2 model state');axs[2].legend(loc='upper left')
for ax in axs:
 ax.grid(alpha=.2);ax.set_xlim(3,60)
 for e in events:ax.axvline(e['time_s'],color='#d58d23' if e['kind']=='BRIGHTENING' else '#5078ab',alpha=.4,lw=1)
axs[2].set_xlabel('Capture wall time (s); model dt =5 ms/step, not wall-time biological latency')
fig.suptitle('Tm1 has repeatable small changes; no state values rescaled\nSeparate vertical axes for visibility: curve heights are NOT cross-type amplitude comparisons')
fig.tight_layout();fig.savefig(O/'tm1_focus.png',dpi=150);plt.close(fig)
print(json.dumps(dict(range_after3s=rangeinfo,shared_axis=domain,tm1_axis_fraction=result['Tm1_span_fraction_of_full_signed_axis'],events=[dict(time=e['time_s'],kind=e['kind'],Tm1=e['peaks_first3seconds']['Tm1'],Tm2=e['peaks_first3seconds']['Tm2'],cells=e['Tm1_cell_change']) for e in events]),indent=2))
files=['SUMMARY.json','TM1_DETAIL.json','input_and_neuron_curves.csv','tm1_focus.png','brightness_response.png','camera_samples.png']
(O/'SHA256.json').write_text(json.dumps({f:sha((O/f).read_bytes()) for f in files},indent=2))
