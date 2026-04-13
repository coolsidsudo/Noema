# Noema Workflow Baseline Adoption

## Purpose

This document adopts the accepted architecture baseline into the active project workflow.
It is the execution bridge between:

- `docs/noema-original-system-design.md` (architecture source of truth)
- `control/development-plan.md` (phase sequencing source of truth)

## Architecture source of truth (authoritative)

The current architecture source of truth is:

1. `docs/noema-original-system-design.md`
2. `control/development-plan.md`
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

- Completed and accepted: Phase 0 architecture baseline
- Completed and accepted: Phase 1 repository skeleton
- Completed and accepted: Phase 2 definition package (core object conventions, metadata profile, relationship/traceability conventions, and index/catalog baseline)
- Latest completed/accepted slice: Phase 4 interoperability consistency verification and profile-compatibility conformance guidance across implementations
- Current active slice: Phase 5 first bounded maintainer workflow implementation slice (to be declared in-sequence)
- Next queued slice: Phase 5 next bounded slice after first maintainer workflow slice closure (to be declared in-sequence)
- Phase 5 queue status: in progress (first bounded maintainer workflow slice to be declared in-sequence)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 5: first bounded maintainer workflow implementation slice (to be declared in-sequence)**.

### Slice objective

Start Phase 5 with a bounded maintainer workflow baseline implementation slice while preserving accepted architecture and prior phase semantics.

### Slice deliverables

1. Declare and execute the first bounded Phase 5 maintainer workflow slice in sequence.
2. Keep implementation scope minimal, traceable, and aligned to baseline documents.

### Slice done criteria

This slice is complete when:

- The first bounded Phase 5 maintainer workflow slice is explicitly declared and completed in sequence.
- Baseline architecture and accepted Phase 2/3/4 semantics remain preserved without drift.
- The next-slice pointer advances to the next bounded Phase 5 slice.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
