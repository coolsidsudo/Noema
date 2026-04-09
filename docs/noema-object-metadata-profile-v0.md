# Noema Baseline Object Metadata Profile (v0)

## Purpose

This document defines the first reusable metadata profile for Noema knowledge objects.
It clarifies baseline metadata expectations across the four core object classes:

- raw
- structured
- proposals
- logs

This profile is intentionally foundation-oriented. It is designed to support consistency and traceability now, while leaving room for future schema hardening.

## Scope and positioning

This profile applies to all baseline Noema knowledge objects whether metadata is represented in Markdown frontmatter, sidecar files, or another equivalent object metadata record.

This profile does **not** require a specific storage engine, serialization format, or validation implementation.

## Baseline field tiers

### Required (all object classes)

These fields are required for every object at baseline:

- `id`
- `class`
- `created_at`
- `created_by`
- `workspace`
- `status`

### Recommended (all object classes)

These fields are recommended for stronger traceability and lifecycle handling:

- `title`
- `updated_at`
- `updated_by`
- `summary`
- `tags`

### Optional (class- or workflow-dependent)

These fields are optional and may appear when relevant:

- `source_uri` (most common on raw)
- `source_captured_at` (most common on raw)
- `target_ids` (most common on proposals)
- `event_type` (most common on logs)

Future slices may expand this set.

## Baseline field definitions and normalization

### `id` (required)

- Meaning: Stable object identifier.
- Type: string.
- Normalization:
  - Must be unique within a workspace.
  - Use lowercase kebab-case by default.
  - Must not be reused for a different object.

Examples:

- `raw-2026-04-09-market-report-01`
- `structured-compound-interest-overview`

### `class` (required)

- Meaning: Object class for the record.
- Type: string enum.
- Allowed values:
  - `raw`
  - `structured`
  - `proposals`
  - `logs`
- Normalization:
  - Must exactly match one of the baseline class tokens above.

### `created_at` (required)

- Meaning: Object creation timestamp.
- Type: timestamp string.
- Normalization:
  - Must use ISO 8601 format.
  - Must include timezone information (`Z` or explicit UTC offset).

Example:

- `2026-04-09T13:30:00Z`

### `created_by` (required)

- Meaning: Identity that created the object (human or agent).
- Type: string.
- Normalization:
  - Should be stable and attributable.
  - Use consistent namespace prefixes when useful (for example `human:` and `agent:`).

Examples:

- `human:alex-reviewer`
- `agent:noema-curator`

### `workspace` (required)

- Meaning: Workspace/project identifier where the object belongs.
- Type: string.
- Normalization:
  - Must match the canonical workspace identifier used by the repository or service layer.
  - Use lowercase kebab-case by default.

### `status` (required)

- Meaning: Lifecycle state for the object.
- Type: string enum (class-specific).
- Normalization:
  - Must use values valid for the object's `class`.
  - Status transitions are workflow-controlled and intentionally not fully specified in this slice.

## Baseline class-specific status sets

The `status` field is required for all classes and should use the following baseline sets:

### raw

- `ingested`
- `superseded`
- `archived`

### structured

- `draft`
- `active`
- `deprecated`
- `archived`

### proposals

- `draft`
- `under_review`
- `accepted`
- `rejected`
- `withdrawn`

### logs

- `recorded`
- `corrected`

## Baseline guidance for recommended fields

### `title` (recommended)

Short human-readable name for quick scanning and review.

### `updated_at` and `updated_by` (recommended)

Track latest modification time and actor identity for non-immutable objects.

### `summary` (recommended)

One- to three-sentence description of object intent or contents.

### `tags` (recommended)

List of lightweight categorization labels for indexing and navigation. Prefer lowercase kebab-case tags.

## Baseline guidance for optional fields

### `source_uri` and `source_captured_at`

Use when retaining source provenance for raw inputs or structured claims derived from external material.

### `target_ids`

Use on proposals to enumerate affected raw/structured/proposal objects.

### `event_type`

Use on logs to normalize event categories (for example `ingest`, `review_decision`, `sync`).

## Cross-class normalization rules (baseline)

- Use UTC timestamps where possible for consistency across contributors and systems.
- Use lowercase kebab-case for identifiers and tags unless external constraints require otherwise.
- Treat missing required fields as invalid baseline metadata.
- Keep metadata portable: field semantics should remain consistent regardless of file layout or storage backend.

## Intentionally out of scope

This profile intentionally does **not** define:

- Full production JSON Schema (or equivalent formal schema).
- Strongly enforced global ID registry across all deployments.
- Full lifecycle transition graphs and approval state machines.
- Storage engine implementation details.
- Authentication/authorization policy models.
- Domain-specific metadata packs.

These are deferred to later slices.

## Relationship to existing convention documents

This profile is the baseline metadata layer for:

- `docs/noema-core-object-conventions.md`
- class directory conventions under `raw/`, `structured/`, `proposals/`, and `logs/`

Future relationship and indexing slices should build on this profile rather than redefining field meanings.
