---
name: fpga-uart-link-validation
description: Diagnose and validate a direct FPGA PL UART connection through a USB-UART bridge using raw binary frames. Use when a board design exposes UART without PYNQ/Jupyter control, a terminal shows question marks, or a TX/RX frame must be checked without reprogramming the FPGA.
---

# FPGA Direct UART Link Validation

This is a project-derived candidate workflow. In the current fly/Zynq project, source inspection and UART loopback simulation are available, but the physical board's raw HEX response has not yet been captured. Do not describe it as board-validated until that evidence exists.

## 1. Identify the physical UART path

1. Confirm the exact board and revision, FPGA part/package, PL UART pins, connector, USB-UART bridge, jumpers, ground, and voltage standard from the matching schematic and XDC.
2. Confirm the loaded BIT identity from project/build evidence and the user's current report. Do not reload a known-running design just to inspect UART.
3. Choose the correct control path. If the design is direct VHDL in PL with a physical UART, use the serial path; do not apply Jupyter/PYNQ overlay or AXI/DMA steps unless the design also exposes those interfaces.
4. Read the UART RX/TX RTL and top-level controller to learn what starts transmission, whether commands are echoed, and which opcodes change persistent state.

## 2. Calculate and configure the serial link

1. Derive baud from the actual PL clock and RTL divisor/counter. Compare it with the terminal's supported baud and note the error.
2. Confirm data bits, parity, stop bits, flow control, COM port, TX/RX pin mapping, and any required bridge jumpers.
3. Enable raw HEX/hexadecimal display for both transmit and receive when the protocol contains binary bytes. Do not type printable hex characters unless the terminal is explicitly in HEX-send mode.
4. Before a command, inspect RTL for startup behavior. An empty RX window can be expected if periodic TX starts only after a valid receive event.

## 3. Use a safe first exchange

1. Capture the idle state first: timestamp, COM port, terminal settings, board-reported loaded image, and whether any command has already been sent.
2. Verify the exact start opcode and its byte encoding from the active controller RTL. If it changes state, do not repeat it blindly.
3. Only send a state-changing opcode when the user has authorized that board action. Send the smallest start/handshake command and capture the raw response before trying a data stimulus.
4. After the first frame is understood, send one minimal stimulus followed by its required end-of-step/commit marker. Capture TX and RX bytes separately.
5. Do not reset or reload the FPGA to recover state unless the user authorizes that specific action and the recovery requirement is understood.

## 4. Decode and classify the evidence

- Decode bytes using the RTL's marker bits, field widths, signedness, ordering, and frame terminator. Reconstruct only the bits actually transmitted; do not label a truncated field as the full source value.
- Preserve original HEX bytes and a separate decoded interpretation. A readable terminal string or question mark is not a decoded frame.
- Separate evidence: baud calculation and source inspection; UART loopback simulation; physical electrical RX/TX; decoded full-network response. Each proves a different layer.
- If the expected frame does not appear, check in this order: terminal raw-byte mode, actual COM port and settings, start condition/opcode, cable/jumper route, pin constraints, clock/divisor, RTL TX enable, then measure RX/TX with an instrument if authorized.

## 5. Record the test

Capture board/revision, FPGA part, BIT hash or identity, source revision, schematic/XDC references, clock and baud calculation, COM settings, jumpers, raw TX bytes, raw RX bytes, frame timing, decoder version, output interpretation, and recovery state. Mark absent HEX data as missing; do not infer it from a screenshot of `?` characters.

## Project-specific observation (not a universal protocol)

The fly Zynq-7020 project uses a 100 MHz internal PL clock and divisor 217 (about 460,829 baud), with XDC pins RX=T19 and TX=J15. Its board schematic identifies P5 bridge jumpers 3-5 and 4-6. The active controller maps Start PQN to `80 49`, ORN0 to `80 4B`, and time-step end to `80 4A`; `80 45` toggles LN0 inactive and is not Start PQN.

The expected output frame begins with 24 state bytes (12 values, two bytes each), may contain two-byte ORN spike addresses, and ends with `0A`. State pairs transmit source bits 15..2 only; decode each as `((b0 & 0x7F) << 7) | (b1 & 0x7F)`, not as a full 18-bit value.

Historical evidence update (2026-10-21 audit): RTL loopback simulation passed for `00 A5 FF` at 460800 baud. The 2026-10-07 board report also records user-pasted raw HEX containing 484 then 263 repeated complete state frames, plus TX `80 4B 80 4A 0D 0A`. Thus received board HEX exists. Its capture timing relative to TX is missing, so a controlled stimulus-caused response and complete RX round trip remain unverified. See [bundled historical report](../../evidence/originals/reference.txt); original raw terminal capture is not bundled. Do not replay historical opcodes without current authorization.
