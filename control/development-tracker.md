# Noema Development Tracker (Live Execution State)

This document is the **live, repo-authoritative execution tracker** for current implementation state.

It records current/near-term control state and is expected to change as slices are opened, reviewed, accepted, or re-queued.

## Scope and authority

`control/development-tracker.md` owns live status for:

- latest completed/accepted slice
- current under-review slice (if any)
- next queued/proposed slice
- brief execution continuity notes needed for immediate operator/reviewer context

It does **not** replace architecture/system-definition authority (`docs/noema-original-system-design.md`) or long-horizon roadmap authority (`control/development-plan.md`).

## Live status

- Latest completed/accepted tranche: **Phase 9 Tranche 2C — operator navigation and handoff workbench over projections and review packets**.
- Current under-review slice/tranche: **None**.
- Next queued/proposed tranche: **Phase 9 Tranche 3A — thin external adapter surface over the accepted bounded service/operator surfaces**.
- Phase 5 queue status: **Closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)**.

## Continuity notes

- Karpathy-first maintainer/compiler schema baseline remains authoritative in `docs/noema-maintainer-agent-skill-management-schema-v0.md`.
- Accepted architecture/system-definition baseline remains in `docs/noema-original-system-design.md`.
- Accepted long-horizon roadmap now includes Phase 9 in `control/development-plan.md`.
- Accepted Phase 9 architecture decision note now lives at `docs/noema-phase-9-architecture-decision-obsidian-client-and-service-surface.md`.
- Accepted Phase 9 Slice 1A reference doc now lives at `docs/noema-phase-9-slice-1a-repo-backed-read-service-core-baseline.md`.
- Accepted Phase 9 Slice 1A control summary now lives at `control/phase-9-slice-1a-repo-backed-read-service-core-baseline.md`.
- Accepted Phase 9 Slice 1B reference doc now lives at `docs/noema-phase-9-slice-1b-bounded-traceability-and-proposal-status-service-operations.md`.
- Accepted Phase 9 Slice 1B control summary now lives at `control/phase-9-slice-1b-bounded-traceability-and-proposal-status-service-operations.md`.
- Accepted Phase 9 Slice 1C added the local stdlib HTTP adapter over the five accepted service-core operations.
- Accepted Phase 9 Slice 1C reference doc now lives at `docs/noema-phase-9-slice-1c-minimal-http-adapter-over-service-core.md`.
- Accepted Phase 9 Slice 1C control summary now lives at `control/phase-9-slice-1c-minimal-http-adapter-over-service-core.md`.
- Accepted Phase 9 Tranche 2A added deterministic Markdown-native operator projections under `packages/noema_operator/`.
- Accepted Phase 9 Tranche 2B added a derived read-only operator review packet model and Markdown review cockpit over proposals, evidence, logs, apply/recovery visibility, readiness classifications, attention flags, and packet-specific next steps.
- Accepted Phase 9 Tranche 2B implementation commit before tracker sync: `780c5df4b9c80886d410145841cdb3148db489b5`.
- Accepted Phase 9 Tranche 2B verification reported:
  - `pytest -q tests/test_noema_service.py tests/test_noema_service_http.py` — 41 passed.
  - `pytest -q tests/test_noema_operator_projections.py tests/test_noema_operator_review_packets.py tests/test_noema_operator_review_projection.py` — 8 passed.
- Accepted Phase 9 Tranche 2C added a derived read-only operator navigation and handoff workbench over projections and review packets, including deterministic targets, routes, handoffs, Markdown workbench pages, manifest output, and CLI resolve/open helpers.
- Accepted Phase 9 Tranche 2C implementation commit before tracker sync: `b0559193e3f673ebceb92634837370106aadffe7`.
- Accepted Phase 9 Tranche 2C verification reported:
  - `pytest -q tests/test_noema_service.py tests/test_noema_service_http.py` — 41 passed.
  - `pytest -q tests/test_noema_operator_projections.py tests/test_noema_operator_review_packets.py tests/test_noema_operator_review_projection.py tests/test_noema_operator_navigation.py tests/test_noema_operator_handoffs.py tests/test_noema_operator_open_helpers.py` — 17 passed.
- Next work should move to Phase 9 Tranche 3A thin external adapter surface over the accepted bounded service/operator surfaces, without redefining Noema authority semantics or treating any client adapter as the authority layer.
- Accepted Phase 6 deployment and backup/restore semantics remain authoritative in:
  - `docs/noema-self-hosted-deployment-operations-baseline.md`
  - `docs/noema-backup-restore-operational-guidance-baseline.md`
- Accepted Phase 7 package/runtime substitution and conformance-expansion assets remain in `deploy/reference-single-node/`.

## Update rule

When live slice status changes, update this file first so control-state remains explicit and non-ambiguous.
