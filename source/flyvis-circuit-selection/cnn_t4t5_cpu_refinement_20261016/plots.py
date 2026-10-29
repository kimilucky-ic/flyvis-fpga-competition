"""Saved-result scientific plots only: no fit or network execution."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from shared import load,mapping,TYPES

old=load(HERE/'training/BASELINE_VALIDATION.json');new=load(HERE/'training/RIDGE.json')['validation']
short=load(HERE/'short_checks/ridge/RESULT.json');m=mapping()
fig,axs=plt.subplots(1,2,figsize=(13,4.4),layout='constrained')
x=np.arange(8)
axs[0].bar(x-.18,np.array(old['subtype_increment_nRMSE'])*100,.36,color='#888888',label='Prior700-update model')
axs[0].bar(x+.18,np.array(new['subtype_increment_nRMSE'])*100,.36,color='#1766a0',label='Same architecture, refined fit')
axs[0].axhline(20,color='#444444',linestyle='--',linewidth=.8,label='Per-type gate20%')
axs[0].set(xticks=x,xticklabels=TYPES,ylabel='One-step RMSE / true increment RMS (%)',title='Same reserved time points,4096 sampled spatial points')
axs[0].legend(fontsize=8)
pos=np.arange(13)
axs[1].plot(pos,[r['H_nRMSE']*100 for r in short['records']],'o-',color='#1766a0',label='H all5768')
axs[1].plot(pos,[r['R_nRMSE']*100 for r in short['records']],'s-',color='#555555',label='R all39901')
axs[1].axhline(5,color='#1766a0',linestyle='--',linewidth=.8,label='H gate5%')
axs[1].axhline(1,color='#555555',linestyle=':',linewidth=.8,label='R gate1%')
axs[1].set(xticks=pos,xticklabels=[str(i+1) for i in pos],xlabel='Predeclared short-window index (13=gray)',
    ylabel='State relative RMSE (%)',title='13 actual live-R short loops,128 steps each')
axs[1].legend(fontsize=8,ncol=2)
for ax in axs:ax.spines[['right','top']].set_visible(False)
fig.suptitle('CPU refinement before holdout:31168 parameters unchanged; no BPTT was needed',fontsize=12)
fig.savefig(HERE/'training_gates.png',dpi=160);plt.close(fig)

rows=load(HERE/'RESULTS.json')['records']
labels=[r['case'].replace('_speed_075','\n0.75speed').replace('_shift_v_minus3','\nshift').replace('_local_left','\nleft').replace('_local_right','\nright').replace('_base','\nbase') for r in rows]
fig,axs=plt.subplots(2,2,figsize=(14,8),layout='constrained')
for ax,key,title,limit in [(axs[0,0],'H','All-H response relative L2',.2),(axs[0,1],'E','Official flow field difference E',.2),
    (axs[1,0],'M','Official flow amplitude ratio M',None),(axs[1,1],'A','Official vector-field angle vs Full',15)]:
    x=np.arange(12)
    if key=='H':ax.bar(x,[r['H_response_relative_L2'] for r in rows],color='#1766a0')
    else:
        fkey={'E':'field_error_E','M':'magnitude_ratio','A':'angle_deg'}[key]
        ax.bar(x-.18,[r['flow']['primary'][fkey] for r in rows],.36,color='#888888',label='Primary200:286')
        ax.bar(x+.18,[r['flow']['allpost'][fkey] for r in rows],.36,color='#1766a0',label='Allpost200:485')
    if limit is not None:ax.axhline(limit,color='#444444',linestyle='--',linewidth=.8,label='Frozen limit')
    if key=='M':
        ax.axhline(.8,color='#444444',linestyle='--',linewidth=.8);ax.axhline(1.2,color='#444444',linestyle='--',linewidth=.8)
        ax.set_ylim(.75,1.25)
    elif key=='A':ax.set_ylim(0,16)
    else:ax.set_ylim(0,.22)
    ax.set_xticks(x,labels,rotation=35,ha='right',fontsize=7)
    ax.set(title=title,ylabel='Degrees' if key=='A' else 'Dimensionless')
    ax.spines[['right','top']].set_visible(False)
    if key!='H':ax.legend(fontsize=8,loc='upper left')
fig.suptitle('Frozen independent test:12/12 pass; each CNN runs485 real closed-loop steps\nFull is the original model reference, not optical-flow ground truth or direction-classification accuracy',fontsize=12)
fig.savefig(HERE/'holdout_gates.png',dpi=160);plt.close(fig)

activity=np.load(HERE/'CENTRAL_T4T5_ACTIVITY.npz');case='ON30_base'
ci=list(activity['case_ids']).index(case);curves=activity['activity'][ci].mean(-1);t=(np.arange(485)+1)*.005
fig,axs=plt.subplots(4,2,figsize=(11,10),layout='constrained',sharex=True)
for i,ax in enumerate(axs.flat):
    ax.plot(t,curves[0,:,i],color='#222222',label='Full')
    ax.plot(t,curves[1,:,i],color='#d55e00',linestyle='--',label='CNN replacement')
    ax.set(title=TYPES[i],ylabel='Continuous activity, original units')
    ax.spines[['right','top']].set_visible(False)
    if i==0:ax.legend(fontsize=9)
for ax in axs[-1]:ax.set_xlabel('Activity output time (s)')
fig.suptitle('First predeclared holdout ON30:fixed central7 positions for each T4/T5 type\nOriginal H update disabled in CNN run; no reference-state corrections',fontsize=12)
fig.savefig(HERE/'eight_type_activity.png',dpi=160);plt.close(fig)

uv=m['grid_uv'];px=np.sqrt(3)/2*uv[1];py=-(uv[0]+uv[1]/2)
fig,axs=plt.subplots(2,2,figsize=(10,8.5),layout='constrained')
for ri,case in enumerate(['ON30_base','ON30_local_left']):
    vals=[np.load(HERE/'test_runs'/case/mode/'flow.npy')[242] for mode in ['Full','CNN']]
    mags=[np.linalg.norm(v,axis=0) for v in vals];norm=LogNorm(vmin=1e-4,vmax=max(max(v.max() for v in mags),.01))
    for col,(mode,v,mag) in enumerate(zip(['Full','CNN'],vals,mags)):
        ax=axs[ri,col];artist=ax.scatter(px,py,c=np.maximum(mag,1e-4),norm=norm,cmap='viridis',s=12)
        ids=np.arange(0,721,13);den=np.maximum(mag[ids],1e-12)
        ax.quiver(px[ids],py[ids],v[0,ids]/den,v[1,ids]/den,angles='xy',scale_units='xy',scale=1,width=.004,color='#222222')
        ax.set(title=f'{case}: {mode}',xlabel='Retinal x (neighbour spacings)',ylabel='Retinal y (neighbour spacings)',aspect='equal')
    fig.colorbar(artist,ax=axs[ri,:].tolist(),label='Raw flow magnitude (log)',shrink=.82)
fig.suptitle('Original DecoderGAVP at output time1.215s:base and first localized case\nSame color scale within each row; arrows are unit direction only, not magnitude.',fontsize=11)
fig.savefig(HERE/'official_flow_comparison.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(2,1,figsize=(10,5.5),layout='constrained',sharex=True)
err=load(HERE/'test_runs/ON30_base/STEP_ERRORS.json')
axs[0].plot(t,[r['H_RMSE'] for r in err],color='#1766a0');axs[0].set(ylabel='All-H RMSE',title='ON30_base: actual state error vs Full')
axs[1].plot(t,[r['R_RMSE'] for r in err],color='#555555');axs[1].set(ylabel='All-R RMSE',xlabel='Activity output time (s)')
for ax in axs:ax.spines[['right','top']].set_visible(False)
fig.savefig(HERE/'closed_loop_errors.png',dpi=160);plt.close(fig)
print('5 figures from saved data; no training, network or decoder execution')
