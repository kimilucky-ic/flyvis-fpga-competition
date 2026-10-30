"""Read-only CPU validation and scientific figure of a newly completed recording run."""
import argparse
import csv
import json
import os
from pathlib import Path
import numpy as np
from live_protocol import host_path, load, require, sha, utc, write


def verify(root):
    root=Path(root);r=load(root/'result.json');identity=load(root/'run_identity.json')
    seal=load(root/'manifest.json');shutdown=load(root/'shutdown.json')
    for name,digest in seal['files_sha256'].items():
        p=(root/name).resolve();require(p.parent==root.resolve() and sha(p)==digest,'RESULT_HASH '+name)
    require(r['run_id']==identity['run_id']==seal['run_id']==shutdown['run_id'],'RUN_ID')
    require(r['status']=='PASS_ACTUAL_RECORDED_FULL_GPU' and r['device']['type']=='cuda'
        and r['actual_new_neural_computation'] and r['actual_new_decoder_computation']
        and not r['PL_execution'] and shutdown['GPU_work_completion_confirmed'],'GPU_RESULT')
    arrays={n:np.load(root/(n+'.npy'),mmap_mode='r',allow_pickle=False) for n in
        ('activities_full','flow','stimulus','time','activity_time','t4t5','final_state_full','source_frame_index')}
    s,f,x,t,at=[arrays[n] for n in ('activities_full','flow','stimulus','time','activity_time')]
    require(s.shape==(1,609,45669) and f.shape==(1,609,2,721) and x.shape==(1,609,1,721),'SHAPES')
    for a in (s,f,x,arrays['t4t5']):require(a.dtype==np.float32 and np.isfinite(a).all(),'DTYPE_FINITE')
    require(np.array_equal(t,np.arange(609)*.005) and np.array_equal(at,t+.005),'EULER_TIMES')
    require(np.array_equal(s[0][:,r['central_global_ids']],arrays['t4t5'])
        and np.array_equal(s[0,-1],arrays['final_state_full']),'ACTIVITY_IDENTITY')
    folder=host_path(load(root/'scope.json')['input_folder'])
    source_time=np.load(folder/'source_time.npy',allow_pickle=False)
    indices=np.searchsorted(source_time,t,side='right')-1
    require(np.array_equal(indices,arrays['source_frame_index']) and np.all(source_time[indices]<=t),'CAUSAL_TIME')
    require(np.array_equal(x,np.load(folder/'stimulus.npy',allow_pickle=False))
        and sha(folder/'stimulus.npy')==r['binding']['stimulus_sha256'],'INPUT_IDENTITY')
    commits=[json.loads(q) for q in (root/'step_commits.jsonl').read_text().splitlines()]
    require(len(commits)==609,'COMMIT_COUNT')
    for k,row in enumerate(commits):
        require(row['run_id']==r['run_id'] and row['step']==k and row['state_token']==k+1 and row['status']=='COMMITTED'
            and row['input_time_s']==t[k] and row['activity_time_s']==at[k],'COMMIT_SEQUENCE')
    chunks=load(root/'chunks.json');end=0
    for c in chunks:
        require(c['start_step']==end and end<c['stop_step']<=609 and c['stop_step']-end<=32,'CHUNK_SEQUENCE')
        end=c['stop_step']
    require(end==609 and r['neural_steps']==r['decoder_frames']==609,'COMPLETENESS')
    require(all(sha(pin['path'])==pin['sha256'] for pin in identity['source_pins'].values()),'ORIGINAL_SOURCE_CHANGED')
    report=dict(status='PASS_READONLY_RECORDED_GPU_EVIDENCE',utc=utc(),run_id=r['run_id'],
        verified_files=len(seal['files_sha256']),commits=609,chunks=len(chunks),activity_values=int(s.size),
        flow_values=int(f.size),causal_input_values=int(x.size),source_sha256_unchanged=True,
        network_weights_unchanged=r['network_weights_unchanged'],decoder_state_unchanged=r['decoder_state_unchanged'],
        new_GPU_computations_in_validator=0,LIVE_INTERACTIVE_GUI_PASS='NOT_RUN',REALTIME_STREAM_PASS='NOT_RUN')
    write(root/'validation.json',report)
    # Plot exact source pixels and scientific arrays; no neural outputs synthesized.
    os.environ['MPLCONFIGDIR']=str((root/'plot_cache').resolve())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    source=load(host_path(r['binding']['input_identity']['source_bundle_path'])/'source.json')
    frames=np.load(host_path(source['frames_path']),mmap_mode='r',allow_pickle=False)
    require(sha(source['frames_path'])==source['frames_sha256'],'RECORDED_PIXELS_CHANGED')
    with (folder/'input_hex_coordinates.csv').open(encoding='utf-8') as file:coords=list(csv.DictReader(file))
    px=np.array([float(q['plot_x']) for q in coords]);py=np.array([float(q['plot_y']) for q in coords])
    k=int(np.argmin(np.abs(x[0,:,0].mean(axis=1)-.5)))
    fig,ax=plt.subplots(2,3,figsize=(15,8),constrained_layout=True)
    ax[0,0].imshow(frames[indices[k]][:,:,::-1]);ax[0,0].axis('off')
    ax[0,0].set_title(f'Actual recorded frame {100+indices[k]} | source {source_time[indices[k]]:.3f}s')
    ax[0,1].set_facecolor('#b7c4ce')
    ax[0,1].scatter(px,py,c=x[0,k,0],cmap='gray',vmin=0,vmax=1,marker='h',s=29,edgecolors='#71808e',linewidths=.2)
    ax[0,1].set_title(f'Actual 721 inputs | model input {t[k]:.3f}s')
    ax[0,2].quiver(px,py,f[0,k,0],f[0,k,1],angles='xy',scale_units='xy',scale=1.5,width=.0025)
    ax[0,2].set_title(f'Official raw flow | post-update {at[k]:.3f}s')
    for a in ax[0,1:]:a.set_aspect('equal');a.set_xlabel('hex coordinates');a.grid(alpha=.15)
    for j in range(4):
        ax[1,0].plot(at,arrays['t4t5'][:,j],label=r['types'][j],lw=1.3)
        ax[1,1].plot(at,arrays['t4t5'][:,j+4],label=r['types'][j+4],lw=1.3)
    for j in (0,1):
        ax[1,j].set_title('Actual center '+('T4' if j==0 else 'T5')+' activities')
        ax[1,j].set_xlabel('Euler post-update time (s)');ax[1,j].set_ylabel('Original model activity')
        ax[1,j].axvline(at[k],color='gray',ls=':',lw=1);ax[1,j].legend();ax[1,j].grid(alpha=.2)
    ax[1,2].axis('off');ax[1,2].text(0,1,
        'NEW FULL GPU COMPUTATION\nRecorded input; this figure is offline replay\n\n'
        f"RTX 5060 Laptop | 45,669 neurons\n609 Euler steps | {r['simulation_duration_s']:.3f}s simulation\n"
        f"Model preload: {r['preload_s']:.3f}s\nNeural update: {r['neural_s']:.3f}s\nOfficial decoder: {r['decoder_s']:.3f}s\n"
        f"Compute loop: {r['compute_wall_s']:.3f}s\n\nWeights / decoder state unchanged\nLive camera / realtime: NOT_RUN\nFPGA: NOT_CONNECTED\n\nRun: {r['run_id'][:16]}…",va='top',fontsize=10)
    fig.suptitle('FlyVis: real recorded phone-screen input → original Full GPU → official optical flow',fontsize=15)
    fig.savefig(root/'recorded_gpu_result.png',dpi=140);plt.close(fig)
    write(root/'presentation.json',dict(run_id=r['run_id'],figure_step=k,source_index=int(indices[k]),
        figure_sha256=sha(root/'recorded_gpu_result.png'),validation_sha256=sha(root/'validation.json'),display_kind='OFFLINE_REPLAY_AFTER_NEW_GPU_COMPUTATION'))
    print(json.dumps(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');verify(p.parse_args().root)
