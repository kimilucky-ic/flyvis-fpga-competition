from pathlib import Path
import sys,json,numpy as np,hashlib
B=Path(r'C:/Users/hzy72/Documents/ChatGPT/fly');sys.path.insert(0,str(B/'gui_v1'));from spatial_state import SpatialRegistry
r=SpatialRegistry();G=B/'gui_v1/evidence/stimuli28_gpu_20261019_r3';E=B/'gui_v1/evidence/central_roi_20261021';files={x['path']:x['sha256'] for x in json.loads((G/'RESULT_MANIFEST.json').read_text())['files']};out={'regions':{},'conditions':{}}
for radius in [2,3,4]:
 indices=[[i for i,n in enumerate(r.nodes) if n['type']==t and max(abs(n['u']),abs(n['v']),abs(n['u']+n['v']))<=radius] for t in r.data['types']]
 out['regions'][radius]={'count':len(indices[0]),'indices':indices,'global_ids':[r.ids[x].tolist() for x in indices],'radius':radius,'map_sha256':r.digest}
for pol in ['ON','OFF']:
 for direction in ['RIGHT','UP','LEFT','DOWN']:
  name=f'EDGE_{pol}_{direction}';p=G/'conditions'/name/'states.npy';assert hashlib.sha256(p.read_bytes()).hexdigest()==files[f'conditions/{name}/states.npy'];a=np.load(p,mmap_mode='r')[:,r.ids];info={}
  for radius,reg in out['regions'].items():
   means=np.array([a[:,ix].astype(np.float64).mean(1) for ix in reg['indices']]).T;v=np.maximum(means,0);peaks=v[200:401].max(0);b=1 if pol=='ON' else 5;pk=peaks[b];half=np.flatnonzero(v[200:401,b]>=pk/2) if pk>0 else []
   info[radius]={'peaks':peaks.tolist(),'target_half_peak_steps':len(half)}
  out['conditions'][name]=info
(E/'ROI_COMPARISON.json').write_text(json.dumps(out,indent=2));print({name:{r:(v['peaks'][1 if '_ON_'in name else 5],v['target_half_peak_steps']) for r,v in info.items()} for name,info in out['conditions'].items()})
