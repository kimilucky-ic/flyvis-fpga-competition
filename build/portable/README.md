# Portable build preparation

This export closes the hidden dependency on the author's original work directory. It preserves the eight actual RTL modules, all50 images, the camera BD seed and five original stage scripts. Only fixed initialization-file path strings in RTL were replaced by `neural/<file>`; arithmetic, topology and update order were not edited. Original/exported identities are recorded in relocation_manifest.json.

## Prerequisites

Vivado2026.1 with xc7z020clg400-2 support. The complete 56-file platform dependency snapshot is included at [src/vendor](../../src/vendor/README.md), and its bytes match vendor_requirements.json. Neural RTL and images are included once at [src/neural](../../src/neural/README.md). Original notices and the third-party scope in [vendor dependency review](../vendor_dependency_review.md) apply. The source snapshot is the known-good local platform input set; an independent clean-machine Vivado source-to-BIT build has not been run in this reorganization.

## Prepare without running Vivado

From this directory:

```text
python prepare.py --vendor-dir ../../src/vendor --output D:/flyvis_build
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

## Consolidated current source

Neural RTL/images are stored once at [src/neural](../../src/neural/README.md). The matching 56 platform dependencies are at [src/vendor](../../src/vendor/README.md). This command validates those exact bytes before preparing the build. Original notices and license scope remain applicable. Fresh source-to-BIT execution is not claimed by this file consolidation.

[Complete 56-file dependency map](vendor_file_map.md) lists every required relative path, its bundled location and SHA256. From the repository root use `python build/portable/prepare.py --vendor-dir src/vendor --output ../flyvis_build`; from this portable directory use the relative command above.
