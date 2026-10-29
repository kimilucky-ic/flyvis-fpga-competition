"""Post-result descriptive checks/figures only; no changed gates or neural calls.

ROI-only shuffle addresses a limitation of preregistered whole-retina shuffle:
whole-retina shuffle also changes which amplitudes fall inside the331 ROI.
"""
from pathlib import Path
import json
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from readout import track
HERE=Path(__file__).resolve().parent

def main():
    p=json.loads((HERE/'PREREGISTRATION.json').read_text(encoding='utf-8-sig'))
    summary=json.loads((HERE/'SUMMARY.json').read_text())
    grid=np.load(HERE/'GRID.npz');xy,roi=grid['xy'],grid['roi']
    dist=np.linalg.norm(xy[:,None]-xy[None],axis=2)
    neighbors=[np.flatnonzero(np.isclose(dist[i],1,atol=1e-8)) for i in range(721)]
    perm=np.arange(721);perm[roi]=np.random.default_rng(2026101804).permutation(roi)
    np.save(HERE/'ROI_ONLY_PERMUTATION.npy',perm)
    controls=[];snapshots=[]
    for c in p['cases'][2:]:
        name=c['id'];f=np.load(HERE/'runs'/name/'flow.npy')
        pr,s=track(f[:,:,perm],xy,neighbors,roi,summary['threshold'])
        np.save(HERE/'tracking'/(name+'_roi_only_permuted.npy'),pr)
        truth=np.load(HERE/'truth'/(name+'.npz'))['position']
        selected=(pr[:,0]>=200)&(pr[:,0]<800);k=pr[selected,0].astype(int);q=pr[selected]
        error=np.linalg.norm(q[:,2:4]-truth[k],axis=1);valid=q[:,1]>0
        original_scores=np.load(HERE/'tracking'/(name+'_saliency.npy'))
        controls.append(dict(id=name,coverage=float(valid.mean()),within3_fraction=float(np.mean(valid&(error<=3))),
            roi_score_sorted_arrays_exact=bool(np.allclose(np.sort(s[:,roi],axis=1),np.sort(original_scores[:,roi],axis=1),atol=0,rtol=0))))
        pred=np.load(HERE/'tracking'/(name+'.npy'))
        for k in [349,649]:snapshots.append((name,k,f[k],original_scores[k],truth[k],pred[k//10]))
    static=[]
    for c in p['cases'][:2]:
        x=np.load(HERE/'inputs'/(c['id']+'.npy')).astype(float)[200:]
        static.append(dict(id=c['id'],actual_temporal_RMS_float64_mean=float(np.sqrt(np.mean((x-x.mean(0))**2))),
            explanation='Preparation used float32 mean and can report numerical cancellation as tiny apparent temporal jitter; input files unchanged.'))
    hit=sum(round(r['primary']['within3_fraction']*r['primary']['n']) for r in summary['cases'])
    valid=sum(r['primary']['valid'] for r in summary['cases'])
    mae=sum(r['primary']['MAE_valid_hex']*r['primary']['valid'] for r in summary['cases'])/valid
    d=dict(scope='POST_RESULT_DESCRIPTIVE_NO_PREREG_GATE_OR_MODEL_CHANGE',neural_steps=0,GPU=False,
        ROI_only_shuffle=controls,ROI_only_shuffle_mean_within3=float(np.mean([r['within3_fraction'] for r in controls])),
        all_motion_readouts=240,within3_count=hit,valid_count=valid,
        pooled_MAE_valid_hex=mae,pooled_MAE_valid_pixels=mae*6,static_input_check=static,
        global_shuffle_limit='Preregistered global721 shuffle changes amplitudes inside331 ROI as well as locations; ROI-only supplementary control preserves every ROI saliency distribution.')
    with (HERE/'DESCRIPTIVE_DIAGNOSTICS.json').open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,allow_nan=False)
    fig,axs=plt.subplots(2,4,figsize=(13,7),sharex=True,sharey=True)
    vmax=max(s[3][roi].max() for s in snapshots)
    for j,(name,k,flow,score,truth,pred) in enumerate(snapshots):
        col=j//2;row=j%2;ax=axs[row,col]
        scatter=ax.scatter(xy[roi,0],xy[roi,1],c=score[roi],s=13,vmin=0,vmax=vmax,cmap='viridis')
        magnitude=np.linalg.norm(flow[:,roi],axis=0);arrows=flow[:,roi]/np.maximum(magnitude,1e-9)
        ax.quiver(xy[roi,0],xy[roi,1],arrows[0],arrows[1],alpha=.45,scale=22,width=.004)
        ax.add_patch(plt.Circle(truth,2,fill=False,color='limegreen',lw=1.8))
        if pred[1]:ax.plot(pred[2],pred[3],'rx',ms=9,mew=2)
        ax.set_title(name+f'\ninput t={k*.005:.3f}s',fontsize=9);ax.set_aspect('equal')
    fig.suptitle('Actual original decoder flow: unit-length direction arrows; color=causal saliency\nGreen=true disk extent; red=flow-only estimate; descriptive fixed snapshots, not selection for scoring',fontsize=10)
    fig.tight_layout(rect=(0,0,.92,.92));fig.colorbar(scatter,ax=axs,shrink=.65,label='Saliency (original output units)')
    fig.savefig(HERE/'flow_spatial.png',dpi=150);plt.close(fig)
    cap=cv2.VideoCapture(str(HERE/'tracking_review.mp4'))
    assert cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==100
    assert np.isclose(cap.get(cv2.CAP_PROP_FPS),20)
    cap.set(cv2.CAP_PROP_POS_FRAMES,39);ok,frame=cap.read();assert ok and frame.shape==(504,448,3)
    cv2.imwrite(str(HERE/'tracking_review_frame39.png'),frame);cap.release()
    print(json.dumps(d,indent=2))

if __name__=='__main__':main()
