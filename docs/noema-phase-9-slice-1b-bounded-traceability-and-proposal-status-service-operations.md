# Noema Phase 9 Slice 1B — Bounded traceability and proposal/status service operations

## Purpose of this slice

Phase 9 Slice 1B expands the accepted repo-backed service core from Slice 1A with the remaining bounded service operations needed before adding a thin HTTP adapter.

## Implemented in this slice

This slice adds three transport-neutral service-core operations over repo-backed Noema objects:

- `get_traceability_links`
  - one-hop only, workspace-scoped
  - supports `outbound`, `inbound`, and `both`
  - supports only `supports`, `targets`, `results_in`, `records_event_for`, `supersedes`
  - bounded by default `limit=100`, max `limit=500`
- `submit_proposal`
  - writes proposal Markdown files only to `proposals/<workspace>/<proposal_id>.md`
  - enforces allowed initial statuses (`draft`, `under_review`)
  - rejects empty `target_ids`
  - rejects duplicate proposal ids with conflict behavior
- `get_proposal_status`
  - returns proposal lifecycle summary from stored proposal metadata
  - derives `result_links` from proposal `results_in`
  - derives `log_refs` from workspace logs that reference the proposal through `records_event_for`
  - returns `review_history: []` when requested in this slice

## Explicitly not implemented yet

This slice does not implement:

- HTTP server or routes
- operator UI
- Obsidian plugin/runtime integration
- MCP adapters
- auth/platform provisioning work
- recursive/global graph traversal
- direct canonical publication of structured objects from proposal submission

## Future Obsidian-hook compatibility preserved by this slice

This slice preserves later Obsidian-hook compatibility by:

- keeping proposals as repo-visible Markdown files
- keeping service-core identifiers and workspace scoping stable
- preserving later vault-facing browse/projection and URI/open helper paths

No Obsidian hook is implemented in this slice.

## How this advances Phase 9

Slice 1B completes the bounded service-core operation set targeted for service-first sequencing in Phase 9 Slice 1. With Slice 1A and Slice 1B together, the accepted service core can now be wrapped by the next step:

- a minimal HTTP adapter over the accepted service core
