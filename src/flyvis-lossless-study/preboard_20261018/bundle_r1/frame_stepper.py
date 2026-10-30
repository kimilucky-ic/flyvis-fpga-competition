"""Synchronous one-input / one-network-step / one-display-update protocol.

No hardware imports or connection. A separately authorized caller provides a
ready driver and a display callback. No rendering, neural math, reset, frame
dropping, catch-up steps, or model-time resampling is performed here.
"""
from dataclasses import dataclass
import time

@dataclass(frozen=True)
class DisplayFrame:
    frame_id: int
    input_bits: bytes
    state_bits: bytes
    completed_steps: int
    compute_cycles: int
    elapsed_seconds: float

class FrameStepper:
    def init__(self,driver,display):
        self.driver=driver
        self.display=display
        self.next_frame_id=0
        self.failed=False
        self.active=False

    def advance(self,frame_bits,timeout=None):
        if self.failed:raise RuntimeError('Previous frame failed; reconcile state before creating a new session')
        if self.active:raise RuntimeError('A frame is already in progress')
        payload=bytes(frame_bits)
        if len(payload)!=721*4:raise ValueError('Expected 721 FP32 input words')
        self.active=True
        start=time.monotonic()
        try:
            self.driver.load_frame_bits(payload)
            info=self.driver.run_steps(1,timeout=timeout)
            state=bytes(self.driver.read_state_bits())
            if len(state)!=45669*4:raise RuntimeError('Incomplete full-network readback')
            packet=DisplayFrame(self.next_frame_id,payload,state,info['completed_steps'],
                info['last_cycles'],time.monotonic()-start)
            self.display(packet)
            self.next_frame_id+=1
            return packet
        except Exception:
            # Advancing PL state and displaying it are not an atomic operation.
            # Stop on either failure; never silently repeat a neural step.
            self.failed=True
            raise
        finally:self.active=False
