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

- Phase 1: repository skeleton
- Phase 2: core knowledge model
- Phase 3: human client baseline
- Phase 4: agent interface baseline
- Phase 5: maintainer workflow baseline
- Phase 6: multi-user/auth/deployment baseline

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

## Next implementation slice (immediate)

The next implementation slice should be **Phase 1: Repository skeleton**.

### Slice objective

Create a concrete repository structure and conventions that encode the baseline knowledge model without prematurely implementing full services.

### Slice deliverables

1. Add top-level directories for the four object classes:
   - raw
   - structured
   - proposals
   - logs
2. Add documentation for object conventions and minimal metadata expectations.
3. Add a minimal sample workspace layout demonstrating separation of:
   - domain
   - profile
   - workspace/project
   - visibility
   - authority
4. Add contributor guidance explaining how future slices should preserve the architecture baseline.

### Slice done criteria

This slice is complete when:

- A new contributor can see where each object class belongs.
- The repository structure reflects the architecture baseline vocabulary.
- The sample layout demonstrates axis separation without introducing extra architecture.
- No implementation detail contradicts the accepted baseline docs.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
