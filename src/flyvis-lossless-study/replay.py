"""Fresh-process replay using only compact template, input and per-step expected hashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["NUMBA_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
import numpy as np
from codec import read_template
from engine import Engine


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = args.output.resolve()
    if root not in output.parents or output.exists():
        raise ValueError("Replay report must be new and inside this package")
    manifest = json.loads((root / "payload_manifest.json").read_text())
    for name, expected in manifest.items():
        path = (root / name).resolve()
        if root not in path.parents or sha(path) != expected:
            raise ValueError(f"Payload identity differs: {name}")
    engine = Engine(read_template(root / "flyvis_template.bin"))
    inputs = np.load(root / "stimulus.npy", allow_pickle=False)
    expected = json.loads((root / "expected_state_hashes.json").read_text())
    if len(expected) != len(inputs):
        raise ValueError("Step count differs")
    start = time.perf_counter()
    for i, stimulus in enumerate(inputs):
        actual = hashlib.sha256(engine.advance(stimulus).tobytes()).hexdigest()
        if actual != expected[i]:
            raise AssertionError(f"State hash mismatch at step {i+1}: {actual}")
    forbidden = {name for name in sys.modules if name == "torch" or name == "flyvis" or name == "reference"}
    assert not forbidden, forbidden
    report = dict(status="PASS_FRESH_PROCESS_COMPACT_ONLY_SELF_FEEDBACK", steps=len(inputs),
                  compared_state_values=len(inputs)*engine.t["n"], self_feedback_transitions=len(inputs)-1,
                  state_hashes_match_every_step=True, final_state_sha256=expected[-1],
                  elapsed_s_including_jit=time.perf_counter()-start, expanded_edge_file_used=False,
                  original_graph_or_checkpoint_used=False, torch_imported=False, flyvis_imported=False,
                  evidence_level="CPU software only; not FPGA or board execution")
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
