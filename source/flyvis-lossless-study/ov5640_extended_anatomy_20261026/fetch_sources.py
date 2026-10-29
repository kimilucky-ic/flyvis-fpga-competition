from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,datetime
O=Path(__file__).resolve().parent;S=O/'source';S.mkdir(exist_ok=True)
BASE='https://storage.googleapis.com/flyem-optic-lobe/v1.1/segmentation/'
def fetch(url,path):
 with urllib.request.urlopen(url,timeout=35) as r:
  data=r.read(8*1024*1024+1);assert len(data)<=8*1024*1024
 path.write_bytes(data)
 return dict(url=url,path=str(path.relative_to(O)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
meta=fetch(BASE+'segment_properties/info',S/'segment_properties.json');d=json.loads((S/'segment_properties.json').read_text())['inline'];types=next(p['values'] for p in d['properties'] if p['id']=='type')
selected=[dict(type=t,body_id=next(i for i,n in zip(d['ids'],types) if n==t),selection='First official v1.1 type entry, representative anatomy only, not a FlyVis computational-cell match') for t in ['L1','L2','Mi1','Tm3','Tm1','Tm2']]
tasks=[]
for item in selected:
 id=item['body_id'];tasks.extend([(BASE+'skeletons-swc/'+id+'.swc',S/(id+'.swc')),(BASE+'skeletons-precomputed/'+id,S/(id+'.bin'))])
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:logs=list(ex.map(lambda x:fetch(*x),tasks))
(S/'selection.json').write_text(json.dumps(selected,indent=2));(O/'DOWNLOADS.json').write_text(json.dumps([meta]+logs,indent=2));print('Downloaded 6 type-verified SWCs and their independent precomputed counterparts:',[(x['type'],x['body_id']) for x in selected])
