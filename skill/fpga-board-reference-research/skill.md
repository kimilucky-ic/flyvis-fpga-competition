---
name: fpga-board-reference-research
description: Research FPGA development-board manuals, Zynq-7000 device and pin details, constraints, interfaces, boot behavior, and software compatibility. Use when checking board specifications, datasheets, schematics, reference designs, or whether a bitstream/project matches a physical board.
---

# FPGA Board Reference Research

## Tested scope

This project's concrete example cross-checks one documented ATK Zynq-7020 revision using the local baseboard schematic V3.9, core-board schematic 2V5, and project XDC. It does not validate other revisions or boards; start each new task from that board's own documents.

## Verify the exact board before applying documentation

1. Identify the board vendor, product name, hardware revision, FPGA part/package/speed grade, and relevant peripherals from the board itself or authoritative project evidence.
2. Keep board model and FPGA device distinct. A compatible FPGA family does not establish matching package pins, clocking, DDR, constraints, connectors, or boot configuration.
3. For Zynq-7000, distinguish PS resources, PL resources, board-level wiring, and the software image/tool version. Do not assume an Artix-7 reference design is directly usable on a Zynq board.

## Use sources in evidence order

Prefer primary sources:

1. Board vendor’s current manual, schematic, reference design, errata, and revision notes.
2. AMD/Xilinx device documentation, product guides, and tool-version notes.
3. Maintained software documentation for the board image, such as PYNQ documentation.
4. Repository source and build metadata for project-specific behavior.

Use reseller pages, forum posts, and search snippets only to locate primary sources or explain an unresolved ambiguity. Cite the actual document title, revision/date, page/section, URL, and the exact fact it supports. Browse for current or uncertain specifications instead of relying on old memory.

## Check compatibility as a chain

For each claimed compatibility, verify the full chain:

- FPGA part/package/speed grade matches the project target.
- Board revision and pin constraints match the schematic and selected connectors.
- Clock frequency, reset polarity, I/O voltage, and electrical standards are valid for the actual bank and pin.
- PS/PL interfaces, AXI widths, DMA paths, address maps, and interrupts match the hardware design.
- Boot mode, SD image, PYNQ version, and driver/API assumptions match the board’s current software image.
- BIT/HWH (or equivalent metadata) are a matched pair generated for the target device.

Do not infer pin assignments from a different board revision or copy constraints between boards without checking the schematic.

## Present findings with boundaries

For each conclusion, label it as verified fact, inference, or unresolved. Include the primary source and a short reason. State what was not established: for example, a manual can establish a device feature or board connection, but it cannot prove the current board has a given bitstream loaded or that a live DMA test passed.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
