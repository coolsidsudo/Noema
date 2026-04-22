# Noema Proposal Payload, Evidence, and Provenance Contract V0

## Purpose

This document defines the **Phase 8 Slice 2 proposal artifact contract baseline** for maintainer-emitted, canonical-impacting structured changes.

It makes proposal artifacts structurally consistent, evidence-linked, provenance-grounded, contradiction-aware, and review-ready while preserving accepted Slice 1 governance posture:

- proposal-first default for canonical-impacting structured edits,
- direct canonical apply as exceptional and policy-gated,
- explicit separation between proposal artifacts and accepted canonical state.

This document is a **contract/profile baseline** and bounded conformance target, not an executable runtime specification.

## Scope boundary for Slice 2

This slice defines:

1. minimum required proposal payload fields,
2. affected-object identification requirements,
3. rationale and intended-outcome requirements,
4. evidence/provenance linkage requirements,
5. contradiction/uncertainty signaling requirements,
6. acceptance-readiness criteria for narrow, attributable, auditable review.

This slice does **not** define full maintainer log/event schema (reserved for Phase 8 Slice 3) and does **not** define executable maintainer-loop runtime realization (reserved for Phase 8 Slice 4).

## Baseline references

This contract baseline is derived from and constrained by:

- `docs/noema-original-system-design.md` (Sections 7, 9, 10, 13)
- `control/development-plan.md` (Phase 8 objective and Slice 2 scope)
- `control/development-tracker.md` (live continuation context)
- `docs/noema-maintainer-agent-skill-management-schema-v0.md` (maintainer rules and lane posture)
- `docs/noema-maintainer-loop-contract-baseline-v0.md` (accepted Slice 1 seam/lane contract)
- `control/workflow-baseline.md` (traceable slice workflow expectations)

## Contract anchors

### Anchor A — Proposal artifact is candidate state, not canonical state

A proposal payload is a review-bounded candidate change request.

Required implications:

- proposal acceptance status must be explicit,
- proposal payload existence must never imply canonical apply,
- apply outcomes must remain separate from proposal payload declaration.

### Anchor B — Proposal-first posture for canonical-impacting structured edits

For maintainer-emitted canonical-impacting structured changes, proposals are the default lane.

Required implications:

- canonical-impacting edits require proposal artifacts unless explicit exception policy lane applies,
- direct canonical apply remains separately policy-gated and auditable.

### Anchor C — Evidence and provenance are mandatory for maintained claims

Proposal claims and change requests must be grounded in identifiable evidence and provenance posture.

Required implications:

- reviewer can inspect why change is requested,
- reviewer can inspect what the request is grounded in,
- unsupported claims are explicitly marked as uncertainty/hypothesis rather than silently treated as settled.

### Anchor D — Contradiction and uncertainty are first-class signals

Proposal payloads must preserve ambiguity where present.

Required implications:

- contradiction candidates are explicit,
- uncertainty levels are explicit,
- proposed canonical edits do not flatten unresolved ambiguity into overconfident truth assertions.

## Proposal artifact profile (normative minimum fields)

A conformant maintainer-emitted proposal artifact for canonical-impacting structured edits must include the following minimum fields.

## 1) Identity and lifecycle posture

Required fields:

- `proposal_id`: stable unique identifier for the proposal artifact.
- `proposal_version`: monotonic version/revision marker for proposal edits.
- `proposal_state`: lifecycle state (`draft`, `under-review`, `accepted`, `rejected`, `superseded`, or policy-equivalent states).
- `created_at`: proposal creation timestamp.
- `updated_at`: latest proposal update timestamp.
- `emitted_by`: maintainer actor identity (agent/service identity).

Requirements:

- lifecycle state must be explicit and machine/human readable,
- state transition history may be tracked outside this payload but current state must be present,
- `accepted` state in proposal artifact must not itself perform canonical apply.

## 2) Scope and affected-object declaration

Required fields:

- `change_scope`: concise statement of requested canonical-impacting scope.
- `affected_objects`: explicit list of target structured objects.
- `operation_type`: requested operation per object (`create`, `update`, `merge`, `split`, `deprecate`, or policy-equivalent).
- `impact_class`: declared impact severity/posture (`low`, `moderate`, `high`, or policy-equivalent).

Required per affected object entry:

- `object_ref`: stable identifier/path for target structured object.
- `object_kind`: object type/profile (e.g., concept page, entity page, timeline, procedure).
- `change_summary`: concise delta summary for that object.

Requirements:

- affected-object set must be explicit enough for bounded reviewer decision,
- proposal must not rely on implicit wildcard scope,
- each requested canonical-impacting object delta must be attributable to this proposal.

## 3) Rationale and intended outcome

Required fields:

- `rationale`: why this proposal is needed now.
- `problem_statement`: specific deficiency, inconsistency, contradiction, staleness, or coverage gap being addressed.
- `intended_outcome`: expected canonical-state outcome if accepted/applied.
- `non_goals`: explicit statements of what this proposal does not attempt to change.

Requirements:

- rationale must be concrete and reviewable, not generic,
- intended outcome must be specific enough to evaluate acceptance success,
- non-goals must prevent accidental scope creep at review time.

## 4) Evidence linkage

Required fields:

- `evidence_set`: list of evidence entries supporting requested change.
- `evidence_coverage`: statement of how evidence maps to requested object deltas.

Required per evidence entry:

- `evidence_id`: stable local identifier within proposal.
- `evidence_type`: source class (`raw`, `structured`, `proposal`, `external-recorded`, or policy-equivalent).
- `source_ref`: resolvable reference to underlying source artifact (path/id/URI according to repository conventions).
- `source_excerpt_or_locator`: bounded locator for inspection (section, heading, paragraph span, timestamp, or line-range pointer).
- `relevance_statement`: why this evidence supports this requested change.
- `supports_objects`: list of affected object refs supported by this evidence.

Requirements:

- every requested canonical-impacting object delta must be supported by one or more evidence entries,
- evidence mapping must allow reviewer inspection without hidden context,
- when evidence is absent or partial, proposal must explicitly mark uncertainty (not suppress it).

## 5) Provenance and support posture

Required fields:

- `provenance_basis`: summary of source/compile context used to derive the proposal.
- `claim_support_posture`: per-claim or per-delta support posture labels.
- `derivation_notes`: maintainer explanation of synthesis/derivation where direct quotation is insufficient.

Allowed support posture labels (minimum):

- `supported`: directly supported by linked evidence,
- `derived`: reasoned synthesis across multiple evidence items,
- `hypothesis`: plausible but not yet sufficiently supported,
- `needs-review`: currently under-supported and requires reviewer judgment.

Requirements:

- no maintained claim in proposal payload may be unlabeled for support posture,
- derived claims must describe derivation logic at reviewer-inspectable granularity,
- hypothesis/needs-review claims must be clearly separable from directly supported claims.

## 6) Contradiction and uncertainty signaling

Required fields:

- `contradiction_flags`: explicit contradiction candidates relevant to requested change.
- `uncertainty_flags`: explicit uncertainty declarations.
- `open_questions`: unresolved questions requiring reviewer decision or further evidence.

Required per contradiction/uncertainty entry:

- `signal_id`: stable local identifier.
- `signal_type`: `contradiction` or `uncertainty`.
- `description`: concise description of the issue.
- `related_evidence_ids`: evidence items associated with the signal.
- `resolution_posture`: requested handling (`defer`, `split-proposal`, `needs-human-judgment`, or policy-equivalent).

Requirements:

- contradictions must be surfaced, not silently reconciled,
- uncertainty must be explicit where evidence is incomplete or conflicting,
- proposals must not encode unresolved contradiction as settled canonical truth.

## 7) Review and decision framing

Required fields:

- `review_scope`: bounded reviewer decision scope.
- `acceptance_criteria`: explicit conditions that must hold for reviewer acceptance.
- `risk_notes`: identified risks of acceptance or rejection.
- `requested_decision`: explicit reviewer action requested (accept/reject/request-revision).

Requirements:

- reviewer decision target must be narrow and attributable,
- acceptance criteria must map to affected objects and intended outcome,
- proposal must expose risks and tradeoffs rather than hiding them in narrative.

## 8) Apply-boundary and authority posture

Required fields:

- `authority_posture`: declaration that proposal emission is request-only by default.
- `apply_mode`: `proposal-only` by default; any non-default mode requires explicit policy reference.
- `policy_basis_ref`: reference to policy lane when any exception posture is claimed.

Requirements:

- proposal artifact must not perform implicit canonical apply,
- exception claims must include explicit policy basis,
- absence of policy basis implies default proposal-only posture.

## Minimal canonical payload skeleton (illustrative)

The following structure is illustrative (profile baseline), not a mandated serialization format:

```yaml
proposal_id: "proposal-2026-..."
proposal_version: 1
proposal_state: "under-review"
created_at: "2026-04-22T00:00:00Z"
updated_at: "2026-04-22T00:00:00Z"
emitted_by: "maintainer-agent"

change_scope: "Update two structured concept pages for contradiction-aware chronology alignment"
affected_objects:
  - object_ref: "structured/concepts/example-a.md"
    object_kind: "concept-page"
    operation_type: "update"
    change_summary: "revise chronology assertions and add uncertainty markers"
impact_class: "moderate"

problem_statement: "Current assertions conflict with newly ingested source timeline"
rationale: "Preserve canonical coherence and provenance traceability"
intended_outcome: "Chronology claims become evidence-linked and contradiction-explicit"
non_goals:
  - "No change to workspace visibility policy"
  - "No change to auth/authority model"

evidence_set:
  - evidence_id: "ev-1"
    evidence_type: "raw"
    source_ref: "raw/imports/source-123.md"
    source_excerpt_or_locator: "Section 3.2"
    relevance_statement: "Contains updated timeline entry"
    supports_objects:
      - "structured/concepts/example-a.md"

evidence_coverage: "All requested object deltas mapped to ev-1..ev-n"

provenance_basis: "Derived from raw/imports/source-123.md + structured chronology index"
claim_support_posture:
  - claim_ref: "example-a:timeline-assertion-2"
    posture: "supported"
  - claim_ref: "example-a:timeline-assertion-3"
    posture: "needs-review"
derivation_notes:
  - "Assertion-3 combines two partially conflicting records"

contradiction_flags:
  - signal_id: "sig-1"
    signal_type: "contradiction"
    description: "Source A date disagrees with Source B date"
    related_evidence_ids: ["ev-2", "ev-3"]
    resolution_posture: "needs-human-judgment"
uncertainty_flags:
  - signal_id: "sig-2"
    signal_type: "uncertainty"
    description: "Secondary source reliability uncertain"
    related_evidence_ids: ["ev-4"]
    resolution_posture: "defer"
open_questions:
  - "Should chronology remain split by source lineage until additional evidence arrives?"

review_scope: "Only listed affected objects and claims"
acceptance_criteria:
  - "Each changed claim has evidence linkage"
  - "Contradictions remain explicit in proposed canonical text"
risk_notes:
  - "If accepted prematurely, unresolved chronology ambiguity may harden"
requested_decision: "request-revision"

authority_posture: "proposal artifact requests canonical change; it does not apply canonical change"
apply_mode: "proposal-only"
policy_basis_ref: null
```

## Acceptance-readiness criteria (normative)

A proposal artifact is acceptance-ready only when all conditions below are met.

1. **Identity completeness**: proposal identity, actor identity, timestamps, and lifecycle state are present.
2. **Bounded scope**: affected-object set is explicit, finite, and operation-typed.
3. **Rationale clarity**: problem statement and intended outcome are concrete and reviewable.
4. **Evidence completeness**: each requested object delta has inspectable evidence linkage.
5. **Provenance labeling**: each maintained claim/delta has explicit support posture.
6. **Contradiction visibility**: contradiction/uncertainty signals are explicit where relevant.
7. **Review narrowness**: acceptance criteria and requested decision are bounded and attributable.
8. **Authority integrity**: proposal-only posture is explicit unless policy-backed exception is declared.

Failure of any condition means proposal requires revision before review decision.

## Bounded validation checklist (Slice 2 conformance)

Use this checklist for maintainer proposal artifact inspection.

- **P1 — Required fields present**: minimum payload sections 1-8 are populated.
- **P2 — Object mapping integrity**: each affected object has operation type and change summary.
- **P3 — Evidence-to-delta mapping**: each requested delta is evidence-backed or explicitly marked uncertainty.
- **P4 — Provenance posture labeling**: each claim/delta has support posture label.
- **P5 — Contradiction discipline**: contradiction/uncertainty signals are explicit and linked.
- **P6 — Review boundedness**: review scope and acceptance criteria are narrow and auditable.
- **P7 — Proposal/canonical separation**: no field implies automatic canonical acceptance/apply.
- **P8 — Exception discipline**: any non-default apply claim carries explicit policy basis.

## Phase boundary and continuity statement

This slice intentionally defines proposal payload/profile contract only.

Deferred to next slices:

- **Phase 8 Slice 3**: maintainer log/event schema and operational trace contract.
- **Phase 8 Slice 4**: bounded executable maintainer loop realization conforming to accepted contracts.

## Drift-check statement

This slice does not:

- treat proposal artifacts as accepted canonical state,
- weaken proposal-first posture for canonical-impacting structured edits,
- weaken evidence/provenance requirements,
- broaden direct canonical apply beyond exceptional policy-gated posture,
- swallow Slice 3 log/event schema scope,
- swallow Slice 4 executable realization scope,
- recenter Noema around generic chat/RAG or generic multi-agent platform framing.

## Next-slice pointer

Direct continuation after Slice 2 remains:

- **Phase 8 Slice 3 — maintainer log/event schema and operational trace contract**.
