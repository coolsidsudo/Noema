# Phase 7 Slice 1 — Minimal Reference Deployment Package and Operator Bootstrap Baseline (Under Review)

## Status

- Slice: Phase 7 Slice 1
- State: Under review (not accepted)
- Previous accepted slice: Phase 6 Slice 6 — conformance evidence interoperability refinement scoping

## Slice objective

Implement a minimal, practical, single-node reference deployment package that maps accepted Noema semantics into an operator-bootstrappable shape.

## Implemented scope in this slice

1. Minimal repo-native deployment package under `deploy/reference-single-node/`
2. Operator bootstrap guide for standing up the reference package
3. Minimal sample config/layout artifacts for concreteness
4. Explicit mapping for storage substrate, human-facing path, bounded machine-facing path, and maintainer/curator path
5. Minimal continuity-aware operator posture statement
6. Explicit non-goals to prevent orchestration/enterprise/productization drift

## Boundaries preserved

- `docs/` remains system-definition source of truth.
- `control/` remains repository execution/control source of truth.
- This slice does not redefine accepted `docs/` semantics.
- This slice remains single-node-first and NAS/VPS practical.

## Drift-check statement

This slice preserves the accepted architecture invariants:

- open-source reusable framing
- self-hosted practicality
- multi-human and multi-agent support
- editor-agnostic, Obsidian-compatible posture
- policy axis independence (domain/profile/workspace/content type/visibility/authority)

## Next-slice pointer

Proposed next bounded continuation: **Phase 7 Slice 2 — reference-package conformance checks and executable runtime substitution planning**.
