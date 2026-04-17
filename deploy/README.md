# Deployment

This directory contains repo-native deployment assets and templates for Noema (single-node-first reference posture).

## Current reference package

- `reference-single-node/` - Phase 7 Slice 3 minimal operator bootstrap package for a single-node self-hosted reference environment with an executable bounded machine-facing facade.

The package is intentionally bounded and demonstrates:

- one human-facing projection path
- one bounded machine-facing executable read/query-only path
- one maintainer/curator operational path
- one continuity-aware operator bootstrap posture

## Boundary reminder

- Stable system semantics remain in `docs/`.
- Execution/control state remains in `control/`.
- Deployment package assets here are practical implementation anchors for accepted semantics.
