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
- Latest completed/accepted slice: Phase 7 Slice 2 reference-package conformance checks and executable runtime substitution planning
- Current active slice: none (no under-review slice currently opened)
- Next queued slice: Phase 7 Slice 3 first executable runtime substitution increment (recommended: bounded machine-facing facade) with matching conformance-check expansion (queued/proposed)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

There is **no currently opened under-review slice** at this moment; Phase 7 Slice 2 is accepted/completed and Phase 7 Slice 3 remains queued/proposed pending explicit open.

### Slice objective

Keep control-state synchronized to the accepted Phase 7 Slice 2 outcome without opening a new under-review slice by default.

### Slice deliverables

1. Record Phase 7 Slice 2 as latest completed/accepted slice in control-state.
2. Remove stale under-review wording for Phase 7 Slice 2 from active-slice status lines.
3. Keep Phase 7 Slice 3 as queued/proposed only unless explicitly opened in a later patch.

### Slice done criteria

This slice is complete when:

- Phase 7 Slice 2 is recorded as accepted in control-state.
- Control-state no longer claims Phase 7 Slice 2 is under review.
- Next-pointer language remains coherent: Phase 7 Slice 3 is queued/proposed and not yet opened.

### Continuity note

Accepted Phase 6 deployment and backup/restore semantics remain authoritative in:

- `docs/noema-self-hosted-deployment-operations-baseline.md`
- `docs/noema-backup-restore-operational-guidance-baseline.md`

Accepted Phase 7 Slice 2 package checks and substitution-planning assets remain in `deploy/reference-single-node/`; this patch only synchronizes control-state and does not modify deployment assets.

**Review posture:** No new under-review slice is opened by this patch; Phase 7 Slice 3 remains queued/proposed until explicitly started.


## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
