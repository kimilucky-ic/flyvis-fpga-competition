"""Fail-closed PYNQ bridge for the V1 FlyVis HLS pointer ABI.

Importing this module never opens an overlay or writes to a board. The
``board-run`` command requires exact BIT and HWH digests reviewed by the
operator, then programs that release and runs only PL-computed requests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

STATE_WORDS = 1498
OUTPUT_WORDS = 67
TOTAL_REPLAY_STEPS = 800
CTRL = 0x00
AP_RETURN = 0x10
REQUEST_LO = 0x18
REQUEST_HI = 0x1C
RESULT_LO = 0x24
RESULT_HI = 0x28
AP_START = 1 << 0
AP_DONE = 1 << 1
TIMEOUT_SECONDS = 30.0


class FlyVisBoardFault(RuntimeError):
    """A transport, HLS status, mapping, timeout, or numerical failure."""


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_release(release_dir: Path) -> Tuple[Dict[str, Any], Path, Path]:
    release_dir = release_dir.resolve()
    manifest_path = release_dir / "release_manifest.json"
    if not manifest_path.is_file():
        raise FlyVisBoardFault("Release manifest is missing; no board action is allowed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "FULL_SOC_BIT_HWH_READY_BOARD_NOT_AUTHORIZED":
        raise FlyVisBoardFault("Release status is not a reviewed full-SoC BIT/HWH candidate")
    bit_entry = manifest.get("files", {}).get("bitstream", {})
    hwh_entry = manifest.get("files", {}).get("hwh", {})
    bit_path = release_dir / bit_entry.get("path", "")
    hwh_path = release_dir / hwh_entry.get("path", "")
    if not bit_path.is_file() or not hwh_path.is_file():
        raise FlyVisBoardFault("BIT/HWH pair is incomplete")
    if sha_file(bit_path) != bit_entry.get("sha256"):
        raise FlyVisBoardFault("BIT digest does not match the release manifest")
    if sha_file(hwh_path) != hwh_entry.get("sha256"):
        raise FlyVisBoardFault("HWH digest does not match the release manifest")
    return manifest, bit_path, hwh_path


def verify_fixture(release_dir: Path, manifest: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    vectors_dir = release_dir / "vectors"
    req_path = vectors_dir / "requests_i32le.bin"
    exp_path = vectors_dir / "expected_i32le.bin"
    fixture_path = vectors_dir / "fixture_manifest.json"
    for path in (req_path, exp_path, fixture_path):
        if not path.is_file():
            raise FlyVisBoardFault("Required immutable reference vector is missing: " + str(path))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    expected_identity = manifest["fixture_identity"]
    if sha_file(req_path) != expected_identity["request_sha256"]:
        raise FlyVisBoardFault("Request vector digest mismatch")
    if sha_file(exp_path) != expected_identity["expected_sha256"]:
        raise FlyVisBoardFault("Integer-oracle vector digest mismatch")
    if fixture.get("comparison_id") != expected_identity.get("comparison_id"):
        raise FlyVisBoardFault("Fixed-animation comparison identity mismatch")
    requests = np.fromfile(str(req_path), dtype="<i4")
    expected = np.fromfile(str(exp_path), dtype="<i4")
    request_shape = tuple(expected_identity["request_shape"])
    expected_shape = tuple(expected_identity["expected_shape"])
    if request_shape != (801, STATE_WORDS) or expected_shape != (801, OUTPUT_WORDS):
        raise FlyVisBoardFault("Reference vector shape is not the sealed 800-step plus control package")
    if requests.size != request_shape[0] * request_shape[1] or expected.size != expected_shape[0] * expected_shape[1]:
        raise FlyVisBoardFault("Reference vector byte count mismatch")
    requests = requests.reshape(request_shape)
    expected = expected.reshape(expected_shape)
    validate_q22_sign_extension(requests)
    return requests, expected, fixture


def validate_q22_sign_extension(values: np.ndarray) -> None:
    u = np.asarray(values, dtype="<i4").view("<u4")
    sign = (u & np.uint32(0x10000000)) != 0
    upper = u & np.uint32(0xE0000000)
    invalid = np.where(sign, upper != np.uint32(0xE0000000), upper != 0)
    if np.any(invalid):
        raise FlyVisBoardFault("Q6.22 input contains non-sign-extended 29-bit state words")


def buffer_address(buffer: Any) -> int:
    if hasattr(buffer, "device_address"):
        return int(buffer.device_address)
    if hasattr(buffer, "physical_address"):
        return int(buffer.physical_address)
    raise FlyVisBoardFault("PYNQ allocated buffer exposes no physical/device address")


def sync_to_device(buffer: Any) -> None:
    if hasattr(buffer, "flush"):
        buffer.flush()
    elif hasattr(buffer, "sync_to_device"):
        buffer.sync_to_device()
    else:
        raise FlyVisBoardFault("PYNQ buffer cannot flush CPU-written data")


def sync_from_device(buffer: Any) -> None:
    if hasattr(buffer, "invalidate"):
        buffer.invalidate()
    elif hasattr(buffer, "sync_from_device"):
        buffer.sync_from_device()
    else:
        raise FlyVisBoardFault("PYNQ buffer cannot invalidate PL-written data")


def write_load_failure(output_dir: Path, manifest: Dict[str, Any], error: Exception,
                       stage: str) -> None:
    report = {
        "status": "FAIL_CLOSED_BOARD_LOAD_OR_ABI",
        "evidence_level": "LIVE_BOARD_OPERATION_ATTEMPT; NO_COMPUTE_PASS",
        "stage": stage,
        "error": f"{type(error).__name__}: {error}",
        "firmware_identity": {
            "bit_sha256": manifest.get("files", {}).get("bitstream", {}).get("sha256"),
            "hwh_sha256": manifest.get("files", {}).get("hwh", {}).get("sha256"),
            "pl_readback_attestation": False,
        },
        "python_fallback": False,
        "board_state_after_attempt": "UNKNOWN; inspect live board before any further action",
    }
    (output_dir / "board_run.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


class FlyVisV1Driver:
    """Single-request PL driver; it never commits or computes on the CPU."""

    def init__(self, overlay: Any, manifest: Dict[str, Any], mmio: Any,
                 allocate_fn: Any, np_module: Any = np,
                 timeout_seconds: float = TIMEOUT_SECONDS) -> None:
        self.overlay = overlay
        self.manifest = manifest
        self.mmio = mmio
        self.allocate = allocate_fn
        self.np = np_module
        self.timeout_seconds = timeout_seconds
        self.identity = {
            "bit_sha256": manifest["files"]["bitstream"]["sha256"],
            "hwh_sha256": manifest["files"]["hwh"]["sha256"],
            "soc_release_status": manifest["status"],
            "pl_readback_attestation": False,
        }

    def step(self, request_q22_i32: np.ndarray) -> Dict[str, Any]:
        """Compute one H.step on PL and return an uncommitted candidate.

        Request order is boundary[1364], old_H[67], x_H[67]. No chemical
        currents or precomputed new_H values are accepted by this interface.
        """
        request = np.asarray(request_q22_i32, dtype="<i4").reshape(-1)
        if request.size != STATE_WORDS:
            raise FlyVisBoardFault("PL request must contain exactly 1498 signed Q6.22 words")
        validate_q22_sign_extension(request)

        inp = self.allocate(shape=(STATE_WORDS,), dtype=self.np.dtype("<i4"))
        out = self.allocate(shape=(OUTPUT_WORDS,), dtype=self.np.dtype("<i4"))
        try:
            inp[:] = request
            out[:] = 0x5A5A5A5A
            sync_to_device(inp)
            sync_to_device(out)
            in_addr = buffer_address(inp)
            out_addr = buffer_address(out)
            self.mmio.write(REQUEST_LO, in_addr & 0xFFFFFFFF)
            self.mmio.write(REQUEST_HI, (in_addr >> 32) & 0xFFFFFFFF)
            self.mmio.write(RESULT_LO, out_addr & 0xFFFFFFFF)
            self.mmio.write(RESULT_HI, (out_addr >> 32) & 0xFFFFFFFF)
            self.mmio.write(CTRL, AP_START)

            deadline = time.monotonic() + self.timeout_seconds
            done = False
            while time.monotonic() < deadline:
                control = int(self.mmio.read(CTRL))
                if control & AP_DONE:
                    done = True
                    break
                time.sleep(0.0005)
            if not done:
                raise FlyVisBoardFault("HLS AP_DONE timeout; no retry or CPU fallback was attempted")

            status = int(self.mmio.read(AP_RETURN))
            sync_from_device(out)
            candidate = np.asarray(out, dtype="<i4").copy()
            if status != 0:
                raise FlyVisBoardFault(f"HLS returned non-zero fail-closed status 0x{status:08x}")
            validate_q22_sign_extension(candidate)
            candidate_bytes = candidate.tobytes(order="C")
            return {
                "status": status,
                "candidate_h_q22_i32": candidate,
                "candidate_sha256": sha_bytes(candidate_bytes),
                "request_sha256": sha_bytes(request.tobytes(order="C")),
                "firmware_identity": dict(self.identity),
                "committed": False,
                "state_semantics": "stateless STEP with explicit old_H; caller/coordinator owns unified COMMIT",
                "compute_owner": "FPGA_PL_HLS",
            }
        finally:
            for buffer in (out, inp):
                free = getattr(buffer, "freebuffer", None)
                if callable(free):
                    free()
                else:
                    close = getattr(buffer, "close", None)
                    if callable(close):
                        close()


def run_board(args: argparse.Namespace) -> Dict[str, Any]:
    release_dir = args.release_dir.resolve()
    manifest, bit_path, _hwh_path = load_release(release_dir)
    bit_sha = manifest["files"]["bitstream"]["sha256"]
    hwh_sha = manifest["files"]["hwh"]["sha256"]
    if args.authorize_bit_sha256 != bit_sha or args.authorize_hwh_sha256 != hwh_sha:
        raise FlyVisBoardFault("Board write blocked: provide the exact reviewed BIT and HWH SHA-256 values")
    if args.steps not in (1, 32, 800) or args.start_step < 0 or args.start_step + args.steps > TOTAL_REPLAY_STEPS:
        raise FlyVisBoardFault("Allowed request spans are 1, 32, or 800 rows within steps 0..799")

    # Complete all disk/vector checks and reserve the evidence path before any
    # Overlay constructor can reconfigure the PL.
    requests, expected, fixture = verify_fixture(release_dir, manifest)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)

    # Importing PYNQ and creating Overlay is the first board-state operation.
    from pynq import Overlay, allocate
    try:
        import pynq
        pynq_version: Optional[str] = getattr(pynq, "__version__", None)
    except Exception:
        pynq_version = None
    from pynq.mmio import MMIO

    try:
        overlay = Overlay(str(bit_path), download=True)
        ip_dict = getattr(overlay, "ip_dict", {})
        ip = ip_dict.get("flyvis_h")
        if not isinstance(ip, dict):
            raise FlyVisBoardFault("Loaded HWH has no top-level flyvis_h IP metadata")
        expected_vlnv = manifest["hwh_instances"]["flyvis_h"].get("VLNV")
        if ip.get("type") and ip.get("type") != expected_vlnv:
            raise FlyVisBoardFault(f"Loaded IP type mismatch: {ip.get('type')} != {expected_vlnv}")
        expected_base = int(manifest["control_register_map"]["base_address"], 16)
        base = int(ip.get("phys_addr", -1))
        span = int(ip.get("addr_range", 0))
        if base != expected_base or span < 65536:
            raise FlyVisBoardFault(f"HWH register map mismatch: base=0x{base:x} range=0x{span:x}")
        mmio = MMIO(base, span)
    except Exception as exc:
        write_load_failure(output_dir, manifest, exc, "overlay download or HWH/IP identity check")
        raise
    driver = FlyVisV1Driver(overlay, manifest, mmio, allocate)
    outputs = np.zeros((args.steps, OUTPUT_WORDS), dtype="<i4")
    rows = []
    failure: Optional[str] = None
    for out_index, step_index in enumerate(range(args.start_step, args.start_step + args.steps)):
        try:
            response = driver.step(requests[step_index])
            candidate = response["candidate_h_q22_i32"]
            oracle = expected[step_index]
            equal = bool(np.array_equal(candidate, oracle))
            candidate_bytes = candidate.tobytes(order="C")
            outputs[out_index] = candidate
            row = {
                "step_id": step_index,
                "request_sha256": response["request_sha256"],
                "pl_output_sha256": response["candidate_sha256"],
                "integer_oracle_sha256": sha_bytes(oracle.tobytes(order="C")),
                "status": response["status"],
                "exact_integer_match": equal,
                "compute_owner": response["compute_owner"],
                "committed": False,
            }
            rows.append(row)
            if not equal:
                failure = f"Integer oracle mismatch at step {step_index}"
                break
        except Exception as exc:
            failure = f"PL step {step_index} failed closed: {type(exc).__name__}: {exc}"
            rows.append({"step_id": step_index, "failed_closed": True, "error": failure})
            break

    output_path = output_dir / "PL_outputs_i32le.bin"
    output_path.write_bytes(outputs[:len(rows) - (1 if rows and rows[-1].get("failed_closed") else 0)].tobytes(order="C"))
    report = {
        "status": "PASS_BOARD_HLS_STEP_INTEGER_ORACLE" if failure is None and len(rows) == args.steps else "FAIL_CLOSED",
        "evidence_level": "LIVE_BOARD_PYNQ_AND_PHYSICAL_PL_EXECUTION" if failure is None else "LIVE_BOARD_ATTEMPT_FAILED_CLOSED",
        "design": "FlyVis T5c 67 SOURCE_RAW Q22; 6537 HH/RH edges computed in PL",
        "fixture_comparison_id": fixture["comparison_id"],
        "replay_semantics": "Reference old_H is supplied independently for every recorded step; this does not claim a live closed loop.",
        "state_commit": "none; returned H values are candidate outputs only",
        "requested_steps": args.steps,
        "completed_steps": sum(1 for row in rows if row.get("exact_integer_match")),
        "start_step": args.start_step,
        "pynq_version": pynq_version,
        "platform": platform.platform(),
        "firmware_identity": {"bit_sha256": bit_sha, "hwh_sha256": hwh_sha,
                              "pl_readback_attestation": False},
        "request_file_sha256": sha_file(release_dir / "vectors" / "requests_i32le.bin"),
        "oracle_file_sha256": sha_file(release_dir / "vectors" / "expected_i32le.bin"),
        "pl_output_file": str(output_path),
        "pl_output_sha256": sha_file(output_path),
        "steps": rows,
        "failure": failure,
        "scientific_acceptance": fixture["scientific_acceptance"],
    }
    report_path = output_dir / "board_run.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failure is not None:
        raise FlyVisBoardFault(failure)
    return report


def preflight(args: argparse.Namespace) -> Dict[str, Any]:
    release_dir = args.release_dir.resolve()
    manifest, bit_path, hwh_path = load_release(release_dir)
    requests, expected, fixture = verify_fixture(release_dir, manifest)
    result = {
        "status": "PASS_LOCAL_RELEASE_PREFLIGHT_NO_BOARD_IO",
        "bit_sha256": sha_file(bit_path),
        "hwh_sha256": sha_file(hwh_path),
        "requests_shape": list(requests.shape),
        "expected_shape": list(expected.shape),
        "comparison_id": fixture["comparison_id"],
        "board_io_operations": 0,
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pf = sub.add_parser("preflight", help="verify a local release without board access")
    pf.add_argument("--release-dir", required=True, type=Path)
    run = sub.add_parser("board-run", help="load exact authorized release and execute PL requests")
    run.add_argument("--release-dir", required=True, type=Path)
    run.add_argument("--steps", required=True, type=int, choices=(1, 32, 800))
    run.add_argument("--start-step", type=int, default=0)
    run.add_argument("--authorize-bit-sha256", required=True)
    run.add_argument("--authorize-hwh-sha256", required=True)
    run.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            preflight(args)
        else:
            run_board(args)
    except Exception as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": f"{type(exc).__name__}: {exc}",
                          "python_fallback": False}, indent=2), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
