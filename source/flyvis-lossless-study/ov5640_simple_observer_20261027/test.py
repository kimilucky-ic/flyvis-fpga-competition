from pathlib import Path
import json,sys,csv,hashlib,time,importlib.util
O=Path('flyvis-lossless-study/ov5640_simple_observer_20261027').resolve();R=O.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
import numpy as np
from live_server import App
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];D=R/'pc/rounds'/sid
app=App(json.loads((D/'session.json').read_text()),D/'records');assert app.audit_result['status']=='PASS_ALL_SAVED_STATES' and not app.audit_running
rows=list(csv.DictReader(open('C:/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1/structure/nodes.csv')))
spec=importlib.util.spec_from_file_location('old_observer',O/'before/pc/neuron_observer.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);old=mod.Observer(O/'before/assets/monitor.json')
packets=[];times=[];err=0
for k in [0,1,25,100,250,500,750,1011]:
 m,_,r=app.store.read(k);values=np.frombuffer(r.state_bits,'<f4');t=time.perf_counter();out=app.observer.means(r.state_bits);times.append((time.perf_counter()-t)*1000)
 assert out[0]==old.means(r.state_bits)[0]
 for j,name in enumerate(app.observer.map['types']):
  ids=[int(x['node_index']) for x in rows if x['cell_type']==name];assert len(ids)==721
  exact=sum(float(values[i]) for i in ids)/721;err=max(err,abs(exact-out[1][j]));assert abs(exact-out[1][j])<1e-12
 packets.append(app.packet(k))
for bad in [b'bad',np.full(45669,np.nan,dtype='<f4').tobytes()]:
 try:app.observer.means(bad)
 except ValueError:pass
 else:raise AssertionError('bad state accepted')
(O/'packets.json').write_text(json.dumps(packets),encoding='utf-8');(O/'CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_PC_SAVED_RECORDS',records=8,central37_exact_previous=True,all721_scalar_max_error=err,all721_values_checked=112,mean_extraction_ms=sum(times)/len(times),timing_scope='PC_ONLY_NOT_ARM',nonfinite_rejected=True,board_actions=0),indent=2))
print((O/'CPU_RESULT.json').read_text())
