"""Windows bridge using ONLY the original camera_pipeline CameraSession."""
import io
import os
import threading
import time
import uuid
from pathlib import Path
import numpy as np
from live_protocol import HERE,canonical,load,require,sha,utc,write
from camera_stream_protocol import CAPACITY,DISPLAY_CAPACITY,admitted_packet,dependencies,relative_asset_path
from spatial_state import SpatialRegistry
from realtime_timing import Timings,latency_sample


class CameraStreamBridge:
    def init__(self,adapter):
        self.adapter=adapter;self.thread=None;self.stop_event=threading.Event();self.control=None;self.lock=threading.RLock();self.serial=0;self.last_client_poll=0.
        self.dependencies=dependencies()
        self.spatial=SpatialRegistry();self.draw_serials=set();self.draw_timing=Timings()
    def clock(self):
        return {'clock':'Windows_perf_counter_ns','server_monotonic_ns':time.perf_counter_ns(),'valid_for_s':5}
    def record_draw(self,body):
        require(self.control and body['run_id']==self.control['run_id'],'DRAW_RUN_IDENTITY')
        require(self.status()['result_valid'],'DRAW_RESULT_REVOKED')
        serial=body['serial'];require(type(serial) is int and serial not in self.draw_serials,'DUPLICATE_DRAW')
        p=load(self.root/'display'/f'{serial%DISPLAY_CAPACITY:02}.json')
        require(p['serial']==serial and p['run_id']==body['run_id'] and p['step_id']==body['step_id'],'DRAW_PACKET_IDENTITY')
        stamp=body['draw_server_monotonic_ns'];now=time.perf_counter_ns()
        require(type(stamp) in (int,float) and abs(now-stamp)<2e9 and 0<=body['clock_age_s']<=5,'DRAW_CLOCK_STALE')
        sample=latency_sample(p['source'],stamp,body['clock_uncertainty_ms'])
        self.draw_serials.add(serial);require(len(self.draw_serials)<=7000,'DRAW_LOG_BOUND')
        self.draw_timing.add('receipt_to_render_upper_bound',sample['upper_ms']/1000)
        with (self.root/'display_receipts.jsonl').open('a',encoding='utf-8') as f:
            f.write(__import__('json').dumps({**body,**sample,'server_receipt_monotonic_ns':now})+'\n')
        return {'status':'RECORDED_RENDER_RECEIPT','latency':sample,'summary':self.draw_timing.summary(),'REALTIME_STREAM_PASS':'NOT_RUN'}
    def start(self,body):
        with self.lock:
            require(self.thread is None,'CAMERA_SESSION_ALREADY_ATTEMPTED_RESTART_ENTRY')
            require(os.name=='nt','WINDOWS_CAPTURE_REQUIRED')
            self.adapter.connected();require(self.adapter.session.get('camera_enabled') is True,'START_ENTRY_REQUIRES_CAMERA_FLAG')
            require(set(body)=={'camera_id'} and type(body['camera_id']) is int and 0<=body['camera_id']<=15,'CAMERA_ID_SCHEMA')
            self.root=self.adapter.root/'camera';self.root.mkdir()
            data=self.adapter.registry.data
            binding={'model':data['model'],'source_kind':'real_windows_camera','spatial_policy':'standard_A_full_field_417_BoxEye15_kernel13_mean',
                'dt_s':.005,'node_map_sha256':data['pins']['nodes']['sha256'],'input_map_sha256':data['pins']['input_map']['sha256'],
                'decoder_contract_sha256':data['pins']['decoder_contract']['sha256'],'camera_dependencies':self.dependencies,
                'initialization':'ONE_SHARED_GRAY_ADAPTED_FULL_INITIAL_STATE_AT_SESSION_START'}
            self.control={'schema':'flyvis-live-camera-control/v1','session_id':self.adapter.session['session_id'],'run_id':uuid.uuid4().hex,
                'mode':'Full','source_kind':'real_windows_camera','spatial_policy':'full-field','camera_id':body['camera_id'],'max_duration_s':300,'max_steps':60000,
                'binding':binding,'central_global_ids':data['central_global_ids'],'created_utc':utc(),'execution_kind':'LIVE_CAMERA_GPU','PL_execution':False}
            self.control['spatial_map_sha256']=self.spatial.digest
            write(self.root/'control.json',self.control)
            self.touch()
            write(self.root/'capture_status.json',{'state':'WAITING_FOR_CONVERTER','frames_read':0,'error':None})
            self.thread=threading.Thread(target=self.capture,daemon=True);self.thread.start();return self.status()
    def capture(self):
        camera=None
        try:
            begin=time.monotonic()
            while not (self.root/'renderer_ready.json').exists():
                self.check_stop();require(time.monotonic()-begin<45,'OFFICIAL_RENDERER_START_TIMEOUT');self.stop_event.wait(.05)
            require(load(self.root/'renderer_ready.json')['run_id']==self.control['run_id'],'RENDERER_IDENTITY')
            import sys
            sys.path.insert(0,str(HERE.parent))
            from camera_pipeline.capture import open_camera,read_frame
            camera=open_camera(self.control['camera_id'],backend='dshow',width=640,height=480,fps=30)
            frames=[];origin=None;origin_unix=None;overwrites=0;lost=0
            raw=self.root/'raw';raw.mkdir()
            with (self.root/'source_events.jsonl').open('x',encoding='utf-8') as events:
                while True:
                    self.check_stop();packet=read_frame(camera);now_unix=time.time();bridge_begin=time.perf_counter()
                    if origin is None:origin=packet.received_monotonic_ns;origin_unix=now_unix
                    elapsed=(packet.received_monotonic_ns-origin)/1e9
                    require(elapsed<=300,'CAMERA_DURATION_LIMIT')
                    slot=packet.sequence%CAPACITY
                    buffer=io.BytesIO();np.save(buffer,packet.bgr,allow_pickle=False);blob=buffer.getvalue()
                    path=raw/f'{slot:02}.npy';self.atomic_bytes(path,blob)
                    ok,image=camera.cv2.imencode('.png',packet.bgr);require(ok,'SOURCE_PREVIEW_ENCODING_FAILED')
                    png=raw/f'{slot:02}.png';self.atomic_bytes(png,image.tobytes())
                    frame={'sequence':packet.sequence,'received_monotonic_ns':packet.received_monotonic_ns,'received_utc':packet.received_utc,
                        'received_unix_s':now_unix,'relative_s':elapsed,'path':relative_asset_path(path,self.root),'sha256':sha(path),
                        'png_path':relative_asset_path(png,self.root),'png_sha256':sha(png),'shape':list(packet.bgr.shape)}
                    frame['capture_read_s']=packet.read_duration_s
                    frame['capture_encode_write_hash_s']=time.perf_counter()-bridge_begin
                    if len(frames)==CAPACITY:
                        dropped=frames.pop(0);overwrites+=1
                        ack=load(self.root/'renderer_progress.json')['last_sequence'] if (self.root/'renderer_progress.json').exists() else -1
                        if dropped['sequence']>ack:lost+=1;events.write(__import__('json').dumps({'event':'DROPPED_BEFORE_RENDER','sequence':dropped['sequence']})+'\n')
                    frames.append(frame);events.write(__import__('json').dumps(frame)+'\n');events.flush()
                    value={**camera.status(),'state':'CAPTURING','run_id':self.control['run_id'],'origin_monotonic_ns':origin,'origin_unix_s':origin_unix,
                        'updated_unix_s':now_unix,'elapsed_s':elapsed,'capture_queue_length':len(frames),'source_ring_overwrites':overwrites,
                        'source_frames_dropped_before_render':lost,'sensor_drop_count':None,'error':None}
                    write(self.root/'source_ring.json',{'run_id':self.control['run_id'],'frames':frames,'status':value})
                    write(self.root/'capture_status.json',value)
                    require(lost==0,'SOURCE_QUEUE_OVERRUN_STOP_NO_FUTURE_SUBSTITUTION')
        except BaseException as exc:
            stopped=self.stop_event.is_set() or (self.root/'STOP_REQUEST.json').exists() or (self.adapter.root/'STOP_REQUEST.json').exists()
            write(self.root/'capture_status.json',{'state':'STOPPING' if stopped else 'FAILED','error':None if stopped else str(exc),'updated_utc':utc()})
            write(self.root/'STOP_REQUEST.json',{'reason':'CAPTURE_STOP' if stopped else 'CAPTURE_FAILED','error':str(exc),'utc':utc()})
        finally:
            if camera is not None:camera.close()
            write(self.root/'capture_closed.json',{'run_id':self.control['run_id'],'closed':True,'utc':utc()})
    @staticmethod
    def atomic_bytes(path,blob):
        path=Path(path);temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex);temp.write_bytes(blob);os.replace(temp,path)
    def check_stop(self):
        require(not self.stop_event.is_set() and not (self.root/'STOP_REQUEST.json').exists() and not (self.adapter.root/'STOP_REQUEST.json').exists(),'CAMERA_STOP_REQUESTED')
        self.adapter.connected()
        require(time.monotonic()-self.last_client_poll<5,'GUI_CONSUMER_DISCONNECTED')
    def touch(self):self.last_client_poll=time.monotonic()
    def stop(self):
        if self.control:
            self.stop_event.set();write(self.root/'STOP_REQUEST.json',{'reason':'USER_CAMERA_STOP','utc':utc()})
            write(self.adapter.root/'GPU_STOP_REQUEST.json',{'reason':'USER_CAMERA_STOP_RELEASE_WORKER','utc':utc()})
            if self.thread:self.thread.join(timeout=2)
        return self.status()
    def status(self):
        if not self.control:return {'status':'NOT_STARTED','execution_kind':'LIVE_CAMERA_GPU','run_id':None,'result':None,'PL_execution':False}
        capture=load(self.root/'capture_status.json');worker=load(self.root/'compute_status.json') if (self.root/'compute_status.json').exists() else {'state':'WAITING_COMPUTE'}
        failed=capture['state'] in ('FAILED','STOPPING') or worker['state'] in ('FAILED','STOPPED') or self.stop_event.is_set()
        if not failed:
            try:self.adapter.connected()
            except (ValueError,OSError,KeyError) as exc:failed=True;worker={'state':'DISCONNECTED','error':str(exc)};write(self.root/'STOP_REQUEST.json',{'reason':'SERVICE_DISCONNECTED'})
        return {'status':'NOT_AVAILABLE' if failed else worker['state'],'run_id':self.control['run_id'],'session_id':self.control['session_id'],
            'capture':capture,'compute':worker,'binding':self.control['binding'],'result_valid':not failed,'execution_kind':'LIVE_CAMERA_GPU','PL_execution':False,
            'FPGA_status':'NOT_CONNECTED','REALTIME_STREAM_PASS':'NOT_RUN','p50_ms':None,'p95_ms':None,'p99_ms':None}
    def latest(self):
        status=self.status();require(status['result_valid'],'CAMERA_RESULT_REVOKED')
        pointer=load(self.root/'display_latest.json');path=self.root/'display'/f"{pointer['serial']%DISPLAY_CAPACITY:02}.json";packet=load(path)
        require(packet['serial']==pointer['serial'],'DISPLAY_QUEUE_OVERWRITE_RETRY');admitted_packet(packet,self.control)
        self.spatial.validate(packet['spatial'],packet['run_id'],packet['step_id'],packet['activity_time_s'],'Full')
        return {'status':status,'packet':packet,'server_unix_s':time.time()}
    def frame(self,sequence,run_id):
        require(self.control is not None and run_id==self.control['run_id'],'SELECTED_FRAME_RUN_IDENTITY')
        self.status();require(self.status()['result_valid'],'CAMERA_RESULT_REVOKED')
        pin=load(self.root/'selected_frames'/f'{sequence:08}.json');path=self.root/pin['png_path']
        require(sha(path)==pin['png_sha256'],'SELECTED_SOURCE_IMAGE_CHANGED');return path.read_bytes()
