"""Unified digital/camera stream: original Full GPU and decoder, bounded memory IPC."""
import base64
from collections import deque
import hashlib
import io
import json
import subprocess
import sys
import threading
import time
import numpy as np
from live_protocol import HERE,canonical,checked_commit,load,require,sha,utc,write
from camera_stream_protocol import PreparedCausalSelector,DT,MAX_LAG_S,dependencies
from spatial_state import SpatialRegistry
from realtime_timing import Timings,CudaProbes,SummaryCache,StepTrace,host_scheduling
from stream_transport import LocalRPC
from checked_full import CombinedCheckedFull
from decoder_audit import PackedDecoderAudit
from stream_wire import encode_packet
from stream_evidence import CommitJournal,EvidenceWriter
from stream_clock import control_clock,model_source_time,schedule
from stream_cadence import DisplayCadence


class StreamHub:
    def init__(self,session_id):
        self.session_id=session_id;self.control=None;self.raw=deque();self.converted=deque(maxlen=96);self.lock=threading.RLock()
        self.packet=None;self.error=None;self.stopping=False;self.stopped=False;self.renderer_ready=False
        self.bridge_at=0.;self.renderer_at=0.;self.last_source=-1;self.last_render=-1;self.raw_peak=0;self.hex_peak=0
        self.state='WAITING_INPUT_SELECTION';self.steps=0;self.started=None;self.finished_at=None;self.serial=0;self.writer=None;self.computed_steps=0;self.journal=None
        self.updated=threading.Condition(self.lock)
    def check(self):
        require(not self.stopping,'STREAM_STOP_REQUESTED');require(self.error is None,'STREAM_FAILED '+str(self.error))
        if self.control:
            require(time.monotonic()-self.bridge_at<3,'STREAM_BRIDGE_DISCONNECTED')
            if self.renderer_ready:require(time.monotonic()-self.renderer_at<3,'STREAM_RENDERER_DISCONNECTED')
    def revoke(self,error):
        with self.lock:
            self.error=str(error);self.packet=None;self.state='FAILED';self.stopping=True;self.updated.notify_all()
    def dispatch(self,role,op,body):
        if op=='converted' and self.writer:
            with self.writer.reserved('source') as ticket:
                return self._dispatch(role,op,body,ticket)
        return self._dispatch(role,op,body)
    def _dispatch(self,role,op,body,source_ticket=None):
        with self.lock:
            if role=='bridge':self.bridge_at=time.monotonic()
            else:self.renderer_at=time.monotonic()
            if op=='status':return self.status()
            if op=='stop':
                require(role=='bridge','STREAM_ROLE')
                if body and body.get('error') and not self.error:self.error=str(body['error'])
                self.stopping=True;self.packet=None;self.state='STOPPING';self.updated.notify_all();return self.status()
            if op=='start':
                require(role=='bridge' and self.control is None,'STREAM_ALREADY_STARTED')
                require(body['session_id']==self.session_id and body['source_kind'] in ('digital_direct','real_windows_camera') and body['mode']=='Full','STREAM_CONTROL')
                require(len(body['run_id'])==32 and body['PL_execution'] is False,'STREAM_RUN');control_clock(body);self.control=body;self.state='WAITING_CONVERTER';return self.status()
            if op=='latest' and (self.stopping or self.error or self.stopped):return dict(status=self.status(),packet=None)
            self.check()
            if op=='ready':
                require(role=='renderer','STREAM_ROLE');self.renderer_ready=True;self.state='WAITING_SOURCE';return True
            if op=='input':
                require(role=='bridge' and self.control is not None and self.renderer_ready,'STREAM_INPUT_BEFORE_READY')
                f=body['source'];require(f['run_id']==self.control['run_id'] and f['source_kind']==self.control['source_kind'],'STREAM_INPUT_RUN')
                require(f['sequence']==self.last_source+1 and len(self.raw)<32,'SOURCE_SEQUENCE_OR_QUEUE_OVERRUN')
                require(np.isfinite(f['relative_s']) and f['relative_s']>=0,'SOURCE_TIME')
                model_source_time(f,control_clock(self.control))
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
                if self.writer:self.writer.submit(source_ticket,body)
                self.converted.append(body);self.last_render=f['sequence'];self.hex_peak=max(self.hex_peak,len(self.converted))
                return True
            if op=='latest':
                wait_ms=body.get('wait_ms',0) if body else 0
                require(type(wait_ms) is int and 0<=wait_ms<=200,'STREAM_WAIT_BOUND')
                if wait_ms:
                    after=body.get('after_serial',-1)
                    self.updated.wait_for(lambda:self.stopping or self.error or self.stopped or (self.packet is not None and self.packet['serial']!=after),timeout=wait_ms/1000)
                if self.stopping or self.error or self.stopped:return dict(status=self.status(),packet=None)
                p=self.packet
                if p and body and body.get('after_serial')==p['serial']:p=None
                return dict(status=self.status(),packet=p)
            raise ValueError('UNKNOWN_STREAM_OPERATION')
    def status(self):
        elapsed=(self.finished_at or time.monotonic())-self.started if self.started else None
        return dict(status=self.state,run_id=self.control['run_id'] if self.control else None,session_id=self.session_id,
            source_kind=self.control['source_kind'] if self.control else None,result_valid=not(self.stopping or self.error or self.stopped),
            renderer_ready=self.renderer_ready,committed_steps=self.steps,computed_steps=self.computed_steps,
            journal_pending_steps=self.computed_steps-self.steps,commit_semantics='FSYNC_CONFIRMED_PUBLIC_WATERMARK',simulation_time_s=self.steps*DT,
            inference_steps_per_s=self.steps/elapsed if elapsed else None,elapsed_s=elapsed,error=self.error,
            clock=control_clock(self.control) if self.control else None,wall_elapsed_s=elapsed,
            source_queue_length=len(self.raw),input_queue_length=len(self.converted),raw_queue_peak=self.raw_peak,hex_queue_peak=self.hex_peak,
            input_frames=self.last_source+1,converted_frames=self.last_render+1,source_frames_dropped_before_render=0,
            stop_acknowledged=self.stopped,FPGA_status='NOT_CONNECTED',PL_execution=False,REALTIME_STREAM_PASS='NOT_RUN')


def run_stream(root,session,registry,oracle,decoder,torch,device,scope_check):
    with host_scheduling(.001):
        return _run_stream(root,session,registry,oracle,decoder,torch,device,scope_check)


def _run_stream(root,session,registry,oracle,decoder,torch,device,scope_check):
    dependencies();require(decoder is not None,'OFFICIAL_DECODER_REQUIRED');spatial=SpatialRegistry()
    hub=StreamHub(session['session_id'])
    rpc=LocalRPC(session['session_id'],hub.dispatch,port=session['stream_rpc_port']) if 'stream_rpc_port' in session else LocalRPC(session['session_id'],hub.dispatch)
    write(root/'stream_endpoint.json',rpc.endpoint)
    folder=root/'stream';folder.mkdir();writer=EvidenceWriter(folder);hub.writer=writer
    journal=CommitJournal(folder/'step_commits.jsonl');hub.journal=journal;working_steps=0;snapshot_ticket=None
    timing=Timings();summary_cache=SummaryCache();probes=CudaProbes(torch,timing);process=None;log=None;success=False;reason=None;rows=[]
    compute=None;decoder_audit=None
    probes.wrap(oracle.net,'_next_state','neural_update_cuda_stream',sample_every=10);probes.wrap(decoder.decoder,'forward','decoder_forward_cuda_stream')
    trace=StepTrace();timing.trace=trace
    def gate(operation='check'):
        if trace.current is None:
            scope_check(operation);hub.check();require(writer.error is None,'EVIDENCE_FAILED '+str(writer.error));return
        with timing.measure('scope_and_stream_gate'):
            scope_check(operation);hub.check();require(writer.error is None,'EVIDENCE_FAILED '+str(writer.error))
    try:
        compute=CombinedCheckedFull(oracle,torch,timing,cache_validated_tensors=True)
        # Stream interval of the reduction itself; the host gate also waits for
        # earlier queued CUDA work. No extra synchronize or skipped validation.
        probes.wrap(compute,'candidate_predicate','candidate_finite_cuda_stream',sample_every=10)
        decoder_audit=PackedDecoderAudit(decoder,timing).install()
        wait=time.monotonic()
        while hub.control is None:scope_check('wait_stream_start');require(time.monotonic()-wait<180,'STREAM_INPUT_START_TIMEOUT');time.sleep(.02)
        control=hub.control;require(control['binding']['model']==registry.data['model'] and control['spatial_map_sha256']==spatial.digest,'STREAM_BINDING')
        clock=control_clock(control)
        write(folder/'control.json',control)
        wait=time.monotonic() # First-input deadline starts at selection, not model readiness.
        log=(folder/'renderer.log').open('ab')
        process=subprocess.Popen([sys.executable,'-B',str(HERE/'stream_renderer.py'),'--root',str(root)],stdout=log,stderr=subprocess.STDOUT)
        state=torch.as_tensor(np.load(registry.path_for('initial'),allow_pickle=False),device='cuda',dtype=torch.float32).clone()
        selector=PreparedCausalSelector();cached=-1;epoch=None;serial=0;history_serial=-1;frames=[];display=DisplayCadence(15)
        while True:
            gate();require(working_steps<60000,'STREAM_STEP_LIMIT')
            require(process.poll() is None,'OFFICIAL_RENDERER_EXITED')
            with timing.measure('input_history_snapshot'),hub.lock:
                changed=history_serial!=hub.last_render
                if changed:frames=list(hub.converted);observed_history_serial=hub.last_render
            if not frames:require(time.monotonic()-wait<60,'STREAM_FIRST_INPUT_TIMEOUT');time.sleep(.002);continue
            if epoch is None:epoch=time.monotonic();hub.started=epoch
            elapsed=time.monotonic()-epoch;delay,lag=schedule(working_steps,elapsed,clock)
            if elapsed>=session.get('stream_observation_s',300):raise ValueError('STREAM_OBSERVATION_COMPLETE')
            require(lag<=MAX_LAG_S,'MODEL_LAG_LIMIT_NO_STEP_SKIP')
            if delay:time.sleep(min(.001,delay));continue
            with timing.measure('causal_input_selection'):
                if changed:
                    selector.prepare([dict(f['source'],relative_s=model_source_time(f['source'],clock)) for f in frames])
                    history_serial=observed_history_serial
                _,index=selector.select(working_steps);item=frames[index];chosen=item['source']
            if cached!=chosen['sequence']:
                with timing.measure('input_H2D'):values=np.asarray(item['values'],dtype=np.float32);tensor=torch.as_tensor(values,device='cuda')
                cached=chosen['sequence']
            # Reserve scarce resources and encode the row BEFORE neural work.
            k=working_steps
            row=dict(run_id=control['run_id'],step_id=k,state_token=k+1,status='COMMITTED',source_sequence=cached,
                input_time_s=k*DT,activity_time_s=k*DT+DT,input_hex_values_sha256=chosen['hex_values_sha256'],old_state_source='OWN_CONTINUOUS_CUDA_STATE',
                scheduled_wall_time_s=k/clock['target_steps_per_s'],source_wall_time_s=chosen['relative_s'],source_model_time_s=model_source_time(chosen,clock))
            display_due=display.due(elapsed)
            trace.begin(k,elapsed,lag,display_due)
            with timing.measure('snapshot_reservation'):
                snapshot_ticket=writer.reserve('snapshot') if display_due else None
            with timing.measure('journal_prepare'):ticket=journal.prepare(row)
            try:
                host_cpu=time.thread_time()
                with timing.measure('Full_host_including_original_checks'):candidate=compute.step(state,tensor)
                timing.add('Full_host_thread_CPU',time.thread_time()-host_cpu)
                with timing.measure('candidate_finite_CUDA_wait'):compute.validate_candidate(candidate)
                with timing.measure('memory_commit_gate'),hub.lock:
                    state=journal.accept(ticket,candidate,gate,compute.commit)
                    selector.commit(chosen,k);working_steps+=1;hub.computed_steps=working_steps;hub.state='RUNNING'
            finally:journal.cancel(ticket)
            if journal.pending>=journal.capacity or display_due:
                with timing.measure('durable_commit_barrier'):durable=journal.flush()
                with hub.lock:hub.steps=durable
            if display_due:
                with timing.measure('display_full_D2H'):full=state.detach().cpu().numpy().copy()
                with timing.measure('official_decoder_host'):flow=decoder.decode(full[None,None],chunk_frames=1)[0,0]
                gate('publish');serial+=1;activity=full[registry.data['central_global_ids']].tolist()
                rows.append(dict(step_id=k,state_token=k+1,activity_time_s=k*DT+DT,activity=activity));rows=rows[-200:]
                with timing.measure('timing_summary_refresh'):summary,summary_age=summary_cache.get(timing)
                packet_started=time.perf_counter()
                packet=dict(schema='flyvis-continuous-output/v1',**row,serial=serial,session_id=session['session_id'],
                    source=chosen,source_kind=control['source_kind'],preview_png=item['png'],activity=activity,input_hex=values,flow=flow,
                    spatial=spatial.packet(full,control['run_id'],k,k*DT+DT,as_array=True),recent_activity=rows.copy(),binding=control['binding'],
                    device=device,backend='original_FlyVis_CUDA',mode='Full',decoder_status='CONNECTED',spatial_transform=item['transform'],
                    execution_kind='LIVE_DIGITAL_GPU' if control['source_kind']=='digital_direct' else 'LIVE_CAMERA_GPU',
                    actual_new_computation=True,evidence_level='ACTUAL_CONTINUOUS_FULL_GPU_STATE',PL_execution=False,
                    clock=clock,wall_elapsed_s=time.monotonic()-epoch,schedule_lag_wall_s=lag,
                    model_lag_s=lag*clock['model_seconds_per_wall_second'],model_epoch_note='compute wall epoch starts at first official converted input; source wall epoch starts at Windows first receipt; model source time scales capture-relative time; receipt-to-draw includes startup',
                    timing=summary,timing_summary_age_s=summary_age,durable_commit_steps=journal.durable_steps,
                    commit_semantics='FSYNC_CONFIRMED_PUBLIC_WATERMARK',REALTIME_STREAM_PASS='NOT_RUN')
                timing.add('display_packet_build',time.perf_counter()-packet_started)
                with timing.measure('evidence_enqueue'):writer.submit(snapshot_ticket,(packet,full));snapshot_ticket=None
                with timing.measure('lossless_wire_pack'):wire=encode_packet(packet)
                with timing.measure('publish_lock_and_gate'),hub.lock:
                    gate('publish_final');hub.packet=wire;hub.updated.notify_all()
                probes.collect();display.published(time.monotonic()-epoch)
            trace.finish(working_steps,journal.durable_steps)
    except BaseException as exc:
        reason=hub.error or str(exc);success=reason in ('STREAM_STOP_REQUESTED','STREAM_OBSERVATION_COMPLETE');hub.revoke(reason)
        if not success:write(folder/'failure.json',dict(error=reason,committed_steps=hub.steps,utc=utc()))
    finally:
        # Stop acknowledgement is published only after actual in-flight CUDA completes.
        hub.finished_at=time.monotonic();hub.stopping=True;hub.packet=None
        try:
            cleanup_errors={};cuda_complete=False;weights_ok=False;decoder_ok=False
            def finish(name,action):
                try:action()
                except BaseException as error:cleanup_errors[name]=repr(error)
            finish('cuda',torch.cuda.synchronize);cuda_complete='cuda' not in cleanup_errors
            finish('probes',probes.close)
            finish('weights',oracle.assert_weights_unchanged);weights_ok='weights' not in cleanup_errors
            finish('decoder',decoder.assert_weights_unchanged);decoder_ok='decoder' not in cleanup_errors
            if decoder_audit:finish('decoder_audit',decoder_audit.close)
            if compute:finish('compute',compute.close)
            if snapshot_ticket:writer.cancel(snapshot_ticket)
            finish('journal',journal.close);hub.steps=journal.durable_steps
            finish('assets',writer.close)
            trace.finish(working_steps,journal.durable_steps)
            if hub.control:
                finish('step_trace',lambda:trace.save(folder/'step_timing.jsonl',session['session_id'],hub.control['run_id']))
            if cleanup_errors or journal.durable_steps!=working_steps:
                success=False;reason=reason if reason not in (None,'STREAM_STOP_REQUESTED','STREAM_OBSERVATION_COMPLETE') else 'EVIDENCE_OR_CUDA_FINALIZATION_FAILED'
            hub.error=reason;hub.stopped=cuda_complete;hub.state='STOPPED' if success else 'FAILED'
            evidence_complete=not cleanup_errors and journal.durable_steps==working_steps
            if not success:write(folder/'failure.json',dict(error=reason,computed_steps=working_steps,committed_steps=hub.steps,cleanup_errors=cleanup_errors,utc=utc()))
            write(folder/'result.json',dict(**hub.status(),success=success,reason=reason,stages=timing.summary(),
                device=device,model=registry.data['model'],original_weights_unchanged=weights_ok,decoder_unchanged=decoder_ok,
                host_scheduling=dict(python_switch_interval_s=sys.getswitchinterval(),timing_summary_interval_s=1.),
                cuda_probe_sampling=dict(neural_update_every_steps=10,candidate_predicate_every_steps=10,decoder_every_call=1,
                    note='Timing only is sampled; all candidate checks and COMMIT gates still run every model step.'),
                input_guard_adapter=compute.info() if compute else None,packed_decoder_audit_calls=decoder_audit.calls if decoder_audit else 0,
                evidence_queue_peak=writer.peak,asset_writer=writer.info(),commit_journal=journal.info(),
                evidence_complete=evidence_complete,cleanup_errors=cleanup_errors,CUDA_completed_before_stop_ack=cuda_complete,snapshots=serial if 'serial' in locals() else 0,
                host_step_trace=dict(file='step_timing.jsonl',rows=len(trace.rows),write_during_compute=False,
                    semantics='Nested host wall/thread CPU intervals; difference includes CUDA/I/O wait and OS scheduling, not pure GPU kernels'),
                LIVE_INTERACTIVE_GUI_PASS='PENDING_BROWSER_EVIDENCE'))
            write(folder/'manifest.json',{str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()
                and (p.parent.name in ('sources','snapshots') or p.name in ('control.json','result.json','failure.json','step_commits.jsonl','step_timing.jsonl'))})
        finally:
            write(folder/'STOP_REQUEST.json',dict(reason=reason,utc=utc()))
            if process:
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
            if log:log.close()
            # Give the Windows bridge a chance to receive the stop acknowledgement.
            time.sleep(.4);rpc.close()
    return success
