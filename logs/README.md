# Log Objects

This directory stores append-oriented operational records.

Examples:
- ingest activity logs
- review decisions
- maintenance workflow runs
- sync events

Conventions:
- Prefer append-only records.
- Keep timestamps and actor identity on every entry.
- Do not mix logs with structured canonical knowledge pages.

Minimum metadata expectation:
- `id`, `class: logs`, `created_at`, `created_by`, `workspace`, `status`

See `docs/noema-core-object-conventions.md` for baseline cross-class conventions.
