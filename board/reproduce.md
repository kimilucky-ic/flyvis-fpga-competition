# Current operation and reproduction boundary

Board: ALIENTEK LingHangZhe Zynq-7020 xc7z020clg400-2, OV5640, original working PYNQ2.7 SD environment. Current computation retains all 45,669 nodes, 1,513,231 connections, strict FP32 and 5ms model steps. PS handles capture/input mapping and DDR; PL advances states; PC audits and displays. Camera mapping is `direct-grey-center-square-area/v2`, not an unverified claim of equality to historical GPU BoxEye inputs.

## One PC entry and one operator Notebook

1. Follow [runtime/README.md](runtime/README.md). Use Windows x64/Python3.12, create/activate a Python environment in `board/runtime`, then run `python -m pip install -r requirements.txt`.
2. Run `python run.py --check-only`. It recomputes the saved 721-input/45,669-state sample using the included independent CPU reference. This is software verification, not a new camera or board test. Sample identities are in `runtime/checks/`.
3. Only for an operator-requested experiment: run `python run.py --ip YOUR_PC_IPV4` (or `start.cmd` in the activated environment). This creates fresh session identities and opens the existing receiver. No token copying or second PC coordinator is needed.
4. Download the generated fixed Notebook, upload it to the original board Jupyter, then run it manually only after the board is exclusively released and its loading/allocation prompt is confirmed. Do not execute embedded historical Notebooks from other source snapshots.
5. Wait for board `NORMAL_CAMERA_CLOSED` and PC `PASS_ALL_SAVED_STATES`, with zero mismatches. Use the page's next-round action and the same fixed Notebook only after normal close. Failure, unknown ownership or unknown commit state requires preservation and diagnosis, not automatic retry/reset/free.

The PC saved-sample check and isolated fresh-session preparation have passed previously; [software preparation evidence](../sim/public_runtime_prepare.json) is distinct from a new live run. Raw camera pixels are not distributed; this sample does not retest image mapping. Existing [saved-run analysis](saved_run_analysis.json) retains its historical evidence level.

## Rebuild the firmware

See [portable build](../build/portable/README.md) and [official vendor acquisition and identity instructions](../build/vendor_dependency_review.md). Obtain matching vendor dependencies, validate them, prepare a fresh output and run the documented Vivado stages only when authorized. Current source-to-BIT reproduction on another machine is not certified. No GPU, service, camera, board or EDA was started for the documentation update.
