---
name: zynq-7000-board-operations
description: Operate and diagnose Zynq-7000 FPGA boards, especially PYNQ-Z2 through Jupyter or browser-based home pages. Use for board connectivity, notebook/kernel access, overlay and bitstream status, AXI/DMA smoke tests, or separating browser evidence from actual PL hardware evidence.
---

# Zynq-7000 Board Operations

Use this workflow for Zynq-7000/PYNQ board interaction. Treat the exact board model, silicon part, operating image, and current board state as task-specific facts that must be rechecked.

## Prerequisites and validation boundary

- Identify the exact board model and revision, FPGA part/package/speed grade, PYNQ image/API version, host route, and matching BIT/HWH pair before using the examples.
- The recorded evidence is from one Zynq-7020 board accessed through PYNQ/Jupyter, including a documented two-neuron test. It does not establish compatibility with another board or unrelated project.
- A direct-PL fly VHDL design that communicates over UART does not use this PYNQ workflow; use its separate UART procedure and current project status.

## 1. Establish the target and current state

1. Read the consuming project's latest board status and previous test record before interacting. Start from its designated checkpoint, if it has one. Do not treat historical notebook output as current state.
2. Record the board model, exact FPGA part/package/speed grade, host connection, board IP/URL, PYNQ image, and the `.bit`/`.hwh` pair under consideration.
3. After a board reboot or power cycle, assume prior PL configuration and runtime register state may have been lost. Re-read live state; never reuse old notebook output as a current reading.
4. Classify the next action before doing it: page navigation, pure Python, software-only overlay inspection, register/MMIO access, DMA, or FPGA programming. Begin with the least invasive action that answers the question.

## 2. Separate access evidence from hardware evidence

Keep these claims distinct:

- The Jupyter home/file page loads: browser-to-web-service access works.
- A harmless Python cell returns a fresh result: the active notebook kernel responds.
- An overlay object can be constructed with `download=False`: software can read overlay metadata; no bitstream was programmed by that call.
- PYNQ reports an overlay loaded: the software runtime records an overlay identity. Record the filename and timestamp and understand what the specific PYNQ version checks.
- AXI register reads/writes or DMA transfer succeeds: the corresponding hardware path was exercised in that run.
- A matching `.bit` was programmed and a functional test passes: evidence applies to that exact bitstream identity and test conditions.

Do not turn a reachable page, visible files, a running-kernel badge, or an old notebook output into a claim that the target PL image is loaded or the accelerator works.

## 3. Handle browser and connector incompatibility

1. If Codex’s command or embedded-browser route cannot reach the board, report that as a limitation of that route. It does not prove the board or the user’s browser is unreachable.
2. Use an already available user browser/Edge tab through the supported browser connector when exposed. If it is unavailable, give the user a small, read-only notebook cell to run and ask for its exact output; do not invent a successful connection.
3. Confirm the active page and notebook before executing a cell. Start with a harmless expression such as `print("kernel check")`.
4. Keep notebook changes reproducible: use named cells or a dedicated notebook/script, capture raw output, and state whether the notebook autosaved.

## 4. Run a bounded hardware check

Before accessing PL registers or DMA, confirm that the task permits hardware access and that the live overlay matches the expected design. Record the overlay path and, when available, compare BIT/HWH hashes with the local build artifacts.

Use this progression:

1. Read the relevant status/control registers and DMA state without changing them.
2. Save pre-test configuration values and counters.
3. Check reset, enable, idle/busy, and error bits against the design’s register map.
4. Send the smallest useful input, then read back output, counters, and status.
5. Compare against a software/RTL golden model only for behavior that model actually represents.
6. Only within the current operation authorization and design-specific recovery contract, restore configuration registers and connection tables to their recorded baseline. Unknown ownership or state requires stopping, not automatic recovery. Read back the restored values and confirm idle/error state. Preserve useful counters when the test record requires them.
7. Store raw input/output words, decoded fields, timestamps, overlay identity, and recovery result in the project’s board-test record.

Do not start a cascade test from an unknown post-reboot state. Do not assume `Overlay.download()` is harmless: it reconfigures the PL. Do not use a possibly blocking DMA stop call as generic cleanup; check the driver and design-specific recovery path.

## 5. Report the result precisely

State what was observed, where it was observed, and when. Separate user-reported observations from tool-verified observations. Mark unknowns explicitly. A successful simulation, implementation, bitstream write, page load, or isolated AXI transaction is evidence only for that layer; it does not prove end-to-end board behavior.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
