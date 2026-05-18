# Noema Phase 9 Tranche 2C — Operator Navigation and Handoff Workbench

## Purpose

Phase 9 Tranche 2C adds a deterministic operator navigation and handoff workbench over existing operator projections, review cockpit pages, review packets, and workspace source records.

The product center is:

```text
Targets → Routes → Handoffs → Markdown workbench → Manifest → CLI resolve/open helpers
```

Navigation targets, routes, handoffs, and the machine-readable manifest are derived read-only convenience layers. They do not approve, reject, apply, mutate, publish, or create authority.

## Generated location

The existing operator projection command now also writes navigation workbench files under:

```text
<workspace-root>/projection/operator/navigation/
```

Generated files:

- `index.md`
- `targets.md`
- `routes.md`
- `handoffs.md`
- `open-commands.md`
- `manifest.json`

The parent operator index links to both:

- `./review/index.md`
- `./navigation/index.md`

## Rebuild command

```bash
python -m packages.noema_operator.cli build-projections --repo-root . --workspace examples/workspaces/sample-research-workspace/workspaces/ai-literature-mapping
```

The command remains repo-backed and filesystem-local. It does not require an HTTP server, `.obsidian`, an Obsidian API, or any Obsidian plugin/configuration.

## Navigation targets

A navigation target is a stable local reference to a generated operator page, generated review page, review packet page, generated navigation page, generated manifest, or workspace-scoped source record.

Target ids include:

- `operator:index`, `operator:objects`, `operator:proposals`, `operator:recent`
- `review:index`, `review:queue`, `review:attention`, `review:readiness`, `review:recovery`
- `review:packet:<safe-proposal-id>`
- `source:<record-id>`
- `navigation:index`, `navigation:targets`, `navigation:routes`, `navigation:handoffs`, `navigation:open-commands`, `navigation:manifest`

Every target carries a repo-relative path. Workspace-relative paths are included only when the path is actually inside the workspace root, so source records under repo-root class directories do not emit misleading `../../` paths.

Target collisions are deterministic: ambiguous ids are diagnosed and are not silently overwritten.

## Operator routes

Routes are deterministic operator workflow guidance over target ids, not policy decisions. Required base routes are:

- `route:workspace-overview`
- `route:proposal-triage`
- `route:blocked-review`
- `route:ready-review`
- `route:accepted-apply-audit`
- `route:recovery-audit`

Packet routes use:

- `route:packet-review:<safe-proposal-id>`

Routes include entry target, ordered target ids, recommended next targets, related packet/source ids, attention summary, checklist items, and deterministic diagnostics. Source-specific routes are intentionally not generated in 2C v1.

## Operator handoffs

Handoffs are derived guidance bundles compiled from routes and review packet state. They are not durable authority records.

Base handoffs are:

- `handoff:workspace-overview`
- `handoff:proposal-triage`
- `handoff:blocked-review`
- `handoff:ready-review`
- `handoff:accepted-apply-audit`
- `handoff:recovery-audit`

Packet handoffs use:

- `handoff:packet-review:<safe-proposal-id>`

Handoffs include primary target, route id, related targets/routes/packets/source records, blockers, warnings, next steps, summary, and diagnostics. Source-specific handoffs are intentionally not generated in 2C v1.

## Manifest schema

`manifest.json` is a deterministic generated bridge for future adapters or UIs. It is not an adapter itself and is not authoritative.

Top-level keys:

- `schema_version: "operator-navigation-workbench-v1"`
- `authority: "derived_non_authoritative"`
- `workspace_id`
- `targets`
- `routes`
- `handoffs`
- `diagnostics`

The manifest uses sorted keys, stable ordering, no timestamps, and no absolute local filesystem paths.

Diagnostics use deterministic codes including missing/unresolved/ambiguous target, route, handoff, and open-helper diagnostics. Diagnostics are visibility signals only.

## CLI commands

List and resolve targets:

```bash
python -m packages.noema_operator.cli list-navigation-targets --repo-root . --workspace <workspace>
python -m packages.noema_operator.cli resolve-navigation-target --repo-root . --workspace <workspace> --target review:queue --format repo-relative-path
```

List and inspect routes:

```bash
python -m packages.noema_operator.cli list-operator-routes --repo-root . --workspace <workspace>
python -m packages.noema_operator.cli show-operator-route --repo-root . --workspace <workspace> --route route:proposal-triage
```

Build handoffs without writing source records:

```bash
python -m packages.noema_operator.cli build-operator-handoff --repo-root . --workspace <workspace> --route route:proposal-triage
python -m packages.noema_operator.cli build-operator-handoff --repo-root . --workspace <workspace> --target review:packet:<safe-proposal-id>
```

All commands return `0` on success and non-zero for invalid kind, format, target, route, or handoff inputs. Unknown target/route/handoff errors include deterministic suggestions when feasible and avoid tracebacks for normal invalid input.

## Open-helper safety model

`open-navigation-target` is a final-mile convenience only:

```bash
python -m packages.noema_operator.cli open-navigation-target --repo-root . --workspace <workspace> --target review:queue --mode file --print
python -m packages.noema_operator.cli open-navigation-target --repo-root . --workspace <workspace> --target review:queue --mode file --execute
```

Rules:

- Default behavior is print/resolve only.
- Execution requires explicit `--execute`.
- Execution uses tokenized local commands and never `shell=True`.
- Arbitrary command strings and network URLs are not accepted.
- Target paths must resolve inside the repo root.
- Tests use fake execution adapters and do not launch GUI apps.
- Obsidian URI mode is not implemented in 2C v1.

Opening a projection or source file does not confer Noema authority.

## Explicitly out of scope

This tranche does not implement:

- Obsidian plugin, API integration, URI mode, or `.obsidian` config writes;
- mandatory Obsidian dependency;
- MCP;
- native web UI;
- auth, TLS, CORS, or public deployment hardening;
- proposal approval or rejection commands;
- canonical apply command or canonical object mutation;
- proposal/log mutation;
- new service-core operations or semantic changes;
- HTTP adapter changes;
- broad query/search/RAG/chat behavior;
- source-specific routes or source-specific handoffs.

## Known limits

The workbench derives from explicit workspace records, generated projection paths, and review packet metadata. It does not infer relationships from freeform Markdown bodies. Navigation and handoff records are regenerated views, not canonical Noema objects.
