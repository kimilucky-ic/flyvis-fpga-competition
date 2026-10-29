from pathlib import Path
import os,sys,json,csv,hashlib,numpy as np
B=Path(r'C:\Users\hzy72\Documents\ChatGPT\fly');E=B/'gui_v1/evidence/central_direction_20261021';E.mkdir(exist_ok=True);os.environ['MPLCONFIGDIR']=str(E/'mpl_cache');sys.path.insert(0,str(B/'gui_v1'))
from data_store import Dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Microsoft YaHei','DejaVu Sans'];plt.rcParams['axes.unicode_minus']=False
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
config=read(B/'gui_v1/datasets.json');ds=Dataset(config['datasets'][0],B);spec=config['official_direction_metrics'];A=(B/spec['analysis_directory']).resolve();R=(B/spec['reference_directory']).resolve()
for name,pin in spec['files'].items():assert sha(A/name)==pin
assert sha(R/'activity_central_gpu.npy')==ds.hashes['activity_central.npy'];assert sha(R/'time.npy')==ds.hashes['time.npy'];assert sha(R/'cell_types.npy')==ds.hashes['cell_types.npy'];assert np.array_equal(np.load(R/'stimulus.npy'),ds.stimulus.astype(np.float32))
# Independent scalar replay of pinned official time_window/mask/clip/max definitions;
# validated against ALL 24*65 saved outputs of original official peak_responses.
start,end=-10,11;speed=19.;from_col=start*2.25/5.8;to_col=(end-1)*2.25/5.8;to_col+=2.25/5.8
lo=(abs(start*2.25/5.8)-abs(from_col))/speed;hi=lo+(to_col-from_col)/speed;mask=(ds.time>=lo)&(ds.time<=hi)
peaks=np.maximum(np.where(mask[None,:,None],ds.activity,0),0).max(axis=1)
pr=list(csv.DictReader((A/'angular_peak_responses.csv').open()));err=max(abs(peaks[int(x['sample']),ds.cells.index(x['cell_type'])]-float(x['rectified_peak'])) for x in pr);assert err<1e-12
T=[f'T{n}{l}' for n in [4,5] for l in 'abcd'];ix=[ds.cells.index(t) for t in T];ids=[next(n['network_node_index'] for n in ds.neurons if n['cell_type']==t and n['u']==0 and n['v']==0) for t in T];angles=np.arange(0,360,30);official={}
for intensity in [0,1]:
 samples=[next(c['sample'] for c in ds.conditions if c['angle']==angle and c['intensity']==intensity) for angle in angles];official[str(intensity)]=peaks[samples][:,ix].astype(np.float64)
metrics=list(csv.DictReader((A/'direction_metrics_T4_T5.csv').open()));metrics_error=0
for i,t in enumerate(T):
 denom=max(official['0'][:,i].sum(),official['1'][:,i].sum())
 for pol in [0,1]:
  v=(official[str(pol)][:,i]*np.exp(1j*np.deg2rad(angles))).sum();dsi=abs(v)/(denom+1e-15);pd=float(np.degrees(np.angle(v))%360);row=next(r for r in metrics if r['cell_type']==t and int(r['intensity'])==pol);metrics_error=max(metrics_error,abs(dsi-float(row['official_dsi'])));assert abs(((pd-float(row['preferred_direction_deg'])+180)%360)-180)<1e-8
assert metrics_error<1e-10
G=B/'gui_v1/evidence/stimuli28_gpu_20261019_r3';cfg=read(B/'gui_v1/stimuli28_results.json')
for name,pin in cfg['pins'].items():assert sha(G/name)==pin
files={f['path']:f for f in read(G/'RESULT_MANIFEST.json')['files']};nodespec=read(B/'gui_v1/spatial_registry.json')['pins']['nodes'];nodepath=Path(nodespec['path']);assert sha(nodepath)==nodespec['sha256'];nodes=list(csv.DictReader(nodepath.open()));assert ids==[int(next(n for n in nodes if n['cell_type']==t and n['u']=='0' and n['v']=='0')['global_node_index']) for t in T]
D=['RIGHT','UP','LEFT','DOWN'];CN=['右 0°','上 90°','左 180°','下 270°'];custom={};runs=[]
for pol in ['ON','OFF']:
 custom[pol]=[]
 for direction in D:
  cid=f'EDGE_{pol}_{direction}';folder=G/'conditions'/cid
  for name in ['states.npy','run.json','input_time.npy','activity_time.npy']:
   rel=f'conditions/{cid}/{name}';assert sha(G/rel)==files[rel]['sha256']
  run=read(folder/'run.json');runs.append(run);a=np.load(folder/'states.npy',mmap_mode='r')[:,ids].copy();tm=np.load(folder/'input_time.npy');w=(tm>=1)&(tm<=2);pk=np.maximum(np.where(w[:,None],a,0),0).max(0)
  custom[pol].append(dict(condition=cid,run_id=run['run_id'],trace=a,peak=pk))
for k in ['initial_raw_sha256','model_checkpoint_sha256','numeric_profile_sha256','dt_s']:assert len({r[k] for r in runs})==1
summary=dict(evidence='SAVED_GPU_STATE_ANALYSIS_NO_INFERENCE_OR_BOARD',central_ids=dict(zip(T,ids)),official24=dict(directory=str(ds.directory),source_commit=ds.identity['source_commit'],window_s=[lo,hi],window_axis='saved input-relative time; activity AFTER corresponding Euler update',window_steps=[int(np.flatnonzero(mask)[0]),int(np.flatnonzero(mask)[-1])],rectification='max(raw_activity,0), no baseline subtraction',peak_comparisons=len(pr),peak_max_abs_error=float(err),dsi_max_abs_error=float(metrics_error),metrics=metrics,peaks={k:v.tolist() for k,v in official.items()},initialization=read(R/'metadata.json')['initialization']),custom4=dict(window_input_s=[1,2],window_steps=[200,400],protocol='same clip/max statistic over full custom sweep, NOT official speed/offset dataset',initialization='ORIGINAL_BIAS_FP32; 1s fixed prestimulus',peaks={p:[x['peak'].tolist() for x in custom[p]] for p in custom},runs=[dict(condition=r['condition_id'],run_id=r['run_id'],input_sha256=r['input_raw_sha256'],initial_sha256=r['initial_raw_sha256']) for r in runs]),limitations=['Custom four directions and official12 are separate protocols/initializations','No new DSI claimed for custom4','This establishes model-relative central tuning, not biological measurement or OFF board acceptance'])
(E/'ANALYSIS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');np.savez(E/'central_traces.npz',official=ds.activity[:,:,ix],official_input_time=ds.time,official_activity_time=ds.time+.005,custom=np.array([[x['trace'] for x in custom[p]] for p in ['ON','OFF']]),custom_input_time=tm,custom_activity_time=tm+.005)
plt.style.use('dark_background');colors=['#69e4dc','#e5c95d','#ef92b5','#9ea4ff'];fig,axs=plt.subplots(2,2,figsize=(12,7))
for col,(pol,i) in enumerate([('ON',1),('OFF',5)]):
 for j,x in enumerate(custom[pol]):axs[0,col].plot(tm+.005,np.maximum(x['trace'][:,i],0),label=CN[j],color=colors[j],lw=2)
 axs[0,col].axvspan(1.005,2.005,alpha=.08,color='white');axs[0,col].set_xlim(.85,2.2);axs[0,col].set_title(f'中央{T[i]} · {pol}：四个方向的整流响应');axs[0,col].legend();axs[0,col].set_xlabel('更新后模型时间（秒）');axs[0,col].set_ylabel('max(原始状态, 0)')
 vals=[float(x['peak'][i]) for x in custom[pol]];bars=axs[1,col].bar(CN,vals,color=colors)
 for bar,v in zip(bars,vals):axs[1,col].text(bar.get_x()+bar.get_width()/2,v+.02,f'{v:.4f}',ha='center')
 axs[1,col].set_ylim(0,max(vals)*1.2);axs[1,col].set_title('仅移动窗口内取峰值；不扣基线');axs[1,col].set_ylabel('中央节点整流峰值')
fig.suptitle('最近自定义四方向真实GPU结果：中央T5b对向右暗边缘响应最强',fontsize=17);fig.tight_layout(rect=(0,.04,1,.94));fig.text(.06,.015,'只分析已有完整状态；窗口输入时间1–2秒（步200–400）；此图不是完整官方12方向协议。',fontsize=11);fig.savefig(E/'CUSTOM_CENTRAL.png',dpi=150)
fig,axs=plt.subplots(2,4,figsize=(14,7),sharex=True)
for i,t in enumerate(T):
 ax=axs.flat[i]
 for pol,color,label in [('1','#f0c767','ON亮边缘'),('0','#70dce0','OFF暗边缘')]:ax.plot(angles,official[pol][:,i],'-o',ms=3,color=color,label=label)
 ax.set_title(f'{t} · 中央节点 {ids[i]}');ax.set_xticks([0,90,180,270,330]);ax.grid(alpha=.15);ax.set_xlabel('方向（度，0°为右）');ax.set_ylabel('窗口内整流峰值')
axs[0,0].legend();fig.suptitle('已有官方MovingEdge 12方向×ON/OFF：八个中央细胞的方向响应',fontsize=17);fig.tight_layout(rect=(0,.045,1,.94));fig.text(.05,.015,'官方窗口0–0.428766秒（输入相对起点）；原始状态整流取峰值，不扣基线。既有GPU结果，无新计算。',fontsize=11);fig.savefig(E/'OFFICIAL_24_CENTRAL.png',dpi=150)
print('OFFICIAL peak check',err,'DSI',metrics_error,'window',lo,hi,'steps',np.flatnonzero(mask)[[0,-1]].tolist());print('T5b OFF 12dir',official['0'][:,5].tolist());print('custom T5b OFF',[float(x['peak'][5]) for x in custom['OFF']]);print('output',E)

