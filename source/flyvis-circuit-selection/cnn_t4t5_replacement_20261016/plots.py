"""Standalone scientific figures from sealed computation, no training/rollouts."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from common import load,read_mapping,LANE

mapping=read_mapping();results=load(HERE/'RESULTS.json');records=[r for r in results['records'] if r['mode']=='CNN']
labels=[r['case'].replace('_','\n') for r in records]
fig,axs=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
for ax,key,title in [(axs[0],'H','H activity response difference'),(axs[1],'E','Official flow field difference')]:
    for i,r in enumerate(records):
        value=r.get('H_response_relative_L2') if key=='H' else r.get('flow',{}).get('allpost',{}).get('field_error_E')
        if value is None:ax.text(i,.4,'STOP\n399 steps',rotation=90,ha='center',va='bottom',fontsize=8)
        else:ax.bar(i,value,color='#1766a0')
    ax.axhline(.2,color='#444444',linestyle='--',label='Frozen gate 0.20')
    ax.set_yscale('log');ax.set_ylim(.1,300);ax.set_xticks(np.arange(8),labels,rotation=35,ha='right',fontsize=8)
    ax.set(title=title,ylabel='Relative L2 difference (dimensionless)');ax.legend(fontsize=8)
    ax.spines[['right','top']].set_visible(False)
fig.suptitle('All eight held-out cases fail the frozen functional gate\nRaw original decoder; Full is a model reference, not optical-flow ground truth',fontsize=11)
fig.savefig(HERE/'closed_loop_gates.png',dpi=160);plt.close(fig)

case='ON0_base';uv=mapping['grid_uv'];center=np.maximum.reduce([abs(uv[0]),abs(uv[1]),abs(uv[0]+uv[1])])<=1
fig,axs=plt.subplots(2,2,figsize=(12,7),layout='constrained')
for mode,color in [('Full','#222222'),('CNN','#1766a0'),('HOLD','#888888')]:
    root=HERE/'runs'/case/mode;n=load(root/'RESULT.json')['steps']
    activity=np.load(root/'states.npy',mmap_mode='r')[:n,mapping['H_grid_ids']]
    t=(np.arange(n)+1)*.005
    for j,typ in enumerate([0,4]):axs[0,j].plot(t,activity[:,typ,center].mean(1),label=mode,color=color)
    if mode=='CNN':
        error=load(root/'STEP_ERRORS.json')
        axs[1,0].plot(t,[max(r['H_RMSE'],1e-9) for r in error],color=color,label='All 5768 H')
        axs[1,1].plot(t,[max(r['R_RMSE'],1e-9) for r in error],color=color,label='All 39901 R')
for j,title in enumerate(['T4a: fixed central7 neurons','T5a: fixed central7 neurons']):
    axs[0,j].set(title=title,ylabel='Original continuous activity units');axs[0,j].legend()
for j,title in enumerate(['H state error vs Full','R state error vs Full']):
    axs[1,j].set(title=title,ylabel='RMSE, log scale',yscale='log');axs[1,j].legend()
for ax in axs.flat:
    ax.set_xlabel('Activity output time (s)');ax.axvline(1,color='#777777',linestyle=':',linewidth=.8)
    ax.spines[['right','top']].set_visible(False)
fig.suptitle('ON0 held-out: real CNN output fed into live original R dynamics\nSame a0 / parameters / dt / stimulus. Error already grows before the motion window.',fontsize=11)
fig.savefig(HERE/'activity_and_feedback_errors.png',dpi=160);plt.close(fig)

roi=np.load(LANE/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy')
x=np.sqrt(3)/2*uv[1];y=-(uv[0]+uv[1]/2)
fig,axs=plt.subplots(2,3,figsize=(12,8.3),layout='constrained')
for ri,k in enumerate([242,484]):
    values=[np.load(HERE/'runs'/case/mode/'flow.npy',mmap_mode='r')[k] for mode in ['Full','CNN','HOLD']]
    mags=[np.linalg.norm(v,axis=0) for v in values]
    norm=LogNorm(vmin=1e-4,vmax=max(max(m.max() for m in mags),.01))
    for ci,(mode,v,mag) in enumerate(zip(['Full','CNN','HOLD'],values,mags)):
        ax=axs[ri,ci];sc=ax.scatter(x,y,c=np.maximum(mag,1e-4),s=12,cmap='viridis',norm=norm)
        ids=roi[::7];den=np.maximum(mag[ids],1e-12)
        ax.quiver(x[ids],y[ids],v[0,ids]/den,v[1,ids]/den,angles='xy',scale_units='xy',scale=1,
            width=.004,color='#222222')
        ax.set(title=f'{mode} at {(k+1)*.005:.3f}s',xlabel='Retinal x (neighbour spacings)',ylabel='Retinal y (neighbour spacings)',aspect='equal')
    fig.colorbar(sc,ax=axs[ri,:].tolist(),label='Raw flow magnitude (log)',shrink=.84)
fig.suptitle('ON0: original DecoderGAVP on actual Full / CNN / HOLD states\nColors share a scale within each row; arrows show direction only (unit length), not magnitude.',fontsize=11)
fig.savefig(HERE/'official_flow_comparison.png',dpi=160);plt.close(fig)

single=load(HERE/'ONE_STEP_ONLY_DIAGNOSTIC.json')
fig,ax=plt.subplots(figsize=(11,4.8),layout='constrained');pos=np.arange(8)
ax.bar(pos-.18,[r['RMSE'] for r in single],.36,label='Offline one step with true old state',color='#888888')
ax.bar(pos+.18,[r['neural']['H_all_RMSE'] for r in records],.36,label='Actual closed-loop H error',color='#1766a0')
ax.set(yscale='log',ylabel='All-H activity RMSE (original units)',title='Small-looking one-step error does not establish a stable replacement')
ax.set_xticks(pos,labels,rotation=35,ha='right',fontsize=8);ax.legend(fontsize=9)
fig.supxlabel('CNN errors use committed steps only (last case:399); offline one-step diagnostic uses all485 reference labels.',fontsize=8)
ax.spines[['right','top']].set_visible(False);fig.savefig(HERE/'single_step_vs_closed_loop.png',dpi=160);plt.close(fig)

history=load(HERE/'training/RESULT.json')['history']
fig,ax=plt.subplots(figsize=(8,3.7),layout='constrained')
ax.plot([h['update'] for h in history],[h['loss'] for h in history],color='#1766a0',linewidth=.8)
ax.set(xlabel='Optimizer update',ylabel='Normalized delta-state MSE',yscale='log',title='Fixed700-update training; no test-based selection or extra fit')
ax.spines[['right','top']].set_visible(False);fig.savefig(HERE/'training_loss.png',dpi=160);plt.close(fig)
print('5 scientific figures generated; no new model execution')
