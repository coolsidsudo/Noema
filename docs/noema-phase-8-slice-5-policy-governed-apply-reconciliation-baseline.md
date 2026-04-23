# Noema Phase 8 Slice 5 — Policy-Governed Apply and Reconciliation Path Baseline

## Purpose

This document defines the bounded Slice 5 bridge from an **accepted proposal** into canonical `structured/` reconciliation while preserving proposal/review/apply boundaries and policy-gated direct authority posture.

## Bounded executable reference

Slice 5 introduces a minimal executable reference path in `packages/noema_maintainer/apply_reconcile.py`, wired through `packages/noema_maintainer/cli.py`.

Command:

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace <workspace-name> \
  --execute-governed-apply \
  --proposal-id <accepted-proposal-id> \
  --policy-gate-ticket <policy-gate-ticket>
```

## Apply eligibility and preconditions

Apply is executed only when all preconditions pass:

1. referenced proposal exists in `proposals/` for the same workspace,
2. proposal status is `accepted`,
3. proposal includes `approved_policy_gate_ticket`,
4. CLI-provided `--policy-gate-ticket` exactly matches that approved ticket,
5. proposal sets `allow_direct_canonical_apply: true`,
6. proposal `results_in` is non-empty,
7. every `results_in` id resolves to an existing `structured/` object in the workspace.

If any precondition fails, apply terminates with explicit error and no reconciliation write.

## Reconciliation behavior

When preconditions pass, the reference path performs a bounded canonical reconciliation step:

- appends a deterministic reconciliation note to each `structured/` object named in `results_in`,
- includes source proposal id, policy-gate ticket, timestamp, and compensation reminder,
- avoids implicit hidden mutation by making reconciliation note machine-visible and reviewer-readable.

This is intentionally narrow and deterministic. It is not a generic autonomous publishing engine.

## Required apply/reconciliation trace artifacts

The path emits a local run bundle under:

- `<workspaces-root>/<workspace>/projection/maintainer-apply-run/logs/`
- `<workspaces-root>/<workspace>/projection/maintainer-apply-run/compensations/`
- `<workspaces-root>/<workspace>/projection/maintainer-apply-run/apply-report.json`

Artifacts include:

1. **apply log event** (`class: logs`, `event_type: apply_reconciliation`) with proposal/result lineage via `records_event_for`,
2. **compensation placeholder artifact** (`class: proposals`, `status: draft`, `operation_type: compensation`),
3. **apply report** containing guards and output paths for deterministic operator reconstruction.

## Compensation / reversal posture

Slice 5 defines minimal correction posture by requiring an emitted compensation artifact for each governed apply run.

If an apply requires correction, the compensation artifact is promoted through normal proposal/review governance before any additional canonical direct mutation.

## Drift-check statement

This Slice 5 baseline does **not**:

- collapse proposal/review/apply into hidden mutation,
- broaden direct canonical authority beyond explicit policy gate,
- collapse `logs/` into canonical structured state,
- introduce broad autonomous publishing behavior,
- introduce workflow-engine/platform sprawl,
- invalidate accepted Slice 1–4 continuity.

## Next-slice pointer

Direct continuation remains:

- **Phase 8 Slice 6 — operator observability and recovery over maintainer/apply traces**.
