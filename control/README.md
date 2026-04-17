# Control Layer Documentation

This directory contains repository **development/control artifacts** for building Noema.

These files are **not part of the Noema system definition**. They are temporary project workflow documents that help contributors coordinate implementation work in this repository.

## Boundary

- **How Noema works** (system/product definition): `docs/`
- **How we build Noema** (repository execution workflow): `control/`

Repository execution in this control layer uses a full loop:

1. Delegate from the Linear issue to Codex to start work.
2. Continue follow-ups in the live in-issue Codex box in Linear.
3. Use GitHub repository state as the authoritative review/acceptance surface.
4. Allow manual human PR landing when Codex cannot push/land automatically.
5. Mark the Linear issue **Done** after merge.

Commit/PR evidence should be provided first when reporting completion so reviewers can verify repository state directly.

## Stability expectations

Control-layer documents may be updated, replaced, reorganized, or removed as implementation needs evolve.

Those changes do **not** change Noema's architecture or system semantics unless corresponding system-definition documents in `docs/` are intentionally revised.

## Current control artifacts

- `development-plan.md`
- `workflow-baseline.md`
- `phase-7-slice-1-reference-deployment-package.md`
