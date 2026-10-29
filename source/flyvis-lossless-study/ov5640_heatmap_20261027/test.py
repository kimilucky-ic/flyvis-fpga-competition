from pathlib import Path
import sys,json,time,base64,hashlib,importlib.util,csv
import numpy as np
O=Path('flyvis-lossless-study/ov5640_heatmap_20261027').resolve();R=O.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
from live_server import App
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];D=R/'pc/rounds'/sid;config=json.loads((D/'session.json').read_text());app=App(config,D/'records');assert app.audit_result['status']=='PASS_ALL_SAVED_STATES';assert app.store.camera_close['status']=='CLOSED'
spec=importlib.util.spec_from_file_location('previous_server',O/'before/pc/live_server.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);old.P=R;previous=old.App(config,D/'records')
nodes=list(csv.DictReader(open('C:/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1/structure/nodes.csv')));types=app.observer.map['types'];packets=[];timings=[];oldtimes=[];checks=0
for k in [0,1,25,100,200,300,500,700,850,969]:
 m,src,r=app.store.read(k);states=np.frombuffer(r.state_bits,'<f4');t=time.perf_counter();p=app.packet(k);timings.append((time.perf_counter()-t)*1000);t=time.perf_counter();q=previous.packet(k);oldtimes.append((time.perf_counter()-t)*1000)
 raw=base64.b64decode(p['heatmap']['values_b64']);assert len(raw)==40376;assert hashlib.sha256(raw).hexdigest()==p['heatmap']['values_sha256'];v=np.frombuffer(raw,'<f4').reshape(14,721)
 for j,name in enumerate(types):
  expected=[int(n['node_index']) for n in nodes if n['cell_type']==name];assert np.array_equal(v[j].view('u4'),states[expected].view('u4'));assert [(nodes[i]['u'],nodes[i]['v']) for i in expected]==[(n['u'],n['v']) for n in nodes[:721]];checks+=721
 rest=dict(p);rest.pop('heatmap');assert rest==q
 packets.append(p)
for bits in [b'bad',np.full(45669,np.nan,dtype='<f4').tobytes()]:
 try:app.observer.heatmap(bits,'0'*64,0)
 except ValueError:pass
 else:raise AssertionError('invalid values accepted')
_,_,r=app.store.read(969);ts=[]
for _ in range(100):
 t=time.perf_counter();app.observer.heatmap(r.state_bits,'0'*64,969);ts.append((time.perf_counter()-t)*1000)
(O/'packets.json').write_text(json.dumps(packets),encoding='utf-8')
result=dict(status='PASS_CPU_SAVED_RECORDS',session_id=sid,records=len(packets),exact_spatial_words=checks,existing_packet_fields_unchanged=True,geometry_all14_matches_input=True,invalid_size_and_nan_rejected=True,heatmap_mean_ms=float(np.mean(ts)),heatmap_p95_ms=float(np.percentile(ts,95)),new_display_mean_ms=float(np.mean(timings)),old_display_mean_ms=float(np.mean(oldtimes)),display_benchmark_note='Sequential saved-file CPU measurements, including cold reads; not board timing',extra_packet_bytes=len(json.dumps(packets[-1]['heatmap'])),new_cache_entries=len(app.display_cache),hardware_actions=0)
(O/'CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
