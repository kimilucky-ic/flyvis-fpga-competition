"""Frozen flow-only tracking, then evaluation. Saved data only; no model calls."""
from pathlib import Path
import csv,hashlib,json,time
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from readout import track,saliency
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PROJECT=ROOT.parent

def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):
    with (HERE/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False)

def metrics(pred,truth,a,b):
    rows=pred[(pred[:,0]>=a)&(pred[:,0]<b)];k=rows[:,0].astype(int)
    valid=rows[:,1]>0;error=np.full(len(rows),20.)
    error[valid]=np.linalg.norm(rows[valid,2:4]-truth[k[valid]],axis=1)
    median=float(np.median(error[valid])) if valid.any() else None
    return dict(n=len(rows),valid=int(valid.sum()),coverage=float(valid.mean()),
        within3_fraction=float(np.mean(valid&(error<=3))),
        median_valid_error_hex=median,MAE_valid_hex=float(error[valid].mean()) if valid.any() else None,
        p95_valid_error_hex=float(np.percentile(error[valid],95)) if valid.any() else None,
        miss_penalized_MAE_hex=float(error.mean()),
        pass_gate=bool(valid.mean()>=.9 and np.mean(valid&(error<=3))>=.8 and median is not None and median<=2))

def main():
    p=load('PREREGISTRATION.json');assert sha(HERE/'PREREGISTRATION.json')==load('FREEZE.json')['sha256']
    for rel,h in p['pins'].items():assert sha(PROJECT/rel)==h,rel
    execution=load('EXECUTION.json');assert execution['neural_steps']==6000 and not execution['GPU']
    grid=np.load(HERE/'GRID.npz');xy,roi=grid['xy'],grid['roi']
    distance=np.linalg.norm(xy[:,None]-xy[None],axis=2)
    neighbors=[np.flatnonzero(np.isclose(distance[i],1,atol=1e-8)) for i in range(721)]
    flow={c['id']:np.load(HERE/'runs'/c['id']/'flow.npy') for c in p['cases']}
    control_scores=np.stack([saliency(flow[c['id']])[200:,roi] for c in p['cases'][:2]])
    threshold=max(1e-5,3*float(np.quantile(control_scores,.999)))
    dump('CALIBRATION.json',dict(threshold=threshold,formula=p['readout']['threshold'],
        motion_results_seen_for_threshold=False,control_cases=[c['id'] for c in p['cases'][:2]]))
    permutation=np.random.default_rng(2026101804).permutation(721)
    np.save(HERE/'SPATIAL_PERMUTATION.npy',permutation)
    (HERE/'tracking').mkdir();predictions={};nulls={};scores={}
    # No truth file/image is opened until every prediction has been saved.
    for c in p['cases']:
        name=c['id'];pred,score=track(flow[name],xy,neighbors,roi,threshold)
        np.save(HERE/'tracking'/(name+'.npy'),pred);np.save(HERE/'tracking'/(name+'_saliency.npy'),score)
        predictions[name]=pred;scores[name]=score
        if c['kind']=='motion':
            prednull,_=track(flow[name][:,:,permutation],xy,neighbors,roi,threshold)
            nulls[name]=prednull;np.save(HERE/'tracking'/(name+'_permuted.npy'),prednull)
    dump('PREDICTIONS_FROZEN.json',dict(time_ns=time.time_ns(),truth_opened=False,original_images_opened=False,
        readout_inputs='flow, fixed geometry, fixed threshold; labels not available to readout API'))
    rows=[];truths={};controls=[]
    for c in p['cases']:
        name=c['id'];truth=np.load(HERE/'truth'/(name+'.npz'));truths[name]=truth
        pred=predictions[name]
        if c['kind']!='motion':
            selected=(pred[:,0]>=200)
            controls.append(dict(id=name,false_detection_fraction=float(pred[selected,1].mean()),
                pass_gate=bool(pred[selected,1].mean()<=.05),scope='calibration scenes only'))
            continue
        primary=metrics(pred,truth['position'],200,800)
        null=metrics(nulls[name],truth['position'],200,800)
        primarytruth=truth['position'][pred[(pred[:,0]>=200)&(pred[:,0]<800),0].astype(int)]
        constant=float(np.mean(np.linalg.norm(primarytruth,axis=1)<=3))
        settled=np.r_[np.flatnonzero((pred[:,0]>=240)&(pred[:,0]<490)),
                       np.flatnonzero((pred[:,0]>=540)&(pred[:,0]<790))]
        secondary=metrics(pred[settled],truth['position'],0,1000)
        stopsel=pred[:,0]>=840
        stopped_fraction=float(pred[stopsel,1].mean())
        # Diagnostic raw-flow direction at detected centers, no filtering by GT.
        angle_errors=[]
        for r in pred[(pred[:,0]>=200)&(pred[:,0]<800)]:
            if not r[1]:continue
            k=int(r[0]);v=truth['velocity'][k]
            local=np.linalg.norm(xy-r[2:4],axis=1)<=3
            fv=flow[name][k][:,local].mean(1)
            if np.linalg.norm(v)>0 and np.linalg.norm(fv)>1e-8:
                angle_errors.append(float(abs((np.degrees(np.arctan2(fv[1],fv[0])-np.arctan2(v[1],v[0]))+180)%360-180)))
        rows.append(dict(id=name,primary=primary,settled_secondary=secondary,
            stopped_detection_fraction=stopped_fraction,
            spatial_permutation=null,constant_origin_within3_fraction=constant,
            raw_flow_angle_MAE_deg=float(np.mean(angle_errors)) if angle_errors else None,
            raw_flow_angle_valid_frames=len(angle_errors)))
    mean_normal=float(np.mean([r['primary']['within3_fraction'] for r in rows]))
    mean_null=float(np.mean([r['spatial_permutation']['within3_fraction'] for r in rows]))
    mean_constant=float(np.mean([r['constant_origin_within3_fraction'] for r in rows]))
    passes=all(r['primary']['pass_gate'] for r in rows) and all(c['pass_gate'] for c in controls)
    passes=passes and mean_normal-mean_null>=.20 and mean_normal-mean_constant>=.20
    summary=dict(status='PASS_FIXED_SIMPLE_FLOW_TRACKER' if passes else 'FAIL_FIXED_SIMPLE_FLOW_TRACKER',
        evidence_execution='COMPLETE_REAL_ORIGINAL_FULL_CPU_AND_OFFICIAL_DECODER',cases=rows,controls=controls,
        mean_within3_fraction=mean_normal,mean_spatial_permutation_fraction=mean_null,
        mean_constant_origin_fraction=mean_constant,threshold=threshold,
        GPU=False,board=False,intrinsic_neural_object_identity='NOT_TESTED',
        interpretation='A failed fixed readout does not prove that FlyVis contains no usable spatial motion information.')
    dump('SUMMARY.json',summary)
    with (HERE/'METRICS.csv').open('x',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=['id','coverage','within3_fraction','median_valid_error_hex','MAE_valid_hex',
            'p95_valid_error_hex','pass_gate','permuted_within3','fixed_origin_within3','raw_flow_angle_MAE_deg'])
        writer.writeheader()
        for r in rows:
            d={k:v for k,v in r['primary'].items() if k in writer.fieldnames}
            writer.writerow(dict(id=r['id'],**d,permuted_within3=r['spatial_permutation']['within3_fraction'],
                fixed_origin_within3=r['constant_origin_within3_fraction'],raw_flow_angle_MAE_deg=r['raw_flow_angle_MAE_deg']))
    fig,axs=plt.subplots(2,2,figsize=(10,9))
    for ax,c,r in zip(axs.flat,p['cases'][2:],rows):
        name=c['id'];truth=truths[name]['position'];pr=predictions[name];valid=pr[:,1]>0
        ax.plot(truth[:,0],truth[:,1],color='black',lw=2,label='Actual target path')
        ax.plot(pr[:,2],pr[:,3],'.-',color='crimson',lw=.6,ms=2,label='Flow-only tracker (gaps=misses)')
        ax.scatter(xy[roi,0],xy[roi,1],s=2,color='gray',alpha=.2)
        ax.set(xlim=(-11,11),ylim=(-11,11),xlabel='x, neighbor spacings',ylabel='y, neighbor spacings',
            title=f"{name}\ncoverage={r['primary']['coverage']:.0%}, within3={r['primary']['within3_fraction']:.0%}, gate={r['primary']['pass_gate']}")
        ax.set_aspect('equal');ax.legend(fontsize=7)
    fig.suptitle('Actual full FlyVis + original decoder -> fixed causal downstream tracker\nGround truth is used only for scoring/plotting; CPU, no FPGA')
    fig.tight_layout();fig.savefig(HERE/'trajectories.png',dpi=150);plt.close(fig)
    # Genuine input frames plus saved predictions, not a live UI or invented demo.
    writer=cv2.VideoWriter(str(HERE/'tracking_review.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),20,(448,504))
    assert writer.isOpened()
    caps=[cv2.VideoCapture(str(HERE/'videos'/(c['id']+'.mp4'))) for c in p['cases'][2:]]
    try:
        for j in range(100):
            tile=np.full((504,448,3),235,np.uint8)
            for i,c in enumerate(p['cases'][2:]):
                k=int(predictions[c['id']][j,0]);caps[i].set(cv2.CAP_PROP_POS_FRAMES,k);ok,im=caps[i].read();assert ok
                truth=truths[c['id']]['position'][k];point=tuple(np.rint([111.5+6*truth[0],111.5-6*truth[1]]).astype(int))
                cv2.drawMarker(im,point,(0,190,0),cv2.MARKER_CROSS,12,1)
                row=predictions[c['id']][j]
                if row[1]:cv2.circle(im,tuple(np.rint([111.5+6*row[2],111.5-6*row[3]]).astype(int)),5,(0,0,230),1)
                x=(i%2)*224;y=(i//2)*252
                tile[y:y+224,x:x+224]=im
                cv2.putText(tile,c['id'],(x+3,y+237),cv2.FONT_HERSHEY_SIMPLEX,.32,(0,0,0),1)
                cv2.putText(tile,'offline CPU; green=truth red=estimate',(x+3,y+248),cv2.FONT_HERSHEY_SIMPLEX,.25,(0,0,0),1)
            writer.write(tile)
    finally:
        writer.release()
        for cap in caps:cap.release()
    # Eight original H-type mean activities, complete spatial layers.
    bundle=HERE.parent/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
    with (bundle/'nodes_full.csv').open(encoding='utf-8-sig') as f:types=np.array([r['cell_type'] for r in csv.DictReader(f)])
    a=np.load(HERE/'runs/HORIZONTAL/states.npy',mmap_mode='r')
    fig,axs=plt.subplots(2,4,figsize=(13,5),sharex=True)
    for ax,typ in zip(axs.flat,['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']):
        ax.plot((np.arange(1000)+1)*.005,a[:,types==typ].mean(1),lw=1);ax.set_title(typ)
        ax.axvline(1,color='gray',ls=':');ax.axvline(2.5,color='gray',ls=':');ax.axvline(4,color='gray',ls=':')
    fig.suptitle('Original continuous activity, mean of721 cells/type; HORIZONTAL\nMotion starts1s, reverses2.5s, stops4s; not spikes or tracking identity')
    fig.tight_layout();fig.savefig(HERE/'T4T5_activity.png',dpi=150);plt.close(fig)
    # Saved-data identity checks only, not another neural run.
    for record in execution['cases']:
        folder=HERE/'runs'/record['id']
        assert sha(folder/'states.npy')==record['full_state_sha256'] and sha(folder/'flow.npy')==record['flow_sha256']
    dump('SAVED_DATA_CHECK.json',dict(all6_state_and_flow_hashes=True,preregistration_pins=True,
        predictions_saved_before_truth_open=True,neural_steps=0,GPU=False))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
