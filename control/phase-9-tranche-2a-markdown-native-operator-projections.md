# Phase 9 Tranche 2A Control Summary — Markdown-native operator projections

## Purpose

Implement a bounded operator-facing projection generator that emits deterministic Markdown browse/review surfaces over accepted repo-backed Noema workspace state.

## Implemented scope

- Added `packages/noema_operator` as a separate operator package, leaving maintainer semantics unchanged.
- Added deterministic workspace-local outputs under `<workspace-root>/projection/operator/`:
  - `index.md`
  - `objects.md`
  - `proposals.md`
  - `recent.md`
- Reused accepted repo/service scanning conventions through the repository substrate rather than HTTP.
- Added workspace resolution for repo-relative paths, absolute paths, and known workspace ids.
- Added deterministic Markdown table rendering with stable missing values and escaping for pipes/newlines/carriage returns.
- Added function-level and CLI-level tests using fixture-local temporary repos/workspaces.

## Boundaries preserved

- No changes to service-core behavior or response envelopes.
- No HTTP server requirement for projection generation.
- No Obsidian plugin, Obsidian API usage, `.obsidian` dependency, or Obsidian URI helper.
- No native web UI.
- No MCP adapter.
- No auth/TLS/CORS/deployment hardening work.
- No canonical apply behavior or proposal review decisions.
- No broad query/search/RAG/chat interface.
- No changes to `control/development-tracker.md` in this implementation pass.

## Testing run

- `pytest -q tests/test_noema_service.py tests/test_noema_service_http.py`
- `pytest -q tests/test_noema_operator_projections.py`

## Next-step pointer

After reviewer acceptance, perform the tiny accepted-state tracker/control sync only if explicitly requested by reviewer guidance.
