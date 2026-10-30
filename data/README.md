# Saved test inputs and references

input.bin contains 721 FP32 visual inputs; state.bin is the corresponding saved 45,669-node state. identity.json and provenance.json retain the original sample scope. These are identical copies of board/runtime/checks so the established runtime remains usable without a path or numerical change. No raw camera image is distributed. The 5ms model step and original reference identity remain unchanged.

Run `python run.py --check-only` in board/runtime for the established CPU comparison. Provenance paths are relative to board/runtime, not this data mirror. This is a saved sample, not a new live experiment.
