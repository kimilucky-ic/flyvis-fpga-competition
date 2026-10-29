---
name: fpga-evidence-preserving-cleanup
description: Audit FPGA workspace dependencies, publication scope and regenerable data before a scoped cleanup or migration. Use to distinguish active source, sealed evidence, derived arrays, vendor products and caches while retaining recoverability and nested repository ownership.
---

# FPGA Evidence-Preserving Cleanup

## Scope and prerequisites

Identify the user's exact cleanup/migration scope, active owners and build/session state. Read nested Git ownership/status, canonical entrypoints, source/release manifests and license attribution. A no-commit parent repository is not a rollback mechanism.

Reviewing or documenting candidates is read-only. Perform deletion/moving only within the scope the user actually authorized; do not ask again for the same already explicit action. A prior cache approval does not include research arrays, independent archives, repositories or chats.

## Procedure

1. **Account consistently.** Separate logical file bytes, allocated disk space and free-space snapshots; label GB versus GiB. Do not count a parent's files again as a sibling. Concurrent pagefile or other-project writes affect net free-space changes.
2. **Map real dependencies.** Trace imports, Tcl/XPR/BD/XCI/COE, initialization files, notebooks and manifest/source-identity references. Byte-identical files may still have active callers, independent Git history, licenses or evidence value.
3. **Classify each candidate.** Distinguish current runtime/source, sealed accepted or failed evidence, irreproducible original input, reconstructible derived arrays, generated EDA products, environment and cache. File age/name alone is not a retirement criterion.
4. **Prefer a smaller publication boundary.** An explicit source/contract/fixture/manifest/license allowlist often reduces a submission more than relocating live projects. Exclude regenerable tool caches and bulk raw data where the release permits; do not blanket-stage nested repositories.
5. **Prove derived-data recovery.** Record original size/dtype/header/order/hash and exact reconstruction inputs. Preserve necessary compact fragments. Reconstruct the complete byte stream in bounded chunks and verify it against the original before retirement; a plausible numerical array is insufficient for byte-exact recovery.
6. **Execute only the selected operation.** Verify resolved absolute targets, intended parents, reparse points and relevant active processes before a recursive Windows delete/move. Use native operations with literal paths. Preserve unrelated modified/untracked work; do not substitute shared-write hard links for independent copies without approval.
7. **Verify afterward.** Check exact target absence/location, named retained files, recovery stream/hash, source manifests and nested Git state as appropriate. Report freed allocation separately from bytes removed, including recovery-fragment overhead.
8. **Migrate conservatively.** Freeze active project paths during delivery when possible. A WSL distribution needs its supported lifecycle/migration path, not an arbitrary live VHDX move. Keep original paths until the selected destination and minimal existing entrypoints pass their scoped checks.

## Failure and recovery

Unknown ownership, live dependencies, unverified reconstruction or a changed retained-file identity stops that candidate. Preserve failure and restore from the exact retained archive/recipe. Do not rerun expensive neural/EDA experiments just to rediscover data that an accepted small recovery path can regenerate.

## Expected result

A scoped candidate list or completed operation has a dependency rationale, exact protected/changed paths, recovery evidence and honest disk accounting. It must remain clear whether retirement was proposed or executed.

## Source evidence and limits

Cases S7/S9 in skill/source_review_20261018.md: the architecture audit found duplicate source still used by callers and protected logs referenced by manifests. A later authorized five-derived-file retirement verified complete reconstruction hashes before and after, retained 8,164 files and 84 old trajectory arrays, and recorded logical-versus-allocated savings.

These are specific Windows/FPGA workspace demonstrations. Fresh reuse of this packaged Skill is observed, not yet reproduced. It does not authorize new deletion, permission changes, chat archival, repository publication or migration of currently active projects.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
