# Noema Review/Apply Execution Interoperability Semantics

## Purpose and boundary

This document defines stable interoperability semantics at the boundary between review decisions and apply/materialization outcomes for proposal operations in Noema.

This stable system-definition document originated from the accepted Phase 4 Slice 4 baseline.

It extends:

- `docs/noema-agent-interface-baseline.md` (Slice 1)
- `docs/noema-agent-surface-contract.md` (Slice 2)
- `docs/noema-agent-operation-state-semantics.md` (Slice 3)

This slice is semantics-definition work only. It does not implement a workflow engine, auth/user management, deployment hardening, or direct canonical-write authority for agents.

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

## Scope in this slice

This slice defines:

1. Interoperability semantics between proposal review outcomes and apply/materialization outcomes.
2. A minimum apply-state contract for machine-visible proposal outcome handling.
3. How `results_in`, `supersedes`, review history, and logs interoperate across apply states.
4. Partial/failure/deferred apply semantics and baseline idempotency expectations.
5. How clients using `get_proposal_status` should distinguish decision completion from materialization completion.

This slice does not define runtime orchestration details or direct publication authority models.

## Core interoperability rule: decision and materialization are distinct

A proposal review decision and a proposal apply/materialization outcome are related but separate state dimensions.

- **Review decision state** answers whether reviewers accepted/rejected/withdrew the proposal intent.
- **Apply state** answers whether accepted intent has been materialized into concrete resulting object state.

At baseline:

- `accepted` means **decision complete in favor**.
- `accepted` does not, by itself, guarantee materialization completion.
- canonical publication remains human-governed and outside direct agent authority.

## Baseline outcome distinctions

For interoperability, clients and services should distinguish at least the following outcome situations.

### 1) Review accepted

Meaning:

- Review decision is complete (`accepted`).
- Apply/materialization may be pending, partial, complete, deferred, or failed.

### 2) Accepted but pending apply

Meaning:

- Proposal is accepted.
- No materialized outcome object has been committed yet.
- apply execution has not started or has started without producing committed result objects.

### 3) Accepted and applied

Meaning:

- Proposal is accepted.
- All in-scope accepted changes are materially reflected in resulting object state.
- required apply logs and result links are present.

### 4) Accepted and partially applied

Meaning:

- Proposal is accepted.
- A strict subset of accepted scope is materialized.
- remaining scope is explicit and traceable.

### 5) Accepted but apply failed/deferred

Meaning:

- Proposal is accepted.
- apply execution either failed (error path) or is intentionally deferred (policy/scheduling/dependency path).
- failure/defer reasons are visible in bounded machine-readable form.

## Minimum apply-state contract (baseline)

When proposal status is `accepted`, machine-facing status views should expose an apply-state contract (as dedicated fields or equivalent semantic encoding).

### Required minimum fields

- `apply_state` (enum):
  - `pending`
  - `in_progress`
  - `applied`
  - `partial`
  - `failed`
  - `deferred`
- `apply_updated_at` (ISO 8601)
- `apply_summary` (short machine-visible/human-readable summary)
- `materialization_complete` (boolean)

### Required lineage/result fields for accepted proposals

- `results_in` (array of resulting object IDs, possibly empty while `pending|in_progress|deferred|failed`)
- `pending_targets` (array; required when `apply_state=partial` and recommended when `pending|deferred`)
- `failed_targets` (array; required when `apply_state=failed` and optional for `partial`)

### Required decision/apply separation fields

- `decision_completed_at` (ISO 8601; timestamp of acceptance decision)
- `decision_completed_by` (review actor identity)
- `materialization_completed_at` (ISO 8601 or null)

`decision_completed_at` and `materialization_completed_at` must be independently interpretable.

## Apply-state semantics by value

### `pending`

- Decision accepted.
- Apply not yet started or no committed materialization step recorded.
- `materialization_complete=false`.
- `results_in` may be empty.

### `in_progress`

- Decision accepted.
- Apply has started with at least one apply event recorded.
- `materialization_complete=false`.
- `results_in` may be partially populated only for committed outputs.

### `applied`

- Decision accepted.
- Full accepted scope materialized.
- `materialization_complete=true`.
- `results_in` must include all resulting canonical object IDs.

### `partial`

- Decision accepted.
- Only subset materialized.
- `materialization_complete=false`.
- `results_in` includes only completed results.
- `pending_targets` must identify unapplied scope.

### `failed`

- Decision accepted.
- Apply attempt failed to complete accepted scope.
- `materialization_complete=false`.
- `failed_targets` and `apply_failure` details are required.

### `deferred`

- Decision accepted.
- Apply intentionally postponed.
- `materialization_complete=false`.
- `apply_deferred` details are required.

## `results_in` interoperability semantics

### Normative behavior

1. `results_in` must not be treated as implied by `accepted`; it is evidence of materialized outputs.
2. For non-accepted terminal decisions (`rejected`, `withdrawn`), `results_in` must not represent canonical apply outcomes from that proposal.
3. For `accepted` proposals:
   - `apply_state=applied` -> `results_in` must be non-empty unless accepted scope explicitly yields no object change (rare and must be explained in apply logs).
   - `apply_state=partial` -> `results_in` must include only successfully materialized subset.
   - `apply_state=pending|in_progress|deferred|failed` -> `results_in` may be empty or partial, but must align with apply logs and state fields.

### Stability expectations

- Once a result object is canonically materialized, its ID should remain stable in `results_in`.
- Corrections should be additive (`supersedes` and logs), not silent removal of history.

## `supersedes` and structured lineage semantics

`supersedes` should appear when apply materialization replaces or version-advances an existing structured artifact.

### Required explicit lineage cases

Lineage must be explicit for at least:

1. **Full replacement** of a structured object.
2. **Versioned update** where prior canonical object remains retained.
3. **Split/merge outcomes** where one accepted proposal yields multiple resulting structured objects or consolidates multiple prior targets.

### Interoperability expectations

- If a result object supersedes a prior object, this must be visible through `supersedes` (or equivalent lineage field) on the resulting object and/or traceability links.
- `results_in` and `supersedes` must be consistent: result IDs listed in `results_in` should be the same artifacts that carry replacement/update lineage.
- If apply updates in place without new ID issuance, explicit update lineage still must be represented in logs and proposal apply fields (for example changed revision token/version marker).

## Apply-event and log interoperability

Apply behavior must remain reconstructable through log links and proposal history.

### Minimum apply-event audit fields

Each apply-related event should include at least:

- `event_id`
- `event_type` (`apply_started`, `apply_step_succeeded`, `apply_step_failed`, `apply_completed`, `apply_deferred`, `apply_resumed`, `apply_correction`)
- `proposal_id`
- `workspace`
- `actor_id`
- `actor_type` (`human`, `agent`, `service`)
- `occurred_at` (ISO 8601)
- `request_id` (or equivalent correlation id)
- `apply_state_before`
- `apply_state_after`
- `target_ids` (scope under action)
- `result_ids` (materialized IDs produced by this event; empty when none)
- `summary`

Recommended additions:

- `error_code`, `error_message`, `retryable` (for failure events)
- `deferred_reason`, `resume_after` (for deferred events)
- `policy_profile`
- `supersedes_links`

### Required linkage behavior

- apply logs should `records_event_for` proposal ID and any affected structured IDs.
- proposal status should expose `log_refs` or equivalent pointers to apply events.
- result structured objects should be traceable back to proposal via `results_in` and logs.

## Failure and deferred-apply semantics

### Failed apply (`apply_state=failed`)

Required machine-visible fields:

- `apply_failure` object with:
  - `failed_at`
  - `failed_by` (actor/service identity)
  - `error_code`
  - `message`
  - `retryable` (boolean)
  - `failed_targets`

Semantics:

- decision remains accepted unless superseded by a later governance action.
- failure does not retroactively invalidate review decision.
- follow-up apply attempts or successor proposals must remain traceable.

### Deferred apply (`apply_state=deferred`)

Required machine-visible fields:

- `apply_deferred` object with:
  - `deferred_at`
  - `deferred_by`
  - `reason_code`
  - `reason`
  - `resume_condition` or `resume_after` (if known)

Semantics:

- deferral is intentional non-completion, not failure.
- accepted decision remains valid while waiting on deferred conditions.
- status polling must make deferment explicit rather than appearing as silent inactivity.

## Partial-apply semantics

When `apply_state=partial`, the contract must explicitly identify applied and unapplied scope.

Required fields/semantics:

- `results_in` includes applied subset only.
- `pending_targets` includes remaining accepted targets.
- `partial_apply` object includes:
  - `partial_at`
  - `partial_by`
  - `applied_targets`
  - `pending_targets`
  - `notes`

Interoperability expectations:

- `get_proposal_status` consumers can deterministically see that decision is complete but materialization is incomplete.
- follow-up apply events or proposals must preserve continuity of the same accepted intent.

## Baseline idempotency and interoperability expectations

To keep cross-implementation behavior consistent:

1. Apply operations should support idempotent retry semantics using operation/request correlation (`request_id`, optional idempotency key).
2. Re-processing the same accepted apply step should not duplicate canonical results.
3. Duplicate detection may return existing `results_in` and latest apply-state without re-materialization.
4. Apply events should be append-oriented and correlation-linked so clients can reconcile retries.
5. Interoperable clients should treat `applied` as completion only when `materialization_complete=true` and consistent `results_in`/logs are present.

This defines behavior expectations without prescribing a specific workflow engine implementation.

## `get_proposal_status` interpretation guidance

Slice 2 operation shape remains valid; this slice adds interpretation requirements.

For deterministic client polling, `get_proposal_status` should allow consumers to distinguish at least:

- `decision_complete` (true when proposal status is terminal)
- `decision_outcome` (`accepted|rejected|withdrawn`)
- `materialization_state` (`not_applicable|pending|in_progress|applied|partial|failed|deferred`)
- `materialization_complete` (boolean)

Recommended interpretation matrix:

| Proposal status | apply_state | decision_complete | materialization_complete | Interpretation |
| --- | --- | --- | --- | --- |
| `draft`/`under_review` | n/a | false | false | Decision pending |
| `rejected`/`withdrawn` | `not_applicable` | true | false | Decision complete, no canonical materialization path |
| `accepted` | `pending`/`in_progress` | true | false | Decision complete, materialization pending |
| `accepted` | `partial` | true | false | Decision complete, materialization partial |
| `accepted` | `failed` | true | false | Decision complete, materialization failed |
| `accepted` | `deferred` | true | false | Decision complete, materialization deferred |
| `accepted` | `applied` | true | true | Decision complete, materialization complete |

## Interaction with Slice 2 operations and Slice 3 state semantics

### Slice 2 continuity

No new baseline operation names are required in this slice. Existing operations remain:

- `submit_proposal`
- `get_proposal_status`
- `get_traceability_links`
- `get_object_by_id`
- `list_objects`

This slice constrains how proposal outcome fields should interoperate when returned by these operations.

### Slice 3 continuity

Slice 3 proposal status transitions remain unchanged:

- lifecycle decisions (`accepted`, `rejected`, `withdrawn`) stay proposal decision semantics
- apply/materialization semantics are an additional dimension layered after acceptance

No transition rule in Slice 3 is redefined by this slice.

## Explicit non-goals and deferred concerns

This slice does **not** define or implement:

- workflow/orchestration engine runtime behavior
- task queue or scheduler architecture
- lock/transaction internals for apply execution
- auth/user management or credential provisioning
- deployment/runtime hardening
- direct agent canonical publication authority
- domain-specific materialization policies
- global graph/query standards beyond accepted baseline operations

## Drift-check statement

This document does not:

- redefine Noema architecture semantics
- redefine object classes
- redefine metadata-profile semantics
- redefine relationship/traceability semantics
- redefine index/catalog semantics
- change Phase 3 human-client semantics
- change Phase 4 Slice 1/2/3 boundaries
- mix control-layer process details into system-definition semantics

## Next-slice pointer

After Phase 4 Slice 4 review/apply interoperability semantics, the next planned execution pointer remains inside Phase 4:

- **Phase 4 next slice: review/apply interoperability hardening for multi-step apply sequencing, richer conflict semantics, and bounded recovery semantics while preserving implementation-light posture and human-governed canonical publication.**

Phase 5 remains queued after remaining Phase 4 baseline closure.
