# Noema Phase 9 Slice 1C — Minimal HTTP adapter over the accepted service core

## Purpose

Phase 9 Slice 1C exposes the accepted Noema service-core operations through a local, single-node, Python-standard-library HTTP adapter.

This slice is intentionally thin: it does not define new service semantics, a new object model, a new policy layer, an operator UI, an MCP server, auth, CORS, TLS, Obsidian runtime behavior, or public deployment hardening. The service core remains the authority for operation behavior and envelopes.

## Route matrix

| Method | Route | Core operation | Success status | Notes |
| --- | --- | --- | --- | --- |
| `GET` | `/v1/workspaces/{workspace}/objects/{id}` | `get_object_by_id` | `200` | Gets one workspace-scoped object. |
| `GET` | `/v1/workspaces/{workspace}/objects` | `list_objects` | `200` | Lists workspace-scoped objects with bounded filters and cursor pagination. |
| `POST` | `/v1/workspaces/{workspace}/traceability-links:query` | `get_traceability_links` | `200` | Queries one-hop traceability links using a JSON object body. |
| `POST` | `/v1/workspaces/{workspace}/proposals` | `submit_proposal` | `201` | Submits a direct proposal payload and writes repo-backed proposal Markdown. |
| `GET` | `/v1/workspaces/{workspace}/proposals/{proposal_id}/status` | `get_proposal_status` | `200` | Gets proposal lifecycle/status summary. |

## Run command

```bash
python -m packages.noema_service.cli --repo-root . --host 127.0.0.1 --port 8765
```

Defaults:

- `--repo-root .`
- `--host 127.0.0.1`
- `--port 8765`

`repo_root` is configured once at server startup and is not supplied per request.

## JSON envelope preservation

The adapter preserves service-core response envelopes unchanged. It does not wrap successful or core-error responses in another JSON object.

Adapter-generated errors use the same envelope shape:

```json
{
  "ok": false,
  "operation": "http_request",
  "request_id": "req_<uuid>",
  "timestamp": "2026-05-17T00:00:00Z",
  "error": {
    "category": "not_found",
    "code": "ROUTE_NOT_FOUND",
    "message": "Route not found.",
    "retryable": false,
    "details": {}
  }
}
```

All handled responses are JSON with `Content-Type: application/json; charset=utf-8` and `Content-Length`.

## Strict parsing behavior

Path handling:

- The adapter uses `urlsplit(...)` to separate path and query.
- The raw path is split on `/` before percent-decoding.
- Only route variables are percent-decoded.
- Empty decoded path variables are rejected.
- Decoded path variables containing `/` or `\` are rejected.

Query handling:

- Query strings are parsed with `parse_qs(..., keep_blank_values=True)`.
- Duplicate query parameters are rejected.
- Unknown query parameters are rejected.
- Optional string query parameters may not be empty.
- Boolean query values must be exactly `true` or `false`.
- Integer query values must parse as integers; semantic ranges remain core-owned.
- `ids` is a single comma-separated query value with whitespace-trimmed non-empty tokens.

JSON body handling:

- POST requests must include `Content-Length`.
- Maximum request body size is 1 MiB.
- Malformed JSON is rejected.
- JSON bodies must be objects.
- Unknown JSON fields are rejected.
- Present fields with wrong JSON types are rejected before calling the core.
- Core-owned semantic validation is preserved; for example, `get_traceability_links(limit=501)` still returns the accepted core `invalid_request` / `INVALID_LIMIT` envelope.

Unsupported methods:

- `PUT`, `PATCH`, and `DELETE` return JSON `METHOD_NOT_ALLOWED` errors.
- The adapter avoids `BaseHTTPRequestHandler` HTML error pages for handled adapter paths.

## HTTP status mapping

For service-core envelopes:

| Envelope state/category | HTTP status |
| --- | ---: |
| `ok: true` | `200` |
| `submit_proposal` with `ok: true` | `201` |
| `invalid_request` | `400` |
| `unauthorized` | `401` |
| `forbidden` | `403` |
| `not_found` | `404` |
| `conflict` | `409` |
| `limit_exceeded` | `400` |
| `rate_limited` | `429` |
| `temporarily_unavailable` | `503` |
| `internal_error` | `500` |
| unknown error category | `500` |

For adapter-generated errors:

| Error code | HTTP status |
| --- | ---: |
| `ROUTE_NOT_FOUND` | `404` |
| `METHOD_NOT_ALLOWED` | `405` |
| `REQUEST_BODY_TOO_LARGE` | `400` |
| Other parse, body, query, or path validation errors | `400` |

## Examples

### Get object by id

```bash
curl 'http://127.0.0.1:8765/v1/workspaces/ws-a/objects/structured-1'
```

Optional query parameters:

- `include_content=true|false`, default `true`
- `include_relationship_hints=true|false`, default `false`

### List objects

```bash
curl 'http://127.0.0.1:8765/v1/workspaces/ws-a/objects?class=structured&status=active&limit=10&sort_by=id'
```

Optional query parameters:

- `class`
- `status`
- `ids`, comma-separated
- `title_contains`
- `limit`
- `cursor`
- `sort_by`
- `sort_order`
- `include_content=true|false`, default `false`
- `include_relationship_hints=true|false`, default `false`

### Query traceability links

```bash
curl -X POST 'http://127.0.0.1:8765/v1/workspaces/ws-a/traceability-links:query' \
  -H 'Content-Type: application/json' \
  --data '{"seed_ids":["proposal-1"],"direction":"outbound","link_types":["targets","results_in"],"limit":10}'
```

Allowed body fields:

- `seed_ids`, required `list[str]`
- `link_types`, optional `list[str]`
- `direction`, optional string
- `limit`, optional integer
- `include_node_summaries`, optional bool

### Submit proposal

```bash
curl -X POST 'http://127.0.0.1:8765/v1/workspaces/ws-a/proposals' \
  -H 'Content-Type: application/json' \
  --data '{"id":"proposal-http","created_by":"agent-http","status":"draft","target_ids":["structured-1"],"title":"HTTP Proposal","summary":"Submitted through HTTP.","rationale":"Exercise adapter path.","intended_effect":"Prove proposal creation."}'
```

The body is the direct proposal payload. There is no `{"proposal": ...}` wrapper in this slice.

### Get proposal status

```bash
curl 'http://127.0.0.1:8765/v1/workspaces/ws-a/proposals/proposal-1/status'
```

Optional query parameters:

- `include_review_history=true|false`, default `false`
- `include_result_links=true|false`, default `true`
- `include_log_refs=true|false`, default `true`

## Explicitly out of scope

This slice does not implement:

- Obsidian plugin/runtime integration
- Obsidian projection generation
- operator UI
- MCP adapter
- auth/identity provisioning
- CORS
- TLS
- public network deployment hardening
- vector DB/RAG/query expansion
- recursive graph traversal
- canonical structured publication
- new object model
- third-party HTTP framework
- changes to maintainer runtime outside the service package

## Future Obsidian-hook compatibility preserved by this slice

No Obsidian hook is implemented now.

The HTTP adapter is useful for a later local bridge, companion process, or plugin because it remains local, repo-backed, workspace-aware, and deterministic. HTTP output stays in stable JSON envelopes, and proposal submissions continue to write ordinary repo-backed Markdown files that remain vault-friendly and inspectable with filesystem-based clients.

No plugin dependency is introduced. Noema remains the governed service/core authority. Obsidian remains a client, not the authority layer.
