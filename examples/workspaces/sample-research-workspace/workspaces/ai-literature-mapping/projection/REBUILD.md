# Rebuild Process (Deterministic, Baseline)

This sample projection is file-friendly and intentionally lightweight.

## Inputs

- Workspace object metadata from `raw/`, `structured/`, `proposals/`, and `logs/`
- Relationship pointers (`supports`, `targets`, `results_in`, `records_event_for`) where available

## Deterministic rebuild steps

1. Gather workspace records for a single workspace ID.
2. Sort rows by:
   - class manifests: `id` ascending
   - proposal queue pending section: priority then `created_at` descending
   - recent changes: timestamp descending
3. Regenerate:
   - `browse/by-class-*.md`
   - `review/proposal-queue.md`
   - `logs/recent-changes.md`
4. Commit regenerated files together.

## Baseline rules

- Do not alter class semantics.
- Do not treat projection files as authority state.
- Ensure every queue row links back to canonical object IDs.
