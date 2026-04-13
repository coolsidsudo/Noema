# Noema Apply/Recovery Interoperability Consistency and Conformance Guidance

## Purpose and boundary

This document defines the stable conformance-guidance layer for cross-implementation interpretation of accepted apply/recovery semantics.

This stable system-definition document originates from the accepted Phase 4 conformance-guidance slice after Slice 6.

It extends accepted semantics from:

- `docs/noema-agent-operation-state-semantics.md` (Slice 3)
- `docs/noema-review-apply-interoperability-semantics.md` (Slice 4)
- `docs/noema-review-apply-hardening-semantics.md` (Slice 5)
- `docs/noema-apply-recovery-policy-profiles.md` (Slice 6)

This document is implementation-light and semantics-preserving. It does not redefine accepted object classes, metadata-profile semantics, relationship/traceability semantics, index/catalog semantics, human-client behavior, or accepted Slice 1/2/3/4/5/6 semantics.

It does not define a workflow engine, CI harness, protocol-level conformance suite, runtime orchestrator, auth/user-management, deployment-hardening model, or Phase 5 maintainer-runtime behavior.

## Baseline references

This document aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `docs/noema-index-catalog-baseline.md`
- `docs/noema-human-client-baseline.md`
- `docs/noema-agent-interface-baseline.md`
- `docs/noema-agent-surface-contract.md`
- `docs/noema-agent-operation-state-semantics.md`
- `docs/noema-review-apply-interoperability-semantics.md`
- `docs/noema-review-apply-hardening-semantics.md`
- `docs/noema-apply-recovery-policy-profiles.md`

## Relationship to accepted Slice 4/5/6 semantics

### Preservation rule

Slice 4 defines baseline decision/apply semantics.

Slice 5 hardens multi-step apply, conflict typing, and bounded recovery semantics.

Slice 6 constrains policy-profile interpretation for apply/recovery behavior.

This document does not alter those semantics. It defines a cross-implementation interpretation layer so independently built systems can be compared as "conformant enough" without requiring shared internals.

### Why a conformance layer is needed after Slice 6

Slice 6 intentionally leaves room for richer local execution internals. Without a final conformance layer, two implementations can both claim Slice 6 alignment while exposing machine-visible behavior that is not comparably interpretable.

This conformance layer closes that gap by requiring stable interpretation behavior across:

1. status exposure;
2. lineage/result exposure;
3. conflict and recovery interpretation;
4. policy-profile interpretation; and
5. log/traceability exposure.

## Bounded definition of interoperability consistency

For this slice, **interoperability consistency** means:

- two or more implementations expose machine-visible outputs that allow a client to reach equivalent apply/recovery interpretation outcomes for the same accepted semantic scenario, even if local storage, execution strategy, or transport differs.

Equivalent interpretation outcomes require that clients can consistently determine:

- decision/apply separation;
- apply-state meaning;
- recovery-path meaning;
- result/lineage meaning;
- effective policy-profile meaning; and
- audit-trace linkage meaning.

Interoperability consistency does not require:

- identical API shapes;
- identical field names;
- identical step engines;
- identical event ordering internals (beyond accepted replay semantics);
- identical deployment/runtime architecture.

## Required conformance dimensions

Implementations claiming conformance guidance alignment should satisfy all dimensions below.

### 1) Status interpretation conformance

Minimum expectation:

- accepted Slice 4/5 apply-state semantics are machine-visible and unambiguous (`pending`, `in_progress`, `applied`, `partial`, `failed`, `deferred`).

Interpretation requirement:

- a client can determine whether accepted scope is not started, in progress, partially materialized, terminally applied, failed, or intentionally deferred.

### 2) Lineage/result interpretation conformance

Minimum expectation:

- `results_in`, pending/remaining scope visibility, and supersession lineage (where used) are exposed in a machine-interpretable way.

Interpretation requirement:

- a client can distinguish committed outcomes from pending scope and can track replacement lineage across retries/corrections/superseding attempts.

### 3) Conflict/recovery interpretation conformance

Minimum expectation:

- typed conflicts and bounded recovery actions from Slice 5 are externally interpretable.

Interpretation requirement:

- a client can determine which conflict class occurred, what recovery action path was taken (`retry`, `resume`, `correction`, `supersede_attempt`, `abandon`), and what state transition followed.

### 4) Policy-profile interpretation conformance

Minimum expectation:

- effective profile and profile snapshot context from Slice 6 are externally visible (or semantically equivalent), including profile versioning/evaluation context.

Interpretation requirement:

- a client can determine whether observed recovery behavior is compatible with the declared effective policy profile.

### 5) Log/traceability interpretation conformance

Minimum expectation:

- apply/recovery status and outcome interpretation is linked to trace records sufficient for audit replay.

Interpretation requirement:

- a client can correlate proposal, attempt, step/recovery transitions, and resulting object outcomes without relying on non-portable private internals.

## Minimum cross-implementation conformance matrix

This matrix is intentionally bounded. It defines minimum external interpretation expectations, not engine internals.

| Apply-state / path condition | Recovery action expectation | Policy-profile compatibility expectation | Minimum externally interpretable outcome |
| --- | --- | --- | --- |
| `pending` after acceptance | no recovery action required yet | profile snapshot is present/evaluable | client can determine accepted-but-not-materialized state |
| `in_progress` with no terminal step | `resume` MAY occur if allowed by profile | profile constraints are machine-visible before/through resume | client can distinguish active materialization from stalling/defer |
| `partial` with committed subset | `resume`, `retry`, or `correction` chosen under typed rationale | selected action is compatible with effective profile | client can distinguish committed `results_in` from remaining scope |
| `failed` terminal attempt | `retry`, `correction`, `supersede_attempt`, or `abandon` recorded | disallowed actions are not represented as successful transitions | client can interpret failed path and subsequent recovery branch |
| `deferred` intentional non-terminal pause | `resume` or `abandon` path remains explicit | defer reason and profile compatibility are visible | client can distinguish policy/scheduling defer from failure |
| `applied` complete materialization | no additional recovery required for completion claim | completion claim remains consistent with profile gating rules | client can interpret materially complete accepted scope |

## Minimum validation scenario set

Implementations should be able to demonstrate these scenarios in documentation, manual verification records, or local validation artifacts.

No required harness format is imposed.

### Positive scenarios (minimum)

1. **Accepted -> pending -> applied (no conflict)**
   - Demonstrates status progression and completion interpretation.
2. **Accepted -> in_progress -> partial -> applied**
   - Demonstrates partial scope visibility and final completion reconciliation.
3. **Accepted -> failed -> retry -> applied**
   - Demonstrates recovery branching and lineage/result continuity.
4. **Accepted -> failed typed-conflict -> correction -> applied**
   - Demonstrates typed conflict interpretation and bounded correction path.
5. **Accepted under declared profile with defer gate -> deferred -> resume -> applied**
   - Demonstrates policy-profile compatibility across defer/resume transitions.

### Negative scenarios (minimum)

1. **Invalid completion claim**
   - `apply_state=applied` while required scope remains pending.
   - Must be detectable as non-conformant interpretation output.
2. **Uninterpretable recovery transition**
   - recovery action implied in logs but absent from externally interpretable state view.
   - Must be detectable as conformance gap.
3. **Profile-incompatible action presentation**
   - action represented as successful even though effective profile disallows it.
   - Must be detectable as policy-compatibility failure.
4. **Result/lineage ambiguity**
   - committed outcomes cannot be distinguished from proposed/pending outcomes.
   - Must be detectable as lineage/result conformance failure.
5. **Traceability break**
   - proposal/attempt/outcome cannot be correlated for audit interpretation.
   - Must be detectable as log/traceability conformance failure.

## Compatibility guidance for richer implementations

Richer implementations may vary internally while remaining conformant if they preserve stable external interpretation semantics.

Allowed internal variation examples:

- multi-queue or event-sourced runtime internals;
- protocol-specific transport adapters;
- richer policy engines with additional local controls;
- expanded conflict taxonomies that map to Slice 5 baseline categories;
- additional step/status detail beyond baseline fields.

Required preservation constraints:

1. Baseline apply/recovery meanings remain externally mappable.
2. Additional states/actions are projected to accepted baseline interpretation without ambiguity.
3. Local policy richness never suppresses required status/lineage/traceability visibility.
4. Human-governed canonical publication and bounded machine authority remain intact.
5. Clients that only know accepted Slice 4/5/6 semantics can still interpret outcomes correctly.

## Explicit non-goals and deferred concerns

This slice does not:

- define a normative protocol test suite;
- define CI conformance automation;
- define runtime orchestration internals;
- define deployment hardening or auth/user identity systems;
- define maintainer operational workflows (Phase 5 scope);
- redefine existing object/metadata/relationship/index semantics.

Deferred concerns:

- transport-specific conformance profiles;
- optional formal certification workflow;
- implementation benchmark comparability;
- richer multi-workspace fleet governance semantics.

## Slice completion checklist

A change set implementing this slice should satisfy all checklist items below.

- [x] A stable system-definition document exists for apply/recovery interoperability consistency and profile-compatibility conformance guidance.
- [x] The document extends accepted Slice 4/5/6 semantics without redefining them.
- [x] Required conformance dimensions are explicit for status, lineage/result, conflict/recovery, policy-profile, and log/traceability interpretation.
- [x] A bounded minimum cross-implementation conformance matrix is defined.
- [x] Minimum positive/negative validation scenarios are defined without prescribing a harness.
- [x] Compatibility guidance for richer local implementations is explicit.
- [x] Non-goals and deferred concerns are explicit.
- [x] System-definition semantics remain in `docs/` and avoid control-workflow mixing.

## Drift-check statement

This slice introduces a conformance-interpretation layer only.

It does not change architecture invariants, object classes, metadata profile semantics, relationship/traceability semantics, index/catalog semantics, accepted Phase 3 behavior, or accepted Phase 4 Slice 1/2/3/4/5/6 semantics.

## Next-slice pointer

Default next step is to pivot toward **Phase 5 maintainer workflow baseline** unless a concrete, bounded, unresolved Phase 4 interoperability gap is explicitly identified and accepted.
