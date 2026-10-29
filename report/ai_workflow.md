# AI collaboration summary

Original conversations,local source paths,source-line metadata and internal memory/session references have been withdrawn. The linked JSON files now contain retrospective engineering summaries only. They are not verbatim prompts/answers and do not establish compliance with a requirement for original collaboration records.

## Retrospective workflow summary (not verbatim)

1. Human fixes model,precision,input source and hardware-operation boundaries.
2. Assistant reads current source and accepted evidence, proposes the smallest isolated change and preserves a known-good version.
3. CPU checks cover changed behavior and rejection paths. No automatic promotion from mock/simulation to physical PASS.
4. Operator runs device steps when authorized; results bind run/input/state/firmware identities.
5. Assistant audits saved evidence, reports failures and timing scope, and corrects false assumptions.

Open-source export examples: ignored session-specific payload relocation initially caused a false negative; exact allowed relocation was then checked instead of weakening the firmware check. Four historical corrupted fixtures were identified as already-invalid inputs rather than new syntax regressions. These are retrospective summaries; exact current checks are in sim/normalized_export_checks.json and sim/public_runtime_prepare.json.

No automated delegation or autonomous board operation is required to use this project. The user's operator-controlled board workflow remains authoritative. Historical dialogue grants no new hardware authorization.
