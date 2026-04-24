# Phase 9 Slice 1B Control Summary — bounded traceability and proposal/status service operations

## Purpose

Implement the next bounded, repo-backed service-core slice after Slice 1A by adding traceability retrieval and proposal submission/status behavior before any HTTP adapter work.

## Implemented scope

- Added `get_traceability_links` with one-hop workspace-scoped outbound/inbound/both link retrieval over accepted metadata keys.
- Added `submit_proposal` with repo-backed Markdown writes at `proposals/<workspace>/<proposal_id>.md` and bounded validation for initial status and target ids.
- Added `get_proposal_status` with lifecycle summary plus derived `result_links` and derived `log_refs`.
- Extended service package exports and deterministic tests for the new operations.
- Added concise runtime reference documentation for Slice 1B.

## Boundaries preserved

This slice remains service-core only and preserves Phase 9 anti-drift boundaries:

- no HTTP/server routes
- no operator UI
- no MCP adapter work
- no auth/platform broadening
- no recursive/global graph traversal
- no direct canonical structured publication from proposal submission
- no second object model
- no recentering as generic chat/RAG over files
- no treatment of Obsidian as authority layer

## Testing run

- `pytest -q tests/test_noema_service.py`

## Next-step pointer

Next slice: minimal HTTP adapter over the accepted service core (after Slice 1A + Slice 1B stability).
