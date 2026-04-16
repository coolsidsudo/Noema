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
- Latest completed/accepted slice: Phase 5 Slice 15 maintainer baseline completion review and Phase 5 closure criteria declaration
- Current active slice: Phase 6 planning readiness and first bounded multi-user/auth/deployment baseline slice definition
- Next queued slice: Phase 6 Slice 1 bounded implementation slice (to be declared in-sequence)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 5 Slice 15: maintainer baseline completion review and Phase 5 closure criteria declaration**.

### Slice objective

Declare a bounded closure decision for Phase 5 by checking accepted maintainer baseline coverage against the original Phase 5 goals in `control/development-plan.md`, then move execution posture out of open-ended Phase 5 continuation.

### Slice deliverables

1. Record a concise Phase 5 completion review (goals, accepted baseline coverage, finish criteria).
2. Record an explicit closure judgment: either close Phase 5 now or identify exactly one final bounded gap.
3. Advance next-slice pointer toward Phase 6 if closure criteria are met.

### Slice done criteria

This slice is complete when:

- Phase 5 closure criteria are explicitly declared in control-layer docs (not implied).
- Phase 5 status is decided as closure-ready vs one-final-gap, with no open-ended continuation wording.
- Baseline architecture and accepted Phase 2/3/4 semantics remain preserved without drift.

### Slice 15 closure judgment

Phase 5 closure criteria are satisfied by the accepted Slices 1–14 maintainer baseline and Slice 15 control review.

**Decision:** Phase 5 complete after this slice; transition execution pointer to Phase 6 planning/readiness slices.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
