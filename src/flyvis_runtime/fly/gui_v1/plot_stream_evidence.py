"""Static plot of saved real GPU evidence, explicitly NOT a live UI screenshot."""
import os
import numpy as np
from live_protocol import HERE,load,require,sha
from spatial_state import SpatialRegistry

def main():
    out=HERE/'evidence/continuous_20261012';root=HERE/'runtime/live/11e08322d3e74f4399b108a879447a4e/stream'
    path,p=next((p,load(p)) for p in (root/'snapshots').glob('*.json') if load(p)['step_id']==181)
    data=np.load(path.with_suffix('.npz'),allow_pickle=False);m=SpatialRegistry();values=m.extract(data['full'])
    m.validate({**p['spatial'],'values':values.tolist()},p['run_id'],181,.91,'Full')
    source=root/'sources'/f"{p['source']['sequence']:06}.png";require(sha(source)==p['source']['png_sha256'],'SOURCE_CHANGED')
    os.environ['MPLCONFIGDIR']=str(HERE/'runtime/plot_cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    fig,axes=plt.subplots(3,4,figsize=(16,10),facecolor='#101a25');uv=np.array([[r['u'],r['v']] for r in m.nodes[:721]])
    x=1.5*uv[:,1];y=-np.sqrt(3)*(uv[:,0]+uv[:,1]/2)
    for ax in axes.flat:ax.set_facecolor('#101a25');ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
    axes[0,0].imshow(Image.open(source));axes[0,0].set_title('Actual digital source PNG',color='white')
    axes[0,1].scatter(x,y,c=data['input'],cmap='gray',vmin=0,vmax=1,marker='h',s=27);axes[0,1].set_title('Official BoxEye: 721 inputs',color='white')
    axes[0,2].quiver(x,y,data['flow'][0],data['flow'][1],color='#73daf8',angles='xy',scale_units='xy',scale=1);axes[0,2].set_title('Official DecoderGAVP raw flow',color='white')
    axes[0,3].axis('off');axes[0,3].text(0,1,f"ARCHIVED ACTUAL COMPUTATION\nOFFLINE REPLAY / FAILED RUN\n\nFull CUDA | k181 / token182\nInput 0.905 s / activity 0.910 s\nSource frame {p['source']['sequence']}\n5,768 T4/T5 / 45,669 total\n\nRun {p['run_id'][:16]}...\nFPGA NOT_CONNECTED\nNo REALTIME_STREAM_PASS",color='white',va='top',fontsize=11,transform=axes[0,3].transAxes)
    for i,typ in enumerate(m.public()['types']):
        ax=axes.flat[4+i];s=ax.scatter(x,y,c=values[i*721:(i+1)*721],cmap='coolwarm',vmin=-1,vmax=1,marker='h',s=27);ax.set_title(typ+' / 721 actual nodes',color='white')
    fig.suptitle('Original FlyVis spatial evidence - actual digital GPU snapshot, NOT a live screenshot',color='white',fontsize=16)
    fig.subplots_adjust(top=.92,hspace=.22,wspace=.12,bottom=.08);cax=fig.add_axes([.30,.025,.4,.018]);cb=fig.colorbar(s,cax=cax,orientation='horizontal');cb.ax.tick_params(colors='white');cb.set_label('signed activity (color clipped to +/-1; stored values unchanged)',color='white')
    fig.savefig(out/'actual_spatial_evidence.png',dpi=120,facecolor=fig.get_facecolor(),bbox_inches='tight');plt.close(fig)
    print(out/'actual_spatial_evidence.png')

if __name__=='__main__':main()
