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
- Current active slice: Phase 3 human client baseline
- Next queued slice: Phase 4 agent interface baseline

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Current implementation slice (immediate)

The current implementation slice remains **Phase 3: Human client baseline**.

### Slice objective

Deliver the first practical human-facing usage layer while preserving the accepted baseline architecture and completed Phase 2 semantics.

### Slice deliverables

1. Define an Obsidian-compatible baseline workspace view for human users without making Obsidian the authority layer.
2. Establish baseline human browse/review flows over structured, proposal, and traceability-linked content.
3. Document owner/reviewer/reader workflow guidance that aligns with baseline policy boundaries.
4. Keep this work implementation-light, documentation-first, and traceable to baseline docs.

### Slice done criteria

This slice is complete when:

- Human-facing baseline guidance exists for workspace browsing/review while preserving editor-agnostic identity.
- Obsidian compatibility is explicitly supported without treating Obsidian as the authority layer.
- Human role workflows (owner/reviewer/reader) are documented at baseline depth.
- The next-slice pointer after this work clearly targets Phase 4 (agent interface baseline).

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
