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
    def init__(self, nonce, output, software_test=False):
        super().init__(None)
        self.nonce,self.output,self.software_test=nonce,Path(output),software_test
        self.root,self.files=verify_release()
        self.codec=record_codec(self.root,self.files)

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
            require(op['startup_sha256']=={n:digest((HERE/n).read_bytes()) for n in
                ('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py')},'DDR_STARTUP_SOURCE_IDENTITY')
            context=json.loads(files['RUN_CONTEXT.json']);receipt=json.loads(files['receipt_000000.json'])
            timing=json.loads(files['TIMING.json'])
            record=self.codec.decode_record(files['record_000000.bin'],0)
            require(record.cycles==CORE_CYCLES,'DDR_FIRST_CYCLES')
            require(record.input_bits==(self.root/'inputs.bin').read_bytes()[:2884]
                    and record.state_bits==(self.root/'expected_states.bin').read_bytes()[:182676],'DDR_FIRST_ALL_WORD_COMPARISON')
            run=context['run_id'];require(re.fullmatch(r'[0-9a-f]{32}',run),'DDR_FIRST_RUN_ID')
            require(context['evidence']==receipt['evidence']==('CPU_MOCK_ONLY' if self.software_test else 'OPERATOR_PHYSICAL_READS_UNATTESTED')
                    and context['board_result'] is False and context['slots']==3,'DDR_FIRST_SCOPE')
            base=context['physical_base'];size=context['allocated_bytes']
            require(type(base) is int and base%4096==0 and base>=0x100000
                    and size==3*188416 and base+size<=0x40000000,'DDR_ALLOCATION_RANGE')
            require(context['input_sha256']==[digest((self.root/'inputs.bin').read_bytes()[i*2884:(i+1)*2884]) for i in range(3)]
                    and context['expected_sha256']==[digest((self.root/'expected_states.bin').read_bytes()[i*182676:(i+1)*182676]) for i in range(3)],'DDR_PLAN_IDENTITY')
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
        return dict(schema='flyvis-full-pl-first-step-display/v1',run_id=c['run_id'],session_id=c['run_id'],
            backend='FULL_NETWORK_FPGA',display_kind='CPU_PROTOCOL_TEST_ONLY' if self.software_test else 'OFFLINE_REPLAY_FULL_NETWORK_FPGA',
            evidence_level=self.status()['evidence_level'],step_id=0,serial=1,state_token=1,input_time_s=0.,activity_time_s=.005,
            source=dict(sequence=0,kind='line11_frozen_frame0'),input_hex=self.input.tolist(),input_sha256=r.input_sha256,
            full_state_sha256=r.state_sha256,spatial=dict(values=a.tolist(),values_sha256=digest(a.tobytes()),map_sha256=self.spatial.digest),
            signed_means=a.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),model=self.contract['model'],
            hardware=dict(boot_id=op['boot_id'],bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,compute_cycles=CORE_CYCLES,
                clock_hz=100000000,faults=0,completed_steps=1,board_id='OPERATOR_REPORTED_ZYNQ7020'),
            transport_profile=PROFILE,initial_state_readback=INITIAL_BOUNDARY,operator_context_pc_verified=not self.software_test,
            audit_chain=v['receipt']['chain'],audit_cookie=c['cookie'],archive_sha256=self.archive_sha,
            flow=None,flow_status='NOT_AVAILABLE_NOT_DECODED',board_connection='NOT_CONNECTED',continuous_execution='PENDING')


class DdrGuiSession(FullPLStream):
    """Only startup admission is new; subsequent frames use the existing stream."""
    def init__(self, output, software_test=False):
        self.preparation_id=uuid.uuid4().hex;self.preparation_token=secrets.token_hex(32)
        self.output=Path(output)/self.preparation_id
        self.admission_lock=threading.Lock()
        super().init__(DdrFirstStep(self.preparation_id,self.output,software_test),True,2,protocol_test=software_test)

    def prepare(self):
        require(self.state not in ('FAILED','STOPPED'),'DDR_ADMISSION_FAILED_NO_RETRY')
        return super().prepare()

    def status(self):
        if self.seed.value is None:
            return dict(status=self.state,configured=True,first_step_accepted=False,result_valid=False,
                error=self.error,preparation_id=self.preparation_id,board_connection='NOT_CONNECTED',received_steps=0)
        return super().status()

    def authenticate_preparation(self, authorization):
        import hmac
        require(isinstance(authorization,str) and hmac.compare_digest(authorization,'Bearer '+self.preparation_token),'DDR_PREPARATION_UNAUTHORIZED')

    def accept_first(self, blob, authorization):
        self.authenticate_preparation(authorization)
        with self.admission_lock:
            require(self.state=='WAITING_FIRST_STEP','DDR_FIRST_ADMISSION_CLOSED')
            try:
                self.seed.admit(blob);self.prepare()
                return dict(status='FIRST_STEP_ALL_WORDS_ACCEPTED_CONTINUE',connection=self.connection(self.callback_url),
                            initial_state_readback=INITIAL_BOUNDARY,whole_run_acceptance='PENDING')
            except Exception as error:
                self.abort(str(error));raise

    def package(self, callback_url):
        self.callback_url=callback_url
        self.output.mkdir(parents=True,exist_ok=False)
        config=dict(schema='flyvis-line2-ddr-preparation/v1',preparation_id=self.preparation_id,
            url=callback_url,token=self.preparation_token,total_steps=3,
            release_manifest_sha256=MANIFEST_SHA,board_operations_authorized=False,
            startup_sha256={n:digest((HERE/n).read_bytes()) for n in
                ('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py')})
        root,files=verify_release()
        self.link_path=self.output/'LINE11_DDR_PREPARE.zip'
        with zipfile.ZipFile(self.link_path,'x',zipfile.ZIP_DEFLATED) as z:
            for name in files:z.write(root/name,name)
            z.write(root/'release_manifest.json','release_manifest.json')
            for name in ('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py'):
                z.write(HERE/name,name)
            z.writestr('PREPARATION.json',json.dumps(config,indent=2))
            z.writestr('start_here.txt',
                'PC: leave the original GUI running. Board: extract this private ZIP into a NEW directory.\n'
                'Only after releasing other board tasks, open START_DDR.ipynb and run its ONE code cell.\n'
                'It loads this image once, allocates 3 DDR slots once, restores once, checks first state on PC, then runs 2 more steps.\n'
                'No GPU/camera/decoder. Initial-state readback unsupported; complete post-step states are checked.\n'
                'On ANY error keep this kernel and DDR; do not retry/reset/reload. This package alone is not authorization.\n')
            z.writestr('START_DDR.ipynb',json.dumps(dict(nbformat=4,nbformat_minor=4,
                metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3')),
                cells=[dict(cell_type='markdown',metadata={},source=['先确认其他板卡任务已停止并释放，才运行下一格。一次加载新版固件、一次DDR分配；严格先验收首步，再继续两步。失败不要重跑或复位。']),
                dict(cell_type='code',execution_count=None,outputs=[],metadata={},source=[
                    '%run line11_ddr_board.py --execute --exclusive-board-window\n'])]),ensure_ascii=False))
        return self.link_path
