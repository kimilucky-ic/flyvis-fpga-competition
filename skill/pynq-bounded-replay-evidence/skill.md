---
name: pynq-bounded-replay-evidence
description: Prepare bounded PYNQ accelerator replays, guide an operator through staged board requests, preserve raw input/output and register traces, and independently audit returned evidence ZIPs. Use for deterministic one-request or multi-request verification with an independently held oracle on Zynq/PYNQ; complements general board access and does not apply to direct-PL UART.
---

# PYNQ Bounded Replay and Evidence

Use for an accelerator with deterministic requests and an independent integer or RTL oracle. Read the consuming lane's checkpoint and general Zynq board-operation workflow first.

## Scope and validation

- Demonstrated case: FlyVis T5c 67-node SOURCE_RAW, Zynq-7020/PYNQ 2.7, with a sealed resetfix BIT/HWH and frozen request vectors.
- The user operated one-request, 32-request and 800-request campaigns; their original archives were independently inspected on the host.
- Each request used recorded old state. Acceptance is board request-replay integer equivalence, with no state-feedback or scientific-precision acceptance implied.
- A fresh independent replay of this packaged Skill has not been performed. Cross-task and cross-board reuse remains **observed, not yet reproduced**; do not claim universal PYNQ compatibility.

## Prerequisites

Identify the exact board/part, PYNQ image and Python runtime, boot ID, active notebook/kernel, current overlay, BIT/HWH/release-manifest hashes, driver identity and interface/register contract. Retain frozen requests and an oracle independently of any returned archive.

Prepare a unique session directory, expected row/output counts, maximum attempts and stop conditions. Execute the reviewed bounded plan within its existing user authorization; seek new authorization only when its physical-operation scope changes. Historical completed-run approval is not reusable.

## Operator experience and recording profile

Use the consuming project's accepted board preparation and one PC launch entrypoint. Automate identity checks, bounded execution, result packaging and normal close inside that path. The older manual ZIP/cell handoffs are a research-audit example; do not impose them on every run.

Keep the accepted recording contract explicit. Durable acceptance may require journal barriers; a user-approved performance profile can defer deep hashing/reference audit/rendering and use nonblocking snapshot recording. Preserve identity/status/timeout checks and label incomplete recording honestly. Changing to deferred recording does not retain the old crash-durability guarantee.

## Procedure

1. **Read the latest source state.** Determine what was actually accepted and which artifacts produced it. Do not use a chat title, stale notebook output, old board clock or build success as current board evidence.
2. **Prepare files before hardware.** Verify the delivery ZIP, its manifest and every required file. Bind a file-only plan to session/boot ID, BIT/HWH/manifest/driver hashes, request/oracle hashes, selected rows, output shape and attempt limit. Verify counts and exclude unrelated perturbation vectors. Keep original packages and failed preparations.
3. **Choose one execution surface.** Give the operator one complete cell or one script command, naming the notebook/kernel or shell where it belongs and the expected last output. Do not mix Python cells, shell commands and password prompts. Verify the selected interpreter and PYNQ/XRT environment before programming.
4. **Recheck live identity.** Through the reviewed read-only path, confirm boot ID, overlay identity and relevant runtime/status facts against the plan. A changed boot, overlay, hash or session invalidates it. Prepare a fresh plan after resolving the mismatch; obtain approval for any new physical operation.
5. **Start with one request.** Under the exact operation approval, use the project's reviewed driver and register map. Keep programming and first computation as separate checkpoints when the approved plan requires it. Check buffer alignment, non-overlap, accessible DDR range, pointer readbacks, one returned START, completion/IDLE and status values.
6. **Capture every request.** Retain raw input/output, intent and returned register events, comparison, elapsed-time scope and faults under the accepted recording profile. Compare against the independent oracle at the contract's declared stage. Stop acceptance on an identity, address, status, timeout, evidence or value failure; do not label lost records complete. Keep buffers alive when completion is uncertain.
7. **Advance within the approved plan.** Review the preceding stage before expanding its row range. Continue already authorized stages without repeated manual confirmation; a new physical-operation scope needs new approval. The demonstrated 1/32/800 progression is an example. One-attempt markers prevent accidental reruns.
8. **Seal files after execution.** Without starting PL again, create a manifest of paths, sizes and hashes; include raw requests/outputs, traces, reports, plan and firmware/software identity. Record the final ZIP hash and retain the original files and ZIP.
9. **Audit the returned ZIP locally.** Perform zero hardware operations. Check the archive/manifest identity, inventory completeness, row order/count, raw array shapes, per-row trace/output hashes and combined arrays. Compare all raw PL codes against a separately retained oracle, rather than trusting only the oracle or PASS summary inside the received ZIP. Verify START/completion/status and pointer/buffer evidence using the exact design contract.
10. **Report the proved result.** Name the release, session/boot provenance, request/output counts, independent comparison, raw archive and limitations. A console summary is operator-reported until original evidence is inspected. Attribute host completion time including logging/SD I/O correctly.

## Expected result

A sealed, hash-identified archive contains complete evidence for every approved request and exact agreement with an independent oracle. Claim PASS for that release, request set and run. The operator's physical-run evidence and the host's independent archive verification are separately identified.

## Failures and recovery

- A reboot, changed file, overlay or session: stop and establish a fresh identity-bound plan.
- PYNQ reports `No Devices Found` in a shell: inspect the interpreter, PYNQ environment and XRT library path, and the last saved operation intent. This does not alone prove bad FPGA firmware. Switch execution surfaces only after proving which programming/request actions were actually reached.
- First MMIO access does not return: preserve the last intent/returned event and inspect the full clock/reset/AXI contract. Use the toolchain diagnosis workflow; do not repeatedly poke the bus.
- A status/value/timeout failure: stop that campaign, preserve the trace, and request design-specific recovery. Do not silently retry, reset, reload, COMMIT or substitute Python outputs.
- A bus operation hangs: a Python timeout may not interrupt it. Preserve the last visible output and do not free in-flight buffers or terminate/restart the kernel as generic cleanup.
- A displayed clock differs: first distinguish a measured frequency from a software calculation using an assumed reference. Reconcile the board oscillator, HWH, installed PYNQ implementation and PLL/dividers before changing any clock or weakening the gate. The candidate11 50-versus-33.333333MHz reference explanation was still pending live confirmation at this review.
- An archive check fails: retain the original unchanged and identify the first failed check. A file-only re-export can be prepared without rerunning hardware.

## Reporting boundaries

Keep integer equivalence, scientific numerical accuracy, feedback/COMMIT correctness, video provenance and performance as separate acceptance questions. An input video or edited result presentation does not record the live board run. Replay of recorded old state does not prove live feedback. PYNQ/MMIO/log provenance does not provide cryptographic silicon attestation.

## Source experience

Read [evidence.md](evidence.md) for the tested target, original archive identities, operator/model correction sequence, missing reproduction and source-report pointers. Never reuse its historical boot IDs or consumed approvals as permission for a new run.

The 2026-10-18 source review adds the user-directed simple-launch policy and later software performance profiles; see cases S1/S2/S4 in skill/source_review_20261018.md. Historical 67-node replay acceptance does not establish these newer paths' board performance.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
