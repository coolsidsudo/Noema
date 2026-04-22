# Noema Minimal Reference Deployment Package (Single Node)

## Purpose

This package defines a minimal, operator-controlled, single-node reference deployment shape for Noema.

It is intentionally narrow and implementation-light. It demonstrates a coherent bootstrap path that maps accepted Noema semantics into a practical NAS/VPS-style deployment baseline without introducing Kubernetes, enterprise IAM, or managed-service dependencies.

## Package boundary

This package is a **repo-native reference deployment package**.

- Stable system semantics remain authoritative in `docs/`.
- Execution and review state remains authoritative in `control/`.
- `deploy/reference-single-node/` provides concrete deployment/bootstrap assets implementing the accepted baseline posture.

## Included assets

- `docker-compose.yml` - minimal service shape for operator bootstrap
- `config/reference.env.example` - sample environment configuration for the reference package
- `contracts/agent-surface-baseline.json` - bounded machine-facing contract artifact for operator inspection
- `agent_surface/server.py` - minimal executable machine-facing facade (bounded read/query only)
- `checks/check_reference_package.py` - conformance checks for executable substitution and boundedness claims
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

`noema-agent-surface` runs a minimal executable facade intentionally bounded to read/query operations plus proposal-lane lifecycle and review-evidence continuity.

Executable operations in this slice:

- `get_object_by_id`
- `list_objects`
- `submit_proposal` (proposal-lane only)
- `get_proposal_status` (proposal-lane status visibility)
- `review_proposal_status` (proposal-lane review continuity only)
- `get_proposal_review_evidence` (proposal-lane review evidence and log-link continuity visibility only)
- `list_recent_continuity_validation_outcomes` (bounded operator inspection of recent validated/failed continuity outcomes)

Guardrails in this slice:

- canonical write/apply remains out of scope
- proposal lifecycle writes are constrained to deterministic inspectable artifacts under `proposals/submitted/` plus append-only review continuity log-link records at `logs/operations/proposal-review-events.jsonl`
- repository access remains read-oriented and constrained to bounded object classes (`raw`, `structured`, `proposals`, `logs`), with a narrow writable subpath only for `proposals/submitted/`
- no direct canonical writes are performed in `structured/`, `raw/`, or other non-proposal classes

This keeps the machine-facing path executable without broadening into auth-stack or policy-engine implementation.

### 4) Maintainer/curator operational path

`noema-maintainer` provides a containerized execution surface for deterministic maintainer rebuild/check workflows using repository-local tools.

This path is operator-invoked and review-bounded; it does not introduce autonomous canonical-write behavior.

## Conformance checks (expanded for Slice 9 recent continuity-inspection ergonomics)

Run from repository root:

```bash
python deploy/reference-single-node/checks/check_reference_package.py
```

This verifies:

1. `noema-agent-surface` uses executable facade code (not static file serving)
2. bounded read/query operations are present and correctly scoped
3. proposal lifecycle continuity (`submit_proposal`, `get_proposal_status`, `review_proposal_status`, `get_proposal_review_evidence`) is executable but bounded to proposal artifacts plus append-only review log-link continuity records
4. review evidence reads enforce bounded review-history shape and linked append-only log-record continuity, with bounded deterministic diagnostics on fail-closed continuity rejection
5. recent continuity-validation outcomes are operator-inspectable via one bounded read-only surface with explicit limits, deterministic retention-window rollup, and explicit truncation metadata
6. canonical write/apply remains out of scope
7. operator bootstrap and package mapping docs remain consistent with executable substitution

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

Next bounded continuation after this slice should focus on **Phase 7 continuity-inspection operator ergonomics beyond retention/rollup (for example compact filtering/export cues)** while preserving single-node package boundaries and proposal-only canonical-write posture.
