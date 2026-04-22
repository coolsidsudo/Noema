# Noema Maintainer Loop Contract Baseline V0

## Purpose

This document defines the **Phase 8 Slice 1 maintainer-loop contract baseline**.

It makes the maintainer/compiler/curator loop concrete and reviewable without broadening canonical authority, collapsing class lanes, or recentering Noema around generic chat/RAG behavior.

This is a **contract baseline** and bounded conformance target. It is not a full runtime platform specification.

## Scope boundary for Slice 1

This slice establishes:

1. seam contract for ingest, compile, lint/coherence/contradiction surfacing, proposal/review handoff, and query-support,
2. class-lane read/write posture across `raw/`, `structured/`, `proposals/`, and `logs/`,
3. default proposal-first canonical-impact posture,
4. bounded validation/check guidance for contract conformance.

This slice does **not** define full proposal payload/evidence/provenance schema (Phase 8 Slice 2) and does **not** define full maintainer log/event schema (Phase 8 Slice 3).

## Baseline references

This contract baseline is derived from and constrained by:

- `docs/noema-original-system-design.md` (Sections 6, 7, 13)
- `control/development-plan.md` (Phase 8 objective and Slice 1 scope)
- `control/development-tracker.md` (live queued continuation context)
- `docs/noema-maintainer-agent-skill-management-schema-v0.md` (maintainer rules, seams, authority posture)

## Contract anchors

### Anchor A — Maintainer role identity

The maintainer is a **compiler/curator** role, not a broad autonomous author.

Required implications:

- prioritize durable maintenance outputs over transient answer-only behavior,
- keep provenance and contradiction visibility explicit,
- preserve governed proposal/review separation by default.

### Anchor B — Class-lane separation is normative

`raw/`, `structured/`, `proposals/`, and `logs/` are distinct lanes with distinct authority and lifecycle semantics.

No seam may treat these lanes as interchangeable.

### Anchor C — Proposal-first canonical-impact posture

Canonical-impacting structured changes emit to `proposals/` by default.

Direct canonical apply is exceptional and requires explicit policy-gated authority plus audit trace.

### Anchor D — Query is maintenance-support

Query behavior supports maintenance and discovery but is not Noema's architectural center. Maintainer loop quality is judged by durable lane artifacts, not by transient response style.

## Seam contract baseline

## 1) Ingest seam

**Seam purpose**

Register new source material and maintenance impact without rewriting source truth.

**May read**

- `raw/` (existing source records)
- relevant `structured/` coverage map
- related `proposals/` (open items affected by ingest)
- prior ingest `logs/`

**May emit**

- `logs/` ingest records (actor, source identifier, workspace context, timestamp, outcome)
- optional `proposals/` when ingest reveals canonical-impacting follow-up that requires review

**Must not do by default**

- mutate canonical `structured/` directly,
- rewrite or silently normalize `raw/` content,
- suppress ingest uncertainty/ambiguity without trace.

## 2) Compile seam

**Seam purpose**

Produce or update compiled knowledge coverage from source-backed context.

**May read**

- `raw/` source content,
- affected `structured/` objects,
- active `proposals/` for overlapping objects,
- relevant maintenance `logs/`.

**May emit**

- `proposals/` for canonical-impacting structured edits (default),
- `logs/` compile-run records and affected-object trace,
- `structured/` canonical writes only if explicit apply authority is granted for the lane.

**Must not do by default**

- publish canonical-impacting `structured/` edits without proposal/review,
- leave claim support posture implicit,
- perform hidden authority escalation via tooling side effects.

## 3) Lint / coherence / contradiction seam

**Seam purpose**

Surface contradictions, unsupported claims, stale assertions, and structural coherence issues.

**May read**

- `structured/` objects and indexes,
- supporting `raw/` context,
- relevant `proposals/`,
- prior quality/coherence `logs/`.

**May emit**

- `proposals/` for contradiction handling, stale-claim remediation, and coherence repair,
- `logs/` lint/coherence findings with severity posture,
- low-risk housekeeping changes in `structured/` only with explicit lane authority.

**Must not do by default**

- silently reconcile contradictions into canonical `structured/`,
- downgrade or hide contradiction signal,
- treat lint diagnostics as equivalent to accepted canonical edits.

## 4) Proposal / review handoff seam

**Seam purpose**

Materialize reviewable candidate canonical changes and hand off to human-governed decision paths.

**May read**

- pending compile/lint outputs,
- impacted `structured/` targets,
- supporting `raw/` references,
- existing proposal state and review status,
- relevant operational `logs/`.

**May emit**

- `proposals/` artifacts for candidate canonical changes,
- `logs/` proposal lifecycle/handoff records.

**Must not do by default**

- apply canonical `structured/` changes as part of handoff,
- collapse review state into implicit acceptance,
- erase rejected/superseded proposal trace from append history.

## 5) Query-support seam

**Seam purpose**

Answer from maintained compiled knowledge and convert revealed gaps into maintenance follow-up.

**May read**

- `structured/` first,
- `raw/` for bounded fallback when coverage is insufficient,
- open `proposals/` for in-flight status,
- maintenance `logs/` for known quality gaps.

**May emit**

- ephemeral answer text,
- `proposals/` when query exposes canonical coverage deficiency requiring review,
- `logs/` query-discovered maintenance signals and follow-up emission records.

**Must not do by default**

- perform direct canonical `structured/` writes from query handling,
- leave discovered gaps only in ephemeral response text,
- reframe Noema as chat-first retrieval over files.

## Class-lane read/write contract baseline

| Lane | Semantic role | Maintainer default write posture | Exceptional write posture | Forbidden posture |
| --- | --- | --- | --- | --- |
| `raw/` | Source truth/provenance anchor | no mutation | append-only ingest registration where policy permits | rewrite/normalize-as-shortcut |
| `structured/` | Canonical compiled knowledge | proposal-first for canonical-impacting changes | direct apply only when policy lane explicitly grants auditable authority | hidden or unlogged canonical mutation |
| `proposals/` | Governed candidate canonical change lane | primary default emission lane for canonical-impacting edits | n/a | bypassing proposal/review for default canonical-impact edits |
| `logs/` | Append operational trace lane | required append trace for maintainer actions | n/a | deleting/rewriting operational history to hide behavior |

## Default and exception posture (normative)

## Default mode

1. canonical-impacting structured change -> emit proposal,
2. maintainer actions -> append log trace,
3. query -> support maintenance and emit durable follow-up when gaps appear,
4. no implicit broad direct-write authority.

## Exception mode (direct canonical apply)

Direct canonical apply is permitted only when **all** are satisfied:

1. explicit policy grants the exact structured lane/action,
2. action is auditable and reversible,
3. provenance + affected-object trace are logged,
4. no proposal/review bypass is hidden where policy requires review.

Absence of any condition means exception mode is not valid.

## Contract conformance guidance (Slice 1 bounded validation)

A seam run is **conformant** when all checks below pass.

## C1 — Seam-intent alignment

The run output matches the invoked seam purpose and does not emit out-of-scope artifact classes.

## C2 — Read-scope discipline

Reads stay within declared seam inputs and do not require undeclared authority expansion.

## C3 — Write-lane discipline

Writes respect default posture:

- canonical-impacting structured changes appear in `proposals/` unless explicit exception policy applies,
- maintainer activity is append-logged.

## C4 — Contradiction/uncertainty visibility

Detected contradiction or uncertainty is surfaced via proposal/log signals; it is not silently flattened into canonical content.

## C5 — Query-follow-up durability

Query-discovered material gaps produce durable maintenance follow-up (`proposals/` and/or `logs/`) rather than transient-only notes.

## C6 — Exception-apply gate evidence

Any direct canonical apply event includes explicit policy basis and audit trace linkage.

## C7 — Lane-separation integrity

No run collapses `raw/` with `structured/`, `proposals/` with accepted canonical state, or `logs/` with structured knowledge artifacts.

## Minimal inspection checklist (review-facing)

For each maintainer loop sample under review, confirm:

1. invoked seam and emitted artifacts are consistent,
2. every canonical-impacting structured delta has proposal trace or explicit exception evidence,
3. contradiction/uncertainty outputs are visible and attributable,
4. query-discovered gaps have durable follow-up records,
5. raw-source mutation did not occur,
6. append-log trace exists for ingest/compile/lint/proposal/query-support actions present in scope.

## Phase boundary and continuity statement

This baseline intentionally stops at contract and bounded conformance guidance.

Deferred to next slices:

- **Phase 8 Slice 2**: proposal payload/evidence/provenance contract,
- **Phase 8 Slice 3**: maintainer log/event schema and trace contract,
- **Phase 8 Slice 4**: bounded executable maintainer loop realization conforming to contracts.

## Drift-check statement

This slice does not:

- treat Noema as thin retrieval/chat wrapper,
- demote the maintainer/compiler/curator role,
- collapse raw and structured lanes,
- collapse visibility and authority semantics,
- broaden direct canonical apply beyond exceptional policy-gated posture,
- swallow distinct remaining Phase 8 slices.
