# Operator Bootstrap Guide (Minimal Single-Node Reference)

## Scope

This guide bootstraps the minimal reference package in `deploy/reference-single-node/`.

It is intentionally bounded to a single-node operator-controlled environment and demonstrates:

- one human-facing path
- one bounded machine-facing path
- one maintainer/curator operational path
- one continuity-aware bootstrap posture

It does not attempt production hardening, multi-node orchestration, or enterprise IAM.

## Prerequisites

- A single operator-controlled host (NAS or VPS class)
- Docker Engine + Compose plugin available
- Local clone of this repository on the host
- Operator write access to a persistent state location

## 1) Prepare environment paths

From repository root:

```bash
mkdir -p /srv/noema-state
cp deploy/reference-single-node/config/reference.env.example deploy/reference-single-node/config/reference.env
```

Edit `deploy/reference-single-node/config/reference.env`:

- `NOEMA_REPO_ROOT` -> absolute path to this repository on the host
- `NOEMA_STATE_ROOT` -> absolute path to persistent deployment-local continuity state
- optional port overrides

## 2) Start the reference package

```bash
docker compose \
  --env-file deploy/reference-single-node/config/reference.env \
  -f deploy/reference-single-node/docker-compose.yml up -d
```

Expected reference services:

- `noema-human-projection`
- `noema-agent-surface`
- `noema-maintainer`

## 3) Validate human-facing path

Open:

- `http://<host>:${NOEMA_HUMAN_PORT}/noema/examples/workspaces/sample-research-workspace/workspaces/ai-literature-mapping/projection/home/README.md`

This confirms a GUI-friendly projection browse path aligned with accepted human-client baseline behavior.

## 4) Validate bounded machine-facing path

Open:

- `http://<host>:${NOEMA_AGENT_PORT}/agent-surface-baseline.json`

This confirms an operator-visible bounded machine-facing surface anchor with proposal-layer-only write posture.

## 5) Validate maintainer operational path

Run a deterministic maintainer rebuild/check flow inside the maintainer container:

```bash
docker exec -it noema-maintainer python -m packages.noema_maintainer.cli --repo-root /opt/noema
```

This confirms maintainer/curator path availability without granting unreviewed canonical-write automation.

## 6) Minimal continuity posture checks

Before considering bootstrap complete, operator should verify:

1. repository knowledge classes are on persistent storage
2. `NOEMA_STATE_ROOT` exists on persistent storage and is backup-included
3. `deploy/reference-single-node/config/reference.env` is preserved in operator continuity records
4. compose package files and contract artifact are versioned/tracked for reproducible re-bootstrap

## 7) Stop/start lifecycle

Stop:

```bash
docker compose \
  --env-file deploy/reference-single-node/config/reference.env \
  -f deploy/reference-single-node/docker-compose.yml down
```

Restart:

```bash
docker compose \
  --env-file deploy/reference-single-node/config/reference.env \
  -f deploy/reference-single-node/docker-compose.yml up -d
```

## Non-goals (explicit)

This bootstrap guide does not provide:

- Kubernetes or multi-node deployment
- production hardening/perimeter playbooks
- managed service dependency patterns
- full auth runtime internals
- enterprise operations/SRE programs

## Drift-check statement

This operator bootstrap preserves:

- docs/ vs control/ boundary
- accepted visibility/authority and auth/identity semantics
- single-node-first NAS/VPS practicality
- separate human, machine, and maintainer paths

## Next-slice pointer

After this bootstrap baseline, next bounded work should validate reference-package conformance and incrementally replace placeholder surfaces with executable Noema runtime components while preserving current boundaries.
