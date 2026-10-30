"""Windows input owner and same-origin GUI consumer of the authenticated stream."""
import base64
from collections import OrderedDict
import hashlib
import io
import json
import threading
import time
import uuid
from live_protocol import HERE,load,require,utc,write
from camera_stream_protocol import dependencies
from spatial_state import SpatialRegistry
from realtime_timing import Timings,SummaryCache,latency_sample
from stream_transport import RPC
from stream_wire import decode_packet
from stream_clock import clock_spec,control_clock,model_source_time

def digital_spec(value):
    require(set(value)=={'polarity','direction_deg','speed_px_s'},'DIGITAL_PARAMETERS')
    require(value['polarity'] in ('ON','OFF') and value['direction_deg'] in range(0,360,30),'DIGITAL_DIRECTION')
    require(type(value['speed_px_s']) in (int,float) and 1<=value['speed_px_s']<=640,'DIGITAL_SPEED')
    return value

class StreamBridge:
    def init__(self,adapter):
        self.adapter=adapter;self.control=None;self.root=None;self.client=None;self.thread=None;self.camera_thread=None
        self.stop_event=threading.Event();self.last_client_poll=0.;self.lock=threading.RLock();self.input_lock=threading.Lock()
        self.updated=threading.Condition(self.lock)
        self.spatial=SpatialRegistry();self.dependencies=dependencies();self.last_status=None;self.packet=None;self.packets=OrderedDict()
        self.error=None;self.capture_closed=True;self.sequence=0;self.origin=None;self.draw_serials=set();self.draw_timing=Timings()
        self.draw_summary_cache=SummaryCache();self.wire_packet=None;self.input_client=None;self.camera_info=None;self.last_received=None
    def touch(self):self.last_client_poll=time.monotonic()
    def clock(self):return dict(clock='Windows_perf_counter_ns',server_monotonic_ns=time.perf_counter_ns(),valid_for_s=5)
    def start(self,body):
        with self.lock:
            require(self.control is None,'STREAM_SESSION_ALREADY_ATTEMPTED_RESTART_ENTRY')
            self.adapter.connected();require(self.adapter.session.get('stream_enabled'),'START_ENTRY_REQUIRES_STREAM')
            kind=body.get('source_kind','real_windows_camera')
            require(kind in ('digital_direct','real_windows_camera'),'SOURCE_KIND')
            if kind=='real_windows_camera':
                require(self.adapter.session.get('camera_enabled'),'CAMERA_MANUAL_ENTRY_REQUIRED')
                require(type(body.get('camera_id')) is int and 0<=body['camera_id']<=15,'CAMERA_ID')
            else:digital_spec(body['parameters'])
            clock=clock_spec(body.get('target_steps_per_s',100 if kind=='real_windows_camera' else 200))
            require(kind=='real_windows_camera' or clock['target_steps_per_s']==200,'DIGITAL_ORIGINAL_CLOCK_ONLY')
            endpoint=load(self.adapter.root/'stream_endpoint.json');require(endpoint['session_id']==self.adapter.session['session_id'],'STREAM_SESSION_IDENTITY')
            self.client=RPC(endpoint);self.input_client=RPC(endpoint);data=self.adapter.registry.data
            self.root=self.adapter.root/'stream'
            self.control=dict(schema='flyvis-continuous-control/v1',session_id=endpoint['session_id'],run_id=uuid.uuid4().hex,
                source_kind=kind,mode='Full',PL_execution=False,spatial_map_sha256=self.spatial.digest,clock=clock,
                binding=dict(model=data['model'],source_kind=kind,dt_s=.005,node_map_sha256=data['pins']['nodes']['sha256'],
                    clock=clock,camera_dependencies=self.dependencies,initialization='ONE_SHARED_GRAY_ADAPTED_FULL_INITIAL_STATE_AT_SESSION_START',
                    digital_renderer='original phase4_phone_camera player.js render(spec,elapsed)' if kind=='digital_direct' else None),
                created_utc=utc(),parameters=body.get('parameters'),camera_id=body.get('camera_id'))
            try:self.last_status=self.client.call('start',self.control)
            except BaseException:self.control=None;self.client.close();raise
            self.touch();self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
            if kind=='real_windows_camera':
                self.capture_closed=False;self.camera_thread=threading.Thread(target=self.capture,daemon=True);self.camera_thread.start()
            return self.status()
    def loop(self):
        try:
            while not self.stop_event.is_set():
                require(time.monotonic()-self.last_client_poll<3,'GUI_CONSUMER_DISCONNECTED')
                response=self.client.call('latest',{'after_serial':self.packet['serial'] if self.packet else -1,'wait_ms':100});status=response['status'];packet=response['packet']
                wire=packet
                if packet:packet=decode_packet(packet)
                with self.lock:
                    self.last_status=status
                    if status['result_valid'] and packet:
                        self.validate(packet);self.packet=packet;self.wire_packet=wire;self.packets[packet['serial']]=packet
                        while len(self.packets)>32:self.packets.popitem(last=False)
                    elif not status['result_valid']:self.packet=None
                    self.updated.notify_all()
                if not status['result_valid']:break
        except BaseException as e:self.error=str(e)
        finally:
            with self.lock:self.packet=None;self.stop_event.set();self.updated.notify_all()
            try:self.last_status=self.client.call('stop',{'error':self.error})
            except (OSError,ValueError):pass
    def validate(self,p):
        c=self.control
        require(p['schema']=='flyvis-continuous-output/v1' and p['session_id']==c['session_id'] and p['run_id']==c['run_id'],'STREAM_OUTPUT_RUN')
        require(p['source_kind']==c['source_kind'] and p['binding']==c['binding'] and p['state_token']==p['step_id']+1,'STREAM_OUTPUT_BINDING')
        if 'commit_semantics' in p:
            require(p['commit_semantics']=='FSYNC_CONFIRMED_PUBLIC_WATERMARK' and type(p.get('durable_commit_steps')) is int
                    and p['durable_commit_steps']==p['state_token'],'STREAM_UNSAVED_STATE_REJECTED')
        require(p['device']['type']=='cuda' and p['actual_new_computation'] is True and p['PL_execution'] is False,'ACTUAL_GPU_REQUIRED')
        require(p['evidence_level']=='ACTUAL_CONTINUOUS_FULL_GPU_STATE' and p['execution_kind']==('LIVE_DIGITAL_GPU' if c['source_kind']=='digital_direct' else 'LIVE_CAMERA_GPU'),'STREAM_EXECUTION_KIND')
        clock=control_clock(c)
        require(p.get('clock',clock)==clock and p['input_time_s']==p['step_id']*.005 and p['activity_time_s']==p['input_time_s']+.005
                and model_source_time(p['source'],clock)<=p['input_time_s'],'STREAM_TIME')
        import numpy as np
        x=np.asarray(p['input_hex'],dtype=np.float32);flow=np.asarray(p['flow']);activity=np.asarray(p['activity'])
        require(x.shape==(721,) and flow.shape==(2,721) and activity.shape==(8,) and np.isfinite(flow).all() and np.isfinite(activity).all(),'STREAM_ARRAYS')
        require(np.isfinite(x).all() and np.all((x>=0)&(x<=1)) and hashlib.sha256(x.tobytes()).hexdigest()==p['source']['hex_values_sha256'],'STREAM_INPUT_SHA')
        require(hashlib.sha256(base64.b64decode(p['preview_png'],validate=True)).hexdigest()==p['source']['png_sha256'],'STREAM_PREVIEW_SHA')
        self.spatial.validate(p['spatial'],p['run_id'],p['step_id'],p['activity_time_s'],'Full')
    def status(self):
        if not self.control:return dict(status='NOT_STARTED',result_valid=False,run_id=None,FPGA_status='NOT_CONNECTED')
        s=self.last_status or {};failed=self.error or not s.get('result_valid',False) or self.stop_event.is_set()
        if self.error:s={**s,'error':self.error}
        return dict(status='NOT_AVAILABLE' if failed else s.get('status'),result_valid=not bool(failed),run_id=self.control['run_id'],session_id=self.control['session_id'],
            source_kind=self.control['source_kind'],compute=s,capture=dict(state='INPUT_STOPPED' if failed else 'CAPTURING' if self.sequence else 'WAITING_INPUT',
                measured_delivery_fps=(self.sequence-1)/max(.001,((self.last_received or self.origin)-self.origin)/1e9) if self.sequence>1 else None,
                frames_read=self.sequence,source_frames_dropped_before_render=0,closed=self.capture_closed,
                camera=self.camera_info,sensor_drop_count=None,sensor_exposure_time_available=False),
            binding=self.control['binding'],renderer_ready=s.get('renderer_ready',False),stop_acknowledged=s.get('stop_acknowledged',False),PL_execution=False,FPGA_status='NOT_CONNECTED')
    def input(self,body):
        require(self.control and body['run_id']==self.control['run_id'] and self.control['source_kind']=='digital_direct','DIGITAL_SESSION')
        require(set(body)=={'run_id','sequence','png','parameters','segment_id','render_elapsed_s'},'DIGITAL_INPUT_SCHEMA')
        digital_spec(body['parameters']);require(type(body['segment_id']) is int and body['segment_id']>=0 and 0<=body['render_elapsed_s']<301,'DIGITAL_EVENT')
        require(body['sequence']==self.sequence,'DIGITAL_INPUT_SEQUENCE');png=base64.b64decode(body['png'],validate=True)
        from PIL import Image
        with Image.open(io.BytesIO(png)) as image:require(image.format=='PNG' and image.size==(640,640),'DIGITAL_RENDER_SIZE')
        return self.push(png,dict(parameters=body['parameters'],segment_id=body['segment_id'],render_elapsed_s=body['render_elapsed_s']))
    def push(self,png,extra,received=None):
        with self.input_lock:
            require(not self.stop_event.is_set(),(self.last_status or {}).get('error') or 'STREAM_INPUT_STOPPED')
            stamp=received or time.perf_counter_ns()
            if self.origin is None:self.origin=stamp
            png_digest=hashlib.sha256(png).hexdigest()
            source=dict(run_id=self.control['run_id'],source_kind=self.control['source_kind'],sequence=self.sequence,
                received_monotonic_ns=stamp,received_utc=utc(),relative_s=(stamp-self.origin)/1e9,
                png_sha256=png_digest,sha256=png_digest,timestamp_kind='Windows_receipt_not_sensor',**extra)
            source['model_relative_s']=model_source_time(source,control_clock(self.control))
            result=self.input_client.call('input',dict(source=source,png=base64.b64encode(png).decode()));self.sequence+=1;self.last_received=stamp;return result
    def capture(self):
        camera=None
        try:
            while not self.status().get('renderer_ready'):
                require(not self.stop_event.wait(.05),'CAPTURE_STOPPED')
            import sys
            sys.path.insert(0,str(HERE.parent))
            from camera_pipeline.capture import open_camera,read_frame
            # Bound input conversion/transfer load, without skipping neural steps.
            # Driver buffering/drops remain unknown; this is the host read cadence.
            camera=open_camera(self.control['camera_id'],backend='dshow',width=640,height=480,fps=15)
            self.camera_info=camera.status()
            next_read=time.monotonic()
            while not self.stop_event.is_set():
                if self.stop_event.wait(max(0,next_read-time.monotonic())):break
                frame=read_frame(camera);ok,png=camera.cv2.imencode('.png',frame.bgr);require(ok,'PNG_ENCODING')
                next_read=time.monotonic()+1/15
                self.camera_info=camera.status()
                self.push(png.tobytes(),dict(capture_read_s=frame.read_duration_s,camera_sequence=frame.sequence,
                    camera_id=self.control['camera_id'],camera_backend=self.camera_info['backend'],
                    camera_resolution=[frame.bgr.shape[1],frame.bgr.shape[0]],camera_received_utc=frame.received_utc,
                    camera_host_read_limit_fps=15),frame.received_monotonic_ns)
        except BaseException as e:
            if not self.stop_event.is_set():self.error=str(e);self.stop_event.set()
        finally:
            try:
                if camera:camera.close();self.camera_info=camera.status()
            finally:
                self.capture_closed=bool(camera is None or camera.closed)
                write(self.root/'camera_capture.json',dict(schema='flyvis-camera-stream-capture/v1',
                    session_id=self.control['session_id'],run_id=self.control['run_id'],source_kind='real_windows_camera',
                    capture=self.camera_info,closed=self.capture_closed,error=self.error,
                    accepted_source_frames=self.sequence,source_frames_dropped_before_render=0,host_read_limit_fps=15,
                    timestamp_semantics='Windows read completion, not sensor exposure',
                    spatial_policy='full-field',temporal_policy='causal zero-order hold on original 5ms model grid',
                    clock=control_clock(self.control),PL_execution=False))
    def latest(self,wire=False,after=None,wait_ms=0):
        require(type(wait_ms) is int and 0<=wait_ms<=200,'STREAM_WAIT_BOUND')
        if after is not None and not self.status()['result_valid']:return dict(status=self.status(),packet=None)
        require(self.status()['result_valid'],'STREAM_RESULT_REVOKED')
        with self.lock:
            if wait_ms:
                self.updated.wait_for(lambda:self.stop_event.is_set() or self.error or not self.status()['result_valid'] or (self.packet is not None and self.packet['serial']!=after),timeout=wait_ms/1000)
                if not self.status()['result_valid']:return dict(status=self.status(),packet=None)
            if after is not None and (self.packet is None or self.packet['serial']==after):return dict(status=self.status(),packet=None)
            require(self.packet is not None,'WAITING_FIRST_PACKET');return dict(status=self.status(),packet=self.wire_packet if wire else self.packet)
    def frame(self,sequence,run_id):
        require(self.status()['result_valid'] and run_id==self.control['run_id'],'STREAM_RESULT_REVOKED')
        with self.lock:
            matches=[p for p in self.packets.values() if p['source']['sequence']==sequence]
            require(matches,'SOURCE_PACKET_EXPIRED');return base64.b64decode(matches[-1]['preview_png'])
    def record_draw(self,body):
        require(self.status()['result_valid'] and body['run_id']==self.control['run_id'],'DRAW_RESULT_REVOKED')
        with self.lock:p=self.packets.get(body['serial'])
        require(p and p['step_id']==body['step_id'] and body['serial'] not in self.draw_serials,'DRAW_PACKET_IDENTITY_OR_DUPLICATE')
        require(0<=body['clock_age_s']<=5 and abs(time.perf_counter_ns()-body['draw_server_monotonic_ns'])<2e9,'DRAW_CLOCK_STALE')
        sample=latency_sample(p['source'],body['draw_server_monotonic_ns'],body['clock_uncertainty_ms'])
        self.draw_serials.add(body['serial']);require(len(self.draw_serials)<=7000,'DRAW_BOUND')
        self.draw_timing.add('receipt_to_render_upper_bound',sample['upper_ms']/1000)
        with (self.root/'display_receipts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({**body,**sample})+'\n')
        summary,age=self.draw_summary_cache.get(self.draw_timing)
        return dict(summary=summary,summary_age_s=age,latency=sample,REALTIME_STREAM_PASS='NOT_RUN')
    def summary(self):
        require(self.control is not None,'STREAM_NOT_STARTED')
        from stream_manual_summary import manual_summary
        summary=manual_summary(self.root,self.control)
        if summary['status']!='WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION':write(self.root/'manual_summary.json',summary)
        return summary
    def stop(self,body=None):
        if body:
            require(set(body)=={'run_id','error'} and self.control and body['run_id']==self.control['run_id'],'CONSUMER_STOP_RUN')
            require(isinstance(body['error'],str) and 0<len(body['error'])<=1000,'CONSUMER_STOP_ERROR')
            with self.lock:
                self.error=self.error or 'BROWSER_CONSUMER: '+body['error']
                write(self.root/'browser_failure.json',dict(run_id=self.control['run_id'],session_id=self.control['session_id'],error=self.error,utc=utc()))
        if self.control:
            self.stop_event.set();self.packet=None
            try:self.last_status=self.client.call('stop',{'error':self.error})
            except (OSError,ValueError):pass
            if self.thread and self.thread is not threading.current_thread():self.thread.join(4)
            if self.camera_thread:self.camera_thread.join(2)
            if self.input_client:self.input_client.close()
            # A stop request is not a stop acknowledgement. Poll recorded GPU completion.
            if (self.root/'result.json').exists():
                r=load(self.root/'result.json')
                if r.get('CUDA_completed_before_stop_ack'):self.last_status=r
            write(self.root/'display_summary.json',dict(draws=len(self.draw_serials),stages=self.draw_timing.summary(),
                transport_stages=self.client.timings.summary() if self.client else {},
                input_transport_stages=self.input_client.timings.summary() if self.input_client else {},
                source_kind=self.control['source_kind'],run_id=self.control['run_id'],REALTIME_STREAM_PASS='NOT_RUN'))
        return self.status()
