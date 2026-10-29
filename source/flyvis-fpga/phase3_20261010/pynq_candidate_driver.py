"""Prepared AXI driver; no Overlay/download/reset/network code or board calls on import.

This transports raw activity and reads PL candidates. Integration with HResult's
missing chemical diagnostic and coordinator identity/COMMIT remains under review.
"""
from dataclasses import dataclass
import threading
import time
import numpy as np


class HardwareNotReady(RuntimeError):
    pass


@dataclass(frozen=True)
class Candidate:
    new_h: np.ndarray
    request_digest: str
    compute_cycles: int
    profile: str = 'Q6.22_weight_Q1.20'
    chemical_diagnostic: object = None
    committed: bool = False


def quantize_request(boundary, old_h, x_h):
    values = []
    for name, value, count in [('boundary', boundary, 1364), ('old_h', old_h, 67), ('x_h', x_h, 67)]:
        array = np.asarray(value, dtype=np.float64)
        if array.shape != (count,) or not np.isfinite(array).all():
            raise ValueError(f'{name}: expected {count} finite values')
        scaled = array * (1 << 22)
        quantized = np.copysign(np.floor(np.abs(scaled) + 0.5), scaled)
        if (quantized < -(1 << 28)).any() or (quantized >= (1 << 28)).any():
            raise OverflowError(f'{name}: Q6.22 range exceeded')
        values.append(quantized.astype(np.int32))
    return np.concatenate(values)


class SourceRawAxiDriver:
    """Requires an existing MMIO object and explicit board-I/O authorization.

    The caller must verify the full .bit/.hwh/coefficient manifest before enabling
    this driver. Its identity registers alone do not attest to a bitstream SHA.
    This prepared driver has not been executed against a board.
    """
    def init__(self, mmio, *, board_io_authorized=False, overlay_identity_verified=False):
        self.mmio = mmio
        self.authorized = board_io_authorized and overlay_identity_verified
        self.poisoned = False
        self.seen = set()
        self.lock = threading.Lock()

    def compute_candidate(self, boundary, old_h, x_h, *, request_digest, timeout_s=1.0):
        if not self.authorized:
            raise HardwareNotReady('NOT_READY: board I/O authorization and overlay identity verification required')
        if self.poisoned:
            raise HardwareNotReady('NOT_READY: prior hardware/transport failure; explicit recovery required')
        if not isinstance(request_digest, str) or len(request_digest) != 64 or any(c not in '0123456789abcdef' for c in request_digest):
            raise ValueError('A full canonical lowercase SHA256 request digest is required')
        if timeout_s <= 0 or not np.isfinite(timeout_s):
            raise ValueError('A finite positive timeout is required')
        words = quantize_request(boundary, old_h, x_h)
        if not self.lock.acquire(blocking=False):
            raise HardwareNotReady('Only one request may be in flight')
        try:
            if request_digest in self.seen:
                raise HardwareNotReady('Duplicate request rejected; no implicit replay/COMMIT')
            identity = [(0, 0x46565333), (4, 0x0616141d), (8, 67), (12, 1364),
                        (16, 6537), (20, 1498), (40, 0x04cc0571), (44, 1)]
            for register, required in identity:
                if self.mmio.read(register) != required:
                    raise HardwareNotReady(f'PL identity/profile mismatch at {register:#x}')
            if self.mmio.read(0x24) & 1:
                raise HardwareNotReady('PL is already busy; request was not started')
            self.seen.add(request_digest)
            deadline = time.monotonic() + timeout_s
            self.mmio.write(0x20, 1)
            for i, word in enumerate(words):
                if time.monotonic() >= deadline:
                    raise TimeoutError('Raw request upload timed out')
                self.mmio.write(0x1000 + i*4, int(word) & 0xffffffff)
            self.mmio.write(0x20, 2)
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError('PL completion timed out')
                flags = self.mmio.read(0x24)
                if flags & 2:
                    break
            fault = self.mmio.read(0x1c)
            if fault or not (flags & 4):
                raise HardwareNotReady(f'PL discarded candidate: status={fault:#x}, flags={flags:#x}')
            raw = np.asarray([self.mmio.read(0x4000 + h*4) for h in range(67)], dtype=np.uint32)
            upper = raw >> np.uint32(29)
            required_upper = np.where((raw & np.uint32(1 << 28)) != 0, 7, 0)
            if not np.array_equal(upper, required_upper):
                raise HardwareNotReady('Malformed PL output: invalid Q29 sign extension')
            if time.monotonic() >= deadline:
                raise TimeoutError('Candidate read timed out')
            new_h = (raw.view(np.int32).astype(np.float64)/(1 << 22)).astype(np.float32)
            new_h.flags.writeable = False
            return Candidate(new_h, request_digest, self.mmio.read(0x18))
        except (TimeoutError, OSError, HardwareNotReady):
            self.poisoned = True
            raise
        finally:
            self.lock.release()
