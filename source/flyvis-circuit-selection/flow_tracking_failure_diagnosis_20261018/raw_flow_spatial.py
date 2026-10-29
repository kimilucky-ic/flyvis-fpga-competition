"""Parameter-free spatial signal checks, not a complete motion detector/tracker.

Always-returning peak estimates cannot establish absence of motion, identity,
or reliable tracking. A blank-subtracted field uses the known calibration run.
"""
from diagnose import *

def main():
    pr=load(OLD/'PREREGISTRATION.json');g=np.load(OLD/'GRID.npz');xy,roi=g['xy'],g['roi']
    blank=np.load(OLD/'runs/CAL_BLANK/flow.npy').astype(float)
    steps=np.arange(9,1000,10);rows=[]
    for c in pr['cases'][2:]:
        name=c['id'];f=np.load(OLD/'runs'/name/'flow.npy').astype(float)
        truth=np.load(OLD/'truth'/(name+'.npz'))['position']
        out={}
        for kind,score in [('raw_flow_norm',np.linalg.norm(f,axis=1)),
                           ('blank_residual_norm',np.linalg.norm(f-blank,axis=1))]:
            peak=xy[roi[np.argmax(score[steps][:,roi],axis=1)]]
            # All pixels above half current peak: no predicted-position gate.
            centroids=[]
            for k in steps:
                mask=score[k,roi]>=.5*score[k,roi].max()
                selected=roi[mask];weights=score[k,selected]
                centroids.append((weights[:,None]*xy[selected]).sum(0)/weights.sum())
            centers=np.asarray(centroids)
            out[kind]=dict(peak=evaluate(peak,truth,steps),half_peak_centroid=evaluate(centers,truth,steps))
            np.savez(HERE/(name+'_'+kind+'.npz'),steps=steps,peak=peak,half_peak_centroid=centers)
        rows.append(dict(id=name,diagnostics=out))
    d=dict(scope='POST_DIAGNOSIS_RAW_FIELD_SPATIAL_INFORMATION_CHECK_NOT_FUNCTIONAL_PASS',
        rule='No ground truth used in maxima/centroids; all units thresholds are fixed half-peak. Always produces a position, so NOT a detector or validated tracker.',
        baseline='blank_residual uses separately saved known white-background control, not candidate future neural truth',
        cases=rows,neural_steps=0,GPU=False,board=False)
    dump('RAW_FLOW_SPATIAL.json',clean(d))
    fig,ax=plt.subplots(figsize=(11,4.5));x=np.arange(4);old=load(OLD/'SUMMARY.json')
    normal=[c['primary']['within3_fraction'] for c in old['cases']]
    raw=[r['diagnostics']['raw_flow_norm']['peak']['primary']['within3'] for r in rows]
    residual=[r['diagnostics']['blank_residual_norm']['peak']['primary']['within3'] for r in rows]
    for offset,vals,label in [(-.23,normal,'Frozen complete tracker'),(0,raw,'Raw flow magnitude peak (diagnostic)'),
        (.23,residual,'Blank-residual peak (diagnostic)')]:
        bars=ax.bar(x+offset,vals,.23,label=label)
        for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.1%}',ha='center',fontsize=8)
    ax.set_xticks(x,[r['id'] for r in rows],fontsize=8);ax.set_ylim(0,1.16)
    ax.set_ylabel('All60 motion readouts within3neighbor spacings')
    ax.set_title('Where is position information lost? Saved original optical flow only\nPeak diagnostics always return a position; they are NOT newly validated trackers',fontsize=10)
    ax.legend(loc='upper center',fontsize=8,ncol=3);fig.tight_layout();fig.savefig(HERE/'raw_flow_spatial.png',dpi=150);plt.close(fig)
    print(json.dumps(clean(rows),indent=2))

if __name__=='__main__':main()
