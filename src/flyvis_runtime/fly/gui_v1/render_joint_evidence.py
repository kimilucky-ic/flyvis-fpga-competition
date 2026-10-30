"""Static scientific figure from admitted actual short-run evidence; no animation."""
import argparse,json,csv
from pathlib import Path
import numpy as np
from live_protocol import host_path,load,require,Registry
from hybrid_v2 import V2Contract

def render(run,audit_path,out):
    run=host_path(run);out=host_path(out);accepted=load(host_path(audit_path))
    require(accepted['status']=='PASS_ACTUAL_THREE_STEP_GPU_FPGA_CLOSED_LOOP','ACTUAL_AUDIT_REQUIRED')
    require(accepted['run_id']==run.name,'RUN_ID');out.mkdir(exist_ok=True,parents=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    c=V2Contract();reg=Registry();pc=run/'pc'
    activities=np.array([np.load(pc/f'committed_full_{k}.npy',allow_pickle=False) for k in (200,201,202)])
    flow=np.load(pc/'flow_202.npy',allow_pickle=False);frame=np.load(pc/'input_721_202.npy',allow_pickle=False)
    fig,axes=plt.subplots(3,4,figsize=(16,11),facecolor='#101b29');fig.subplots_adjust(top=.87,bottom=.065,hspace=.36,wspace=.24)
    plt.rcParams.update({'text.color':'#dbeaf2','axes.labelcolor':'#dbeaf2','xtick.color':'#b9ccd6','ytick.color':'#b9ccd6'})
    for ax in axes.flat:
        ax.set_facecolor('#101b29');ax.tick_params(colors='#b9ccd6');ax.title.set_color('#dbeaf2')
        ax.xaxis.label.set_color('#dbeaf2');ax.yaxis.label.set_color('#dbeaf2')
        for spine in ax.spines.values():spine.set_color('#435365')
    vmax=float(np.abs(activities[-1,c.h]).max());norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    for ax,typ in zip(axes.flat,c.spatial.data['types'] if 'types' in c.spatial.data else ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']):
        nodes=[n for n in c.spatial.nodes if n['type']==typ]
        x=[1.5*n['v'] for n in nodes];y=[np.sqrt(3)*(n['u']+n['v']/2) for n in nodes]
        values=activities[-1,[n['global_id'] for n in nodes]]
        m=ax.scatter(x,y,c=values,cmap='coolwarm',norm=norm,marker='h',s=12)
        ax.set_title(typ+' | 721 actual PL-updated nodes',fontsize=10);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
    cb=fig.colorbar(m,ax=axes[:2,:].ravel().tolist(),fraction=.015,pad=.015);cb.set_label('signed activity (original model units)',color='#dbeaf2');cb.ax.tick_params(colors='#dbeaf2')
    u,v=reg.uv.T;x=1.5*v;y=np.sqrt(3)*(u+v/2)
    ax=axes[2,0];ax.scatter(x,y,c=frame,cmap='gray',vmin=0,vmax=1,marker='h',s=16);ax.set_aspect('equal');ax.set_title('Actual ON60 input | k202',fontsize=11)
    ax=axes[2,1];ax.quiver(x,y,flow[0],flow[1],angles='xy',scale_units='xy',scale=.1,color='#71ddf7',width=.005);ax.set_aspect('equal');ax.set_title('Official flow | raw vectors x10',fontsize=11)
    ax=axes[2,2]
    for typ,gid in zip(reg.data['types'],reg.data['central_global_ids']):ax.plot([5,10,15],activities[:,gid],'.-',label=typ,linewidth=1)
    ax.set_title('Actual central T4/T5 activity',fontsize=11);ax.set_xlabel('Euler activity time (ms after onset)');ax.legend(fontsize=6,ncol=2,facecolor='#172535',labelcolor='#dbeaf2')
    ax=axes[2,3];ax.axis('off');ax.text(0,.98,'3 actual joint commits\n17,304 PL integer checks: error 0\n11,536 feedback words verified\nGPU: current chemical + R39,901\nPL: H5,768 only\nOriginal DecoderGAVP after ACK\n\nSession completed / disconnected\nNot a real-time performance PASS\nNot a 485-step experiment',va='top',fontsize=10,color='#dbeaf2',linespacing=1.65)
    fig.suptitle('ACTUAL GPU + FPGA SHORT JOINT EXPERIMENT\nON60 | model steps 200-202 | displayed state k202 / activity 15 ms',color='#e3f3ff',fontsize=17,y=.965)
    fig.text(.02,.016,'OFFLINE VIEW OF ACTUAL COMPUTATION | run '+run.name+' | warm start: accepted Full output199; H quantized once',fontsize=9,color='#adc8d7')
    path=out/'actual_joint_short.png';fig.savefig(path,dpi=145,facecolor=fig.get_facecolor());plt.close(fig)
    with (out/'performance.csv').open('w',newline='',encoding='utf-8') as f:
        names=['model_step','core_cycles','adapter_cycles','PC_STEP_roundtrip_ns','PC_COMMIT_roundtrip_ns','PL_integer_error']
        writer=csv.DictWriter(f,fieldnames=names);writer.writeheader()
        for row in accepted['rows']:writer.writerow({k:row[k] for k in names})
    print(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--audit',required=True);p.add_argument('--output',required=True);a=p.parse_args();render(a.run,a.audit,a.output)
