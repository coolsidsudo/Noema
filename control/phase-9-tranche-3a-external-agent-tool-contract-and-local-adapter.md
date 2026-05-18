# Phase 9 Tranche 3A Control Summary — External Agent Tool Contract and Local Adapter Harness

## Purpose

Implement a substantive but bounded external-agent integration layer over accepted Noema service-core and operator surfaces: stable tool contract, tool specs/schemas, deterministic local adapter dispatcher, manifest emission, CLI list/describe/invoke harness, tests, and documentation.

## Implemented scope

- Add `packages/noema_external_adapter/contract.py` for the fixed 11-tool catalog, argument specs, side-effect classes, validation error codes, and catalog lookup.
- Add `packages/noema_external_adapter/adapter.py` for explicit dispatch to accepted service/operator functions and normalized deterministic JSON envelopes.
- Add `packages/noema_external_adapter/manifest.py` for deterministic manifest generation with no repo state, timestamps, or absolute local paths.
- Add `packages/noema_external_adapter/cli.py` for `list-tools`, `describe-tool`, `emit-manifest`, and `invoke-tool`.
- Add tests for catalog/manifest determinism, validation, invocation, CLI behavior, service-core envelope unwrapping, proposal-only write behavior, generated projection write classification, and path-resolution boundaries.
- Add system documentation for the Tranche 3A external adapter contract and local harness.

## Tool catalog

3A exposes exactly:

- `noema.object.get`
- `noema.objects.list`
- `noema.operator.handoff.build`
- `noema.operator.navigation.target.resolve`
- `noema.operator.navigation.targets.list`
- `noema.operator.projections.build`
- `noema.operator.route.show`
- `noema.operator.routes.list`
- `noema.proposal.status`
- `noema.proposal.submit`
- `noema.traceability.links`

Side-effect class assignments are exactly:

- `noema.proposal.submit` → `proposal_write`
- `noema.operator.projections.build` → `generated_projection_write`
- all other tools → `read_only`

## Boundaries preserved

- No MCP server or MCP protocol transport.
- No HTTP adapter changes.
- No service-core semantic changes.
- No proposal approval/rejection/apply behavior.
- No canonical object mutation or direct log mutation.
- No direct proposal file writing outside accepted service-core `submit_proposal`.
- No Obsidian plugin/API/config writes, `.obsidian` dependency, or Obsidian URI generation.
- No native web UI, auth, TLS, CORS, deployment hardening, or broad search/RAG/chat behavior.
- No arbitrary shell execution or open-helper execution.
- `control/development-tracker.md` remains intentionally unchanged for this implementation step.

## Determinism and error handling

- Adapter envelopes do not include timestamps, UUIDs, request ids, or copied service-core `request_id`/`timestamp` values.
- Service-core `ok=false` responses are converted to deterministic external `backing_operation_error` envelopes with selected backing operation/category/code/message details.
- CLI invocation failures print deterministic `ok=false` JSON envelopes and return nonzero without tracebacks.
- Manifest/list/describe operations require no repo, workspace, HTTP server, `.obsidian`, or generated projection files.

## Testing plan

Required verification:

```bash
pytest -q tests/test_noema_service.py tests/test_noema_service_http.py
pytest -q tests/test_noema_operator_projections.py tests/test_noema_operator_review_packets.py tests/test_noema_operator_review_projection.py tests/test_noema_operator_navigation.py tests/test_noema_operator_handoffs.py tests/test_noema_operator_open_helpers.py
pytest -q tests/test_noema_external_adapter_contract.py tests/test_noema_external_adapter_invocation.py tests/test_noema_external_adapter_cli.py
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

## Next-step pointer

After implementation review acceptance, tracker synchronization should remain a tiny final follow-up commit unless the reviewer directs otherwise. Later MCP/native adapters may bind to this contract without changing Noema authority semantics.
