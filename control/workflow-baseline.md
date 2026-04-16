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
- Latest completed/accepted slice: Phase 6 Slice 2B self-hosted deployment and operations baseline semantics
- Current active slice: Phase 6 Slice 3 backup and restore operational guidance refinement baseline semantics (under review)
- Next queued slice: Phase 6 follow-on slice after Slice 3 review (deployment hardening/profile guidance or tightly justified equivalent)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice is **Phase 6 Slice 3: backup and restore operational guidance refinement baseline semantics (under review)**.

### Slice objective

Define the stable baseline semantics for backup and restore operational guidance so accepted Slice 1, Slice 2A, and Slice 2B semantics preserve continuity coherently in self-hosted NAS/VPS-practical environments.

### Slice deliverables

1. Stable system-definition document in `docs/` for backup and restore operational guidance baseline semantics.
2. Explicit backup coverage classes spanning knowledge artifacts and continuity-critical governance state.
3. Coherent restore semantics with full vs partial posture clarity and governance/history continuity expectations.
4. Verification/inspectability/portability posture and qualitative recovery-point/recovery-time guidance at baseline depth.
5. Explicit operator responsibilities, deferrals/non-goals, and next-slice pointer for deployment hardening/profile guidance.

### Slice done criteria

This slice is complete when:

- Backup scope semantics are explicit for knowledge artifacts, workspace/project continuity state, and policy/auth continuity state.
- Coherent restore semantics are explicit, including full vs partial restore posture and governance/history continuity expectations.
- Verification posture is explicit, including recoverability confidence plus inspectability/portability expectations.
- Recovery-point/recovery-time guidance remains qualitative, and deferred/non-goal boundaries remain explicit (no tooling implementation, no vendor snapshots, no detailed DR engineering, no production SRE targets).

### Slice 3 review posture note

Phase 6 Slice 3 semantics are captured in `docs/noema-backup-restore-operational-guidance-baseline.md` and aligned with accepted Phase 6 Slice 1, Slice 2A, and Slice 2B semantics without architecture drift.

**Review posture:** Phase 6 Slice 3 is the current implementation slice under review; next bounded continuation should focus on deployment hardening/profile guidance (or tightly justified equivalent follow-on).


## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
