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
- Current active slice: Phase 6 Slice 1 baseline multi-user access and authority model semantics
- Next queued slice: Phase 6 Slice 2A or 2B (bounded follow-on after Slice 1 acceptance)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 6 Slice 1: baseline multi-user access and authority model semantics**.

### Slice objective

Define the stable baseline semantics of who can see what, who can change what, and how those differ in Noema before deeper authentication/deployment internals are specified.

### Slice deliverables

1. Stable system-definition document in `docs/` for access/authority baseline semantics.
2. Explicit visibility and authority separation semantics at workspace/object policy layers.
3. Baseline human and agent role-family semantics with machine auditability expectations.
4. Control-layer progression updates and next-slice pointer for Phase 6 continuation.

### Slice done criteria

This slice is complete when:

- Access vs authority separation is explicit and preserved in stable docs.
- Multi-human and multi-agent baseline participation semantics are coherent.
- Workspace defaults and object-level policy refinement semantics are defined at baseline depth.
- Deferred/non-goal boundaries are explicit (no auth internals, no deployment hardening internals).

### Slice 1 review posture note

Phase 6 Slice 1 semantics are captured in `docs/noema-access-authority-baseline.md` and aligned with accepted Phase 3/4 baselines without architecture drift.

**Review posture:** Phase 6 Slice 1 remains the current implementation slice under review; Phase 6 Slice 2 remains queued as the bounded follow-on (auth/identity provisioning semantics baseline or deployment/operations baseline) after Slice 1 acceptance.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
