# Noema Minimal Reference Deployment Package (Single Node)

## Purpose

This package defines a minimal, operator-controlled, single-node reference deployment shape for Noema.

It is intentionally narrow and implementation-light. It demonstrates a coherent bootstrap path that maps accepted Noema semantics into a practical NAS/VPS-style deployment baseline without introducing Kubernetes, enterprise IAM, or managed-service dependencies.

## Package boundary

This package is a **repo-native reference deployment package**.

- Stable system semantics remain authoritative in `docs/`.
- Execution and review state remains authoritative in `control/`.
- This `deploy/reference-single-node/` package provides concrete deployment/bootstrap assets that implement the accepted baseline posture.

## Included assets

- `docker-compose.yml` - minimal service shape for operator bootstrap
- `config/reference.env.example` - sample environment configuration for the reference package
- `contracts/agent-surface-baseline.json` - bounded machine-facing baseline contract artifact for operator inspection
- `operator/bootstrap.md` - step-by-step bootstrap guide
- `state/.keep` - explicit placeholder for operator-preserved continuity state roots

## Reference component mapping

### 1) Storage/workspace substrate

The reference package assumes canonical Noema state remains in operator-controlled host storage and repository-visible object classes (`raw/`, `structured/`, `proposals/`, `logs/`, and workspace projections).

In the compose shape this is represented by bind-mounted `NOEMA_REPO_ROOT` and a dedicated `NOEMA_STATE_ROOT` for deployment-local continuity artifacts.

### 2) Human-facing path

`noema-human-projection` serves workspace projection files over HTTP as a GUI-friendly browse/review surface for baseline human-client behavior.

This path is intentionally read-oriented and does not replace review/apply authority semantics.

### 3) Bounded machine-facing path

`noema-agent-surface` serves the baseline contract artifact to provide a concrete machine-facing path boundary and operator-visible surface anchor.

This path demonstrates bounded machine entry shape and avoids claiming full runtime auth/policy engine implementation in this slice.

### 4) Maintainer/curator operational path

`noema-maintainer` provides a containerized execution surface for deterministic maintainer rebuild/check workflows using repository-local tools.

This path is operator-invoked and review-bounded; it does not introduce autonomous canonical-write behavior.

## Continuity-aware operator posture (minimal)

This package assumes continuity-critical state is preserved at least across:

1. repository knowledge/state (`raw`, `structured`, `proposals`, `logs`, workspace artifacts)
2. deployment-local state under `NOEMA_STATE_ROOT`
3. operator environment/configuration material required for reproducible bootstrap

This package is continuity-aware but not a full disaster-recovery playbook.

## Explicit non-goals

This reference package intentionally does **not** include:

- Kubernetes, multi-node orchestration, or fleet management
- enterprise IAM or production auth-stack internals
- managed cloud dependency assumptions
- production hardening internals or SRE-grade operations programs
- full implementation of all Noema runtime/auth internals

## Drift-check statement

This package preserves Noema architecture invariants:

- open-source and reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support assumptions
- editor-agnostic and Obsidian-compatible posture
- independent separation of domain/profile/workspace/content-type/visibility/authority axes

## Next-slice pointer

Next bounded continuation after this slice should focus on **reference deployment conformance validation and incrementally executable runtime integration** while preserving this single-node-first package boundary.
