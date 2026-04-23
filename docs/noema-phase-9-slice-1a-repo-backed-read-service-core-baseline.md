# Noema Phase 9 Slice 1A — Repo-Backed Read Service Core Baseline

## Purpose of this slice

This slice implements the smallest bounded Phase 9 service-core step: a transport-neutral, repo-backed read layer for Noema objects.

## Implemented in this slice

- New `packages/noema_service` read-side package with:
  - `get_object_by_id`
  - `list_objects`
- Repo-backed loading via existing `scan_repository(...)` and `ObjectRecord` substrate.
- Workspace-scoped filtering plus bounded filters for class, status, ids, and `title_contains`.
- Bounded pagination with cursor format `offset:<integer>`, default `limit=50`, max `limit=200`.
- Optional markdown body inclusion and optional direct relationship hints from existing metadata fields.
- Deterministic tests for bounded retrieval/listing behavior and cursor/error handling.

## Explicitly not implemented yet

This slice does **not** implement:

- HTTP server or routes
- traceability retrieval operation
- proposal submission
- proposal status retrieval
- operator UI
- Obsidian plugin/integration runtime code
- MCP adapter
- auth/platform identity provisioning

## How this supports the larger Phase 9 direction

This baseline establishes a reusable service-core seam over the current repo-native object model so later slices can add traceability/proposal/status operations and then a thin adapter layer without changing object semantics.

## Future Obsidian-hook compatibility preserved by this slice

This slice preserves later compatibility by staying:

- repo-backed
- markdown/object oriented
- workspace-aware
- suitable for later vault-facing browse/projection layers

No Obsidian hook is implemented in this slice.

## Next step pointer

Next issue should add bounded `get_traceability_links`, `submit_proposal`, and `get_proposal_status` service operations, then add a minimal HTTP adapter after those service operations are stable.
