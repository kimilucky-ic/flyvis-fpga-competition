"""Pure-PL backend adapter in the original GUI; reuses camera/BoxEye/mailboxes.

No devices open on import/construction. A human-run board Notebook calls ready,
then the current input/committed-record endpoints. No Full GPU producer exists.
"""
import base64
import hashlib
import io
import json
from pathlib import Path
import secrets
import struct
import threading
import time
import uuid
import zipfile
import numpy as np
from live_protocol import HERE,load,require
from line11_ddr_bridge import verify_release,record_codec,digest,check_receipt,MANIFEST_SHA,CORE_CYCLES
from line11_ddr_start import DdrFirstStep,DdrGuiSession,check_operator,READINESS,READINESS_SHA,sha
from line11_stream import FullPLStream
from line11_ddr_plan import STARTUP_FILES
from line11_live_cpu import INITIAL

CAPACITY=485
STEP_RATE_LIMIT_HZ=8
LIVE_FILES=STARTUP_FILES+('line11_live_camera_board.py',)


class CameraFeed:
    """Original Windows camera + prepared BoxEye + original two latest mailboxes."""
    def init__(self,run,device=0):
        from joint_camera_protocol import LatestCameraInput
        self.inputs=LatestCameraInput(run);self.run=run;self.device=device
        self.stop=threading.Event();self.ready=threading.Event();self.error=None;self.deadline_ns=None;self.stats={}

    def start(self):
        self.thread=threading.Thread(target=self._run,name='line2-original-camera-boxeye',daemon=True);self.thread.start()

    def _run(self):
        try:
            import sys
            sys.path.insert(0,str(HERE.parent))
            from camera_pipeline.capture import CameraSession
            from prepared_camera_input import PreparedCameraInput
            from joint_camera_protocol import conversion_receipt
            from PIL import Image
            converter=PreparedCameraInput()
            converter.render(np.full((480,640,3),127,dtype=np.uint8))  # prepare before acquiring the first REAL frame
            with CameraSession(self.device,backend='dshow',width=640,height=480,fps=30) as camera:
                first=None
                while not self.stop.is_set() and (self.deadline_ns is None or time.perf_counter_ns()<self.deadline_ns):
                    pkt=camera.read_frame();first=pkt.received_monotonic_ns if first is None else first
                    out=io.BytesIO();Image.fromarray(pkt.bgr[:,:,::-1]).save(out,format='PNG');png=out.getvalue()
                    frame=dict(png=base64.b64encode(png).decode(),source=dict(run_id=self.run,source_kind='real_windows_camera',
                        sequence=pkt.sequence,received_monotonic_ns=pkt.received_monotonic_ns,received_utc=pkt.received_utc,
                        relative_s=(pkt.received_monotonic_ns-first)/1e9,timestamp_kind='Windows_receipt_not_sensor',png_sha256=digest(png)))
                    self.inputs.receive(frame);raw=self.inputs.take_raw()
                    values,coordinates,transform=converter.render(pkt.bgr)
                    raw['values']=values[0].tolist();raw['source']['hex_values_sha256']=digest(values[0].tobytes())
                    raw['conversion']=dict(backend='ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU',transform=transform,
                        coordinates_sha256=digest(np.asarray(coordinates).tobytes()))
                    self.inputs.accept_conversion(conversion_receipt(raw));self.stats=camera.status();self.ready.set()
        except Exception as error:self.error=type(error).__name__+': '+str(error);self.ready.set()

    def close(self):
        self.stop.set()
        if hasattr(self,'thread') and self.thread is not threading.current_thread():
            self.thread.join(3)
            if self.thread.is_alive():self.error=self.error or 'LIVE_CAMERA_CLOSE_NOT_ACKNOWLEDGED'


class LiveFirst(DdrFirstStep):
    def init__(self,nonce,output,software_test,scientific=None):
        super().init__(nonce,output,software_test,total_steps=3)
        self.numeric_verified=False
        self.total_steps=CAPACITY
        self.plan_id='CURRENT_CAMERA_FULL_PL_60S'
        self.plan=dict(condition_id='本次真实摄像头',input_kind='real_windows_camera',input_time_offset_s=0.,
                       temporal_policy='LATEST_AVAILABLE_HOLD_AT_EACH_FULL_PL_STEP; MODEL_DT_5MS; WALL_WINDOW_60S',
                       initial_state=dict(kind='ORIGINAL_PER_TYPE_BIAS',sha256=INITIAL))

        if scientific:
            self.plan.update(condition_id=scientific.condition,input_kind='controlled_animation',
                temporal_policy='FROZEN_STEP_K_TO_INPUT_K_NO_SKIP',scientific_input=scientific.binding('FULL_FPGA'))
            self.plan_id='SCIENTIFIC28_'+scientific.condition

    def frame(self):
        p=super().frame();p['model']['initial_state_sha256']=INITIAL
        p['plan_metadata'].update(input_kind=self.plan['input_kind'],scientific_input=self.plan.get('scientific_input'),camera_live=True,window_duration_s=None if self.plan.get('scientific_input') else 60,steps=CAPACITY,
                                 step_rate_limit_hz=0 if self.plan.get('scientific_input') else STEP_RATE_LIMIT_HZ,temporal_policy=self.plan['temporal_policy'])
        return p

    def status(self):
        if not self.numeric_verified:
            return dict(configured=True,status='WAITING_FIRST_STEP',board_connection='NOT_CONNECTED',
                        evidence_level='FIRST_COMPLETE_STATE_NUMERICAL_AUDIT_PENDING')
        return super().status()


class CameraDdrSession(DdrGuiSession):
    camera_live=True
    def init__(self,output,device=0,*,software_test=False,capture=None,consumer=None,clock=time.perf_counter_ns,scientific_condition=None,require_gui_start=False):
        self.require_gui_start=require_gui_start;self.gui_start=threading.Event();self.prepared_for_compute=False
        self.preparation_id=uuid.uuid4().hex;self.preparation_token=secrets.token_hex(32)
        self.output=Path(output)/self.preparation_id;self.total_steps=CAPACITY;self.receipt_limit=CAPACITY
        self.admission_lock=threading.Lock();self.decoded_frame=None;self.flow_revision=0
        self.first_audited=threading.Event();self.first_verified=False;self.claimed=False;self.started_ns=None
        self.issued={};self.window_stop_reason=None;self.requested_stop=False;self.last_state=INITIAL
        self.window_elapsed_s=None;self.last_issue_ns=None;self.normal_end_ack=False;self.closeout_proof=None
        self.scientific_condition=scientific_condition
        if scientific_condition:
            from frozen28_input import Frozen28Input
            require(capture is None,'SCIENTIFIC_NO_CAMERA_OVERRIDE')
            self.capture=Frozen28Input(self.preparation_id,scientific_condition)
        else:self.capture=capture or CameraFeed(self.preparation_id,device)
        self.flow_consumer=consumer;self.software_test=software_test
        FullPLStream.init__(self,LiveFirst(self.preparation_id,self.output,software_test,self.capture if scientific_condition else None),True,CAPACITY-1,
                              protocol_test=software_test,clock=clock,idle_timeout_s=120)

    def package(self,callback_url):
        self.callback_url=callback_url;self.output.mkdir(parents=True,exist_ok=False)
        root,files=verify_release()
        config=dict(schema='flyvis-line2-ddr-live-camera/v1',preparation_id=self.preparation_id,url=callback_url,
                    token=self.preparation_token,duration_s=60,total_steps=CAPACITY,step_rate_limit_hz=STEP_RATE_LIMIT_HZ,release_manifest_sha256=MANIFEST_SHA,
                    board_operations_authorized=False,startup_sha256={n:digest((HERE/n).read_bytes()) for n in LIVE_FILES})
        config['waits_for_gui_start']=self.require_gui_start
        if self.scientific_condition:
            config.update(scientific_input=self.capture.binding('FULL_FPGA'),source_kind='controlled_animation',duration_s=None,step_rate_limit_hz=0)
        self.link_path=self.output/'LINE11_DDR_PREPARE.zip'
        with zipfile.ZipFile(self.link_path,'x',zipfile.ZIP_DEFLATED) as z:
            for name in files:z.write(root/name,name)
            z.write(root/'release_manifest.json','release_manifest.json')
            for name in LIVE_FILES:z.write(HERE/name,name)
            z.writestr('PREPARATION.json',json.dumps(config,indent=2))
        return self.link_path

    def start_cpu_flow(self):
        from line11_live_cpu import LiveCPUConsumer
        if self.flow_consumer is None:self.flow_consumer=LiveCPUConsumer(self.output/'official_flow',self._flow_ready)
        self.flow_consumer.start()

    def start_compute(self,body):
        require(self.require_gui_start and self.prepared_for_compute and not self.gui_start.is_set()
            and not self.requested_stop and not self.error and self.state=='WAITING_FIRST_STEP'
            and body==dict(preparation_id=self.preparation_id),'FULL_PL_GUI_START_NOT_READY_OR_CONSUMED')
        self.gui_start.set()
        return dict(status='START_REQUESTED',preparation_id=self.preparation_id)

    def ready_board(self,body):
        require(body['preparation_id']==self.preparation_id and self.state=='WAITING_FIRST_STEP'
                and not self.claimed,'LIVE_ALREADY_CLAIMED_OR_CLOSED')
        self.claimed=True
        return dict(status='CAMERA_PREPARATION_ACCEPTED_NOT_NEURAL_RESULT')

    def begin_input(self,body):
        require(self.claimed and self.state=='WAITING_FIRST_STEP','LIVE_FIRST_INPUT_STATE')
        op=body['operator'];context=body['context']
        check_operator(op,self.preparation_id,self.software_test)
        require(op['startup_sha256']=={n:digest((HERE/n).read_bytes()) for n in LIVE_FILES},'LIVE_STARTUP_IDENTITY')
        require(body['preparation_id']==context['run_id']==self.preparation_id and context['slots']==CAPACITY
                and context['allocated_bytes']==CAPACITY*188416 and context['physical_base']%4096==0
                and context['physical_base']>=0x100000 and context['physical_base']+context['allocated_bytes']<=0x40000000
                and context['cookie']==int(self.preparation_id[:8],16),'LIVE_ALLOCATION_IDENTITY')
        self.operator=op;self.context=context
        require(self.flow_consumer is not None and self.flow_consumer.ready.wait(120)
                and not self.flow_consumer.error,'LIVE_CPU_AUDITOR_NOT_READY')
        if self.require_gui_start:
            self.prepared_for_compute=True
            require(self.gui_start.wait(120) and not self.requested_stop and not self.error,'GUI_START_TIMEOUT_OR_CANCELLED_NO_NEURAL_STEP')
        self.capture.start();require(self.capture.ready.wait(30) and not self.capture.error,'LIVE_CAMERA_NOT_READY')
        self.started_ns=self.clock();self.capture.deadline_ns=self.started_ns+60_000_000_000
        return self.issue(0,INITIAL)

    def issue(self,k,previous):
        require(self.error is None and not self.flow_consumer.error and not self.capture.error,'LIVE_BACKEND_ERROR')
        require(previous==self.last_state and k==len(self.issued),'LIVE_CURRENT_INPUT_ORDER')
        # Explicit experiment pacing preserves the existing485-slot audit budget.
        # This does not change the5ms neural dynamics or assert a hardware speed.
        due=self.started_ns if self.scientific_condition or self.last_issue_ns is None else self.last_issue_ns+int(1e9/STEP_RATE_LIMIT_HZ)
        while not self.requested_stop and self.clock()<due and self.clock()<self.started_ns+60_000_000_000:
            require(not self.capture.error and not self.flow_consumer.error,'LIVE_BACKEND_ERROR_DURING_PACING')
            time.sleep(max(0,min(.02,(due-self.clock())/1e9)))
        if self.scientific_condition:
            wait_begin=time.monotonic()
            q=getattr(self.flow_consumer,'queue',None)
            while q is not None and q.qsize()>=16 and not self.requested_stop:
                require(not self.flow_consumer.error and time.monotonic()-wait_begin<120,'SCIENTIFIC_AUDIT_BACKPRESSURE_TIMEOUT')
                time.sleep(.01)
        elapsed=(self.clock()-self.started_ns)/1e9
        if self.requested_stop or (not self.scientific_condition and elapsed>=60) or k>=CAPACITY:
            self.window_elapsed_s=elapsed
            self.window_stop_reason='USER_STOP' if self.requested_stop else 'SCIENTIFIC_485_STEPS_COMPLETE' if self.scientific_condition else 'WALL_60S' if elapsed>=60 else 'CAPACITY_EXHAUSTED'
            self.capture.close()
            require(not self.capture.error,'LIVE_CAMERA_CLOSE_FAILED')
            return dict(stop=True,reason=self.window_stop_reason,elapsed_s=elapsed,completed_steps=k,model_time_s=k*.005)
        frame=self.capture.for_step(k) if self.scientific_condition else self.capture.inputs.freeze_for_step();require(frame is not None,'LIVE_NO_CONVERTED_CURRENT_FRAME')
        inp=np.asarray(frame['values'],dtype='<f4').tobytes()
        require(len(inp)==2884 and digest(inp)==frame['source']['hex_values_sha256'],'LIVE_CURRENT_BOXEYE_IDENTITY')
        self.issued[k]=dict(frame=frame,input=inp,state_sha=None)
        self.last_issue_ns=self.clock()
        return dict(stop=False,step=k,input_b64=base64.b64encode(inp).decode(),input_sha256=digest(inp),previous_state_sha256=previous)

    def receive_camera(self,blob):
        with self.admission_lock:return self._receive_camera(blob)

    def _receive_camera(self,blob):
        require(4<len(blob)<200000,'LIVE_RAW_RECORD_BOUND')
        n=struct.unpack_from('<I',blob)[0];require(0<n<=8192 and len(blob)==4+n+188416,'LIVE_RAW_PACKET_LENGTH')
        m=json.loads(blob[4:4+n]);raw=blob[4+n:];k=m['frame_id']
        require(type(k) is int and k in self.issued and k==(self.count+1 if self.first_verified else 0)
                and m['run_id']==self.preparation_id and m['previous_state_sha256']==self.last_state,'LIVE_RECORD_RUN_STEP_OLD_STATE')
        r=self.seed.codec.decode_record(raw,k)
        require(r.input_bits==self.issued[k]['input'] and r.cycles==m['compute_cycles']==CORE_CYCLES,'LIVE_RECORD_CURRENT_INPUT_OR_CYCLES')
        row=m['source_audit'];evidence='CPU_MOCK_ONLY' if self.protocol_test else 'OPERATOR_PHYSICAL_READS_UNATTESTED'
        require(row['evidence']==evidence and row['record_sha256']==digest(raw),'LIVE_RAW_SOURCE_IDENTITY')
        check_receipt(row,k,m['run_id'],self.context['cookie'],self.audit_chain if self.first_verified else '0'*64,r.input_sha256,r.state_sha256)
        self.issued[k]['state_sha']=r.state_sha256
        self.issued[k]['raw_record']=raw
        if k==0:
            require(sha(READINESS)==READINESS_SHA,'LIVE_READINESS_CHANGED')
            from spatial_state import SpatialRegistry
            self.seed.contract=load(READINESS);self.seed.spatial=SpatialRegistry()
            require(self.seed.spatial.digest==self.seed.contract['consumer']['spatial_mapping_sha256'],'LIVE_SPATIAL_MAP_CHANGED')
            first=io.BytesIO()
            with zipfile.ZipFile(first,'w',zipfile.ZIP_DEFLATED) as z:
                for name,data in {'record_000000.bin':raw,'OPERATOR.json':json.dumps(self.operator).encode(),
                    'RUN_CONTEXT.json':json.dumps(self.context).encode(),'receipt_000000.json':json.dumps(row).encode(),
                    'TIMING.json':json.dumps({'input_and_STEP_ns':int(m['elapsed_seconds']*1e9)}).encode()}.items():z.writestr(name,data)
            data=first.getvalue();self.seed.archive_sha=digest(data);self.seed.path=self.output/'FIRST_STEP.zip'
            self.seed.path.write_bytes(data);self.seed.value=dict(operator=self.operator,context=self.context,receipt=row,
                timing={'input_and_STEP_ns':int(m['elapsed_seconds']*1e9)},record=r)
            self.seed.full=np.frombuffer(r.state_bits,dtype='<f4');self.seed.input=np.frombuffer(r.input_bits,dtype='<f4')
            self.prepare()
            m.update(schema='flyvis-line11-state-stream/v1',session_id=self.session_id,boot_id=self.operator['boot_id'],
                     input_sha256=r.input_sha256,state_sha256=r.state_sha256,completed_steps=1,clock_hz=100000000,faults=0)
            self.received_ns=self.clock();self.latest_frame=(m,r.input_bits,r.state_bits,self.received_ns,None);self.last_sha=r.state_sha256
            self.receipts[0]=(r.state_sha256,self.clock());self.state='RECEIVING'
            self.flow_consumer.submit(self.latest_frame)
            require(self.first_audited.wait(120) and not self.flow_consumer.error,'LIVE_FIRST_COMPLETE_STATE_AUDIT_FAILED')
            self.first_verified=True;self.seed.numeric_verified=True
        else:
            m.update(schema='flyvis-line11-state-stream/v1',session_id=self.session_id,boot_id=self.operator['boot_id'],
                     input_sha256=r.input_sha256,state_sha256=r.state_sha256,completed_steps=k+1,clock_hz=100000000,
                     faults=0,transport_profile=self.profile)
            header=json.dumps(m,separators=(',',':')).encode()
            FullPLStream.accept(self,struct.pack('<I',len(header))+header+r.input_bits+r.state_bits,'Bearer '+self.token)
            self.flow_consumer.submit(self.latest_frame)
        self.last_state=r.state_sha256
        return dict(accepted_step=k,full_state_sha256=r.state_sha256,next_input=self.issue(k+1,r.state_sha256))

    def _flow_ready(self,snapshot,flow):
        k=snapshot[0]['frame_id'];row=self.issued[k];frame=row['frame'];png=base64.b64decode(frame['png'],validate=True)
        require(digest(png)==frame['source']['png_sha256'],'LIVE_CAMERA_PIXELS_CHANGED')
        folder=self.output/'source_frames';folder.mkdir(exist_ok=True);path=folder/('%06d.png'%k)
        from os import fsync
        with path.open('xb') as f:f.write(png);f.flush();fsync(f.fileno())
        target=self.output/'raw_records';target.mkdir(exist_ok=True)
        with (target/('%06d.bin'%k)).open('xb') as f:
            f.write(row['raw_record']);f.flush();fsync(f.fileno())
        row.pop('raw_record')
        row['png_path']=path;row['source']=dict(frame['source']);row['conversion']=frame['conversion'];row.pop('frame')
        source_record=dict(run_id=self.preparation_id,session_id=self.session_id,step=k,
            input_sha256=digest(row['input']),full_state_sha256=row['state_sha'],source=row['source'],
            conversion=row['conversion'],model_input_time_s=k*.005,model_activity_time_s=(k+1)*.005,
            temporal_policy=self.seed.plan['temporal_policy'],source_clock='frozen_model_time_not_capture' if self.scientific_condition else 'Windows_receipt_not_sensor')
        with path.with_suffix('.json').open('x',encoding='utf-8') as f:
            json.dump(source_record,f,ensure_ascii=False);f.flush();fsync(f.fileno())
        DdrGuiSession._flow_ready(self,snapshot,flow)
        if k==0:self.first_audited.set()

    def replay(self,step):
        """Read only this completed run's actual received states, never the plan."""
        with self.lock:
            s=self.status()
            require(self.scientific_condition and self.flow_consumer is not None and s['status']=='FINISHED' and s.get('display_complete')
                    and type(step) is int and 0<=step<485,'DDR_REPLAY_NOT_COMPLETE')
            base=self.flow_consumer.output/('%06d'%step)
        row=json.loads(base.with_suffix('.json').read_text(encoding='utf-8'))
        m=row['stream_metadata'];bits=base.with_suffix('.state.bin').read_bytes()
        inp=base.with_suffix('.input.bin').read_bytes();flow=base.with_suffix('.flow.bin').read_bytes()
        require(row['run_id']==m['run_id']==self.anchor['run_id'] and row['session_id']==m['session_id']==self.session_id
                and row['frame_id']==m['frame_id']==step,'DDR_REPLAY_RUN_STEP')
        require(digest(bits)==row['full_state_sha256']==m['state_sha256']
                and digest(inp)==row['input_sha256']==m['input_sha256']
                and digest(flow)==row['flow_sha256'] and len(flow)==5768,'DDR_REPLAY_FILE_IDENTITY')
        accepted=self.issued[step]
        require(row['numerical_audit']=='FULL_STATE_BIT_EXACT'
                and digest(bits)==accepted['state_sha'] and inp==accepted['input'],
                'DDR_REPLAY_CURRENT_ACCEPTED_STATE')
        values=np.frombuffer(flow,dtype='<f4').reshape(2,721)
        require(np.isfinite(values).all(),'DDR_REPLAY_FINITE')
        require(row['decoder']=='DecoderGAVP' and row['recursive_eval'] is True
                and row['decoder_source_sha256']==self.decoder_pin['sha256']
                and row['checkpoint_sha256']==self.anchor['model']['checkpoint_sha256'],'DDR_REPLAY_DECODER')
        packet=self.frame_reply((m,inp,bits,row['received_pc_ns'],dict(values=values.tolist(),sha256=digest(flow),binding=row)),s,step)['frame']
        packet['display_kind']='CPU_PROTOCOL_TEST_ONLY' if self.protocol_test else 'OFFLINE_REPLAY_FULL_PL_TRAJECTORY'
        packet['offline_replay']=True
        return dict(status=s,frame=packet)

    def latest(self,after=-1):
        with self.lock:
            status=self.status()
            if not status['result_valid'] or self.revision==after:return dict(status=status,frame=None)
            return self.frame_reply(self.decoded_frame,status,self.revision)

    def frame_reply(self,snapshot,status,revision):
        result=FullPLStream.frame_reply(self,snapshot,status,revision);p=result['frame'];row=self.issued[p['step_id']]
        p['source'].update(row['source'],kind=self.seed.plan['input_kind'],source_frame=row['source']['sequence'],
                           capture_utc=row['source']['received_utc'],pixel_png_sha256=row['source']['png_sha256'])
        if self.scientific_condition:
            p['source_kind']='controlled_animation';p['condition_id']=self.scientific_condition
            p['scientific_input']=self.capture.binding('FULL_FPGA')
        p['capture_elapsed_s']=row['source']['relative_s'];p['wall_elapsed_s']=self.wall_elapsed()
        return result

    def source_frame(self,step,run,state_sha):
        require(run==self.preparation_id and step in self.issued and self.issued[step]['state_sha']==state_sha,'LIVE_SOURCE_RUN_STATE')
        row=self.issued[step];data=row['png_path'].read_bytes();require(digest(data)==row['source']['png_sha256'],'LIVE_SOURCE_PIXELS_CHANGED')
        return data

    def status(self):
        if not self.first_verified:
            return dict(configured=True,status=self.state,first_step_accepted=False,result_valid=False,error=self.error,
                        preparation_id=self.preparation_id,camera_live=True,start_requested=self.gui_start.is_set(),ready_to_start=self.require_gui_start and self.prepared_for_compute and not self.gui_start.is_set() and not self.error,source_kind='controlled_animation' if self.scientific_condition else 'real_windows_camera',condition_id=self.scientific_condition,board_connection='NOT_CONNECTED',received_steps=0)
        s=FullPLStream.status(self);s.update(received_steps=self.count+1,start_requested=self.gui_start.is_set(),camera_live=True,preparation_id=self.preparation_id,requested_wall_duration_s=60,model_dt_s=.005,
            step_rate_limit_hz=STEP_RATE_LIMIT_HZ,step_capacity=CAPACITY,
            elapsed_wall_s=self.wall_elapsed(),model_time_s=(self.count+1)*.005,
            capture=self.capture.inputs.status(),capture_device_stats=getattr(self.capture,'stats',{}),
            capture_error=self.capture.error,stop_reason=self.window_stop_reason,
            official_flow=self.flow_consumer.status(),display_complete=self.state=='FINISHED' and self.flow_consumer.state=='COMPLETE',
            storage_policy='OWNED_BOARD_DDR_AND_PC_ASYNC_FULL_STATE_INPUT_FLOW_SOURCE_ARCHIVE',
            evidence_level='CPU_PROTOCOL_ONLY' if self.protocol_test else 'LIVE_CAMERA_FULL_PL_FIRST_STATE_BIT_VERIFIED_SUBSEQUENT_ASYNC_AUDIT',
            result_valid=self.decoded_frame is not None and self.state in ('RECEIVING','FINISHED') and not self.flow_consumer.error)
        if self.flow_consumer.error:self.abort(self.flow_consumer.error);s.update(status='FAILED',error=self.error,result_valid=False)
        if self.scientific_condition:
            s.update(source_kind='controlled_animation',condition_id=self.scientific_condition,
                scientific_input=self.capture.binding('FULL_FPGA'),requested_wall_duration_s=None,step_rate_limit_hz=0,
                evidence_level='CPU_PROTOCOL_ONLY' if self.protocol_test else 'PHYSICAL_FULL_PL_PENDING_FULL_STATE_AUDIT')
        if self.scientific_condition:s['scientific_condition_complete']=s['display_complete'] and s['received_steps']==485
        s['replay_available']=bool(self.scientific_condition and s['display_complete'] and s['result_valid'])
        s['normal_end_ack']=self.normal_end_ack
        s['numerical_audit']='FULL_STATE_BIT_EXACT_COMPLETE' if self.flow_consumer.state=='COMPLETE' else 'PENDING'
        return s

    def end_camera(self,body):
        require(self.first_verified and body['preparation_id']==self.preparation_id and body['completed_steps']==self.count+1
                and body['last_state_sha256']==self.last_state and body['receipt_chain']==self.audit_chain
                and body['idle'] is True and body['faults']==0 and body['stop_reason']==self.window_stop_reason
                and not self.capture.error and not self.flow_consumer.error,'LIVE_WINDOW_END_BINDING')
        self.capture.close();self.state='FINISHED';self.flow_consumer.finish_input();self.revision+=1
        result=dict(status='FINISHED_PRODUCER_REPORTED',completed_steps=self.count+1,stop_reason=self.window_stop_reason,
                    actual_60s_complete=self.window_stop_reason=='WALL_60S',whole_run_acceptance='PENDING_NUMERICAL_AUDIT')
        (self.output/'WINDOW_FINISH.json').write_text(json.dumps(dict(result,body=body,elapsed_wall_s=self.wall_elapsed(),
            model_time_s=(self.count+1)*.005,step_rate_limit_hz=0 if self.scientific_condition else STEP_RATE_LIMIT_HZ,
            scientific_input=self.seed.plan.get('scientific_input'),
            capture=self.capture.inputs.status(),capture_device_stats=getattr(self.capture,'stats',{})))+'\n',encoding='utf-8')
        return result

    def closeout(self,body):
        """Authenticated board return handshake AFTER all async audit/durable writes."""
        require(isinstance(body,dict) and set(body)=={'op','preparation_id','completed_steps','last_state_sha256','receipt_chain'}
                and body['preparation_id']==self.preparation_id and body['completed_steps']==self.count+1
                and body['last_state_sha256']==self.last_state and body['receipt_chain']==self.audit_chain,
                'NORMAL_CLOSEOUT_IDENTITY')
        require(self.state=='FINISHED' and self.error is None and self.capture.error is None
                and self.flow_consumer.error is None and self.window_stop_reason in
                ('WALL_60S','SCIENTIFIC_485_STEPS_COMPLETE'),'NORMAL_CLOSEOUT_REQUIRES_SUCCESS')
        require(body['op'] in ('audit','ack'),'NORMAL_CLOSEOUT_OPERATION')
        if self.flow_consumer.state!='COMPLETE':
            require(body['op']=='audit','NORMAL_CLOSEOUT_ACK_BEFORE_AUDIT')
            return dict(status='AUDIT_PENDING',preparation_id=self.preparation_id)
        require(self.flow_consumer.completed==self.flow_consumer.accepted==body['completed_steps']
                and self.flow_consumer.last_binding['full_state_sha256']==self.last_state,'NORMAL_CLOSEOUT_AUDIT_COUNT')
        from os import fsync
        if self.closeout_proof is None:
            proof=dict(status='NORMAL_WINDOW_AUDITED',preparation_id=self.preparation_id,
                completed_steps=body['completed_steps'],last_state_sha256=self.last_state,receipt_chain=self.audit_chain,
                session_id=self.session_id,stop_reason=self.window_stop_reason)
            with (self.output/'NORMAL_CLOSEOUT.json').open('x',encoding='utf-8') as f:
                json.dump(proof,f);f.flush();fsync(f.fileno())
            self.closeout_proof=proof
        if body['op']=='ack' and not self.normal_end_ack:
            with (self.output/'BOARD_RETURN_ACK.json').open('x',encoding='utf-8') as f:
                json.dump(body,f);f.flush();fsync(f.fileno())
            self.normal_end_ack=True
        return dict(self.closeout_proof,status='NORMAL_RETURN_ACKED' if self.normal_end_ack else 'NORMAL_WINDOW_AUDITED')

    def close(self):
        self.requested_stop=True;self.gui_start.set()
        self.capture.close();DdrGuiSession.close(self)

    def paint(self,receipt):
        result=FullPLStream.paint(self,receipt)
        folder=self.output/'browser_receipts';folder.mkdir(exist_ok=True)
        # Separate browser request, never the board's STEP/record return path.
        with (folder/('%06d_%d_%s.json'%(receipt['frame_id'],self.drawn,uuid.uuid4().hex))).open('x',encoding='utf-8') as f:
            json.dump(receipt,f)
        return result

    def wall_elapsed(self):
        return self.window_elapsed_s if self.window_elapsed_s is not None else (self.clock()-self.started_ns)/1e9

    def abort(self,message):
        self.capture.close();FullPLStream.abort(self,message)
        try:
            with (self.output/'FAILED.json').open('x',encoding='utf-8') as f:
                json.dump(dict(status='FAILED_KEEP_BOARD_DDR_AND_KERNEL',error=str(message),
                    first_verified=self.first_verified,received_after_first=self.count),f)
        except OSError:pass
