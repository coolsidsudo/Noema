# Noema Phase 8 Slice 6 — Operator Observability and Recovery over Maintainer/Apply Traces

## Purpose

This document defines the bounded Slice 6 bridge from **emitted maintainer/apply traces** into an **operator-usable reconstruction and recovery surface**.

Slice 6 builds directly on Slice 5 apply/reconciliation outputs and keeps proposal/review/apply boundaries explicit.

## Bounded executable reference

Slice 6 introduces a minimal executable operator-facing snapshot path in `packages/noema_maintainer/observe_recover.py`, wired through `packages/noema_maintainer/cli.py`.

Command:

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace <workspace-name> \
  --proposal-id <accepted-proposal-id> \
  --emit-operator-observability-report
```

## What the operator can inspect

The command emits:

- `<workspaces-root>/<workspace>/projection/maintainer-observability-run/<proposal-id>-observability-report.json`

The report is a bounded reconstruction surface that includes:

1. source-context lineage (`supporting_raw_ids`, resolved raw object paths),
2. proposal lineage (status, target ids, policy gate metadata),
3. apply/reconciliation lineage (apply id, apply report, apply log event linkage, reconciled structured paths),
4. compensation/recovery posture (compensation artifact state and operator recovery steps).

## Lineage reconstruction contract

Slice 6 requires the report to surface enough data for a reviewer/operator to reconstruct:

`source context -> proposal -> apply/reconciliation -> compensation/recovery posture`

Required linkage fields are derived from existing governed artifacts:

- proposal metadata (`id`, `status`, `results_in`, `supporting_raw_ids`, policy gate fields),
- apply report bundle paths from Slice 5,
- apply log `records_event_for` references,
- compensation placeholder metadata (`proposal_state`, `operation_type`, `source_apply_id`),
- structured-object reconciliation-note presence per `results_in` target.

## Recovery posture

Slice 6 keeps recovery human-governed and bounded.

The observability report does **not** perform correction automatically. Instead, it records the recovery boundary and operator steps:

1. inspect apply report + apply log + reconciled structured objects,
2. evolve emitted compensation artifact through normal proposal/review governance,
3. run any further direct apply only after accepted review outcome and policy gate checks.

## Drift-check statement

This Slice 6 baseline does **not**:

- collapse proposal/review/apply/recovery boundaries,
- permit hidden canonical mutation through observability or recovery ergonomics,
- weaken policy-gated authority posture,
- collapse logs into canonical structured knowledge,
- introduce broad observability/orchestration platform behavior,
- invalidate accepted Slice 1–5 continuity.

## Next-slice pointer

Direct continuation remains conservative and bounded:

- **Phase 8 Slice 7 — bounded multi-maintainer coordination (only if still justified after Slice 6)**.
