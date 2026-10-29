# FlyVis 67-node source evidence

This is a curated source summary, not a verbatim chat export or a new board run.

## Source and target

- Source chat: “⑥ FlyVis · 67节点FPGA真板闭环”, local thread ID `01a124d3-6d27-7322-a0d3-7226d25fad91`.
- Source workspace: FPGA project, lane `flyvis-fpga/phase4_67_20261010/`; archived 2026-10-12.
- Board path: Zynq-7020/PYNQ 2.7. Full SoC evidence: Vivado 2026.1.1 build 6605303, `xc7z020clg400-2`.
- Workload: 1,364 raw boundary + 67 old_H + 67 x_H signed Q22 words per request; PL computes 970 HH + 5,567 RH = 6,537 edges and returns 67 uncommitted candidates. The host does not supply precomputed chemical/new_H.

## Frozen identities

- BIT SHA256: `23cf5da15db221f399b54cae95e341e6a90a699c88d321d0a883aecca15f7569`.
- HWH SHA256: `3ea3f1e27c7b214e0f7a965455799875cbae94fb87bee6455a58ecbed4813f7d`.
- Release manifest SHA256: `90e522246d99322e574c33ec5a6378a6e35660eb1130079198a83313fda2c81f`.
- V1 archive `V1_ROW0_EVIDENCE_b895835f9643.zip`: SHA256 `b70fdd8e03d2cdea047fd5032820b5aa35fa0d08a0fee31c72a761cca395108d`; 25 inventoried files; 1 request; 67/67 exact codes.
- V2 archive `V2_32_REQUEST_EVIDENCE_11458b7a04ea.zip`: SHA256 `3bb2fd8400d2200c7986b0ec4289186fd03dc1262930311468c6ea6f2eb8c365`; 204 inventoried files; 32 requests; 2,144/2,144 exact codes.
- V3 archive `V3_800_REQUEST_EVIDENCE_7c53b766f037.zip`: SHA256 `aba7b8a54b61dc421eca48045b77d040d5c8e0fc9b9e67187b05dc77045d6c79`; 4,812 inventoried files; 800 requests; 53,600/53,600 exact codes.
- V3 actual output / independently retained oracle SHA256: `1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665`.

## Operator and model correction sequence

1. User required actual PL synaptic/neuron calculation, a small first test, isolated builds and specific authorization before physical operations.
2. The older bankfix image stalled on the first AXI read. The saved trace contained only a read intent and no returned read/START/output. Source/HWH inspection found active-low auxiliary reset tied to zero, holding reset asserted. A separate resetfix build explicitly selected polarity; generated HWH/HDL and artifact payload were checked. Subsequent corrected-release board output passed. The complete cause of every earlier system symptom was not established by a controlled A/B replay.
3. The serial Python route failed with `No Devices Found` before reaching overlay-download intent. The model inspected operation logs and environment, preserved that failure, and continued through the working Jupyter/PYNQ/XRT runtime. The user helped by reporting terminal output and choosing Jupyter.
4. The user executed exact separately approved one/32/800 campaigns. File-only export followed each stage. Original ZIPs were returned for host-side inventory, raw-output and independent-oracle checks; console PASS alone was initially labelled operator-reported.
5. Existing animation/result videos were found after the user clarified available recordings. The model corrected “video” into input stimulus, archival result presentation and live run recording; no live recording was claimed for these tests.
6. The user elected to archive the 67-node replay milestone and move to task ⑦. The archive preserves completed replay evidence and outstanding scientific/feedback scope.

## Source reports

Resolve these paths from the source workspace root. They are retained evidence pointers; the Skill does not include bulk board archives.

- `flyvis-fpga/phase4_67_20261010/V1_BANKFIX_BUILD_EVIDENCE_20261011.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/recovery_r2/R2_FIRST_AXI_STALL_DIAGNOSIS.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/recovery_r2/RESETFIX_BUILD_EVIDENCE.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/recovery_r3_resetfix/sealed_v1_row0_b895835f9643/V1_ACCEPTANCE_REPORT.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/replay32/sealed_v2_32_11458b7a04ea/V2_ACCEPTANCE_REPORT.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/replay800/sealed_v3_800_7c53b766f037/V3_ACCEPTANCE_REPORT.md`.
- `flyvis-fpga/phase4_67_20261010/board_test_20261012/ARCHIVE_STATUS_67_20261012.md`.

## Reproduction and limits

The staged campaigns and local original-archive reviews were demonstrated for this one target/release. Authoring this Skill did not independently rerun the board, change its state or repeat EDA builds. Fresh reuse of the packaged instructions on another task/board remains observed, not yet reproduced.

Each request used recorded old_H; there was no PL-output feedback, coordinated COMMIT or Python fallback. Scientific Q22 acceptance was NOT_GRANTED. Times include host/evidence I/O; no pure PL latency or real-time throughput was established. No unedited live-run video was supplied. Historical authorizations are consumed.
