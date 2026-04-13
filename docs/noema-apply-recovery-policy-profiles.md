# Noema Apply/Recovery Policy-Profile Refinement Interoperability Baseline

## Purpose and boundary

This document defines the stable baseline policy-profile refinement layer for hardened apply/recovery interoperability.

This stable system-definition document originated from the accepted Phase 4 Slice 6 baseline.

It extends accepted semantics from:

- `docs/noema-agent-operation-state-semantics.md` (Slice 3)
- `docs/noema-review-apply-interoperability-semantics.md` (Slice 4)
- `docs/noema-review-apply-hardening-semantics.md` (Slice 5)

This slice is semantics-definition only. It does not redefine accepted object classes, metadata-profile semantics, relationship/traceability semantics, index/catalog semantics, human-client behavior, or prior Slice 1/2/3/4/5 semantics. It does not define workflow-engine internals, scheduler/queue runtime, auth/user-management, deployment hardening, direct canonical-write authority for agents, or Phase 5 maintainer workflows.

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

## Why a policy-profile layer is required after Slice 5

Slice 5 hardened recovery semantics (multi-step apply, typed conflicts, bounded recovery actions, and machine-visible path state), but intentionally deferred profile-driven behavior presets.

Slice 6 adds a bounded profile layer so shared deployments can:

1. expose recovery-policy expectations in machine-visible form;
2. adopt conservative interoperable defaults without local-policy guesswork;
3. vary behavior only within explicit recovery dimensions; and
4. map richer local policy engines back to baseline semantics without changing authority architecture.

## Relationship to accepted Slice 3/4/5 semantics

### Slice 3 participation profiles vs Slice 6 apply/recovery profiles

Slice 3 presets describe **participation capability** (who/what may act on bounded surfaces).

Slice 6 profiles describe **apply/recovery interpretation constraints** once accepted proposals move through hardened apply paths.

They are complementary and non-substitutable:

- Slice 3: capability scope.
- Slice 6: hardened recovery-behavior policy constraints.

### Preservation of Slice 4/5 behavior

Slice 6 does not alter accepted state models or recovery primitives. It only constrains how policy differences are expressed.

Invariants preserved:

- decision/apply separation;
- human-governed canonical publication;
- attributable, scoped, review-bounded machine pathways;
- typed conflicts and bounded recovery semantics;
- coherent `results_in`, lineage, and log traceability.

## Minimum machine-visible policy-profile contract

For accepted proposals with apply/recovery interpretation, machine-visible status MUST include these fields (or semantically equivalent encodings):

- `apply_policy_profile` (string enum)
- `apply_policy_profile_version` (string)
- `recovery_policy_snapshot` (object)
- `approval_expectation` (enum: `standard_review`, `heightened_review`, `manual_checkpoint_required`)
- `delegation_expectation` (enum: `none`, `bounded_assist`, `bounded_with_manual_gate`)
- `recovery_visibility_level` (enum: `baseline`, `detailed`)
- `policy_evaluated_at` (ISO 8601)
- `policy_evaluated_by` (actor/service identity)

### Minimum interpretation requirements

1. Clients can determine the effective policy profile for any accepted apply path.
2. Recovery actions (`retry`, `resume`, `correction`, `supersede_attempt`, `abandon`) are interpretable against the effective profile snapshot.
3. Profile selection never implies direct canonical-write authority for agents.
4. Profile metadata never suppresses required Slice 4/5 status, lineage, conflict, or log visibility.

## Baseline preset set (conservative shared-deployment defaults)

Implementations SHOULD expose at least these baseline presets.

### 1) `shared_conservative`

Intent:

- default for heterogeneous shared deployments where strong intervention gates are preferred.

Baseline behavior:

- manual checkpoints before high-impact recovery transitions;
- minimal autonomous recovery chaining;
- explicit machine-visible recovery-state transitions.

### 2) `shared_balanced`

Intent:

- shared-deployment preset allowing bounded operational efficiency while preserving review governance.

Baseline behavior:

- bounded retry/resume under typed constraints;
- correction and superseding paths remain review-bounded;
- explicit, queryable recovery history remains required.

### 3) `single_workspace_strict`

Intent:

- strict preset for tightly governed workspace scope.

Baseline behavior:

- manual checkpointing for most non-trivial recovery actions;
- highly constrained delegation;
- detailed recovery-state visibility expectations.

These presets are interoperability anchors, not a full policy framework.

## Bounded profile variation by recovery action

Profiles may vary only within the dimensions listed below.

### `retry`

Allowed variation:

- automatic retry policy (`never`, `bounded`, `manual-only`);
- maximum retry attempts before manual checkpoint;
- delay/backoff policy visibility requirements.

Invariant requirements:

- retry remains explicit and traceable;
- no bypass of review-governed publication boundaries;
- failed/superseded lineage remains visible.

### `resume`

Allowed variation:

- whether resume needs manual checkpoint for deferred/paused attempts;
- resume-window constraints;
- precondition revalidation strictness.

Invariant requirements:

- deterministic attempt/step lineage remains intact;
- prior defer/interruption history is never erased.

### `correction`

Allowed variation:

- delegation gate (`bounded_assist` vs manual-gated only);
- mandatory reviewer acknowledgement before continuation;
- correction visibility depth (`baseline` vs `detailed`).

Invariant requirements:

- correction remains explicit, attributable, and auditable;
- supersession/correction lineage remains traceable.

### `supersede_attempt`

Allowed variation:

- threshold for manual approval before superseding;
- whether supersede initiation can be bounded-delegated;
- required conflict prechecks before superseding.

Invariant requirements:

- superseded attempts remain discoverable;
- active resulting path is explicit and machine-visible;
- no hidden replacement of authoritative lineage.

### `abandon`

Allowed variation:

- bounded scope of actors who may trigger abandonment;
- mandatory abandon-rationale template enforcement;
- whether post-abandon review confirmation is required.

Invariant requirements:

- abandonment is terminally explicit;
- reason, actor, and timestamp remain visible;
- abandonment never appears as `applied` success.

## Baseline preset interoperability matrix

The matrix below is a baseline expectation contract for shared deployments.

| Recovery action | `shared_conservative` | `shared_balanced` | `single_workspace_strict` |
| --- | --- | --- | --- |
| `retry` | manual-only or tightly bounded | bounded automatic retry allowed | manual checkpoint before/after each retry |
| `resume` | manual gate for deferred paths | bounded resume when preconditions revalidated | manual gate required |
| `correction` | manual checkpoint required | bounded assist possible with explicit visibility | manual-only correction gate |
| `supersede_attempt` | heightened/manual approval expected | manual approval expected for high-impact scope | manual approval always required |
| `abandon` | manual actor confirmation + rationale | bounded delegated abandon possible with explicit rationale | manual confirmation + post-abandon review confirmation |

Interpretation note:

- This matrix constrains baseline interoperability expectations, not implementation internals.

## How profiles affect approval, delegation, and visibility expectations

Profiles may tighten expectations, but may not weaken baseline governance:

1. **Approval expectations**
   - Profiles may escalate from `standard_review` to `heightened_review` or `manual_checkpoint_required`.
   - Profiles must not remove required review boundaries.

2. **Bounded delegation expectations**
   - Profiles may narrow or permit `bounded_assist` transitions.
   - Profiles must not create unrestricted authority or direct canonical publication power.

3. **Recovery visibility expectations**
   - Profiles may require `baseline` or `detailed` visibility.
   - Profiles must preserve minimum Slice 4/5 machine-visible status, lineage, and log behavior.

## Compatibility guidance for richer local policy engines

Implementations may maintain richer local policy logic (risk scoring, policy graphs, contextual controls) if external behavior remains baseline-interoperable.

### Required compatibility rules

1. **Deterministic mapping:** internal outcomes map deterministically to exposed baseline profile semantics.
2. **No semantic contraction:** local optimization cannot remove required visibility, traceability, or review boundaries.
3. **Stable external interpretation:** baseline clients can interpret behavior without vendor-specific policy internals.
4. **Effective strictness disclosure:** stricter-than-baseline policy outcomes are exposed in status/log surfaces.
5. **Portable records:** exported/federated records keep enough policy-profile context for cross-implementation interpretation.

### Recommended mapping pattern

Maintain an implementation-local mapping table with:

- local policy mode identifier;
- mapped `apply_policy_profile`;
- mapped `approval_expectation`, `delegation_expectation`, and `recovery_visibility_level`;
- notes when local strictness exceeds baseline defaults.

## Explicit non-goals and deferred concerns

This slice does not define:

- participation-profile redesign (Slice 3 remains authoritative);
- new review/apply state machine values;
- workflow engine, scheduler, queue, or orchestration internals;
- auth/user lifecycle or deployment-hardening semantics;
- Phase 5 maintainer-runtime workflows;
- domain-specific policy packs.

## Slice completion checklist

This slice is complete when:

- a stable apply/recovery policy-profile refinement layer is defined;
- Slice 3 participation presets remain distinct from Slice 6 apply/recovery profiles;
- minimum machine-visible policy-profile expectations are explicit;
- conservative baseline presets are defined and interoperable;
- bounded variation is defined for `retry`, `resume`, `correction`, `supersede_attempt`, and `abandon`;
- profile impacts on approval, delegation, and visibility are explicit;
- richer local-policy compatibility guidance is present without authority-architecture change;
- no drift into workflow-engine, auth, deployment, or Phase 5 maintainer semantics.

## Next-slice pointer

The next bounded slice should remain in Phase 4 and focus on interoperability conformance guidance and consistency validation for profile-driven apply/recovery behavior, without introducing workflow-engine internals or changing authority architecture.
