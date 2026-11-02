# Independent C++ reference: host support and build

The supplied `app/bundle/reference.exe` is a Windows x64 executable. `host_reference.cpp` uses SSE intrinsics to select round-to-nearest and disable FTZ/DAZ. The current implementation targets x86/x64; it is not an ARM/PYNQ executable. It runs on the PC, not on the FPGA board.

## Build on an x86/x64 host with g++

From `board/runtime/app/bundle`, compile to a new output; keep the supplied executable and frozen manifests unchanged:

```text
g++ -std=c++17 -O2 -fno-fast-math -ffp-contract=off -frounding-math -msse2 -mfpmath=sse -static reference.cpp host_reference.cpp -o reference_rebuilt.exe
```

On Linux x86_64, from the same bundle directory:

```text
g++ -std=c++17 -O2 -fno-fast-math -ffp-contract=off -frounding-math -msse2 -mfpmath=sse reference.cpp host_reference.cpp -o /tmp/flyvis-reference
```
 No RTL, camera, GPU, PyTorch or board is involved. These two files implement serial ordered-edge FP32 operations; do not enable fast-math or fused multiply-add.

## Verify the rebuilt executable

Windows, from the same bundle directory:

```text
reference_rebuilt.exe . ../../checks/input.bin reference_rebuilt_state.bin
```

Compare the complete output bytes with `../../checks/state.bin`; 721 inputs must produce 45,669 identical state words. The equivalent Linux x86_64 commands are:

```sh
/tmp/flyvis-reference . ../../checks/input.bin /tmp/flyvis-state.bin
cmp /tmp/flyvis-state.bin ../../checks/state.bin
```

The public Python self-check continues to use the supplied Windows executable. The manual build/byte comparison is the source-level host reference procedure. Windows MinGW rebuild is tested in this packaging update; fresh Linux execution and ARM support are not claimed.
