from pathlib import Path
import numpy as np,json,struct,hashlib,shutil
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';A=Path('C:/Users/hzy72/Documents/ChatGPT/fly/flyvis-3d-studio/anatomy_trial_20261013');F=Path('C:/Users/hzy72/Documents/ChatGPT/fly/flyvis-3d-studio/activity_replay_20261014/live_canvas_cpu_20261015/evidence/gui_ff14862183fc423a90b55eb9e276a706/fixed_projection')
for rel in ['assets/projection.json','assets/projection.bin','assets/fixed_skeleton.js','assets/ui.js','assets/index.html','assets/monitor.js','FINAL_MANIFEST_SHA256.json']:
 p=O/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise RuntimeError('backup exists')
 shutil.copy2(R/rel,p)
h=json.loads((R/'assets/projection.json').read_text());old=h['fixed_cpu_projection'];mat=np.array(old['camera_matrix']);bg=np.array(Image.open(F/'fixed_background.png').convert('RGBA'));assert hashlib.sha256(bg.tobytes()).hexdigest()==old['background_sha256']
selection=json.loads((O/'source/selection.json').read_text())+[dict(type=t['type'],body_id=t['body_id'],selection='Previously accepted representative body') for t in old['types']]
geometry=[]
for item in selection:
 id=item['body_id'];p=O/'source'/f'{id}.swc' if (O/'source'/f'{id}.swc').exists() else A/'data/swc'/f'{id}.swc';data=p.read_bytes();raw=np.loadtxt(p);lookup={int(x[0]):i for i,x in enumerate(raw)};pairs=[(i,lookup[int(row[6])]) for i,row in enumerate(raw) if row[6]!=-1]
 xyz=raw[:,2:5]*.008;clip=np.c_[xyz,np.ones(len(xyz))]@mat.T;ndc=clip[:,:3]/clip[:,3,None];xy=np.c_[(ndc[:,0]+1)*480,(1-ndc[:,1])*240];geometry.append((item,xy,pairs,float(ndc[:,2].mean()),hashlib.sha256(data).hexdigest()))
allxy=np.concatenate([x[1] for x in geometry]);lo=allxy.min(0);hi=allxy.max(0);scale=min(864/(hi-lo)[0],408/(hi-lo)[1]);offset=np.array([480,240])-(hi+lo)/2*scale
# Same camera for all shapes and the retained background, one uniform screen-space zoom/pan.
bg2=Image.fromarray(bg).transform((960,480),Image.Transform.AFFINE,(1/scale,0,-offset[0]/scale,0,1/scale,-offset[1]/scale),resample=Image.Resampling.BICUBIC,fillcolor=tuple(bg[0,0]));background=np.array(bg2)
masks=[];ident=[];depth=[]
for item,xy,pairs,z,digest in geometry:
 xy=xy*scale+offset;assert ((xy>=0)&(xy<[960,480])).all()
 im=Image.new('L',(1920,960));dr=ImageDraw.Draw(im)
 for a,b in pairs:dr.line([tuple(xy[a]*2),tuple(xy[b]*2)],fill=255,width=5)
 mask=np.asarray(im.resize((960,480),Image.Resampling.LANCZOS),dtype=np.float32)/255;masks.append(mask);depth.append(z)
 ident.append(dict(**item,swc_sha256=digest,nodes=len(xy),edges=len(pairs),mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest(),bounds_px=[xy.min(0).tolist(),xy.max(0).tolist()],clipped_nodes=0))
identity=dict(schema='line11.extended_fixed_anatomy/v1',width=960,height=480,types=ident,camera_matrix=mat.tolist(),view_scale=float(scale),view_offset=offset.tolist(),original_background_sha256=old['background_sha256'],background_sha256=hashlib.sha256(background.tobytes()).hexdigest(),units='um; SWC coordinate multiplied by0.008',attribution='Janelia FlyEM Optic Lobe v1.1 / CC-BY; representative morphology, NOT FlyVis node-to-body identity',source='https://www.janelia.org/project-team/flyem/optic-lobe',neural_values_generated=False,occlusion_policy='fixed per-type mean-depth painter order; display projection, not full per-pixel3D depth',painter_order=np.argsort(depth)[::-1].tolist())
idsha=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest();arrays=[];payload=[];offsetb=0
for name,value in [('base',background[:,:,:3].astype('<f4')),('alpha',background[:,:,3])]:
 data=np.ascontiguousarray(value).tobytes();arrays.append(dict(name=name,offset=offsetb,length=len(data),shape=list(value.shape),dtype=value.dtype.str));payload.append(data);offsetb+=len(data)
boxes=[]
for i,mask in enumerate(masks):
 y,x=np.nonzero(mask);y0,y1,x0,x1=int(y.min()),int(y.max()+1),int(x.min()),int(x.max()+1);value=mask[y0:y1,x0:x1].astype('<f4');boxes.append([y0,y1,x0,x1]);data=value.tobytes();arrays.append(dict(name='weight'+str(i),offset=offsetb,length=len(data),shape=list(value.shape),dtype=value.dtype.str));payload.append(data);offsetb+=len(data)
data=b''.join(payload);header=json.dumps(dict(schema='flyvis-fixed-cpu-cache/v2',projection_sha256=idsha,width=960,height=480,boxes=boxes,arrays=arrays,payload_sha256=hashlib.sha256(data).hexdigest()),separators=(',',':')).encode();wire=struct.pack('<I',len(header))+header+data
(R/'assets/projection.bin').write_bytes(wire)
palette=dict(zip([x['type'] for x in selection],['#e4c071','#71c9ed','#76ddba','#a8e0b4','#e1a4be','#c8a8e2']+[h['color_encoding']['palette'][x['type']] for x in old['types']]))
new=dict(schema='line11.extended_projection_health/v1',viewport=h['viewport'],expected_binding=dict(types=[x['type'] for x in selection],observer_map_sha256='4282f4524df248aa27a313768813fe2062c6d4f3633db4470e5d6c1291360dc8'),fixed_cpu_projection=identity,fixed_cpu_projection_sha256=idsha,projection_cache=dict(url='/api/competition-live/cache',sha256=hashlib.sha256(wire).hexdigest(),bytes=len(wire)),color_encoding=dict(palette=palette,intensity_domain=[0,2],brightness_floor=.18,brightness_exponent=.35,formula='.18+.82*min(abs(selected_signed_mean)/2,1)^.35',sign_semantics='brightness encodes absolute magnitude; signed values shown in label and curves'),geometry_rebuilt_per_frame=False,renderer_computes_neurons=False)
(R/'assets/projection.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8');(O/'BUILD_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ANATOMY_BUILD',types=len(ident),nodes=sum(x['nodes'] for x in ident),clipped_nodes=0,bytes=len(wire),view_scale=float(scale),all_coordinates_common_transform=True,source='Official v1.1 six newSWCs, same8previousSWCs; no synthetic morphology',board_actions=0),indent=2));np.savez_compressed(O/'render_reference.npz',background=background,masks=np.array(masks));print('CPU cache built',len(wire),'bytes;14types;',sum(x['nodes'] for x in ident),'nodes;0clipped')
