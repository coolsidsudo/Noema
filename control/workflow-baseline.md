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
- Latest completed/accepted slice: Phase 7 Slice 4 bounded executable proposal-submission continuity for the reference single-node package
- Current active slice: none (no under-review slice currently opened)
- Next queued slice: Phase 7 Slice 5 bounded proposal status/review continuity and matching conformance-hardening continuation (queued/proposed; not yet opened)
- Phase 5 queue status: closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of system design / development plan it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

### Rule 5: Use the full Linear/Codex/GitHub workflow loop with phase-appropriate review authority

For repository execution workflow:

1. Delegate from a Linear issue to Codex to start implementation work.
2. Use the live in-issue Codex composer/comment box in Linear for follow-up instructions and iteration.
3. Before PR creation/merge/landed-state verification, treat Codex live in-issue output as the primary higher-level in-flight review surface; GitHub may be stale during this phase and should not be overtreated as authoritative for pre-merge implementation review.
4. If full changed-file content or other special proof artifacts are required, request that proof shape up front in the Linear issue description and Codex execution note; follow-up requests should not introduce materially new proof requirements that should have been declared earlier.
5. At the end of implementation review, reviewer guidance must explicitly state the human operator's next step (for example: create PR now, merge now, wait, or do not merge yet).
6. For landed-state review, merge verification, and acceptance-close verification, treat GitHub repository state (branch/commit/diff/PR) as authoritative again.
7. After acceptance-close review, reviewer guidance must explicitly state the remaining operator step(s), including merge/close/mark-Done actions where applicable.
8. When Codex cannot push/land automatically, a human may manually push or merge the reviewed PR while preserving issue/PR traceability.
9. After the substantive slice and any required acceptance-close sync are merged and reflected in landed state, mark the Linear issue **Done** as the final workflow move.

Additional guardrails:

- Use **Linear issues/comments** as the default execution and reporting channel for Codex issue work.
- During in-flight pre-merge review, reviewers should prefer Codex live in-issue output as the primary surface and avoid over-weighting potentially stale GitHub state.
- For landed-state and acceptance-close verification, reviewers should prefer direct repository verification in GitHub over summary text alone when GitHub state is available.
- Manual pasteback into ChatGPT should be used only as a fallback when needed content is not visible in Linear or GitHub.

## Current implementation slice (immediate)

There is **no currently opened under-review slice** at this moment; Phase 7 Slice 4 is accepted/completed and Phase 7 Slice 5 remains queued/proposed pending explicit open.

### Slice objective

Keep control-state synchronized to the accepted Phase 7 Slice 4 outcome without opening a new under-review slice by default.

### Slice deliverables

1. Record Phase 7 Slice 4 as latest completed/accepted slice in control-state.
2. Keep current active/under-review slice state as none.
3. Keep Phase 7 Slice 5 as queued/proposed only unless explicitly opened in a later patch.

### Slice done criteria

This slice is complete when:

- Phase 7 Slice 4 is recorded as accepted in control-state.
- Control-state keeps current active/under-review slice state as none.
- Next-pointer language remains coherent: Phase 7 Slice 5 is queued/proposed and not yet opened.

### Continuity note

Accepted Phase 6 deployment and backup/restore semantics remain authoritative in:

- `docs/noema-self-hosted-deployment-operations-baseline.md`
- `docs/noema-backup-restore-operational-guidance-baseline.md`

Accepted Phase 7 Slice 4 package/runtime substitution and conformance-expansion assets remain in `deploy/reference-single-node/`; this patch only synchronizes control-state and does not modify deployment assets.

**Review posture:** No new under-review slice is opened by this patch; Phase 7 Slice 5 remains queued/proposed until explicitly started.


## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references it together with the two baseline docs.
