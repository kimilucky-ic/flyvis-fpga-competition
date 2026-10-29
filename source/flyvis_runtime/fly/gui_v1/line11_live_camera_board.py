"""Human-only full-PL camera backend. Reuses sealed DDR drivers, no GPU math.

One restored complete state remains in PL throughout the bounded camera window.
The original drivers retain immutable DDR; failures never reload/reset/retry.
"""
import base64
import hashlib
import io
import json
from pathlib import Path
import platform
import struct
import sys
import time
import zipfile
from line11_ddr_board import (exclusive_inventory,live_context,PreparationClient,
                             BIT_SHA,HWH_SHA,MANIFEST_SHA,require,digest)

ROOT=Path(__file__).resolve().parent
INITIAL='d276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f'


def verify(root):
    raw=(root/'release_manifest.json').read_bytes()
    require(digest(raw)==MANIFEST_SHA,'LIVE_DDR_RELEASE_CHANGED')
    for name,info in json.loads(raw).items():
        require(Path(name).name==name and len((root/name).read_bytes())==info['bytes']
                and digest((root/name).read_bytes())==info['sha256'],'LIVE_DDR_SOURCE_CHANGED '+name)
    config=json.loads((root/'PREPARATION.json').read_text(encoding='utf-8'))
    require(config['schema']=='flyvis-line2-ddr-live-camera/v1'
            and config['total_steps']==485
            and ((config.get('scientific_input') and config['duration_s'] is None and config['step_rate_limit_hz']==0)
                 or (not config.get('scientific_input') and config['duration_s']==60 and config['step_rate_limit_hz']==8))
            and config['release_manifest_sha256']==MANIFEST_SHA,'LIVE_CAMERA_SCOPE')
    if config.get('scientific_input'):
        b=config['scientific_input']
        require(b['PACK_sha256']=='7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
            and b['steps']==485 and b['dt_s']==.005 and b['initial_raw_sha256']==INITIAL
            and b['numerical_profile']=='FULL_PL_STRICT_FP32' and b['initial_policy']=='ORIGINAL_BIAS_FP32','SCIENTIFIC_BOARD_PROFILE')
    for name,pin in config['startup_sha256'].items():
        require(Path(name).name==name and digest((root/name).read_bytes())==pin,'LIVE_STARTUP_SOURCE_CHANGED')
    return config


def run_window(control,memory,pc,config,operator,output,*,clock=time.monotonic_ns):
    """CPU-injectable orchestration; all neural advancement uses original DdrControl."""
    from ddr_acceptance import save_new
    output=Path(output);capacity=config['total_steps'];run=config['preparation_id'];cookie=int(run[:8],16)
    memory.pin_before_configure();control.restore_initial();control.configure(memory.base,memory.size,capacity,cookie)
    record_evidence='CPU_MOCK_ONLY' if operator['evidence']=='CPU_MOCK_ONLY' else 'OPERATOR_PHYSICAL_READS_UNATTESTED'
    context=dict(run_id=run,slots=capacity,cookie=cookie,physical_base=memory.base,allocated_bytes=memory.size,
                 evidence=record_evidence,board_result=False,mode='SCIENTIFIC_FULL_NETWORK_FPGA' if config.get('scientific_input') else 'LIVE_CAMERA_FULL_NETWORK_FPGA')
    previous=INITIAL;chain='0'*64;timing=[];began=clock()
    try:
        if config.get('waits_for_gui_start'):print('BOARD_INITIALIZED_WAITING_GUI_START · 请回实验台点开始；本格继续等待，不重复运行。',flush=True)
        request=pc.post('/api/full-pl-stream/camera-input',json.dumps(dict(preparation_id=run,operator=operator,context=context)).encode(),'application/json')
        input_setup_ns=clock()-began
        while not request.get('stop'):
            k=len(timing)
            require(k<capacity and request['step']==k and request['previous_state_sha256']==previous,'LIVE_INPUT_STATE_BINDING')
            inp=base64.b64decode(request['input_b64'],validate=True)
            require(len(inp)==2884 and digest(inp)==request['input_sha256'],'LIVE_INPUT_SHA')
            before=clock();descriptor=control.advance(inp);elapsed=clock()-before
            require(descriptor.frame_id==k and descriptor.sequence==k+1 and descriptor.cookie==cookie,'LIVE_PUBLICATION_IDENTITY')
            raw=memory.copy_record(descriptor)
            require(len(raw)==188416 and struct.unpack_from('<I',raw,8)[0]==k
                    and raw[128:3012]==inp,'LIVE_PUBLISHED_CURRENT_INPUT')
            bits=raw[4096:186772];after=digest(bits)
            following=digest(bytes.fromhex(chain)+struct.pack('<I',k)+bytes.fromhex(digest(inp))+bytes.fromhex(after))
            receipt=dict(frame_id=k,run_id=run,cookie=cookie,input_sha256=digest(inp),state_sha256=after,
                         previous_chain=chain,chain=following,record_bytes=len(raw),record_sha256=digest(raw),
                         evidence=record_evidence,board_result=False)
            meta=dict(run_id=run,frame_id=k,previous_state_sha256=previous,source_audit=receipt,
                      elapsed_seconds=elapsed/1e9,compute_cycles=descriptor.cycles)
            header=json.dumps(meta,separators=(',',':')).encode()
            reply=pc.post('/api/full-pl-stream/camera-record',struct.pack('<I',len(header))+header+raw,'application/octet-stream')
            require(reply['accepted_step']==k and reply['full_state_sha256']==after,'LIVE_PC_RECEIPT_MISMATCH')
            timing.append(dict(step=k,input_and_STEP_ns=elapsed,record_copy_send_return_ns=clock()-before-elapsed))
            previous,chain=after,following;request=reply['next_input']
        require(timing and control._r(0x14)==len(timing) and not control._r(0x10)&1
                and control._r(0x24)==0,'LIVE_FINAL_IDLE_COUNT_OR_ERROR')
        result=dict(status='LIVE_CAMERA_WINDOW_FINISHED_PENDING_PC_NUMERICAL_AUDIT',run_id=run,
                    completed_steps=len(timing),last_state_sha256=previous,receipt_chain=chain,
                    requested_wall_s=config.get('duration_s',60),scientific_input=config.get('scientific_input'),PC_window=request,board_loop_ns=clock()-began,input_setup_wait_ns=input_setup_ns,
                    model_time_s=len(timing)*.005,step_rate_limit_hz=config.get('step_rate_limit_hz',8),
                    timing=timing,allocation_retained=True,board_result=False,
                    physical_clock_measured=False,REALTIME_STREAM_PASS='NOT_CLAIMED',
                    storage='NONOVERWRITING_OWNED_DDR_RETAINED; PC_ASYNC_RAW_RECORDS_INPUT_STATE_FLOW',
                    GPU_neural_updates=0)
        save_new(output/'RESULT.json',result)
        pc.post('/api/full-pl-stream/camera-end',json.dumps(dict(preparation_id=run,completed_steps=len(timing),
                last_state_sha256=previous,idle=True,faults=0,receipt_chain=chain,stop_reason=request['reason'])).encode(),'application/json')
        return result
    except BaseException as error:
        control.failed=True
        save_new(output/'STOP.json',dict(error=str(error),status='IN_DOUBT_KEEP_KERNEL_AND_DDR_NO_RETRY_RESET_OR_FREE',steps=len(timing)))
        raise


def verify_previous_owner(owner,boot_id,pid):
    """Read-only gate; only a completed/audited SAME-kernel owner can hand over."""
    require(owner.get('schema')=='line2-normal-owned-ddr/v1' and owner['boot_id']==boot_id
            and owner['pid']==pid and not owner.get('retired'), 'PREVIOUS_OWNER_IDENTITY_OR_RETIRED')
    memory=owner['memory'];control=owner['control'];proof=owner['proof']
    require(proof['status']=='NORMAL_RETURN_ACKED' and proof['preparation_id']==owner['run_id']
            and proof['completed_steps']==owner['completed_steps'] and not control.failed
            and memory.armed and not memory.released and owner['pins'].get(id(memory)) is memory,
            'PREVIOUS_OWNER_NOT_NORMALLY_AUDITED')
    require(not control._r(0x10)&1 and control._r(0x14)==owner['completed_steps']
            and control._r(0x18)==0 and control._r(0x24)==0
            and control._r(4)==memory.base and control._r(8)==memory.base+memory.size
            and control._r(12)==memory.slots and control._r(0x2c)==int(owner['run_id'][:8],16),
            'PREVIOUS_OWNER_NOT_IDLE_KEEP_DDR')


def release_previous_after_reload(owner,fresh_control):
    """Only after HUMAN-authorized verified reload removes the old PL DDR binding.

    Partial60s windows cannot use sealed release_after_verified_full(). Keep their
    armed allocation until a fresh image has discarded the old configuration.
    No sealed driver change and no old configured buffer freed before reload.
    """
    require(all(fresh_control._r(a)==0 for a in (0x10,0x14,0x18,0x24)),
            'RELOAD_NOT_FRESH_KEEP_PREVIOUS_DDR')
    memory=owner['memory']
    require(not owner.get('retired') and memory.armed and not memory.released
            and owner['pins'].get(id(memory)) is memory,'PREVIOUS_ALLOCATION_IDENTITY')
    memory.buffer.freebuffer()  # Old PL target is gone; exactly this owned allocation.
    memory.buffer=None;memory.released=True;memory.armed=False
    del owner['pins'][id(memory)];owner['control'].failed=True;owner['retired']=True


def complete_normal_return(control,memory,pc,config,operator,output,result,*,clock=time.monotonic,sleep=time.sleep):
    """No neural calls: wait for audit, persist handshake, retain owned DDR."""
    from ddr_acceptance import save_new
    request=dict(preparation_id=config['preparation_id'],completed_steps=result['completed_steps'],
                 last_state_sha256=result['last_state_sha256'],receipt_chain=result['receipt_chain'])
    deadline=clock()+120
    while True:
        reply=pc.post('/api/full-pl-stream/camera-closeout',json.dumps(dict(request,op='audit')).encode(),'application/json')
        if reply.get('status')!='AUDIT_PENDING':break
        require(clock()<deadline,'NORMAL_AUDIT_TIMEOUT_KEEP_DDR_NO_RETRY');sleep(.1)
    require(reply.get('status')=='NORMAL_WINDOW_AUDITED' and all(reply.get(k)==v for k,v in request.items()),'NORMAL_AUDIT_PROOF_MISMATCH')
    require(not control.failed and not control._r(0x10)&1 and control._r(0x14)==result['completed_steps']
            and control._r(0x18)==0 and control._r(0x24)==0,'NORMAL_RETURN_NOT_IDLE')
    proof=pc.post('/api/full-pl-stream/camera-closeout',json.dumps(dict(request,op='ack')).encode(),'application/json')
    require(proof.get('status')=='NORMAL_RETURN_ACKED' and all(proof.get(k)==v for k,v in request.items()),'NORMAL_RETURN_ACK_MISMATCH')
    save_new(Path(output)/'NORMAL_END.json',proof)
    import ddr_memory,os
    return dict(schema='line2-normal-owned-ddr/v1',run_id=config['preparation_id'],boot_id=operator['boot_id'],
                pid=os.getpid(),memory=memory,control=control,pins=ddr_memory._PINNED,
                completed_steps=result['completed_steps'],proof=proof,retired=False)


def main():
    require('--execute' in sys.argv and '--exclusive-board-window' in sys.argv,'Human execution/exclusive window required')
    # PC readiness can use 120s for CPU decoder plus 30s for first camera input.
    config=verify(ROOT);pc=PreparationClient(config);pc.http.timeout=300 if config.get('waits_for_gui_start') else 180
    pc.post('/api/full-pl-stream/camera-ready',json.dumps({'preparation_id':config['preparation_id']}).encode(),'application/json')
    # Initialization can exceed the PC's 5-second keep-alive idle timeout.
    # End the completed readiness exchange; next post reconnects, never retries a STEP.
    pc.http.close()
    require(platform.machine()=='armv7l','Zynq ARMv7 only')
    import pynq
    require(str(pynq.__version__).startswith('2.7.'),'Prepared PYNQ2.7 only')
    require(b'xlnx,zynq-7000' in Path('/proc/device-tree/compatible').read_bytes(),'Zynq7000 only')
    inventory=exclusive_inventory()
    previous=globals().get('LINE2_PREVIOUS_COMPLETED_OWNER')
    if previous is not None:
        import os
        verify_previous_owner(previous,Path('/proc/sys/kernel/random/boot_id').read_text().strip(),os.getpid())
    meminfo={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/meminfo').read_text().splitlines() if ':' in line}
    # CmaFree excludes movable pages: diagnostic only, never an allocation oracle.
    with (ROOT/'EXECUTION_STARTED.json').open('x',encoding='utf-8') as f:json.dump({'inventory':inventory},f)
    output=ROOT/'live_result';output.mkdir(exist_ok=False)
    from ddr_memory import OwnedDdr,pynq_allocator_and_barrier
    from ddr_control import DdrControl
    from ddr_acceptance import save_new
    admission=dict(required_bytes=config['total_steps']*188416,reported_meminfo=meminfo,
                   policy='LOAD_VERIFIED_OVERLAY_THEN_ALLOCATE_BEFORE_NEURAL_CONTROL',
                   overlay_load_attempted=False,overlay_loaded=False,neural_step_started=False)
    memory=None
    phase='ALLOCATOR_SETUP'
    try:
        allocator,barrier=pynq_allocator_and_barrier(output/'native',operator_authorized=True)
        phase='OVERLAY_LOAD'
        print('DDR_PREPARE: loading verified firmware; neural computation not started',flush=True)
        overlay=pynq.Overlay(str(ROOT/'flyvis_ddr.bit'),download=False)
        admission['overlay_load_attempted']=True
        overlay.download()
        admission['overlay_loaded']=True
        if previous is not None:
            phase='PREVIOUS_COMPLETED_DDR_HANDOVER'
            release_previous_after_reload(previous,DdrControl(pynq.MMIO(0x43c40000,4096)))
            save_new(output/'PREVIOUS_DDR_RELEASED.json',dict(previous_run=previous['run_id'],after_verified_reload=True))
        phase='DDR_ALLOCATION_AND_VALIDATION'
        print('DDR_PREPARE: allocating 91381760 bytes; neural computation not started',flush=True)
        memory=OwnedDdr(allocator,barrier,config['total_steps'])
    except Exception as error:
        save_new(output/'MEMORY_ADMISSION.json',dict(admission,status='PREPARATION_FAILED_NO_NEURAL_STEP',failed_phase=phase,error=str(error)))
        raise RuntimeError('DDR_PREPARATION_FAILED phase='+phase+'; overlay_loaded='+str(admission['overlay_loaded'])+
                           '; no neural control configuration or STEP; no automatic retry/reset; preserve this output') from error
    try:
        save_new(output/'MEMORY_ADMISSION.json',dict(admission,status='ALLOCATED_AND_VALIDATED',physical_base=memory.base))
        operator=live_context(ROOT,overlay,config,inventory)
        operator['barrier_library_sha256']=json.loads((output/'native/identity.json').read_text())['library_sha256']
        control=DdrControl(pynq.MMIO(0x43c40000,4096))
        require(all(control._r(a)==0 for a in (0x10,0x14,0x18,0x24)),'Fresh unused DDR candidate required')
        save_new(output/'OPERATOR.json',operator)
        result=run_window(control,memory,pc,config,operator,output)
        try:
            owner=complete_normal_return(control,memory,pc,config,operator,output,result)
            globals()['LINE2_COMPLETED_OWNER']=owner
        except BaseException as error:
            control.failed=True
            save_new(output/'CLOSEOUT_STOP.json',dict(status='IN_DOUBT_KEEP_KERNEL_AND_DDR_NO_RETRY',error=str(error)))
            raise
    finally:
        # Only our never-configured buffer may be reclaimed. Armed DDR stays pinned.
        if memory is not None and not memory.armed and not memory.released:
            memory.release_unarmed()
    pc.http.close()
    print('NORMAL_END_READY_FOR_NEXT · 本格已正常结束；可在原页面选择下一实验，再运行同一格，无需关闭内核。',flush=True)
    print(('LINE2_PURE_FPGA_SCIENTIFIC485_FINISHED ' if config.get('scientific_input') else 'LINE2_PURE_FPGA_CAMERA60_FINISHED ')+json.dumps({k:v for k,v in result.items() if k!='timing'}))


if __name__=='__main__':main()
