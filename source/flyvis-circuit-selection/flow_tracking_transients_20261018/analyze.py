"""Bounded saved-data diagnosis. No FlyVis, decoder, GPU, or board invocation."""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MPLBACKEND='Agg', PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import csv, hashlib, importlib.util, json, time
import numpy as np

HERE=Path(__file__).resolve().parent
source=HERE.parent/'flow_tracking_refinement_20261018'
PILOT=HERE.parent/'flow_tracking_pilot_20261018'
PROJECT=HERE.parents[2]

def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p, value):
    with (HERE/p).open('x', encoding='utf-8') as f: json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def last_on(values, mask, times):
    k=np.flatnonzero(values&mask);return float(times[k[-1]]) if len(k) else None

def main():
    start=time.perf_counter();manifest=load(source/'DELIVERY_MANIFEST.json')
    pins={r['path'].replace('\\','/'):r['sha256'] for r in manifest['files']}
    p=load(source/'PREREGISTRATION.json');cal=dict(np.load(source/'CALIBRATION.npz'))
    grid=np.load(PILOT/'GRID.npz');xy,roi=grid['xy'],grid['roi'];steps=np.arange(9,1000,10);t=np.arange(1000)*.005
    old=module(source/'tracker.py','frozen_tracker');records=[];pin_checks={}
    for name in ['tracker.py','CALIBRATION.npz','PREREGISTRATION.json','EXECUTION.json']:
        assert sha(source/name)==pins[name];pin_checks[name]=pins[name]
    dump('ANALYSIS_PLAN.json',dict(created_ns=time.time_ns(),mode='retrospective_existing_data_diagnosis_not_holdout',
        source_manifest_sha256=sha(source/'DELIVERY_MANIFEST.json'),
        questions=['input constancy versus neural/decoder relaxation','100ms difference and50ms EMA memory','does coordinate smoothing cause valid output','causal known-input stillness veto versus flow-only changes'],
        fixed_gates=p['metrics'],dt=.005,all_cases=[c['id'] for c in p['cases']],
        no_new_inputs=True,no_neural_or_decoder_calls=True,GPU=False,board=False,
        variants_planned=['original','flow-only subtract fixed white temporal template, same threshold','flow-only remove EMA, same100ms difference and threshold','same original location plus causal100ms sampled-input stillness veto'],
        input_veto='only motion validity; consumes current/past721 samples, no pixels used for position, no truth/time-of-motion labels; less than half one3x3-mean8bit quantum treated unchanged',
        limits='all videos now seen; no new generalization or model accuracy PASS; no threshold grid search'))
    (HERE/'series').mkdir()
    for case in p['cases']:
        name=case['id'];folder=source/'runs'/name
        for rel in [f'runs/{name}/flow.npy',f'inputs/{name}.npy',f'predictions/{name}.npy']:
            assert sha(source/rel)==pins[rel];pin_checks[rel]=pins[rel]
        f=np.load(folder/'flow.npy').astype(float);x=np.load(source/'inputs'/(name+'.npy')).astype(float)
        pred=np.load(source/'predictions'/(name+'.npy'));recomputed,_=old.run(f,xy,roi,cal)
        assert np.allclose(pred,recomputed,rtol=0,atol=0,equal_nan=True)
        background=np.empty_like(f);background[:200]=cal['background_prefix'];background[200:]=cal['background_steady']
        residual=f-background;raw=np.zeros((1000,721));res=np.zeros_like(raw);ema=np.zeros_like(raw)
        delta=np.zeros(1000);input_range=np.zeros(1000)
        for k in range(1000):
            if k>=20:
                raw[k]=np.linalg.norm(f[k]-f[k-20],axis=0)
                res[k]=np.linalg.norm(residual[k]-residual[k-20],axis=0)
                input_range[k]=np.ptp(x[k-20:k+1],axis=0).max()
            if k:delta[k]=np.max(np.abs(x[k]-x[k-1]))
            ema[k]=(1-.005/.055)*(ema[k-1] if k else 0)+.005/.055*raw[k]
        corrected_ema=np.zeros_like(res)
        for k in range(1000):corrected_ema[k]=(1-.005/.055)*(corrected_ema[k-1] if k else 0)+.005/.055*res[k]
        assert np.array_equal(pred[:,8],ema[steps][:,roi].max(1))
        # Inspect existing full state via memory map, no recurrence/re-decoding.
        states=np.load(folder/'states.npy',mmap_mode='r');state_rms=np.zeros(1000);state_step_max=np.zeros(1000)
        prev=np.load(source/'INITIAL_STATE.npy').astype(float)
        for k in range(1000):
            a=np.asarray(states[k],float);d=a-prev;state_rms[k]=np.sqrt(np.mean(d*d));state_step_max[k]=np.abs(d).max();prev=a
        del states
        locok=(pred[:,9]>=float(cal['location_floor']))&(pred[:,7]>=3)
        threshold=float(cal['motion_threshold']);v=pred[:,1]>0
        noema=locok&(raw[steps][:,roi].max(1)>=threshold)
        corrected=locok&(corrected_ema[steps][:,roi].max(1)>=threshold)
        dt=.005
        if case['kind']=='motion':
            stop=case['stop'];stationary=t>=stop;late=steps*dt>=stop+.2;start_mask=steps*dt<case['onset'];active=(steps*dt>=case['onset'])&(steps*dt<stop)
            tail=steps*dt>=stop
        else:
            stop=0;stationary=np.ones(1000,bool);late=steps>=200;start_mask=steps<200;active=np.zeros(100,bool);tail=np.ones(100,bool)
        exact_tail=np.flatnonzero(np.maximum.accumulate(delta[::-1])[::-1]>0)
        final_change=int(exact_tail[-1]) if len(exact_tail) else None
        row=dict(id=name,kind=case['kind'],recomputed_predictions_exact=True,
            input_unique_frames=int(len(np.unique(x,axis=0))),input_constant_entire_clip=bool(np.all(delta==0)),
            last_input_sample_change_t=None if final_change is None else float(t[final_change]),
            stop_input_t=float(stop),input_changes_after_stop=int(np.count_nonzero(delta[stationary])),
            input_stationary_max_delta=float(delta[stationary].max()),
            original_startup_or_premotion_triggers=int(v[start_mask].sum()),startup_or_premotion_outputs=int(start_mask.sum()),
            original_late_triggers=int(v[late].sum()),late_outputs=int(late.sum()),
            without_EMA_late_triggers=int(noema[late].sum()),background_corrected_late_triggers=int(corrected[late].sum()),
            original_last_tail_trigger_t=last_on(v,tail,steps*dt),
            without_EMA_last_tail_trigger_t=last_on(noema,tail,steps*dt),
            original_first_trigger_t=last_on(v,np.arange(100)==np.flatnonzero(v)[0],steps*dt) if v.any() else None,
            filtered_coordinates_cannot_trigger='valid depends only motion/peak/support, not p/v/gaps',
            counterfactual_mask_source='existing location/support retained; only confidence formula changed',
            late_state_step_RMS_peak=float(state_rms[stationary].max()),
            late_raw100ms_change_max=float(raw[stationary][:,roi].max()),
            late_ema_change_max=float(ema[stationary][:,roi].max()),
            state_final_step_RMS=float(state_rms[-1]))
        np.savez_compressed(HERE/'series'/(name+'.npz'),input_t=t,output_t=t+.005,
            input_step_max=delta,input_100ms_range=input_range,raw100_max=raw[:,roi].max(1),
            ema100_max=ema[:,roi].max(1),white_corrected_ema100_max=corrected_ema[:,roi].max(1),
            state_step_RMS=state_rms,state_step_max=state_step_max,output_step=steps,
            original_valid=v,noema_valid=noema,white_corrected_valid=corrected,location_peak=pred[:,9])
        records.append(row);print('DIAGNOSED',name,flush=True)
    dump('DIAGNOSIS.json',dict(cases=records,seconds=time.perf_counter()-start,
        source_decoder='original DecoderGAVP eval is frame-local Conv2d/BatchNorm(eval)/activation, no temporal state; source forward flattens sample and frame dimensions',
        neuron_model='continuous Euler carries state; input held constant does not imply immediate equilibrium',
        static_codec_noise_ruled_out_by_exact_samples=all(r['input_constant_entire_clip'] for r in records if r['kind']!='motion'),
        state_hash_scope='existing sealed full-state SHA retained; current diagnosis sequentially reads those arrays without neural recomputation; lightweight file identities and flow/input hashes freshly checked',
        no_new_neural_steps=True,no_new_decoder_calls=True,GPU=False,board=False))
    dump('SOURCE_PINS.json',dict(source_manifest_sha256=sha(source/'DELIVERY_MANIFEST.json'),freshly_checked_files=pin_checks))
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
