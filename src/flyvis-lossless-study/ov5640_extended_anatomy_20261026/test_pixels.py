from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';ref=np.load(O/'render_reference.npz');h=json.loads((R/'assets/projection.json').read_text());test=json.loads((O/'RENDER_TEST.json').read_text());results=[]
f=np.float32
for i,(mode,receipt) in enumerate(zip(test['modes'],test['receipts'])):
 out=ref['background'][:,:,:3].astype('float32').copy();mask=ref['masks']
 for k in h['fixed_cpu_projection']['painter_order']:
  if not mode['visible'][k]:continue
  color=h['color_encoding']['palette'][receipt['types'][k]];brightness=receipt['brightness'][k];c=np.array([f(f(int(color[j:j+2],16)/255*brightness)*255) for j in [1,3,5]],dtype='float32');alpha=mask[k][:,:,None]
  out=f(f(out*f(1-alpha))+f(alpha*c))
 rgba=np.empty((480,960,4),dtype=np.uint8);rgba[:,:,:3]=np.clip(np.floor(f(out+.5)),0,255).astype(np.uint8);rgba[:,:,3]=ref['background'][:,:,3]
 actual=np.frombuffer((O/f'case{i}.rgba').read_bytes(),dtype=np.uint8).reshape(480,960,4);assert np.array_equal(actual,rgba),i
 if i==2:assert np.array_equal(actual,ref['background'])
 Image.fromarray(actual).save(O/f'CPU_case{i}.png');results.append(dict(case=i,pixel_bytes=actual.size,mismatch_bytes=0,sha256=hashlib.sha256(actual.tobytes()).hexdigest()))
(O/'PIXEL_CHECK.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_CPU_PIXEL_COMPARISON',cases=results,all_hidden_restores_background_exactly=True,board_actions=0),indent=2));print('PASS independent NumPy composition:3cases,all5529600RGBAbytes identical; hiding all restores original transformed background')
