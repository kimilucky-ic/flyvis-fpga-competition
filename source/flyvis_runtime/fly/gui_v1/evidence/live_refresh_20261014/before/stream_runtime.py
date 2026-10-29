"""Unified digital/camera stream: original Full GPU and decoder, bounded memory IPC."""
import base64
from collections import deque
import hashlib
import io
import json
import queue
import subprocess
import sys
import threading
import time
import numpy as np
from live_protocol import HERE,canonical,checked_commit,load,require,sha,utc,write
from camera_stream_protocol import CausalSelector,DT,MAX_LAG_S,dependencies
from spatial_state import SpatialRegistry
from realtime_timing import Timings,CudaProbes,SummaryCache,host_scheduling
from stream_transport import LocalRPC
from checked_full import CombinedCheckedFull
from decoder_audit import PackedDecoderAudit


class EvidenceWriter:
    def init__(self,root):
        self.root=root;self.queue=queue.Queue(128);self.error=None;self.bytes=0;self.peak=0
        self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def put(self,kind,value):
        require(self.error is None,'EVIDENCE_WRITE_FAILED '+str(self.error))
        try:self.queue.put_nowait((kind,value));self.peak=max(self.peak,self.queue.qsize())
        except queue.Full:raise ValueError('EVIDENCE_QUEUE_FULL_NO_SILENT_LOSS')
    def loop(self):
        try:
            with (self.root/'step_commits.jsonl').open('x',encoding='utf-8') as steps:
                while True:
                    item=self.queue.get()
                    if item is None:return
                    kind,value=item
                    if kind=='step':steps.write(json.dumps(value)+'\n')
                    elif kind=='source':
                        p=self.root/'sources';p.mkdir(exist_ok=True);seq=value['source']['sequence']
                        png=base64.b64decode(value['png']);(p/f'{seq:06}.png').write_bytes(png)
                        np.save(p/f'{seq:06}_hex.npy',np.asarray(value['values'],dtype=np.float32),allow_pickle=False)
                        write(p/f'{seq:06}.json',value['source']);self.bytes+=len(png)+2884
                    elif kind=='snapshot':
                        packet,full=value;p=self.root/'snapshots';p.mkdir(exist_ok=True)
                        np.savez(p/f"{packet['serial']:06}.npz",full=full,flow=np.asarray(packet['flow'],dtype=np.float32),
                            input=np.asarray(packet['input_hex'],dtype=np.float32),step_id=packet['step_id'])
                        # Numeric truth is lossless in the NPZ; avoid serializing the
                        # same 5,768 values/flow/history again in the CUDA host process.
                        metadata={k:v for k,v in packet.items() if k not in ('preview_png','input_hex','flow','recent_activity','spatial')}
                        metadata['spatial']={k:v for k,v in packet['spatial'].items() if k!='values'}
                        metadata['arrays_file']=f"{packet['serial']:06}.npz"
                        write(p/f"{packet['serial']:06}.json",metadata)
                        self.bytes+=full.nbytes+200000
                    require(self.bytes<512*1048576,'STREAM_EVIDENCE_STORAGE_LIMIT')
        except BaseException as e:self.error=repr(e)
    def close(self):
        if self.thread.is_alive():self.queue.put(None,timeout=5);self.thread.join(10)
        require(not self.thread.is_alive() and self.error is None,'EVIDENCE_CLOSE_FAILED '+str(self.error))


class StreamHub:
    def init__(self,session_id):
        self.session_id=session_id;self.control=None;self.raw=deque();self.converted=deque(maxlen=96);self.lock=threading.RLock()
        self.packet=None;self.error=None;self.stopping=False;self.stopped=False;self.renderer_ready=False
        self.bridge_at=0.;self.renderer_at=0.;self.last_source=-1;self.last_render=-1;self.raw_peak=0;self.hex_peak=0
        self.state='WAITING_INPUT_SELECTION';self.steps=0;self.started=None;self.serial=0;self.writer=None
    def check(self):
        require(not self.stopping,'STREAM_STOP_REQUESTED');require(self.error is None,'STREAM_FAILED '+str(self.error))
        if self.control:
            require(time.monotonic()-self.bridge_at<3,'STREAM_BRIDGE_DISCONNECTED')
            if self.renderer_ready:require(time.monotonic()-self.renderer_at<3,'STREAM_RENDERER_DISCONNECTED')
    def revoke(self,error):
        with self.lock:self.error=str(error);self.packet=None;self.state='FAILED';self.stopping=True
    def dispatch(self,role,op,body):
        with self.lock:
            if role=='bridge':self.bridge_at=time.monotonic()
            else:self.renderer_at=time.monotonic()
            if op=='status':return self.status()
            if op=='stop':
                require(role=='bridge','STREAM_ROLE')
                if body and body.get('error'):self.error=str(body['error'])
                self.stopping=True;self.packet=None;self.state='STOPPING';return self.status()
            if op=='start':
                require(role=='bridge' and self.control is None,'STREAM_ALREADY_STARTED')
                require(body['session_id']==self.session_id and body['source_kind'] in ('digital_direct','real_windows_camera') and body['mode']=='Full','STREAM_CONTROL')
                require(len(body['run_id'])==32 and body['PL_execution'] is False,'STREAM_RUN');self.control=body;self.state='WAITING_CONVERTER';return self.status()
            self.check()
            if op=='ready':
                require(role=='renderer','STREAM_ROLE');self.renderer_ready=True;self.state='WAITING_SOURCE';return True
            if op=='input':
                require(role=='bridge' and self.control is not None and self.renderer_ready,'STREAM_INPUT_BEFORE_READY')
                f=body['source'];require(f['run_id']==self.control['run_id'] and f['source_kind']==self.control['source_kind'],'STREAM_INPUT_RUN')
                require(f['sequence']==self.last_source+1 and len(self.raw)<32,'SOURCE_SEQUENCE_OR_QUEUE_OVERRUN')
                require(np.isfinite(f['relative_s']) and f['relative_s']>=0,'SOURCE_TIME')
                if self.last_source>=0:require(f['relative_s']>self.last_time,'SOURCE_TIME_ORDER')
                require(len(body['png'])<2500000 and hashlib.sha256(base64.b64decode(body['png'],validate=True)).hexdigest()==f['png_sha256'],'SOURCE_PNG_IDENTITY')
                self.raw.append(body);self.last_source=f['sequence'];self.last_time=f['relative_s'];self.raw_peak=max(self.raw_peak,len(self.raw));return {'accepted_sequence':f['sequence']}
            if op=='raw':
                require(role=='renderer','STREAM_ROLE');return self.raw.popleft() if self.raw else None
            if op=='converted':
                require(role=='renderer','STREAM_ROLE');f=body['source'];values=np.asarray(body['values'],dtype=np.float32)
                require(f['sequence']==self.last_render+1 and f['run_id']==self.control['run_id'],'RENDER_SEQUENCE_OR_RUN')
                require(values.shape==(721,) and np.isfinite(values).all() and np.all((values>=0)&(values<=1)),'OFFICIAL_HEX_SCHEMA')
                require(hashlib.sha256(values.tobytes()).hexdigest()==f['hex_values_sha256'],'OFFICIAL_HEX_HASH')
                self.converted.append(body);self.last_render=f['sequence'];self.hex_peak=max(self.hex_peak,len(self.converted))
                if self.writer:self.writer.put('source',body)
                return True
            if op=='latest':
                p=self.packet
                if p and body and body.get('after_serial')==p['serial']:p=None
                if p:
                    # Lossless FP32 wire encoding reduces Python JSON/GIL overhead.
                    p={**p,'spatial':{k:v for k,v in p['spatial'].items() if k!='values'},
                        'spatial_values_f32_le_b64':base64.b64encode(np.asarray(p['spatial']['values'],dtype='<f4').tobytes()).decode()}
                return dict(status=self.status(),packet=p)
            raise ValueError('UNKNOWN_STREAM_OPERATION')
    def status(self):
        elapsed=time.monotonic()-self.started if self.started else None
        return dict(status=self.state,run_id=self.control['run_id'] if self.control else None,session_id=self.session_id,
            source_kind=self.control['source_kind'] if self.control else None,result_valid=not(self.stopping or self.error or self.stopped),
            renderer_ready=self.renderer_ready,committed_steps=self.steps,simulation_time_s=self.steps*DT,
            inference_steps_per_s=self.steps/elapsed if elapsed else None,elapsed_s=elapsed,error=self.error,
            source_queue_length=len(self.raw),input_queue_length=len(self.converted),raw_queue_peak=self.raw_peak,hex_queue_peak=self.hex_peak,
            input_frames=self.last_source+1,converted_frames=self.last_render+1,source_frames_dropped_before_render=0,
            stop_acknowledged=self.stopped,FPGA_status='NOT_CONNECTED',PL_execution=False,REALTIME_STREAM_PASS='NOT_RUN')


def run_stream(root,session,registry,oracle,decoder,torch,device,scope_check):
    with host_scheduling(.001):
        return _run_stream(root,session,registry,oracle,decoder,torch,device,scope_check)


def _run_stream(root,session,registry,oracle,decoder,torch,device,scope_check):
    dependencies();require(decoder is not None,'OFFICIAL_DECODER_REQUIRED');spatial=SpatialRegistry()
    hub=StreamHub(session['session_id']);rpc=LocalRPC(session['session_id'],hub.dispatch)
    write(root/'stream_endpoint.json',rpc.endpoint)
    folder=root/'stream';folder.mkdir();writer=EvidenceWriter(folder);hub.writer=writer
    timing=Timings();summary_cache=SummaryCache();probes=CudaProbes(torch,timing);process=None;log=None;success=False;reason=None;rows=[]
    compute=None;decoder_audit=None
    probes.wrap(oracle.net,'_next_state','neural_update_cuda_stream');probes.wrap(decoder.decoder,'forward','decoder_forward_cuda_stream')
    def gate(operation='check'):scope_check(operation);hub.check();require(writer.error is None,'EVIDENCE_FAILED '+str(writer.error))
    try:
        compute=CombinedCheckedFull(oracle,torch,timing,cache_validated_tensors=True)
        # Stream interval of the reduction itself; the host gate also waits for
        # earlier queued CUDA work. No extra synchronize or skipped validation.
        probes.wrap(compute,'validate_candidate','candidate_finite_cuda_stream')
        decoder_audit=PackedDecoderAudit(decoder,timing).install()
        wait=time.monotonic()
        while hub.control is None:scope_check('wait_stream_start');require(time.monotonic()-wait<180,'STREAM_INPUT_START_TIMEOUT');time.sleep(.02)
        control=hub.control;require(control['binding']['model']==registry.data['model'] and control['spatial_map_sha256']==spatial.digest,'STREAM_BINDING')
        write(folder/'control.json',control)
        log=(folder/'renderer.log').open('ab')
        process=subprocess.Popen([sys.executable,'-B',str(HERE/'stream_renderer.py'),'--root',str(root)],stdout=log,stderr=subprocess.STDOUT)
        state=torch.as_tensor(np.load(registry.path_for('initial'),allow_pickle=False),device='cuda',dtype=torch.float32).clone()
        selector=CausalSelector();cached=-1;last_display=-1.;epoch=None;serial=0
        while True:
            gate();require(hub.steps<60000,'STREAM_STEP_LIMIT')
            require(process.poll() is None,'OFFICIAL_RENDERER_EXITED')
            with timing.measure('input_history_snapshot'),hub.lock:frames=list(hub.converted)
            if not frames:require(time.monotonic()-wait<60,'STREAM_FIRST_INPUT_TIMEOUT');time.sleep(.002);continue
            if epoch is None:epoch=time.monotonic();hub.started=epoch
            elapsed=time.monotonic()-epoch;lag=max(0,elapsed-hub.steps*DT)
            require(elapsed<300,'STREAM_DURATION_LIMIT');require(lag<=MAX_LAG_S,'MODEL_LAG_LIMIT_NO_STEP_SKIP')
            if hub.steps*DT>elapsed:time.sleep(min(.001,hub.steps*DT-elapsed));continue
            with timing.measure('causal_input_selection'):
                chosen=selector.choose([f['source'] for f in frames],hub.steps)
                item=next(f for f in frames if f['source']['sequence']==chosen['sequence'])
            if cached!=chosen['sequence']:
                with timing.measure('input_H2D'):values=np.asarray(item['values'],dtype=np.float32);tensor=torch.as_tensor(values,device='cuda')
                cached=chosen['sequence']
            host_cpu=time.thread_time()
            with timing.measure('Full_host_including_original_checks'):candidate=compute.step(state,tensor)
            timing.add('Full_host_thread_CPU',time.thread_time()-host_cpu)
            with timing.measure('candidate_finite_CUDA_wait'):compute.validate_candidate(candidate)
            with timing.measure('memory_commit_gate'),hub.lock:
                state=checked_commit(candidate,gate,compute.commit)
                k=hub.steps;selector.commit(chosen,k);hub.steps+=1;hub.state='RUNNING'
            row=dict(run_id=control['run_id'],step_id=k,state_token=k+1,status='COMMITTED',source_sequence=cached,
                input_time_s=k*DT,activity_time_s=k*DT+DT,input_hex_values_sha256=chosen['hex_values_sha256'],old_state_source='OWN_CONTINUOUS_CUDA_STATE')
            writer.put('step',row)
            if time.monotonic()-last_display>=.05:
                with timing.measure('display_full_D2H'):full=state.detach().cpu().numpy().copy()
                with timing.measure('official_decoder_host'):flow=decoder.decode(full[None,None],chunk_frames=1)[0,0]
                gate('publish');serial+=1;activity=full[registry.data['central_global_ids']].tolist()
                rows.append({**row,'activity':activity});rows=rows[-200:]
                with timing.measure('timing_summary_refresh'):summary,summary_age=summary_cache.get(timing)
                packet_started=time.perf_counter()
                packet=dict(schema='flyvis-continuous-output/v1',**row,serial=serial,session_id=session['session_id'],
                    source=chosen,source_kind=control['source_kind'],preview_png=item['png'],activity=activity,input_hex=values.tolist(),flow=flow.tolist(),
                    spatial=spatial.packet(full,control['run_id'],k,k*DT+DT),recent_activity=rows.copy(),binding=control['binding'],
                    device=device,backend='original_FlyVis_CUDA',mode='Full',decoder_status='CONNECTED',spatial_transform=item['transform'],
                    execution_kind='LIVE_DIGITAL_GPU' if control['source_kind']=='digital_direct' else 'LIVE_CAMERA_GPU',
                    actual_new_computation=True,evidence_level='ACTUAL_CONTINUOUS_FULL_GPU_STATE',PL_execution=False,
                    model_lag_s=lag,model_epoch_note='compute epoch starts at first official converted input; receipt-to-draw includes conversion startup',
                    timing=summary,timing_summary_age_s=summary_age,REALTIME_STREAM_PASS='NOT_RUN')
                timing.add('display_packet_build',time.perf_counter()-packet_started)
                with timing.measure('evidence_enqueue'):writer.put('snapshot',(packet,full))
                with hub.lock:gate('publish_final');hub.packet=packet
                probes.collect();last_display=time.monotonic()
    except BaseException as exc:
        reason=hub.error or str(exc);success=reason=='STREAM_STOP_REQUESTED';hub.revoke(reason)
        if not success:write(folder/'failure.json',dict(error=reason,committed_steps=hub.steps,utc=utc()))
    finally:
        # Stop acknowledgement is published only after actual in-flight CUDA completes.
        hub.stopping=True;hub.packet=None
        try:
            torch.cuda.synchronize();probes.close();oracle.assert_weights_unchanged();decoder.assert_weights_unchanged()
            if decoder_audit:decoder_audit.close()
            if compute:compute.close()
            writer.close()
            hub.stopped=True;hub.state='STOPPED' if success else 'FAILED'
            write(folder/'result.json',dict(**hub.status(),success=success,reason=reason,stages=timing.summary(),
                device=device,model=registry.data['model'],original_weights_unchanged=True,decoder_unchanged=True,
                host_scheduling=dict(python_switch_interval_s=sys.getswitchinterval(),timing_summary_interval_s=1.),
                input_guard_adapter=compute.info() if compute else None,packed_decoder_audit_calls=decoder_audit.calls if decoder_audit else 0,
                evidence_queue_peak=writer.peak,CUDA_completed_before_stop_ack=True,snapshots=serial if 'serial' in locals() else 0,
                LIVE_INTERACTIVE_GUI_PASS='PENDING_BROWSER_EVIDENCE'))
            write(folder/'manifest.json',{str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()
                and (p.parent.name in ('sources','snapshots') or p.name in ('control.json','result.json','failure.json','step_commits.jsonl'))})
        finally:
            write(folder/'STOP_REQUEST.json',dict(reason=reason,utc=utc()))
            if process:
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
            if log:log.close()
            # Give the Windows bridge a chance to receive the stop acknowledgement.
            time.sleep(.4);rpc.close()
    return success
