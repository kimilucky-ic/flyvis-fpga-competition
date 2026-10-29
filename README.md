# FlyVis visual neural network on Zynq-7020

Competition source delivery, 2026-10-29. Repository remains private; no restoration of previously withdrawn conversations. Full configured FlyVis network:45,669 nodes,1,513,231 connections,721 visual inputs,strict FP32/Euler,5ms model step. PL executes the neural updates; PS handles OV5640 capture/mapping/DDR records; PC displays results and independently audits states.

## Current implementation

- [Current camera/PC runtime](source/flyvis-lossless-study/ov5640_live_v261_20261026/): bundle,pc,assets and tests. Includes the current chart/axis/web layout snapshot from2026-10-28 and bounded audit-monitor read fix.
- [Final Vivado2026.1 SoC](source/flyvis-lossless-study/vivado2026_1_20261026/): build scripts and release hardware metadata.
- [Original GUI and GPU integration](source/flyvis_runtime/fly/): viewer and gui_v1. Older scientific/hybrid paths are retained as historical implementations, not the current full-PL camera entry.
- [Competition skill package](skill/README.md): usage, limitations and historical verification.
- [Licensing/attribution](third_party_notices.md).

## Build and run

For the current PC entry use [board/runtime/README.md](board/runtime/README.md): Windows x64/Python3.12, install its requirements, then `python run.py --check-only`. For an operator-requested live experiment use `python run.py --ip YOUR_PC_IPV4` and the generated fixed Notebook. Board operations remain manual and require exclusive ownership; failed/unknown states are not retried automatically.

For firmware use Vivado2026.1 and [build/portable/README.md](build/portable/README.md). [Official vendor acquisition](build/vendor_dependency_review.md) documents the required reference and 56-file identity check. Fresh official-download-to-BIT reproduction and third-party redistribution permission remain unverified. Do not treat old source variants or archived scripts as the current entry.

## Evidence

Historical software/RTL/implementation reports remain in their source directories and retain their own scope. Latest full-PL camera basis:1090 steps,49,779,210 saved state words,zero mismatches in that bounded operator run. This does not establish biological equivalence,unlimited duration or200Hz realtime. Replaying saved results is offline replay. No new device experiment was run for publication.

## Export

All published paths and hashes are in public_manifest.json. Personal running notes,credentials,virtual environments,EDA caches,bulk recordings and unrelated MaleCNS/PQN projects are excluded. Original source variants are retained to preserve the engineering process; start with the current implementation above. The original competition RAR remains a separate immutable upload artifact.

## AMD guide audit

[Requirement-to-file map](report/amd_requirements.md), [seven-page design report](report/design_report.pdf), [actual implementation reports](build/), [verification summaries](sim/), [operation steps](board/reproduce.md), and [selected current AI collaboration record](report/ai_collaboration_record.md). Repository delivery is distinct from public-release permission and fresh source-to-BIT validation; remaining boundaries are in report/amd_compliance_audit.json.

## Normalized export verification

All exported paths pass the naming check. export_path_map.json records the initial path/content transformation, while public_manifest.json records final deliverable bytes after deliberate bundle-manifest regeneration. The current46-file bundle admission and two corrupt-firmware rejection cases passed; three current JS files pass syntax checks. Four pre-existing intentionally invalid historical fixtures are recorded, not promoted to runnable Python. Historical acceptance manifests retain original candidate scope; they are not newly passed tests. Full historical functionality, browser execution and clean Vivado rebuilding remain unverified. See sim/normalized_runtime_check.json and sim/normalized_export_checks.json.

## Current deployable PC entry

Use [board/runtime](board/runtime/README.md), which assembles the current PC/web files with the existing fresh-session generator. Run `python run.py --check-only` there for the actual saved721input/full45669state CPU comparison. Then use `python run.py --ip YOUR_PC_IPV4` only when the user wants to start the receiver. Device operations remain operator-controlled. Fresh prepare-only generation was checked offline; no HTTP/browser/board experiment was run. Raw camera pixels are not public; this sample does not retest frame mapping.

## Detailed engineering and publication hold

[Detailed seven-part technical report](report/technical_report.md), [AI evidence guide](report/ai_workflow.md), [vendor dependency review](build/vendor_dependency_review.md). ALIENTEK copyrighted-source instances are identified in report/third_party_holds.json; redistributability has not been established. Publication of this reviewed inventory has been authorized by the project owner; unresolved third-party and rebuild limitations are disclosed below. The current directory is a local review candidate, not an assertion of all-license clearance or clean-machine Vivado success.
