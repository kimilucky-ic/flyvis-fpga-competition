# Full FlyVis lossless-template study

Assigned 2026-10-13. This is an independent CPU-only research lane, separate from hardware lines ⑦ and ⑨.

**Accepted:** the 34,528-byte template reproduces every ordered source/target/FP32-weight record. Whole-network 1/32/800-step self-feedback is bitwise equal to the pinned CPU reference, with 36,535,200 state values checked in the 800-step run. A fresh compact-only process also passes. See [REPORT.md](REPORT.md) and [BINARY_FORMAT.md](BINARY_FORMAT.md). No FPGA implementation or real-time claim.

## Goal and stopping boundary

Validate a binary representation of the complete original 45,669-node / 1,513,231-edge FlyVis network, including source/target indices, original edge order and effective FP32 weight bits. Execute the original continuous ReLU / Euler model with feedback from its own previous output, and compare all nodes against the pinned official CPU implementation.

The bounded acceptance sequence is structure, one step, 32 steps, then 800 steps. Stop at software evidence and a hardware feasibility budget. No Vivado, GPU, board I/O, services, training, pruning, model conversion, publication, commits or changes to other lanes. Hardware synthesis, board operation, 200 Hz and energy remain separate future questions.

## Source contract

- Upstream: TuragaLab/flyvis, commit `92b3845cc426dd309a1a0e1b3890156c42e14021`.
- Graph: `fib25-fib19_v2.2.json`, extent 15, n_syn_fill 1.
- Model: `flow/0000/000/chkpts/chkpt_00000`.
- Checkpoint SHA256: `d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f`.
- Graph SHA256: `6779065467f70cef14e8f2f1005efd4830fd29c00795c103756a6af60607f825`.
- Single model, batch 1, dt 0.005 s. Decoder and image rendering are outside this study.

Original source, data and checkpoint are read in place. All new outputs live here. The source repository license and attribution are preserved in the source inventory; no external distribution is authorized.

## Evidence implementation

`reference.py` builds the original graph through upstream helpers and runs upstream Network arithmetic. `codec.py` independently enumerates the binary template. `engine.py` executes it without an expanded edge list. `run_study.py` performs bounded acceptance and records provenance, exact comparisons, timing and limitations. `audit_study.py` checks saved results and damaged-file rejection, computes the analytical hardware budget and prepares a separate `replay.py` package. Generated reports, not this summary, are the authoritative results.

The official reference uses an in-memory storage adapter for its connectome because the original project's Windows HDF5 construction is not accepted. Its node/edge generation, parameter initialization/sharing, clamp, ReLU, scatter-add and Euler implementations remain the pinned upstream code. This adapter must be disclosed in all numerical claims; it is not an independent validation of HDF5 or GPU behavior.
