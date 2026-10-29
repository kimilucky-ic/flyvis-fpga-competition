# FlyVis Phase 2: full a0 and stateless R-only service

2026-10-10. This directory belongs to the original FlyVis GPU/software workline.
All new files remain under C:\Users\hzy72\Documents\ChatGPT\fly\gpu_phase2.
Official model, checkpoint, dynamics and connections are unchanged. Controller/B files are read-only.

## Entry points

- R production API: r_only.py → RStepService.step.
- Optional original Full comparison: full_oracle.py → FullNetworkOracle.step.
- Independently executable consumer: example_call.py.
- Frozen inputs: artifacts/reference_bundle_v1/.
- CPU completed acceptance: artifacts/r_only_cpu_r3/acceptance.json.
- CPU complete recorded arrays: artifacts/r_only_cpu_r2/{full_activity.npy,r_activity.npy}. The original r2 test stopped at a Python instrumentation assertion; final replay acceptance is r3. Their raw-array stream hashes are independently checked before final handoff.
- GPU acceptance artifacts/r_only_gpu_r2/acceptance.json and cross-device/initial replay reports are listed in handoff.json when completed.
- This service is a local synchronous Python callable. It does not implement the v0.1 PC–PS transport or joint H/R commit coordinator.

## Canonical model and initial state

Model flow/0000/000, FlyVis 1.2.0, source commit 92b3845cc426dd309a1a0e1b3890156c42e14021.
Checkpoint SHA256 d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f.
45,669 nodes; 1,513,231 original edges; PPNeuronIGRSynapses with presynaptic ReLU.

initial_state_full.npy is little-endian float32 [45669], in global-node order 0..45668.
It is the actual final state from unchanged Network.steady_state(1.0,0.005,1,value=0.5,return_last=False):
official bias initialization followed by 200 gray-adaptation updates. It is not a bias, zero or local-H array.
Two independent CPU processes produce identical bytes. The canonical file SHA256 is
e1ca6d82b262088afff135418e5bf90bc3ceabc8e584e91d4c2047539805145f.
Load this same canonical a0 into CPU and GPU comparisons; do not independently adapt each comparison mode.
warmup_activity_full.npy for all 200 steps is retained in artifacts/init_cpu_r1/.
Actual restored bias/tau/sign/syn_count/syn_strength/derived weight and original edge indices are in expanded_parameters.npz.
identity_manifest.json binds these arrays, node order, checkpoint, initialization and hashes.

## Explicit parameter profile: do not mix H/R bundles

CPU baseline: artifacts/reference_bundle_v1.
Original GPU Full/R baseline: artifacts/reference_bundle_gpu_native_v1.
Both contain byte-identical canonical CPU a0, frozen stimulus/time, nodes and original edge order.
Their expanded syn_count and effective_weight differ slightly because the original Lognormal semantic_values
calls raw_values.exp() on the selected CPU/CUDA device. This is preserved, not normalized away.
Measured maximum native-profile difference: syn_count 1.52587890625e-5, weight 1.1920928955078125e-7.
Same-device R/Full comparison must load ONE profile's identity, parameters and candidate together.
Independent H must load the SAME profile as R; B's old CPU weight tables are not the GPU profile.
Cross-device results use the same checkpoint/input/a0 but report native expanded-parameter differences.

example_call.py selects CPU/GPU profile from --device; --bundle can explicitly select a bundle.
RStepService itself never silently switches parameters: its three constructor file arguments bind them.
The first GPU guard rejected a CPU parameter profile before any experiment step; failure evidence is preserved.

## Frozen stimulus and time

stimulus.npy: little-endian C-contiguous float32 [4,485,1,721].
conditions.csv preserves original Golden v2 sample IDs 0,1,12,13:
0° OFF, 0° ON, 180° OFF, 180° ON. The source 24-condition array is not re-rendered.
Each condition independently starts from the SAME a0. Do not inherit the previous condition's state.
Execute all 485 frames, including the dataset's 200 pre-stimulus gray frames.
dt is fixed at 0.005 seconds; B=1 per call.
time.npy[k] = k*0.005 - 1.0 labels activity AFTER updating using frame k.
Do not add 0.005 to these official edge labels. step_id=k is the synchronization identity.

The 721 values are official hex-pixel order. input_node_indices.npy [8,721] gives exact
global indices for R1–R8. nodes_full.csv supplies each node's type/u/v.
Each frame is replicated across the eight receptor maps using those indices.
H containing receptors is supported: its receptor inputs are omitted from external_r, not mis-assigned.
For independent H, construct x_H by the same exact input_node_indices map into its ascending H order;
all other x_H entries are zero. Do not sort pixels by type/coordinates or reshape into a guessed image.

## Candidate manifest and R calculation

candidates/B_T5c/candidate_manifest.json is the first SOFTWARE TEST candidate, not final FPGA selection.
H=67, R=45,602, HH=970, RH=5,567, HR=8,159, RR=1,498,535.
R production evaluates all 1,506,694 HR+RR edges in original global edge order.
The copied B node map and all four partition-ID arrays were independently checked against the actual restored graph.
The API also accepts another flyvis-r-only-candidate/v1 manifest. Tested: A_T4c, C_T4T5_all_centers and
a test-only one-receptor H. H must be an ascending unique proper subset; R is its ascending complement.
Candidate and actual expanded-parameter identities/counts/digests are checked on construction.

For each R target:
current_R = scatter_add(weight_e * relu(old_full[source_e]), target_R_local), over all edges with target in R.
velocity_R = reciprocal(max(actual_tau_R,float32(dt))) *
             (-old_R + actual_bias_R + current_R + external_R).
new_R = old_R + velocity_R * dt.
This preserves the original floating-point expression order. Negative activity is retained; only release uses ReLU.
Negative weights, duplicate edges, self-connections and feedback edges are not removed or merged.
No H next-state vector, H velocity or H-target current is calculated.
r_only.py imports only numpy/torch/standard library, never Full or FlyVis.

## Python call

Use the existing WSL environment. The following is a consumer call, not a closed-loop implementation.

~~~python
from pathlib import Path
import numpy as np, torch
from r_only import RStepService

bundle = Path(__file__).resolve().parent / "artifacts/reference_bundle_gpu_native_v1"  # use reference_bundle_v1 for CPU
svc = RStepService(bundle / "expanded_parameters.npz",
                   bundle / "identity_manifest.json",
                   bundle / "candidates/B_T5c/candidate_manifest.json",
                   device="cuda:0")  # or "cpu"
old_full = torch.from_numpy(np.load(bundle / "initial_state_full.npy")).to(svc.device)
frame = torch.from_numpy(np.load(bundle / "stimulus.npy")[0, 0, 0].copy()).to(svc.device)
r_candidate = svc.step(old_full, frame, step_id=0,
                       run_id="your-run-UUID", condition_id="0")
# r_candidate.activity: float32 [N_R] on svc.device
# r_candidate.global_node_indices: int64 [N_R], ascending GLOBAL indices
# status == "CANDIDATE_NOT_COMMITTED"
~~~

Both old_full [45669] and frame [721] must be explicit detached float32 Tensors on the requested device.
No implicit dtype conversion/device transfer or batch broadcasting occurs inside step.
Returned indices identify global nodes, not cell types. No state is cached or advanced.
Negative activity is valid. Nonfinite state/output, wrong shapes/dtypes/devices, invalid stimulus range,
wrong checkpoint/parameter hashes or invalid H indices raise InterfaceError and return no candidate.

The caller freezes old_full=a[k], supplies this SAME snapshot to independent H and R, and checks both results'
run/condition/step/model/map identities and finiteness before building a new merged a[k+1].
Never feed R the new H from the same step, never use recorded future boundaries, and never commit R alone
when H fails. H failure/timeout/duplicate-result and atomic-merge behavior belong to the B coordinator
and are not claimed as tested by this standalone service. This API cannot detect a logically mislabelled
caller-owned state token; the coordinator must enforce it.

For a debug comparison ONLY:
~~~python
from full_oracle import FullNetworkOracle
oracle = FullNetworkOracle(bundle / "identity_manifest.json", device="cuda:0")
full_next = oracle.step(old_full, frame)  # unchanged original Network._next_state
~~~
The Full oracle loads/reverifies the original local checkpoint. It does not adapt state or consume recordings.
It is not imported or called by R production. FlyVis selects a default device at import; set
CUDA_VISIBLE_DEVICES before importing Full/FlyVis, as the provided examples do.

## Run the existing environments

From PowerShell, for an independent R consumer with no Full/FlyVis import:

~~~powershell
wsl -d FlyVisCPU -- bash -lc '/opt/flyvis-venv/bin/python /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/example_call.py --device cpu --output /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/artifacts/your_consumer_cpu.json'
wsl -d FlyVisCPU -- bash -lc '/opt/flyvis-gpu-venv/bin/python /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/example_call.py --device cuda --output /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/artifacts/your_consumer_gpu.json'
~~~

Add --compare-full only when requesting an explicit debug oracle.
Existing output names are rejected, so choose fresh names for independent verification.

For a new full 4x485 validation:

~~~powershell
wsl -d FlyVisCPU -- bash -lc '/opt/flyvis-gpu-venv/bin/python /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/validate_r_only.py --device cuda --bundle reference_bundle_gpu_native_v1 --run your_fresh_run'
~~~

--record-full additionally saves all-node Full and all-R output time series (~708 MB per run).
No-record validation retains stream hashes, per-step errors, central/H activity and perturbation deltas.
Initialization and bundle construction scripts reject existing run directories and preserve accepted inputs.
The existing environment is reused; no package installation is performed.

## Evidence and limits

Validation includes all 1,940 same-old-state comparisons, positive/negative actual H→R perturbations,
disabling official Full update entrypoints, R-only scatter-size tracing, candidate generalization
and error rejection/no input mutation. GPU uses exactly the canonical CPU a0 and frozen input bytes.

r_only_cpu_r1 and r_only_cpu_r2 stopped at a test instrumentation assertion AFTER all numerical steps passed.
An isolated reproduction found FlyVis's default-device TorchFunction context redispatching the Python
scatter wrapper twice. The guarded spy now temporarily disables that mode; all production operations
already specify explicit devices. It leaves R math and official source unchanged.
The numerical tolerance remains atol=rtol=1e-5. Raw failures/trace diagnosis/logs are preserved.

PASS here means the standalone A R-only service works against original Full.
It does not mean SOFTWARE_CLOSED_LOOP, final-H selection, finite-width arithmetic, RTL or board acceptance.
R-only is nearly the whole original network for this small H; speed savings are not guaranteed.
Timings explicitly separate network calls from saved-array I/O and perform no HexEye rendering.
