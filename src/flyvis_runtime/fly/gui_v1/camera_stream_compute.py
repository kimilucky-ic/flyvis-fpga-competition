"""Thin camera orchestration around existing Full.step and official decoder, under one lease."""
import hashlib
import io
import json
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from live_protocol import HERE,checked_commit,load,require,sha,utc,write
from camera_stream_protocol import DISPLAY_CAPACITY,DT,MAX_LAG_S,CausalSelector,check_control,dependencies
from spatial_state import SpatialRegistry
from realtime_timing import Timings,CudaProbes


def run_camera(root,session,registry,oracle,decoder,torch,device,check_scope):
    control=load(root/'control.json');check_control(control,session);dependencies()
    spatial=SpatialRegistry();timings=Timings();probes=CudaProbes(torch,timings)
    require(control['spatial_map_sha256']==spatial.digest,'CAMERA_SPATIAL_BINDING')
    probes.wrap(oracle.net,'_next_state','neural_update_cuda_stream')
    if decoder:probes.wrap(decoder.decoder,'forward','decoder_forward_cuda_stream')
    renderer_log=(root/'renderer.log').open('ab')
    process=subprocess.Popen([sys.executable,'-B',str(HERE/'camera_stream_renderer.py'),'--root',str(root)],stdout=renderer_log,stderr=subprocess.STDOUT)
    selector=CausalSelector();state=torch.as_tensor(np.load(registry.path_for('initial'),allow_pickle=False),device='cuda',dtype=torch.float32).clone()
    cache={};recent=[];serial=0;last_display=0.;start=time.monotonic();wall_epoch=None;steps=0;selected_saved=set();evidence_bytes=0
    last_ring_read=0.;last_status=0.;mapped=None;source=None
    (root/'display').mkdir();(root/'selected_frames').mkdir()
    def status(value,**extra):write(root/'compute_status.json',{'state':value,'run_id':control['run_id'],'committed_steps':steps,
        'simulation_time_s':steps*DT,'inference_steps_per_s':steps/(time.monotonic()-start) if steps else None,'updated_unix_s':time.time(),
        'device':device,'decoder_status':'CONNECTED' if decoder else 'NOT_CONNECTED','error':None,**extra})
    status('WAITING_INPUT')
    try:
        with (root/'step_commits.jsonl').open('x',encoding='utf-8') as log:
            while True:
                check_scope('camera_before_read');require(not (root/'STOP_REQUEST.json').exists(),'CAMERA_STOP_REQUESTED')
                require(steps<60000,'CAMERA_STEP_LIMIT');require(time.monotonic()-start<345,'CAMERA_WINDOW_LIMIT')
                if process.poll() is not None:raise ValueError('OFFICIAL_CPU_RENDERER_EXITED '+str(process.returncode))
                if not (root/'hex_ring.json').exists():time.sleep(.003);continue
                if time.monotonic()-last_ring_read>=.01 or mapped is None:
                    with timings.measure('WSL_file_bridge_read'):
                        mapped=load(root/'hex_ring.json');source=load(root/'source_ring.json')
                    last_ring_read=time.monotonic()
                capture=source['status']
                require(mapped['run_id']==control['run_id'] and capture['source_frames_dropped_before_render']==0,'CAMERA_SOURCE_IDENTITY_OR_LOSS')
                if wall_epoch is None:wall_epoch=time.monotonic()-max(0.,time.time()-capture['origin_unix_s']);start=wall_epoch
                elapsed=time.monotonic()-wall_epoch;lag=max(0.,elapsed-steps*DT)
                if time.monotonic()-last_status>=.05:
                    status('RUNNING',model_lag_s=lag,input_queue_length=len(mapped['frames']),source_queue_length=len(source['frames']));last_status=time.monotonic()
                require(lag<=MAX_LAG_S,'MODEL_LAG_LIMIT_NO_STEP_SKIP')
                if steps*DT>elapsed:time.sleep(min(.002,steps*DT-elapsed));continue
                chosen=selector.choose(mapped['frames'],steps);seq=chosen['sequence']
                if seq not in cache:
                    with timings.measure('new_source_read_hash'):
                        path=root/chosen['hex_path'];blob=path.read_bytes()
                        require(hashlib.sha256(blob).hexdigest()==chosen['hex_sha256'],'HEX_QUEUE_OVERWRITE_MODEL_TOO_LATE')
                        values=np.load(io.BytesIO(blob),allow_pickle=False);require(values.shape==(721,) and values.dtype==np.float32 and np.isfinite(values).all(),'CAMERA_HEX_VALUES')
                    with timings.measure('input_host_to_GPU'):
                        cache={seq:(values,torch.as_tensor(values,device='cuda',dtype=torch.float32))}
                values,tensor=cache[seq]
                if seq not in selected_saved:
                    png=root/chosen['png_path'];require(sha(png)==chosen['png_sha256'],'SOURCE_IMAGE_QUEUE_OVERWRITE')
                    dest=root/'selected_frames'/f'{seq:08}.png';blob=png.read_bytes();dest.write_bytes(blob);evidence_bytes+=len(blob)
                    # Actual selected receptor values retained once per source frame.
                    retained_hex=root/'selected_frames'/f'{seq:08}_hex.npy';np.save(retained_hex,values,allow_pickle=False)
                    pin={**chosen,'png_path':str(dest.relative_to(root)),'hex_path':str(retained_hex.relative_to(root)),
                        'hex_sha256':sha(retained_hex),'raw_ring_path_ephemeral':True};write(root/'selected_frames'/f'{seq:08}.json',pin)
                    selected_saved.add(seq);require(evidence_bytes<256*1024*1024,'CAMERA_EVIDENCE_STORAGE_LIMIT')
                with timings.measure('Full_step_host_including_original_checks'):
                    candidate=oracle.step(state,tensor)
                with timings.measure('candidate_finite_and_commit_gate'):
                    require(bool(torch.isfinite(candidate).all()),'NONFINITE_CAMERA_CANDIDATE_NO_COMMIT')
                    state=checked_commit(candidate,check_scope,lambda x:x);k=steps;selector.commit(chosen,k);steps+=1
                row={'step_id':k,'state_token':steps,'input_time_s':k*DT,'activity_time_s':k*DT+DT,'source_sequence':seq,
                    'source_received_monotonic_ns':chosen['received_monotonic_ns'],'source_relative_s':chosen['relative_s'],
                    'input_hex_values_sha256':chosen['hex_values_sha256'],'status':'COMMITTED','run_id':control['run_id'],
                    'old_state_source':'OWN_LIVE_COMMITTED_STATE','utc':utc()}
                with timings.measure('commit_log_buffered_write'):log.write(json.dumps(row)+'\n')
                if time.monotonic()-last_display>=.05:
                    # One full-state D2H at display cadence: original decoder needs
                    # all 34 spatial layers. No central-node D2H on every model step.
                    with timings.measure('display_full_state_D2H_sync'):full=state.detach().cpu().numpy().copy()
                    activity=full[control['central_global_ids']].tolist();flow=None
                    if decoder is not None:
                        with timings.measure('official_decoder_host'):flow=decoder.decode(full[None,None],chunk_frames=1)[0,0].tolist()
                    check_scope('camera_before_display_publish');probes.collect()
                    recent.append({**row,'activity':activity});recent=recent[-200:]
                    with timings.measure('spatial_5768_extract'):spatial_packet=spatial.packet(full,control['run_id'],k,k*DT+DT)
                    retained_source=load(root/'selected_frames'/f'{seq:08}.json')
                    serial+=1;packet={'schema':'flyvis-live-camera-output/v1','session_id':session['session_id'],'run_id':control['run_id'],
                        'serial':serial,'step_id':k,'state_token':steps,'input_time_s':k*DT,'activity_time_s':k*DT+DT,'source':retained_source,
                        'activity':activity,'input_hex':values.tolist(),'flow':flow,'decoder_status':'CONNECTED' if decoder else 'NOT_CONNECTED',
                        'spatial':spatial_packet,'timing':timings.summary(),'curve_sampling':'display_samples_not_all_model_steps',
                        'central_global_ids':control['central_global_ids'],'binding':control['binding'],'device':device,
                        'backend':'original_FlyVis_CUDA','mode':'Full','spatial_transform':load(root/'spatial_identity.json')['transform'],
                        'execution_kind':'LIVE_CAMERA_GPU','actual_new_computation':True,'evidence_level':'ACTUAL_FULL_GPU_CAMERA_STATE','PL_execution':False,
                        'recent_activity':recent,'model_lag_s':max(0.,time.monotonic()-wall_epoch-steps*DT),'published_unix_s':time.time(),
                        'display_queue_overwrites':max(0,serial-DISPLAY_CAPACITY),'REALTIME_STREAM_PASS':'NOT_RUN','p50_ms':None,'p95_ms':None,'p99_ms':None}
                    with timings.measure('display_packet_and_state_write'):
                        write(root/'display'/f'{serial%DISPLAY_CAPACITY:02}.json',packet);write(root/'display_latest.json',{'serial':serial})
                        np.save(root/'latest_full_state.npy',full,allow_pickle=False);log.flush()
                    last_display=time.monotonic()
    except BaseException as exc:
        requested=(root/'STOP_REQUEST.json').exists() or (root.parent/'GPU_STOP_REQUEST.json').exists() or (root.parent/'STOP_REQUEST.json').exists()
        status('STOPPED' if requested else 'FAILED',error=str(exc));write(root/'STOP_REQUEST.json',{'reason':'CAMERA_COMPUTE_END','error':str(exc),'utc':utc()})
        raise
    finally:
        probes.close();write(root/'timing_summary.json',{'stages':timings.summary(),'pending_cuda_events':len(probes.pending),
            'exclusive_totals':False,'kernel_event_note':'CUDA stream intervals; not profiler kernel-only sum',
            'per_step_full_D2H':False,'display_target_Hz':20,'REALTIME_STREAM_PASS':'NOT_RUN'})
        write(root/'STOP_REQUEST.json',{'reason':'CAMERA_WORKER_STOP','utc':utc()})
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5) # Only CPU renderer child; never the GPU worker.
        renderer_log.close();oracle.assert_weights_unchanged()
        if decoder:decoder.assert_weights_unchanged()
