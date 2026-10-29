from pathlib import Path
import json,hashlib,numpy as np,os
b=Path(r'C:\Users\hzy72\Documents\ChatGPT\fly');e=b/'gui_v1/evidence/on_off_right_compare_20261021';e.mkdir(exist_ok=True);os.environ['MPLCONFIGDIR']=str(e/'mpl_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Microsoft YaHei','DejaVu Sans'];plt.rcParams['axes.unicode_minus']=False
r=b/'gui_v1/evidence/stimuli28_gpu_20261019_r3';config=json.loads((b/'gui_v1/stimuli28_results.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in config['pins'].items():assert sha(r/name)==pin
manifest=json.loads((r/'RESULT_MANIFEST.json').read_text());entries={f['path']:f for f in manifest['files']};acc=json.loads((r/'ACCEPTANCE.json').read_text());assert acc['status']=='PASS_ACTUAL_GPU_DATA_AND_TARGETED_NUMERICAL_AUDIT'
ids=np.load(r/'T4T5_global_ids.npy');assert sha(r/'T4T5_global_ids.npy')==entries['T4T5_global_ids.npy']['sha256']
data={};identities=[];verified=[]
for pol in ['ON','OFF']:
 for suffix in ['', '_STATIC']:
  cid=f'EDGE_{pol}_RIGHT'+suffix;folder=r/'conditions'/cid
  for name in ['run.json','means.npy','flow.npy','input.npy','activity_time.npy','states.npy']:
   rel=f'conditions/{cid}/{name}';assert sha(r/rel)==entries[rel]['sha256'];verified.append(rel)
  run=json.loads((folder/'run.json').read_text());identities.append(run)
  assert run['PL_execution'] is False and run['backend']=='original_FlyVis_Full_GPU' and run['steps']==485
  a=np.load(folder/'means.npy');states=np.load(folder/'states.npy',mmap_mode='r');np.testing.assert_allclose(states[:,ids].mean(2,dtype=np.float64),a,atol=1e-14,rtol=0)
  data[cid]=dict(a=a,flow=np.load(folder/'flow.npy'),input=np.load(folder/'input.npy'),t=np.load(folder/'activity_time.npy'))
for key in ['initial_raw_sha256','model_checkpoint_sha256','numeric_profile_sha256','decoder_state_sha256','dt_s','PACK_sha256']:assert len({x[key] for x in identities})==1
complement_error=float(np.max(np.abs(data['EDGE_ON_RIGHT']['input']+data['EDGE_OFF_RIGHT']['input']-1)))
types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];results={}
for pol in ['ON','OFF']:
 a=data[f'EDGE_{pol}_RIGHT']['a'];st=data[f'EDGE_{pol}_RIGHT_STATIC']['a'];d=a-a[160:200].mean(0);f=data[f'EDGE_{pol}_RIGHT']['flow'][200:400].mean((0,2))
 results[pol]=dict(run_id=next(x['run_id'] for x in identities if x['condition_id']==f'EDGE_{pol}_RIGHT'),mean_delta=dict(zip(types,d[200:400].mean(0).tolist())),peak_delta=dict(zip(types,d[200:400].max(0).tolist())),mean_vs_static=dict(zip(types,(a-st)[200:400].mean(0).tolist())),flow_mean=f.tolist(),flow_angle_deg=float(np.degrees(np.arctan2(f[1],f[0]))))
report=dict(evidence='SAVED_ACTUAL_GPU_RESULTS_ONLY_NOT_FPGA_OFF_TEST',baseline_steps=[160,199],motion_steps=[200,399],same_backend_initial_model_dt_numeric_decoder=True,input_complement_max_abs_error=complement_error,verified_files=verified,results=results,identities=identities)
(e/'ANALYSIS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
plt.style.use('dark_background');fig,axs=plt.subplots(2,2,figsize=(13,7),sharex=True,sharey=True);colors=['#efc65b','#5edce9','#5fe2b0','#b89aff'];
for col,pol in enumerate(['ON','OFF']):
 item=data[f'EDGE_{pol}_RIGHT'];d=item['a']-item['a'][160:200].mean(0)
 for row,family in enumerate(['T4','T5']):
  ax=axs[row,col]
  for j in range(4):ax.plot(item['t'],d[:,row*4+j],color=colors[j],lw=2,label=types[row*4+j])
  ax.axhline(0,c='#aaaaaa',lw=.8);ax.axvspan(1.005,2,alpha=.10,color='white');ax.set_xlim(.8,2.425);ax.set_ylim(-.22,.22);ax.grid(alpha=.14);ax.legend(ncol=4,fontsize=10,loc='upper right');ax.set_title(('向右亮边缘 ON' if pol=='ON' else '向右暗边缘 OFF')+' · '+family,fontsize=14)
  if col==0:ax.set_ylabel('相对运动前的活动变化')
  if row==1:ax.set_xlabel('模型时间（秒）；灰色区域为移动阶段')
fig.suptitle('同一原模型 / 同一初态 / 同一GPU数值配置：ON与OFF并非“T4b、T5b轮流最强”',fontsize=16)
fig.text(.05,.018,'每条曲线为721节点均值；基线：160–199步；已有真实GPU结果的离线分析，未重新运行，非OFF实板验收。',fontsize=11)
fig.tight_layout(rect=(0,.05,1,.94));fig.savefig(e/'ON_OFF_RIGHT.png',dpi=150);print(json.dumps(results,ensure_ascii=False,indent=1));print('verified and saved',e)

