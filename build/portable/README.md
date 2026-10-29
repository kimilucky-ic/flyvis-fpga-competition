# Portable build preparation

This export closes the hidden dependency on the author's original work directory. It preserves the eight actual RTL modules, all50 images, the camera BD seed and five original stage scripts. Only fixed initialization-file path strings in RTL were replaced by `neural/<file>`; arithmetic, topology and update order were not edited. Original/exported identities are recorded in relocation_manifest.json.

## Prerequisites

Vivado2026.1, xc7z020clg400-2 support, and the original ALIENTEK official camera reference dependencies. vendor_requirements.json lists56 exact files and hashes needed from the vendor reference working directory (base.xdc, vendor IP component metadata/RTL and associated files). The existing known-good environment has that directory at C:/fpga_work/line11_v261_20261026/vendor. This local path is an acquisition example, not a runtime requirement in the new export. Redistribution of these third-party inputs remains pending license review; hashes alone do not deliver those sources. Until a permitted retrieval/distribution route is supplied, this is not a complete public clean-build deliverable.

## Prepare without running Vivado

From this directory:

```text
python prepare.py --vendor-dir D:/vendor_camera --output D:/flyvis_build
```

The command verifies every dependency and RTL/image hash before creating a fresh output directory. It never starts EDA, camera or hardware. An existing output or bad input stops before copying. Do not reuse output from a failed heavy build without diagnosis.

## Operator-requested build

Only when a heavy build has been authorized, run from the newly prepared output:

```powershell
./launch.ps1 -Vivado D:/2026.1/Vivado/bin/vivado.bat -Stage migrate3
./launch.ps1 -Vivado D:/2026.1/Vivado/bin/vivado.bat -Stage combine
./launch.ps1 -Vivado D:/2026.1/Vivado/bin/vivado.bat -Stage synth
./launch.ps1 -Vivado D:/2026.1/Vivado/bin/vivado.bat -Stage route
./launch.ps1 -Vivado D:/2026.1/Vivado/bin/vivado.bat -Stage bitgen
```

Stop on any error. Inspect utilization, timing, DRC/CDC and bitgen logs; do not infer board correctness from implementation. This export has CPU file preparation validation only. No fresh Vivado build was run to prove clean-machine equivalence, and generated BIT need not be byte-identical to the archived accepted BIT.

No stage connects to a board. Physical loading remains a separate operator action. The camera external timing budget and non-dedicated PCLK exception remain conditional; portable packaging does not establish electrical signoff.
