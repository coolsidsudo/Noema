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
- Latest completed/accepted slice: Phase 6 Slice 5 implementation-constrained hardening conformance/validation guidance baseline semantics
- Current active slice: Phase 6 Slice 6 conformance evidence interoperability refinement scoping (under review)
- Next queued slice: Phase 6 next substantive slice after Slice 6 scoping closure (to be explicitly scoped)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 6 Slice 6: conformance evidence interoperability refinement scoping (under review)**.

### Slice objective

Define the bounded follow-on scope for conformance evidence interoperability refinement so accepted Slice 5 conformance/validation semantics can be adopted in implementation-facing workflows without changing accepted baseline semantics.

### Slice deliverables

1. Control-state scoping note for Slice 6 follow-on objective and boundary posture.
2. Explicit continuity anchoring to accepted Slice 5 conformance/validation guidance semantics.
3. Next-slice pointer coherence without prematurely claiming acceptance-close for Slice 6.

### Slice done criteria

This slice is complete when:

- Slice 5 remains recorded as accepted and unchanged in docs semantics.
- Slice 6 follow-on scope is explicitly marked as under-review scoping (not accepted).
- Control-state continuity and next-pointer language remain coherent with accepted flow.

### Slice 5 acceptance continuity posture note

Accepted Phase 6 Slice 5 semantics are captured in `docs/noema-hardening-conformance-validation-guidance-baseline.md` and provide the direct semantic prerequisite for current Slice 6 follow-on scoping work.

**Review posture:** Phase 6 Slice 6 follow-on scoping is the current implementation slice under review; acceptance-close state updates remain deferred until explicit review closure.


## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
