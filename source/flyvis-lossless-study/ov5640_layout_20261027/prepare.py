from pathlib import Path
import json
O=Path(__file__).resolve().parent;S=O.parent/'ov5640_extended_anatomy_20261026'
s=(S/'build_projection.py').read_text('utf-8')
s=s.replace("O/'source/selection.json'","S/'source/selection.json'").replace("O/'source'","S/'source'")
s=s.replace("O=Path(__file__).resolve().parent;", "O=Path(__file__).resolve().parent;S=O.parent/'ov5640_extended_anatomy_20261026';")
# Existing14types already accepted: take existing identities, no duplicate selection.
a=s.index('selection=json.loads');b=s.index('geometry=[]',a)
s=s[:a]+"selection=old['types']\n"+s[b:]
s=s.replace('ident.append(dict(**item,swc_sha256=digest,','ident.append(dict(item,swc_sha256=digest,')
a=s.index('allxy=np.concatenate');b=s.index('masks=[]',a)
s=s[:a]+'''import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import PolyCollection
meshes=[];sources=[]
for name,color in [('ME(R)','#70b0cf'),('LO(R)','#c3a2c8'),('LOP(R)','#cabc7d')]:
 p=A/'data/roi'/f'{name}.ngmesh';raw=p.read_bytes();n=struct.unpack_from('<I',raw)[0]
 xyz=np.frombuffer(raw,dtype='<f4',count=n*3,offset=4).reshape(-1,3).astype(float)/1000
 faces=np.frombuffer(raw,dtype='<u4',offset=4+n*12).reshape(-1,3);assert faces.max()<n
 clip=np.c_[xyz,np.ones(len(xyz))]@mat.T;assert (clip[:,3]>0).all();ndc=clip[:,:3]/clip[:,3,None]
 xy=np.c_[(ndc[:,0]+1)*480,(1-ndc[:,1])*240];meshes.append((name,xy,ndc[:,2],faces,color));sources.append(dict(name=name,path=str(p),sha256=hashlib.sha256(raw).hexdigest(),vertices=n,faces=len(faces)))
allxy=np.concatenate([x[1] for x in geometry]+[x[1] for x in meshes]);lo=allxy.min(0);hi=allxy.max(0);scale=min(584/(hi-lo)[0],544/(hi-lo)[1]);offset=np.array([320,300])-(hi+lo)/2*scale
fig=Figure(figsize=(6.4,6),dpi=100,facecolor='#0b1823');canvas=FigureCanvasAgg(fig);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,640);ax.set_ylim(600,0);ax.set_axis_off()
for name,xy,z,faces,color in sorted(meshes,key=lambda m:float(m[2].mean()),reverse=True):
 xy=xy*scale+offset;assert ((xy>=20)&(xy<np.array([640,600])-20)).all();order=np.argsort(z[faces].mean(1))[::-1]
 ax.add_collection(PolyCollection(xy[faces[order]],facecolors=color,edgecolors='none',alpha=.055,rasterized=True))
canvas.draw();background=np.asarray(canvas.buffer_rgba()).copy()
''' +s[b:]
s=s.replace("bg=np.array(Image.open(F/'fixed_background.png').convert('RGBA'));assert hashlib.sha256(bg.tobytes()).hexdigest()==old['background_sha256']",'bg=None')
s=s.replace('[960,480]','[640,600]').replace('(1920,960)','(1280,1200)').replace('(960,480)','(640,600)').replace('width=960,height=480','width=640,height=600')
s=s.replace("viewport=h['viewport']","viewport=dict(width=640,height=600,pixel_ratio=1)")
s=s.replace("palette=dict(zip([x['type'] for x in selection],['#e4c071','#71c9ed','#76ddba','#a8e0b4','#e1a4be','#c8a8e2']+[h['color_encoding']['palette'][x['type']] for x in old['types']]))","palette=h['color_encoding']['palette']")
s=s.replace("idsha=hashlib", "identity.update(background_meshes=sources,background_semantics='Complete right ME/LO/LOP source meshes, not whole brain',full_anatomy_bounds_px=[(lo*scale+offset).tolist(),(hi*scale+offset).tolist()],background_renderer='CPU Agg complete triangle projection')\nidsha=hashlib")
s=s.replace("dict(**item,swc_sha256", "dict(item,swc_sha256")
(O/'build_projection.py').write_text(s,encoding='utf-8')
