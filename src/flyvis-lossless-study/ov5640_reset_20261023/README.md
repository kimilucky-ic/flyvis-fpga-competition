# OV5640 synchronous capture/FIFO reset candidate

Offline candidate only. User explicitly authorized CPU/RTL and Vivado implementation; no physical board, camera access, GPU, BIT download, MMIO, reset or DMA was performed. Module family confirmed by user: 正点原子OV5640. Physical baseboard revision and module oscillator remain unverified.

## Concrete changes

The prior candidate used asynchronous-reset capture registers in video FIFO RAM write-enable logic (three REQP-1839 warnings). cmos_capture_data now keeps only the reset synchronizer asynchronous; functional pixel/line/warmup registers reset on PCLK edges. camera_guard provides reset sequencing for the video and AXIS domains, and a sticky overflow status. The final video FIFO reset itself is also a PCLK register with synchronous assertion/release; if PCLK is stopped, AXIS is reset within one FCLK cycle plus register propagation and video reset completes when PCLK resumes. The status acknowledgement does not falsely claim that stopped PCLK has performed a synchronous reset.

A small AXI GPIO controls the capture reset. It is preferable to relying on software to ignore stale/overflowed FIFO contents. Neural RTL is not involved. Default RUN=0 holds capture stopped. The PS side first grants a non-held buffer and arms one-frame VDMA, then RUN=1 releases capture. Completion requires VDMA frame completion AND halted; then normal RUN=0 quiesces the video source, waits for the reset acknowledgement, invalidates/copies through the injected backend, checks sticky fault again, and only then publishes the immutable frame. Overflow/failure retains the WRITING lease, latches the software failure and does not retry, clear faults, or perform global reset. Normal stop does not erase a previously latched overflow.

The existing CapturePool and BoundSteps path remains the owner of selected-frame/actual-721-input/neural-step binding. No neural code or FP32 arithmetic was rewritten. 58 neural RTL/image files are checked byte-identical to the preceding candidate. New constructor OneFrameVdma requires CameraControl; the prior uncontrolled continuous-stream adapter is not an accepted way to use this candidate.

## Verification and boundaries

CPU.log/CPU_RESULT.json: 9 register-model tests, including overflow before completion, late fault during cache copy, no publication/retry, halted-before-copy, stop-before-copy, held buffer exclusion and bounded IIC errors.

sim_r6 is the passed build_r7 source-matched video test, using actual Vivado Video In 5.0.8 and XPM asynchronous FIFO models (1024 entries), not a handwritten FIFO substitute. It checks RGB565 expansion and all AXIS pixel bits/SOF/EOL, backpressure, reset with bytes/FIFO data in flight, stopped-PCLK reset/resume, actual FIFO overflow, sticky fault across normal stop, and restart into a complete 640x480 frame (307200 pixels). FPGA synthesis/physical timing/metastability/real sensor signals are distinct evidence.

sim_iic_r1 uses the actual generated AXI IIC 2.1.12 configuration at 100MHz/100kHz, with a behavioral ACK slave and assumed 300ns rise/20ns fall digital line model. One write to 0x3008 is byte-checked (78 30 08 82). Low/high/setup minima are 5300/5010/4900ns; minimum period 10310ns. This is a write-path timing test, not actual sensor read/initialization or analog RC verification.

Each new start currently repeats the inherited 11-VSYNC warmup. This is correctness-first single-frame capture, not continuous camera frame-rate validation. The known 22.01418ms neural cycle estimate is not whole camera-system latency. ARM execution, cache barriers, actual VDMA/DDR arbitration and full-state oracle with real camera input remain unverified.

## Timing basis

TIMING_BASIS.json and source PDFs record the default 0x4740=0x20 / falling-edge output basis. Final DVP design envelope is PCLK72MHz, launch falling edge, input delay -0.5..2.0ns, setup/hold uncertainty 0.25/0.10ns. Frequency follows the official driver comment for a 24MHz module oscillator. The delay envelope combines sensor tCO and relative board skew and IS NOT guaranteed by the available datasheet or established by measurement. It must be verified for the actual module/board before physical timing signoff.

SCCB is asynchronous/open-drain. Output propagation is bounded to20ns from valid IIC sequential-cell startpoints; vendor first-stage CDC input false paths are retained, and physical input propagation is separately reported/audited against20ns. No fictitious synchronous SCL-to-FCLK relationship is imposed. V3.9 schematic shows R110/R111 4.7kohm to3.3V; under an ideal single-pole model, <=300ns rise would require bus capacitance <=75.33pF. Actual pullups, module parallel resistors, capacitance, voltage thresholds and physical revision are not measured.

PCLK uses official W14/non-CCIO assignment and retains CLOCK_DEDICATED_ROUTE FALSE; PLCK-12 remains an explicit exception, not a clean clock-placement signoff.

## Rejected attempts and reproducibility

sim_r1/r2 failed simulator setup; sim_r3 passed the earlier video-reset form; sim_r4 caught declaration order before simulation; sim_r5 passed build_r6; sim_r6 passes the registered-request build_r7. build_r1/r2 stopped at GPIO-value format/reset polarity metadata. build_r3 synthesized but XDC nested source was unsupported. build_r4 stopped on a missing max-delay startpoint. build_r5 is REJECTED: invalid Q startpoints segmented timing paths and the FIFO reset still had one async-control warning. Its COMPLETED marker is NOT acceptance; see REJECTED_R5.json. All failed logs retained. build_r6 removed all REQP-1839 warnings and restored full neural timing analysis, but FAILED acceptance: two first-stage status CDC paths were not exempted and CDC-10 identified combinational reset gating. build_r7 registers the request in FCLK and constrains only the two first-stage CDC D pins. The first launch was blocked with 664.7MiB host memory available. The user released resources to3936MiB; sim_r6 then passed in18.328s, and build_r7 synthesis/route resumed. build_r7 full SoC synthesis and route passed the report audit: 10018LUT,10675FF,109BRAM36eq,2DSP; 100MHz WNS+0.333ns/WHS+0.042ns/WPWS+3.870ns,32545 setup/hold endpoints and zero failing endpoints. Camera conditional72MHz WNS+4.529/WHS+0.055ns. CDC reports6 CDC-3 and2 CDC-9 information items, no Warning/Critical. FIFO bus-skew margins+9.281/+9.016ns; REQP-1839 count0. DRC retains11 Warning and2 Advisory, including official non-CCIO PCLK exception. Synthesis292.078s/peak3304.92MiB; route312.250s/peak2196.90MiB. Both exited0 without guard stop.

Reproduce CPU: fly/.venv/Scripts/python.exe -B <candidate>/test_io.py.
Reproduce final video simulation or IIC test: same Python run_guarded.py sim_r6 sim / sim_iic_r1 sim, after copying source test inputs into a new empty simulation directory (avoid overwriting evidence).
Reproduce implementation: copy build_r7 authored .sv/.v/.hex/.tcl/.xdc/.ps1 into a fresh ASCII build directory with tmp/, then run_guarded.py <new-directory> synth followed by route. Requires installed Vivado2026.1.1 and its normal license. These are local offline jobs only. Source waveform and testbench are archived; no WDB waveform dump was requested.

Raw commands, logs, tool version, DCP, effective XDC and reports are retained. No new reusable Skill was created: the physical camera workflow has not been reproduced on hardware. Rollback is selecting the previous sealed candidate; no previous candidate was modified.

FINAL_RESULT.json records accepted offline CPU/RTL/full-SoC routed evidence only. check_timing reports zero unclocked/unconstrained internal endpoints, but two no_input_delay ports remain: asynchronous SCCB SCL/SDA, with vendor input synchronization and explicitly documented propagation audit. This is not complete external-interface signoff. No new whole-network FP32 numerical regression or gate-level equivalence was run: neural sources/images remain byte-identical. Old2034 sealed members were rechecked unchanged. See FINAL_MANIFEST_SHA256.json for selected authored sources and evidence; generated tool caches are not a release package.
