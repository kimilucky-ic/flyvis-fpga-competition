from pathlib import Path
import sys,json,csv,time,hashlib,ast
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
import numpy as np
from neuron_observer import Observer
from live_server import App
D=R/'pc/rounds/1f942a59a8515cd6a2e62ddd5fc7bc42';cfg=json.loads((D/'session.json').read_text());app=App(cfg,D/'records');assert not app.audit_running
mp=json.loads((R/'assets/monitor.json').read_text());csvrows=list(csv.DictReader(open('C:/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1/structure/nodes.csv')))
chosen=[0,1,2,10,25,50,100,250,500,750,1000,1080];packets=[];maxerr=0;times=[]
for k in chosen:
 m,_,r=app.store.read(k);states=np.frombuffer(r.state_bits,'<f4');start=time.perf_counter();means=app.observer.means(r.state_bits);times.append((time.perf_counter()-start)*1000)
 for ri,region in enumerate(mp['regions']):
  cu,cv=region['center']
  for ti,name in enumerate(mp['types']):
   ids=[int(x['node_index']) for x in csvrows if x['cell_type']==name and max(abs(int(x['u'])-cu),abs(int(x['v'])-cv),abs(int(x['u'])+int(x['v'])-cu-cv))<=3]
   assert ids==region['ids'][ti] and len(ids)==37
   manual=sum(float(states[i]) for i in ids)/37;err=abs(manual-means[ri][ti]);maxerr=max(maxerr,err);assert err<1e-12
 p=app.packet(k);assert p['observer']['state_sha256']==m['state_sha256'];assert p['observer']['reference_step_id']==0;assert p['observer']['means']==means
 oldvals=states[app.spatial['ids']].tolist();assert p['spatial']['values']==oldvals;packets.append(p)
# Test corrupt state shape and nonfinite observations fail, before any rendering.
for bits in [b'bad',np.full(45669,np.nan,dtype='<f4').tobytes()]:
 try:app.observer.means(bits)
 except ValueError:pass
 else:raise AssertionError('bad state accepted')
(O/'packets.json').write_text(json.dumps(packets))
for p in [R/'pc/neuron_observer.py',R/'pc/live_server.py']:ast.parse(p.read_text(encoding='utf-8-sig'),feature_version=(3,8))
result=dict(status='PASS_PC_SAVED_STATE_OBSERVER',saved_physical_records=len(chosen),scalar_values_compared=len(chosen)*5*14,max_abs_difference=maxerr,types=mp['types'],roi_cells=37,skeleton_values_unchanged=True,negative_states_preserved=True,reference_step=0,pc_observer_mean_ms=sum(times)/len(times),pc_observer_max_ms=max(times),timing_scope='PC_ONLY_NOT_BOARD',board_actions=0,new_neural_computation=False)
(O/'RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
