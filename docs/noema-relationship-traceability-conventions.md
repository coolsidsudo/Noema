# Noema Baseline Relationship and Traceability Conventions

## Purpose

This document defines a lightweight, reusable baseline for how Noema core object classes should refer to one another during Phase 2 convention work.

It clarifies cross-object traceability without introducing a full graph model, database schema, or implementation-specific storage strategy.

## Scope and guardrails

This convention layer is intentionally limited.

It should:

- define baseline link expectations between raw, structured, proposals, and logs
- clarify what baseline traceability means in Noema terms
- define accepted proposal to structured update expectations
- define lifecycle and review logging linkage expectations

It should not:

- define a production graph or ontology system
- require bidirectional materialization in every storage backend
- prescribe a specific database, index engine, or event bus
- collapse object-class boundaries established in architecture baseline docs

## Core relationship primitives (baseline level)

Use these generic relationship primitives at the convention layer:

- `supports` — evidence/provenance support for a claim or structured artifact
- `targets` — object(s) a proposal intends to create, modify, reclassify, or deprecate
- `results_in` — object(s) created/updated when a proposal is accepted and applied
- `records_event_for` — object(s) a log entry describes
- `supersedes` — newer object version or replacement lineage at object level

These are semantic conventions, not required implementation fields. Repositories can encode them in frontmatter, sidecars, indexes, or service-managed metadata while preserving the same meaning.

## Class-to-class baseline link expectations

### 1) Structured -> Raw (`supports`)

Structured objects should reference one or more raw objects that support important claims, summaries, interpretations, or extracted facts.

Baseline expectation:

- every non-trivial structured artifact has at least one supporting raw reference unless explicitly marked synthesis-only
- supporting references should be stable object IDs, not only filenames

### 2) Proposals -> Structured and/or Raw (`targets`)

Every proposal should declare the object(s) it affects.

Baseline expectation:

- proposals that edit existing knowledge target the current structured object ID(s)
- proposals that introduce new structured artifacts target intended destination path/class plus any source raw IDs used to justify the change
- reclassification or provenance corrections may target raw and structured IDs together

### 3) Accepted proposal -> Structured (`results_in` + `supersedes`)

Accepted proposals should map to concrete structured outcomes.

Baseline expectation:

- acceptance alone is not the end state; it should resolve to an applied structured create/update event
- when a structured object is replaced, lineage should be explicit via `supersedes` (or equivalent version lineage metadata)
- if acceptance is partial, the resulting structured updates should identify the exact subset applied

### 4) Logs -> Any class (`records_event_for`)

Logs should attach operational history to the objects they concern.

Baseline expectation:

- ingest logs record events for raw object IDs
- review logs record events for proposal IDs and decision actors
- apply/publish logs record events for resulting structured object IDs
- correction logs reference the corrected log entry and impacted object IDs

## Baseline traceability definition

In this phase, an object is considered **traceable** when a reviewer can follow a bounded chain of references that answers all of the following:

1. **Source basis**: what raw object(s) support this structured knowledge?
2. **Change intent**: what proposal introduced or requested this change?
3. **Decision context**: who reviewed/accepted/rejected it and when?
4. **Applied outcome**: what structured object state resulted?
5. **Operational history**: what lifecycle events were recorded for these objects?

This is a practical audit chain, not a requirement for exhaustive global graph traversal.

## Minimum chain patterns

### Canonical happy path

`raw --supports--> structured(draft/active)`

`proposal --targets--> structured`

`log(review_decision) --records_event_for--> proposal`

`proposal(accepted) --results_in--> structured(updated)`

`log(apply_update) --records_event_for--> structured(updated)`

### New artifact from raw

`raw --supports--> proposal(new structured artifact)`

`proposal(accepted) --results_in--> structured(new)`

`log(acceptance/apply) --records_event_for--> proposal + structured(new)`

### Rejection path

`proposal --targets--> structured`

`log(review_rejection) --records_event_for--> proposal (+ optional target structured)`

Rejected proposals do not create `results_in` links to new canonical structured state.

## Lifecycle and review logging expectations

Log entries should make review and lifecycle transitions reconstructable.

At baseline, record at least:

- event type (ingest, propose, review_accept, review_reject, apply_update, correct_log, archive, etc.)
- event timestamp
- actor identity
- referenced object IDs (`records_event_for` set)
- optional reason/notes for review or correction decisions

Logs remain append-oriented; corrections should be additive events, not destructive history edits.

## Relationship consistency checks (convention-level)

Future implementation may automate this, but baseline conventions should assume these checks:

- active structured objects have at least one supporting raw link (unless explicitly exempt)
- non-draft proposals declare at least one target
- accepted proposals have at least one resulting structured reference
- review decision logs exist for terminal proposal states (`accepted`, `rejected`, `withdrawn` where policy requires)
- apply/update logs exist when accepted proposals are materialized

## Deferred complexity (intentional)

The following relationship complexity is intentionally deferred:

- global graph query language and traversal APIs
- transitive inference and automatic link recovery
- cross-workspace federation of relationship graphs
- conflict-free replicated relationship state across distributed nodes
- domain-specific relationship taxonomies
- full provenance confidence scoring models

These can be layered later without changing the baseline semantics defined here.

## Alignment with existing Noema docs

This document extends, and does not replace:

- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-workflow-baseline.md`

Use this as the relationship and traceability companion for the initial core object convention layer.
