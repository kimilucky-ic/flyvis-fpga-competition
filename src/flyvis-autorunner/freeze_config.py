"""Freeze a new read-only baseline config. Refuses to overwrite an existing one."""
import argparse
import os
from pathlib import Path
from autorunner import HERE, SCHEMA, load_json, own_path, sha, write_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="configs/camera609.fast.json")
    args = p.parse_args()
    out = own_path(args.out)
    if out.exists():
        raise SystemExit("Existing config preserved")
    fpga = HERE.parent
    a = fpga / "flyvis-gpu-validation/phase4_camera_rectb_20261011"
    b = fpga / "flyvis-circuit-selection/phase4_camera_replacement_20261011_r1"
    bundle = a / "common_bundle"
    identity = load_json(bundle / "camera_backend_identity.json")
    sources = {"full": fpga.parent / "fly/gpu_phase2/full_oracle.py",
               "r_only": fpga.parent / "fly/gpu_phase2/r_only.py", "bound_r": b / "a_video_adapter.py",
               **{n: b / ("dependencies/b_core/" + n + ".py") for n in ("h_step", "coordinator", "gpu_adapter", "run_closed_loop")}}
    def relative(path):
        return os.path.relpath(path, HERE).replace("\\", "/")
    pins = {"bundle_manifest": bundle / "artifact_manifest.json",
            "a_handoff": a / "CAMERA_BACKEND_HANDOFF.json", "b_handoff": b / "B_CAMERA_609_HANDOFF.json",
            "a_receipt": a / "DELIVERY_ACCEPTANCE.json",
            "b_receipt": b / "artifacts/final_camera_audit_r2/result.json",
            "full_manifest": a / "artifacts/full_gpu_609_r1/artifact_manifest.json",
            "replacement_manifest": b / "artifacts/python_camera_609_r2/artifact_manifest.json",
            **{"source_" + n: path for n, path in sources.items()}}
    config = {"schema": SCHEMA, "mode": "fast", "experiment_id": identity["comparison_id"],
              "backend_binding_id": identity["backend_binding_id"], "bundle": relative(bundle),
              "fresh_full": False, "fresh_replacement": False, "affected_modules": ["scheduler"],
              "decoder": {"enabled": False, "status": "NOT_USED_PHASE1"},
              "scope": {"writes": True, "board": False, "steps": 609, "ablation": "NONE",
                        "gpu": {"authorized": False, "confirmed_by_user": False,
                                "authorization_reference": None, "start": None, "end": None,
                                "experiment_id": identity["comparison_id"], "steps": 609, "ablation": "NONE",
                                "conflict_free": False, "board_resources_reserved": False,
                                "max_invocations": {"FullGPU": 1, "PythonReplacement": 1}, "cache_keys": {}}},
              "runtime": {"kind": "wsl", "python": "/opt/flyvis-gpu-venv/bin/python",
                          "model_path": "/opt/flyvis-visual-experiments-data/results/flow/0000/000",
                          "checkpoint": "/opt/flyvis-visual-experiments-data/results/flow/0000/000/chkpts/chkpt_00000",
                          "busy_markers": ["runtime/EXTERNAL_GPU_BUSY.json", "runtime/BOARD_RESERVED.json"]},
              "timeouts": {"worker_s": 120, "queue_s": 120},
              "sources": {n: relative(path) for n, path in sources.items()},
              "pins": {n: {"path": relative(path), "sha256": sha(path)} for n, path in pins.items()},
              "accepted": {"FullGPU": {"root": relative(a / "artifacts/full_gpu_609_r1"),
                           "receipt": relative(a / "DELIVERY_ACCEPTANCE.json"),
                           "run_id": "8069326e-6838-41c2-b2f1-f75ff1d7b7e3"},
                           "PythonReplacement": {"root": relative(b / "artifacts/python_camera_609_r2"),
                           "receipt": relative(b / "artifacts/final_camera_audit_r2/result.json"),
                           "run_id": "e2dd3f0e-9c43-4268-b820-97465467cdba"}}}
    write_json(out, config)
    print(out)


if __name__ == "__main__":
    main()
