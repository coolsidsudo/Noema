# Noema Phase 4 Agent Operation-State Semantics (Slice 3)

## Purpose and boundary

This document defines baseline operation-state semantics for the accepted Phase 4 machine-facing operation contract.

It extends:

- `docs/noema-phase4-agent-interface-baseline.md` (Slice 1)
- `docs/noema-phase4-agent-surface-contract.md` (Slice 2)

This slice is semantics-definition work only. It does not implement a workflow engine, auth stack, or deployment/runtime hardening.

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

## Scope in this slice

This slice defines:

1. Proposal lifecycle states and transition rules.
2. Review-decision and result contracts.
3. Interaction expectations for `submit_proposal` and `get_proposal_status`.
4. Invalid transition and conflict behavior.
5. Minimum audit fields for state-change traceability.
6. Baseline policy-profile presets for common agent participation modes.

This slice does not define a full policy engine, identity provisioning system, or automation runtime.

## Proposal operation states (baseline)

At operation level, proposal status is constrained to:

- `draft`
- `under_review`
- `accepted`
- `rejected`
- `withdrawn`

These values match baseline proposal status semantics defined in prior docs and are treated as a closed set for this slice.

## Baseline transition model

### Allowed transitions

1. `draft -> under_review`
2. `draft -> withdrawn`
3. `under_review -> accepted`
4. `under_review -> rejected`
5. `under_review -> withdrawn`

### Terminal-state behavior

- `accepted`, `rejected`, and `withdrawn` are terminal states at baseline depth.
- No baseline transition is defined from any terminal state back into `draft` or `under_review`.
- Re-open/reconsider behavior is deferred; a new proposal should be created instead.

### Transition matrix

| From | To | Baseline allowed | Baseline initiators |
| --- | --- | --- | --- |
| `draft` | `under_review` | yes | proposer, reviewer-role human, bounded workflow service acting on behalf of policy |
| `draft` | `withdrawn` | yes | proposer, reviewer-role human, bounded workflow service acting on behalf of policy |
| `draft` | `accepted` | no | none |
| `draft` | `rejected` | no | none |
| `under_review` | `accepted` | yes | reviewer-role human; optionally maintainer-support service with explicit human-governed authority |
| `under_review` | `rejected` | yes | reviewer-role human; optionally maintainer-support service with explicit human-governed authority |
| `under_review` | `withdrawn` | yes | proposer (subject to policy), reviewer-role human |
| terminal (`accepted`/`rejected`/`withdrawn`) | any other state | no | none |

## Baseline actor semantics

### Proposer actor

A proposer (human or agent identity) may:

- create/submit proposals
- move own proposal from `draft` to `under_review`
- withdraw own proposal when policy allows

A proposer may not directly mark a proposal `accepted` or `rejected` at baseline depth.

### Reviewer actor

A reviewer-role human may:

- move `under_review` proposals to `accepted` or `rejected`
- withdraw proposals where policy allows
- request changes outside this state machine by creating follow-up proposal objects

### Maintainer-support actor (bounded)

A maintainer-support service/agent may:

- assist with queue handling and review support
- execute state changes only where explicit scoped authority exists
- never bypass human-governed canonical publication boundaries

## Review decision record contract

When a review transition to `accepted` or `rejected` occurs, a decision record should exist as structured proposal metadata and/or linked event content.

### Required baseline decision fields

- `proposal_id`
- `decision` (`accepted` or `rejected`)
- `decided_at` (ISO 8601)
- `decided_by` (stable human/actor identity)
- `rationale` (human-readable reason)
- `request_id` or equivalent operation correlation id

### Recommended baseline decision fields

- `reviewer_role`
- `policy_profile`
- `conditions` (if acceptance is conditional)
- `evidence_refs` (object IDs used in decision)
- `notes`

### Withdrawn decision semantics

For `withdrawn`, a lightweight transition reason should be recorded:

- `withdrawn_at`
- `withdrawn_by`
- `withdrawn_reason` (optional but recommended)

## Accepted/rejected/withdrawn outcome semantics

### Accepted

Meaning:

- Review has approved the proposal outcome within baseline authority boundaries.
- Acceptance does not grant unrestricted direct write authority to agents.

Contract expectations:

- `results_in` should reference one or more resulting canonical/derived object IDs when concrete result objects exist.
- If acceptance only records approval intent and application is deferred, `results_in` may be empty at transition time but should later resolve via follow-up update/log linkage.
- Acceptance should include application scope semantics (`full` or `partial`) in review/result metadata.

### Rejected

Meaning:

- Proposal was reviewed and not approved for canonical outcome.

Contract expectations:

- `results_in` must not point to canonical apply results produced from this rejected proposal.
- Decision rationale should explain rejection grounds.
- Follow-up work should occur through a new proposal.

### Withdrawn

Meaning:

- Proposal removed from active review path without acceptance/rejection decision.

Contract expectations:

- `results_in` must not represent canonical apply results for withdrawn proposals.
- Withdrawal metadata should preserve actor and reason where available.

## `results_in` contract expectations

### When `results_in` should exist

`results_in` should exist when a proposal outcome has produced specific resulting object(s), typically after acceptance and application.

Examples:

- accepted proposal creates a new `structured` object
- accepted proposal updates/replaces one or more target objects
- accepted proposal emits a canonical decision record object

### When `results_in` must not exist

- rejected proposals
- withdrawn proposals
- accepted proposals that have not yet produced concrete result objects (temporary empty/absent `results_in` is permitted, but this should be traceable through status/log fields)

### Partial application representation

When an accepted proposal is only partially applied at baseline depth:

- `application_state` should indicate `partial`
- `results_in` should include only completed result object IDs
- unresolved scope should be explicit (for example `pending_targets` list or equivalent metadata)
- follow-up events/proposals should continue traceability for unfinished scope

## Review history contract expectations

Each proposal should expose a review history view suitable for `get_proposal_status`.

### Baseline review-history fields

Each entry should include:

- `event_id`
- `proposal_id`
- `from_state`
- `to_state`
- `actor_id`
- `actor_type` (`human` or `agent`/`service`)
- `timestamp`
- `reason` or `summary`
- `request_id` (or equivalent)

### Ordering and immutability

- History should be append-oriented and ordered by event time.
- Corrections should be represented as new events, not silent mutation.

## Log-link expectations

Proposal status changes should be linkable to log events and vice versa.

Baseline expectation:

- each state transition emits (or references) a log event
- proposal metadata may include `latest_log_id` and/or transition-event references
- logs should include enough identifiers to reconstruct lifecycle and reviewer attribution

This keeps proposal lifecycle aligned with existing traceability conventions across raw/structured/proposals/logs.

## Invalid transition behavior

When a requested transition violates baseline rules:

- operation should fail with `ok: false`
- error category should be `conflict`
- error code should be machine-parseable (for example `INVALID_PROPOSAL_TRANSITION`)
- error details should include attempted `from_state`, requested `to_state`, and applicable policy/profile context

No implicit fallback transitions should occur.

## Conflict semantics

At baseline depth, conflicts include at least:

1. **State race conflict**: proposal already moved by another actor.
2. **Version conflict**: stale revision token / outdated status snapshot.
3. **Policy conflict**: actor scope valid for read but not for requested transition.

Conflict handling expectations:

- return `conflict` (or `forbidden` for pure policy denial where no state race is present, consistent with Slice 2 categories)
- include retry guidance where safe
- preserve auditable failed-attempt eventing where deployment policy requires it

## Minimum audit fields for state changes

Every state-change event should include at least:

- `event_id`
- `proposal_id`
- `workspace`
- `from_state`
- `to_state`
- `actor_id`
- `actor_type`
- `occurred_at`
- `request_id`
- `reason` (or structured rationale reference)

Recommended additions:

- `policy_profile`
- `scope_snapshot`
- `review_decision_id` (for accepted/rejected transitions)
- `log_id`

## Interaction with `submit_proposal`

Baseline interaction rules:

- `submit_proposal` creates or updates proposal-layer artifacts only.
- Initial status after submission is typically `draft` unless policy allows immediate `under_review` placement.
- `submit_proposal` must not directly produce `accepted` or `rejected` status as a shortcut.
- Submission response should provide enough identifiers for later `get_proposal_status` polling/retrieval.

## Interaction with `get_proposal_status`

`get_proposal_status` should return operation-state information sufficient for deterministic client behavior.

At baseline, include:

- current proposal state
- latest state-change timestamp and actor
- review-decision payload when state is `accepted` or `rejected`
- `results_in` linkage (when present)
- review-history summary or cursor to full history
- log linkage hints (event/log identifiers)

If proposal is out-of-scope, apply Slice 2 `not_found`/`forbidden` handling conventions without leaking restricted details.

## Policy-profile presets (baseline depth)

These presets are reusable baseline participation modes, not a full authorization framework.

### 1) Read-only agent

Capabilities:

- `get_object_by_id`
- `list_objects`
- `get_traceability_links`
- `get_proposal_status` (scope-limited)

Restrictions:

- cannot call `submit_proposal`
- cannot initiate proposal state transitions

### 2) Proposal-submitting agent

Capabilities:

- read-only set above
- `submit_proposal`
- may move own proposal `draft -> under_review` where policy allows
- may withdraw own proposal where policy allows

Restrictions:

- cannot accept/reject proposals
- no direct canonical publication authority

### 3) Reviewer-visible but non-publishing agent

Capabilities:

- proposal-submitting capabilities
- visibility into review status/history for relevant workspaces
- may provide review-support annotations via proposal/log pathways

Restrictions:

- cannot finalize `accepted`/`rejected`
- cannot directly publish canonical structured changes

### 4) Maintainer-support agent (bounded)

Capabilities:

- broad read/query over assigned workspace scope
- proposal creation and maintenance-oriented proposal updates
- optional workflow-assist transitions when explicitly delegated by policy

Restrictions:

- remains bounded by review-governed publication model
- no unrestricted filesystem write path as authority bypass
- no replacement of human-governed canonical approval

## Explicit non-goals and deferred concerns

This slice explicitly does not define or implement:

- full workflow/orchestration engine semantics
- complete auth/user provisioning lifecycle
- deployment/runtime hardening model
- maintainer/compiler operational automation details (Phase 5)
- direct canonical-write authority for agent identities
- protocol lock-in to MCP-only operation
- domain-specific policy bundles

## Drift checks for this slice

This document does not:

- redefine Noema architecture semantics
- redefine object classes
- redefine metadata-profile semantics
- redefine relationship/traceability semantics
- redefine index/catalog semantics
- change Phase 3 human-client semantics
- change Phase 4 Slice 1/2 interface boundaries
- mix control-layer workflow process into system-definition semantics

## Next-slice pointer

After Phase 4 Slice 3 baseline state semantics, the next planned execution pointer remains inside Phase 4 unless reprioritized:

- **Phase 4 next slice: deeper operation contracts for review/apply execution behavior and interoperability hardening**

After remaining Phase 4 baseline closure, queue continues to:

- **Phase 5 — Maintainer workflow baseline**
