# Noema Baseline Index/Catalog Approach

## Purpose

This document defines the first lightweight index/catalog approach for Noema knowledge objects during the early file-friendly implementation stage.

It explains what the index/catalog means in Noema terms, what it is responsible for now, how discoverability works at baseline, and what advanced indexing work is intentionally deferred.

## What "index/catalog" means in Noema

In Noema, the baseline index/catalog is a discoverability layer over existing knowledge objects. It is not a new object class and not a replacement for raw/structured/proposals/logs.

At baseline, the index/catalog is:

- a navigable listing of known objects in a workspace
- driven by stable object metadata and class conventions
- usable by both human-facing tools and bounded machine interfaces
- implementation-flexible (frontmatter extraction, sidecar scanning, generated manifest files, or equivalent)

The index/catalog should make objects easy to find and traverse before a dedicated backend or full-text search subsystem exists.

## Baseline responsibilities

The baseline index/catalog is responsible for:

1. **Object discoverability**
   - Make objects findable by core metadata (for example: `id`, `class`, `workspace`, `status`, `title`, `tags`).
2. **Navigation support**
   - Provide a consistent way to browse by object class and workspace.
3. **Traceability entry points**
   - Expose minimum linkage cues so users/agents can follow provenance and lifecycle chains (for example, references to supporting raw IDs, proposal targets, and logged events).
4. **Portable operation**
   - Work with file-based repositories and simple generation/update workflows.
5. **Baseline consistency checks**
   - Support convention-level checks such as missing required metadata or invalid class/status combinations.

The baseline index/catalog is **not** responsible for deep ranking, semantic retrieval, inference, or autonomous data repair.

## Baseline discoverability model

At this stage, an object is considered discoverable when all of the following are true:

1. It exists in the expected repository class location (`raw/`, `structured/`, `proposals/`, or `logs/`).
2. It includes required baseline metadata fields.
3. Its metadata can be collected by a deterministic file-friendly process.
4. It appears in a catalog view or generated index artifact for its workspace.

### Practical baseline browse paths

The index/catalog should support at least these browse patterns:

- by `workspace`
- by `class`
- by `status`
- by recent update/create timestamps (`updated_at` or `created_at`)
- by lightweight topical cues (`title`, `summary`, `tags` when present)

### Minimum retrieval expectation

Given a known `id` (or `title` + `workspace` pair), a human or agent should be able to:

- find the object record,
- identify its class and status,
- and locate direct traceability pointers relevant at baseline.

## Minimum metadata dependencies

The baseline index/catalog depends on metadata defined in:

- `docs/noema-object-metadata-profile-v0.md`

### Required dependencies

These fields are required for inclusion as first-class catalog records:

- `id`
- `class`
- `created_at`
- `created_by`
- `workspace`
- `status`

Objects missing required fields may remain in storage but should be treated as catalog validation failures until corrected.

### Strongly recommended dependencies

These fields materially improve discoverability and should be included whenever available:

- `title`
- `updated_at`
- `updated_by`
- `summary`
- `tags`

### Relationship-aware optional dependencies

Where available, the following optional fields improve traceability-oriented navigation:

- `target_ids`
- `source_uri`
- `source_captured_at`
- `event_type`

## File-based baseline implementation posture

To stay architecture-aligned and early-stage, the index/catalog may remain file/convention-based for now.

Examples of acceptable baseline implementations:

- periodic metadata scan that generates per-workspace index manifests (for example, Markdown or JSON)
- class-level directory indexes maintained by convention
- simple machine-readable catalog artifacts committed to the repository
- lightweight CLI/scripts that rebuild catalog artifacts from object metadata

Any option is acceptable if it preserves semantics and keeps discoverability deterministic, inspectable, and portable.

## Deferred indexing complexity (intentional)

The following are intentionally deferred to later slices:

- full-text search engine design and ranking strategies
- vector/embedding retrieval architecture
- distributed index synchronization and federation
- query language design beyond baseline filtering/browsing
- relevance tuning, personalization, and recommendation logic
- advanced faceting over domain-specific ontologies/taxonomies
- real-time event-driven indexing pipelines

Deferring these decisions keeps Phase 2 focused on consistent object conventions and portable discoverability.

## Alignment with existing baseline docs

This index/catalog approach extends and aligns with:

- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `control/workflow-baseline.md`

It does not replace those documents and should be interpreted as the discoverability companion to the initial Phase 2 convention layer.

## Next-slice pointer

With this baseline in place, the next execution slice remains Phase 3 (human client baseline), where catalog visibility can be projected into first practical human browsing/review experiences without changing core semantics.
