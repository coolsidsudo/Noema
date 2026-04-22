# Noema Workflow Baseline Adoption

## Purpose

This document adopts the accepted architecture baseline into the active project workflow.
It is the execution bridge between:

- `docs/noema-original-system-design.md` (architecture and system-definition source of truth)
- `control/development-plan.md` (long-horizon roadmap source of truth)
- `control/development-tracker.md` (live execution tracker source of truth)

## Authority mapping (non-overlapping)

1. **Original system design** (`docs/noema-original-system-design.md`) owns architecture and system-definition baseline.
2. **Development plan** (`control/development-plan.md`) owns long-horizon roadmap, phase intent, and sequencing rationale.
3. **Development tracker** (`control/development-tracker.md`) owns live execution state: latest accepted slice, any current under-review slice, next queued slice, and brief continuity notes.

If implementation details conflict with these documents, implementation must be updated to match the baseline unless the baseline is intentionally revised through an explicit architecture/workflow change.

## Required pre-issue read-first rule (higher-level review/governance)

Before opening **every new issue**, higher-level review/governance must read, in order:

1. `docs/noema-original-system-design.md`
2. `control/development-plan.md`
3. `control/development-tracker.md`

Issue framing should be derived from those three documents together so architecture, long-horizon direction, and live state are all considered before new work is queued.

Ownership baseline for issue start:

- Higher-level review/governance owns initiation of the next issue by default.
- Higher-level review/governance writes the initial issue description and the initial Codex execution note by default.
- The operator is not, by default, asked to author or paste that initial issue package.
- Default paste-ready text for the operator should be limited to live-issue follow-up instructions for the existing Linear/Codex issue box.

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

Implementation should progress in development-plan order unless a documented dependency requires otherwise.

Use `control/development-tracker.md` for current live slice status, queued continuation state, and immediate execution continuity.

### Rule 4: Make each PR traceable to baseline

Each implementation PR should include:

- Baseline references (which section(s) of original system design / development plan / tracker it implements)
- Drift check statement (what was intentionally not changed)
- Next-slice pointer (what follows directly next)

### Rule 5: Use the full Linear/Codex/GitHub workflow loop with phase-appropriate review authority

For repository execution workflow:

1. Higher-level review/governance initiates the next Linear issue and provides the initial issue description plus initial Codex execution note; this initial package is not a default operator authoring/paste task.
2. Delegate from that Linear issue to Codex to start implementation work.
3. Use the live in-issue Codex composer/comment box in Linear for follow-up instructions and iteration.
4. Before PR creation/merge/landed-state verification, treat Codex live in-issue output as the primary higher-level in-flight review surface; GitHub may be stale during this phase and should not be overtreated as authoritative for pre-merge implementation review.
5. If full changed-file content or other special proof artifacts are required, request that proof shape up front in the Linear issue description and Codex execution note; follow-up requests should not introduce materially new proof requirements that should have been declared earlier.
6. When a slice is accepted at higher-level review, first provide a fully formed paste-ready reviewer-acceptance message for the Codex live in-issue box (unless a no-Codex-acknowledgement exception is explicitly declared for that slice).
7. For a substantive slice, reviewer acceptance instructions must include any bounded tracker/control-state updates required so landed state will remain coherent before PR/merge; these updates belong to the accepted issue path, not to a default separate post-merge patch.
8. After that acceptance text is provided, reviewer guidance must explicitly state the human operator's immediate next completion step (for example: create PR now, merge now, or run a required acceptance-close sync first if applicable), and must frame PR creation/merge as operator completion actions after acceptance rather than unresolved acceptance conditions.
9. For landed-state review, merge verification, and acceptance-close verification, treat GitHub repository state (branch/commit/diff/PR) as authoritative again.
10. After acceptance-close review, reviewer guidance must explicitly state the remaining operator step(s), including merge/close/mark-Done actions where applicable.
11. When Codex cannot push/land automatically, a human may manually push or merge the reviewed PR while preserving issue/PR traceability.
12. For a normal issue, merge is the last implementation step; after the substantive slice and any required acceptance-close sync are merged and reflected in landed state, mark the Linear issue **Done** as the final workflow move.
13. There is no default post-merge Codex acceptance-close patch for a normal merged issue.
14. Any additional post-merge follow-up should occur only if a distinct new issue is intentionally opened or if an explicitly declared exception requires it.

### Rule 5A: Reviewer acceptance-message pattern for the live issue/Codex box

Unless a no-Codex-acknowledgement exception is explicitly declared, higher-level review should normally provide a fully formed paste-ready acceptance message that includes:

1. **Explicit acceptance state**: clearly states that the issue/slice is accepted at higher-level review.
2. **Acceptance judgment section**: briefly explains what is accepted and why.
3. **Drift-check acceptance section**: briefly explains what was intentionally not broadened or changed.
4. **Bounded same-issue landed-state alignment instructions (when needed)**: includes any required tracker/control-state sync that must land in the accepted issue path before PR/merge so landed state remains coherent.
5. **Codex-side status instruction**: tells Codex to treat the issue/slice as reviewer-accepted from the Codex work side.
6. **Acknowledgement shape instruction**: requests only a brief acknowledgement when brief acknowledgement is the intended next move.

This acceptance-message pattern is a clarity requirement for reviewer instructions, not a change to review authority. It preserves the existing in-flight vs landed-state authority split and accepted Linear -> Codex -> GitHub flow.

Additional guardrails:

- Use **Linear issues/comments** as the default execution and reporting channel for Codex issue work.
- Higher-level review/governance owns initial issue initiation and initial issue drafting (issue description + initial Codex execution note); default operator paste-ready output should target only live-issue follow-up instructions.
- Unless a no-acknowledgement exception is explicitly declared, reviewer acceptance text should be fully formed and should include explicit acceptance state, acceptance judgment, drift-check acceptance, and Codex-side acknowledgement shape.
- During in-flight pre-merge review, reviewers should prefer Codex live in-issue output as the primary surface and avoid over-weighting potentially stale GitHub state.
- When accepting a slice in higher-level review, reviewers should provide paste-ready Codex live-box acceptance text before instructing PR/merge actions (unless a no-acknowledgement exception is explicitly declared).
- For substantive slices, acceptance instructions should include bounded tracker/control-state landing updates needed for coherent merged state before PR/merge guidance is executed.
- After acceptance is established, PR creation and merge should be described as operator completion actions, not as unresolved acceptance evidence.
- For landed-state and acceptance-close verification, reviewers should prefer direct repository verification in GitHub over summary text alone when GitHub state is available.
- Manual pasteback into ChatGPT should be used only as a fallback when needed content is not visible in Linear or GitHub.

## Definition of done for baseline adoption

This architecture-adoption step is complete when this document is present and used as the workflow bridge, and future implementation work references the original system design, development plan, and development tracker with their non-overlapping authority boundaries.
