---
name: gpu-fpga-feedback-transactions
description: Integrate and verify iterative GPU and FPGA state feedback with explicit state ownership, request identities, commit acknowledgements and bounded failure handling. Use for partitioned recurrent-model execution; select the actual backend contract before applying a protocol.
---

# GPU–FPGA State Feedback

## Scope and prerequisites

Use for a model partition whose next state depends on both software and hardware. Identify the model/checkpoint, full initial state, partition IDs/order, numerical profiles, exact BIT/HWH, driver, boot/session and accepted protocol. A complete-network PL backend needs its own state/step contract; do not impose a partitioned A3R1 COMMIT/ACK protocol on it.

Respect the current operator's assignment and approved run scope. For this competition, prefer one board preparation and one existing PC entrypoint that performs the bounded plan automatically. Keep identity checks inside that path; repeated human token exchange is not an invariant.

## Procedure

1. **Assign committed-state ownership.** Specify who owns H[k], R[k], step and epoch, and whether the backend is stateless, staging candidates or advancing persistent state. Keep at most one unresolved step unless a reviewed protocol explicitly supports more.
2. **Pin the common start.** Bind all participants to the same checkpoint, source, graph, input and initial-state hashes. Quantize the selected partition once under its declared profile. An integer oracle and a float operator with quantized storage are different backends.
3. **Prepare candidates from one old state.** GPU computes its assigned terms/R candidate; PL computes its assigned H candidate. Disable the native GPU update of the replaced H partition. Preserve raw PL integers as the next state's source rather than recomputing H on the host.
4. **Validate actual responses.** Bind request, response and ACK to run/session/boot/epoch/step and exact input/result identities. Enforce lengths, numerical format, status, ordered framing and a deadline for the complete frame; receiving a few bytes must not indefinitely renew the deadline.
5. **Publish after the accepted barrier.** For the tested partitioned path, verify candidates, complete COMMIT and actual RELEASE/IDLE, receive the matching ACK, then publish the complete next state. Check H[k+1] is the previous real PL result in the following request.
6. **Handle uncertainty explicitly.** If a side might have advanced but confirmation is missing, enter IN_DOUBT and stop further steps. Query/retry only when the protocol defines and verifies the exact idempotent operation; never turn a generic reconnect into a replay of an unknown transaction.
7. **Declare the recording profile.** The durable profile requires its accepted journal barriers before ACK/publication. A user-approved performance profile may move reference audit, full hashing, fsync and rendering out of the STEP path, while preserving necessary identity/ACK/error checks. Report the resulting loss of crash-durable recording guarantees; dropped/failed records cannot produce a complete-evidence PASS.
8. **Measure and close.** Record GPU, protocol/transfer, PS/DMA/PL, commit and evidence times separately. After the bounded run, finish the accepted audit, retain results, close owned PC workers normally, and leave board resources according to the approved plan.

## Known failures and recovery

- A software readiness object serialized as text instead of an object can fail before STEP. Keep the raw HTTP status/body and first failing stage; do not blame neural computation without its evidence.
- The PS wall clock may be stale. Use monotonic durations; where approval windows require wall time, use the reviewed bounded time proof tied to the boot/session rather than disabling time checks or changing the system clock.
- Reuse of an old overlay/CMA/kernel requires the same live object, verified identity, idle/error state and explicit ownership. A quiet status page or absence of visible terminals is insufficient.
- A missing/late/wrong ACK stops publication. Preserve pending state and buffers; recovery must match the state-owning backend.

## Expected verification

Check per-step candidates against an independent numerical path, all consecutive feedback words, original-partition update counts, and transaction order. CPU/mock protocol tests validate handling; they do not establish physical PL execution.

## Demonstrated source and limits

FlyVis A3R1, Zynq-7020/PYNQ2.7, Vivado2026.1.1, H=5768/Q24: the retained 485-step run c708f1c9bac14c07ac8f56d59678b95a reports 2,797,480 checked PL candidates, 2,791,712 feedback words and zero native GPU-H updates. Its FINAL_RESULT.json is under flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_latency485_20261016/runs/.

Cases S2/S4/S7 in skill/source_review_20261018.md document the journal/performance distinction and source contracts. The newer minimal GPU+software-Q24 test is software evidence only. This packaged workflow has not been freshly reproduced on another board/task; broader reuse is observed, not yet reproduced. It does not establish real-time response or biological replacement.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
