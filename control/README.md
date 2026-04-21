# Control Layer Documentation

This directory contains repository **development/control artifacts** for building Noema.

These files are **not part of the Noema system definition**. They are temporary project workflow documents that help contributors coordinate implementation work in this repository.

## Boundary

- **How Noema works** (system/product definition): `docs/`
- **How we build Noema** (repository execution workflow): `control/`

Within `control/`, authority is intentionally separated:

- `development-plan.md` = long-horizon roadmap (stable)
- `development-tracker.md` = live execution tracker (mutable)
- `workflow-baseline.md` = workflow rules and review/governance process

Repository execution in this control layer uses a full loop with explicit in-flight vs landed-state review authority:

1. Delegate from the Linear issue to Codex to start work.
2. Continue follow-ups in the live in-issue Codex box in Linear.
3. Before PR creation/merge/landed-state verification, use Codex live in-issue output as the primary in-flight review surface; GitHub may be stale in this phase.
4. Declare any full changed-file content or special proof-artifact requirements up front in the Linear issue description and Codex execution note.
5. When higher-level review accepts a slice, first provide paste-ready reviewer-acceptance text for the Codex live in-issue box (unless a no-Codex-acknowledgement exception is explicitly stated).
6. For a substantive slice, include any bounded tracker/control-state landing updates needed for coherent merged state in that acceptance instruction before any PR/merge guidance.
7. After providing acceptance text, give explicit operator next-step guidance (create PR now, merge now, or run a required acceptance-close sync first if applicable), framing PR creation/merge as operator completion actions after acceptance.
8. Use GitHub repository state as authoritative again for landed-state review, merge verification, and acceptance-close verification.
9. End acceptance-close review with explicit remaining operator step guidance, including merge/close/mark-Done actions where applicable.
10. Allow manual human PR landing when Codex cannot push/land automatically.
11. For a normal issue, merge is the last implementation step; mark the Linear issue **Done** only as the final move after substantive and acceptance-close merged state is reflected.
12. Do not run a default post-merge Codex acceptance-close patch for a normal merged issue.
13. Run post-merge follow-up only when a distinct new issue is intentionally opened or an explicitly declared exception requires it.

### Pre-issue read-first requirement

Before opening every new issue, higher-level review/governance must read:

1. `docs/noema-original-system-design.md`
2. `control/development-plan.md`
3. `control/development-tracker.md`

Commit/PR evidence should be provided first when reporting completion so reviewers can verify repository state directly.

## Stability expectations

Control-layer documents may be updated, replaced, reorganized, or removed as implementation needs evolve.

Those changes do **not** change Noema's architecture or system semantics unless corresponding system-definition documents in `docs/` are intentionally revised.

## Current control artifacts

- `development-plan.md`
- `development-tracker.md`
- `workflow-baseline.md`
- `phase-7-slice-1-reference-deployment-package.md`
