# Noema Workflow Baseline Adoption

## Purpose

This document adopts the accepted architecture baseline into the active project workflow.
It is the execution bridge between:

- `docs/noema-original-system-design.md` (architecture source of truth)
- `docs/noema-development-plan.md` (phase sequencing source of truth)

## Architecture source of truth (authoritative)

The current architecture source of truth is:

1. `docs/noema-original-system-design.md`
2. `docs/noema-development-plan.md`
3. `README.md` (project-facing summary aligned to the two docs above)

If implementation details conflict with these documents, implementation must be updated to match the baseline unless the baseline is intentionally revised through an explicit architecture change.

## Workflow translation: architecture -> execution

Use the following execution language for all near-term implementation work.

### Rule 1: Preserve architectural invariants

Every implementation PR should explicitly preserve these invariants:

- Open-source, reusable project framing
- Self-hosted operation (NAS/VPS practical)
- Multi-human and multi-agent support assumptions
- Obsidian-compatible, but not Obsidian-dependent
- Editor-agnostic platform identity
- Independent policy/organization axes:
  - domain
  - profile
  - workspace/project
  - content type
  - visibility
  - authority

### Rule 2: Avoid architecture drift

Do not introduce implementation shortcuts that collapse independent axes. In particular:

- Do not treat profile as domain
- Do not treat visibility as authority
- Do not treat an Obsidian vault as the authority layer
- Do not treat raw content and compiled structured knowledge as interchangeable

### Rule 3: Work in phase-consistent slices

Implementation should progress in development-plan order unless a documented dependency requires otherwise:

- Completed and accepted: Phase 1 repository skeleton
- Completed and accepted: initial Phase 2 core knowledge object convention layer
- Current active slice: Phase 2 follow-on definition work (metadata, relationship, and indexing conventions)
- Next queued slices: Phase 3 human client baseline, Phase 4 agent interface baseline, Phase 5 maintainer workflow baseline, Phase 6 multi-user/auth/deployment baseline

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Next implementation slice (immediate)

The next implementation slice remains in **Phase 2: Core knowledge model follow-on definition work**.

### Slice objective

Refine the initial Phase 2 convention layer with clearer metadata, relationship, and indexing definitions while preserving the accepted baseline model.

### Slice deliverables

1. Clarify required and optional metadata expectations for core object classes.
2. Define tighter relationship/link conventions between raw, structured, proposals, and logs.
3. Define baseline index/catalog expectations for navigation and traceability.
4. Keep this work documentation-first and traceable to baseline docs.

### Slice done criteria

This slice is complete when:

- Core object conventions include clearer metadata and relationship definitions for consistent use.
- Baseline index/catalog expectations are documented for implementation follow-through.
- The Phase 2 convention layer stays aligned with architecture and workflow baselines.
- The next-slice pointer after this work clearly targets Phase 3 (human client baseline).

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
