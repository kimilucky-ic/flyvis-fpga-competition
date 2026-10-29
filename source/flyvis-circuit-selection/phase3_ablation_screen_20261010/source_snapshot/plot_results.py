"""Static research figures from sealed numerical output; not demonstration footage."""
import csv
from common import *

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=HERE/'artifacts/formal_figures'
    if out.exists():raise SystemExit('Preserve figures')
    out.mkdir(parents=True);analysis=HERE/'artifacts/formal_analysis';rows=list(csv.DictReader((analysis/'direction_metrics.csv').open()))
    names=['B_T5c','A_T4c','C_T4T5_all_centers'];labels=['T5c-related (67)','T4c-related (92)','Joint T4/T5 (298)'];xx=np.arange(3);fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
    for ax,metric,title,unit in zip(axes,['S','E'],['Retention along Full direction axis','Relative change of direction trace'],['Coefficient S (Full=1)','Relative L2 change E (Full=0)']):
        for i,pol in enumerate(['OFF','ON']):
            values=[float(next(r for r in rows if r['repeat']=='formal_r1' and r['candidate']==n and r['population']=='primary_visual_readout' and r['polarity']==pol and r['mode']=='Ablation')[metric]) for n in names]
            bars=ax.bar(xx+(i-.5)*.32,values,width=.30,label=pol,color=['#23495d','#899ba4'][i])
            for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.008,f'{v:.3f}',ha='center',fontsize=9)
        ax.set_xticks(xx,labels);ax.set_ylabel(unit);ax.set_xlabel('Frozen candidate');ax.set_title(title);ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
    axes[0].axhline(1,color='.35',ls='--',lw=.8);axes[0].set_ylim(0,1.10);axes[1].axhline(.20,color='.35',ls='--',lw=.8,label='Extension criterion');axes[1].set_ylim(0,.54)
    fig.suptitle('Live software BLOCK_HR_RELEASE: fixed shared downstream T4/T5 (V=1057)',fontsize=12)
    fig.text(.5,-.018,'Source: formal_r1, original pretrained FlyVis; ON/OFF x 0/180; steps 200-484; baseline 160-199. Two angles, not DSI. No FPGA execution.',ha='center',fontsize=9)
    fig.savefig(out/'fixed_V_direction_comparison.png',dpi=180,bbox_inches='tight');fig.savefig(out/'fixed_V_direction_comparison.pdf',bbox_inches='tight');plt.close(fig)
    # Show actual remaining-network effects separately from the H centers.
    fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True,constrained_layout=True)
    for ax,name,label in zip(axes,names,labels):
        traces=list(csv.DictReader((analysis/'formal_r1'/name/'signed_readout_traces.csv').open()))
        for mode,color,linestyle in [('Full','#23495d','-'),('Sham','#899ba4','--'),('Ablation','#9b4e39','-')]:
            subset=[r for r in traces if r['group']=='primary_visual_readout' and r['condition']=='0' and r['mode']==mode]
            ax.plot([float(r['state_after_time']) for r in subset],[float(r['signed_mean_response']) for r in subset],label=mode,color=color,ls=linestyle,lw=1.4)
        ax.axvline(.005,color='.35',ls=':',lw=.8);ax.set_ylabel('Signed mean response\n(activity units)');ax.set_title(label+' / OFF 0 degrees');ax.legend(frameon=False,loc='upper right');ax.spines[['top','right']].set_visible(False)
    axes[-1].set_xlabel('State-after time relative to stimulus onset (s)')
    fig.suptitle('Actual common remaining-network response; no output zeroing',fontsize=13)
    fig.text(.5,-.012,'Source: formal_r1; fixed V=1057 outside all candidate H; baseline steps 160-199; intervention starts at step 200. All four conditions are in the CSV report.',ha='center',fontsize=9)
    fig.savefig(out/'fixed_V_OFF0_signed_response.png',dpi=160,bbox_inches='tight');plt.close(fig)
    dump(out/'result.json',dict(status='GENERATED_FROM_ACTUAL_SEALED_SOFTWARE_DATA',source_manifest_sha256=file_hash(analysis/'artifact_manifest.json'),code_sha256=file_hash(Path(__file__)),not_new_neural_execution=True,FPGA_execution=False));seal(out)

if __name__=='__main__':main()
