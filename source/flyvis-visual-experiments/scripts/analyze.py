"""Analyze saved experiments using official DSI and export scientific figures."""
import os,json,hashlib
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='-1',FLYVIS_ROOT_DIR='/opt/flyvis-visual-experiments-data',
                  MPLBACKEND='Agg',MPLCONFIGDIR='/opt/flyvis-visual-experiments-data/matplotlib',
                  NUMBA_CACHE_DIR='/opt/flyvis-visual-experiments-data/numba',TIMEZONE='Asia/Shanghai')
import numpy as np,pandas as pd,xarray as xr
import matplotlib.pyplot as plt
from PIL import Image
from flyvis.analysis.moving_bar_responses import direction_selectivity_index,preferred_direction,peak_responses
WORK=Path(__file__).resolve().parents[1]
ART=WORK/'artifacts';OUT=ART/'analysis';OUT.mkdir(exist_ok=True)
BASE=Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly')
GPU=ART/'cross_gpu_cuda_r1';CPU=ART/'cross_cpu_cpu_r1'
ct=np.load(GPU/'cell_types.npy').astype(str)
targets=[f'T{n}{s}' for n in [4,5] for s in 'abcd']
idx=[list(ct).index(c) for c in targets]
a=np.load(GPU/'activity_central.npy');b=np.load(CPU/'activity_central.npy')
s=np.load(GPU/'stimulus.npy');t=np.load(GPU/'time.npy');samples=pd.read_csv(GPU/'samples.csv',index_col='sample')
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str))
config=dict(offsets=[-10,11],angles=list(range(0,360,30)),intensities=[0,1],widths=[80],speeds=[19],dt=.005,t_pre=1,t_post=1,height=80,post_pad_mode='continue')
def dataset(activity):
    return xr.Dataset({'responses':(['network_id','sample','frame','neuron'],activity[None])},
                      coords={'network_id':[0],'sample':np.arange(24),'frame':np.arange(485),'neuron':np.arange(65),
                              'time':('frame',t),'cell_type':('neuron',ct),
                              **{col:('sample',samples[col].values) for col in samples.columns}},attrs={'config':config})
data=dataset(a);cpu_data=dataset(b)
dsi=direction_selectivity_index(data)
pd_rad=preferred_direction(data).squeeze('network_id',drop=True)
peak=peak_responses(data).squeeze('network_id',drop=True)
cpu_dsi=direction_selectivity_index(cpu_data)
cpu_pd=preferred_direction(cpu_data).squeeze('network_id',drop=True)
rows=[]
for neuron,c in enumerate(ct):
    for polarity in [0,1]:
        value=float(dsi.sel(neuron=neuron,intensity=polarity))
        theta=float(pd_rad.sel(neuron=neuron,intensity=polarity))
        cpu_theta=float(cpu_pd.sel(neuron=neuron,intensity=polarity))
        rows.append(dict(cell_type=c,intensity=polarity,polarity='ON' if polarity else 'OFF',
                         official_dsi=value,preferred_direction_deg=float(np.degrees(theta)%360),
                         cpu_dsi=float(cpu_dsi.sel(neuron=neuron,intensity=polarity)),
                         cpu_gpu_pd_difference_deg=float(abs(np.degrees(np.angle(np.exp(1j*(theta-cpu_theta)))))),
                         dsi_interpretation='single model, one speed, original rectified peak metric'))
metrics=pd.DataFrame(rows);metrics.to_csv(OUT/'direction_metrics_all_65.csv',index=False)
metrics[metrics.cell_type.isin(targets)].to_csv(OUT/'direction_metrics_T4_T5.csv',index=False)
peak_rows=[];trend=[]
for sample,param in samples.iterrows():
    for neuron,c in enumerate(ct):
        peak_rows.append(dict(sample=int(sample),cell_type=c,angle_deg=param.angle,intensity=param.intensity,
                              speed=param.speed,rectified_peak=float(peak.sel(sample=sample,neuron=neuron))))
    for neuron,c in zip(idx,targets):
        x,y=a[sample,:,neuron],b[sample,:,neuron]
        corr=float(np.corrcoef(x,y)[0,1]) if np.std(x)>1e-12 and np.std(y)>1e-12 else None
        trend.append(dict(sample=int(sample),cell_type=c,angle_deg=param.angle,intensity=param.intensity,
                          pearson_r=corr,peak_frame_difference=int(np.argmax(x)-np.argmax(y)),
                          max_abs_error=float(np.abs(x-y).max())))
pd.DataFrame(peak_rows).to_csv(OUT/'angular_peak_responses.csv',index=False)
pd.DataFrame(trend).to_csv(OUT/'cpu_gpu_target_trends.csv',index=False)
np.save(OUT/'activity_T4_T5.npy',a[:,:,idx])
pd.DataFrame(a[:,:,idx].reshape(-1,8),columns=targets).assign(sample=np.repeat(np.arange(24),485),frame=np.tile(np.arange(485),24),time_s=np.tile(t,24)).to_csv(OUT/'activity_T4_T5.csv',index=False)
dump(OUT/'direction_analysis.json',dict(status='PASS',official_functions=['peak_responses','direction_selectivity_index','preferred_direction'],
    analysis_module='flyvis.analysis.moving_bar_responses',config=config,
    dsi_formula='abs(sum_angle(peak*exp(i*angle))) / max_intensity(sum_angle(peak))',
    peak_definition='max rectified raw activity over official speed/offset time window; no baseline subtraction',
    dsi_max_abs_cpu_gpu_error=float(np.abs(dsi.values-cpu_dsi.values).max()),
    target_metrics=metrics[metrics.cell_type.isin(targets)].to_dict(orient='records'),
    limitations=['One pretrained model and speed=19 only; no ensemble statistical or biological validation',
                 'All 12 directions present; stimulus derived from GPU renderer, not validated as identical to independent CPU rendering',
                 'Very weak directional responses can yield unstable preferred angles; examine DSI and peaks together']))
angles=np.deg2rad(np.arange(0,360,30))
fig,axs=plt.subplots(2,4,subplot_kw={'projection':'polar'},figsize=(14,7.5))
for ax,c,n in zip(axs.flat,targets,idx):
    for intensity,color in [(1,'#cc6519'),(0,'#176da5')]:
        sample_ids=samples.index[samples.intensity==intensity]
        values=peak.values[sample_ids,n]
        ax.plot(np.r_[angles,angles[0]],np.r_[values,values[0]],label='ON' if intensity else 'OFF',color=color)
    ax.set_title(c,pad=17)
    ax.set_xticks(np.deg2rad([0,90,180,270]));ax.tick_params(labelsize=8)
axs[0,0].legend(loc='upper left',bbox_to_anchor=(-.25,1.4))
fig.suptitle('Original FlyVis: rectified peak angular tuning (12 directions, speed=19)',fontsize=14)
fig.text(.5,.02,'Single pretrained model flow/0000/000 | original official peak window | software simulation',ha='center',fontsize=10)
fig.subplots_adjust(top=.85,bottom=.1,hspace=.45,wspace=.35)
fig.savefig(OUT/'angular_tuning.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(4,2,figsize=(12,11),sharex=True)
for ax,c,n in zip(axs.flat,targets,idx):
    for sample,label,color,style in [(0,'OFF 0','#176da5','-'),(12,'OFF 180','#176da5','--'),(1,'ON 0','#cc6519','-'),(13,'ON 180','#cc6519','--')]:
        ax.plot(t,a[sample,:,n],label=label,color=color,ls=style,lw=1.2)
    ax.axvline(0,color='grey',lw=.7);ax.set_title(c);ax.set_ylabel('model activity');ax.grid(alpha=.2)
axs[0,0].legend(ncol=2,fontsize=8)
for ax in axs[-1]:ax.set_xlabel('Time from motion onset (s)')
fig.suptitle('Original FlyVis ON/OFF opposed edges: same checkpoint, full network')
fig.tight_layout(rect=[0,0,1,.96]);fig.savefig(OUT/'on_off_opposed_traces.png',dpi=150);plt.close(fig)
fig,axs=plt.subplots(2,1,figsize=(12,7),sharex=True)
for ax,sample in zip(axs,[0,1]):
    image=ax.imshow(a[sample].T,aspect='auto',origin='lower',extent=[t[0],t[-1],-.5,64.5],cmap='coolwarm')
    ax.set_yticks(idx);ax.set_yticklabels(targets);ax.set_title(f'All 65 central cells: {"OFF" if sample==0 else "ON"}, 0 degrees')
    fig.colorbar(image,ax=ax,label='raw model activity')
axs[-1].set_xlabel('Time from motion onset (s)');fig.tight_layout();fig.savefig(OUT/'activity_heatmap.png',dpi=150);plt.close(fig)

bar=ART/'bar_cuda_r1'
if (bar/'result.json').exists():
    fig,axs=plt.subplots(2,2,figsize=(12,7),sharex=False);conditions=[]
    for folder in sorted(bar.glob('condition_*')):
        info=json.loads((folder/'result.json').read_text());param=info['parameters']
        aa=np.load(folder/'activity_central.npy')[0];tt=np.load(folder/'time.npy')
        conditions.append(dict(**param,frames=len(tt),**{f'{c}_peak_above_prebaseline':float((aa[:,n]-aa[(tt>=-.2)&(tt<0),n].mean())[tt>=0].max()) for c,n in zip(targets,idx)}))
        if param['angle']==0 and param['width']==1 and param['intensity'] in [0,1]:
            for ax,c in zip(axs.flat,['T4c','T5c','T4a','T5a']):
                ax.plot(tt,aa[:,list(ct).index(c)],label=f'{"ON" if param["intensity"] else "OFF"}, speed {param["speed"]}')
                ax.set_title(c);ax.set_xlabel('Time from motion onset (s)');ax.set_ylabel('model activity');ax.grid(alpha=.2)
    axs[0,0].legend(fontsize=8);fig.suptitle('Original finite MovingBar: two speeds, ON/OFF, 0 degrees')
    fig.tight_layout(rect=[0,0,1,.95]);fig.savefig(OUT/'moving_bar_speed_traces.png',dpi=150);plt.close(fig)
    pd.DataFrame(conditions).to_csv(OUT/'moving_bar_condition_summary.csv',index=False)

decoder=ART/'decoder_cuda_r3'
if (decoder/'flow.npy').exists():
    flow=np.load(decoder/'flow.npy');stim=np.load(decoder/'stimulus.npy');dt=np.load(decoder/'time.npy')
    u=np.load(decoder/'hex_u.npy');v=np.load(decoder/'hex_v.npy')
    # Hex coordinate conversion follows flyvis.utils.hex_utils.hex_to_pixel default.
    from flyvis.utils.hex_utils import hex_to_pixel
    x,y=hex_to_pixel(u,v)
    frame=int(np.argmin(abs(dt-.2)));mask=(np.arange(721)%9)==0
    fig,axs=plt.subplots(2,2,figsize=(11,9))
    for sample,ax in enumerate(axs.flat):
        ax.scatter(x,y,c=stim[sample,frame,0],cmap='gray',vmin=0,vmax=1,s=30,marker='h')
        ax.quiver(x[mask],y[mask],flow[sample,frame,0,mask],flow[sample,frame,1,mask],color='#e56c14',scale=None)
        ax.set_title(f'{"OFF" if sample%2==0 else "ON"}, {0 if sample<2 else 180} degrees | t={dt[frame]:.3f}s')
        ax.set_aspect('equal');ax.axis('off')
    fig.suptitle('Original pretrained DecoderGAVP output on synthetic edges',fontsize=14)
    fig.text(.5,.035,'Automatic arrow scale per panel; component values in model output units. No calibrated velocity/EPE claim.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,.95]);fig.savefig(OUT/'decoded_flow_vectors.png',dpi=150);plt.close(fig)
    # A compact animation is prerecorded software simulation, with actual 5 ms time axis.
    images=[];sample=1
    fig,(eye_ax,trace_ax)=plt.subplots(1,2,figsize=(9,4.2),gridspec_kw={'width_ratios':[1,1.5]})
    dots=eye_ax.scatter(x,y,c=stim[sample,0,0],cmap='gray',vmin=0,vmax=1,s=22,marker='h')
    eye_ax.set_aspect('equal');eye_ax.axis('off')
    for c in ['T4c','T5c']:trace_ax.plot(t,a[1,:,list(ct).index(c)],label=c,lw=1.4)
    marker=trace_ax.axvline(t[0],color='red',lw=1)
    trace_ax.legend();trace_ax.set_xlabel('Simulation time from motion onset (s)');trace_ax.set_ylabel('model activity');trace_ax.grid(alpha=.2)
    title=fig.suptitle('Prerecorded original FlyVis software simulation: ON edge, 0 degrees')
    fig.tight_layout(rect=[0,0,1,.87])
    for f in range(0,len(t),8):
        dots.set_array(stim[sample,f,0]);marker.set_xdata([t[f],t[f]])
        eye_ax.set_title(f'721 hex inputs | t={t[f]:.3f}s')
        fig.canvas.draw();images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()).convert('P',palette=Image.Palette.ADAPTIVE))
    images[0].save(OUT/'stimulus_activity_playback.gif',save_all=True,append_images=images[1:],duration=40,loop=0)
    plt.close(fig)
    np.save(OUT/'decoded_flow_spatial_mean.npy',flow.mean(axis=-1))
    pd.DataFrame(flow.mean(axis=-1).reshape(-1,2),columns=['component_0','component_1']).assign(sample=np.repeat(np.arange(4),485),frame=np.tile(np.arange(485),4),time_s=np.tile(t,4)).to_csv(OUT/'decoded_flow_spatial_mean.csv',index=False)

# Verify candidate Euler semantics from exported boundary inputs; no graph is modified.
bound=ART/'boundary_cuda_r1'
if (bound/'result.json').exists():
    checks=[]
    for candidate in ['T4c','T5c']:
        folder=bound/candidate;nodes=pd.read_csv(folder/'internal_nodes.csv');incoming=pd.read_csv(folder/'incoming_source_nodes.csv')
        edges=pd.concat([pd.read_csv(folder/'internal_edges.csv'),pd.read_csv(folder/'incoming_edges.csv')]).sort_values('edge_index')
        internal=nodes.node_index.values;external=incoming.node_index.values
        union=np.r_[internal,external];mapping={int(node):i for i,node in enumerate(union)}
        src=np.array([mapping[int(v)] for v in edges.source_index]);target_map={int(node):i for i,node in enumerate(internal)}
        dest=np.array([target_map[int(v)] for v in edges.target_index]);weight=edges.weight.values.astype(np.float32)
        tau=nodes.time_const_s.values.astype(np.float32);bias=nodes.bias.values.astype(np.float32)
        for sub in sorted(folder.glob('sample_*')):
            ref=np.load(sub/'internal_activity_after.npy');initial=np.load(sub/'initial_internal.npy')
            boundary=np.load(sub/'boundary_incoming_activity_before.npy');external_input=np.load(sub/'external_node_input.npy')
            predictions=[];state=initial.copy();step_predictions=[]
            for frame in range(len(ref)):
                source_a=np.r_[state,boundary[frame]]
                current=np.zeros(len(internal),dtype=np.float32)
                np.add.at(current,dest,weight*np.maximum(source_a[src],np.float32(0)))
                state=state+((-state+bias+current+external_input[frame])/np.maximum(tau,np.float32(.005)))*np.float32(.005)
                predictions.append(state.copy())
                # Also audit one step with observed internal pre-state to distinguish accumulated rounding.
                observed_before=initial if frame==0 else ref[frame-1]
                source_a=np.r_[observed_before,boundary[frame]];current=np.zeros(len(internal),dtype=np.float32)
                np.add.at(current,dest,weight*np.maximum(source_a[src],np.float32(0)))
                step_predictions.append(observed_before+((-observed_before+bias+current+external_input[frame])/np.maximum(tau,np.float32(.005)))*np.float32(.005))
            predicted=np.asarray(predictions);one_step=np.asarray(step_predictions)
            item=dict(candidate=candidate,sample=int(sub.name.split('_')[1]),
                      recurrence_max_abs_error=float(np.abs(predicted-ref).max()),
                      recurrence_rmse=float(np.sqrt(np.mean((predicted.astype(float)-ref)**2))),
                      one_step_max_abs_error=float(np.abs(one_step-ref).max()),
                      allclose=bool(np.allclose(predicted,ref,atol=1e-5,rtol=1e-5)),atol=1e-5,rtol=1e-5)
            checks.append(item);np.save(sub/'boundary_driven_euler_replay.npy',predicted)
    dump(OUT/'boundary_euler_audit.json',dict(status='PASS' if all(c['allclose'] for c in checks) else 'FAIL',checks=checks,
        method='Float32 software audit of original Euler equation with recorded external boundary; all incoming edges retained in ascending original edge order; no topology change'))
print('ANALYSIS_COMPLETE',json.dumps({'target_metrics':metrics[metrics.cell_type.isin(targets)].to_dict('records'),'output':str(OUT)}),flush=True)
