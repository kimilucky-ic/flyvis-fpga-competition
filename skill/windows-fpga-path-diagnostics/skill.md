---
name: windows-fpga-path-diagnostics
description: Diagnose Windows FPGA tool startup, Tcl, IP-generation, child-process, and log failures by checking non-ASCII characters throughout project, temporary, and output paths. Use before changing RTL or reinstalling Vivado/Vitis when an error may depend on the project location.
---

# Windows FPGA Path Diagnostics

## Scope and evidence boundary

Use this workflow when Vivado, Vitis, Vitis HLS, XSim, Tcl, IP generation, or a child process fails from a Windows project directory. Chinese and other non-ASCII characters in any part of an absolute path are a high-priority compatibility check. Windows supports Unicode paths; do not assume every failure under such a path has the same cause.

## Diagnostic procedure

1. Preserve the source tree and record the exact error, command, working directory, tool version, exit code, and log path. Check the full paths for the project, every parent folder, temporary directories, generated output, and scripts passed to child processes.
2. If any relevant path contains non-ASCII characters, avoid editing RTL or reinstalling tools as the first response. Close tools that have the project open, then make a separate copy under a short ASCII-only root such as C:/fpga_work/project. Keep the original untouched.
3. Rerun the smallest failing command from the ASCII-only copy with the same tool version and a fresh isolated output directory. Keep other inputs and settings unchanged where practical; compare the first meaningful error, exit code, and generated files.
4. If the operation succeeds from the ASCII-only copy, record the result as path-sensitive. Check for other changed variables such as path length, permissions, temporary directory, OneDrive synchronization, and stale build outputs before claiming that the non-ASCII characters alone caused the failure.
5. If the failure remains, continue with ordinary toolchain diagnosis: installation/Tcl environment, PATH mixing, permissions, license, versioned IP, missing dependencies, and the earliest meaningful log error.
6. Do not rename or move an open project, delete a known-good build, or reprogram a board to validate this diagnostic. An ASCII drive mapping can be a lower-change probe when a separate copy is impractical, but verify which paths child processes actually receive and remove only the mapping created for that run.

## Expected record

Capture the before/after absolute paths, exact command, tool version, exit codes, first meaningful log lines, output-directory identity, and whether the original source was copied or moved. State whether the comparison changed path only or also changed path length, permissions, or build state.

## Project observation

On 2026-10-08, the user reported that a Windows FPGA operation failed while the project folder had a Chinese name, then worked normally after the folder was renamed to the ASCII name fpga. The exact tool, command, and original error were not captured, so this is a useful observed diagnostic lead rather than proof that all FPGA errors are caused by Unicode paths.

This workflow has one user-reported Windows case. Reproduce it with a controlled ASCII-path comparison and capture the tool/error before claiming a specific root cause or general compatibility rule.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.

Submission status: **observed pitfall candidate, verification incomplete**. This item does not yet meet a claim of validated stable effect; keep that gap visible when submitting the fourteen-item draft.
