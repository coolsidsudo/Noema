# Noema Phase 4 Review/Apply Interoperability Hardening Semantics (Slice 5)

## Purpose and boundary

This document defines the next bounded interoperability-hardening semantics that follow the accepted Phase 4 Slice 4 review/apply execution interoperability baseline.

It extends:

- `docs/noema-phase4-agent-interface-baseline.md` (Slice 1)
- `docs/noema-phase4-agent-surface-contract.md` (Slice 2)
- `docs/noema-phase4-agent-operation-state-semantics.md` (Slice 3)
- `docs/noema-phase4-review-apply-interoperability-semantics.md` (Slice 4)

This slice is semantics-definition work only. It does not implement a workflow engine, auth/user management, deployment hardening, direct canonical-write authority for agents, or Phase 5 maintainer workflows.

## Baseline references

This document aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `docs/noema-index-catalog-baseline.md`
- `docs/noema-phase3-human-client-baseline.md`
- `docs/noema-phase4-agent-interface-baseline.md`
- `docs/noema-phase4-agent-surface-contract.md`
- `docs/noema-phase4-agent-operation-state-semantics.md`
- `docs/noema-phase4-review-apply-interoperability-semantics.md`

## Scope in this slice

This slice hardens interoperability semantics by defining:

1. Multi-step apply sequencing behavior and completion interpretation.
2. Richer conflict categories and machine-visible conflict encoding.
3. Bounded recovery semantics for retry, resume, correction, superseding attempts, and abandonment.
4. Machine-visible status/result behavior across resumed/retried/corrected/superseded apply paths.
5. Minimum apply-step and recovery-record field expectations.
6. How `results_in`, `supersedes`, review history, and apply/log traceability remain coherent through recovery paths.

This slice remains implementation-light and does not define runtime orchestration internals.

## Hardening principles

1. **Decision/apply separation remains foundational.** Acceptance is a decision outcome; materialization remains independently tracked.
2. **Bounded and explicit sequencing over implicit orchestration.** Multi-step semantics define interoperable behavior, not engine internals.
3. **Conflicts are typed, machine-visible, and auditable.** Clients should distinguish conflict classes without textual guesswork.
4. **Recovery is bounded, traceable, and state-safe.** Recovery must preserve lineage and avoid silent mutation.
5. **Canonical publication remains human-governed.** Agent pathways remain proposal/review/apply support surfaces.

## Multi-step apply sequencing semantics

### Why multi-step semantics are required

Slice 4 established apply states and decision/materialization separation. Slice 5 adds the minimum interoperable semantics required when accepted scope materializes through more than one apply step.

### Apply attempt and step model

For accepted proposals, apply materialization should be interpreted as one or more **apply attempts**. Each attempt may contain one or more ordered **apply steps**.

- An apply attempt is a bounded execution path for materializing accepted scope.
- Steps are the smallest interoperable units of observable apply progress.
- Recovery actions may continue the same attempt (`resume`) or create a new attempt (`retry`, `correction`, or `superseding attempt`) depending on semantics below.

### Step ordering expectations

Implementations may execute work internally in varied ways, but machine-visible step records must preserve a deterministic ordering view.

Minimum expectations:

1. Each step record has a stable `step_sequence` integer within an attempt.
2. `step_sequence` ordering represents the authoritative replay order for client interpretation.
3. If parallel internal execution exists, emitted step records still map to deterministic sequence values.
4. A sequence gap is invalid unless explicitly represented as skipped/deferred with a typed reason.

### Step identity and correlation expectations

Each step must be uniquely identifiable and correlated to proposal and attempt context.

Minimum expectations:

- Step identity is stable within its attempt (`step_id`).
- Step correlation includes `proposal_id`, `apply_attempt_id`, and `request_id` (or equivalent operation correlation id).
- Where steps produce object-level outcomes, step records reference the affected `target_object_id` and/or resulting object IDs.

### Partial progress visibility

Partial progress must be machine-visible during multi-step execution.

Minimum expectations:

- `apply_state=in_progress|partial|failed` must be explainable by emitted step records.
- Status responses expose enough information to distinguish:
  - not started
  - started with no completed step
  - some steps completed
  - blocked/failed/deferred scope
- `results_in` contains only committed outcomes, never speculative outputs.

### Multi-step completion criteria

For an accepted proposal with multi-step apply behavior:

- `apply_state=applied` only when all required in-scope steps are terminal-success and no required pending scope remains.
- `apply_state=partial` when at least one in-scope step succeeded and at least one required scope segment remains unapplied.
- `apply_state=failed` when attempt termination is failure and remaining required scope exists.
- `materialization_complete=true` only for `apply_state=applied`.

## Minimum apply-step record fields

An implementation may use event logs, sidecar records, or equivalent structures. Interoperable semantics require at least the following fields per step record.

### Required fields

- `step_id` (stable within attempt)
- `proposal_id`
- `apply_attempt_id`
- `step_sequence` (positive integer)
- `step_type` (implementation-defined category)
- `step_state` (`pending`, `in_progress`, `succeeded`, `failed`, `deferred`, `skipped`)
- `started_at` (ISO 8601 or null)
- `updated_at` (ISO 8601)
- `completed_at` (ISO 8601 or null)
- `actor_id`
- `request_id` (or equivalent correlation id)
- `target_refs` (array of affected object IDs or target descriptors)
- `result_refs` (array of resulting object IDs emitted by the step)
- `failure_code` (required when `step_state=failed`)
- `defer_code` (required when `step_state=deferred`)

### Recommended fields

- `idempotency_key_step`
- `precondition_snapshot` (version/lineage tokens checked by the step)
- `attempt_ordinal` (1,2,3...)
- `notes`

## Richer conflict semantics

Slice 3/4 conflict behavior is preserved and hardened with typed categories for review/apply interoperability.

### Conflict representation contract

When conflict conditions arise, responses and logs should expose:

- `conflict_category` (enum below)
- `conflict_code` (stable implementation-defined subtype)
- `conflict_scope` (`proposal`, `attempt`, `step`, or `target`)
- `conflict_targets` (array)
- `conflict_detected_at` (ISO 8601)
- `conflict_detected_by` (actor/service identity)
- `resolution_hint` (bounded machine/human-readable guidance)

### Baseline conflict categories

#### 1) State race conflict (`state_race`)

Meaning:

- Concurrent transitions or operations raced and produced an invalid or stale operation ordering relative to current state.

Examples:

- Apply resume invoked after terminal failure has already been superseded.
- Duplicate completion transition for same attempt.

#### 2) Stale lineage/version conflict (`stale_lineage`)

Meaning:

- Apply step or attempt preconditions were evaluated against outdated object lineage/version tokens.

Examples:

- Target object changed after review acceptance but before apply step commit.
- Superseded lineage token no longer current.

#### 3) Target replacement conflict (`target_replaced`)

Meaning:

- Intended target identity or mapping no longer valid because a replacement/superseding target path has already been committed.

Examples:

- Target object was replaced by another accepted proposal path.
- Split/merge mapping invalidates original target reference.

#### 4) Policy/scope conflict (`policy_scope`)

Meaning:

- Apply operation violates current policy boundary, authority scope, or workspace constraints.

Examples:

- Attempt execution token lacks scope for one target.
- Visibility/authority policy changed since acceptance.

#### 5) Duplicate/idempotency conflict (`duplicate_idempotency`)

Meaning:

- A logically duplicate operation was detected through idempotency keys or equivalent deduplication controls.

Examples:

- Repeat step commit with same step idempotency key and already committed effect.
- Replayed proposal-level apply request already finalized.

### Conflict and apply-state interaction

- A typed conflict does not always force `apply_state=failed`; it may produce `partial`, `deferred`, or immediate no-op completion depending on category and recovery policy.
- Status surfaces should expose current `apply_state` plus latest conflict record(s) when unresolved conflicts exist.

## Idempotency expectations

### Proposal-level idempotency

Proposal-level apply initiation should be idempotent for the same accepted proposal and proposal-level idempotency key.

Expected behavior:

- Duplicate initiation should return existing attempt context where appropriate.
- Implementations should not silently create unbounded duplicate attempts for identical request context.

### Step-level idempotency

Step-level commits should be idempotent for the same `idempotency_key_step` (or equivalent deterministic dedupe identity).

Expected behavior:

- Replaying the same step request should not create duplicate resulting objects.
- Duplicate detection should produce explicit `duplicate_idempotency` conflict metadata or explicit no-op replay acknowledgment.

### Relationship between levels

- Proposal-level idempotency does not remove need for step-level idempotency.
- Step-level idempotency does not authorize bypass of proposal/attempt state guards.

## Bounded recovery semantics

Recovery must preserve traceability and avoid silent rewriting of prior outcomes.

### Recovery action taxonomy

#### 1) Retry

Meaning:

- Start a new apply attempt after failed/deferred/partial outcome, typically re-running all or selected scope under new attempt identity.

Contract expectations:

- New `apply_attempt_id` required.
- Links to prior attempt via `recovery_from_attempt_id`.
- Prior attempt history remains immutable.

#### 2) Resume

Meaning:

- Continue the same non-terminal attempt after interruption or bounded pause.

Contract expectations:

- Same `apply_attempt_id` retained.
- Step sequence continues or revisits deferred/pending steps with explicit state transitions.
- Resume is invalid for terminal attempts unless policy explicitly reopens with recorded override semantics.

#### 3) Correction

Meaning:

- Apply a bounded corrective path to address an erroneous or incomplete materialization outcome while preserving lineage.

Contract expectations:

- Correction may use a new attempt or correction sub-records under same attempt; either way must emit explicit correction records.
- Correction outputs should use `supersedes` and logs rather than silent history erasure.

#### 4) Superseding apply attempt

Meaning:

- A new apply path intentionally replaces prior incomplete/failed/obsolete apply path for the same proposal.

Contract expectations:

- New attempt declares `supersedes_attempt_id`.
- Superseded attempt is terminal with explicit superseded reason.
- Status views make supersession visible to clients.

#### 5) Abandonment / escalation

Meaning:

- Current apply path is intentionally stopped and unresolved scope is escalated to follow-up proposal workflow.

Contract expectations:

- Attempt/proposal outcome includes `abandoned_at`, `abandoned_by`, and `abandon_reason`.
- Unresolved scope references should be carried into follow-up proposal links.

## Minimum recovery/correction record fields

Where recovery actions occur, interoperable semantics require at least:

- `recovery_event_id`
- `proposal_id`
- `apply_attempt_id`
- `recovery_action` (`retry`, `resume`, `correction`, `supersede_attempt`, `abandon`)
- `trigger_reason_code`
- `trigger_summary`
- `requested_by`
- `requested_at` (ISO 8601)
- `approved_by` (if governance requires explicit approval)
- `approved_at` (ISO 8601 or null)
- `from_attempt_id` (null for first attempt)
- `to_attempt_id` (null for pure in-attempt resume)
- `affected_step_ids`
- `new_conflict_refs`
- `new_result_refs`
- `log_refs`

## Machine-visible status/result semantics for hardened paths

Status surfaces (for example via `get_proposal_status`) should expose enough fields to disambiguate path semantics.

### Required apply path fields

- `apply_attempt_id` (current or most recent)
- `apply_attempt_ordinal`
- `apply_path_state` (`active`, `terminal`, `superseded`, `abandoned`)
- `recovery_state` (`none`, `retrying`, `resumed`, `correcting`, `superseded`, `abandoned`)
- `last_recovery_action`
- `last_recovery_at`

### Semantics by path type

#### Resumed apply path

- Same attempt identity is visible.
- `recovery_state=resumed` until terminal or superseded transition.
- Step history shows prior interruption/defer plus resumed transitions.

#### Retried apply path

- New attempt identity is visible with incremented ordinal.
- Prior attempt linked as ancestor.
- Client can distinguish previous failure/partial/deferred history from current active attempt.

#### Corrected apply path

- Correction record visible and linked to affected results/steps.
- If new result objects are emitted, lineage is explicit with `supersedes` and result/log references.

#### Superseded apply path

- Prior attempt marked terminal-superseded.
- Current attempt indicates supersession linkage.
- Status APIs should return active attempt plus reference to superseded chain.

## `results_in`, `supersedes`, review history, and logs through recovery

### `results_in` behavior through retries/corrections

1. `results_in` remains the proposal-level view of committed resulting artifacts.
2. During non-terminal paths, it may be partial but must only list committed outputs.
3. When correction supersedes earlier outputs, prior outputs remain traceable through lineage/logs; proposal-level `results_in` may reflect latest canonical outputs while historical outputs remain discoverable via review/apply history and logs.

### `supersedes` behavior through correction and superseded attempts

- Correction or replacement outputs should carry `supersedes` relationships to prior outputs when canonical lineage advances.
- Superseding an attempt does not erase previous result objects; it changes active path semantics and requires explicit trace links.

### Review history behavior

Review history should preserve both decision history and apply/recovery milestones.

Minimum history coverage:

- acceptance/rejection/withdrawal decisions (Slice 3)
- apply attempt lifecycle events (Slice 4)
- recovery events and conflict events (Slice 5)
- supersession and abandonment markers

### Log linkage behavior

- Every attempt and recovery action should emit append-oriented logs.
- Status responses should provide `log_refs` or equivalent pointers for machine replay/debug.
- Log links must allow reconstruction of how final materialization state emerged from accepted decision plus recovery chain.

## Interaction with Slice 2 operations and Slice 3/4 semantics

### Slice 2 operation surface compatibility

These semantics are designed to fit the accepted Slice 2 bounded surface (`get_object_by_id`, `list_objects`, `get_traceability_links`, `submit_proposal`, `get_proposal_status`) and to remain compatible with future review/apply operation shapes or implementation surfaces without requiring workflow-engine-specific API commitments in this slice.

### Slice 3 compatibility

- Proposal lifecycle states and decision records remain unchanged.
- Invalid transition and conflict handling are strengthened through typed apply/recovery conflict categories, not lifecycle redefinition.

### Slice 4 compatibility

- Slice 4 apply states remain authoritative.
- Slice 5 adds step-level and recovery-path semantics to improve interoperability under partial, failed, deferred, and resumed/retried/corrected conditions.

## Non-goals and deferred concerns

### Non-goals in this slice

- No workflow engine/runtime scheduler specification.
- No authentication/user-management implementation details.
- No deployment/runtime hardening details.
- No Phase 5 maintainer/compiler workflow implementation.
- No direct canonical-write authority grant to agents.

### Deferred concerns

- Optional profile-specific recovery policy presets beyond baseline semantics.
- Performance/SLO contracts for long-running apply attempts.
- Rich UI/UX representations for apply timelines.
- Advanced cross-workspace transactional semantics.

## Acceptance checklist (slice-level)

This slice is complete when:

1. Multi-step apply sequencing semantics are explicit (ordering, identity/correlation, partial progress, completion criteria).
2. Conflict categories are distinguishable and machine-visible (`state_race`, `stale_lineage`, `target_replaced`, `policy_scope`, `duplicate_idempotency`).
3. Recovery paths (`retry`, `resume`, `correction`, `supersede_attempt`, `abandon`) are bounded and traceable.
4. Status/result semantics distinguish resumed, retried, corrected, and superseded paths.
5. `results_in`, `supersedes`, review history, and logs remain coherent through retries/corrections.
6. Canonical publication remains human-governed and outside direct agent authority.
7. Next-slice pointer remains in Phase 4 unless explicit baseline closure is declared.

## Next-slice pointer

The next bounded slice should remain inside Phase 4 and focus on interoperability profile refinement for policy-driven apply/recovery behavior (for example baseline profile presets and compatibility guidance), without introducing a workflow engine or changing authority architecture.
