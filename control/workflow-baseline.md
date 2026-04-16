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
- Latest completed/accepted slice: Phase 6 Slice 2A authentication and identity provisioning baseline semantics
- Current active slice: Phase 6 Slice 2B self-hosted deployment and operations baseline semantics (under review)
- Next queued slice: Phase 6 follow-on selection after Slice 2B review (backup/restore operational guidance refinement or deployment hardening/profile guidance)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 6 Slice 2B: self-hosted deployment and operations baseline semantics (under review)**.

### Slice objective

Define the stable baseline semantics for self-hosted deployment posture and operational boundaries so accepted Slice 1 and Slice 2A semantics can operate coherently in real NAS/VPS-style environments.

### Slice deliverables

1. Stable system-definition document in `docs/` for self-hosted deployment and operations baseline semantics.
2. Explicit single-node-first and operator-controlled deployment posture with NAS/VPS practicality semantics.
3. Baseline component/access-path, backup/restore, and operational continuity/change-management semantics.
4. Clear responsibility boundaries, explicit deferrals, and next-slice pointer for post-2B follow-on work.

### Slice done criteria

This slice is complete when:

- Single-node-first, operator-controlled, NAS/VPS-practical deployment semantics are explicit in stable docs.
- Baseline environment-boundary and access-path posture is defined without collapsing accepted policy/auth semantics.
- Backup/restore and operational continuity/change-management semantics are defined at baseline depth.
- Deferred/non-goal boundaries remain explicit (no deployment scripts, no container specifics, no production hardening internals).

### Slice 2B review posture note

Phase 6 Slice 2B semantics are captured in `docs/noema-self-hosted-deployment-operations-baseline.md` and aligned with accepted Phase 6 Slice 1 and Slice 2A semantics without architecture drift.

**Review posture:** Phase 6 Slice 2B is the current implementation slice under review; next bounded continuation selection follows review and should prioritize either backup/restore operational guidance refinement or deployment hardening/profile guidance.


## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
