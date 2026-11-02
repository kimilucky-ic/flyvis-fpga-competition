# AMD delivery map — verified repository contents

Original 2026 AMD guide, sections3.3.3–3.3.5, PDF pages22–25, SHA256 `c6ad82acd4f7bdcd13bd412e232ed85d05f2a87dd5e2cdd04f9d219f88b569fc`. The guide is not redistributed. Its seven bullets are report topics, not seven assumed portal attachments.

## Materials in this repository

- Source and current GUI: [source](../src/); current deployable PC entry [board/runtime](../board/runtime/README.md).
- Verification: [sim](../sim/), [saved operator-run analysis](../board/saved_run_analysis.json), actual saved input/initial state/full state/reference and identities in `board/runtime/checks/`.
- Synthesis/implementation and build: [build](../build/), [portable steps](../build/portable/README.md), [official vendor acquisition](../build/vendor_dependency_review.md).
- Skill: [index](../skill/README.md), scope, usage, failure conditions, historical effects and limitations. Generic cross-board bonus is not claimed.
- Seven report topics: [five-page design report](design_report.pdf) and [detailed engineering report](technical_report.md). Background/innovation, diagram, partition/interfaces, optimization comparisons, AI collaboration, Skill extraction and reproduction are all addressed.
- Main AI collaboration evidence: [engineering cases](ai_engineering_cases.md), with two short original prompt/answer pairs and two labelled engineering summaries. [Historical repository-delivery exchanges](ai_collaboration_record.md) are supplementary. Private historical chats remain withdrawn; missing original dialogues are not reconstructed.
- Identity and attribution: root `public_manifest.json`, `license` and `third_party_notices.md`. The manifest name is an inventory convention; it does not mean the repository is public.

## Honest remaining boundaries

Repository is PUBLIC and anonymous HTTP access was verified on 2026-11-02. AMD strongly requests GitHub/Gitee open source under a redistributable license. Public access is now available; third-party redistribution scope remains unresolved and is not cleared merely by the visibility setting.

Official manufacturer download locators have been verified, but today's full vendor archive was not downloaded and its derived build files were not proved byte-identical. The 56-file hash list and fail-stop preparation are available. Third-party redistribution permission and a clean-machine source-to-BIT build remain unverified. Existing historical source variants were not all reaccepted after path normalization. The included PDF is the current engineering submission copy; the user approved this five-page narrative on 2026-11-02; contest-site upload is outside this repository check.

Tool/device and performance evidence must retain the original version and scope. No new board/GPU/camera/EDA experiment was run to fill documentation gaps.


[补充：实际研发脱敏案例](ai_engineering_cases.md)（短原文与工程摘要分列；设计PDF已同步用户确认稿。）

## Final presentation materials

- [Approved design report](design_report.pdf): synchronized byte-for-byte with the user-approved local PDF; titled Biological Neural-Network Hardware Implementation and Functional Validation. Biological neural hardware is the main goal; FlyVis vision is the demonstrated instance, low-energy operation is a potential, and brain-interface-related applications are future work.
- [English poster PDF](poster_en_a4.pdf), [editable poster](poster_en.pptx) and [preview](poster_preview.png): biological visual-circuit simulation on FPGA.
- Existing reported runs, estimates and limitations retain their original evidence scopes.

