"""Bounded CPU-only diagnosis of two frozen-CNN failures; no optimization.

Cached Full states are used only in explicitly named diagnostic probes.
Fresh production CNN rollouts use the unchanged own-state ClosedLoop API.
"""
from pathlib import Path
import argparse, copy, csv, hashlib, importlib.util, json, os, sys, time, uuid

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'cnn_t4t5_mp4_holdout_20261016'
spec = importlib.util.spec_from_file_location('line4_accepted_mp4', OLD/'core.py')
accepted = importlib.util.module_from_spec(spec); spec.loader.exec_module(accepted)
np, torch = accepted.np, accepted.torch
ref = accepted.ref
dump, load, sha, digest = accepted.dump, accepted.load, accepted.sha, accepted.digest
MODEL, MODEL_SHA = accepted.MODEL, accepted.MODEL_SHA
FAIL_MOTION = 'OFF345_local_moving_background'
FAIL_STATIC = 'STATIC_TEXTURE5s'


def dependencies():
    files = {Path(__file__), OLD/'core.py', OLD/'video_io.py', OLD/'PREREGISTRATION.json',
             OLD/'FREEZE.json', OLD/'SUMMARY.json', OLD/'FAILURE_DIAGNOSTICS.json',
             OLD/'SAMPLER.npz', MODEL, accepted.BUNDLE/'initial_state_full.npy',
             accepted.BUNDLE/'expanded_parameters.npz', ref.OLD/'mapping.npz'}
    for module in list(sys.modules.values()):
        f = getattr(module, '__file__', None)
        if f and Path(f).is_file() and Path(f).suffix == '.py' and Path(f).resolve().is_relative_to(HERE.parent):
            files.add(Path(f).resolve())
    for case in [FAIL_MOTION, FAIL_STATIC]:
        files.add(OLD/'inputs'/(case+'.npy'))
        for mode in ['Full','CNN']:
            for name in ['states_raw.npy','flow.npy','RESULT.json','VALIDITY.json']:
                files.add(OLD/'runs'/case/mode/name)
    return sorted(files)


def check(deep=False):
    p = load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json') == load(HERE/'FREEZE.json')['sha256']
    for file, pin in p['pins'].items():
        s = Path(file).stat()
        assert (s.st_size,s.st_mtime_ns)==(pin['bytes'],pin['mtime_ns']),file
        if deep: assert sha(file)==pin['sha256'],file
    assert sha(MODEL)==MODEL_SHA
    assert not torch.cuda.is_initialized() and torch.get_num_threads()==1
    return p


def registration():
    assert not (HERE/'PREREGISTRATION.json').exists(), 'PRESERVE_RUN_NO_RETRY'
    resources = dict(RAM=accepted.memory(), disk_free_bytes=__import__('shutil').disk_usage(HERE).free)
    assert resources['RAM']['available_bytes']>=2*1024**3 and resources['disk_free_bytes']>=5*1024**3
    accepted.check(deep=True)
    oldcases={x['id']:x for x in load(OLD/'INPUTS.json')}
    cases=[]
    for name, values in [
        ('OFF345_BG_FROZEN',dict(background_speed=0)),
        ('OFF345_BG_GRAY',dict(background='gray')),
        ('OFF345_BG_ONLY',dict(target_absent=True)),
    ]:
        c=copy.deepcopy(oldcases[FAIL_MOTION]);c.update(values);c['id']=name
        c['provenance']='NEW_ACTUAL_MP4_MATCHED_COUNTERFACTUAL_NOT_HOLDOUT'
        c['input_method']='MP4'
        for key in ['path','sha256','video_path','video_sha256']:c.pop(key,None)
        cases.append(c)
    for name,kind in [('TEXTURE_EXACT_HOLD','hold'),('TEXTURE_SPATIAL_MEAN','mean')]:
        c=copy.deepcopy(oldcases[FAIL_STATIC]);c['id']=name;c['input_method']=kind
        c['provenance']='DECODED_RETINAL_INTERVENTION_NOT_A_NEW_MP4'
        for key in ['path','sha256','video_path','video_sha256']:c.pop(key,None)
        cases.append(c)
    files=dependencies()
    pins={str(p):dict(bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,sha256=sha(p)) for p in files}
    plan=dict(schema='line4-frozen-CNN-failure-causal-diagnosis/v1',cases=cases,pins=pins,
        model_SHA=MODEL_SHA, model_parameters=31168,dt=.005,CPU_threads=1,
        training_updates=0,GPU=0,board=0,old_failure_records_immutable=True,
        primary_windows='unchanged old331ROI; active320:720 and foregroundradius3 centered(4,0); allpost200:1000,stopped840:1000; staticadapted400:1000,late800:1000',
        inherited_gates='motionH<=.20,E<=.20,M[.8,1.2],fieldangle<=15; staticH/R/flow absoluteRMSE<=.002; no threshold adjustments',
        diagnostic_samples=list(range(0,1000,5)),
        teacher_probe='CNN(Full old), CNN(Full H + CNN R), CNN(CNN old), originalH(Full old), originalH(CNN old); separate offline diagnostics NEVER fed to production',
        evidence_rules=dict(background_motion_contribution='paired original-moving minus frozen-background foregroundE; >=.02 marked material in this pair, no population significance claim',
            jitter_primary='locked late H and flow RMSE each reduced>=50% relative original => material; <=10% reduction both => jitter not primary; otherwise mixed',
            spatial_primary='spatialmean passes both unchanged staticwindows and original fails => spatialcontrast associated contribution; this does not isolate all texture statistics',
            short_local_operator='teacher/own-state one-step defect and recurrence decomposition reported in absolute model units; no relative division by almost-zero static increment',
            feedback='error splitting is one chosen counterfactual path; RMS terms need not sum and are not causal percentages'),
        budget=dict(new_conditions=5,new_production_commits=10000,max_total_CPU_s=480,max_disk_GiB=4,retries=0),
        stop='one bounded diagnosis, preserve negatives; no retraining, new architecture, FPGA/GPU/GUI, source edits, or unseen-test accuracy claim')
    dump(HERE/'RESOURCE_CHECK.json',resources);dump(HERE/'PREREGISTRATION.json',plan)
    dump(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
    print(json.dumps(dict(stage='PREREGISTERED',cases=len(cases),sha256=sha(HERE/'PREREGISTRATION.json'),GPU=0,board=0)),flush=True)


def inputs():
    p=check();spec=importlib.util.spec_from_file_location('line4_video_io',OLD/'video_io.py')
    video=importlib.util.module_from_spec(spec);spec.loader.exec_module(video)
    # Explicit local copy: only foreground removal branch added to accepted renderer.
    original=(OLD/'video_io.py').read_text(encoding='utf-8')
    text=original.replace('picture=bg+aperture*(target-bg)',"picture=bg if case.get('target_absent',False) else bg+aperture*(target-bg)")
    assert text!=original
    (HERE/'video_render.py').write_text(text,encoding='utf-8',newline='\n')
    spec=importlib.util.spec_from_file_location('line4_paired_renderer',HERE/'video_render.py')
    render=importlib.util.module_from_spec(spec);spec.loader.exec_module(render)
    # The generator edit is specified in the frozen diagnostic source above.
    sampling=dict(np.load(OLD/'SAMPLER.npz')); base=np.load(OLD/'inputs'/(FAIL_STATIC+'.npy'))
    (HERE/'inputs').mkdir();(HERE/'videos').mkdir();records=[]
    for case in p['cases']:
        c=copy.deepcopy(case)
        if case['input_method']=='MP4':
            target=HERE/'videos'/(case['id']+'.mp4');render.render(target,case)
            x,meta=video.decode(target,sampling)
            c.update(video_path=str(target),video_sha256=sha(target),decode_metadata=meta)
        elif case['input_method']=='hold':
            x=base.copy();x[220:]=base[220]
            assert np.array_equal(x[:220],base[:220]) and np.array_equal(x[220:],np.broadcast_to(base[220],x[220:].shape))
            c['intervention']='preserve original0:220; hold actual decoded frame110 fromstep220; remove subsequent temporal codec variation'
        else:
            x=np.broadcast_to(base.mean(1,dtype=np.float64).astype(np.float32)[:,None],base.shape).copy()
            c['intervention']='everyframe spatialmean across721; preserve perframe mean and onset schedule; removes spatialcontrast'
        assert x.shape==(1000,721) and x.dtype==np.float32 and np.isfinite(x).all()
        f=HERE/'inputs'/(case['id']+'.npy');np.save(f,x)
        c.update(path=str(f),sha256=sha(f));records.append(c)
    dump(HERE/'INPUTS.json',records)
    print(json.dumps(dict(stage='INPUTS_READY',new_MP4=3,retinal_interventions=2)),flush=True)


def simulate():
    p=check(deep=True);began=time.perf_counter();run=uuid.uuid4().hex
    assert not (HERE/'runs').exists()
    model=ref.model_from(MODEL);m=ref.mapping();initial=torch.from_numpy(np.load(accepted.BUNDLE/'initial_state_full.npy'))
    decoder=ref.CPUDecoder();_,_,_,params=ref.source()
    records=[];guard_calls=0
    def forbidden(*a,**kw):
        nonlocal guard_calls
        guard_calls+=1;raise RuntimeError('NATIVE_H_FORBIDDEN_IN_PRODUCTION')
    for case in load(HERE/'INPUTS.json'):
        assert sha(case['path'])==case['sha256'];x=np.load(case['path'])
        for mode in ['Full','CNN']:
            assert time.perf_counter()-began<p['budget']['max_total_CPU_s']
            tick=time.perf_counter();out=HERE/'runs'/case['id']/mode;out.mkdir(parents=True)
            state=initial.clone();engine=None;native=None
            if mode=='Full':native=ref.OriginalTargets(params,np.arange(45669))
            else:engine=ref.ClosedLoop(ref.r_service(),ref.CNNService(model,m),initial,m,run+case['id'])
            values=np.lib.format.open_memmap(out/'states_raw.npy',mode='w+',dtype=np.float32,shape=(1000,45669))
            count=0;failure=None;original=ref.OriginalTargets.step
            if mode=='CNN':ref.OriginalTargets.step=forbidden
            try:
                with (out/'chain.jsonl').open('x',encoding='utf-8') as journal:
                    for k in range(1000):
                        if time.perf_counter()-began>p['budget']['max_total_CPU_s']:raise TimeoutError('BOUNDED_CPU_EXPERIMENT')
                        pixels=torch.from_numpy(x[k])
                        try:
                            if mode=='CNN':candidate,chain=engine.step(pixels,k)
                            else:
                                candidate=native.step(state,pixels)
                                if not torch.isfinite(candidate).all() or candidate.abs().max()>100:raise ValueError('STABILITY_ENVELOPE')
                                chain=dict(step=k,old=digest(state),input=digest(pixels),new=digest(candidate),time=k*.005,next_time=(k+1)*.005,committed=True)
                        except (ValueError,RuntimeError) as exc:failure=dict(step=k,error=repr(exc));break
                        state=candidate;values[k]=state.numpy();journal.write(json.dumps(chain)+'\n');count+=1
            finally:ref.OriginalTargets.step=original;values.flush()
            np.save(out/'final.npy',state.numpy())
            dump(out/'VALIDITY.json',dict(valid_rows=count,allocated_rows=1000,invalid_range=[count,1000],failure=failure))
            flow=decoder.decode(values[:count]);np.save(out/'flow.npy',flow)
            record=dict(case=case['id'],mode=mode,valid_steps=count,complete=count==1000,failure=failure,wall_s=time.perf_counter()-tick,
                run_uuid=run,actual_CPU=True,native_H_updates=0 if mode=='CNN' else native.calls,
                teacher_corrections=0,CNN_calls=engine.cnn.calls if engine else 0)
            dump(out/'RESULT.json',record);records.append(record);del values
            print(json.dumps(dict(stage='ACTUAL_CPU',**record)),flush=True)
    decoder.assert_unchanged();check()
    dump(HERE/'EXECUTION.json',dict(status='ACTUAL_CPU_PAIRED_DIAGNOSIS_COMPLETE',records=records,
        commits=sum(r['valid_steps'] for r in records),wall_s=time.perf_counter()-began,
        native_H_guard_violations=guard_calls,model_unchanged=True,decoder_unchanged=True,training_updates=0,GPU=0,board=0))


def probe():
    p=check();began=time.perf_counter();m=ref.mapping();model=ref.model_from(MODEL)
    cnn=ref.CNNService(model,m);_,_,_,params=ref.source();native=ref.OriginalTargets(params,m['H'])
    initial=np.load(accepted.BUNDLE/'initial_state_full.npy');H=m['H'];R=m['R'];summary={}
    decoder=ref.CPUDecoder();roi=np.load(accepted.ROI_PATH)
    for name in [FAIL_STATIC,FAIL_MOTION]:
        full=np.load(OLD/'runs'/name/'Full/states_raw.npy',mmap_mode='r')
        value=np.load(OLD/'runs'/name/'CNN/states_raw.npy',mmap_mode='r')
        pixels=np.load(OLD/'inputs'/(name+'.npy'))
        arrays={key:[] for key in ['teacher_defect','own_defect','R_input_effect','H_history_effect','saved_total_error']}
        rows=[];maxcal=0.;closure=0.;ownrepro=0.
        for k in p['diagnostic_samples']:
            f=torch.from_numpy(initial.copy() if k==0 else np.array(full[k-1],copy=True))
            v=torch.from_numpy(initial.copy() if k==0 else np.array(value[k-1],copy=True))
            mix=f.clone();mix[R]=v[R];stim=torch.from_numpy(pixels[k])
            tf=cnn.step(f).numpy();mx=cnn.step(mix).numpy();own=cnn.step(v).numpy()
            exact=native.step(f,stim).numpy();ownexact=native.step(v,stim).numpy()
            maxcal=max(maxcal,float(abs(exact-full[k,H]).max()))
            ownrepro=max(ownrepro,float(abs(own-value[k,H]).max()))
            d=tf-exact;r=mx-tf;h=own-mx;e=value[k,H]-full[k,H]
            closure=max(closure,float(abs(d+r+h-e).max()))
            for key,a in zip(arrays,[d,own-ownexact,r,h,e]):arrays[key].append(a.copy())
            rows.append(dict(step=k,time_s=(k+1)*.005,teacher_defect_RMS=float(np.sqrt(np.mean(d.astype(np.float64)**2))),
                own_defect_RMS=float(np.sqrt(np.mean((own-ownexact).astype(np.float64)**2))),
                R_input_effect_RMS=float(np.sqrt(np.mean(r.astype(np.float64)**2))),
                H_history_effect_RMS=float(np.sqrt(np.mean(h.astype(np.float64)**2))),
                total_H_error_RMS=float(np.sqrt(np.mean(e.astype(np.float64)**2))),
                original_H_increment_RMS=float(np.sqrt(np.mean((exact-f[H].numpy()).astype(np.float64)**2)))))
        arrays={k:np.asarray(v) for k,v in arrays.items()};steps=np.asarray(p['diagnostic_samples'])
        np.savez(HERE/(name+'_PROBES.npz'),steps=steps,H_global_ids=H,**arrays)
        dump(HERE/(name+'_PROBE_STEPS.json'),rows)
        assert maxcal<=1e-5 and ownrepro<=1e-6 and closure<=1e-5
        windows={}
        for window,(start,stop) in load(OLD/'INPUTS.json')[[x['id'] for x in load(OLD/'INPUTS.json')].index(name)]['windows'].items():
            chosen=(steps>=start)&(steps<stop)
            windows[window]={k:float(np.sqrt(np.mean(v[chosen].astype(np.float64)**2))) for k,v in arrays.items()}
            windows[window]['teacher_defect_by_type'] = np.sqrt(np.mean(arrays['teacher_defect'][chosen].reshape(-1,8,721).astype(np.float64)**2,axis=(0,2))).tolist()
        # Decoder-only counterfactuals; never alter a production neural trajectory.
        sample=steps[steps>=800] if name==FAIL_STATIC else steps[(steps>=320)&(steps<720)]
        f=np.array(full[sample],copy=True);v=np.array(value[sample],copy=True)
        hmix=f.copy();hmix[:,H]=v[:,H]
        rmix=f.copy();rmix[:,R]=v[:,R]
        ff=np.load(OLD/'runs'/name/'Full/flow.npy')[sample]
        cf=np.load(OLD/'runs'/name/'CNN/flow.npy')[sample]
        fh=decoder.decode(hmix);fr=decoder.decode(rmix)
        def flow_rms(a,b):return float(np.sqrt(np.mean((a[:,:,roi].astype(np.float64)-b[:,:,roi])**2)))
        np.savez(HERE/(name+'_DECODER_PROBES.npz'),steps=sample,Full=ff,CNN=cf,CNN_H_Full_R=fh,Full_H_CNN_R=fr)
        summary[name]=dict(windows=windows,original_H_vs_saved_Full_max_abs=maxcal,CNN_vs_saved_CNN_max_abs=ownrepro,
            decomposition_closure_max_abs=closure,decoder_counterfactual=dict(total_RMSE=flow_rms(cf,ff),
                CNN_H_Full_R_RMSE=flow_rms(fh,ff),Full_H_CNN_R_RMSE=flow_rms(fr,ff)),
            decoder_direct_H_types=[t for t in accepted.TYPES if t in decoder.contract['ordered_input_types']])
        print(json.dumps(dict(stage='DIAGNOSTIC_PROBES',case=name,checks=summary[name])),flush=True)
    decoder.assert_unchanged();check()
    dump(HERE/'PROBE_SUMMARY.json',dict(status='OFFLINE_SAME_OLD_DIAGNOSTICS_ONLY',cases=summary,
        CNN_diagnostic_calls=cnn.calls,original_H_diagnostic_calls=native.calls,production_commits=0,
        wall_s=time.perf_counter()-began,training_updates=0,GPU=0,board=0))


def score(case,root):
    m=ref.mapping();roi=np.load(accepted.ROI_PATH)
    full,cnn=[np.load(root/mode/'states_raw.npy',mmap_mode='r') for mode in ['Full','CNN']]
    ff,cf=[np.load(root/mode/'flow.npy',mmap_mode='r') for mode in ['Full','CNN']]
    rows=[]
    for k in range(1000):
        dh=cnn[k,m['H']].astype(np.float64)-full[k,m['H']]
        dr=cnn[k,m['R']].astype(np.float64)-full[k,m['R']]
        df=cf[k,:,roi].astype(np.float64)-ff[k,:,roi]
        rows.append([np.sqrt(np.mean(dh*dh)),np.sqrt(np.mean(dr*dr)),np.sqrt(np.mean(df*df))])
    error=np.asarray(rows)
    if root.is_relative_to(HERE):np.save(root/'STEP_ERRORS.npy',error)
    if case['group']=='static':
        windows={}
        for name,(a,b) in case['windows'].items():
            h,r,f=np.sqrt(np.mean(error[a:b]**2,axis=0))
            windows[name]=dict(H_RMSE=float(h),R_RMSE=float(r),flow_RMSE=float(f),pass_gate=bool(max(h,r,f)<=.002))
    else:
        windows=accepted.score_motion(case,full[:,m['H']],cnn[:,m['H']],ff,cf,roi,m)
    return dict(case=case['id'],source='NEW_PAIRED_CPU' if root.is_relative_to(HERE) else 'REUSED_ACCEPTED_ORIGINAL_RUN',
        group=case['group'],pass_gate=all(v['pass_gate'] for v in windows.values()),windows=windows,
        max_H_abs=float(abs(cnn[-1,m['H']]-full[-1,m['H']]).max()))


def analyze():
    p=check();oldcases={x['id']:x for x in load(OLD/'INPUTS.json')}
    records=[score(oldcases[n],OLD/'runs'/n) for n in [FAIL_MOTION,FAIL_STATIC]]
    for case in load(HERE/'INPUTS.json'):records.append(score(case,HERE/'runs'/case['id']))
    by={r['case']:r for r in records}
    foreground=lambda name:by[name]['windows']['active']['foreground_flow']['field_error_E']
    late=lambda name:by[name]['windows']['late']
    original=late(FAIL_STATIC);held=late('TEXTURE_EXACT_HOLD')
    reductions={k:1-held[k]/original[k] for k in ['H_RMSE','flow_RMSE']}
    if all(x>=.5 for x in reductions.values()):jitter='MATERIAL_IN_THIS_LOCKED_PAIR'
    elif all(x<=.1 for x in reductions.values()):jitter='NOT_PRIMARY_IN_THIS_LOCKED_PAIR'
    else:jitter='MIXED_OR_INCONCLUSIVE'
    conclusions=dict(background=dict(original_E=foreground(FAIL_MOTION),frozen_E=foreground('OFF345_BG_FROZEN'),
        gray_E=foreground('OFF345_BG_GRAY'),background_only_E=foreground('OFF345_BG_ONLY'),
        moving_minus_frozen_E=foreground(FAIL_MOTION)-foreground('OFF345_BG_FROZEN'),
        material_at_predeclared_002=foreground(FAIL_MOTION)-foreground('OFF345_BG_FROZEN')>=.02),
        static=dict(original_late=original,locked_late=held,relative_error_reductions=reductions,jitter_conclusion=jitter,
            spatial_mean=by['TEXTURE_SPATIAL_MEAN'],spatial_structure_contribution=by['TEXTURE_SPATIAL_MEAN']['pass_gate'] and not by[FAIL_STATIC]['pass_gate']))
    result=dict(status='DIAGNOSIS_COMPLETE_NOT_MODEL_RECOVERY',records=records,conclusions=conclusions,
        no_new_holdout_claim=True,model_unchanged=True,thresholds_unchanged=True,training_updates=0,GPU=0,board=0)
    dump(HERE/'SUMMARY.json',result)
    csvrows=[]
    for row in records:
        for window,v in row['windows'].items():
            if row['group']=='static':csvrows.append(dict(case=row['case'],window=window,scope='static',E=None,M=None,angle=None,H_RMSE=v['H_RMSE'],flow_RMSE=v['flow_RMSE'],passed=v['pass_gate']))
            else:
                for scope in ['flow','foreground_flow']:
                    if scope not in v:continue
                    f=v[scope];csvrows.append(dict(case=row['case'],window=window,scope=scope,E=f['field_error_E'],M=f['magnitude_ratio'],angle=f['angle_deg'],H_RMSE=None,flow_RMSE=None,passed=f['pass_gate']))
    with (HERE/'METRICS.csv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    print(json.dumps(conclusions,ensure_ascii=False,indent=2),flush=True)


def audit():
    p=check(deep=True);initial=np.load(accepted.BUNDLE/'initial_state_full.npy');total=0
    cases=load(HERE/'INPUTS.json')
    for c in cases:
        assert sha(c['path'])==c['sha256'];x=np.load(c['path'])
        for mode in ['Full','CNN']:
            out=HERE/'runs'/c['id']/mode;v=load(out/'VALIDITY.json');assert v['valid_rows']==1000 and v['failure'] is None
            states=np.load(out/'states_raw.npy',mmap_mode='r');lines=(out/'chain.jsonl').read_text(encoding='utf-8').splitlines()
            assert len(lines)==1000;previous=digest(initial)
            for k,line in enumerate(lines):
                row=json.loads(line);assert row['step']==k and row['old']==previous and row['input']==digest(x[k]) and row['new']==digest(states[k])
                assert row['time']==k*.005 and row['next_time']==(k+1)*.005 and row['committed']
                assert np.isfinite(states[k]).all() and abs(states[k]).max()<=100
                if mode=='CNN':assert row['native_H_updates']==0 and row['old_source']=='OWN_LIVE_STATE'
                previous=row['new'];total+=1
            assert np.array_equal(states[-1],np.load(out/'final.npy'))
    result=dict(status='PASS_SAVED_CPU_DIAGNOSIS_EVIDENCE',all_new_commits_checked=total,new_neural_steps_in_audit=0,
        original_failures_preserved=True,model_and_source_identity_verified=True,thresholds_unchanged=True,
        teacher_probes_are_not_production=True,training_updates=0,GPU=0,board=0)
    dump(HERE/'FINAL_AUDIT.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','run','analyze','audit']);args=parser.parse_args()
    try:
        if args.stage=='prepare':registration();inputs()
        elif args.stage=='run':simulate();probe()
        elif args.stage=='analyze':analyze()
        else:audit()
    except BaseException as exc:
        dump(HERE/('FAILURE_'+args.stage+'_'+str(time.time_ns())+'.json'),dict(error=repr(exc),automatic_retry=False,GPU=0,board=0))
        raise
