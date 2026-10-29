---
name: vivado-vitis-toolchain-debugging
description: Diagnose Vivado, Vitis, Vitis HLS, Tcl, IP, Block Design, synthesis, implementation, and bitstream build failures on Windows FPGA projects. Use when tool startup, legacy IP migration, Unicode paths, HLS interfaces, utilization, or rebuild safety is involved.
---

# Vivado and Vitis Toolchain Debugging

## Tested scope

Project evidence covers Vivado 2024.2.2, Vitis HLS 2024.2, and a legacy fly source project created with Vivado 2016.4. The separate FlyVis T5c 67-node SOURCE_RAW case also has a full SoC resetfix build in Vivado 2026.1.1 build 6605303 for xc7z020clg400-2 and subsequent independently inspected board replay. This validates that case, not every packaged toolchain procedure. Vivado/Vitis 2025.2 and fresh cross-project replay remain unverified.

## Start with a safe, reproducible build context

1. Inspect the project instructions, current GUI/open project, build scripts, logs, tool versions, exact target part, and source-control state before changing anything.
2. Prefer read-only probes first. Identify scripts that delete build directories or rewrite project/IP files before running them. Keep a user-open project intact; use a separate build/output directory for rebuilds.
3. Record the full command, working directory, tool version, exit code, and log path. A blank log is not proof that a build started.
4. On this project the installed Vivado entry point was recorded as `D:/Vivado/2024.2/bin/vivado.bat`; verify it still exists and reports the expected version before reuse.

## Windows startup and path failures

- If Vivado reports `Can't find a usable init.tcl`, do not assume the installation is broken. Bypass ambiguous PATH entries and run the verified `vivado.bat` by full path. Probe the Tcl library under the same installation (previously `tps/tcl/tcl8.6`) and preserve the probe log.
- Vivado/Vitis child processes may fail on non-ASCII or long Windows paths even when the GUI opens the project. If logs show mojibake, missing generated files, or failed IP delivery, retry through a temporary ASCII drive mapping such as `subst X: "<project-root>"`, with the build started from `X:`. Remove only the mapping created for that run after all child processes have exited.
- When a startup, Tcl, IP-generation, or child-process failure occurs, inspect the entire absolute path, including parent folders and TEMP/TMP/output paths. A user-reported Chinese-folder-to-ASCII-folder rename made an FPGA operation work normally, but its exact command and error were not captured. Prefer testing a separate short ASCII-only project copy with the same tool version and a fresh output directory; preserve the original and do not assume every Unicode path fails. Follow the detailed checklist in the project skill package and record whether path length or other variables changed.

- Check dependencies such as `tee.exe`, `settings64.bat`, working directory, and `PATH` using the selected installation. Do not mix binaries or Tcl libraries from different tool versions.
- On Windows check whether a supposed symlink was materialized as a plain text file. For headers, replace it with a valid include wrapper only after confirming the intended target and keeping the repair in source control.

## Legacy IP and Block Design failures

1. Confirm the project’s original tool version and the active tool version. Locked IP after opening an older design is an IP migration issue, not automatically an RTL syntax error.
2. Read the IP status, VLNV/version, upgrade messages, and generated-output status. Preserve a copy before migration or regeneration.
3. For duplicate-source Block Design errors, trace the source and sink ports in both the BD Tcl and RTL. Do not add a constant driver to a port that is already driven in RTL or represented as an input source in the design.
4. Re-run validation and wrapper generation before full synthesis. Save the first meaningful error and the changed design diff.

## HLS and AXI contract checks

Before integrating a newly built HLS IP, compare all three sides: HLS-generated IP metadata, Block Design connections, and host software packing/unpacking.

- Check IP VLNV, control protocol, AXI-Lite map, AXI-Stream direction and width, DMA width, `TKEEP`/`TLAST` behavior, and reset/clock domains.
- For every packed field, calculate the total width and check all source bit-select ranges against the actual `TDATA` width. Verify neuron ID limits, weights, timestamps, row/column fields, and Python/RTL parity.
- Do not infer an external learning handshake from a signal name. Inspect generated HLS ports and their actual BD sinks; an `m_axis_weights` stream routed to a DMA is different from nonexistent `learn_weight_*` ports.
- Treat Windows symlink/header fixes, HLS source changes, and generated-IP changes as separate provenance steps. Confirm the build log and exported IP path correspond to the current source.

## Resource and implementation diagnosis

- Investigate implementation DRC using both top-level and out-of-context IP reports. A small top-level synthesis BRAM count may omit large HLS OOC memory until implementation merges the IP.
- Check RAMB18, RAMB36, FIFO, LUT, FF, DSP, timing, and constraints against the exact device. A design at the BRAM limit has no safe margin for FIFO growth, debug cores, or feature additions.
- Distinguish estimates, old checked-in reports, fresh synthesis reports, routed timing reports, and generated bitstreams. Record the run directory and source revision for each claim.
- Fix the earliest real cause, not only the last DRC message. Rebuild in a fresh directory and verify the resulting BIT/HWH pair, target part, reports, and warnings.

## Zynq configuration and a stalled first AXI access

1. If programming returns but the first MMIO access does not, locate the last intent and last returned transaction in the saved trace. A read intent without a response, START or raw output does not prove that the accelerator computed.
2. Cross-check the manufacturer board guide, PS preset/import script and generated HWH. Retain DDR preset, MIO bank voltage and HP width settings explicitly; a valid FPGA part alone does not make a PS configuration board-compatible.
3. Inspect every reset input's configured polarity and tied value, then trace the generated reset outputs to the HLS and AXI interconnects. For proc_sys_reset, C_AUX_RESET_HIGH=0 with aux_reset_in tied to zero asserts reset. Explicitly choose polarity and an inactive tied level in Tcl; do not infer semantics from a signal name.
4. Keep the original image and build the correction in a new directory. Verify the generated HWH/HDL reset contract, routed reports, BIT/HWH/XSA identities and configuration payload. A changed BIT header timestamp alone is not proof of a changed configuration.
5. Review the installed PYNQ loader and live PS image assumptions: loading a BIT/HWH is not proof that XSA ps7_init, DDR/MIO configuration or HP widths were applied. Use the documented read-only runtime checks before proposing another load.
6. Seek exact authorization for the new release's physical test; stop after the smallest approved operation and retain failures. Subsequent successful access supports the correction, but does not prove every prior whole-system symptom had that single cause.

Observed source case: FlyVis67 bankfix retained manufacturer DDR/bank settings; first-read trace then exposed auxiliary-reset polarity. The isolated resetfix generated C_EXT_RESET_HIGH=1/C_AUX_RESET_HIGH=1 with aux tied to zero, and the corrected release later passed 1/32/800 real-board integer replay. Detailed source reports are indexed in the pynq-bounded-replay-evidence Skill's evidence.md and the skill-development checkpoint. No fresh EDA/board rerun is implied by documenting this case.

## DDR transfers, BRAM layout and simulation-model faults

- Before widening compute, determine whether capacity, bandwidth or arithmetic is limiting. Inspect actual RAM inference around power-of-two boundaries; a small LUTRAM tail may avoid doubling a BRAM allocation while preserving every address and one-cycle read semantics.
- Prefer bulk DDR payload transfer with a small GP0 control plane when per-word MMIO dominates. Verify flush/invalidate order, accessible aligned disjoint buffers, 4KiB burst splits, FIFO backpressure and waiting for every AXI write response before publishing success. Retain buffers when accepted bus transactions might still be in flight.
- Audit actual retired edge order/term/partial sum and DDR readback, not only an AXI producer's intended data. Add the final source address, final burst, repeated destination and timeout/error-drain cases.
- If correct AXI beats/OKAY responses coexist with missing native model storage, preserve a failing run and isolate the model scheduling contract. Pin the installed model SHA and use a local simulation-only copy for a minimal diagnostic correction. Record its diff, exact scope and elaboration identity, and independently rerun full-system checks. Keep the original failure and installed sources intact.

Hardware B case S8 in skill/source_review_20261018.md demonstrates 16,402 source entries split into a 16,384-entry BRAM main area plus an 18-entry distributed tail, and DDR block I/O. Routed SoC BRAM was 69.5 versus 85 tiles; simulation and routed evidence exist, board throughput does not.

The same case isolated a specific Vivado2026.1.1 PS7 VIP active/#0 scheduling race. Its local 1ps sampling correction is disclosed simulation evidence, not a general vendor fix or DUT/hardware change; do not apply it blindly to another model/version.

## Known failure patterns from this project

- `[BD 41-249] ... already has a source port` can mean a BD constant is driving a signal already assigned in RTL. Trace both drivers before changing the graph; remove the redundant source only after confirming the RTL contract.
- `[HLS 207-1260] cannot use dot operator on a type` was caused by a header that contained only a Git symlink target path. Inspect the file bytes and checkout symlink behavior before debugging the C++ expression.
- `[Synth 8-524] part-select [33:26] out of range` exposed a 34-bit row/column/weight payload being sliced from a 32-bit AXI stream. Recalculate every field width and stop at the interface decision; do not hide the mismatch by changing slices without updating the producer and consumer.
- `[DRC UTLZ-1]` may be caused by an out-of-context HLS IP whose BRAM use is absent from the top-level synthesis count. Inspect the HLS OOC utilization report and the implementation merge.
- A fly reference project created with Vivado 2016.4 can show locked memory/FIFO/clocking IP in Vivado 2024.2. Treat this as versioned IP migration and record the upgrade result; it does not by itself establish that the RTL is invalid or that the design targets Zynq.

## Stop at unresolved interface decisions

If the design’s data format cannot fit its interface, do not choose a new format silently. Show the field-width arithmetic, affected RTL/HLS/BD/software files, and compatible options; pause dependent integration until the owner selects the contract. Do not report a completed build or board success when synthesis or integration stopped at that decision.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
