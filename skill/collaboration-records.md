Privacy revision: [engineering summary](evidence/chat_excerpts.json) contains no original conversation. Original prompts/answers are not publicly distributed.

# Skill collaboration and correction records

This is a curated record of reusable failures and corrections from the project's separate workstreams. It summarizes earlier interactions; it is not a verbatim transcript. The competition guide asks for prompts, model responses, and self-correction trajectories, so attach the original chat exports/screenshots with this index before final submission.

## Captured user requirement for durable skill learning

The user asked that Codex record and reproduce suitable reusable procedures while working: “工作的时候遇到合适的、可以复现的，就记录下来、复现下来。”

- **Model response:** added a project rule to identify repeatable workflows, reproduce safely, record scope/prerequisites/steps/expected result/failure recovery/evidence, and label unverified observations honestly.
- **Self-correction:** a single shared `AGENTS.md` is suitable for common rules but not per-chat progress. The project now routes four separate workstreams to four checkpoint files under `docs/workstreams/`; `AGENTS.md` says routine progress belongs in the assigned lane checkpoint.
- **Evidence:** `AGENTS.md`, `docs/workstreams/README.md`, and the four lane checkpoint files.

## Case 1 — Do not rebuild an open Vivado project in place

- **Prompt / issue (summary):** a rebuild was run while the user's Vivado GUI project was open; the user reported cascading errors and asked to stop modification and perform read-only inspection.
- **Initial model failure:** a Tcl script deleted and recreated a build directory that the GUI still had open.
- **Correction:** stopped the rebuild, preserved the open project, inspected logs and existing outputs, and changed the reusable procedure to check destructive commands and use an isolated build directory.
- **Observed effect:** later project outputs were reviewed from a separate build record. The toolchain Skill now requires checking the active project and delete operations before running scripts.
- **Evidence:** `snn_rebuild_v8.log`, `docs/phase1_resource_report.md`, and `skill/vivado-vitis-toolchain-debugging/skill.md`.

## Case 2 — Separate direct fly VHDL from PYNQ/Jupyter

- **Prompt / issue (summary):** the fly design was being tested as a direct VHDL implementation in Zynq PL, while an earlier response incorrectly brought in the SNN/PYNQ Jupyter route.
- **Self-correction:** re-read the fly project and board schematics, separated the direct PL UART path from the PS/PYNQ workflow, and corrected an earlier false assumption that the question marks reflected ongoing TX. The latest user report is that XCOM is empty and no command has been sent; RTL waits for a valid RX start before periodic triggers. The next step is HEX mode, raw Start PQN `80 49`, capture the first response, then one ORN0/time-step pair `80 4B 80 4A`.
- **Observed effect:** current reports identify the correct board path and prevent Jupyter/HLS steps from being applied to this direct-VHDL test.
- **Boundary:** no physical HEX response or controlled RX result is captured yet, so the UART link skill remains a candidate, not a validated procedure.
- **Evidence:** `docs/fly-Zynq7020-current-status.md`, `docs/fly-Zynq-移植进度报告-2026-10-06.md`, and `skill/fpga-board-reference-research/skill.md`.

## Case 3 — Distinguish build success from board success

- **Prompt / issue (summary):** the team needed to know whether a successfully generated bitstream meant the FPGA design was already validated on hardware.
- **Correction:** separated synthesis, implementation, bitstream identity, board programming, and functional input/output into distinct evidence steps. Board tests must record the exact BIT/HWH identity and preserve raw inputs, outputs, status, and recovery state.
- **Observed effect:** the board report records a two-neuron cascade and also preserves the fact that an earlier run reloaded the bitstream despite a no-reload constraint; later observations are tied to the exact candidate image.
- **Evidence:** `docs/board_cascade_validation_status.md` and `skill/zynq-7000-board-operations/skill.md`.

## Case 4 — Stop when an AXI payload does not fit

- **Prompt / issue (summary):** the HLS weight path packed row, column, and weight into 34 bits, while the AXI stream exposed 32-bit `TDATA`.
- **Correction:** calculate the field widths, identify the out-of-range slice and affected producer/consumer, then stop integration for an explicit contract decision. Do not hide the mismatch by truncating fields or inventing new slices.
- **Observed effect:** the toolchain Skill has a concrete failure signature (`[Synth 8-524] part-select [33:26] out of range`) and a stop rule for unresolved interface contracts.
- **Evidence:** `skill/vivado-vitis-toolchain-debugging/skill.md` and the HLS/AXI source/build records in the project.

## Case 5 — Do not call a named "in-silico" notebook a software simulator

- **Prompt / issue (summary):** determine whether the fly repository already contains a full local software network simulator before building another one.
- **Finding and correction:** inspect notebook code for serial-port setup and actual FPGA I/O; notebooks that control a board are not CPU-only network simulators merely because their directory says `in_silico`.
- **Observed effect:** the workstream built a distinct software PQN baseline and all-LIF comparison path. The exact 1,030,688,757-byte ORN LFS object is restored separately and its SHA-256 was verified. A bounded 100 ms PQN-vs-FPGA-trace comparison diverged at step 0 with 0.67% aggregate exact matches, so the estimated full replay was held pending time/initial-state diagnosis. The original oscillation is not yet reproduced.
- **Evidence:** `fly_software_baseline/README.md`, `comparison/README.md`, `comparison/results/original_stimulus_pqn_100ms.json`, and the file identity check for `fly_original_data/ORN_3000s_osci_1odor.csv`.

## Case 6 — Gate performance claims and input provenance

- **Prompt / issue (summary):** speed up a full local fly reference without changing its behavior, and determine whether saved raster exports can stand in for missing event data.
- **Correction:** optimize only the PN-to-KC sparse accumulation, prove exact equality against the dense rule on zero, low, random 18-bit, and near-wrap states, then compare the full short synthetic output against the pre-optimization result. Describe the 14.46x number as an isolated microbenchmark only. Inspect the original raster extraction and keep its 20-second/100-ORN crop separate from the 1,780-ORN full input.
- **Observed effect:** the 1-second synthetic report was field-identical before and after the optimization; the cropped raster was explicitly rejected as a full-network stimulus substitute.
- **Evidence:** `fly_software_baseline/README.md`, `comparison/README.md`, and `comparison/results/synthetic_drive_1s_sparse_pnkc.json`.

## Case 7 — Do not use task accuracy as a substitute for quantized-model equivalence

- **Prompt / issue (summary):** turn a frozen MaleCNS software network into an integer/RTL candidate without carrying the old SNN's BRAM/router limits or silently reducing the connectome.
- **Correction:** freeze the 321-neuron/7,590-edge graph and trial split; compare 8/10/12-bit arithmetic across four seeds and both unresolved glutamate-sign scenarios; report a candidate-specific re-fit decoder separately from direct transfer of the frozen float decoder; measure per-neuron spike agreement, exact full-network timesteps, output-feature error, and conservative current/state bounds.
- **Observed effect:** for the positive-sign scenario, 8-bit direct transfer averaged 64.4%; 12-bit averaged 80.8% against an 80.1% float baseline. Even at 12 bits, only 32.0% of full 321-neuron timestep vectors matched exactly. The negative-sign scenario scored 100%, but sign is unresolved, so 12-bit remains a candidate rather than a biological or hardware conclusion. Golden vectors and RTL exist; XSim later passed 11 directed checks and 1,200/1,200 timestep vectors in Vivado Simulator 2024.2.2. Synthesis, bitstream, and board evidence remain unverified.
- **Reusable rule:** task-level function, internal trace equivalence, arithmetic safety, RTL simulation, synthesis, and board behavior are separate acceptance questions. Keep the exact frozen readout transfer score in addition to any re-fitted score.
- **Evidence:** `data/connectome/male_cns_v1_0/malecns_inference_v1/quantization_robustness_4seeds.md`, `data/connectome/male_cns_v1_0/malecns_inference_v1/rtl_vectors_seed_20261007/README.md`, and `skill/fpga-fixed-point-quantization/skill.md`.

## Case 8 — Check non-ASCII Windows paths early in FPGA tool failures

- **Prompt / issue (summary):** an FPGA operation failed while the project folder had a Chinese name; after the folder was renamed to ASCII fpga, the user reports the same operation worked normally.
- **Reusable procedure:** inspect the full project path, including parent folders, TEMP/TMP, output paths, and child-process script paths. Preserve the original, test a separate short ASCII-only copy with the same tool version and a fresh output directory, and compare the same minimal command before changing RTL or reinstalling tools.
- **Evidence boundary:** the exact tool, command, and error were not captured, and changing the folder may also change path length or build state. Treat this as an observed diagnostic lead, not a universal claim about Chinese paths.
- **Evidence:** user report in this Skill conversation and .agents/skills/windows-fpga-path-diagnostics/skill.md.

## Case 9 — Diagnose the first AXI stall from reset configuration

- **Source chat:** “⑥ FlyVis · 67节点FPGA真板闭环”, thread `01a124d3-6d27-7322-a0d3-7226d25fad91`; prompt/response details below are summaries.
- **Prompt / issue:** the user returned a stalled first board attempt. Programming had returned, but the trace ended at the first MMIO read intent; no returned read, START or raw PL output was established.
- **Finding:** the sealed HWH had C_AUX_RESET_HIGH=0, active-low aux_reset_in tied to zero, driving AXI/HLS reset. Earlier PS importer work had also required retaining the manufacturer DDR preset and bank voltage settings.
- **Correction:** preserve the failed release; explicitly select reset polarity in a new isolated full SoC build; verify generated HWH/HDL, BIT configuration payload and exact BIT/HWH identity; obtain the new release's scoped test authorization.
- **Observed effect:** the corrected resetfix release later completed one/32/800 physical-board integer replay. Static reset defect and successful corrected-release operation are established; a controlled A/B proof of every earlier whole-system symptom is not.
- **Evidence:** AXI-stall diagnosis (original-workspace source: `../flyvis-fpga/phase4_67_20261010/board_test_20261012/recovery_r2/R2_FIRST_AXI_STALL_DIAGNOSIS.md`; not a bundled dependency), resetfix build (original-workspace source: `../flyvis-fpga/phase4_67_20261010/board_test_20261012/recovery_r2/RESETFIX_BUILD_EVIDENCE.md`; not a bundled dependency), bankfix evidence (original-workspace source: `../flyvis-fpga/phase4_67_20261010/V1_BANKFIX_BUILD_EVIDENCE_20261011.md`; not a bundled dependency).

## Case 10 — Respect PYNQ execution environments and verify raw replay archives

- **Prompt / issue:** the user reported shell/password/pasted-code confusion, then requested Jupyter. The serial Python route reported `No Devices Found`; operation logs showed it stopped before overlay-download intent.
- **Correction:** inspect the interpreter and XRT environment, retain failed logs, name one execution surface, verify the same boot and remaining exact operation scope, then use the working Jupyter runtime.
- **Prompt / progression:** user supplied one-request results and original ZIP, then separately approved 32 and 800 requests and returned their archives. The model initially labelled console results operator-reported; after checking original files, hashes, every request trace and a separately held local oracle, it promoted only the exact engineering-replay claim.
- **Observed effect:** independent V1/V2/V3 reviews accepted 67/2,144/53,600 exact codes; V3 checked 4,812 inventoried files and 800 START/completion sequences. Each stage used recorded old_H and the same resetfix release.
- **Self-correction:** the user clarified that many videos already existed. The model distinguished input animation and archival result presentation from a live recording of the current board run; scientific precision, true feedback and live-video proof were retained as unaccepted.
- **Evidence:** 67-node archive checkpoint (original-workspace source: `../flyvis-fpga/phase4_67_20261010/board_test_20261012/ARCHIVE_STATUS_67_20261012.md`; not a bundled dependency), V3 original-archive review (original-workspace source: `../flyvis-fpga/phase4_67_20261010/board_test_20261012/replay800/sealed_v3_800_7c53b766f037/V3_ACCEPTANCE_REPORT.md`; not a bundled dependency), [new Skill source summary](pynq-bounded-replay-evidence/evidence.md).

## 2026-10-18 — 九个对话的补充记录

用户要求读取截图中的全部九个对话，把能复用的经验整理出来。本轮对完整本地会话的用户／最终答复作检索，读取近期与历史关键纠错，并核对对应原始结果文件。

完整的提示摘要、观察、模型修正、效果和边界归入 [source_review_20261018.md](source_review_20261018.md) 的S1–S9，避免重复抄录：

- S1：无损有序图／FP32、分阶段硬件证明和待确认的时钟显示。
- S2：运行／持久化性能、单入口，以及完整PL与分区PL接口区别。
- S3：受控消融、冻结后新刺激、无teacher correction的CPU替代，以及GPU功耗分母。
- S4：实际485步GPU–PL反馈、事务确认和范围内的稳定性。
- S5：同数据启动提速、四区解释和实际模型读出。
- S6：计算坐标／SWC形态边界、固定基线亮度、资源分类误判。
- S7：前缀数值门槛和可字节恢复的派生文件退役。
- S8：DDR整块搬运、BRAM尾区与只适用于特定仿真的VIP调度修复。
- S9：真实依赖、嵌套Git及发布白名单，避免按目录名退役。

本节和来源记录均为整理摘要，不代替完整逐字导出；没有新增设备验证。5个新Skill、3个更新Skill和2个已有软件Skill的包副本在本地形成，发布状态不变。

## Open evidence work

- Capture an XCOM HEX receive trace and complete a controlled direct-VHDL UART test before claiming that Skill as board-validated.
- Diagnose the 100 ms fly software/FPGA trace divergence before increasing replay duration; the original input is available and hash-verified, but the short-window comparison is not yet explained.
- Re-run the relevant packaged toolchain procedures in Vivado/Vitis2025.2 or a newly selected target/version. FlyVis67 supplies a scoped Vivado2026.1.1 full SoC case, not validation of all existing procedures.
- Independently reuse the packaged PYNQ instructions on another task/board before claiming universal compatibility. The source's staged campaigns are retained demonstrations, not a new reproduction performed during Skill authoring.
