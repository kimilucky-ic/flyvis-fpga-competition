# Candidate 11 DDR offline release — 2026-10-18

**Local BIT/HWH package and CPU acceptance preparation only. No board authorization, connection, programming, reset, MMIO, DMA or physical neural steps performed.** Full 45,669 nodes / 1,513,231 connections, strict binary32 RNE and nominal 100 MHz are unchanged. The previously sealed releases remain the rollback versions.

`flyvis_ddr.bit` is generated directly from the accepted `ddr_soc_20261018/soc_r9` routed DCP, without new synthesis/place/route or RTL edits. Vivado2026.1.1 checks the device, fully resolved SoC, 10-ns clock, timing and DRC before bit generation. New BIT SHA256: `d365f41da4b52dc8dbd0ba751f8691da448607747a6bcf04e619ab465d956b66`. HWH SHA256: `69a4332593e32852aec9dbc7b177341f3303af067ee1f182c44152744f8598f1`. Target `XC7Z020-2CLG400`, top `flyvis_ddr_wrapper`, GP0 `0x43C40000`, ABI `0x00110004`, 64-bit HP0. Neither file has been loaded to hardware.

The accepted routed evidence remains 7531 LUT / 7092 FF / 102 BRAM36-equivalent / 2 DSP, WNS+0.075ns / WHS+0.056ns / WPWS+3.870ns. Setup margin is narrow. The eight ordinary DRC warnings are retained and documented in `release_info.json`/reports; there is no waiver or severity reduction. BIT generation is another local evidence layer, not numerical equivalence or a board result.

## Safe default and CPU check

After extracting the full offline ZIP, the default check is:

```text
python offline_check.py
```

It verifies every package file, fixed BIT/HWH hashes, BIT header/payload length/sync, HWH target, FCLK/HP0 and GP0 address plus complete three-step vectors. It imports no PYNQ and does not access a board.

Explicit local CPU fixture replay (choose a NEW output directory):

```text
python cpu_replay.py cpu_result_new
```

This uses saved behavioral-RTL DDR bytes as fake PL output and an independent serial strict-FP32 full-network CPU oracle as expected states. Three steps use the original frozen stimulus sequence frame0, frame1, frame0, checking every 137007 state and 2163 input words. First-step oracle must agree with the previously accepted original first-state file. There is no GPU or runtime CPU-neural fallback, and the replay always identifies itself as `CPU_MOCK_ONLY` / `board_result=false`.

## DDR and cache ownership

`ddr_memory.py` requests exactly `slots * 188416` bytes through an injected allocator with `shape=(bytes,), dtype='u1', cacheable=True`; the future real binding uses `pynq.allocate`. It checks a one-dimensional contiguous byte buffer, a 4KiB-aligned allocator-returned physical address, exact size and the design's 1MiB..1GiB HP0 range. No hardcoded physical address, assumed CMA capacity, smaller fallback allocation, or retry is used. Three acceptance slots need 565248 bytes; 485 slots would need 91381760 bytes / 87.1484375MiB and have NOT been allocated or tested here.

Before PL can write, CPU clears the allocation once, flushes it, executes a barrier and marks the NumPy view read-only. It never flushes/writes that allocation after arming. After a record's final write response and publication, the reader orders access, invalidates ONLY that complete committed slot, executes another barrier and makes an immutable byte copy before validation. Slots are page-aligned/non-overlapping. Physical HP0/XRT/cache behavior remains to be tested.

The future `pynq_allocator_and_barrier` requires explicit operator authorization and ARMv7/PYNQ2.7. It compiles the included tiny `arm_barrier.c` with the installed target compiler in a fresh owned directory and uses `dsb sy`. Missing compiler or unsupported runtime fails before allocation. **The target ARM helper has not been compiled/executed on the board here**; CPU tests inject a traceable barrier/cache model, and never invoke the real binding. The binding does not program/reset PL, create MMIO or start a step.

An armed allocation keeps a strong process-wide reference even when exceptions unwind or caller references are lost. It cannot be freed through automatic/finally cleanup. Unknown STEP acceptance, cache failure, comparison failure or disk failure leaves it retained for reconciliation; do not restart its kernel or reset/retry as recovery. Explicit normal release is allowed only after a full idle/error-free bounded session and all raw records/receipts have been durably saved. XRT buffer/mapping lifetime is used; deprecated PYNQ2.7 `.close()` is not treated as a free operation.

## Full-state acceptance and asynchronous display

`AcceptanceSession` reuses the sealed control API/record codec. One producer owns neural writes; a separate auditor can copy and validate immutable completed records later. Cache operations, all-state comparison, file fsync and display do not hold the producer lock. Each actual input must equal its frozen input; all 45669 FP32 state words compare by exact uint32 bits against the independent oracle, preserving global IDs. Counter/header/publication identities must agree. Raw records are saved before validation, followed by mismatch diagnostics and chained receipts. A damaged last neuron is not hidden by sampling or aggregate checksums. Failure stops new submissions and retains uncertain DDR; there is no reset/retry/CPU inference/display fallback.

The display uses only verified immutable snapshots. It may skip old references while audit retains every completed record; journal capacity refuses the next neural step before overwrite. This finite design does not promise infinite storage or immunity from DDR backpressure. CPU timing numbers measure mocks; no physical step latency, frames/s, power or real-time performance is claimed.

**Initialization boundary:** ABI0x00110004 has no separate full initial-state readback port. The included `initial_state.bin` documents the oracle input. This package checks RESTORE completion/clean status and every complete post-step state; it cannot claim an independent 45669-word initial-state hardware comparison. Adding that port would require a separately reviewed RTL candidate and new timing/verification, so no RTL was changed here.

## Before any future physical run

Current disposition is **OFFLINE_PACKAGE_ONLY / EXECUTION_AUTHORITY_NONE**. Do not run this ZIP as approval to program the board. A separately authorized human preparation must establish exclusive board ownership, matching board/device, exact new loaded BIT/HWH and fresh unused ABI. Live PS clock/source/dividers/lock and HP0 64-bit port settings must be checked before allocation/configuration. Raw PYNQ150MHz under a50MHz software reference must not be substituted for the board's33.333333MHz reference, and no clock/HP0 register rewrite is supplied here. PYNQ2.7's Zynq-7000 load path does not establish that boot-time HP0 width matches this HWH.

The prepared software flow is: construct the driver from the explicitly approved existing MMIO, create the owned allocation/barrier, `start()` once, bounded `produce_next()` calls, independent `audit_next()` calls for EVERY step, `finish()` and then explicit normal release. A caller may use `OPERATOR_PHYSICAL_READS_UNATTESTED`, but this component still does not emit a complete board-identity PASS; that requires the external operator context and PC artifact review. No physical launcher/download or automatic board action is included.

No new generic Skill is claimed. The project-specific workflow and untested target boundary are recorded here. Primary API sources: [PYNQ2.7 buffer lifetime/cache methods](https://github.com/Xilinx/PYNQ/blob/v2.7.0/pynq/buffer.py), [XRT allocation and sync](https://github.com/Xilinx/PYNQ/blob/v2.7.0/pynq/pl_server/xrt_device.py), [PYNQ2.7 bit parsing and port-width handling](https://github.com/Xilinx/PYNQ/blob/v2.7.0/pynq/pl_server/embedded_device.py). These are API references, not physical validation.
