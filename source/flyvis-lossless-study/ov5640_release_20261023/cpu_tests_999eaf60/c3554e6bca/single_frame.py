"""One captured frame -> durable actual input -> one PL step. Injectable, no hardware imports."""
from pathlib import Path
import time
import numpy as np
from capture_binding import BoundSteps,save_new,save_json
from ps_input import PsInput
from snapshot_records import decode_record

def capture_and_step(capture,pool,control,memory,output,channel_order='BGR',timestamp_ns=None):
    session=BoundSteps(output,1,first_step=0)
    mapper=PsInput(channel_order=channel_order)
    stamp=time.monotonic_ns() if timestamp_ns is None else timestamp_ns
    token=capture.capture(0,stamp)
    if token is None:raise RuntimeError('No capture lease; no neural STEP')
    def render(raw):
        return mapper.render(np.frombuffer(raw,dtype=np.uint8).reshape(480,640,3)).astype('<f4').tobytes()
    def fetch(descriptor):
        raw=memory.copy_record(descriptor)
        save_new(Path(output)/'000000'/'record.bin',raw)
        record=decode_record(raw,0)
        if record.cycles!=descriptor.cycles:raise RuntimeError('Descriptor/record cycle mismatch')
        return record
    descriptor=session.process_latest(pool,render,control.advance,fetch)
    if descriptor is None:raise RuntimeError('No completed capture; no neural STEP')
    result=dict(status='ONE_FRAME_ONE_STEP_SAVED_ORACLE_PENDING',completed_steps=1,
        source_frame_id=0,neural_step_id=descriptor.frame_id,sequence=descriptor.sequence,
        cycles=descriptor.cycles,channel_order=channel_order,input_words=721,state_words=45669,
        timestamp_definition='PS monotonic capture request; NOT exposure timestamp',
        board_result=False,full_state_verified=False)
    save_json(Path(output)/'CAPTURE_RESULT.json',result)
    return result
