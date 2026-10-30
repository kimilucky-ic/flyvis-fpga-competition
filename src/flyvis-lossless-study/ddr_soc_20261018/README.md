# Candidate 11: full-network PS7/HP0 DDR snapshot SoC

2026-10-18 user-authorized local CPU/RTL verification and Vivado synthesis/place/route only. No board, GPU, HLS, camera or GUI operation. Preserve the accepted `hole_pipeline_20261016` release and the sealed `ddr_snapshot_20261018` prototype.

This candidate fixes the missing PS-facing path of the DDR prototype: ordered input admission, bounded one-step control, a generated AXI4-to-AXI3 HP0 connection, and a coherent publication descriptor. Neural graph generation, FP32 arithmetic and old-state feedback are unchanged. The simpler accepted MMIO full-state readback remains intact as rollback; its observed 1.687-second first-step readback motivates the separate bulk-DDR path.

## Completed local implementation

**PASS_FULL_DDR_SOC_100MHZ_LOCAL_IMPLEMENTATION_ONLY**. Complete SoC synthesis is `soc_r8`; its identical checkpoint was routed in `soc_r9` after an earlier route attempt stopped under system commit pressure. `AUDIT.json` checks source identities, both prior seals, complete IP resolution, actual reports and platform address/clock/reset bindings.

Vivado **2026.1.1**, `flyvis_ddr_wrapper`, `xc7z020clg400-2`, fully routed: **7,531 LUT (14.16%), 7,092 FF (6.67%), 102 BRAM36-equivalent (72.86%), 2 DSP (0.91%), no latches**. Compared with the accepted MMIO release: +780 LUT, +942 FF, unchanged BRAM/DSP. 16,068/16,068 routable nets routed; zero routing errors. All twelve `check_timing` categories report zero issues.

10-ns clock: **WNS +0.075 ns, WHS +0.056 ns, WPWS +3.870 ns**; zero setup/hold/pulse failures. Margin is narrow. Worst setup is high-fanout peripheral reset to neural current BRAM write-enable (4,791 loads, 95.925% route delay), not an arithmetic-stage failure. This local timing result does not measure the physical clock or promise frequency headroom beyond 100 MHz.

DRC has **0 Error / 0 Critical Warning and 8 ordinary warnings**: five inherited DSP pipeline advisories; two unused-LUT-input checks in the newly generated vendor AXI conversion FIFOs; one no-routable-load check covering 22 vendor FIFO nets. All warnings remain visible, with no waiver or severity reduction. Generated AWID/WID explicitly pad the top two HP0 ID bits with zero; only ID 0 is issued, and no valid issued ID aliases on narrowing returned BID. Native PS7/fault-injection/gate-level or physical validation of that integration has not run.

Synthesis completed in 204.766 seconds, peak owned private memory 3,089.824 MiB; route completed in 208.297 seconds, peak owned private memory 2,083.594 MiB. These are host tool execution times, **not neural step times**. Command logs and sampled physical/commit/owned-memory figures remain in the attempt directories. Final artifacts are `soc_r9/release/ddr_soc_routed.dcp`, `flyvis_ddr.hwh` and the complete routed reports. No BIT/XSA was generated.

## CPU/RTL evidence

- `control_r1/summary.json`: full-network behavioral RTL, three model steps, two feedback transitions, 137,007 state words and 2,163 actual input words exact. First-step state matches the frozen state accepted from the human board run. The test deliberately holds a GP0 read response for 2,201,469 cycles while the next complete neural step and DDR publication finish. This uses a CPU DDR responder, **not native PS7 VIP or physical DDR**.
- `CPU_CONTROL_RESULT.json`: nine focused CPU tests of the injectable PS API, no PYNQ import or hardware connection. Covers identity before writes, bounds, complete ordered input, capacity stop, timeout/uncertain-write failure with no automatic retry, coherent descriptor readers, explicit cache callback, and all three actual RTL DDR records. Display skips frame 1 while audit retains frames 0, 1 and 2.
- `AUDIT.json` binds the successful synthesis and route above; failed/stopped attempts remain separate. A stopped synthesis or a validated BD is not routed timing success.

Strict FP32 operator acceptance and all-edge-order coverage are reused by exact source identity from the sealed predecessor. This new control test checks every resulting state/input word; it does not claim a fresh ordered-edge trace or post-synthesis numerical-equivalence proof.

## PS and DDR interfaces

Target: `xc7z020clg400-2`, FCLK0/GP0/HP0 at nominal 100 MHz, 64-bit HP0, vendor PS7 DDR/MIO parameters preserved. GP0 control address is **0x43C40000 / 4 KiB**, ABI **0x00110004**. This is a distinct address and ABI from the old accepted MMIO candidate.

`rtl/flyvis_ddr_soc_ip.sv` accepts independent AXI-Lite address/data handshakes and holds read/write responses until accepted. Full-word writes only. The 721 input words must be written in ascending index order; duplicates, gaps and partial writes are rejected without advancing admission. A new step requires a complete frame, a clean configured engine and space for its next audit record.

Commands at 0x00: 2 restore initial neural state, 4 configure an audit session, 1 execute exactly one step, 8 latch the complete current publication tuple. No display acknowledgement gates the neural engine. Illegal or busy writes receive SLVERR and increment 0x28.

Registers: 0x04 DDR base; 0x08 exclusive end; 0x0C slot count; 0x10 status; 0x14 committed count; 0x18 staged input count; 0x1C first frame ID; 0x20 latest core-phase cycles; 0x24 engine error flags; 0x28 rejected writes; 0x2C caller session cookie; 0x30 nodes; 0x34 edges; 0x38 ABI; 0x3C record stride; 0x40 expected next frame. Input words occupy 0x400 through 0xF40.

Status bits 0..6: busy, clean initial state, configured, journal full, complete staged input, publication valid, engine error. Configuration is frozen after admission. Restoring/reusing a configured audit session is forbidden by the PS API; recovery after an uncertain hardware transition requires reconciliation rather than an automatic reset/retry.

After command 8, stable descriptor fields are: 0x80 sequence; 0x84 record address; 0x88 frame ID; 0x8C cycles; 0x90 count; 0x94 session cookie; 0x98 errors; 0x9C nodes; 0xA0 edges. Capture is a single RTL clock edge even when a new record publishes concurrently. `ddr_control.py` serializes only capture/read between threads. One process and one shared API object own MMIO; one producer owns neural-control/input writes. Bulk copy, validation and rendering run outside the descriptor lock.

The 188,416-byte append-only record is unchanged from the sealed prototype. It stores all 721 actual input FP32 words at offset 128 and all 45,669 post-step FP32 state words in global-ID order at offset 4096. The final 128-byte header is written only after payload responses; publication waits for the final header OKAY response. DDR slots are never reused within a session. At full/error/timeout the next neural step is stopped; there is no silent drop, wrap or retry. 485 slots require 91,381,760 bytes (87.1484375 MiB), a capacity calculation rather than a real allocation or bandwidth result.

## PS reader boundary

`ddr_control.py` is an injectable interface, not a board launcher. It imports no PYNQ, opens no network and allocates no DDR. A future human-authorized board binding must own a suitable contiguous physical DDR region and prove allocation identity, mapping, cache visibility and memory ordering. `copy_published` requires an explicit invalidate/order callback before copying immutable bytes. Copying alone does not validate a record: call the existing sealed `snapshot_records.decode_record`, retain every audit frame in order, and hand only the newest verified reference to display.

Display rendering can skip old frames without removing their audit records. This finite journal provides decoupling from display; it does not provide unlimited storage or immunity from physical DDR backpressure. A new bitstream, real HP0 throughput, cache semantics, sustained frames/s and physical multi-step feedback remain unverified in this phase.

The new record's core-phase counter is 2,199,975 in each tested step (21.99975 ms at nominal 100 MHz); it excludes the internal input-feed phase and final DDR/header publication. The accepted old 2,201,418-cycle/22.01418-ms counter used a different boundary. Neither is this candidate's measured end-to-end step time, so their difference is not presented as a speed improvement.

## Rebuild and inspect

`build_soc.tcl` creates a new in-memory BD and performs global full-SoC synthesis; `source_mgmt_mode All` and `synth_checkpoint_mode None` follow AMD UG994's module-reference/non-project flow. `route_soc.tcl` opens the complete synthesis checkpoint in a fresh process and performs opt/place/phys-opt/route plus resource, timing, constraint, route and DRC reports. It generates no BIT/XSA and performs no hardware action. The source scripts and generated BD/HWH/checkpoints remain the independently inspectable project artifacts.

The source still deliberately references the immutable `hole_pipeline_20261016/images` by absolute path. `BASELINE_BEFORE.json` and `BASELINE_AFTER.json` bind that dependency and verify both old seals; this is a local rebuild, not a portable relocation package.

CPU commands (workspace root, fly Python environment):

```powershell
& '../fly/.venv/Scripts/python.exe' -B 'flyvis-lossless-study/ddr_soc_20261018/tests/test_control.py'
& '../fly/.venv/Scripts/python.exe' -B 'flyvis-lossless-study/ddr_soc_20261018/audit_soc.py' --tag soc_r9
```

Vivado commands are retained in each attempt's `*_console.log`; exact tool/source hashes, resource sampling and exit reasons are retained alongside. The guarded launcher uses one synthesis job and below-normal priority. After the user's explicit “直接启动vivado”, direct mode retains a 6-GiB owned-memory limit, 1-GiB available-commit floor, 128-MiB physical floor sustained for 10 seconds and 3600-second stage bound; it records pressure below 512 MiB rather than stopping immediately. It changes no Windows paging configuration and never stops an unrelated process.

Attempt history: r1/r2 launcher sandbox access failures; r3 another Vivado active before launch; r4 project flow stopped by its 512-MiB host-headroom guard; r5 not launched below its initial 3.3-GiB preflight; r6 non-project module-reference setup missing automatic source management, fixed in build Tcl only; r7 passed that setup then stopped at its original 512-MiB guard; r8 synthesis passed but its first route stopped at 985-MiB available commit; r9 reused the exact passed synthesis DCP and completed routing. All attempt evidence is retained. Passing CPU/RTL evidence alone is never labeled synthesis, routing or board success.

AMD references: [non-project script](https://docs.amd.com/r/en-US/ug994-vivado-ip-subsystems/Non-Project-Script), [module references in non-project flow](https://docs.amd.com/r/en-US/ug994-vivado-ip-subsystems/Module-Reference-in-a-Non-Project-Flow), [AXI4-to-AXI3 conversion](https://docs.amd.com/r/en-US/pg059-axi-interconnect/AXI4-to-AXI3-Converter).
