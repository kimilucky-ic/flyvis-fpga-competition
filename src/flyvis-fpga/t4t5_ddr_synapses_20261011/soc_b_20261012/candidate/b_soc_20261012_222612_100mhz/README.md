# FlyVis B SoC candidate — board not run

2026-10-12. Vivado2026.1.1, xc7z020clg400-2, PS7 FCLK0 100MHz.
Actual production BD simulation and full SoC routed timing passed. See [acceptance report — 历史依赖未随包提供](../../../../../../report/archive_dependencies.md#missing-058) and [file identities — 历史依赖未随包提供](../../../../../../report/archive_dependencies.md#missing-059).

flyvis_b.bit and flyvis_b.hwh are the matching load pair; the ZIP contains exactly these two files. The ARM controller is provided separately and does not download an Overlay. Its constructor allocates and flushes a DDR edge buffer only when the caller explicitly invokes it on an already-loaded, separately authorized Overlay.

Production H5768/S16402/E433880/W645; GP0 base0x43C20000, 128KiB; HP0 64-bit. Keep all raw edge records including zero effective weights. Load one common old state, validate result identity and candidate values, and let the caller coordinate GPU/PL COMMIT.

This package has not been programmed to any board. Actual DDR bandwidth, ARM transfer time and full application latency are unmeasured. A later board test requires board availability and separate explicit authorization for the exact operation.
