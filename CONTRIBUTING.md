# Contributing to Noema

Thanks for contributing.

## Baseline-first workflow

Before proposing implementation changes, read:

1. `docs/noema-original-system-design.md`
2. `docs/noema-development-plan.md`
3. `docs/noema-workflow-baseline.md`

Treat these as the architecture and execution baseline.

## Phase alignment

Current active slice: **Phase 1 — Repository skeleton**.

Contributions in this phase should prefer structure, conventions, and concise docs over heavy implementation.

## Drift checks for pull requests

Each PR should include:

- Baseline reference: what design-plan sections the change implements
- Drift check: what invariants were preserved
- Next-slice pointer: what follows next

## Architectural invariants to preserve

- Open-source and reusable framing
- Self-hosted assumptions (NAS/VPS practical)
- Multi-human and multi-agent orientation
- Obsidian-compatible but not Obsidian-dependent
- Clear separation of domain, profile, workspace/project, content type, visibility, and authority
- Distinction between raw, structured, proposals, and logs
