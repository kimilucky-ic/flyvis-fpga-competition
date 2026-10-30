"""Original-GUI DDR admission and package builder; no hardware execution.

Only a new human-operated, complete first record opens the existing ingress.
No saved old-board PASS, CPU fixture or directory discovery can open this gate.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import secrets
import threading
import uuid
import zipfile

import numpy as np
from line11_ddr_bridge import (PROFILE, BIT_SHA, HWH_SHA, CORE_CYCLES,
    INITIAL_BOUNDARY, MANIFEST_SHA, verify_release, record_codec, check_receipt, digest)
from line11_result import FullPLResult, READINESS, READINESS_SHA
from line11_stream import FullPLStream
from live_protocol import HERE, load, require, sha
from line11_ddr_plan import load_plan, STARTUP_FILES, PLAN32_SHA, PLAN485_SHA,plan_directory,plan_metadata

FIRST_FILES={'record_000000.bin','receipt_000000.json','RUN_CONTEXT.json','OPERATOR.json','TIMING.json'}


def check_operator(p, nonce, software_test=False):
    require(p['schema']=='flyvis-line2-ddr-operator/v1' and p['preparation_id']==nonce,'DDR_PREPARATION_BINDING')
    require(p['evidence']==('CPU_MOCK_ONLY' if software_test else 'HUMAN_EXECUTED_PHYSICAL_READS'),'DDR_OPERATOR_EVIDENCE')
    require(p['bit_sha256']==BIT_SHA and p['hwh_sha256']==HWH_SHA and p['release_manifest_sha256']==MANIFEST_SHA,'DDR_OPERATOR_IMAGE')
    require(re.fullmatch(r'[0-9a-f-]{36}',p['boot_id']) and p['exclusive_board_window'] is True,'DDR_BOOT_OR_OWNERSHIP')
    require(p['pynq_version'].startswith('2.7.') and p['machine']=='armv7l','DDR_RUNTIME_PROFILE')
    c=p['clock']
    require(c['clock_control']==0x200500 and c['io_pll_control']==0x1e000 and c['pll_status']&4
            and abs(c['reference_mhz']-33.333333)<.000001,'DDR_LIVE_CLOCK')
    require(p['hp0_read_control']&1==0 and p['hp0_write_control']&1==0,'DDR_HP0_NOT_64_BIT')
    require(p['initial_state_readback']==INITIAL_BOUNDARY,'DDR_INITIAL_CAPABILITY')
    require(p['cache_policy']=='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH'
            and len(bytes.fromhex(p['barrier_library_sha256']))==32,'DDR_CACHE_BINDING')


class DdrFirstStep(FullPLResult):
    def init__(self, nonce, output, software_test=False, total_steps=3,plan_root=None,plan_sha=None):
        super().init__(None)
        self.nonce,self.output,self.software_test=nonce,Path(output),software_test
        self.root,self.files=verify_release()
        self.codec=record_codec(self.root,self.files)
        self.total_steps=total_steps
        self.plan_root=Path(plan_root) if plan_root else plan_directory(HERE,self.root,total_steps)
        self.plan_sha=plan_sha
        self.plan_input,self.plan_expected,self.plan_id=load_plan(self.plan_root,total_steps,plan_sha)
        self.plan=plan_metadata(self.plan_root,total_steps)

    def _load(self):
        require(self.value is not None,'DDR_WAITING_FIRST_STEP')
        return self.value

    def admit(self, blob):
        with self.lock:
            require(self.value is None,'DDR_FIRST_STEP_ALREADY_CONSUMED')
            require(len(blob)<=500000,'DDR_FIRST_PACKET_BOUND')
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                rows=z.infolist()
                require(len(rows)==5 and {x.filename for x in rows}==FIRST_FILES
                        and sum(x.file_size for x in rows)<300000
                        and all(not x.flag_bits&1 for x in rows),'DDR_FIRST_ARCHIVE_FILES')
                files={x.filename:z.read(x) for x in rows}
            op=json.loads(files['OPERATOR.json']);check_operator(op,self.nonce,self.software_test)
            require(op['startup_sha256']=={n:digest((HERE/n).read_bytes()) for n in STARTUP_FILES},'DDR_STARTUP_SOURCE_IDENTITY')
            context=json.loads(files['RUN_CONTEXT.json']);receipt=json.loads(files['receipt_000000.json'])
            timing=json.loads(files['TIMING.json'])
            record=self.codec.decode_record(files['record_000000.bin'],0)
            require(record.cycles==CORE_CYCLES,'DDR_FIRST_CYCLES')
            require(record.input_bits==self.plan_input[:2884]
                    and record.state_bits==self.plan_expected[:182676],'DDR_FIRST_ALL_WORD_COMPARISON')
            run=context['run_id'];require(re.fullmatch(r'[0-9a-f]{32}',run),'DDR_FIRST_RUN_ID')
            require(context['evidence']==receipt['evidence']==('CPU_MOCK_ONLY' if self.software_test else 'OPERATOR_PHYSICAL_READS_UNATTESTED')
                    and context['board_result'] is False and context['slots']==self.total_steps,'DDR_FIRST_SCOPE')
            base=context['physical_base'];size=context['allocated_bytes']
            require(type(base) is int and base%4096==0 and base>=0x100000
                    and size==self.total_steps*188416 and base+size<=0x40000000,'DDR_ALLOCATION_RANGE')
            require(context['input_sha256']==[digest(self.plan_input[i*2884:(i+1)*2884]) for i in range(self.total_steps)]
                    and context['expected_sha256']==[digest(self.plan_expected[i*182676:(i+1)*182676]) for i in range(self.total_steps)],'DDR_PLAN_IDENTITY')
            check_receipt(receipt,0,run,context['cookie'],'0'*64,record.input_sha256,record.state_sha256)
            require(receipt['record_sha256']==digest(files['record_000000.bin']),'DDR_FIRST_RAW_SHA')
            ns=timing['input_and_STEP_ns'];require(type(ns) is int and 0<=ns<60_000_000_000,'DDR_FIRST_TIMING')
            require(sha(READINESS)==READINESS_SHA,'DDR_MODEL_READINESS_CHANGED')
            contract=load(READINESS)
            from spatial_state import SpatialRegistry
            spatial=SpatialRegistry();require(spatial.digest==contract['consumer']['spatial_mapping_sha256'],'DDR_SPATIAL_IDENTITY')
            # Save the exact observation before returning permission to continue.
            self.output.mkdir(parents=True,exist_ok=True)
            with (self.output/'FIRST_STEP.zip').open('xb') as f:
                f.write(blob);f.flush()
                import os
                os.fsync(f.fileno())
            self.contract,self.spatial=contract,spatial
            self.full=np.frombuffer(record.state_bits,dtype='<f4');self.input=np.frombuffer(record.input_bits,dtype='<f4')
            self.archive_sha=digest(blob);self.path=self.output/'FIRST_STEP.zip'
            self.value=dict(operator=op,context=context,receipt=receipt,timing=timing,record=record)
            return self.frame()

    def status(self):
        if self.value is None:return dict(configured=True,status='WAITING_FIRST_STEP',board_connection='NOT_CONNECTED')
        v=self.value
        return dict(configured=True,status='VERIFIED_SAVED_FIRST_STEP',run_id=v['context']['run_id'],
            boot_id=v['operator']['boot_id'],archive_sha256=self.archive_sha,board_connection='NOT_CONNECTED',
            timing=dict(input_seconds=0.,step_call_seconds=v['timing']['input_and_STEP_ns']/1e9,readback_seconds=0.),
            initial_state_readback=INITIAL_BOUNDARY,evidence_level='CPU_PROTOCOL_ONLY' if self.software_test else 'HUMAN_PHYSICAL_FIRST_POST_STATE_PC_ALL_WORDS_VERIFIED')

    def frame(self):
        v=self._load();op,c,r=v['operator'],v['context'],v['record'];a=self.spatial.extract(self.full)
        model=dict(self.contract['model'])
        if self.total_steps==485:model['initial_state_sha256']=self.plan['initial_state']['sha256']
        return dict(schema='flyvis-full-pl-first-step-display/v1',run_id=c['run_id'],session_id=c['run_id'],
            backend='FULL_NETWORK_FPGA',display_kind='CPU_PROTOCOL_TEST_ONLY' if self.software_test else 'OFFLINE_REPLAY_FULL_NETWORK_FPGA',
            evidence_level=self.status()['evidence_level'],step_id=0,serial=1,state_token=1,
            input_time_s=self.plan.get('input_time_offset_s',0.),activity_time_s=self.plan.get('input_time_offset_s',0.)+.005,
            source=dict(sequence=0,kind='line11_frozen_frame0',condition_id=self.plan.get('condition_id')),input_hex=self.input.tolist(),input_sha256=r.input_sha256,
            full_state_sha256=r.state_sha256,spatial=dict(values=a.tolist(),values_sha256=digest(a.tobytes()),map_sha256=self.spatial.digest),
            signed_means=a.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),model=model,
            hardware=dict(boot_id=op['boot_id'],bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,compute_cycles=CORE_CYCLES,
                clock_hz=100000000,faults=0,completed_steps=1,board_id='OPERATOR_REPORTED_ZYNQ7020'),
            transport_profile=PROFILE,initial_state_readback=INITIAL_BOUNDARY,operator_context_pc_verified=not self.software_test,
            audit_chain=v['receipt']['chain'],audit_cookie=c['cookie'],archive_sha256=self.archive_sha,plan_id=self.plan_id,
            plan_metadata=dict(condition_id=self.plan.get('condition_id'),initial_state=self.plan.get('initial_state'),
                steps=self.total_steps,input_time_offset_s=self.plan.get('input_time_offset_s',0.),model_dt_s=.005,
                input_kind=self.plan.get('input_kind','official_frozen_digital_stimulus')),
            flow=None,flow_status='NOT_AVAILABLE_NOT_DECODED',board_connection='NOT_CONNECTED',continuous_execution='PENDING')


class DdrGuiSession(FullPLStream):
    """Only startup admission is new; subsequent frames use the existing stream."""
    def init__(self, output, software_test=False, total_steps=3,plan_root=None,plan_sha=None):
        self.preparation_id=uuid.uuid4().hex;self.preparation_token=secrets.token_hex(32)
        self.output=Path(output)/self.preparation_id
        self.admission_lock=threading.Lock()
        self.total_steps=total_steps;self.flow_consumer=None;self.decoded_frame=None;self.flow_revision=0
        self.receipt_limit=485 if total_steps==485 else 64
        super().init__(DdrFirstStep(self.preparation_id,self.output,software_test,total_steps,plan_root,plan_sha),True,total_steps-1,protocol_test=software_test)

    def prepare(self):
        require(self.state not in ('FAILED','STOPPED'),'DDR_ADMISSION_FAILED_NO_RETRY')
        return super().prepare()

    def status(self):
        if self.seed.value is None:
            return dict(status=self.state,configured=True,first_step_accepted=False,result_valid=False,
                error=self.error,preparation_id=self.preparation_id,board_connection='NOT_CONNECTED',received_steps=0)
        s=super().status()
        if self.flow_consumer:
            s['official_flow']=self.flow_consumer.status()
            s['display_complete']=s['status']=='FINISHED' and s['official_flow']['status']=='COMPLETE'
            s['storage_policy']='BOARD_RAW_RECORDS_AND_PC_ASYNC_COMPLETE_STATE_INPUT_FLOW_ARCHIVE'
        return s

    def _flow_ready(self,snapshot,flow):
        with self.lock:
            if self.state in ('FAILED','STOPPED'):return
            m=snapshot[0];b=flow['binding']
            require(all(b.get(k)==v for k,v in dict(run_id=m['run_id'],session_id=self.session_id,
                frame_id=m['frame_id'],full_state_sha256=m['state_sha256']).items()),'DDR_DECODED_FLOW_BINDING')
            require(b['decoder']=='DecoderGAVP' and b['recursive_eval'] is True
                    and b['decoder_source_sha256']==self.decoder_pin['sha256']
                    and b['checkpoint_sha256']==self.anchor['model']['checkpoint_sha256'],'DDR_OFFICIAL_DECODER_IDENTITY')
            self.decoded_frame=(*snapshot[:4],flow);self.revision+=1;self.flow_revision+=1

    def frame_reply(self,snapshot,status,revision):
        reply=super().frame_reply(snapshot,status,revision)
        if self.seed.plan.get('input_kind')=='recorded_camera_flyvis':
            p=reply['frame'];row=self.seed.plan['source_frames'][p['step_id']]
            p['source'].update(kind='recorded_camera_flyvis',**row)
        return reply

    def source_frame(self,step,run,state_sha):
        require(self.seed.plan.get('input_kind')=='recorded_camera_flyvis','DDR_NOT_CAMERA_SOURCE')
        with self.lock:
            require(self.status()['result_valid'] and run==self.anchor['run_id'] and type(step) is int and 0<=step<485,'DDR_CAMERA_PREVIEW_IDENTITY')
            require(digest(self.seed.plan_expected[step*182676:(step+1)*182676])==state_sha,'DDR_CAMERA_PREVIEW_STATE')
            row=self.seed.plan['source_frames'][step]
        path=Path(self.seed.plan['recording_directory'])/'raw_frames'/('frame_%06d.png'%row['source_frame'])
        raw=path.read_bytes();require(digest(raw)==row['pixel_png_sha256'],'DDR_CAMERA_PREVIEW_PIXELS_CHANGED')
        return raw

    def replay(self,step):
        """Read only this completed run's actual received states, never the plan."""
        with self.lock:
            s=self.status()
            require(self.flow_consumer is not None and s['status']=='FINISHED' and s.get('display_complete')
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
        require(bits==self.seed.plan_expected[step*182676:(step+1)*182676]
                and inp==self.seed.plan_input[step*2884:(step+1)*2884],'DDR_REPLAY_CURRENT_PLAN')
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
        if self.flow_consumer:
            with self.lock:
                s=self.status()
                if s['official_flow']['error']:return dict(status=dict(s,result_valid=False,error=s['official_flow']['error'],status='FAILED'),frame=None)
                if not s['result_valid'] or self.decoded_frame is None or self.flow_revision==after:return dict(status=s,frame=None)
                snapshot=self.decoded_frame;revision=self.flow_revision
            return self.frame_reply(snapshot,s,revision)
        return super().latest(after)

    def accept(self,blob,authorization):
        reply=super().accept(blob,authorization)
        with self.lock:
            m,inp,bits,_,_=self.latest_frame;k=m['frame_id']
            if inp!=self.seed.plan_input[k*2884:(k+1)*2884] or bits!=self.seed.plan_expected[k*182676:(k+1)*182676]:
                self.abort('DDR_CURRENT_PLAN_ALL_WORD_MISMATCH');raise ValueError('DDR_CURRENT_PLAN_ALL_WORD_MISMATCH')
            if self.flow_consumer:self.flow_consumer.submit(self.latest_frame)
        return reply

    def authenticate_preparation(self, authorization):
        import hmac
        require(isinstance(authorization,str) and hmac.compare_digest(authorization,'Bearer '+self.preparation_token),'DDR_PREPARATION_UNAUTHORIZED')

    def accept_first(self, blob, authorization):
        self.authenticate_preparation(authorization)
        with self.admission_lock:
            require(self.state=='WAITING_FIRST_STEP','DDR_FIRST_ADMISSION_CLOSED')
            try:
                self.seed.admit(blob);self.prepare()
                if self.flow_consumer:
                    r=self.seed.value['record'];m=dict(run_id=self.anchor['run_id'],session_id=self.session_id,
                        frame_id=0,state_sha256=r.state_sha256,input_sha256=r.input_sha256,
                        previous_state_sha256=self.seed.plan['initial_state']['sha256'],elapsed_seconds=self.seed.value['timing']['input_and_STEP_ns']/1e9,
                        source_audit=self.seed.value['receipt'])
                    now=self.clock();self.receipts[0]=(r.state_sha256,now)
                    self.flow_consumer.submit((m,r.input_bits,r.state_bits,now,None))
                return dict(status='FIRST_STEP_ALL_WORDS_ACCEPTED_CONTINUE',connection=self.connection(self.callback_url),
                            initial_state_readback=INITIAL_BOUNDARY,whole_run_acceptance='PENDING')
            except Exception as error:
                self.abort(str(error));raise

    def package(self, callback_url):
        self.callback_url=callback_url
        self.output.mkdir(parents=True,exist_ok=False)
        config=dict(schema='flyvis-line2-ddr-preparation/v1',preparation_id=self.preparation_id,
            url=callback_url,token=self.preparation_token,total_steps=self.total_steps,
            release_manifest_sha256=MANIFEST_SHA,board_operations_authorized=False,
            startup_sha256={n:digest((HERE/n).read_bytes()) for n in STARTUP_FILES})
        if self.total_steps in (32,485):config['plan_manifest_sha256']=self.seed.plan_sha or {32:PLAN32_SHA,485:PLAN485_SHA}[self.total_steps]
        root,files=verify_release()
        self.link_path=self.output/'LINE11_DDR_PREPARE.zip'
        with zipfile.ZipFile(self.link_path,'x',zipfile.ZIP_DEFLATED) as z:
            for name in files:z.write(root/name,name)
            z.write(root/'release_manifest.json','release_manifest.json')
            for name in STARTUP_FILES:
                z.write(HERE/name,name)
            if self.total_steps in (32,485):
                for name in ('RUN_PLAN.json','plan_inputs.bin','plan_expected_states.bin'):z.write(self.seed.plan_root/name,name)
            z.writestr('PREPARATION.json',json.dumps(config,indent=2))
            z.writestr('start_here.txt',
                'PC: leave the original GUI running. Board: extract this private ZIP into a NEW directory.\n'
                'Only after releasing other board tasks, open START_DDR.ipynb and run its ONE code cell.\n'
                f'It loads this image once, allocates {self.total_steps} DDR slots once, restores once, checks first state on PC, then runs {self.total_steps-1} more steps.\n'
                'No GPU/camera/neural inference on PC. For ON60_485 only, original CPU decoder consumes actual received full states asynchronously.\n'
                'Initial-state readback unsupported; complete post-step states are checked.\n'
                'On ANY error keep this kernel and DDR; do not retry/reset/reload. This package alone is not authorization.\n')
            z.writestr('START_DDR.ipynb',json.dumps(dict(nbformat=4,nbformat_minor=4,
                metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3')),
                cells=[dict(cell_type='markdown',metadata={},source=['先确认其他板卡任务已停止并释放，才运行下一格。一次加载新版固件、一次DDR分配；严格先验收首步，再继续本次有界计划。失败不要重跑或复位。']),
                dict(cell_type='code',execution_count=None,outputs=[],metadata={},source=[
                    '%run line11_ddr_board.py --execute --exclusive-board-window\n'])]),ensure_ascii=False))
        self.write_bootstrap()
        return self.link_path

    def write_bootstrap(self):
        """Second upload file: safe extraction, then the SAME human board entry."""
        source='''from pathlib import Path
import hashlib, runpy, sys, zipfile
line2_zip=Path("LINE11_DDR_PREPARE.zip")
assert hashlib.sha256(line2_zip.read_bytes()).hexdigest()=="ZIP_SHA", "Wrong preparation ZIP"
line2_dir=Path("LINE11_DDR_PREP_ID").resolve()
assert not line2_dir.exists(), "Already extracted/attempted; stop and report, do not retry"
with zipfile.ZipFile(line2_zip) as line2_archive:
    rows=line2_archive.infolist()
    assert len(rows)<40 and sum(x.file_size for x in rows)<128000000, "Package bounds"
    assert len({x.filename for x in rows})==len(rows), "Duplicate entries"
    assert all(Path(x.filename).name==x.filename and not x.is_dir() and not x.flag_bits&1 for x in rows), "Unsafe archive"
    line2_dir.mkdir()
    line2_archive.extractall(line2_dir)
sys.path.insert(0,str(line2_dir))
sys.argv=[str(line2_dir/"line11_ddr_board.py"),"--execute","--exclusive-board-window"]
runpy.run_path(str(line2_dir/"line11_ddr_board.py"),run_name="__main__")
'''.replace('ZIP_SHA',digest(self.link_path.read_bytes())).replace('PREP_ID',self.preparation_id)
        nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3')),
            cells=[dict(cell_type='markdown',metadata={},source=['板卡独占并释放其他任务后，上传本文件与同次ZIP到同一目录，只运行下一格一次。首步PC验收后自动继续；失败保留内核、DDR和输出，不自动重试。']),
            dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=source.splitlines(keepends=True))])
        (self.output/'START_DDR.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def start_cpu_flow(self):
        if self.total_steps!=485 or self.flow_consumer is not None:raise ValueError('DDR485_EXPLICIT_DECODER_ONLY')
        from line11_ddr_flow import FlowConsumer
        self.flow_consumer=FlowConsumer(self.output/'official_flow',self._flow_ready);self.flow_consumer.start()

    def close(self):
        if self.flow_consumer:self.flow_consumer.close()
        super().close()
