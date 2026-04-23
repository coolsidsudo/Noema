# Noema Phase 8 Slice 4 — Bounded Executable Maintainer Loop Reference

## Purpose

This document records the initial executable realization for **Phase 8 Slice 4** as a narrow, deterministic, fixture/example-driven maintainer loop path.

The implementation is intentionally substitution-oriented: it proves that accepted Slice 1–3 contracts are executable without broadening direct canonical authority or introducing platform sprawl.

## Realized bounded executable path

The executable path is exposed via `packages/noema_maintainer/cli.py` using:

- `--execute-bounded-loop`
- `--workspace <workspace-name>`

When invoked, the reference path:

1. scans repository objects in `raw/`, `structured/`, `proposals/`, and `logs/`,
2. selects a deterministic workspace-local structured target,
3. emits a proposal artifact for a canonical-impacting candidate update (`apply_mode: proposal-only`),
4. emits a corresponding append-oriented operational log/event artifact,
5. writes a deterministic run report for operator/reviewer reconstruction.

Outputs are written to:

- `<workspaces-root>/<workspace>/projection/maintainer-loop-run/proposals/`
- `<workspaces-root>/<workspace>/projection/maintainer-loop-run/logs/`
- `<workspaces-root>/<workspace>/projection/maintainer-loop-run/run-report.json`

## Contract continuity mapping (Slices 1–3)

- **Slice 1 continuity (maintainer seam/lane posture):** canonical-impacting structured work defaults to proposal emission; no direct structured canonical write occurs in this path.
- **Slice 2 continuity (proposal contract posture):** emitted proposal includes identity/lifecycle, target scope, rationale/problem framing, evidence-support hooks (`supporting_raw_ids`), and explicit proposal-only apply posture.
- **Slice 3 continuity (operational trace posture):** emitted log contains deterministic event identity/class/timing/actor/run linkage and affected-object/records-event-for traceability.

## Determinism and inspectability

Determinism is preserved by:

- fixed run profile/version markers,
- deterministic target-selection ordering,
- fixed deterministic timestamp for this bounded reference path,
- stable run/proposal/log identifiers.

Inspectability is preserved by explicit output bundle paths and by run-report object link summaries.

## Drift-check statement

This Slice 4 realization does **not**:

- collapse proposal/review/apply boundaries,
- broaden direct canonical apply authority,
- collapse `logs/` into canonical structured knowledge,
- recenter Noema around generic chat/RAG behavior,
- introduce multi-agent/orchestration platform sprawl,
- invalidate accepted Slice 1–3 contracts.

## Exact bounded run command

```bash
python -m packages.noema_maintainer.cli \
  --repo-root . \
  --workspaces-root examples/workspaces/sample-research-workspace/workspaces \
  --workspace ai-literature-mapping \
  --execute-bounded-loop
```

## Continuity pointer after Slice 4

Most direct downstream direction after this bounded realization:

- strengthen policy-governed apply pathways and exception-lane evidence,
- deepen operator observability/recovery around maintainer run replay and compensating events,
- only then consider bounded multi-maintainer coordination patterns that preserve proposal-first governance.
