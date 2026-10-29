"""Scientific static comparison from verified structural numbers."""
from pathlib import Path
import os,json
HERE=Path(__file__).resolve().parent
os.environ['MPLBACKEND']='Agg'
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib_windows')
import numpy as np
import matplotlib.pyplot as plt
records=json.loads((HERE/'artifacts/summary.json').read_text(encoding='utf-8'))['candidates']
labels=['A: T4c','B: T5c','C: T4/T5 centers']
x=np.arange(3)
fig,axes=plt.subplots(1,3,figsize=(14.5,5),layout='constrained')
bottom=np.zeros(3)
for key,label,color in [('internal_edges','Internal','#326496'),('incoming_edges','Incoming boundary','#adb5bd'),('outgoing_edges','Outgoing boundary','#e2e5e8')]:
    values=np.array([r[key] for r in records])
    axes[0].bar(x,values,bottom=bottom,label=label,color=color,edgecolor='white',width=.65)
    for j,val in enumerate(values):
        axes[0].text(j,bottom[j]+val/2,f'{val:,}',ha='center',va='center',fontsize=10,color='white' if key=='internal_edges' else '#232323')
    bottom+=values
axes[0].set(title='Connections touching the partition',ylabel='Model connection entries (count)',xlabel='Candidate')
axes[0].legend(frameon=False,loc='upper left',fontsize=9)
axes[0].set_ylim(0,max(bottom)*1.23)
for shift,key,label,color in [(-.18,'n_nodes','Internal state nodes','#326496'),(.18,'incoming_source_nodes','External source nodes','#adb5bd')]:
    values=[r[key] for r in records]
    bars=axes[1].bar(x+shift,values,width=.34,color=color,label=label)
    axes[1].bar_label(bars,labels=[f'{v:,}' for v in values],padding=3,fontsize=10)
axes[1].set(title='States needed by an activity boundary',ylabel='Neurons (count)',xlabel='Candidate',ylim=(0,3500))
axes[1].legend(frameon=False,loc='upper left',fontsize=9)
storage=[r['logical_core_bytes']/1024 for r in records]
bars=axes[2].bar(x,storage,width=.65,color='#326496')
axes[2].bar_label(bars,labels=[f'{v:.2f}' for v in storage],padding=4,fontsize=11)
axes[2].set(title='Logical core storage lower bound',ylabel='Storage (KiB)',xlabel='Candidate',ylim=(0,80))
for ax in axes:
    ax.set_xticks(x,labels,fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.15)
    ax.set_axisbelow(True)
fig.suptitle('FlyVis candidates: small state count does not remove boundary dependence',fontsize=14)
fig.text(.5,-.12,'Source: original complete graph / flow/0000/000, audited 2026-10-10. Storage: 8 bytes/internal edge + 20 bytes/node.\nLogical data only; memory packing, operators, protocol and system overhead excluded. No RTL/synthesis/board result.',ha='center',va='top',fontsize=10)
fig.savefig(HERE/'artifacts/candidate_comparison.png',dpi=150,bbox_inches='tight')
plt.close(fig)
print('Saved',HERE/'artifacts/candidate_comparison.png')
