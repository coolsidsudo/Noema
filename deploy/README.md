# Deployment

This directory contains repo-native deployment assets and templates for Noema.

## Current reference package

- `reference-single-node/` - Phase 7 Slice 1 minimal operator bootstrap package for a single-node self-hosted reference environment.

The package is intentionally bounded and demonstrates:

- one human-facing projection path
- one bounded machine-facing path
- one maintainer/curator operational path
- one continuity-aware operator bootstrap posture

## Boundary reminder

- Stable system semantics remain in `docs/`.
- Execution/control state remains in `control/`.
- Deployment package assets here are practical implementation anchors for accepted semantics.
