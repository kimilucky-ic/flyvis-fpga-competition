"""Saved evidence summaries, explicit failures and figures. No neuron/decoder calls."""
from study import *

def main():
    p=load(HERE/'PREREGISTRATION.json');f=load(HERE/'ALGORITHM_FREEZE.json')
    summary=load(HERE/'SUMMARY.json');execution=load(HERE/'EXECUTION.json')
    assert sha(HERE/'tracker.py')==f['tracker_sha256'] and sha(HERE/'CALIBRATION.npz')==f['calibration_sha256']
    assert sha(HERE/'PREREGISTRATION.json')==f['prereg_sha256']
    assert load(HERE/'INPUT_GENERATION.json')['time_ns']>f['time_ns']
    assert load(HERE/'PREDICTIONS_FROZEN.json')['time_ns']>load(HERE/'RUN_STARTED.json')['time_ns']
    oldhash={r['input_sha256'] for r in load(OLD/'INPUT_MANIFEST.json')}
    novelty=[]
    for r in load(HERE/'INPUT_MANIFEST.json'):
        h=sha(HERE/'inputs'/(r['id']+'.npy'));assert h==r['input_sha256']
        is_new=h not in oldhash
        assert is_new==(r['id']!='WHITE_CONTROL')
        novelty.append(dict(id=r['id'],input_differs_from_all6_old_inputs=is_new,sha256=h))
    oldparams=np.load(OLD/'EFFECTIVE_MODEL.npz');newparams=np.load(HERE/'EFFECTIVE_MODEL.npz')
    same={k:bool(np.array_equal(oldparams[k],newparams[k])) for k in oldparams.files}
    assert all(same.values())
    assert np.array_equal(np.load(HERE/'INITIAL_STATE.npy'),np.load(OLD/'INITIAL_STATE.npy'))
    failures=[];pooled_n=pooled_valid=pooled_hit=0;errors=[];static=[];margins=[]
    for c in p['cases']:
        name=c['id'];pred=np.load(HERE/'predictions'/(name+'.npy'));k=pred[:,0].astype(int);times=k*.005
        if c['kind']!='motion':
            static.append(dict(id=name,scored_outputs=int((k>=200).sum()),
                scored_triggers=int(pred[k>=200,1].sum()),startup_0to1s_triggers=int(pred[k<200,1].sum()),
                startup_outputs=int((k<200).sum())))
            continue
        pos=np.load(HERE/'truth'/(name+'.npz'))['position'];active=(times>=c['onset'])&(times<c['stop'])
        valid=pred[:,1]>0;e=np.linalg.norm(pred[:,2:4]-pos[k],axis=1);hit=valid&(e<=3)
        pooled_n+=int(active.sum());pooled_valid+=int((active&valid).sum());pooled_hit+=int((active&hit).sum())
        errors.extend(e[active&valid].tolist())
        for j in np.flatnonzero(active&~hit):
            failures.append(dict(id=name,step_id=int(k[j]),input_t=float(times[j]),output_t=float(times[j]+.005),
                valid=bool(valid[j]),error_pixels=float(e[j]*6) if valid[j] else None,
                reason='MISS' if not valid[j] else 'POSITION_ERROR_OVER18PX'))
        row=next(r for r in summary['cases'] if r['id']==name)
        margins.append(dict(id=name,median_margin_pixels=12-row['primary']['median_valid_error_hex']*6))
    dump(HERE/'FAILURES.json',dict(scope='all new motion primary outputs, unchanged18px rule',
        total=len(failures),misses=sum(not r['valid'] for r in failures),
        position_errors=sum(r['valid'] for r in failures),events=failures))
    total_static=sum(r['scored_outputs'] for r in static);triggers=sum(r['scored_triggers'] for r in static)
    descriptive=dict(pooled_motion_outputs=pooled_n,pooled_valid=pooled_valid,pooled_within18px=pooled_hit,
        pooled_coverage=pooled_valid/pooled_n,pooled_within18px_fraction=pooled_hit/pooled_n,
        pooled_MAE_valid_pixels=float(np.mean(errors)*6),pooled_median_valid_pixels=float(np.median(errors)*6),
        old_tracker_case_passes=sum(r['old_tracker']['pass_gate'] for r in summary['cases']),
        new_tracker_case_passes=sum(r['primary']['pass_gate'] for r in summary['cases']),
        mean_old_tracker_within18px=float(np.mean([r['old_tracker']['within3_fraction'] for r in summary['cases']])),
        static_scored_outputs=total_static,static_scored_triggers=triggers,static_including_startup_description=static,
        median_gate_margins=margins,scope='descriptive saved-data summary; no new gates')
    dump(HERE/'DESCRIPTIVE_SUMMARY.json',descriptive)
    dump(HERE/'FINAL_SAVED_AUDIT.json',dict(status='PASS_FROZEN_ALGORITHM_INPUT_AND_MODEL_IDENTITY_CHECK',
        all9_new_inputs_distinct_from_old=True,white_control_deliberately_matches_old=True,novelty=novelty,
        old_and_new_effective_model_array_bitwise_equal=same,full_initial_state_equal=True,
        algorithm_calibration_prereg_SHA_unchanged=True,freeze_precedes_video_generation=True,
        ordinary_predictions_saved_before_truth_scoring=True,all10_state_flow_hashes_already_checked=load(HERE/'SAVED_DATA_CHECK.json'),
        new_neural_steps=0,GPU=False,board=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x=np.arange(6);fig,ax=plt.subplots(figsize=(11,4.5))
    for off,label,values in [(-.18,'Original postprocessor on SAME new flow',[r['old_tracker']['within3_fraction'] for r in summary['cases']]),
        (.18,'Frozen revised postprocessor',[r['primary']['within3_fraction'] for r in summary['cases']])]:
        bars=ax.bar(x+off,values,.36,label=label)
        for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.015,f'{v:.1%}',ha='center',fontsize=8)
    ax.axhline(.8,color='gray',ls='--',lw=1,label='Unchanged80% within18px gate')
    ax.set_xticks(x,[r['id'] for r in summary['cases']],fontsize=8);ax.set_ylim(0,1.16)
    ax.set_ylabel('Fraction of ALL motion outputs within18pixels')
    ax.set_title('Same original FlyVis/decoder, different postprocessing;6 genuinely new motion clips\nThis is controlled white-background CPU validation, not real-time/camera/FPGA proof',fontsize=10)
    ax.legend(fontsize=7,ncol=3,loc='lower right');fig.tight_layout();fig.savefig(HERE/'new_comparison.png',dpi=150);plt.close(fig)
    cap=cv2.VideoCapture(str(HERE/'new_tracking_review.mp4'));assert cap.isOpened()
    assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==100 and np.isclose(cap.get(cv2.CAP_PROP_FPS),20)
    cap.set(cv2.CAP_PROP_POS_FRAMES,39);ok,frame=cap.read();assert ok and frame.shape==(504,672,3)
    cv2.imwrite(str(HERE/'review_frame39.png'),frame);cap.release()
    print(json.dumps(descriptive,indent=2))

if __name__=='__main__':main()
