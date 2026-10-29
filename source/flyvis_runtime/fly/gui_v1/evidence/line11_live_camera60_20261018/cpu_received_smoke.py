"""One bounded CPU-only smoke of the NEW pipe with saved original 3-step arrays."""
import json
from pathlib import Path
import sys
import threading
import time
import numpy as np

OUT=Path(__file__).resolve().parent
HERE=OUT.parents[1];sys.path.insert(0,str(HERE))
from line11_live_cpu import LiveCPUConsumer
from line11_ddr_bridge import verify_release,record_codec,digest

root,files=verify_release();codec=record_codec(root,files)
records=(root/'cpu_fixture_ddr.bin').read_bytes()
destination=OUT/'actual_cpu_worker_r2'
received=[];completed=threading.Event()
def callback(snapshot,flow):
    m=snapshot[0];assert flow['binding']['frame_id']==m['frame_id']
    assert flow['binding']['numerical_audit']=='FULL_STATE_BIT_EXACT'
    assert flow['binding']['device']=='cpu'
    received.append(flow['binding'])
    if len(received)==3:completed.set()
consumer=LiveCPUConsumer(destination,callback)
started=time.monotonic();consumer.start()
try:
    assert consumer.ready.wait(90) and not consumer.error,consumer.error or 'CPU worker ready timeout'
    print('CPU_ONLY_READY',flush=True)
    for k in range(3):
        record=codec.decode_record(records[k*188416:(k+1)*188416],k)
        meta=dict(run_id='CPU_SAVED_THREE_STEP_SMOKE',session_id='CPU_ONLY_NO_BOARD',frame_id=k,
                  state_sha256=record.state_sha256,input_sha256=record.input_sha256)
        consumer.submit((meta,record.input_bits,record.state_bits,time.perf_counter_ns(),None))
    consumer.finish_input()
    assert completed.wait(45),consumer.error or 'CPU decode/audit timeout'
    consumer.thread.join(10)
    assert not consumer.thread.is_alive() and consumer.state=='COMPLETE' and not consumer.error,consumer.status()
    result=dict(status='PASS_SAVED_THREE_STEP_CPU_REFERENCE_AND_OFFICIAL_DECODER_PIPE',
        evidence='CPU_ONLY_SAVED_ARRAYS_NO_NEW_CAMERA_OR_BOARD',frames=len(received),
        full_state_bit_comparisons=3*45669,CUDA_initialized=False,
        elapsed_s=time.monotonic()-started,bindings=received,worker_status=consumer.status())
    (OUT/'CPU_RECEIVED_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','frames','elapsed_s')}),flush=True)
finally:consumer.close()
