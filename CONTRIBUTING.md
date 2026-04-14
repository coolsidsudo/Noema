# Contributing to Noema

Thanks for contributing.

This document describes contribution workflow for this repository and is not part of the Noema system definition.

## Baseline-first workflow

Before proposing implementation changes, read:

1. `docs/noema-original-system-design.md`
2. `control/development-plan.md`
3. `control/workflow-baseline.md`

Treat these as the architecture and execution baseline.

## Phase alignment

Latest completed/accepted slice: **Phase 5 Slice 2 — deterministic relationship and traceability cross-reference checks in the maintainer baseline**.

Current active slice: **Phase 5 — next bounded maintainer workflow implementation slice after Slice 2**.

Contributions in the current slice should prioritize bounded Phase 5 maintainer workflow baseline progress while preserving baseline architecture and accepted Phase 2/3/4 semantics.

## Local verification command baseline

Run repository tests from repo root with:

- `pytest -q`

The repository test configuration ensures local package imports resolve under standard `pytest` invocation (no extra `PYTHONPATH` prefix required).

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
