# Phase 3 fixed-input consumer

This lane only publishes already frozen sample1 and animation a0 identities. No camera/GPU/RTL backend is added.
[Delivery and dependencies — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-114), [machine contract — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-115), [acceptance — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-116).

From `C:\Users\hzy72\Documents\ChatGPT\fly`:

```powershell
& .\.venv\Scripts\python.exe camera_pipeline\phase3_input_20261010_r1\identity.py --verify
& .\.venv\Scripts\python.exe camera_pipeline\phase3_input_20261010_r1\test_handoff.py
& .\.venv\Scripts\python.exe camera_pipeline\phase3_input_20261010_r1\finalize.py --verify
```

The same consumer works in the existing WSL environment without importing torch or loading a network:

```powershell
wsl -d FlyVisCPU -- /opt/flyvis-gpu-venv/bin/python /mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/phase3_input_20261010_r1/identity.py --verify
```

Python API, with `fly` on the Python import path:

```python
from camera_pipeline.phase3_input_20261010_r1.identity import load_bundle
bundle = load_bundle()  # optionally expected_identity_sha256 from the delivered acceptance.json
x = bundle['x']        # read-only float32 [800,721]; original sample1 bytes
a0 = bundle['a0']      # read-only float32 [45669]; exact animation initial state
input_time = bundle['input_time']
activity_time = bundle['activity_time']  # input_time + .005, post-update a[k+1]
```

The identity JSON records canonical Windows paths. The consumer resolves them relative to its own camera_pipeline module directory,
checks that each recorded path corresponds to the expected artifact, and verifies the exact files on Windows or WSL /mnt/c.
File SHA, C-order numeric payload SHA, and dtype+shape+payload tensor SHA are explicitly separated.
Actual source remains640×640/60Hz; model dt=.005/200 steps per second is not a wall-clock throughput promise.

Generation `identity.py --build` was performed once. It refuses to overwrite its identity or alignment outputs. Do not rerun preprocessing.
No full-network per-step trace is invented from the historical65-center-node results. A/B own strict-comparison state/parameter identity;
B owns SOURCE_RAW H inputs, and C owns RTL/SoC/live PL. Future quantized a0 requires a new comparison_id and all-mode reruns.

Reusable scope is this pinned input and Windows/WSL identity pattern; no general hardware Skill is claimed or published.
