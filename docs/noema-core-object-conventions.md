# Noema Core Knowledge Object Conventions (Initial)

## Purpose

This document defines the first practical convention layer for Noema's four core knowledge object classes:

- raw
- structured
- proposals
- logs

It translates the architecture baseline into reusable repository conventions without introducing a production-grade schema yet.

## Baseline design intent

These conventions are intentionally lightweight:

- They define what belongs in each object class.
- They define minimum metadata and provenance expectations.
- They define baseline relationships between object classes.
- They avoid domain-specific or personal-only assumptions.

## Shared minimum metadata expectations

All object classes should include metadata as defined by the baseline profile:

- `docs/noema-object-metadata-profile-v0.md`

At minimum, each object includes these required fields:

- `id`
- `class`
- `created_at`
- `created_by`
- `workspace`
- `status`

Recommended and optional fields, plus normalization guidance, are defined in the profile document so future slices can extend metadata consistently without redefining baseline semantics.

## Object class conventions

### 1) Raw

**Meaning**

Raw objects preserve source-facing material and provenance anchors.

**Content that belongs here**

- imported source documents
- transcript captures
- source snapshots
- attachments and source exports

**Baseline handling expectations**

- Prefer immutable or append-protected behavior after ingest.
- Preserve original source content whenever possible.
- Include source provenance (`source_uri`, capture/import time, and capture actor when available).

**Baseline status values**

- `ingested`
- `superseded` (when a newer source snapshot replaces it)
- `archived`

### 2) Structured

**Meaning**

Structured objects are the curated, canonical knowledge artifacts used for ongoing human and agent understanding.

**Content that belongs here**

- summaries
- entity or concept pages
- procedures
- timelines
- decision records
- relationship/index artifacts

**Baseline handling expectations**

- Must reference supporting raw object IDs where claims originate.
- Should remain diff-friendly and reviewable.
- Represents canonical knowledge after acceptance/review.

**Baseline status values**

- `draft`
- `active`
- `deprecated`
- `archived`

### 3) Proposals

**Meaning**

Proposal objects are non-canonical candidate changes to raw/structured conventions or content.

**Content that belongs here**

- proposed creation of structured artifacts
- proposed edits to existing structured artifacts
- reclassification requests
- contradiction/consistency review submissions

**Baseline handling expectations**

- Must include proposer identity and target object reference(s).
- Must include rationale and intended effect.
- Must keep review state explicit.

**Baseline status values**

- `draft`
- `under_review`
- `accepted`
- `rejected`
- `withdrawn`

### 4) Logs

**Meaning**

Log objects are append-oriented records of system and workflow events.

**Content that belongs here**

- ingest events
- proposal review decisions
- maintenance/compiler run records
- sync and operational history
- policy-relevant audit events

**Baseline handling expectations**

- Prefer append-only event records.
- Every entry should include timestamp, actor identity, and event type.
- Logs are operational history, not canonical structured knowledge pages.

**Baseline status values**

- `recorded`
- `corrected` (for explicit correction entries)

## Baseline relationship conventions

At minimum, object classes should link as follows:

1. **Structured -> Raw**: structured knowledge cites supporting raw provenance.
2. **Proposals -> Structured and/or Raw**: proposals declare affected target objects.
3. **Logs -> Any class**: logs record lifecycle and workflow events for raw, structured, and proposal objects.
4. **Accepted proposal -> Structured update**: accepted proposals should resolve to new or updated structured objects, with log entries for traceability.

This creates a minimal traceability chain:

`raw evidence -> structured knowledge -> proposed changes -> logged decisions/events`

## Repository mapping

The top-level repository directories map directly to these classes:

- `raw/`
- `structured/`
- `proposals/`
- `logs/`

Each directory README should remain aligned with this convention document.

## Out of scope for this slice

This document does not define:

- final production schemas
- storage engine requirements
- full policy/auth implementation
- domain-specific taxonomy packs

Those are intentionally deferred to later slices.
