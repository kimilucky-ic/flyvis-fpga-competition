"""Bounded WSL host for GUI jobs; imports original compute cores only AFTER the shared lease.

Importing this file is CPU-only. Execution requires a freshly enabled user session.
Only explicitly pinned static graph files may be reused; no historical neural
activity, batch-campaign runner, camera capture, or board driver is used.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

import numpy as np
from live_protocol import Registry, canonical, checked_commit, host_path, load, require, sha, utc, validate_scope, write


def import_file(name,path):
    path=host_path(path);sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def run(session_path):
    session_path=host_path(session_path);root=session_path.parent;session=load(session_path)
    validate_scope(session)
    require(root.resolve().is_relative_to((Path(__file__).parent/'runtime/live').resolve()),'SESSION_WRITE_SCOPE')
    from realtime_timing import StartupTimings
    startup=StartupTimings(root,session['session_id'])
    with startup.measure('registry_and_frozen_source_validation'):registry=Registry();reg_sha=canonical(registry.data)
    require(root.is_relative_to(host_path(registry.data['pins']['full']['path']).parents[1]/'gui_v1/runtime/live'),'SESSION_WRITE_SCOPE')
    runner=import_file('flyvis_gui_existing_runner_lease',registry.path_for('runner_lease'))
    active=[None];device=[None];phase=['WAITING_FOR_SHARED_GPU'];end=threading.Event();monitor=[None]

    class GUILimitedLease(runner.Lease):
        # Reuse existing shared lock/probe/ledger. Never broaden its frozen A/B authorize().
        def init__(self):
            self.job=root;self.config={'campaign_id':'GUI_'+session['session_id'],'stage':'GUI_LIVE_SESSION','queue_s':15}
            self.ticket={'config':self.config,'identity_key':canonical(session),'job_dir':str(root),'scope':'new GUI session; not historical A/B'}
            self.last_camera_audit=-1.
        def check(self,operation='check'):
            validate_scope(session) # In-memory deadline check on every candidate.
            if monitor[0]:return monitor[0].check(operation)
            return self.audit(operation)
        def audit(self,operation='check'):
            validate_scope(session)
            audit=not session.get('camera_enabled') or time.monotonic()-self.last_camera_audit>=.25
            if audit:
                require(load(session_path)==session,'SESSION_IDENTITY_CHANGED');registry.unchanged()
                for name,digest in session.get('stream_adapter_sha256',{}).items():
                    require(name in ('live_protocol.py','checked_full.py','decoder_audit.py','stream_runtime.py','stream_renderer.py','prepared_camera_input.py','stream_cadence.py','stream_evidence.py','stream_wire.py','stream_bridge.py','stream_clock.py','stream_transport.py','realtime_timing.py','camera_stream_protocol.py','spatial_state.py','input_preparation.py','static_connectome.py') and sha(Path(__file__).parent/name)==digest,'STREAM_ADAPTER_CHANGED')
                controller=load(root/'controller.json')
                require(controller['session_id']==session['session_id'] and time.time()-controller['unix_time']<15,'CONTROLLER_DISCONNECTED')
                require(not runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists(),'RESOURCE_QUARANTINE')
                self.last_camera_audit=time.monotonic()
            require(not (root/'STOP_REQUEST.json').exists(),'SESSION_STOP_REQUESTED')
            require(not (root/'GPU_STOP_REQUEST.json').exists(),'GPU_SESSION_STOP_REQUESTED')
            if active[0]:require(not (active[0]/'STOP_REQUEST.json').exists(),'JOB_STOP_REQUESTED')
    lease=GUILimitedLease()
    def beat():
        while not end.is_set():
            write(root/'heartbeat.json',{'session_id':session['session_id'],'registry_sha256':reg_sha,'unix_time':time.time(),'utc':utc(),
                'state':'READY' if device[0] else 'PRELOADING','phase':phase[0],'startup':startup.snapshot(),
                'device':device[0],'pid':os.getpid(),'evidence_scope':session['evidence_scope']})
            # Scope is explicit so CPU protocol fixtures are never executable sessions.
            end.wait(1)
    thread=threading.Thread(target=beat,daemon=True);thread.start();handle=None;torch=None;worker_error=None;prepared_converter=None;graph_cache=None
    try:
        with startup.measure('shared_gpu_lease'):handle,queue_s=lease.acquire();lease.check('before_torch_import')
        from stream_transport import AuditMonitor
        monitor[0]=AuditMonitor(lease.audit)
        phase[0]='PRELOADING_ORIGINAL_MODEL';preload_start=time.monotonic()
        # Datamate HDF5 scratch must be on Linux, not the Windows source tree.
        scratch=Path('/tmp')/('flyvis-gui-'+session['session_id'])
        scratch.mkdir(parents=True,exist_ok=True)
        library_cache=Path('/tmp/flyvis-gui-library-cache')/canonical(dict(source=registry.data['model']['source_commit'],python=sys.version))[:16]
        library_cache.mkdir(parents=True,exist_ok=True)
        os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',CUDA_VISIBLE_DEVICES='0',
            FLYVIS_ROOT_DIR=str(scratch/'flyvis'),MPLBACKEND='Agg',MPLCONFIGDIR=str(library_cache/'matplotlib'),
            NUMBA_CACHE_DIR=str(library_cache/'numba'))
        if session.get('stream_enabled'):
            from input_preparation import PreparedConverter
            with startup.measure('parallel_input_preparation_launch'):
                prepared_converter=PreparedConverter(root,session).start()
        with startup.measure('torch_import'):import torch as torch_module
        torch=torch_module;torch.set_num_threads(1)
        require(torch.cuda.is_available(),'CUDA_REQUIRED_NO_CPU_FALLBACK')
        torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        from static_connectome import prepare_static_connectome,confirm_static_connectome
        with startup.measure('verified_static_connectome_copy'):
            graph_cache=prepare_static_connectome(registry,scratch/'flyvis/connectome',session['session_id'])
            write(root/'static_connectome_cache.json',graph_cache)
        with startup.measure('original_full_model_load'):
            with startup.measure('original_full_module_import'):
                Full=import_file('gui_original_full',registry.path_for('full')).FullNetworkOracle
            # Full.init__ imports this same original package before building the
            # network. Separating that import exposes eager analysis/viz loading;
            # no official module is replaced, skipped, or monkey-patched.
            with startup.measure('official_flyvis_import'):
                importlib.import_module('flyvis')
            with startup.measure('original_full_model_construct'):
                oracle=Full(registry.path_for('identity'),model_path=registry.data['runtime']['model_path'],device='cuda')
        confirm_static_connectome(oracle,graph_cache)
        write(root/'static_connectome_cache.json',graph_cache)
        if prepared_converter:prepared_converter.check()
        try:
            with startup.measure('official_decoder_load'):
                Decode=import_file('gui_original_decoder',registry.path_for('decoder')).OfficialDecoderService
                decoder=Decode(registry.data['runtime']['model_path'],registry.path_for('decoder_contract'),device='cuda',check_scope=lease.check)
        except Exception as exc:
            if not session.get('camera_enabled'):raise
            decoder=None;write(root/'camera_decoder_error.json',{'status':'NOT_CONNECTED','error':str(exc),'utc':utc()})
        initial=np.load(registry.path_for('initial'),allow_pickle=False)
        if session.get('stream_enabled'):
            # Warm kernels/decoder with an explicitly recorded frozen input, before
            # publishing READY. This scratch state never becomes the live old state.
            phase[0]='WARMING_ORIGINAL_CUDA';warm=time.monotonic()
            warm_frames=torch.as_tensor(np.array(registry.input('ON60')[0,:32,0],copy=True),device='cuda')
            warm_state=torch.as_tensor(initial.copy(),device='cuda')
            for k in range(32):lease.check('warmup');warm_state=oracle.step(warm_state,warm_frames[k])
            require(decoder is not None,'OFFICIAL_DECODER_REQUIRED')
            decoder.decode(warm_state.detach().cpu().numpy()[None,None],chunk_frames=1);torch.cuda.synchronize()
            write(root/'warmup.json',{'steps':32,'elapsed_s':time.monotonic()-warm,'source':'frozen_ON60_first32',
                'input_sha256':registry.pins['stimulus_ON60']['sha256'],'not_published_as_live':True,'live_initial_state':'original_frozen_a0'})
            del warm_state,warm_frames
        if not session.get('stream_enabled'):
            # Continuous Full streaming does not use fixed-job interventions/R data.
            with startup.measure('fixed_job_support'):
                intervention=import_file('gui_original_intervention',registry.path_for('intervention')).InterventionAdapter
                readout=import_file('gui_original_readout',registry.path_for('readout'))
                graph={key:value.copy() for key,value in np.load(registry.path_for('graph'),allow_pickle=False).items()}
                from spatial_state import SpatialRegistry
                spatial=SpatialRegistry()
                H=torch.as_tensor(graph['H_global_ids'],device='cuda',dtype=torch.int64)
        device[0]={'type':'cuda','index':torch.cuda.current_device(),'name':torch.cuda.get_device_name(),'torch_version':torch.__version__}
        preload_s=time.monotonic()-preload_start
        if prepared_converter:prepared_converter.check()
        startup.save('READY',preload_s=preload_s,queue_s=queue_s,
            library_cache=str(library_cache),cache_scope='verified static connectome copy plus font/library cache only; model/checkpoint/a0 and CUDA state loaded fresh',
            static_connectome=graph_cache,input_preparation_parallel=prepared_converter is not None,
            warmup=load(root/'warmup.json') if (root/'warmup.json').exists() else None)
        phase[0]='IDLE';idle_since=time.monotonic();attempted=set()
        while True:
            lease.check('idle')
            if session.get('stream_enabled'):
                from stream_runtime import run_stream
                phase[0]='CONTINUOUS_INPUT_GPU'
                run_stream(root,session,registry,oracle,decoder,torch,device[0],lease.check,prepared_converter)
                break
            if session.get('camera_enabled') and (root/'camera/control.json').exists():
                from camera_stream_compute import run_camera
                active[0]=root/'camera';phase[0]='LIVE_CAMERA_GPU'
                run_camera(root/'camera',session,registry,oracle,decoder,torch,device[0],lease.check)
                break
            ledger=load(root/'submitted.json') if (root/'submitted.json').exists() else {'jobs':[],'steps':0}
            require(len(ledger['jobs'])<=2 and ledger['steps']<=2910,'SESSION_BUDGET_EXCEEDED')
            require(len(set(ledger['jobs']))==len(ledger['jobs']) and all(re.fullmatch(r'[a-f0-9]{32}',j) for j in ledger['jobs']),'QUEUE_JOB_IDENTITY')
            pending=[j for j in ledger['jobs'] if j not in attempted]
            if not pending:
                if time.monotonic()-idle_since>180:break
                end.wait(.2);continue
            job_id=pending[0];folder=root/'jobs'/job_id
            # Budget reservation precedes atomic request publication.
            if not (folder/'request.json').exists() or not (folder/'status.json').exists():end.wait(.05);continue
            attempted.add(job_id);active[0]=folder;phase[0]='RUNNING';request=load(folder/'request.json')
            start=time.monotonic();completed=0;events=[];counts={};flows={};reference=None;checks={};all_pins={}
            from datetime import datetime,timezone
            job_queue_s=max(0.,(datetime.now(timezone.utc)-datetime.fromisoformat(request['created_utc'])).total_seconds())
            def status(state,**extra):
                write(folder/'status.json',{'job_id':job_id,'request_sha256':canonical(request),'status':state,'step':completed,
                'total_steps':485*len(request['modes']),'updated_utc':utc(),'device':device[0],'wall_time_s':time.monotonic()-start,
                    'backend':'R_only_CUDA_plus_H67_NumPy_SOURCE_RAW' if extra.get('mode')=='Python_Replacement' else 'original_FlyVis_CUDA',
                    'job_queue_s':job_queue_s,'elapsed_since_accept_s':job_queue_s+time.monotonic()-start,
                    'actual_new_computation':True,'result':None,'PL_execution':False,**extra})
            try:
                require(request['schema']=='flyvis-live-job/v1' and request['job_id']==job_id and request['session_id']==session['session_id']
                    and request['registry_sha256']==reg_sha and request['binding']==registry.binding(request['condition_id']),'REQUEST_IDENTITY')
                require(load(folder/'status.json')['request_sha256']==canonical(request),'REQUEST_CHANGED_BEFORE_EXECUTION')
                selected=request['selected_mode'];expected_modes=['Full','Sham']+([] if selected in ('Full','Sham') else [selected])
                require(selected in registry.data['modes'] and request['modes']==expected_modes and request['central_global_ids']==registry.data['central_global_ids'],'REQUEST_MODES')
                require(set(request['run_ids'])==set(expected_modes) and len(set(request['run_ids'].values()))==len(expected_modes)
                    and all(re.fullmatch(r'[a-f0-9]{32}',v) for v in request['run_ids'].values()),'RUN_ID_COLLISION')
                stimulus=np.array(registry.input(request['condition_id'])[0,:,0],copy=True)
                frames=torch.as_tensor(stimulus,device='cuda',dtype=torch.float32)
                replacement=None;r_digest=None
                if selected=='Python_Replacement':
                    R=import_file('gui_original_r',registry.path_for('r_only')).RStepService
                    r=R(registry.path_for('parameters'),registry.path_for('identity'),registry.path_for('candidate'),device='cuda')
                    def digest_r():
                        digest=hashlib.sha256()
                        for key,value in sorted(vars(r).items()):
                            if isinstance(value,torch.Tensor):digest.update(key.encode()+str(value.dtype).encode()+value.detach().cpu().contiguous().numpy().tobytes())
                        return digest.hexdigest()
                    r_digest=digest_r()
                    h_module=import_file('h_step',registry.path_for('h_step'))
                    c_module=import_file('coordinator',registry.path_for('coordinator'))
                    g_module=import_file('gpu_adapter',registry.path_for('gpu_adapter'))
                    closed=import_file('gui_original_closed_loop',registry.path_for('closed_loop'))
                    h=h_module.HUpdater(registry.path_for('h_static'))
                    input_map=closed.validate_parameters(h,registry.path_for('parameters'))
                    g=g_module.GPUAdapter(r,input_map)
                    replacement=(c_module.Coordinator(h,g,initial,request['run_ids'][selected],request['comparison_id'],request['condition_id']),closed,input_map)
                for mode in request['modes']:
                    lease.check('mode_start');status('RUNNING',mode=mode,run_id=request['run_ids'][mode]);run_dir=folder/'runs'/request['run_ids'][mode];run_dir.mkdir(parents=True)
                    states=np.lib.format.open_memmap(run_dir/'activities_full.npy',mode='w+',dtype=np.float32,shape=(1,485,45669))
                    flow=np.lib.format.open_memmap(run_dir/'flow.npy',mode='w+',dtype=np.float32,shape=(1,485,2,721))
                    state=torch.as_tensor(initial.copy(),device='cuda',dtype=torch.float32);adapter=None
                    if mode not in ('Full','Python_Replacement'):
                        group={'BLOCK_T4_RELEASE':'T4','BLOCK_T5_RELEASE':'T5','BLOCK_T4T5_RELEASE':'T4T5'}.get(mode)
                        edges=np.array([],dtype=np.int64) if group is None else graph[group+'_outgoing_original_edge_ids']
                        adapter=intervention(oracle,mode,torch.as_tensor(edges,device='cuda',dtype=torch.int64),H,graph,lease.check)
                    neural_s=0.;decoder_s=0.;violations=0;flow_violations=0;maximum=0.;gate_calls=0;clamp_checks=0;native_calls=0
                    with (run_dir/'step_events.jsonl').open('x',encoding='utf-8') as log:
                        for a in range(0,485,32):
                            b=min(a+32,485);tick=time.monotonic();errors=[]
                            for k in range(a,b):
                                lease.check('before_step')
                                if mode=='Python_Replacement':
                                    coord,closed,input_map=replacement;x=np.zeros(45669,dtype=np.float32);x[input_map.reshape(-1)]=np.tile(stimulus[k],8)
                                    with closed.native_full_forbidden() as guard:
                                        candidate=coord.prepare(k,x,'SOURCE_RAW');row=checked_commit(candidate,lease.check,coord.commit)
                                    native_calls+=guard['forbidden_native_call_count'];require(native_calls==0,'NATIVE_H_EXECUTED')
                                    commit_record=coord.logs[-1]
                                else:
                                    original_sum=oracle.net.target_sum
                                    if mode.startswith('BLOCK_') and k>=200:
                                        def observed_sum(currents):
                                            nonlocal gate_calls
                                            require(not bool(torch.any(currents[...,adapter.edge_indices]!=0)),'BLOCK_CURRENT_NOT_ZERO')
                                            gate_calls+=1;return original_sum(currents)
                                        oracle.net.target_sum=observed_sum
                                    try:candidate=oracle.step(state,frames[k]) if adapter is None else adapter.step(state,frames[k],k)
                                    finally:oracle.net.target_sum=original_sum
                                    require(candidate.shape==(45669,) and bool(torch.isfinite(candidate).all()),'INVALID_CANDIDATE_NO_COMMIT')
                                    if mode=='CLAMP_T4T5' and k>=200:
                                        require(not bool(torch.any(candidate[H]!=0)),'CLAMP_CANDIDATE_NOT_ZERO');clamp_checks+=1
                                    state=checked_commit(candidate,lease.check,lambda value:value);row=state.detach().cpu().numpy()
                                    commit_record={'status':'COMMITTED','step_id':k,'state_token':k+1}
                                states[0,k]=row;completed+=1
                                if mode!='Full':
                                    delta=row.astype(np.float64)-reference[0,k];maximum=max(maximum,float(np.abs(delta).max()))
                                    bad=int(np.count_nonzero(np.abs(delta)>1e-5+1e-5*np.abs(reference[0,k])))
                                    if mode=='Sham' or (k<200 and mode!='Python_Replacement'):violations+=bad
                                    errors.append({'step':k,'RMSE':float(np.sqrt(np.mean(delta**2))),'max_abs':float(np.abs(delta).max())})
                                log.write(json.dumps({**commit_record,'job_id':job_id,'comparison_id':request['comparison_id'],'run_id':request['run_ids'][mode],
                                    'mode':mode,'old_state_source':'OWN_LIVE_COMMITTED_STATE','input_time_s':float(registry.time[k]),
                                    'activity_time_s':float(registry.time[k]+.005),'utc':utc(),'execution_monotonic':time.monotonic()})+'\n')
                            torch.cuda.synchronize();neural_elapsed=time.monotonic()-tick;neural_s+=neural_elapsed;states.flush();log.flush()
                            status('DECODING',mode=mode,run_id=request['run_ids'][mode]);tick=time.monotonic()
                            decoded=decoder.decode(np.array(states[:,a:b],copy=True),chunk_frames=32)
                            torch.cuda.synchronize();decode_elapsed=time.monotonic()-tick;decoder_s+=decode_elapsed
                            lease.check('before_chunk_publication');flow[:,a:b]=decoded;flow.flush()
                            if mode=='Sham' or (a<200 and mode not in ('Full','Python_Replacement')):
                                end_step=b if mode=='Sham' else min(b,200);base=flows['Full'][:,a:end_step];d=np.abs(decoded[:,:end_step-a]-base)
                                flow_violations+=int(np.count_nonzero(d>1e-5+1e-5*np.abs(base)))
                            index=len(events);chunk_dir=folder/'chunks';chunk_dir.mkdir(exist_ok=True);files={}
                            for name,array in (('activity',np.asarray(states[0,a:b][:,registry.data['central_global_ids']],dtype=np.float32)),('flow',decoded[0]),('spatial',spatial.extract(states[0,a:b]))):
                                path=chunk_dir/f'{index:06}_{name}.npy';np.save(path,array,allow_pickle=False)
                                files[name]={'path':str(path.relative_to(folder)),'sha256':sha(path)}
                            event={'schema':'flyvis-live-chunk/v1',**{key:request[key] for key in ('job_id','comparison_id','condition_id','binding')},
                                'event_index':index,'mode':mode,'run_id':request['run_ids'][mode],'start_step':a,'stop_step':b,'committed_stop_step':b,
                                'central_global_ids':registry.data['central_global_ids'],'input_sha256':request['binding']['input_sha256'],
                                'input_time_s':registry.time[a:b].tolist(),'activity_time_s':(registry.time[a:b]+.005).tolist(),'files':files,
                                'execution_kind':'new_inference','actual_new_computation':True,'evidence_level':'ACTUAL_ORIGINAL_GPU_CHUNK',
                                'display_kind':'LIVE_COMPUTE_CHUNK','PL_execution':False,'device':device[0],'execution_UTC':utc(),
                                'execution_monotonic':time.monotonic(),'neural_steps_in_chunk':b-a,'decoder_frames_in_chunk':b-a,
                                'neural_s':neural_elapsed,'decoder_s':decode_elapsed,'full_network_error':errors,'scientific_acceptance':'PENDING',
                                'spatial_map_sha256':spatial.digest}
                            write(chunk_dir/f'{index:06}.json',event);events.append(event);status('RUNNING',mode=mode,run_id=request['run_ids'][mode])
                    require(violations==0 and flow_violations==0,'FULL_SHAM_OR_PRE200_TOLERANCE_FAILED')
                    oracle.assert_weights_unchanged();decoder.assert_weights_unchanged();counts[mode]={'neural_steps':485,'decoder_frames':485,'neural_s':neural_s,'decoder_s':decoder_s}
                    checks[mode]={'all_node_max_abs_vs_fresh_Full':maximum,'required_tolerance_violations':violations,'flow_tolerance_violations':flow_violations,
                        'observed_zero_current_scatter_calls':gate_calls,'clamp_candidate_checks':clamp_checks,'forbidden_native_call_count':native_calls}
                    np.save(run_dir/'final_state_full.npy',np.asarray(states[0,-1]),allow_pickle=False)
                    np.save(run_dir/'time.npy',registry.time,allow_pickle=False);np.save(run_dir/'activity_time.npy',registry.time+.005,allow_pickle=False)
                    write(run_dir/'run_identity.json',{**request,'mode':mode,'run_id':request['run_ids'][mode],'device':device[0],'counts':counts[mode],'checks':checks[mode]})
                    all_pins[mode]={p.name:{'path':str(p.relative_to(folder)),'sha256':sha(p)} for p in run_dir.iterdir() if p.is_file()}
                    flows[mode]=flow
                    if mode=='Full':reference=states
                lease.check('before_final_seal');oracle.assert_weights_unchanged();decoder.assert_weights_unchanged()
                if r_digest is not None:require(digest_r()==r_digest,'R_ONLY_PARAMETERS_CHANGED')
                metrics=readout.frozen_B_metrics(flows['Sham'][0],flows[selected][0],angle_deg=registry.data['inputs'][request['condition_id']]['angle_deg'],contract_path=registry.path_for('readout_contract'))
                result={'schema':'flyvis-live-result/v1',**{key:request[key] for key in ('job_id','comparison_id','binding','run_ids','condition_id','selected_mode')},
                    'request_sha256':canonical(request),'event_chain_sha256':canonical(events),'files':all_pins,'counts':counts,'checks':checks,'metrics':metrics,
                    'backend_per_mode':{m:'R_only_CUDA_plus_H67_NumPy_SOURCE_RAW' if m=='Python_Replacement' else 'original_FlyVis_CUDA' for m in request['modes']},
                    'decoder_backend':'official_DecoderGAVP_CUDA_eval','R_parameters_unchanged':True if r_digest is not None else None,
                    'actual_new_computation':True,'execution_kind':'new_inference','evidence_level':'ACTUAL_ORIGINAL_GPU_EXECUTION','PL_execution':False,
                    'FPGA_status':'NOT_CONNECTED','device':device[0],'wall_time_s':time.monotonic()-start,'job_queue_s':job_queue_s,
                    'elapsed_since_accept_s':job_queue_s+time.monotonic()-start,'resource_lease_queue_s':queue_s,'model_preload_s':preload_s,
                    'integrity_checks':{'original_weights_unchanged':True,'decoder_state_unchanged':True,'all_commits_verified':True},
                    'scientific_acceptance':'PENDING_IV_REVIEW','LIVE_INTERACTIVE_GUI_PASS':'NOT_RUN','REALTIME_STREAM_PASS':'NOT_RUN',
                    'realtime_measurements':{'p50_ms':None,'p95_ms':None,'p99_ms':None,'display_FPS':None,'dropped_frames':None,'queue_length':None},'completed_utc':utc()}
                write(folder/'result.json',result);lease.check('before_complete');status('COMPLETED',mode=selected,run_id=request['run_ids'][selected]);idle_since=time.monotonic()
            except BaseException as exc:
                status('CANCELLED' if (folder/'STOP_REQUEST.json').exists() else 'FAILED',error=str(exc));raise
            finally:active[0]=None
    except BaseException as exc:
        worker_error={'code':getattr(exc,'code',type(exc).__name__),'message':str(exc),'phase':phase[0],'utc':utc()}
        write(root/'worker_error.json',dict(worker_error,session_id=session['session_id'],registry_sha256=reg_sha))
        raise
    finally:
        phase[0]='STOPPING'
        cuda_synchronized=False
        try:
            if torch is not None:torch.cuda.synchronize();cuda_synchronized=True
        except BaseException as exc:
            worker_error={'code':'GUI_CUDA_COMPLETION_UNKNOWN','message':str(exc),'phase':'STOPPING','utc':utc()}
            write(root/'worker_error.json',dict(worker_error,session_id=session['session_id'],registry_sha256=reg_sha))
            write(runner.own_path('runtime','RESOURCE_QUARANTINE.json'),{'reason':'GUI_CUDA_COMPLETION_UNKNOWN','session_id':session['session_id'],'error':str(exc),'utc':utc()})
            raise
        finally:
            device[0]=None;end.set();thread.join(timeout=2)
            if prepared_converter:
                try:prepared_converter.close()
                except BaseException as exc:
                    worker_error={'code':'INPUT_PREPARATION_STOP_FAILED','message':str(exc),'phase':'STOPPING','utc':utc()}
                    write(root/'worker_error.json',dict(worker_error,session_id=session['session_id'],registry_sha256=reg_sha))
            write(root/'heartbeat.json',{'state':'FAILED' if worker_error else 'STOPPED','session_id':session['session_id'],
                'registry_sha256':reg_sha,'unix_time':time.time(),'device':None,'phase':'STOPPED',
                'evidence_scope':session['evidence_scope'],'error':worker_error})
            if handle:handle.close()
            if monitor[0]:monitor[0].close()
            write(root/'worker_shutdown.json',{'CUDA_synchronized':cuda_synchronized,'shared_lock_closed':handle is not None,'utc':utc()})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--session',required=True);args=parser.parse_args()
    run(args.session)
