"""Fixed saved-data figures. No neural or decoder calls."""
from core import *
import video_io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size':10,'axes.spines.right':False,'axes.spines.top':False})
summary=load(HERE/'SUMMARY.json'); cases=load(HERE/'INPUTS.json'); mapping=ref.mapping()
uv=mapping['grid_uv']; x=np.sqrt(3)/2*uv[1]; y=-(uv[0]+uv[1]/2)
motion=[r for r in summary['records'] if r['group']=='motion']
fig,axes=plt.subplots(3,1,figsize=(12,11),layout='constrained')
for ax,window in zip(axes,['active','stopped','allpost']):
    values=[]
    for r in motion:
        v=r['windows'].get(window,{}).get('flow',{}).get('field_error_E')
        values.append(np.nan if v is None else v)
    ax.bar(np.arange(8),values,color=['#267e78' if r['pass_gate'] else '#bc553c' for r in motion])
    if window=='active':
        for i,r in enumerate(motion):
            local=r['windows'].get(window,{}).get('foreground_flow')
            if local and local['field_error_E'] is not None:
                ax.scatter(i,local['field_error_E'],marker='D',color='#56237d',zorder=4,label='Local foreground ROI' if i==4 else None)
        ax.legend()
    ax.axhline(.2,ls='--',color='#bc553c',label='Preregistered .20 limit')
    ax.set_xticks(np.arange(8),[r['case'] for r in motion],rotation=25,ha='right',fontsize=8)
    ax.set_title(window+' | field error E vs original Full'); ax.grid(axis='y',alpha=.2)
fig.suptitle('Frozen CNN on actual MP4 inputs | eligible windows only; missing bars mean NOT EVALUABLE')
fig.savefig(HERE/'mp4_functional_gates.png',dpi=160); plt.close(fig)

chosen=['ON75_v12_full','ON75_local_static_texture','ON165_local_moving_background']
fig,axes=plt.subplots(3,2,figsize=(12,9),layout='constrained')
for row,name in enumerate(chosen):
    z=np.load(HERE/'runs'/name/'STEP_ERRORS.npy'); t=(np.arange(len(z))+1)*DT
    for col,index,title in [(0,0,'all H RMSE'),(1,6,'official flow component RMSE')]:
        ax=axes[row,col]; ax.plot(t,z[:,index],color='#277f85'); ax.axvspan(4,5,color='gray',alpha=.15)
        ax.set_title(name+' | '+title,fontsize=10); ax.set_xlabel('Model seconds'); ax.grid(alpha=.2)
fig.suptitle('Actual five-second closed loops | shaded: held final image | no state reset')
fig.savefig(HERE/'mp4_step_errors.png',dpi=160); plt.close(fig)

fig,axes=plt.subplots(2,2,figsize=(10,9),layout='constrained')
preview=chosen+['STATIC_TEXTURE5s']
for ax,name in zip(axes.flat,preview):
    case=next(c for c in cases if c['id']==name); cap=video_io.cv2.VideoCapture(case['video_path']); frame=None
    for k in range(251): okay,frame=cap.read()
    cap.release(); assert okay
    ax.imshow(video_io.cv2.cvtColor(frame,video_io.cv2.COLOR_BGR2RGB)); ax.set_axis_off(); ax.set_title(name+' | video frame250',fontsize=10)
fig.suptitle('Actual decoded MP4 images | controlled synthetic scenes, not natural footage')
fig.savefig(HERE/'decoded_mp4_examples.png',dpi=160); plt.close(fig)

case=next(c for c in cases if c['id']=='ON165_local_moving_background'); k=500
fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
arrays=[np.load(HERE/'runs'/case['id']/mode/'flow.npy') for mode in ['Full','CNN']]
if min(len(z) for z in arrays)>k:
    fields=[z[k] for z in arrays]; vmax=max(float(np.linalg.norm(z,axis=0).max()) for z in fields)
    for ax,field,mode in zip(axes,fields,['Full','CNN']):
        mag=np.linalg.norm(field,axis=0); unit=field/np.maximum(mag,1e-12)
        scatter=ax.scatter(x,y,c=mag,cmap='viridis',s=24,vmin=0,vmax=vmax); sel=np.arange(0,721,3)
        ax.quiver(x[sel],y[sel],unit[0,sel],unit[1,sel],color='white',scale=35,width=.003)
        ax.add_patch(plt.Circle(case['center'],3,fill=False,color='red',lw=1.5))
        ax.set_aspect('equal'); ax.set_title(mode+' | state t=2.505s'); ax.set_xlabel('Retinal spacing')
    fig.colorbar(scatter,ax=axes.tolist(),label='Original decoder magnitude (shared scale)')
else:
    for ax in axes: ax.text(.5,.5,'INCOMPLETE: no committed requested state',transform=ax.transAxes,ha='center')
fig.suptitle('Local motion with moving background | red: fixed foreground ROI; arrows: unit directions')
fig.savefig(HERE/'mp4_official_flow.png',dpi=160); plt.close(fig)
print('SAVED_4_SCIENTIFIC_PLOTS_NO_NEURAL_COMPUTATION')
