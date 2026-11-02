# Fresh PC deployment

Use Windows x64/Python3.12 and the original working ALIENTEK OV5640/PYNQ2.7 board environment. In this directory create/activate a Python environment and run `python -m pip install -r requirements-check.txt`. Packages are fetched from the package index; the public source tree does not include wheels. Then `python run.py --check-only` checks files and recomputes the saved721-input/full45669-state sample on CPU. This does not use a camera,GPU or board. Raw camera pixels are intentionally not distributed; input mapping is not retested by this public sample.

Start with `python run.py --ip YOUR_PC_IPV4` (or start.cmd after activating your environment). The existing accepted entry generates fresh session/key/Notebook identities locally and opens the receiver page. Download its fixed Notebook once, upload to the user's original board Jupyter, and run only after the operator confirms exclusive ownership. Wait for NORMAL_CAMERA_CLOSED and PC PASS_ALL_SAVED_STATES/zero mismatches before another round. Use the page's next-round action and the same fixed Notebook. On failure preserve the kernel/DDR/records; no automatic retry or reprogramming.

First deployment uses the current exported app/pc and app/assets, not the older layout in the original20261027 package. Firmware pair is unchanged. The included original reference.exe is paired with reference.cpp and host_reference.cpp. Rebuild it for another host before attempting operation there. selfcheck is Windows-only until that rebuild is supplied.

The Notebook template is deliberately unconfigured. No checked-in token,active session or old camera frame is used. checks/identity.json names the existing operator run and step; checks/state.bin is its saved full state. Offline reference equality is not a new board result. evidence/last_board_result.json is a historical summary, not newly executed data.

2026-11-02 repair: Python special constructors restored from the accepted runtime; current pages retained. The pinned official CPU flow artifact is now included with its original SHA; PyTorch2.5.1 is required for that display readout. The neural model, firmware and numerical state update are unchanged.

## Two dependency profiles

For `--check-only` or `--prepare-only`: `python -m pip install -r requirements-check.txt` (numpy/Pillow/psutil; no torch).

For the full display with the official CPU optical-flow decoder: `python -m pip install -r requirements-full.txt` (adds torch==2.5.1). `requirements.txt` aliases the lightweight check profile. Install the full profile before starting a complete camera/display experiment.

Git checkout uses .gitattributes to preserve every byte-pinned payload regardless of core.autocrlf. No hash check is disabled. The included executable is Windows x64; [reference build instructions](REFERENCE_BUILD.md) describe rebuilding the x86/x64 reference from source. Linux and ARM are not newly validated by this documentation.
