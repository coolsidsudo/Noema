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
- Latest completed/accepted slice: Phase 4 Slice 6 apply/recovery policy-profile refinement interoperability baseline
- Current active slice: Phase 4 interoperability consistency verification and profile-compatibility conformance guidance across implementations
- Next queued slice: Phase 4 next bounded slice after current conformance-guidance slice closure (to be declared in-sequence)
- Phase 5 queue status: queued after remaining Phase 4 baseline closure

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 4: interoperability consistency verification and profile-compatibility conformance guidance across implementations**.

### Slice objective

Define bounded interoperability consistency and conformance guidance for accepted Slice 6 policy-profile semantics while preserving accepted baseline semantics.

### Slice deliverables

1. Define interoperability consistency checks for apply/recovery policy-profile interpretation.
2. Define profile-compatibility conformance guidance across implementations for accepted Slice 6 semantics.
3. Keep this work implementation-light, documentation-first, and traceable to baseline docs.

### Slice done criteria

This slice is complete when:

- Interoperability consistency expectations for accepted Slice 6 semantics are explicit and bounded.
- Profile-compatibility conformance guidance across implementations is explicit and machine-interpretation-friendly.
- Accepted Slice 1/2/3/4/5/6 semantics remain preserved rather than redefined.
- Canonical publication remains separated from agent proposal/review support authority.
- The next-slice pointer remains inside Phase 4 unless baseline closure is explicitly declared.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
