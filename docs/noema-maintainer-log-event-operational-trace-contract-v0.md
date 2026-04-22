# Noema Maintainer Log/Event Schema and Operational Trace Contract V0

## Purpose

This document defines the Phase 8 Slice 3 baseline contract for maintainer operational trace in Noema.

It specifies the minimum event classes, required event fields, linkage rules, and interpretation guidance needed so maintainer behavior is reconstructable and auditable across ingest, compile, lint/coherence, proposal lifecycle handoff, and query-discovered maintenance follow-up.

This is a contract/profile baseline, not a runtime implementation specification.

## Scope boundary for Slice 3

This slice defines:

1. required maintainer operational event classes,
2. required event identity/actor/time/object fields,
3. event linkage rules across `logs/`, `proposals/`, `structured/`, and `raw/` references,
4. append-only and non-rewrite posture for operational trace,
5. interpretation guidance for reviewer/operator reconstruction.

This slice does **not**:

- redesign Slice 1 seam/lane boundaries,
- redesign Slice 2 proposal payload/evidence/provenance contract,
- define Slice 4 executable maintainer-loop runtime realization,
- broaden direct canonical authority,
- treat logs as canonical structured knowledge.

## Baseline references

This contract is constrained by:

- `docs/noema-original-system-design.md` (Sections 7, 9, 10, 13)
- `control/development-plan.md` (Phase 8 objective and Slice 3 scope)
- `control/development-tracker.md` (live continuation context)
- `docs/noema-maintainer-agent-skill-management-schema-v0.md` (maintainer rules and append-log posture)
- `docs/noema-maintainer-loop-contract-baseline-v0.md` (accepted Slice 1 seam/lane contract)
- `docs/noema-proposal-payload-evidence-provenance-contract-v0.md` (accepted Slice 2 proposal contract)
- `control/workflow-baseline.md` (traceable slice workflow expectations)

## Contract anchors

### Anchor A — Operational log lane is append trace, not canonical knowledge lane

Maintainer operational events in `logs/` are durable trace artifacts, not accepted domain truth.

Required implications:

- logs may support reconstruction/audit but do not become canonical structured state,
- logs must not be used as an alternate canonical write lane,
- canonical-impacting changes remain proposal/review/apply governed.

### Anchor B — Event traceability must be linkable and inspectable

Each maintainer event must include enough identity, actor, timing, and object linkage to support replay-oriented inspection by humans and machines.

Required implications:

- event identity and causal links are explicit,
- affected objects and related artifacts are explicitly referenced,
- reviewers can trace event -> proposal -> structured/raw context without hidden state.

### Anchor C — Append-only operational posture

Operational event lanes are append-only by default.

Required implications:

- event records are not silently rewritten to hide prior maintainer behavior,
- corrections are represented as compensating/superseding events,
- redaction (if policy-required) is explicit, attributable, and non-silent.

### Anchor D — Proposal-first and policy-gated apply posture remains intact

Log/event contracts must preserve accepted Slice 1 and Slice 2 governance boundaries.

Required implications:

- proposal emission/lifecycle events may reference proposal artifacts but do not apply canonical changes,
- direct canonical apply remains explicit, exceptional, auditable, and policy-gated,
- query-discovered gaps produce maintenance follow-up trace and/or proposals rather than hidden edits.

## Event class taxonomy (normative minimum)

A conformant maintainer operational trace must support at least the following event classes.

1. `ingest`
   - records source registration/intake outcomes and immediate maintenance impact declaration.
2. `compile`
   - records maintainer compilation/curation runs and structured-impact intent/outcomes.
3. `lint_coherence`
   - records contradiction surfacing, support/lint checks, coherence diagnostics, and severity posture.
4. `proposal_lifecycle`
   - records proposal emission and lifecycle handoff touchpoints (emit/update/supersede/close references).
5. `query_followup`
   - records query-discovered maintenance deficits and emitted follow-up maintenance actions.

Optional subclasses may exist, but implementations must map back to this minimum taxonomy for interoperability.

## Event schema profile (normative minimum fields)

Every maintainer event record in scope must include these fields.

## 1) Event identity and class

Required fields:

- `event_id`: stable unique event identifier.
- `event_class`: one of the required classes (`ingest`, `compile`, `lint_coherence`, `proposal_lifecycle`, `query_followup`).
- `event_type`: finer-grained subtype within class (policy/schema-defined).
- `event_version`: schema/profile version marker.
- `event_sequence`: monotonic ordering marker within an event stream/partition.

Requirements:

- `event_id` must not be reused,
- `event_class` must be explicit even when `event_type` is specific,
- ordering metadata must permit deterministic replay within the declared stream scope.

## 2) Actor identity and execution context

Required fields:

- `actor_id`: stable actor identity (agent/service principal).
- `actor_type`: actor kind (`maintainer-agent`, `service-account`, or policy-equivalent bounded identities).
- `workspace_ref`: workspace/project scope where event occurred.
- `run_id`: maintainer run/operation correlation id.
- `tooling_context`: optional bounded identifier for maintainer build/profile/config in effect.

Requirements:

- actor identity must be attributable,
- actor identity must be resolvable to policy-bound authority scope,
- shared or anonymous actor values are non-conformant.

## 3) Time fields

Required fields:

- `occurred_at`: event occurrence timestamp.
- `recorded_at`: durable log append timestamp.
- `time_source`: declared time basis (`system-clock`, `external-clock`, or policy-equivalent).

Optional fields:

- `duration_ms`: execution duration where applicable.

Requirements:

- timestamps should be RFC 3339 / ISO 8601 compatible with timezone offset,
- `recorded_at` must be >= `occurred_at` unless documented queue buffering explains inversion,
- clock quality anomalies should be surfaced as explicit flags, not silently ignored.

## 4) Action and outcome fields

Required fields:

- `action_summary`: concise statement of what maintainer attempted.
- `outcome_status`: `success`, `partial`, `failed`, or policy-equivalent bounded set.
- `outcome_notes`: concise machine/human-inspectable outcome details.

Optional fields:

- `error_code`: bounded code for failures/partials.
- `retry_of_event_id`: reference when event is a retry/compensation attempt.

Requirements:

- partial/failed outcomes must preserve enough context for operational diagnosis,
- failures must still include affected-object linkage when determinable.

## 5) Affected-object trace fields

Required fields:

- `affected_objects`: explicit list of touched/impacted objects.

Required per affected object entry:

- `object_ref`: stable reference/path/id.
- `object_class`: `raw`, `structured`, `proposal`, `log`, or policy-equivalent class mapping.
- `relation`: relation to event (`read`, `created`, `updated-candidate`, `linked`, `flagged`, `no-change`, etc.).
- `impact_scope`: `canonical-impacting`, `non-canonical`, `diagnostic`, or policy-equivalent.

Requirements:

- object references must be resolvable to repository artifacts or stable ids,
- canonical-impacting intent must be explicit and must align with proposal/apply posture,
- wildcard-only affected-object declarations are non-conformant.

## 6) Related-artifact linkage fields

Required fields:

- `related_artifacts`: explicit links to relevant neighboring artifacts.

Allowed related artifact categories:

- `proposal_ref` (proposal artifact id/path)
- `raw_ref` (source object id/path)
- `structured_ref` (compiled object id/path)
- `log_ref` (other event ids / event stream positions)
- `policy_ref` (policy lane/exception basis when claimed)

Requirements:

- links must be directional and inspectable,
- proposal linkage must reference existing proposal artifacts when lifecycle events claim emission/update,
- policy exception claims without `policy_ref` are non-conformant.

## 7) Causality and trace continuity fields

Required fields:

- `correlation_id`: cross-event correlation id for a bounded operation.
- `caused_by`: zero or more predecessor event ids or external trigger ids.
- `follow_up_expected`: boolean or bounded enum indicating whether further maintainer action is expected.

Optional fields:

- `supersedes_event_id`: for compensating/superseding records.
- `trace_notes`: bounded human-readable continuity notes.

Requirements:

- causality should support chain reconstruction across seam boundaries,
- compensation/supersession must be append-expressed rather than history rewrite.

## Event-class-specific required extensions

In addition to the common minimum fields above, each class must include the following extensions.

### `ingest` extensions

Required:

- `source_registration`: stable source identity assignment details.
- `ingest_mode`: ingest mode/profile (batch/manual/automated policy-equivalent).
- `source_integrity_posture`: checksum/hash or integrity note where available.

### `compile` extensions

Required:

- `compile_scope`: bounded statement of compile target set.
- `compile_basis`: references to raw/structured basis used for compile decisions.
- `canonical_change_mode`: `proposal-emitted`, `direct-apply-exception`, or `no-canonical-change`.

### `lint_coherence` extensions

Required:

- `finding_summary`: concise summary of lint/coherence findings.
- `finding_severity`: bounded severity posture.
- `contradiction_signals`: explicit contradiction/uncertainty signal references when present.

### `proposal_lifecycle` extensions

Required:

- `proposal_action`: lifecycle action (`emitted`, `updated`, `superseded`, `review-linked`, `closed`, policy-equivalent).
- `proposal_refs`: one or more proposal artifact references.
- `review_handoff_posture`: whether event represents review request, reviewer response linkage, or closure linkage.

### `query_followup` extensions

Required:

- `query_context_ref`: stable pointer to query context/session artifact as allowed by policy.
- `discovered_gap_type`: gap category (`coverage`, `staleness`, `contradiction`, `provenance-missing`, policy-equivalent).
- `follow_up_artifact_refs`: proposals/tasks/log events emitted to address gap.

## Append-only and non-rewrite posture

Operational trace lanes must satisfy:

1. event creation is append-only,
2. historical entries are not silently modified in-place,
3. corrections use superseding/compensating append events,
4. deletion/redaction (if policy/legal required) is explicit, minimally scoped, and itself logged as an auditable event,
5. consumers must treat latest supersession chain as effective interpretation while retaining prior chain visibility for audit.

## Log vs canonical guardrails

To prevent `logs/` from becoming a second canonical lane:

1. log entries must not declare canonical fact acceptance by themselves,
2. any canonical-impacting intent in logs must reference proposal/apply governance artifacts,
3. structured consumers must not infer canonical state directly from operational event assertions alone,
4. proposal acceptance and apply outcomes remain distinct governed artifacts,
5. derived analytics over logs are observational and must not auto-promote to canonical structured truth without explicit governed path.

## Interpretation guidance for reconstruction and audit

Reviewer/operator reconstruction should proceed with this minimum sequence:

1. identify target operation scope using `correlation_id`, `run_id`, `workspace_ref`, and time window,
2. replay ordered events via `event_sequence` and `occurred_at`/`recorded_at`,
3. inspect `affected_objects` and `related_artifacts` for each step,
4. verify proposal-first posture for canonical-impacting actions,
5. verify contradiction/uncertainty surfacing where lint/query follow-up events indicate ambiguity,
6. verify append-only continuity (no hidden rewrites) and explicit supersession chains,
7. conclude operator judgment with explicit distinction between operational trace evidence and accepted canonical state.

## Slice 3 conformance checklist (bounded)

A maintainer log/event implementation profile is Slice 3-conformant when all are true:

1. required event classes exist and are mapped to the normative taxonomy,
2. all required common fields are present for each event,
3. class-specific extensions are present where class applies,
4. actor identity is attributable and non-anonymous,
5. timestamps and ordering support deterministic bounded replay,
6. affected objects are explicit and resolvable,
7. proposal/raw/structured/log/policy linkage is explicit where relevant,
8. append-only/supersession posture is enforced,
9. logs are prevented from acting as canonical acceptance lane,
10. canonical-impacting actions preserve proposal-first and policy-gated apply boundaries.

## Relationship to next slice

This Slice 3 contract establishes the event/log trace baseline consumed by:

- **Phase 8 Slice 4 — initial executable maintainer loop realization (bounded substitution path)**,

which should implement bounded executable behavior that emits events conforming to this profile without broadening authority scope.
