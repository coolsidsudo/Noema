# Control Layer Documentation

This directory contains repository **development/control artifacts** for building Noema.

These files are **not part of the Noema system definition**. They are temporary project workflow documents that help contributors coordinate implementation work in this repository.

## Boundary

- **How Noema works** (system/product definition): `docs/`
- **How we build Noema** (repository execution workflow): `control/`

Repository execution in this control layer uses a full loop with explicit in-flight vs landed-state review authority:

1. Delegate from the Linear issue to Codex to start work.
2. Continue follow-ups in the live in-issue Codex box in Linear.
3. Before PR creation/merge/landed-state verification, use Codex live in-issue output as the primary in-flight review surface; GitHub may be stale in this phase.
4. Declare any full changed-file content or special proof-artifact requirements up front in the Linear issue description and Codex execution note.
5. When higher-level review accepts a slice, first provide paste-ready reviewer-acceptance text for the Codex live in-issue box (unless a no-Codex-acknowledgement exception is explicitly stated).
6. After providing that acceptance text, give explicit operator next-step guidance (create PR now, merge now, or run a required acceptance-close sync first if applicable).
7. Use GitHub repository state as authoritative again for landed-state review, merge verification, and acceptance-close verification.
8. End acceptance-close review with explicit remaining operator step guidance, including merge/close/mark-Done actions where applicable.
9. Allow manual human PR landing when Codex cannot push/land automatically.
10. Mark the Linear issue **Done** only as the final move after substantive and acceptance-close merged state is reflected.

Commit/PR evidence should be provided first when reporting completion so reviewers can verify repository state directly.

## Stability expectations

Control-layer documents may be updated, replaced, reorganized, or removed as implementation needs evolve.

Those changes do **not** change Noema's architecture or system semantics unless corresponding system-definition documents in `docs/` are intentionally revised.

## Current control artifacts

- `development-plan.md`
- `workflow-baseline.md`
- `phase-7-slice-1-reference-deployment-package.md`
