# Noema Phase 9 Tranche 3A — External Agent Tool Contract and Local Adapter Harness

## Purpose

Phase 9 Tranche 3A adds a local, Python-standard-library external adapter surface over the accepted Noema service-core and operator surfaces.

The product center is:

```text
Accepted Noema operations → Stable external tool names → JSON schemas/specs → Local deterministic invocation → Manifest/CLI harness
```

This tranche is intentionally bounded. It is not a new Noema authority layer, not an MCP server, not an HTTP server change, and not an Obsidian integration. External agents interact with Noema through stable operation contracts that call accepted Noema service/operator functions directly.

## Tool catalog

The adapter exposes exactly 11 tools:

| Tool | Category | Side-effect class | Backing operation |
| --- | --- | --- | --- |
| `noema.object.get` | service | `read_only` | `packages.noema_service.core.get_object_by_id` |
| `noema.objects.list` | service | `read_only` | `packages.noema_service.core.list_objects` |
| `noema.operator.handoff.build` | operator | `read_only` | `packages.noema_operator.handoffs.build_operator_handoffs` over the accepted 2C bundle |
| `noema.operator.navigation.target.resolve` | operator | `read_only` | accepted 2C navigation registry resolution |
| `noema.operator.navigation.targets.list` | operator | `read_only` | `packages.noema_operator.navigation.build_navigation_bundle` |
| `noema.operator.projections.build` | operator | `generated_projection_write` | `packages.noema_operator.projections.build_operator_projections` |
| `noema.operator.route.show` | operator | `read_only` | accepted 2C route registry lookup |
| `noema.operator.routes.list` | operator | `read_only` | accepted 2C route model |
| `noema.proposal.status` | service | `read_only` | `packages.noema_service.core.get_proposal_status` |
| `noema.proposal.submit` | service | `proposal_write` | `packages.noema_service.core.submit_proposal` |
| `noema.traceability.links` | service | `read_only` | `packages.noema_service.core.get_traceability_links` |

Tool names are sorted lexicographically in catalog, manifest, and JSON CLI output.

## Side-effect classes

Allowed side-effect classes are exactly:

- `read_only`
- `proposal_write`
- `generated_projection_write`

`noema.proposal.submit` is the only `proposal_write` tool. It creates a proposal only through the accepted service-core `submit_proposal` operation. It does not approve, reject, apply, publish, mutate canonical structured objects, or write logs except for service-core behavior already accepted for proposal submission.

`noema.operator.projections.build` is the only `generated_projection_write` tool. It writes generated operator projection files only. It does not mutate source records or proposal review/apply state.

All other tools are `read_only`.

## Argument notes

`noema.proposal.submit` requires the service-core proposal fields explicitly exposed by the external contract:

- `repo_root`
- `workspace`
- `proposal_id`
- `title`
- `summary`
- `rationale`
- `intended_effect`
- `target_ids`
- optional `proposed_by`
- optional `evidence_ids`
- optional `status`
- optional `created_at`

The adapter maps:

- `proposal_id` → `id`
- `proposed_by` or `external_adapter` → `created_by`
- `status` or `draft` → `status`
- `evidence_ids` → `supporting_raw_ids`
- `rationale` → `rationale`
- `intended_effect` → `intended_effect`
- `created_at` → `created_at` only when supplied

The adapter does not synthesize `intended_effect` from `summary` and does not bypass service-core submission.

`noema.traceability.links` exposes one public seed argument, `object_id`, and maps it directly to `seed_ids=[object_id]` for the accepted service-core operation. It does not infer or expose multiple seeds in 3A.

`noema.operator.navigation.target.resolve` supports `repo-relative-path`, `workspace-relative-path`, `file-uri`, `markdown-link`, and `path`. Manifest and list outputs never include absolute local paths. `format=path` may return a local absolute path only because it was explicitly requested. The tool never opens or executes anything.

## Normalized invocation envelope

Every invocation returns a deterministic adapter envelope.

Success:

```json
{
  "ok": true,
  "tool": "<tool-name>",
  "data": {},
  "error": null,
  "meta": {
    "adapter_version": "external-adapter-v1",
    "side_effect_class": "read_only",
    "authority": "bounded_adapter_over_accepted_noema_surfaces"
  }
}
```

Error:

```json
{
  "ok": false,
  "tool": "<tool-name-or-null>",
  "data": null,
  "error": {
    "code": "backing_operation_error",
    "message": "Accepted backing operation returned an error.",
    "details": {}
  },
  "meta": {
    "adapter_version": "external-adapter-v1",
    "side_effect_class": "unknown",
    "authority": "bounded_adapter_over_accepted_noema_surfaces"
  }
}
```

The adapter does not copy service-core `request_id` or `timestamp` fields into external envelopes. If a service-core operation returns `ok=false`, the adapter converts it to `backing_operation_error` with deterministic details such as backing operation, category, code, and message.

## Validation errors

The adapter validates locally before invocation and returns deterministic error envelopes for:

- `unknown_tool`
- `missing_required_argument`
- `invalid_argument_type`
- `invalid_argument_value`
- `unexpected_argument`
- `invalid_argument_combination`
- `backing_operation_error`

Local validation rejects unknown tool names, missing required arguments, wrong primitive/list types, unsupported enum values, extra arguments, non-positive limits, and `noema.operator.handoff.build` requests that do not supply exactly one selector.

## Manifest schema

`emit-manifest` returns a deterministic manifest with:

- `schema_version: "noema-external-tool-manifest-v1"`
- `adapter_version: "external-adapter-v1"`
- `authority: "bounded_adapter_over_accepted_noema_surfaces"`
- `tools`
- `side_effect_classes`
- `categories`
- `non_goals`
- `generated_policy`

Manifest generation does not require a repo, workspace, HTTP server, `.obsidian` directory, or generated projection files. It includes no timestamps, no request ids, no absolute local paths, and no repo-specific state.

## CLI commands

List tools:

```bash
python -m packages.noema_external_adapter.cli list-tools
python -m packages.noema_external_adapter.cli list-tools --category service --format json
python -m packages.noema_external_adapter.cli list-tools --side-effect read_only --format json
```

Describe one tool:

```bash
python -m packages.noema_external_adapter.cli describe-tool --tool noema.objects.list
python -m packages.noema_external_adapter.cli describe-tool --tool noema.objects.list --format json
```

Emit manifest:

```bash
python -m packages.noema_external_adapter.cli emit-manifest
```

Invoke a tool:

```bash
python -m packages.noema_external_adapter.cli invoke-tool --tool noema.objects.list --args-json '{"repo_root": ".", "workspace": "ws"}'
python -m packages.noema_external_adapter.cli invoke-tool --request-json '{"tool": "noema.objects.list", "arguments": {"repo_root": ".", "workspace": "ws"}}'
```

Invocation prints normalized JSON envelopes. The CLI exits `0` when `ok` is true and nonzero when `ok` is false. Normal CLI errors avoid tracebacks, including malformed JSON, missing/extra/wrong-type arguments, unsupported values, and backing operation errors.

## Determinism and authority boundary

The adapter introduces no timestamps, UUIDs, request ids, or nondeterministic fields. CLI JSON uses sorted keys. Tool ordering, manifest ordering, validation errors, and normalized metadata are stable.

The adapter is MCP-ready in shape but does not implement MCP in 3A. Later MCP/native adapters can bind to this contract without redefining Noema semantics.

## Explicitly out of scope

This tranche does not implement:

- MCP server or protocol transport;
- JSON-RPC daemon;
- HTTP adapter changes;
- native web UI;
- auth, TLS, CORS, or public deployment hardening;
- Obsidian plugin, Obsidian API integration, Obsidian URI generation, or `.obsidian` config writes;
- open-navigation-target execution;
- proposal approval/rejection/apply commands;
- canonical object mutation;
- direct proposal file writing outside accepted service-core `submit_proposal`;
- direct log mutation;
- new service-core semantic operations;
- broad query/search/RAG/chat behavior;
- arbitrary shell execution or open helper execution.

## Known limits

The adapter is local and stdlib-only. It assumes the caller has local filesystem access to a Noema repo root. It exposes only accepted service/operator functions and intentionally does not add auth, network transport, multi-seed traceability, broader search, or new governance semantics.
