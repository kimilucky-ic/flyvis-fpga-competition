"""CPU-tested adapter only; caller admits combined BIT/HWH/HP1/DDR first.
No overlay load/reset. Vendor synchronous calls can block; no timeout claim.
"""
from pathlib import Path
import time
import step_profile as prof
import numpy as np
from capture_binding import BoundSteps, save_json, save_new
from ps_input import PsInput
from snapshot_records import decode_record


def start_official(overlay, AxiIIC, OV5640, VideoMode):
    """Same successful vendor calls; classes injected for CPU tests.
    No custom IIC/VDMA writes, LCD, retry or error cleanup.
    """
    iic = AxiIIC(overlay.ip_dict['cam_iic'])
    sensor = OV5640(0x3c, iic)
    sensor.init()
    sensor.set_outsize(800, 480, 1800, 1000)
    video = overlay.video.video_in
    video.configure(VideoMode(800, 480, 24))
    video.start()
    return sensor, video


class OfficialBridge:
    """Single producer. Copy readframe before freebuffer, bind before STEP.
    Readout ordinal is not a sensor exposure counter. Unselected camera frames
    may be skipped; neural steps and their audit records must not be skipped.
    """
    def init__(self, video, control, memory, output, capacity,
                 evidence='CPU_MOCK_ONLY'):
        if evidence not in ('CPU_MOCK_ONLY', 'OPERATOR_PHYSICAL_RUN_UNATTESTED'):
            raise ValueError('explicit evidence required')
        self.video, self.control, self.memory = video, control, memory
        self.output = Path(output)
        self.output.mkdir(exist_ok=False)
        self.binding = BoundSteps(self.output/'bound', capacity)
        self.mapper = PsInput(height=480, width=800, channel_order='BGR')
        self.failed = False
        self.closed = False
        self.held_frame = None
        self.next_readout = 0
        self.last_record_bytes = None
        save_json(self.output/'PROFILE.json', dict(
            schema='line11-official-bridge/v1', evidence=evidence,
            width=800, height=480, channels=3, channel_order='BGR',
            color_order_physically_verified=False, input_words=721,
            nodes=45669, edges=1513231, neural_clock_target_hz=100000000,
            neural_arithmetic='UNCHANGED_STRICT_FP32',
            camera_path='VENDOR_PYNQ27_VIDEO2LCD_READFRAME',
            source_id_definition='readframe return ordinal, not exposure counter',
            timestamp_definition='PS monotonic after readframe; not exposure time',
            mapping='unchanged PsInput full-field letterbox, 800x480 BGR',
            mapping_is_bitwise_torch=False, capacity=capacity, automatic_retry=False))

    def step(self):
        if self.failed or self.closed:
            raise RuntimeError('session stopped; no automatic retry')
        if self.binding.next >= self.binding.capacity:
            raise RuntimeError('audit capacity reached before capture or STEP')
        phase = 'READFRAME'
        try:
            self.held_frame = self.video.readframe()
            stamp = time.monotonic_ns()
            phase = 'COPY_FRAME'
            a = np.asarray(self.held_frame)
            if a.dtype != np.uint8 or a.shape != (480, 800, 3):
                raise ValueError('official 800x480 uint8 frame required')
            _copy_start=prof.tick()
            raw = a.tobytes(order='C')  # immutable; no DMA-buffer view retained
            prof.add('camera_immutable_copy',_copy_start,len(raw))
            phase = 'RELEASE_COPIED_FRAME'
            self.held_frame.freebuffer()
            self.held_frame = None
            ordinal = self.next_readout
            self.next_readout += 1
            phase = 'BIND_AND_STEP'

            def render(blob):
                frame = np.frombuffer(blob, dtype=np.uint8).reshape(480, 800, 3)
                return self.mapper.render(frame).astype('<f4').tobytes()

            def fetch(descriptor):
                data = self.memory.copy_record(descriptor)
                try:
                    _decode_start=prof.tick();record = decode_record(data, self.binding.next)
                    prof.add('ddr_record_decode',_decode_start,len(data))
                    if record.cycles != descriptor.cycles:raise RuntimeError('DDR descriptor/record cycle mismatch')
                except BaseException:
                    save_new(self.output/'bound'/('%06d'%descriptor.frame_id)/'RETURNED_UNCOMMITTED.bin',data)
                    raise
                self.last_record_bytes = data
                return record,data

            return self.binding.step((ordinal, stamp, raw), render,
                                     self.control.advance, fetch)
        except BaseException as exc:
            self.failed = True
            try:
                save_json(self.output/'STOPPED.json', dict(
                    phase=phase, error=repr(exc), next_step=self.binding.next,
                    automatic_retry=False, automatic_cleanup=False))
            except BaseException:
                pass
            raise  # retain hardware state and any still-held frame

    def close_success(self):
        if self.failed or self.closed or self.held_frame is not None:
            raise RuntimeError('no cleanup on failed/closed/held session')
        try:
            self.video.close()
            self.closed = True
        except BaseException:
            self.failed = True
            raise
