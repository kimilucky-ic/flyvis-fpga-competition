"""Scientific plots from saved predictions; no fits or neural runs."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib')
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from study import load,frame

summary=load(HERE/'SUMMARY.json')['results']
probes=['legacy8','central8','central56','field8','field488']
labels=['Old center8','Refit center8','Center56','Field pooled8','Field488 (primary)']
colors=['#888888','#b7b7b7','#d6a048','#2a9d8f','#1766a0']
groups=['center','left','right','up','down','wide_edge']
x=np.arange(len(groups))
fig,axs=plt.subplots(2,1,figsize=(12,8),layout='constrained',sharex=True)
for ax,model in zip(axs,['Full','a_r4']):
    for j,probe in enumerate(probes):
        r=next(r for r in summary if r['model']==model and r['probe']==probe)
        ax.bar(x+(j-2)*.155,[r['groups'][g]['hit30']*100 for g in groups],.155,color=colors[j],label=labels[j])
    ax.axhline(75,color='#555555',linestyle='--',linewidth=.8)
    ax.set(title=model+' with same Full-design readout weights',ylabel='Direction hit within 30 degrees (%)',ylim=(0,109))
    ax.spines[['right','top']].set_visible(False)
    ax.axvspan(2.5,4.5,color='#eeeeee',alpha=.35,zorder=-1)
axs[0].legend(ncol=3,fontsize=9,loc='upper center',bbox_to_anchor=(.5,1.35))
axs[1].set_xticks(x,['Center','Left 2','Right 2','Up 2 (new)','Down 2 (new)','Wide edge'])
axs[1].set_xlabel('Fixed screen position / control; offsets in retinal-neighbour spacings')
fig.suptitle('New held-out directions: 8 moving clips per group, rejects count as misses\nSource: actual CPU study 2026-10-13; neural model frozen, only diagnostic readouts fitted',fontsize=12)
fig.savefig(HERE/'direction_by_position.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for j,model in enumerate(['Full','a_r4']):
    rs=[next(r for r in summary if r['model']==model and r['probe']==p) for p in probes]
    for ax,key,n,title in zip(axs,['coverage','static_fp','appearance_fp'],[40,10,8],['Motion output coverage','Static false motion','Edge appearance false motion']):
        vals=[r['local']['coverage']*100 for r in rs] if key=='coverage' else [r[key]/n*100 for r in rs]
        ax.bar(np.arange(5)+(j-.5)*.36,vals,.36,label=model,color=['#444444','#1766a0'][j])
        ax.set(title=title,ylabel='Rate (%)',ylim=(0,105));ax.set_xticks(np.arange(5),labels,rotation=38,ha='right',fontsize=8)
        ax.spines[['right','top']].set_visible(False)
axs[0].legend();fig.suptitle('Same frozen test set: 40 local motion, 10 static, 8 appearance controls')
fig.savefig(HERE/'coverage_and_controls.png',dpi=160);plt.close(fig)

cases=load(HERE/'CASES.json');m=np.load(HERE/'READOUT_MAP.npz')
fig,axs=plt.subplots(1,5,figsize=(12,3),layout='constrained')
for ax,g in zip(axs,groups[:5]):
    c=next(c for c in cases if c['split']=='test' and c['group']==g and c['polarity']=='ON')
    ax.imshow(frame(c,1.25),cmap='gray',vmin=0,vmax=255)
    ax.set_xlim(82,141);ax.set_ylim(141,82);ax.set_title(g);ax.set_xticks([]);ax.set_yticks([])
fig.suptitle('Stimulus geometry at 1.25s: fixed window locations independent of direction\nCrop shown; true video is 224x224, same local window radius 1.6 spacings')
fig.savefig(HERE/'stimulus_positions.png',dpi=160);plt.close(fig)
print('3 scientific figures generated from saved results')
