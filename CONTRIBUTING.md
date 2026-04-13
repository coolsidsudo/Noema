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

Latest completed/accepted slice: **Phase 4 — Slice 6 apply/recovery policy-profile refinement interoperability baseline**.

Current active slice: **Phase 4 — interoperability consistency verification and profile-compatibility conformance guidance across implementations**.

Contributions in the current slice should prioritize bounded interoperability consistency/conformance guidance aligned with accepted Slice 1/2/3/4/5/6 contracts, while preserving baseline architecture and accepted Phase 2/3/4 semantics.

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
