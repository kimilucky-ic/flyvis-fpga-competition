import json,pathlib,hashlib,numpy as np,csv
b=pathlib.Path(r'C:/Users/hzy72/Documents/ChatGPT/fly/gui_v1');config=json.loads((b/'stimuli28_results.json').read_text());g=pathlib.Path(config['root']);manifest=json.loads((g/'RESULT_MANIFEST.json').read_text());pins={r['path']:r['sha256'] for r in manifest['files']};folder=g/'conditions/EDGE_ON_RIGHT';run=json.loads((folder/'run.json').read_text());p=b/'runtime/line11_live_camera/da31181aa303477ab0a6f8e113f4c698';fin=json.loads((p/'WINDOW_FINISH.json').read_text());checks={name:hashlib.sha256((g/name).read_bytes()).hexdigest()==v for name,v in config['pins'].items()}
for n in ['input','states','flow']:
 rel='conditions/EDGE_ON_RIGHT/'+n+'.npy';checks[rel]=hashlib.sha256((g/rel).read_bytes()).hexdigest()==pins[rel]
assert all(checks.values());assert run['input_raw_sha256']==fin['scientific_input']['input_raw_sha256'];assert run['initial_raw_sha256']==fin['scientific_input']['initial_raw_sha256']
S=np.load(folder/'states.npy',mmap_mode='r');F=np.load(folder/'flow.npy');X=np.load(folder/'input.npy');ps=[];pf=[];px=[]
for k in range(485):
 q=p/'official_flow'/('%06d'%k);m=json.loads(q.with_suffix('.json').read_text());vals=[]
 for suf,key in [('.state.bin','full_state_sha256'),('.flow.bin','flow_sha256'),('.input.bin','input_sha256')]:
  data=q.with_suffix(suf).read_bytes();assert hashlib.sha256(data).hexdigest()==m[key];vals.append(np.frombuffer(data,dtype='<f4'))
 ps.append(vals[0]);pf.append(vals[1].reshape(2,721));px.append(vals[2])
ps=np.array(ps);pf=np.array(pf);px=np.array(px)
coords=list(csv.DictReader(open('flyvis-circuit-selection/controlled_stimuli_20261019_v1/coordinates.csv')));row=np.array([float(r['source_row_418']) for r in coords]);col=np.array([float(r['source_col_418']) for r in coords]);cross=[]
for i in range(721):
 j=np.flatnonzero((X[:-1,i]<.5)&(X[1:,i]>=.5));
 if len(j):cross.append([col[i],row[i],float(j[0]+1)])
cs=np.array(cross);coef=np.linalg.lstsq(np.column_stack([cs[:,0],cs[:,1],np.ones(len(cs))]),cs[:,2],rcond=None)[0]
out=dict(run=p.name,gpu_run=run['run_id'],file_checks=checks,same_input_bits=bool(np.array_equal(X,px)),same_initial=run['initial_raw_sha256'],model_checkpoint=run['model_checkpoint_sha256'],state_max_abs=float(np.max(np.abs(S-ps))),state_allclose_1e5=bool(np.allclose(S,ps,atol=1e-5,rtol=1e-5)),flow_max_abs=float(np.max(np.abs(F-pf))),flow_allclose_1e5=bool(np.allclose(F,pf,atol=1e-5,rtol=1e-5)),input_half_crossing_fit_step_per_source_xy=coef.tolist(),input_crossings=len(cs),samples=[])
for k in [285,300,315,330,350,484]:
 def val(z):
  v=z[k,:,360];return dict(x=float(v[0]),y=float(v[1]),magnitude=float(np.linalg.norm(v)),angle_deg=float(np.degrees(np.arctan2(v[1],v[0]))%360))
 out['samples'].append(dict(step=k,GPU=val(F),PL_received=val(pf)))
(b/'evidence/flow_explanation_20261022/COMPARISON.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
