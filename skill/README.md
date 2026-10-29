# FPGA Skill Package

Version: competition audit draft 1.4, local update 2026-10-21  
Purpose: reusable FPGA competition workflows for board operation, numerical equivalence, feedback integration, scientific controls, demonstration, performance/energy accounting and evidence-preserving maintenance.

This directory is a competition-facing draft with fourteen inventoried Skills and one separate UART candidate. Working copies live in .agents/skills/ or .cursor/skills/; package instruction bodies derive from those working sources; this audit adds lowercase submission entrypoints, portable provenance references and submission-specific usage/evidence appendices. Codex working sources retain SKILL.md. The board recovery wording is additionally scoped to current authorization. New authoring is documentation validation, not independent replay on another board. Local draft publication is not implied.

## Original-guide audit (2026-10-21)

The original AMD guide was re-read, including PDF page24 / printed page21, sections3.3.5.2–3.3.5.4. See [clause-by-clause audit](guide_compliance.md), [missing validation evidence](validation_gaps.md), [source manifest](evidence/source_manifest.json), and [report-ready distillation](report_extract.md).

Fourteen items remain in this draft; **thirteen have bundled historical case records, one Windows-path item remains an unverified user observation**. This is not fourteen independently reproduced Skills. The direct-PL UART candidate remains separate and is not counted. Structured pitfalls/case workflows are allowed; adding a script is not mandatory for every item.

Submission entrypoints are lowercase `skill.md`; `README.md` is retained because the guide explicitly names it. Codex runtime entrypoints outside this submission remain `SKILL.md`. Unicode is allowed in content, not submitted directory/file names. A different Vivado version is allowed with explanation and reproducible scripts; 2025.2 is not a mandatory per-Skill test.

For another team: copy this whole directory, select an item below, read its `usage.md`, `skill.md` and `validation.md`, then adapt the target/input contract and fill [reuse record](templates/reuse_record.json). The fourteen workflows are prompt/pitfall/case instructions, not complete Vivado projects or bundled model weights. Historical reports are included for review; full experiment replay still needs the specific project's legal sources/data/tools listed in that item's gaps. Universal PYNQ bonus is not claimed.

Package map: per-item instructions/use/verification; `evidence/originals/` small original records; `evidence/source_manifest.json` source identities; `templates/` reuse record; `scripts/` offline integrity checking; root audit/report/collaboration files. Do not execute old commands or board preparation from historical report snapshots.

## Use the package

1. Identify the task and actual backend: general board access, bounded replay, partitioned feedback, complete-network PL, software research, display, build diagnosis, performance accounting or maintenance.
2. Open the matching `skill/<name>/skill.md` and follow its prerequisites and stop conditions.
3. Record the exact target, software versions, source/artifact identity, and evidence level. A workflow does not itself prove that a board is programmed or working.

## Included Skills

### [`zynq-7000-board-operations`](zynq-7000-board-operations/skill.md)

- **Scope:** PYNQ/Jupyter interaction with Zynq-7000 boards: home/file page, notebook kernel, overlay identity, AXI register access, DMA smoke checks, and state recovery.
- **Use:** when reading or testing a Zynq board through PYNQ or a browser-based board interface. Start with harmless page/kernel checks; read status before touching hardware; capture pre-test values; test the smallest useful path; read back recovery state.
- **Failure conditions:** browser route failure alone does not establish board failure; stale notebook output is not a live reading; a reboot invalidates prior runtime assumptions; `Overlay.download()` reprograms PL; a PYNQ workflow does not apply to a direct-VHDL UART design that has no PS/PYNQ path.
- **Evidence of effect:** the project records distinguish the Jupyter service, kernel response, overlay metadata, AXI/DMA behavior, and actual BIT identity. A two-neuron cascade has a recorded board result, with its earlier reload-constraint deviation preserved in the report.
- **Experience source:** board access failures that were specific to Codex's browser/command route; stale post-reboot state; the observed cascade and cleanup sequence.
- **Validated boundary:** project Zynq-7020/PYNQ workflow only. It has not been independently exercised on a different board or unrelated task, so the universal PYNQ bonus is not claimed.

### [`pynq-bounded-replay-evidence`](pynq-bounded-replay-evidence/skill.md)

- **Scope:** deterministic accelerator requests through PYNQ/Jupyter, staged small-to-large tests, raw input/output/register evidence, and local independent ZIP verification.
- **Use:** when a reviewed driver, fixed vectors and an independently retained oracle are available. Bind the run to boot/session/release identities; prepare files first; run only the approved bounded stage; seal and audit before expanding.
- **Failure conditions:** changed boot/overlay/hash invalidates the plan; a shell PYNQ/XRT failure does not alone prove bad firmware; a first-MMIO hang or output mismatch stops the campaign; returned-console PASS needs original raw evidence; no silent retries, resets, fallback or replay-to-closed-loop promotion.
- **Evidence of effect:** FlyVis67 V1/V2/V3 original archives were independently inspected: 1/32/800 requests and 67/2,144/53,600 exact integer outputs. The 800-request review checked 4,812 inventoried files and every START/completion/status sequence.
- **Experience source:** task “⑥ FlyVis · 67节点FPGA真板闭环”: first-AXI reset diagnosis, serial PYNQ/XRT failure followed by Jupyter execution, separate one/32/800 approvals, raw archive handoff, and correction of input-video/result-presentation versus live-run-video claims. See [source evidence](pynq-bounded-replay-evidence/evidence.md).
- **Validated boundary:** one Zynq-7020/PYNQ2.7 target and sealed FlyVis SOURCE_RAW release. Fresh independent replay of the packaged instructions and second-board reuse remain observed, not yet reproduced. Scientific Q22 precision and true feedback were not accepted.

### [`vivado-vitis-toolchain-debugging`](vivado-vitis-toolchain-debugging/skill.md)

- **Scope:** Windows Vivado/Vitis HLS startup, versioned IP, Tcl/Block Design, Unicode paths, AXI/HLS interfaces, resource reports, and safe rebuilds.
- **Use:** when a tool fails to start, an older IP is locked, a build script changes/deletes a working project, an interface-width error appears, or synthesis and implementation resource counts disagree.
- **Failure conditions:** an empty log is not a build; a locked IP is not proof that RTL is invalid; a top-level BRAM count may omit OOC HLS memory; generated BIT/HWH are not board proof; never run delete/recreate scripts against an open known-good project.
- **Evidence of effect:** earlier cases used a full Vivado 2024.2.2 entry point, isolated outputs, the actual `m_axis_weights` interface and separate HLS/top/routed BRAM counts. FlyVis67 adds a Vivado2026.1.1 full SoC bank/reset correction whose generated HWH/HDL were checked; the corrected release subsequently passed real-board integer replay.
- **Experience source:** `init.tcl`, non-ASCII paths, legacy IP, duplicate BD sources, a materialized Git symlink, a 34-bit payload in a 32-bit interface, unsafe in-place rebuild, dropped PS bank settings, and active-low auxiliary reset tied to zero.
- **Validated boundary:** each case names its own target and version. The FlyVis67 full SoC case used Vivado2026.1.1; this does not establish every package workflow on 2026.1.1. Vivado/Vitis2025.2 and independent cross-project reuse remain unverified.

### [`fpga-board-reference-research`](fpga-board-reference-research/skill.md)

- **Scope:** confirm exact board, hardware revision, FPGA part/package/speed grade, pins, clocks, interfaces, boot/image assumptions, and project compatibility from primary sources.
- **Use:** before copying constraints, selecting a board workflow, interpreting a schematic, or claiming a design matches physical hardware. Check board manual/schematic, AMD device documentation, project constraints and metadata as one chain.
- **Failure conditions:** matching an FPGA family alone does not validate package pins or board wiring; a Cmod A7 reference is not a Zynq-7020 board design; schematic facts do not prove current bitstream/runtime state; do not generalize a pin map across board revisions.
- **Evidence of effect:** the fly port review reconciled the local ATK Zynq schematics with project constraints: 50 MHz PL clock at U18, UART pins T19/J15, and P5 jumpers 3-5 and 4-6. These facts are recorded in the current fly board report.
- **Experience source:** initial confusion between the original Cmod A7 target and the ATK Zynq-7020 target, then a source-backed schematic/constraint cross-check.
- **Validated boundary:** one documented ATK Zynq-7020 hardware revision; other board revisions still require their own documents.

### [`fpga-model-equivalence`](fpga-model-equivalence/skill.md)

- **Scope:** build a reference model from the instantiated production RTL and compare behavior across software, RTL/HLS simulation, implementation artifacts, and board runs.
- **Use:** when translating fixed-point or event-driven behavior, validating a neuron or accelerator, or deciding what a verification result proves.
- **Failure conditions:** do not use a similarly named test kernel without equation comparison; do not approximate bit-exact arithmetic with floating point; stop at unresolved field-width/interface contracts; do not infer board execution from simulation or bitstream generation.
- **Evidence of effect:** recorded checks include 512 PN state comparisons, nine neuron-type equation checks over 32 random states each, and 11 UART decode edge values. Sparse PN-to-KC accumulation matched the dense RTL for four boundary/input classes and improved that isolated microbenchmark 14.46x; no whole-network speed claim is made. A hash-verified original ORN input was tried for a bounded 100 ms comparison, which diverged at step 0 (0.67% aggregate exact matches); this correctly stopped the full multi-hour replay pending contract diagnosis.
- **Experience source:** production `PQN_PN.vhd` differs from test-only `DSSN_PN.vhd`; the 34-bit row/column/weight payload does not fit a 32-bit AXI stream; high fan-out in the MaleCNS graph exceeds the existing fixed router; board result must be tied to exact BIT/HWH and test input. A Git LFS hash check plus 100 ms hardware-trace preflight caught network-level divergence before the estimated 6.9-hour run.
- **Validated boundary:** project-specific software and RTL checks only. Independent reuse on another FPGA design or board has not been demonstrated.

### [`fpga-fixed-point-quantization`](fpga-fixed-point-quantization/skill.md)

- **Scope:** fixed-point formats, quantization sweeps, accumulator/state range bounds, golden vectors, and software-to-RTL comparison.
- **Use:** when translating a floating-point network or signal model into finite-width FPGA arithmetic or selecting candidate weight/state widths.
- **Failure conditions:** task accuracy alone does not prove internal spike/state equivalence; retraining a candidate readout does not prove a frozen PC readout transfers; random traces alone do not establish overflow safety; never prune edges to fit storage.
- **Evidence of effect:** the MaleCNS 321-neuron/7,590-edge software model compared 8/10/12-bit candidates over four seeds. Under the positive-glutamate scenario, 12-bit transferred the float-trained decoder at 80.8% mean accuracy versus 80.1% float, while only 32.0% of full 321-neuron timestep vectors matched exactly. A conservative current/state bound was checked against signed Q16.16 range.
- **Experience source:** the MaleCNS inference v1 quantization robustness report and generated RTL vector manifest.
- **Validated boundary:** software-only for one MaleCNS graph. Glutamate polarity remains unresolved; RTL simulation passed in Vivado Simulator 2024.2.2 (11 directed checks and 1,200/1,200 golden timestep vectors); synthesis, bitstream, and board evidence remain absent.

### [windows-fpga-path-diagnostics](windows-fpga-path-diagnostics/skill.md)

- **Scope:** triage Windows Vivado/Vitis/XSim failures that may depend on Chinese or other non-ASCII characters in project, parent, temporary, generated, or output paths.
- **Use:** early in tool startup, Tcl, IP-generation, log-encoding, or child-process failures, before changing RTL or reinstalling tools.
- **Failure conditions:** Windows supports Unicode paths and not every failure is path-related; a successful move can also change path length, permissions, or build state. Preserve the original and compare one minimal command from a separate ASCII-only copy.
- **Evidence of effect:** the user reports that renaming the Chinese-named project folder to ASCII fpga made the FPGA operation work normally. The exact failing command and error were not recorded.
- **Experience source:** the user-reported path rename and the diagnostic procedure in the project skill.
- **Validated boundary:** one reported Windows case only; direct controlled reproduction and exact tool/version/error remain open.

### [gpu-fpga-feedback-transactions](gpu-fpga-feedback-transactions/skill.md)

- **Scope/use:** partitioned recurrent GPU/PL state ownership, real old-state feedback, COMMIT/RELEASE/ACK and bounded uncertainty handling. Select the actual backend contract first.
- **Failures/recovery:** wrong/late ACK, missing journal barrier, stale session or unknown completion stop publication; use only the contract's supported recovery.
- **Evidence/effect:** A3R1 485-step actual joint run checked 2,797,480 candidates and 2,791,712 feedback words with native GPU-H updates disabled.
- **Source experience:** S2/S4/S7, including durable versus asynchronous recording, stale PS wall time and readiness-format failures.
- **Boundary:** does not transfer A3R1 protocol, numerical proof, current board state or timing to complete-network PL; fresh packaged reuse remains observed, not yet reproduced.

### [flyvis-demo-data-integration](flyvis-demo-data-integration/skill.md)

- **Scope/use:** existing GUI, camera and 3D consumers with exact run/node/time provenance, actual decoder output and simple operator controls.
- **Failures/recovery:** reject stale/short data, invalidate unavailable panels, retain raw values and original rendering, and distinguish computational coordinates from anatomical illustrations.
- **Evidence/effect:** verified lazy startup on unchanged data, eight-type fixed-baseline replay, and an independently identified real-GPU/software-H 32-step performance check.
- **Source experience:** S2/S5/S6; removes repeated all-data hashing, synchronous optional work, duplicated explanations and second-producer ambiguity.
- **Boundary:** software/replay/reader evidence does not establish a new camera/PL run or live cross-individual anatomy; candidate11 reader work was in progress.

### [flyvis-controlled-replacement](flyvis-controlled-replacement/skill.md)

- **Scope/use:** Full/Sham ablation and learned-module replacement with common initialization, frozen criteria and own-state feedback.
- **Failures/recovery:** preserve failing windows; correct comparator/identity errors using saved traces, or issue a new experiment identity; do not tune the observed failed threshold.
- **Evidence/effect:** frozen 31,168-parameter CPU candidate passed 10 held-out stimulus conditions with 21,000 formal commits audited and no native-H production update or teacher correction.
- **Source experience:** S3/S7/S9; static texture/local-position diagnosis and prefix-versus-endpoint corrections.
- **Boundary:** controlled computational-model scope only; not a biological-function percentage, every-input proof, faster implementation or FPGA CNN.

### [fpga-performance-power-accounting](fpga-performance-power-accounting/skill.md)

- **Scope/use:** matched model-sample work, timing phases, actual resource stage, telemetry windows and chip/board/system energy boundaries.
- **Failures/recovery:** correct batch denominators and window mismatch from saved logs; retain conflicting telemetry, unknown clocks and vectorless assumptions rather than selecting a favorable number.
- **Evidence/effect:** 17,460-step GPU telemetry; scoped routed FPGA power scenarios; actual B BRAM report after layout/bulk-I/O change.
- **Source experience:** S1/S3/S4/S8; no TGP substitution, no PL-only versus device-total comparison, no cycle-model value promoted to measured throughput.
- **Boundary:** FPGA energy remains an estimate and complete-network first-board computation is unaccepted; no unconditional whole-system energy/cost claim.

### [fpga-evidence-preserving-cleanup](fpga-evidence-preserving-cleanup/skill.md)

- **Scope/use:** owner/dependency inventory, release allowlists, reconstructible data and a specifically authorized Windows cleanup/migration.
- **Failures/recovery:** unknown caller/manifest/Git ownership or failed byte reconstruction keeps the candidate protected; named retained files and recovery hashes are checked after an approved operation.
- **Evidence/effect:** dependency audit found live callers of duplicate source; five derived files were recovered byte-for-byte before/after retirement while 8,164 retained files and 84 old trajectories were checked.
- **Source experience:** S7/S9, including logical versus allocated bytes and source/manifest references.
- **Boundary:** no automatic deletion, hard-link deduplication, live-project relocation or reuse of old cleanup approval.

### [flyvis-gpu-reference](flyvis-gpu-reference/skill.md)

- **Scope/use:** existing WSL original-FlyVis CUDA render/inference against pinned CPU references.
- **Failures/recovery:** verify actual CUDA kernels, device/wheel/cache selection and frozen input before changing environments; retain failed conditions.
- **Evidence/effect:** separately restored GPU processes reproduced exact GPU output; source Skill records the original CPU/GPU tolerances and tested versions.
- **Source experience:** accepted source Skill and its existing GPU validation reports; used by S3/S5.
- **Boundary:** existing environment/checkpoint only; clean-install reuse, unrelated GPU and physical-board proof remain unverified.

### [flyvis-decoder-inference](flyvis-decoder-inference/skill.md)

- **Scope/use:** original flow decoder with recursive eval, buffer/weight invariance and independently restored CPU/GPU inference.
- **Failures/recovery:** no-gradient alone did not disable child BatchNorm/Dropout; reload mutated state and compare only accepted eval-mode results.
- **Evidence/effect:** independently restored CPU/GPU checks and repeated GPU equality are recorded in the existing source Skill.
- **Source experience:** original training-mode failure, stale comparison target and hex-mask projection diagnosis; needed by S2/S3/S5/S6.
- **Boundary:** tested checkpoint/input comparisons, not physical speed calibration, natural optical-flow accuracy or PL execution.

## Collaboration evidence

[Engineering summary](evidence/chat_excerpts.json) is retrospective only; original conversations and source-path/session metadata are not distributed.

Run `python scripts/check_package.py` to check this folder offline; the checker does not run any historical experiment.


See [`collaboration-records.md`](collaboration-records.md) for the observed failures, model corrections, evidence links, and remaining transcript requirements.

The [nine-chat source review](source_review_20261018.md) lists all screenshot conversations, concrete prompt/error/correction summaries, primary paths and current unverified boundaries. It also separates the active candidate11 clock stop from completed A3R1 board feedback and B's model-patched simulation.

## Candidate pending physical validation

### [`fpga-uart-link-validation`](candidates/fpga-uart-link-validation/skill.md) — observed, not yet reproduced on the board

- **Scope:** serial communication with a direct-VHDL PL design that has no PYNQ/PS control path.
- **Use:** choose this procedure when the board design exposes UART directly to a USB-UART bridge; do not use the Jupyter/Overlay workflow for that path.
- **Failure conditions:** a terminal showing `?` is not proof of bad UART when the payload is binary; no bytes before a required start command may be expected; never guess or repeat state-toggle opcodes; do not reload/restart the board just to collect evidence.
- **Current evidence:** RTL and constraints establish this project's expected baud, pin mapping, command framing, and response framing; UART loopback simulation passed for `00 A5 FF`. The historical report includes user-pasted RX frames and a TX log; a timestamp-aligned controlled stimulus-response and original terminal capture remain missing.
- **Source observation:** XCOM was reported empty before any test command. RTL waits for a valid RX start before periodic trigger generation. The next capture procedure is in the candidate SKILL and `docs/fly-Zynq7020-current-status.md`.
- **Readiness:** keep this as a candidate until the real board returns a captured HEX frame and a controlled RX stimulus is decoded end to end.

## Package limitations

- These Skills were built from one team's Zynq-7020/fly/SNN experience. The included failure examples are useful starting points, not proof of operation on every AMD board.
- Older lanes use Vivado2024.2.2/Vitis HLS2024.2; FlyVis67 additionally has a scoped Vivado2026.1.1 full SoC and board-replay case. The 2025.2 alternative and fresh replay of all packaged procedures remain unverified.
- The collaboration record is a curated summary, not a verbatim export of all four chats. The guide asks for prompts, model responses, and self-correction trajectories; attach the original chat exports or screenshots before final submission.

## Competition-readiness checklist

- `skill/README.md` and self-contained per-Skill files are present.
- Each of the fourteen included Skills lists scope, use, failure conditions, evidence of effect, and source experience; fresh independent reuse is distinguished from historical case evidence.
- The direct-UART procedure is separated as a candidate and is not counted as a validated Skill until raw board HEX traffic and a controlled command/response are captured.
- The project has not demonstrated cross-board PYNQ reuse; no universal PYNQ bonus is claimed.
- Version evidence is scoped by case: older Vivado/Vitis2024.2 work and the new FlyVis67 Vivado2026.1.1 full SoC. 2025.2 and full package reuse remain outstanding.
- The collaboration record summarizes correction trajectories but is not a complete raw transcript export.
