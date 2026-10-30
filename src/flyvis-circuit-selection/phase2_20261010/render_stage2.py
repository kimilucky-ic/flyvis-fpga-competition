"""Scientific plots from the accepted all-step CSVs; no simulation."""
from pathlib import Path
import argparse,os,csv
HERE=Path(__file__).resolve().parent
os.environ['MPLBACKEND']='Agg'
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib_windows')
import numpy as np
import matplotlib.pyplot as plt
ART=HERE/'artifacts'
parser=argparse.ArgumentParser()
parser.add_argument('--source-run',default='source_gpu_r1')
parser.add_argument('--aggregate-run',default='aggregate_gpu_r1')
parser.add_argument('--audit-run',default='final_audit')
parser.add_argument('--profile',choices=['CPU_CANONICAL','OFFICIAL_NATIVE_GPU_EXPANDED'],default='CPU_CANONICAL')
args=parser.parse_args()
fig,axes=plt.subplots(2,2,figsize=(13,8),layout='constrained',sharex=True,sharey=True)
labels=['OFF 0 deg','ON 0 deg','OFF 180 deg','ON 180 deg']
for c,ax in enumerate(axes.flat):
    for run,label,style in [(args.source_run,'SOURCE_RAW','-'),(args.aggregate_run,'CURRENT_AGG','--')]:
        records=list(csv.DictReader((ART/run/f'condition_{c:02d}/step_errors.csv').open()))
        steps=[int(row['step_id']) for row in records]
        for group,color in [('H','#326496'),('R','#6b737b')]:
            values=np.array([float(row[group+'_max_abs']) for row in records])
            ax.semilogy(steps,np.where(values>0,values,np.nan),linestyle=style,color=color,
                linewidth=1.1,label=f'{label} {group}')
    ax.axhline(1e-5,color='#aab0b6',linestyle=':',linewidth=.8,label='atol term 1e-5')
    ax.set(title=labels[c],xlabel='step_id (5 ms logical step)',ylabel='Max absolute activity error')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.15)
axes[0,0].legend(fontsize=9,frameon=False,loc='upper right')
fig.suptitle('True FlyVis closed loop: every H/R node compared at every step',fontsize=14)
profile_caption=('Official GPU Full vs GPU R-only + independent NumPy H; identical CUDA-native expanded parameters' if
    args.profile=='OFFICIAL_NATIVE_GPU_EXPANDED' else 'CPU official Full vs GPU R-only + independent NumPy H; CPU-canonical expanded parameters')
fig.text(.5,-.055,profile_caption+'; shared a0 and fixed input.\n'
    'Source: phase2_20261010 accepted runs, 2026-10-10. Each condition: 485 steps, H=67 / R=45,602.\n'
    'Gate also applies rtol=1e-5; zero errors omitted on log axis. Software evidence only; no FPGA/RTL result.',
    ha='center',va='top',fontsize=10)
path=ART/args.audit_run/'step_error_comparison.png'
fig.savefig(path,dpi=150,bbox_inches='tight');plt.close(fig)
print('Saved',path)
