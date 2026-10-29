# Current operation and reproduction boundary

Board: ALIENTEK LingHangZhe Zynq-7020 xc7z020clg400-2, OV5640 module, original working PYNQ2.7 SD image. The runtime relies on original vendor ov5640/video2lcd and IIC support. A stock unrelated PYNQ image is not claimed equivalent.

Current computation: full45669/1513231 strict FP32 network,721 inputs,dt5ms. PS captures/maps and manages DDR ring; PL advances neural state; PC audits and displays. Do not equate mathematical model time with wall time or GUI frames.

Known working deployment workflow: use the separately verified deployment package with Python3.12x64; start.cmd sets PC IPv4 and starts receiver8798; download fixed60second Notebook once, upload to board; after exclusive board release, operator restarts/runs that Notebook and confirms the prompt. Wait NORMAL_CAMERA_CLOSED plus PC PASS_ALL_SAVED_STATES and zero mismatches. Start another round only after clean close. Failure or unknown DDR ownership is not an automatic retry instruction.

This source repository currently lacks a completely portable packaging/build path. Do not substitute a stale embedded Notebook from source history. A clean-checkout build must resolve run_build.py dependencies and original vendor IP paths, regenerate session identities and notebook payloads, then validate PC-only protocol/self-check before operator device execution. No device was started for this audit.

Existing saved-run analysis is in saved_run_analysis.json; no new numerical verification was executed. Raw frame privacy/session credentials must be reviewed before publishing an example, with actual721 input/full state/reference identity retained.
