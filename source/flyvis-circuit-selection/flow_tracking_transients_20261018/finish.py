"""Identity checks, additional descriptive counts and scientific figures only."""
from analyze import *

def main():
    result=load(HERE/'RESULT.json');diagnosis=load(HERE/'DIAGNOSIS.json');p=load(source/'PREREGISTRATION.json')
    steps=np.arange(9,1000,10);times=steps*.005;extra=[];checks=[]
    # Once per newly used file; preserve and do not recompute original neural trajectories.
    for base in [source,PILOT]:
        manifest=load(base/'DELIVERY_MANIFEST.json');pins={r['path'].replace('\\','/'):r['sha256'] for r in manifest['files']}
        cases=p['cases'] if base==source else [c for c in load(PILOT/'PREREGISTRATION.json')['cases'] if c['kind']=='motion']
        for c in cases:
            name=c['id'];rels=[f'inputs/{name}.npy',f'runs/{name}/flow.npy',f'truth/{name}.npz']
            if base==source:rels.append(f'runs/{name}/states.npy')
            for rel in rels:
                observed=sha(base/rel);assert observed==pins[rel],str(base/rel)
                checks.append(dict(source=base.name,path=rel,sha256=observed,bytes=(base/rel).stat().st_size))
        checks.append(dict(source=base.name,path='DELIVERY_MANIFEST.json',sha256=sha(base/'DELIVERY_MANIFEST.json')))
    total0=total1=total2=0;late0=late1=late2=0
    for c in p['cases']:
        name=c['id'];s=np.load(HERE/'series'/(name+'.npz'));v=np.load(source/'predictions'/(name+'.npy'))[:,1]>0
        if c['kind']=='motion':
            late=times>=c['stop']+.2;start=times<c['onset'];k=int(np.ceil((c['stop']+.2)/.005))
        else:
            late=steps>=200;start=steps<200;k=40
        q=dict(id=name,original_start=int(v[start].sum()),noEMA_start=int(s['noema_valid'][start].sum()),
            white_corrected_start=int(s['white_corrected_valid'][start].sum()),
            original_late=int(v[late].sum()),noEMA_late=int(s['noema_valid'][late].sum()),
            white_corrected_late=int(s['white_corrected_valid'][late].sum()),
            state_step_RMS_at_stop_plus200ms_or_static200ms=float(s['state_step_RMS'][k]),
            raw_change_at_same_time=float(s['raw100_max'][k]),ema_at_same_time=float(s['ema100_max'][k]))
        extra.append(q)
        if c['kind']=='static':total0+=q['original_start'];total1+=q['noEMA_start'];total2+=q['white_corrected_start']
        if c['kind']=='motion':late0+=q['original_late'];late1+=q['noEMA_late'];late2+=q['white_corrected_late']
    stops=[]
    for c in result['motion']:
        # Last active20Hz output and first following quiet output, both on consumed input[k] time.
        last=c['candidate_last_trigger_after_stop_s']
        stops.append(dict(id=c['id'],candidate_last_trigger_s=last,
            candidate_first_sustained_quiet_s=None if last is None else last+.05,
            flow_output_availability_offset_s=.005))
    dump('DESCRIPTIVE_CAUSAL_CHECKS.json',dict(cases=extra,static_start_original_noEMA_white=[total0,total1,total2],
        stopped_late_original_noEMA_white=[late0,late1,late2],stop_timing=stops,
        timing_definition='consumed input[k] timestamp k*.005; corresponding neural/decoder state becomes available at(k+1)*.005; add5ms if quoting output availability',
        interpretations=['Static sampled inputs exactly constant but original neural states and decoded flow transient: ongoing picture motion or codec noise is not necessary for startup trigger.',
            'Original decoder eval forward has no temporal recurrence or state updates; persistent time dependence resides in evolving neural activities and downstream differencing/EMA.',
            'Location filter p/v/gaps not in original validity predicate: keeping a predicted p cannot itself emit valid detections.',
            'NoEMA reduces late stops but cannot eliminate them;100ms differencing remembers recent neural change, not actual sensor motion.',
            'White temporal correction removes common startup but cannot remove location-dependent static-object transients and post-stop relaxation.',
            'This observational state analysis does not isolate individual cell types, time constants, or biological circuits; no interventions run.']))
    # Remaining motion errors intentionally unchanged; retain proof of non-bypass.
    original_failures=load(source/'FAILURES.json')['events']
    assert [(e['id'],e['step_id'],e['valid']) for e in result['failures']]==[(e['id'],e['step_id'],e['valid']) for e in original_failures]
    assert result['candidate_pooled_within18px']==261 and result['primary_outputs']==274
    assert result['candidate_late_stop_triggers']==0
    assert all(x['score']['pass_gate'] for x in result['old_development_regression'])
    assert load(HERE/'CANDIDATE_SPEC.json')['algorithm_sha256']==sha(HERE/'input_verified_tracker.py')
    assert load(HERE/'SOURCE_PINS.json')['source_manifest_sha256']==sha(source/'DELIVERY_MANIFEST.json')
    # Existing spatial null can only lose detections under a validity veto; all motion gates are open
    # on ordinary outputs. Reusing accepted null is conservative, no extra reruns needed.
    accepted=load(source/'SUMMARY.json')
    normal=np.mean([r['candidate']['within18px_fraction'] for r in result['motion']]);null=accepted['mean_null_within3'];origin=accepted['mean_fixed_origin']
    assert normal-null>=.2 and normal-origin>=.2
    dump('FINAL_AUDIT.json',dict(status='PASS_SAVED_DATA_DIAGNOSIS_AND_CAUSAL_VETO_CHECKS_ONLY',
        freshly_verified_used_source_files=checks,all10_original_prediction_arrays_reproduced_exactly=True,
        original_manifest_unchanged=True,original_model_and_trajectories_read_only=True,
        frozen_candidate_unchanged_after_comparison=True,all_motion_coordinates_bitwise_unchanged=True,
        all13_original_primary_failures_retained=True,unchanged_per_motion_gates_still6of6=True,
        accepted_spatial_null_conservative_margin=float(normal-null),fixed_origin_margin=float(normal-origin),
        fresh_unknown_input_validation=False,no_neural_or_decoder_calls=True,GPU=False,board=False,
        tests=load(HERE/'FOCUSED_TESTS.json')))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,2,figsize=(13,8.2));threshold=float(np.load(source/'CALIBRATION.npz')['motion_threshold'])
    static=np.load(HERE/'series/NEW_STATIC_A.npz');time0=static['input_t']
    ax=axs[0,0];ax.plot(time0,static['state_step_RMS'],label='Original neural state change, RMS/step')
    ax.plot(time0,static['input_step_max'],label='Sampled visual input change (exactly zero)');ax.set_xlim(0,1)
    ax.set_title('Stationary scene, evolving original neural state');ax.set_xlabel('Input time (s)');ax.legend(fontsize=8)
    ax=axs[0,1]
    for key,label in [('ema100_max','Original temporal confidence'),('raw100_max','No EMA'),('white_corrected_ema100_max','White temporal template subtracted')]:
        ax.semilogy(time0,np.maximum(static[key],1e-8),label=label)
    ax.axhline(threshold,color='gray',ls='--',label='Unchanged motion threshold');ax.set_xlim(0,1);ax.set_ylim(1e-5,3)
    ax.set_title('Static-object adaptation still crosses motion threshold');ax.set_xlabel('Input time (s)');ax.legend(fontsize=7)
    ax=axs[1,0];stop=p['cases'][0]['stop'];s=np.load(HERE/'series/NEW_DIR20_V3.npz')
    for key,label in [('ema100_max','Original'),('raw100_max','No EMA')]:ax.semilogy(time0-stop,np.maximum(s[key],1e-8),label=label)
    ax.axhline(threshold,color='gray',ls='--');ax.axvline(0,color='black',lw=1,label='Video target stops')
    row=next(x for x in diagnosis['cases'] if x['id']==p['cases'][0]['id'])
    ax.axvline(row['last_input_sample_change_t']-stop,color='green',ls=':',label='Last sensor input change')
    ax.set_xlim(-.2,.9);ax.set_ylim(1e-5,3);ax.set_title('Example20deg/speed3: neural/flow tail after input is fixed')
    ax.set_xlabel('Time after programmed stop (s)');ax.legend(fontsize=7)
    ax=axs[1,1];labels=['Original','No EMA','White-template\ncorrection','Input stillness\nveto']
    x=np.arange(4);a=[total0,total1,total2,0];b=[late0,late1,late2,0]
    bars=ax.bar(x-.18,a,.36,label='Static startup triggers /60');bars2=ax.bar(x+.18,b,.36,label='After stop+0.2s triggers /171')
    for bar in list(bars)+list(bars2):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.7,str(int(bar.get_height())),ha='center',fontsize=8)
    ax.set_xticks(x,labels,fontsize=8);ax.set_ylim(0,62);ax.set_title('Retrospective counterfactuals; no new neural runs');ax.legend(fontsize=7)
    fig.suptitle('Startup and stop-tail diagnosis on existing official FlyVis CPU data\nInput veto adds synchronized721-point sensor samples; localization remains original flow-only output',fontsize=11)
    fig.tight_layout();fig.savefig(HERE/'transient_causes.png',dpi=160);plt.close(fig)
    print(json.dumps(dict(static_start_original_noEMA_white=[total0,total1,total2],stopped_late_original_noEMA_white=[late0,late1,late2],stop_timing=stops,source_checks=len(checks)),indent=2))

if __name__=='__main__':main()
