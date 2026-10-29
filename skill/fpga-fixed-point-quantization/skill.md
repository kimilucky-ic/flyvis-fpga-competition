---
name: fpga-fixed-point-quantization
description: Choose and validate fixed-point representations for FPGA neural-network or signal-processing models. Use when translating a floating-point reference into integer RTL, selecting weight/state widths, checking overflow bounds, or generating hardware golden vectors.
---

# FPGA Fixed-Point Quantization

Use this workflow to turn a floating-point reference into a hardware-ready fixed-point candidate while preserving the behavioral contract and reporting what is still unverified.

## 1. Freeze the comparison contract

1. Identify the production model, graph/topology, exact input dataset and hash, initial state, update order, reset behavior, and target FPGA interface.
2. State signed formats and scales for weights, state, inputs, accumulators, and outputs. Specify rounding, truncation, saturation, wrap, and threshold comparison explicitly.
3. Keep uncertain model assumptions as separate named scenarios. Do not bury a polarity, threshold, or parameter choice in the implementation.
4. Freeze trial generation, labels, train/test partitions, random seeds, and any readout/classifier before comparing precision candidates.

## 2. Build a small integer reference first

1. Implement the exact integer recurrence independently of RTL, including intermediate widths and operation ordering.
2. Add hand-checkable vectors for zero input, one edge, coincident inputs, recurrent input, threshold boundary, negative weights, rounding ties, reset, and signed extrema.
3. Verify causal timing: document whether an event affects the current or next timestep and how simultaneous sources are accumulated.
4. Compare small networks with a simple reference implementation before loading the full graph.

## 3. Sweep candidate formats without changing the task

1. Quantize the frozen weights at candidate signed widths and fractional scales. Record each edge that rounds to zero or saturates; preserve the full edge list.
2. Run the same trials and seeds for floating-point and each integer candidate.
3. If a readout is part of deployment, report both (a) a separately fitted readout for each model and (b) the frozen floating-point readout transferred directly to integer-model outputs.
4. Report task accuracy alongside per-neuron spike-bit agreement, exact full-network timestep vectors, analog feature error, and first divergence. A stable task score does not establish internal equivalence.
5. Repeat across seeds and unresolved model scenarios. State which scenario supports the candidate and which remain uncertain.

## 4. Prove arithmetic range

1. Compute a conservative per-target current bound from the sum of absolute incoming quantized weights or another justified graph bound.
2. Propagate that bound through the state recurrence, including leak/retention, rounding allowance, accumulated timesteps, and any bias or persistent input.
3. Compare every intermediate and stored state against the exact signed range. Record margin to overflow, not only whether one tested trace happened to fit.
4. Check weight quantization error, zeroed/saturated edges, and accumulator capacity separately; they are different failure modes.

## 5. Generate hardware golden vectors

1. Generate vectors from the frozen integer reference, with a manifest containing graph/source hash, quantization format, scenario, seed, input trial, timestep count, and bit ordering.
2. Include both ordinary stimuli and edge cases for maximum fan-out, simultaneous activity, signed extremes, and near-overflow accumulation.
3. Preserve the raw expected vectors and a decoder. Verify vector width, line count, reset prefix, and final-state format before invoking the HDL simulator.
4. Compare RTL cycle by cycle or timestep by timestep at the agreed boundary. Report first mismatch and preserve the simulator log.

## 6. Keep evidence levels distinct

- Integer reference tests establish software-model behavior only.
- A successful RTL simulation establishes behavior only for the simulated RTL, vectors, and simulator configuration.
- Synthesis and implementation reports establish resource and timing properties for their exact run and target.
- A generated bitstream does not establish that the board loaded or executed it.
- A board test must record exact image identity, input, raw output, state, and recovery status.
- If the HDL tool cannot start or compile, mark simulation blocked; do not describe static review or golden-vector generation as a passing RTL test.

## Project example and boundary

The MaleCNS software-only experiment froze a 321-neuron / 7,590-edge graph and compared 8-, 10-, and 12-bit weights over four seeds. Under its positive-glutamate scenario, 12-bit quantization transferred the float-trained decoder at 80.8% mean accuracy versus 80.1% for float, while only 32.0% of full 321-neuron timestep vectors exactly matched. The negative-sign scenario scored 100%, but the sign assumption is unresolved. Twelve-bit is therefore a conservative software-supported RTL candidate, not a biological conclusion or hardware signoff. The generated RTL vectors later passed Vivado Simulator 2024.2.2: 11 directed checks and 1,200/1,200 timestep vectors exact, recorded in rtl_sim/xsim.log. Synthesis, implementation, bitstream generation, and board execution remain unverified.

This workflow has software-model and directed/golden RTL-simulation evidence for one MaleCNS graph, with Vivado Simulator 2024.2.2. Synthesis, implementation, bitstream and physical-board procedures remain unvalidated for this candidate. The quantization sweep itself remains software-only.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
