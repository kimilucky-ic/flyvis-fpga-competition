"""One user-approved 32-step GPU + pinned CPU-Q24 experiment, never PL evidence."""
import csv, dataclasses, io, json, os, socket, sys, threading, time, uuid
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1]
sys.path.insert(0,str(GUI))
from live_protocol import Registry,load,write,sha,canonical,require,utc
from live_worker import import_file
from hybrid_full485 import Full485Contract
from hybrid_gpu import GPUCandidates
from joint_minimal_core import MinimalEngine,AsyncRecords
from joint_diagnostics import NONE
from joint_camera_control import hardware_module

KIND='ACTUAL_GPU_WITH_SOFTWARE_Q24_H'
source=GUI/'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e'
RUN=uuid.uuid4().hex
began=time.monotonic()
handle=torch=engine=recorder=None
flush=threading.Event()
network_attempts=[]
old_connect=socket.socket.connect
def no_network(sock,address):
    if sock.family in (socket.AF_INET,socket.AF_INET6):
        network_attempts.append(str(address));raise RuntimeError('NETWORK_FORBIDDEN_IN_SOFTWARE32')
    return old_connect(sock,address)
socket.socket.connect=no_network

def checkpoint(phase):
    require(time.monotonic()-began<180,'SOFTWARE32_TIME_BOUND')
    if phase!='compute':
        require(not (OUT/'STOP_REQUEST.json').exists(),'SOFTWARE32_USER_STOP')

class SoftwareQ24Client:
    """No socket. Original scalar oracle supplies H; ACK is software-only."""
    def init__(self,c):
        self.c=c;self.w=c.wire;self.asid=uuid.uuid4().bytes
        self.pending=self.previous=None;self.rows=[]
    def step(self,old,chemical,x,identity):
        require(self.pending is None,'SOFTWARE_PREVIOUS_ACK_REQUIRED')
        payload=old+chemical+x
        if self.previous:
            k,words,decision,txn=self.previous
            require(identity['step']==k+1 and old==words and identity['parent_commit']==decision
                and identity['previous_txn']==txn,'SOFTWARE_CANONICAL_FEEDBACK')
        at=time.perf_counter_ns();candidate,_=self.c.expected_H(payload)
        self.rows.append(dict(Q24_software_H_ns=time.perf_counter_ns()-at))
        h=self.w.Header(self.w.STEP,payload_bytes=len(payload),payload_sha=self.w.digest(payload),**identity)
        self.pending=(h,candidate)
        # These constants only satisfy the existing barrier's wire-shape check.
        # They are NOT read from a board and are NOT exported as PL timings.
        return candidate,dataclasses.replace(h,op=self.w.RESULT,payload_bytes=len(candidate),
            payload_sha=self.w.digest(candidate),compute_cycles=57681,transfer_cycles=57681)
    def commit(self,decision):
        require(self.pending is not None,'SOFTWARE_NO_PENDING_CANDIDATE')
        h,words=self.pending
        ack=dataclasses.replace(h,op=self.w.ACK,payload_bytes=0,payload_sha=self.w.digest(b''),parent_commit=decision)
        self.previous=(h.step,words,decision,h.txn);self.pending=None
        return ack
    def close(self):pass

try:
    require(not (OUT/'SCOPE.json').exists(),'ONE_ATTEMPT_ONLY')
    c=Full485Contract();reg=c.reg
    accepted=GUI/'evidence/camera_joint32_20261017_b3c166fc'
    audit=load(accepted/'actual_audit/FINAL_AUDIT.json')
    pins=load(accepted/'DELIVERY_MANIFEST.json')['files']
    require(sha(accepted/'actual_audit/FINAL_AUDIT.json')==pins['actual_audit\\FINAL_AUDIT.json']
        and audit['status']=='PASS_CAMERA_GPU_FPGA_32STEP_SAVED_DATA_PATH_AUDIT'
        and sha(source/'pc/evidence.fvej')==audit['PC_capture_sha256'],'ACCEPTED_INPUT_IDENTITY')
    Reader=hardware_module(load(source/'hardware_handoff.json'),'evidence_journal').JournalReader
    reader=Reader(source/'pc/evidence.fvej')
    array=lambda name:np.load(io.BytesIO(reader.read(name)),allow_pickle=False)
    frames=np.stack([array('input_721_%d.npy'%k) for k in range(32)])
    expected=np.stack([array('committed_full_%d.npy'%k) for k in range(32)])
    expected_words=[reader.read('candidate_%d.bin'%k) for k in range(32)]
    expected_flows=np.stack([array('flow_%d.npy'%k) for k in range(32)])
    require(np.array_equal(c.initial()[0],array('old_full_0.npy')),'SAME_FROZEN_INITIAL_STATE')
    scope=dict(run_id=RUN,session_id=uuid.uuid4().hex,comparison_id='GPU_SOFTWARE_Q24_'+RUN,
        condition_id='RECORDED_CAMERA32',max_steps=32,model=c.registry['model'],mapping_sha256=c.mapping_sha,
        execution_kind=KIND,source_kind='RECORDED_CAMERA_FROZEN_NOT_LIVE',source_run=audit['run_id'],
        input_sha256=__import__('hashlib').sha256(frames.tobytes()).hexdigest(),model_dt_s=.005,
        H_backend='PINNED_A3_SCALAR_Q24_CPU',R_backend='ORIGINAL_FLYVIS_GPU_FP32',
        authorization='CURRENT_CHAT_USER_20261018_THEN_TEST_32_STEPS',board_enabled=False,camera_enabled=False,
        GUI_enabled=False,PL_proven_global_ids=[],max_gpu_neural_steps=32,max_decoder_frames=32,
        max_attempts=1,wall_bound_s=180,recording='ASYNC_FLUSH_AFTER_COMPUTE_NO_INLINE_DISK',
        power_mode='current_unconfirmed',source_sha256={str(p):sha(p) for p in
            [Path(__file__),GUI/'joint_minimal_core.py',GUI/'hybrid_gpu.py',GUI/'hybrid_a3.py',
             reg.path_for('full'),reg.path_for('r_only'),reg.path_for('decoder'),c.paths['integer_reference']]})
    write(OUT/'SCOPE.json',scope);print('SOFTWARE32_CPU_ADMISSION_OK',flush=True)
    runner=import_file('line2_software32_existing_lease',reg.path_for('runner_lease'))
    class Lease(runner.Lease):
        def init__(self):
            self.job=OUT;self.config=dict(campaign_id=RUN,stage=KIND,queue_s=10)
            self.ticket=dict(config=self.config,identity_key=canonical(scope),job_dir=str(OUT),scope='32 actual GPU chemical/R, CPU Q24 H, zero board/camera/GUI')
        def check(self,phase='check'):
            checkpoint(phase)
            require(not runner.own_path('runtime','RESOURCE_QUARANTINE.json').exists(),'RESOURCE_QUARANTINE')
    handle,queue_s=Lease().acquire()
    scratch=Path('/tmp')/('software32-'+RUN);scratch.mkdir()
    os.environ.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',CUDA_VISIBLE_DEVICES='0',
        FLYVIS_ROOT_DIR=str(scratch/'flyvis'),MPLBACKEND='Agg',MPLCONFIGDIR=str(scratch/'mpl'))
    import torch as t
    torch=t;torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=torch.backends.cudnn.allow_tf32=False
    require(torch.cuda.is_available(),'CUDA_REQUIRED_NO_FALLBACK')
    require(torch.tensor([1.],device='cuda').add(1).item()==2,'ACTUAL_CUDA_OPERATION_REQUIRED')
    torch.cuda.reset_peak_memory_stats()
    at=time.monotonic()
    Full=import_file('line2_software32_original_model',reg.path_for('full')).FullNetworkOracle
    oracle=Full(reg.path_for('identity'),model_path=reg.data['runtime']['model_path'],device='cuda')
    producer=GPUCandidates(reg,c,oracle,torch,NONE)
    model_load_s=time.monotonic()-at
    print('ACTUAL_CUDA_MODEL_READY '+torch.cuda.get_device_name(),flush=True)
    def save(record):
        flush.wait()
        k=record['step_id']
        np.savez(OUT/('step_%02d.npz'%k),old_full=record['old'],input_721=record['frame'],
            chemical_H=record['output']['chemical_H'],R_candidate=record['output']['new_R'],
            software_Q24_H=np.frombuffer(record['candidate'],dtype='<i4'),committed_full=record['full'])
    recorder=AsyncRecords(save,capacity=32)
    client=SoftwareQ24Client(c);events=[]
    def produce(old,frame,k):
        before,after=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
        before.record()
        value=producer.produce(old,torch.as_tensor(frame,device='cuda'),run_id=RUN,step_id=k,condition_id='RECORDED_CAMERA32')
        after.record();events.append((before,after));return value
    engine=MinimalEngine(c,client,produce,lambda a:torch.as_tensor(a.copy(),device='cuda',dtype=torch.float32),scope,recorder)
    engine.barrier.execution_kind=KIND
    torch.cuda.synchronize();at=time.perf_counter_ns();calls=[]
    # No files, decoder, GUI, logging drain or socket in this measured window.
    for k in range(32):
        checkpoint('compute')
        start=time.perf_counter_ns();sample=engine.step(dict(values=frames[k]))
        calls.append(time.perf_counter_ns()-start)
    torch.cuda.synchronize();compute_ns=time.perf_counter_ns()-at
    flush.set();save_started=time.monotonic();recording=recorder.close(timeout=10)
    save_s=time.monotonic()-save_started
    rows=[]
    for k,(sample,call) in enumerate(zip(engine.samples,calls)):
        events[k][1].synchronize()
        gpu=sample['GPU_produce_wall_ns'];h=sample['STEP_socket_roundtrip_ns'];ack=sample['COMMIT_socket_roundtrip_ns']
        rows.append(dict(step=k,GPU_host_ms=gpu/1e6,CUDA_stream_interval_ms=events[k][0].elapsed_time(events[k][1]),
            Q24_software_H_ms=client.rows[k]['Q24_software_H_ns']/1e6,software_STEP_ms=h/1e6,
            software_ACK_ms=ack/1e6,coordinator_pack_merge_upload_ms=(sample['compute_step_wall_ns']-gpu-h-ack)/1e6,
            enqueue_and_return_ms=(call-sample['compute_step_wall_ns'])/1e6,total_call_ms=call/1e6))
    actual=np.stack([s['full'] for s in engine.samples])
    state_error=np.abs(actual-expected)
    code_errors=[int(np.abs(np.frombuffer(s['candidate'],dtype='<i4').astype(np.int64)-
        np.frombuffer(expected_words[k],dtype='<i4').astype(np.int64)).max()) for k,s in enumerate(engine.samples)]
    require(np.allclose(actual,expected,atol=1e-5,rtol=1e-5),'NEW_GPU_STATE_REFERENCE_MISMATCH')
    producer.check_unchanged();engine.original_unchanged();reg.unchanged()
    at=time.monotonic()
    Decode=import_file('line2_software32_original_decoder',reg.path_for('decoder')).OfficialDecoderService
    decoder=Decode(reg.data['runtime']['model_path'],reg.path_for('decoder_contract'),device='cuda',check_scope=checkpoint)
    decoder_load_s=time.monotonic()-at
    at=time.monotonic();flows=np.asarray(decoder.decode(actual[None],chunk_frames=32)[0],dtype='<f4')
    decode_s=time.monotonic()-at
    decoder.assert_weights_unchanged()
    require(np.allclose(flows,expected_flows,atol=1e-5,rtol=1e-5),'NEW_OFFICIAL_FLOW_REFERENCE_MISMATCH')
    np.save(OUT/'official_flow.npy',flows,allow_pickle=False)
    np.save(OUT/'input_721.npy',frames,allow_pickle=False)
    with (OUT/'timings.csv').open('x',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    stats=lambda name:dict(median=float(np.median([r[name] for r in rows])),p95=float(np.percentile([r[name] for r in rows],95)),max=float(max(r[name] for r in rows)),total=float(sum(r[name] for r in rows)))
    result=dict(status='PASS_ACTUAL_GPU32_SOFTWARE_Q24_ONLY' if recording['complete'] else 'COMPUTE_PASSED_RECORDING_INCOMPLETE',run_id=RUN,execution_kind=KIND,
        source_kind=scope['source_kind'],source_run=scope['source_run'],input_sha256=scope['input_sha256'],
        device=torch.cuda.get_device_name(),steps=32,model_time_s=.16,compute_wall_s=compute_ns/1e9,steps_per_s=32e9/compute_ns,
        GPU=stats('GPU_host_ms'),CUDA_stream_interval=stats('CUDA_stream_interval_ms'),
        software_H=stats('Q24_software_H_ms'),software_STEP=stats('software_STEP_ms'),software_ACK=stats('software_ACK_ms'),
        coordinator=stats('coordinator_pack_merge_upload_ms'),enqueue=stats('enqueue_and_return_ms'),
        first_step=rows[0],remaining_31_GPU_median_ms=float(np.median([r['GPU_host_ms'] for r in rows[1:]])),
        model_load_s=model_load_s,decoder_load_s=decoder_load_s,post_compute_decode_s=decode_s,post_compute_save_s=save_s,
        recording=recording,source_and_model_unchanged=True,native_H_GPU_updates=producer.native_H_update_count,
        state_bitwise_equal=bool(np.array_equal(actual,expected)),state_max_abs=float(state_error.max()),
        H_integer_code_max_error_vs_historical_PL=max(code_errors),flow_max_abs=float(np.abs(flows-expected_flows).max()),
        flow_bitwise_equal=bool(np.array_equal(flows,expected_flows)),atol=1e-5,rtol=1e-5,
        peak_CUDA_allocated_bytes=torch.cuda.max_memory_allocated(),peak_CUDA_reserved_bytes=torch.cuda.max_memory_reserved(),
        queue_s=queue_s,FPGA_status='NOT_CONNECTED',physical_board_operations=0,camera_operations=0,GUI_operations=0,
        network_attempts=network_attempts,PL_compute_ms=None,physical_transfer_ms=None,
        protocol_cycle_fields='SYNTHETIC_COMPATIBILITY_CONSTANTS_NOT_PL_MEASUREMENTS',
        timing_notes='GPU includes real host calls/synchronization/copies; CUDA events are stream intervals, not pure kernels. CPU scalar H is not PL latency. First cold step included, no extra warm-up or second rollout.',
        REALTIME_STREAM_PASS='NOT_CLAIMED')
    write(OUT/'RESULT.json',result);print(json.dumps(result),flush=True)
except BaseException as error:
    write(OUT/'FAILURE.json',dict(status='FAILED',error=repr(error),run_id=RUN,FPGA_status='NOT_CONNECTED',network_attempts=network_attempts))
    raise
finally:
    flush.set()
    if recorder:recorder.close(timeout=1)
    if engine:engine.close()
    if torch:torch.cuda.synchronize()
    if handle:handle.close()
    write(OUT/'EXIT.json',dict(GPU_waited=bool(torch),lease_closed=bool(handle),FPGA_status='NOT_CONNECTED',
        physical_board_operations=0,network_attempts=network_attempts,wall_s=time.monotonic()-began))
