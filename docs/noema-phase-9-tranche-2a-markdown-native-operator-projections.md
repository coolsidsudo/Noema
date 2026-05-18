# Noema Phase 9 Tranche 2A — Markdown-Native Operator Projections

## Purpose

Phase 9 Tranche 2A adds deterministic, repo-backed Markdown operator projections over accepted Noema workspace state.

Operator projections are navigational/read-only surfaces for humans. They help an operator browse workspace objects, proposals, and recent activity from Obsidian or any Markdown-capable editor without turning the editor into the authority layer.

## Generated location

The operator projection generator writes workspace-local files under:

```text
<workspace-root>/projection/operator/
```

Generated files:

- `index.md`
- `objects.md`
- `proposals.md`
- `recent.md`

The generator does not write canonical object files and does not mutate `raw/`, `structured/`, `proposals/`, or `logs/` records.

## Rebuild command

Example:

```bash
python -m packages.noema_operator.cli build-projections --repo-root . --workspace examples/workspaces/sample-research-workspace/workspaces/ai-literature-mapping
```

`--workspace` may be a repo-relative path, an absolute workspace path, or a known workspace id under the existing sample workspace layout. When a path is supplied, the workspace directory basename is used as the workspace id. Scanned records are filtered by the accepted exact-match frontmatter `workspace` convention.

If the workspace path exists but no records match that workspace id, the generator still emits deterministic empty projections.

## Projection pages

`index.md` includes:

- workspace id and path
- object counts by class
- object counts by status
- links to `objects.md`, `proposals.md`, and `recent.md`

`objects.md` includes a stable table across accepted object classes:

```markdown
| id | class | status | title | updated_at | path |
```

`proposals.md` includes a stable proposal queue table:

```markdown
| proposal_id | status | title | target_ids | created_by | created_at | path |
```

`proposal_id` is rendered from `proposal_id` metadata when present and otherwise falls back to `id`. `target_ids` uses the accepted proposal metadata convention and renders a stable missing value when absent.

`recent.md` includes recent logs, proposals, and structured updates. ISO-like date strings are sorted lexicographically; missing dates sort last, including in descending recent lists.

## Determinism and rendering hygiene

Projection rendering is deterministic when source records are unchanged:

- no generated current-time timestamps
- stable sorting for all rows and counts
- stable missing-value rendering
- Markdown table cells escape pipes, newlines, and carriage returns
- relative Markdown links are used for object paths when feasible
- generated projection files are not scanned as knowledge objects

## Obsidian-friendly, not Obsidian-dependent

These files are Obsidian-friendly because they are plain Markdown files with ordinary Markdown links. They do not use Obsidian internals, `.obsidian` configuration, Obsidian APIs, or Obsidian URI helpers.

Any Markdown editor or filesystem-based review workflow can inspect the same projections.

## Authority boundary

Operator projections do not confer authority, do not replace service-core governance, and do not redefine object semantics. Authoritative state remains in Noema object metadata, proposal/review/apply conventions, logs, and the accepted service/repository surface.

Opening, editing, or viewing a projection file is not an approval action and does not publish canonical structured changes.

## Explicitly out of scope

This tranche does not implement:

- Obsidian plugin/runtime integration
- Obsidian URI/open helpers
- native web UI
- MCP adapter
- HTTP server dependency for projection generation
- auth, TLS, CORS, or deployment hardening
- canonical apply behavior
- proposal review decisions
- new service-core semantics
- broad query/search/RAG/chat behavior
