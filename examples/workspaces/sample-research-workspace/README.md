# Sample Research Workspace Layout

This example is intentionally lightweight. It demonstrates separation of core policy and organization axes without implying final implementation details.

## Included folders

- `domain/` - what the knowledge is about
- `profiles/` - how the knowledge is used
- `workspaces/` - concrete project/workspace instances
- `policies/` - visibility and authority definitions

This sample is for reference only and should not be treated as production data.

## Phase 5 Slice 1 maintainer rebuild usage

From repository root, run the deterministic local maintainer baseline tool:

- Rebuild one workspace:
  - `python -m packages.noema_maintainer.cli --workspace ai-literature-mapping`
- Rebuild all workspaces under this sample layout:
  - `python -m packages.noema_maintainer.cli`

Optional flags:

- `--repo-root <path>` to point at a different Noema repository root.
- `--workspaces-root <path>` to point at a different workspaces directory root.

The tool scans Markdown objects with YAML frontmatter from `raw/`, `structured/`, `proposals/`, and `logs/`, validates bounded baseline checks, and rebuilds deterministic projection outputs plus `projection/build-report.json` for each workspace.
