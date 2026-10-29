---
name: flyvis-demo-data-integration
description: Integrate FlyVis activity, camera input, official optical flow and anatomical illustrations into an existing demo while preserving time, node and execution provenance. Use for GUI or 3D consumers of saved or live model results and for removing display overhead from a measured compute path.
---

# FlyVis Demo Data Integration

## Scope and prerequisites

Use the existing approved GUI/launcher and a documented producer interface. Identify the exact run, source/checkpoint, input, state ordering, spatial registry, time axes, backend kind and recording profile. Read the producer's current contract; GPU-R/PL-H, complete-network PL, GPU+software-H and saved playback are distinct modes.

The current competition interface uses four clear areas: what the fly saw, optical flow, neurons and their explanation. Preserve the consuming user's layout and terminology in other projects.

## Procedure

1. **Keep one owner per live resource.** Reuse the camera producer and neural controller; a display consumer must not open a second camera or silently step another model. Coordinate edits by file ownership and consume versioned read-only handoffs.
2. **Validate before showing.** Check run/input/state/mapping identities, dimensions, finite values and complete node IDs. Reject stale, short or reordered data. In a first complete-network PL test, compare all initial and next-state words before accepting a display frame.
3. **Align three clocks.** Retain source capture/receive time, model input time k*dt, and the post-Euler state time. Bind every picture, activity row and flow output to the same source frame/model step; video playback speed does not change dt.
4. **Use the real decoder.** Feed the required full activity layers to the original pretrained decoder, recursively set eval mode, and check parameters/buffers remain unchanged. Display unavailable flow when no accepted decoder output exists; old GPU flow cannot fill a new PL run's missing result.
5. **Preserve spatial meaning.** Verify global-ID/type/u/v ordering against the canonical registry. Hex-grid positions are computational coordinates. A type-matched SWC is a morphological illustration, not a proved one-to-one identity or anatomical registration with a FlyVis node.
6. **Explain brightness truthfully.** Keep type identity color fixed. If response enhancement is used, freeze a declared pre-stimulus baseline, scale and threshold for the clip, preserve signed delta and raw values, and distinguish type-level mapping from cell-specific measurement. Compare predicted direction with the known input only where ground truth exists; a bright group alone is not a success verdict.
7. **Keep the neural loop small.** In an approved performance mode, place decode, rendering, video export and optional deep audit outside STEP. Copy immutable snapshots into a bounded nonblocking recorder; count computed, committed and saved steps separately. Missing records make evidence incomplete even if computation finished.
8. **Optimize startup at its source.** Load only the selected experiment, then lazy-load other panels. Reuse a prior full-hash result only under the accepted path/size/time/file-identity cache rule; invalidate changes or corrupt cache. Treat this as a local performance cache, not proof against adversarial replacement.
9. **Close with clear provenance.** Mark live computation, recorded-camera input, actual-board-result playback and software-only playback explicitly. Keep controls minimal, show the actual fault/stage, drain or mark recording failure, and close owned workers normally.

## Failure and recovery

- An interface from 65 center cells or H67 cannot masquerade as a full 5768-node interface.
- A missing/bad producer result must clear or visibly invalidate its panel rather than retain stale successful content.
- A frame-specific renderer or resource-guard failure requires its PID plus creation-time/ownership context. Process names alone, including wsl.exe, cannot prove conflicting research activity; narrowly classify known read-only queries and retain unknown cases.
- Preserve the accepted raw activity and original rendering as rollback/scientific reference when changing brightness or layout.

## Expected result and evidence

Verify the displayed source, arrays and times; test stale identity, missing frames and short arrays; inspect actual screenshots/interactions at representative steps. Separate backend-first-frame timing from desktop-window startup and neural throughput.

Source cases S2/S5/S6 in skill/source_review_20261018.md: startup data preparation 14.71s→2.49s on the same saved data; fixed-baseline eight-type SWC rendering with exact source times; minimal GPU+software-Q24 32-step run verified in 1.166s. These are scoped offline/software results, not a new board-speed or live-camera acceptance.

The complete-network candidate's new GUI reader and clock-stop investigation were still in progress at review. Fresh reuse of this packaged Skill is observed, not yet reproduced. GPU/camera/board execution requires its own current scope; documentation authoring does not start them.

## Competition package use and evidence

See [parameterized usage](usage.md) and [historical verification and missing evidence](validation.md). These submission appendices supplement the Codex working source; they do not certify fresh reuse.
