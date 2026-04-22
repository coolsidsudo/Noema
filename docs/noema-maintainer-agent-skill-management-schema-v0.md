# Noema Maintainer Agent Skill / Management Schema V0

## Purpose

This document defines the post-Phase 7 maintainer-agent operating schema for Noema.

It is a **management-skill definition** for the AI maintainer/compiler/curator role: what the maintainer is for, where it hooks into Noema, exactly what it can emit at each seam, and how governance boundaries are preserved.

This is architecture/control guidance, not runtime implementation.

## Why Karpathy's pattern is the primary reference

Noema anchors to Karpathy's LLM Wiki pattern:

- immutable **raw source truth**,
- maintained **compiled wiki/knowledge surface**,
- explicit **schema/instructions** that drive maintainer behavior,
- AI as **compiler/maintainer** rather than query-only retriever.

Noema extends this pattern for shared operation by adding governed proposal/review and operational logging classes, without replacing the raw -> compiled -> schema center.

## Noema mapping of raw / compiled knowledge / schema

Karpathy-to-Noema mapping:

- raw sources -> `raw/`
- compiled wiki -> `structured/`
- schema/instructions -> maintainer skill/schema docs and control/config guidance

Governed shared-operation extensions:

- `proposals/` for review-bounded candidate canonical changes
- `logs/` for append-only operational trace

## Maintainer agent role

The maintainer is Noema's knowledge compiler/curator management role.

Primary role outcomes:

1. keep `structured/` coherent and current from `raw/`,
2. preserve provenance and contradiction visibility,
3. surface governed proposals where authority requires review,
4. maintain durable operational trace.

The maintainer is not a broad autonomous author. Its default posture is bounded, policy-aware maintenance.

## Maintainer Skill Rules V0

1. **`raw/` is immutable source truth.** Maintainer must not silently rewrite source records.
2. **`structured/` is compiled default answer surface.** Query handling starts there.
3. **Canonical-impacting structured edits default to proposals.** Direct canonical apply is exceptional and policy-gated.
4. **Contradictions must be surfaced, not silently reconciled.** Emit contradiction candidates/proposals/logs.
5. **Structured claims require support posture.** Each maintained claim must be provenance-supported or explicitly marked (`derived`, `hypothesis`, or `needs-review`).
6. **Query-discovered gaps become maintenance work.** Emit task/proposal/log follow-up; do not leave gaps only in transient response text.
7. **Maintainer actions are append-logged.** Approved operational lanes in `logs/` must record ingest/compile/lint/proposal/query-maintenance activity.
8. **Direct canonical apply is non-default.** It requires explicit authority scope and auditable trace.

## Maintainer operating seams

### Ingest seam

Purpose: incorporate new source material and register maintenance impact.

### Compile seam

Purpose: update compiled knowledge objects, indexes, and links from maintained source context.

### Lint / contradiction / coherence seam

Purpose: detect contradictions, stale assertions, unsupported claims, and structural coherence issues.

### Proposal / review seam

Purpose: route canonical-impacting changes through governed review when direct apply is not authorized.

### Query seam (maintenance-support seam)

Purpose: serve compiled-first answers and convert discovered gaps into maintenance actions.

Query is not the center of Noema. Persistent knowledge maintenance is the center.

## Allowed Outputs by Seam

### 1) Ingest seam

Allowed outputs:

- `logs/`: ingest-event records (source id, workspace context, maintainer actor, timestamp, outcome)
- `proposals/`: optional ingest-derived candidate updates when authority requires review
- `structured/`: no canonical-impacting write by default unless explicit apply authority exists
- nowhere pending review: candidate compile notes may remain transient until proposal emission

### 2) Compile seam

Allowed outputs:

- `structured/`: only for authorized compile updates within explicit authority scope
- `proposals/`: default lane for canonical-impacting structured edits
- `logs/`: compile-run records, affected object set, provenance/lint summary
- nowhere pending review: draft compile deltas before proposal materialization

### 3) Lint / coherence seam

Allowed outputs:

- `proposals/`: contradiction candidates, stale-claim remediation proposals, missing-link proposals
- `logs/`: lint/coherence findings and severity summaries
- `structured/`: only low-risk metadata housekeeping if explicitly authorized; otherwise proposal-only
- nowhere pending review: temporary diagnostics not yet accepted into proposals/logs

### 4) Proposal / review seam

Allowed outputs:

- `proposals/`: structured proposal artifacts with rationale, affected objects, and provenance references
- `logs/`: proposal lifecycle/review events in approved append lanes
- `structured/`: none until accepted and apply authority path executes
- nowhere pending review: reviewer notes before formal proposal/review artifact update

### 5) Query seam

Allowed outputs:

- answer text: compiled-first response (ephemeral channel output)
- `proposals/`: gap-remediation proposal when question reveals material deficiency
- `logs/`: query-maintenance events (coverage gaps, stale assertions found, follow-up emitted)
- `structured/`: no direct canonical write by default from query handling
- nowhere pending review: transient reasoning traces not promoted to durable artifacts

## Read/write authority boundaries

### Maintainer read scope

Maintainer may read:

- `raw/` source objects
- `structured/` compiled knowledge objects
- `proposals/` and review status
- `logs/` operational history
- workspace/context/policy/schema files required for bounded operation

### Maintainer write posture (default vs exception)

**Default mode (normal):**

- canonical-impacting `structured/` change -> emit `proposals/`
- append operational trace -> `logs/`
- do not mutate canonical structured truth directly

**Exception mode (explicitly authorized):**

Direct canonical apply is permitted only when all are true:

1. authority policy explicitly grants the specific lane,
2. action is auditable and reversible,
3. provenance and affected-object trace are logged,
4. no policy bypass or hidden mutation is introduced.

**Forbidden:**

- raw-source mutation as maintenance shortcut
- silent contradiction suppression
- unlogged canonical mutation
- implicit authority escalation via tooling side effects

## Maintainer operating loop

1. ingest new/changed source context (`raw/` + context metadata)
2. compile/update affected `structured/` coverage
3. run lint/coherence checks and contradiction scan
4. emit governed proposals for canonical-impacting changes
5. record append-only operational logs for all maintenance actions
6. process review outcomes and reconcile maintenance backlog
7. answer from compiled layer and convert discovered gaps into maintenance follow-up

## Answering/query posture

Query is a maintenance-support seam, not Noema's center.

Required posture:

1. answer from `structured/` first,
2. use `raw/` fallback only when compiled coverage is insufficient,
3. mark uncertainty explicitly,
4. emit durable maintenance follow-up (proposal/log/task) for revealed gaps,
5. avoid leaving useful synthesis only in transient answer text.

## Human review/governance posture

Human reviewers/owners remain authority anchors.

- policy and authority lanes are human-governed,
- canonical-impacting changes are review-bounded by default,
- ambiguous or high-impact contradiction resolution requires human judgment,
- acceptance/rejection outcomes remain attributable and logged.

## Model and tool posture

This schema assumes a maintainer-oriented model/tool behavior:

- document-grounded synthesis,
- deterministic update discipline,
- explicit provenance and contradiction surfacing,
- bounded seam-level operations (ingest/compile/lint/propose/query-support),
- no generic open-ended filesystem mutation posture.

## Second-tier practical borrowings

Second-tier references are practical hints only, subordinate to Karpathy-first structure.

- **Khoj:** self-hosted/personal-AI operational ergonomics and client pragmatics.
- **Mem0 OSS:** persistent context/memory ergonomics as secondary implementation cue.
- **Tana supertags:** typed-object workflow ergonomics for structured navigation.
- **WorkBuddy + Obsidian article:** practical daily maintainer rhythm hints.

None of the above replace raw -> compiled -> schema as Noema's primary pattern.

## Explicit non-goals

This schema is not:

- a generic RAG/chat-over-files design,
- a generic multi-agent swarm platform,
- a memory SDK product strategy,
- a runtime/package implementation slice,
- an authority-expansion shortcut for direct canonical writes,
- an Obsidian-only operating model.

## Recommended next implementation direction

After higher-level acceptance of NOE-67, first bounded follow-on slice should be:

**Phase 8 Slice 1 — Maintainer loop contract baseline**

Minimum scope:

1. seam-level operation contract (ingest/compile/lint/propose/query-support),
2. class-lane read/write permission contract,
3. proposal payload requirements for canonical-impacting edits,
4. append-log event schema for maintainer actions,
5. validation that direct canonical apply remains exceptional and policy-gated.
