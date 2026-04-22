# Phase 8 Slice 1 — Maintainer Loop Contract Baseline (Accepted)

## Status

- Slice: Phase 8 Slice 1
- State: Accepted
- Previous accepted slice: NOE-68 — development-plan Phase 8 expansion accepted

## Slice objective

Establish the minimum maintainer loop contract that makes Noema's maintainer/compiler role concrete and reviewable while preserving proposal/review/apply boundaries and class-lane authority separation.

## Implemented scope in this slice

1. Stable seam contract baseline for ingest, compile, lint/coherence/contradiction surfacing, proposal/review handoff, and query-support.
2. Explicit read/write class-lane posture across `raw/`, `structured/`, `proposals/`, and `logs/`.
3. Normative default posture: canonical-impacting structured edits emit proposals by default.
4. Normative exception posture: direct canonical apply remains explicit, auditable, reversible, and policy-gated.
5. Bounded conformance guidance to make contract violations inspectable in later slices.

## Boundaries preserved

- No full proposal payload/evidence/provenance schema defined here (reserved for Phase 8 Slice 2).
- No full maintainer log/event schema defined here (reserved for Phase 8 Slice 3).
- No broad executable agent-platform/runtime expansion introduced.
- No canonical authority broadening beyond explicit exception-gated posture.

## Drift-check statement

This slice preserves Noema's maintainer/compiler/curator center and does not collapse raw/structured/proposal/log lanes into generic chat/RAG behavior.

## Next-slice pointer

Proposed direct continuation: **Phase 8 Slice 2 — proposal payload, evidence, and provenance contract**.
