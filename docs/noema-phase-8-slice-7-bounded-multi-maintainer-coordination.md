# Noema Phase 8 Slice 7 — Bounded Multi-Maintainer Coordination Reference

This document records the executable reference path realized for Phase 8 Slice 7.

## Runtime shape

The bounded coordination runtime is implemented in `packages/noema_maintainer/coordination.py` and surfaced through `packages/noema_maintainer/cli.py`.

### Coordination command surface

- Claim a bounded scope for one maintainer:

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace ai-literature-mapping \
  --execute-coordination-claim \
  --coordination-maintainer-id maintainer-alpha \
  --coordination-scope structured-target-a
```

- Check overlap against current active claims:

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace ai-literature-mapping \
  --execute-coordination-conflict-check \
  --coordination-maintainer-id maintainer-beta \
  --coordination-scope structured-target-a
```

- Emit an operator-visible coordination report:

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace ai-literature-mapping \
  --emit-coordination-report
```

## Emitted artifacts

All coordination outputs are scoped under:

- `<workspace>/projection/maintainer-coordination-run/`

Artifacts:

- `coordination-state.json`: append-style claim state ledger.
- `claims/<claim-id>.json`: per-claim attributable artifact (active or blocked conflict).
- `conflict-check.json`: deterministic overlap check output.
- `coordination-report.json`: operator review summary over active/blocked claims plus guards.

## Guard posture

The coordination path is intentionally non-authoritative for canonical mutation:

- no direct `structured/` mutation,
- no proposal/review/apply boundary collapse,
- no policy-gated apply bypass,
- no hidden collision handling.

Conflicts are surfaced explicitly as blocked claim artifacts for operator review.
