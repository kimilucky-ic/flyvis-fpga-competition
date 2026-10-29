# AMD submission requirements and current audit

Source: original 28-page2026 AMD guide, PDF pages22–25 (printed19–22), sections3.3.3–3.3.5. SHA256:c6ad82acd4f7bdcd13bd412e232ed85d05f2a87dd5e2cdd04f9d219f88b569fc. Source PDF is not redistributed in this repository.

## Required deliverables

3.3.3.3 strongly requests GitHub/Gitee open source under a redistributable license, recommending MIT or Apache-2.0. Source text does not literally say mandatory; the team has chosen public open-source delivery.

3.3.5.1 requires full applicable RTL/HLS/PS project sources; simulation/verification results and explanation; synthesis and implementation reports with resources, clocks and performance; board projects/scripts/measured outputs and reference comparisons; reproducible build scripts. A file archive without a resolved dependency chain is insufficient for a clean rebuild claim.

3.3.5.2 requires root skill/ with README.md describing each item's scope, usage and failure conditions. Each item must state validated effects and originating failures/observations. Generic PYNQ cross-project/cross-board reuse is extra credit, not automatically established by this board.

3.3.5.3 requires background/innovation, principles/block diagram, partition rationale/interfaces, before/after optimization data, AI prompts/answers/self-correction, skill extraction/validation/boundaries and from-zero reproduction instructions. Keep the short design report concise and link detailed evidence here; repository details do not silently waive required report topics.

3.3.5.4 requires English lowercase/digit/underscore/hyphen path names, no Chinese/spaces/special characters. The explicit README.md name is retained. Directory layout src/sim/build/board/data/skill/report is recommended; alternatives need a README directory mapping.

Vivado/Vitis2026.1 recommended or2025.2; other versions require explanation and reproducibility. Declare exact device, actual board output and baseline performance/resource comparison. Public repository availability and a license alone do not prove reproducibility.

## Current status

Full implementation/source snapshots and audited Skill material exist. build/ now includes actual routed resource/timing reports and build command metadata. sim/ includes original CPU/RTL summaries with their original evidence levels. board/ contains existing saved-run analysis; it is not raw board output and does not replace the original state records. report/ai_chat_excerpts.json contains a retrospective engineering summary only; original prompts/answers are not publicly distributed.

NOT READY: naming violations remain; some source README files describe historical modes; build scripts still reference original paths and dependencies outside a clean checkout. Final design report, sanitized raw board/reference sample and fully resolved rebuild instructions remain to be completed. Do not mark these as passed based on this document. See amd_compliance_audit.json for precise inventory.
