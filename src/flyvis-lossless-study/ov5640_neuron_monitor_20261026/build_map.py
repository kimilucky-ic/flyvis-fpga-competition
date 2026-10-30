from pathlib import Path
import json,csv,hashlib,shutil
R=Path('flyvis-lossless-study/ov5640_live_v261_20261026');O=R.parent/'ov5640_neuron_monitor_20261026';O.mkdir(exist_ok=False)
for rel in ['assets/index.html','assets/ui.js','pc/live_server.py','FINAL_MANIFEST_SHA256.json']:
 q=O/'before'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,q)
F=Path('C:/Users/hzy72/Documents/ChatGPT/fly');nodes=F/'artifacts/golden_reference_v1/structure/nodes.csv';graph=F/'upstream/flyvis/flyvis/connectome/fib25-fib19_v2.2.json'
inv=json.loads((R.parent/'runs/acceptance800_20261013/source_inventory.json').read_text())
for p in [nodes,graph]:assert hashlib.sha256(p.read_bytes()).hexdigest()==inv[str(p)]['sha256']
rows=[(int(r['node_index']),r['cell_type'],int(r['u']),int(r['v'])) for r in csv.DictReader(nodes.open())];spec=json.loads(graph.read_text());expected=[]
for n in spec['nodes']:
 pattern,(su,sv)=n['pattern'];assert pattern=='stride'
 for u in range(-15,16):
  for v in range(-15,16):
   if abs(u+v)<=15 and u%su==0 and v%sv==0:expected.append((len(expected),n['name'],u,v))
assert rows==expected and len(rows)==45669
names=['L1','L2','Mi1','Tm3','Tm1','Tm2','T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
regions=[]
for key,label,cu,cv in [('center','中央',0,0),('left','左侧',3,-6),('right','右侧',-3,6),('top','上方',-6,0),('bottom','下方',6,0)]:
 mask=lambda u,v:max(abs(u-cu),abs(v-cv),abs(u+v-cu-cv))<=3
 ids=[[i for i,t,u,v in rows if t==name and mask(u,v)] for name in names];assert all(len(x)==37 for x in ids)
 receptors=[(i,u,v) for i,t,u,v in rows if t=='R1' and mask(u,v)]
 regions.append(dict(key=key,label=label,center=[cu,cv],ids=ids,receptor_ids=[i for i,u,v in receptors],pixels=[[13*v+208,int(13*(u+v/2))+208] for i,u,v in receptors]))
sp=json.loads((R/'assets/spatial.json').read_text());offsets=[270,271,272,273,298,299,300,301,302,327,328,329,330,331,332,357,358,359,360,361,362,363,388,389,390,391,392,393,418,419,420,421,422,447,448,449,450]
assert regions[0]['ids'][6:]==[[sp['ids'][k*721+j] for j in offsets] for k in range(8)]
m=dict(schema='line11-observer-map/v1',types=names,regions=regions,count=37,graph_sha256=hashlib.sha256(graph.read_bytes()).hexdigest(),nodes_sha256=hashlib.sha256(nodes.read_bytes()).hexdigest(),state_count=45669,aggregation='SIGNED_MEAN_FLOAT64_DISPLAY_ONLY',units='model_state_not_calibrated_mV',reference='first_completed_step_not_assumed_resting_baseline')
(R/'assets/monitor.json').write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')),encoding='utf-8');digest=hashlib.sha256((R/'assets/monitor.json').read_bytes()).hexdigest()
(O/'MAP_CHECK.json').write_text(json.dumps(dict(status='PASS_PINNED_NODE_IDENTITY',all_nodes_matched=45669,types=names,regions=5,each_count=37,map_sha256=digest,central_ids={n:next(i for i,t,u,v in rows if t==n and u==v==0) for n in names}),indent=2))
print('Verified all45669 node IDs against accepted CSV and pinned graph; five spatially matched37cell ROIs; map',digest)
