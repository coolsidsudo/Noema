# Noema Agent Surface Contract

## Purpose and boundary

This document defines the stable machine-facing surface contract for Noema's agent-interface baseline.

This stable system-definition document originated from the accepted Phase 4 Slice 2 baseline.

It turns baseline semantics into explicit operation shapes for:

- bounded read/query
- bounded proposal submission
- attributable agent identity and scoped behavior
- auditable machine activity

This slice remains documentation-first and implementation-light. It defines contract semantics and operation shapes, not a production server/runtime.

## Baseline references

This contract extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `docs/noema-index-catalog-baseline.md`
- `docs/noema-human-client-baseline.md`
- `docs/noema-agent-interface-baseline.md`

## Contract posture

### Semantics first, transport second

Noema supports multiple protocol shapes (including MCP-style tools and bounded APIs). The contract semantics in this document are authoritative; protocol mapping is an adapter concern.

### Bounded authority

Agent-facing operations in this slice allow:

- bounded read/query over discoverable objects
- bounded proposal submission and proposal-status retrieval

Agent-facing operations in this slice do **not** allow:

- direct canonical publication of structured objects
- unrestricted filesystem traversal
- bypass of policy/scope boundaries

## Shared envelope conventions

All operations SHOULD use a consistent envelope shape.

### Success envelope (baseline)

```json
{
  "ok": true,
  "operation": "list_objects",
  "request_id": "req_01hxyz...",
  "timestamp": "2026-04-10T00:00:00Z",
  "data": { "...operation-specific...": "..." },
  "meta": {
    "workspace": "workspace-id",
    "scope_applied": {
      "visibility": "policy-filtered",
      "classes": ["structured", "proposals"]
    },
    "pagination": {
      "limit": 50,
      "next_cursor": "cur_abc",
      "has_more": true
    }
  }
}
```

Required top-level fields (success):

- `ok` (`true`)
- `operation`
- `request_id`
- `timestamp`
- `data`

Recommended top-level fields:

- `meta`

### Error envelope (baseline)

```json
{
  "ok": false,
  "operation": "get_object_by_id",
  "request_id": "req_01hxyz...",
  "timestamp": "2026-04-10T00:00:00Z",
  "error": {
    "category": "not_found",
    "code": "OBJECT_NOT_FOUND",
    "message": "Object not found in allowed scope.",
    "retryable": false,
    "details": {
      "object_id": "structured-abc"
    }
  }
}
```

Required error fields:

- `category`
- `code`
- `message`
- `retryable`

Optional error fields:

- `details`

### Baseline error categories

- `invalid_request` — malformed inputs, invalid parameter combinations, unsupported filter values
- `unauthorized` — identity missing/invalid for requested operation
- `forbidden` — identity valid, but scope/policy denies this operation or object
- `not_found` — object/proposal not found in effective allowed scope
- `conflict` — write conflict or state conflict (for example status transition constraints)
- `rate_limited` — request exceeds configured rate/throughput boundaries
- `limit_exceeded` — request exceeds pagination/result/window limits
- `temporarily_unavailable` — service dependency temporarily unavailable
- `internal_error` — unexpected processing failure

## Shared limits and boundaries (baseline)

Implementations MAY choose exact numeric limits, but MUST publish defaults and max values per deployment/profile.

Baseline limit dimensions:

- max `limit` for list/query operations
- max cursor lifetime (if cursors are used)
- max proposal payload size (bytes/chars)
- max `target_ids` count in a single proposal
- per-agent and/or per-workspace rate limits
- max traceability fan-out per request

When a limit is hit, return `limit_exceeded` (or `rate_limited` where appropriate) with machine-parseable details.

## Operation contract definitions

The following operations define the minimum concrete surface for this slice.

---

### 1) `get_object_by_id`

#### Purpose

Return one object by stable `id` within bounded workspace/scope policy.

#### Required inputs

- `workspace` (string)
- `id` (string)

#### Optional inputs

- `include_content` (boolean, default implementation-defined; recommended default `true` for authorized classes)
- `include_relationship_hints` (boolean; include direct traceability pointers)
- `if_none_match` (string; optional cache/version token where supported)

#### Response shape (`data`)

- `object`
  - `id`
  - `class` (`raw|structured|proposals|logs`)
  - `workspace`
  - `status`
  - `metadata` (baseline metadata profile fields)
  - `content` (omitted when `include_content=false` or scope-limited)
  - `relationship_hints` (optional), e.g.:
    - `supports`
    - `targets`
    - `results_in`
    - `records_event_for`
    - `supersedes`

#### Policy/scope behavior

- Object visibility is filtered by agent scope.
- Sensitive fields MAY be redacted by field-level scope rules.
- Not-found and forbidden handling should avoid leaking restricted object existence where policy requires concealment.

#### Error categories

- `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `temporarily_unavailable`, `internal_error`

#### Audit/log expectations

- Log read event with agent identity, workspace, object id, timestamp, and request id.
- Log redaction/scope decision metadata where policy requires auditable minimization.

---

### 2) `list_objects`

#### Purpose

Return a bounded, paginated list of objects discoverable in effective scope.

#### Required inputs

- `workspace` (string)

#### Optional inputs

- `class` (one of `raw|structured|proposals|logs`)
- `status` (string; class-valid statuses)
- `created_after` / `created_before` (ISO 8601)
- `updated_after` / `updated_before` (ISO 8601)
- `title_contains` (string)
- `tags_any` (array of strings)
- `ids` (array of explicit IDs for bounded batch fetch)
- `sort_by` (`created_at|updated_at|title|status`, baseline minimum)
- `sort_order` (`asc|desc`)
- `limit` (integer)
- `cursor` (opaque string)
- `include_content` (boolean, recommended default `false`)
- `include_relationship_hints` (boolean)

#### Response shape (`data`)

- `items` (array of object summaries/records)
  - each item includes: `id`, `class`, `workspace`, `status`, metadata subset
  - optional: `content` if requested and permitted
  - optional: `relationship_hints`

`meta.pagination` SHOULD include:

- `limit`
- `next_cursor` (nullable)
- `has_more` (boolean)

`meta.filter_applied` SHOULD echo normalized effective filters.

#### Pagination / limit behavior

- Cursor-based pagination is recommended for stable bounded traversal.
- If `limit` omitted, apply deployment default.
- If `limit` exceeds max, either clamp with explicit `meta.limit_clamped=true` or reject with `limit_exceeded` (implementation policy must be consistent and documented).

#### Policy/scope behavior

- Return only objects visible in effective scope.
- Total counts MAY be omitted or bucketed when exposing them would leak restricted object presence.

#### Error categories

- `invalid_request`, `unauthorized`, `forbidden`, `limit_exceeded`, `rate_limited`, `temporarily_unavailable`, `internal_error`

#### Audit/log expectations

- Log query event with agent identity, workspace, normalized filter set, result count, and request id.

---

### 3) `get_traceability_links`

#### Purpose

Return direct traceability links for one or more seed object IDs without requiring unbounded graph traversal.

#### Required inputs

- `workspace` (string)
- `seed_ids` (array of object ids, non-empty)

#### Optional inputs

- `link_types` (array subset of `supports|targets|results_in|records_event_for|supersedes`)
- `direction` (`outbound|inbound|both`, default `both`)
- `max_hops` (integer; baseline recommended max `1`, optionally `2`)
- `limit` (integer; total returned links bound)
- `cursor` (opaque string for paged link sets)
- `include_node_summaries` (boolean)

#### Response shape (`data`)

- `seed_ids` (echo)
- `links` (array)
  - `from_id`
  - `to_id`
  - `type`
  - `direction`
  - optional `evidence`/`notes`
- `nodes` (optional summary map when `include_node_summaries=true`)
- `truncation` (optional details when bounded results truncate reachable links)

#### Pagination / limit behavior

- Must remain bounded by `limit` and/or implementation max link cap.
- Return cursor for continued traversal if more links exist in-scope.
- Must not silently degrade into unbounded global graph walks.

#### Policy/scope behavior

- Only return links where both endpoint visibility and link disclosure policy permit exposure.
- If one endpoint is hidden, implementations may omit link or return redacted endpoint token per policy.

#### Error categories

- `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `limit_exceeded`, `temporarily_unavailable`, `internal_error`

#### Audit/log expectations

- Log traceability query with seed IDs, link types, bounds, and request id.

---

### 4) `submit_proposal`

#### Purpose

Create a new proposal object for human-governed review; never directly publish canonical structured changes.

#### Required inputs

- `workspace` (string)
- `proposal`
  - `id` (string; client-supplied or service-generated policy)
  - `class` (must be `proposals`)
  - `created_by` (stable agent identity)
  - `status` (initial status; usually `draft` or `under_review` per policy)
  - `target_ids` (non-empty array)
  - `title` (string)
  - `summary` (string)
  - `rationale` (string)
  - `intended_effect` (string)

#### Optional inputs

- `content_patch` / `proposed_content` (implementation-defined structured payload)
- `supporting_raw_ids` (array)
- `requested_reviewers` (array of reviewer identities)
- `idempotency_key` (string)
- `attachments` (bounded references)

#### Response shape (`data`)

- `proposal`
  - canonical stored proposal metadata + accepted payload fields
- `status` (current proposal status)
- `review_path` (optional workflow hints)

`meta` SHOULD include any server-normalized fields and validation warnings.

#### Policy/scope behavior

- Agent must have proposal-submit authority in target workspace.
- `target_ids` must be within allowed scope/class rules.
- Submission may be accepted as `draft` pending policy checks, or directly set to `under_review` by workflow policy.
- Submission cannot materialize direct structured canonical updates in this operation.

#### Error categories

- `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `limit_exceeded`, `rate_limited`, `temporarily_unavailable`, `internal_error`

#### Audit/log expectations

- Log proposal submission event with proposal id, target IDs, agent identity, request id, and timestamp.
- Record provenance pointers sufficient to trace proposal -> review decision -> applied outcome.

---

### 5) `get_proposal_status`

#### Purpose

Return lifecycle status and review-facing summary for a proposal.

#### Required inputs

- `workspace` (string)
- `proposal_id` (string)

#### Optional inputs

- `include_review_history` (boolean)
- `include_result_links` (boolean; include `results_in` where available)
- `include_log_refs` (boolean)

#### Response shape (`data`)

- `proposal`
  - `id`
  - `status` (`draft|under_review|accepted|rejected|withdrawn`)
  - `created_at`
  - `created_by`
  - `target_ids`
  - `summary`
- `review_history` (optional)
  - decision entries with actor, timestamp, decision, notes
- `result_links` (optional)
  - structured IDs produced when accepted and applied
- `log_refs` (optional)
  - relevant log object IDs or event references

#### Policy/scope behavior

- Subject to same workspace visibility and field redaction policies.
- Review details may be partially hidden for scoped agents.

#### Error categories

- `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `temporarily_unavailable`, `internal_error`

#### Audit/log expectations

- Log status-query event with proposal id, agent identity, and request id.

## MCP-style tool mapping examples

These examples show one valid MCP-style expression of this contract semantics.

### Tool definitions (illustrative)

- `noema.get_object_by_id`
  - args: `{ workspace, id, include_content?, include_relationship_hints? }`
- `noema.list_objects`
  - args: `{ workspace, class?, status?, created_after?, created_before?, updated_after?, updated_before?, tags_any?, limit?, cursor? }`
- `noema.get_traceability_links`
  - args: `{ workspace, seed_ids, link_types?, direction?, max_hops?, limit?, cursor? }`
- `noema.submit_proposal`
  - args: `{ workspace, proposal, idempotency_key? }`
- `noema.get_proposal_status`
  - args: `{ workspace, proposal_id, include_review_history?, include_result_links?, include_log_refs? }`

### MCP mapping notes

- MCP transport/tool naming does not change operation semantics.
- MCP responses SHOULD preserve the same success/error envelope conventions.
- Scope enforcement and audit behavior are identical to non-MCP surfaces.

## Equivalent bounded API mapping examples

These examples show equivalent HTTP-style endpoint mappings for the same semantics.

- `GET /v1/workspaces/{workspace}/objects/{id}` -> `get_object_by_id`
- `GET /v1/workspaces/{workspace}/objects` -> `list_objects`
- `POST /v1/workspaces/{workspace}/traceability-links:query` -> `get_traceability_links`
- `POST /v1/workspaces/{workspace}/proposals` -> `submit_proposal`
- `GET /v1/workspaces/{workspace}/proposals/{proposal_id}/status` -> `get_proposal_status`

API transport notes:

- Query params/body schemas should map 1:1 to operation input fields.
- Responses should preserve shared success/error envelope semantics.
- Endpoint style may vary (REST/RPC), but semantics and boundaries must remain equivalent.

## Explicit non-goals and deferred concerns

This slice does **not** define or implement:

- production auth/user provisioning or credential lifecycle
- deployment/runtime hardening
- full maintainer/compiler automation flows
- direct agent authority to publish canonical structured state
- global query language standard beyond these baseline operation shapes
- domain-specific extensions or personal-only policy framing

## Drift-check statement

This contract intentionally preserves existing Noema semantics:

- no redefinition of object classes (`raw`, `structured`, `proposals`, `logs`)
- no redefinition of metadata profile semantics
- no redefinition of relationship/traceability semantics
- no redefinition of index/catalog semantics
- no change to Phase 3 human-client semantics
- no collapse of proposal submission into canonical publication authority
- no MCP-only coupling

## Next-slice pointer

After this Phase 4 Slice 2 surface-contract definition, the next planned slice remains within Phase 4:

- **Phase 4 Slice 3 — baseline operation-state semantics (proposal state transitions, review-decision/result-link contracts, and policy-profile presets) while preserving human-governed canonical publication.**
