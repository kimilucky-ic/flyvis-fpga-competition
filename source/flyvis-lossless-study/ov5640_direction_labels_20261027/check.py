from pathlib import Path
import ast,json,hashlib,sys
import numpy as np
from PIL import Image
O=Path('flyvis-lossless-study/ov5640_direction_labels_20261027');O.mkdir(exist_ok=True)
R=O.parent/'ov5640_live_v261_20261026';U=Path('C:/Users/hzy72/Documents/ChatGPT/fly/upstream/flyvis/flyvis')
gt=U/'utils/groundtruth_utils.py';tree=ast.parse(gt.read_text());pd=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='preferred_directions' for t in n.targets))
utils=U/'datasets/rendering/utils.py';tree=ast.parse(utils.read_text());funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rotate_image','render_bars_cartesian']];ns={'np':np,'Image':Image};exec(compile(ast.Module(body=funcs,type_ignores=[]),str(utils),'exec'),ns)
sys.path.insert(0,str(R/'bundle'));from direct_input import DirectAreaInput
from ps_input import receptor_centers
mapper=DirectAreaInput();xy=receptor_centers()[:,::-1].astype(float);records=[]
for subtype,angle,expected in [('a',180,[-1,0]),('b',0,[1,0]),('c',90,[0,-1]),('d',270,[0,1])]:
 assert pd['T4'+subtype]==pd['T5'+subtype]==angle
 raw=[];mapped=[]
 for col in [31,49]:
  im=ns['render_bars_cartesian'](48,80,3,9,col,24,1,1.,0.,angle)
  yy,xx=np.indices(im.shape);raw.append([float((xx*im).sum()/im.sum()),float((yy*im).sum()/im.sum())])
  frame=np.repeat(np.rint(im*255).astype(np.uint8)[...,None],3,axis=2);v=mapper.render(frame);mapped.append((xy*v[:,None]).sum(axis=0)/v.sum())
 delta=np.subtract(mapped[1],mapped[0]);rd=np.subtract(raw[1],raw[0]);main=0 if expected[0] else 1;cross=1-main
 assert delta[main]*expected[main]>100 and abs(delta[cross])<5,(subtype,delta)
 assert rd[main]*expected[main]>10 and abs(rd[cross])<2
 records.append(dict(subtype=subtype,official_degrees=angle,screen_direction=['left','right','up','down']['abcd'.index(subtype)],raw_pixel_delta=rd.tolist(),display_721_centroid_delta=delta.tolist()))
files=[gt,utils,U/'datasets/rendering/eye.py',U/'datasets/moving_bar.py',R/'bundle/direct_input.py',R/'bundle/ps_input.py',R/'pc/live_server.py']
result=dict(status='PASS_CPU_INPUT_COORDINATE_MAPPING',evidence='OFFICIAL_REFERENCE_PLUS_CPU_GEOMETRY_NOT_NEURAL_TUNING_TEST',records=records,files={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},hardware_actions=0,neural_steps=0,orientation_scope='Directions of motion visible in the GUI input image; not operator body coordinates')
(O/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(records,indent=2))
