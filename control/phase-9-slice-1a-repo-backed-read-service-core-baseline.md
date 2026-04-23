# Phase 9 Slice 1A — Repo-Backed Read Service Core Baseline

## Purpose

Deliver the first bounded Phase 9 service-core implementation: repo-backed read operations for object retrieval and listing.

## Implemented scope

- Added `packages/noema_service` with transport-neutral read operations:
  - `get_object_by_id`
  - `list_objects`
- Reused existing repo-native scan substrate (`scan_repository`, `ObjectRecord`) with no second object model.
- Added bounded filtering, sorting, optional content loading, optional direct relationship hints, and cursor pagination (`offset:<integer>`).
- Added deterministic tests in `tests/test_noema_service.py` for envelope shape, content toggles, filtering, pagination, invalid cursor handling, workspace scoping, and relationship hints behavior.

## Boundaries preserved

- No HTTP/server/routes added.
- No traceability operation, proposal submission, or proposal status operation added yet.
- No operator UI, Obsidian integration runtime, MCP, or auth/platform work added.
- No mutation/write paths introduced.

## Testing run

- `pytest -q tests/test_noema_service.py`

## Next-step pointer

Add bounded service-core operations for traceability links and proposal/status behavior next, then add the minimal HTTP adapter on top of the expanded service core.
