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
    require(config['schema']=='flyvis-line2-ddr-live-camera/v1' and config['duration_s']==60
            and config['total_steps']==485 and config['step_rate_limit_hz']==8
            and config['release_manifest_sha256']==MANIFEST_SHA,'LIVE_CAMERA_SCOPE')
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
                 evidence=record_evidence,board_result=False,mode='LIVE_CAMERA_FULL_NETWORK_FPGA')
    previous=INITIAL;chain='0'*64;timing=[];began=clock()
    try:
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
                    requested_wall_s=60,PC_window=request,board_loop_ns=clock()-began,input_setup_wait_ns=input_setup_ns,
                    model_time_s=len(timing)*.005,step_rate_limit_hz=8,
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


def main():
    require('--execute' in sys.argv and '--exclusive-board-window' in sys.argv,'Human execution/exclusive window required')
    # PC readiness can use 120s for CPU decoder plus 30s for first camera input.
    config=verify(ROOT);pc=PreparationClient(config);pc.http.timeout=180
    pc.post('/api/full-pl-stream/camera-ready',json.dumps({'preparation_id':config['preparation_id']}).encode(),'application/json')
    require(platform.machine()=='armv7l','Zynq ARMv7 only')
    import pynq
    require(str(pynq.__version__).startswith('2.7.'),'Prepared PYNQ2.7 only')
    require(b'xlnx,zynq-7000' in Path('/proc/device-tree/compatible').read_bytes(),'Zynq7000 only')
    inventory=exclusive_inventory()
    meminfo={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/meminfo').read_text().splitlines() if ':' in line}
    require('CmaFree' in meminfo and int(meminfo['CmaFree'].split()[0])*1024>=config['total_steps']*188416,
            'Insufficient reported CMA for485 complete snapshots; no load/allocation attempted')
    with (ROOT/'EXECUTION_STARTED.json').open('x',encoding='utf-8') as f:json.dump({'inventory':inventory},f)
    output=ROOT/'live_result';output.mkdir(exist_ok=False)
    overlay=pynq.Overlay(str(ROOT/'flyvis_ddr.bit'),download=False)
    overlay.download()
    operator=live_context(ROOT,overlay,config,inventory)
    from ddr_memory import OwnedDdr,pynq_allocator_and_barrier
    from ddr_control import DdrControl
    from ddr_acceptance import save_new
    allocator,barrier=pynq_allocator_and_barrier(output/'native',operator_authorized=True)
    operator['barrier_library_sha256']=json.loads((output/'native/identity.json').read_text())['library_sha256']
    control=DdrControl(pynq.MMIO(0x43c40000,4096))
    require(all(control._r(a)==0 for a in (0x10,0x14,0x18,0x24)),'Fresh unused DDR candidate required')
    memory=OwnedDdr(allocator,barrier,config['total_steps'])
    save_new(output/'OPERATOR.json',operator)
    result=run_window(control,memory,pc,config,operator,output)
    print('LINE2_PURE_FPGA_CAMERA60_FINISHED '+json.dumps({k:v for k,v in result.items() if k!='timing'}))


if __name__=='__main__':main()
