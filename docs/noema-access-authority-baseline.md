# Noema Access and Authority Baseline

## Purpose and boundary

This document defines the stable baseline semantics for multi-user access and authority in Noema.

This stable system-definition document originates from accepted **Phase 6 Slice 1**.

The slice is intentionally semantics-first and implementation-light. It defines baseline meaning for who can discover/read objects, who can create/change/review/publish them, and how those policy axes layer across workspace and object scope.

This slice does **not** implement production authentication, credential internals, deployment hardening internals, or runtime policy-engine internals.

## Why Phase 6 starts here

Phase 5 established maintainer workflow baseline behavior, including deterministic projections, proposal/review visibility surfaces, and operational traceability posture. Before deeper auth and deployment implementation can proceed coherently, Noema requires a stable access/authority language that preserves original architecture invariants.

Phase 6 therefore starts by stabilizing:

- multi-human and multi-agent participation semantics
- explicit separation of visibility from authority
- workspace/project as the primary policy operating unit
- object-level policy refinement without model collapse
- machine-scope boundedness and auditability

Without this baseline, downstream authentication and deployment work would risk introducing inconsistent meanings for the same policy terms.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-human-client-baseline.md`
- `docs/noema-agent-interface-baseline.md`
- `docs/noema-agent-surface-contract.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Core model invariants (Phase 6 Slice 1)

The following invariants are normative for this baseline:

1. **Noema is multi-human and multi-agent by default.**
2. **Visibility and authority are separate policy axes.**
3. **Workspace/project is the concrete operating policy unit.**
4. **Agent users are first-class bounded users, not hidden implementation details.**
5. **Obsidian compatibility does not grant policy bypass authority.**
6. **Machine-originated access and changes must remain attributable and auditable.**

## Identity categories at baseline depth

Identity semantics in this slice are category-level and transport-agnostic.

### Human identities

Humans are recognized as first-class participants with assignable workspace and object-level roles. A single human may hold multiple role families in one workspace if policy allows, but role semantics remain distinct.

### Agent identities

Agents are recognized as first-class bounded identities with explicit scope and operation limits. Agent identities must be durable and distinguishable from human identities in proposal metadata and logs (for example namespaced identity forms such as `agent:<id>`).

### Service/automation identities (bounded machine identities)

Where deployment requires machine-run automation, those actors are treated as bounded machine identities and governed through the same visibility/authority model. They are never implicitly “trusted root” identities at baseline.

## Visibility semantics (who can discover/read)

Visibility defines what an identity may discover and read. Visibility does not imply write or approval authority.

### Policy layers

Visibility may be applied at:

- **system level** (global defaults and global-public policy)
- **workspace level** (primary effective visibility baseline)
- **object level** (narrower or explicit override semantics under policy constraints)

### Baseline visibility categories

At baseline depth, Noema supports these visibility categories:

1. **Private**
   - Visible only to explicitly allowed identities.
   - Typical use: personal drafts, sensitive workspace artifacts, restricted logs.

2. **Team**
   - Visible to workspace members under workspace membership policy.
   - Typical use: default shared workspace content.

3. **Public**
   - Discoverable/readable without workspace membership (as configured by operator policy).
   - Public visibility still does not grant modify/approve authority.

4. **Scoped-agent**
   - Visible to specific bounded agent identities/scopes only.
   - Typical use: controlled machine context windows, bounded maintenance inputs, redacted operational records.

These categories are semantic classes; deployments may map them to concrete enforcement mechanisms differently while preserving meaning.

## Authority semantics (who can create/change/review/approve/publish)

Authority defines what an identity may do to system objects and workflow state. Authority is independent from visibility.

### Baseline authority action families

At baseline depth, authority should distinguish at least:

- **Create** — produce new objects/proposals/log entries in allowed scope.
- **Modify** — edit existing objects in allowed class/state scope.
- **Review** — evaluate proposals and record structured review outcomes.
- **Approve** — authorize proposal acceptance according to workflow policy.
- **Publish/Apply** — materialize accepted outcomes into canonical structured state.

The same identity may have one action family without another (for example review without publish).

### Explicit separation from visibility

Normative examples:

- An identity may have **team visibility** but **reader-only authority**.
- A contributor agent may have **proposal-create authority** with **no publish authority**.
- A reviewer may have **approve authority** even where they did not author the proposal.
- A public object may remain under tightly restricted publish authority.

## Workspace-level and object-level policy application

Workspace/project is the default policy operating unit. Object-level policy refines workspace baseline where needed.

### Workspace-level baseline

Workspace policy defines:

- participant membership classes (human/agent/service)
- default visibility posture for workspace objects
- baseline authority role assignments and action permissions
- default review/apply gates for canonical updates

### Object-level refinement

Object-level policy may:

- narrow visibility relative to workspace default (for sensitive objects)
- constrain authority actions for specific object classes or states
- require additional review gates for selected objects

Object-level policy should not silently broaden authority beyond workspace baseline unless explicitly declared and auditable.

### Conflict handling semantics (baseline)

When policy scopes conflict:

1. explicit deny/restriction semantics take precedence
2. narrower object-level constraints override broader workspace defaults
3. system-level safety constraints remain upper bounds

Implementations may differ in mechanics, but these precedence semantics should remain consistent.

## Baseline role families

Role families are semantic bundles of common authority patterns. Deployments may map them into concrete ACL/RBAC/ABAC shapes later.

### Owner

Typical baseline semantics:

- administer workspace policy defaults and membership
- delegate/revoke reviewer/contributor/reader/agent role assignments
- retain final governance responsibility for workspace policy posture

### Reviewer

Typical baseline semantics:

- inspect proposals and supporting traceability context
- record review outcomes and rationale
- approve/reject/return proposals according to policy

### Contributor

Typical baseline semantics:

- create proposals and allowed non-canonical artifacts
- modify proposal-layer artifacts in permitted states
- no direct canonical publish authority by default

### Reader

Typical baseline semantics:

- discover/read objects within effective visibility scope
- no create/modify/review/approve/publish authority by default

### Bounded agent roles

Agent role families should be explicit and bounded, for example:

- **Agent reader** (read/query only)
- **Agent analyst** (read/query + bounded traceability operations)
- **Agent contributor** (proposal submission only)
- **Agent maintainer-support** (bounded maintenance-oriented read/query/proposal behavior)

Bounded agent roles never imply unconstrained filesystem authority.

## Interaction with accepted Phase 3 and Phase 4 semantics

This baseline preserves earlier accepted semantics.

### Phase 3 (human client baseline) alignment

- Human GUI projections remain browse/review surfaces, not authority engines.
- Access in a client view (including Obsidian-compatible views) does not override Noema policy semantics.

### Phase 4 (agent interface baseline + surface contract) alignment

- Agent interfaces remain bounded to scope-enforced read/query and proposal workflows.
- Proposal submission by agents remains distinct from canonical publish authority.
- Identity attribution and scope enforcement remain required across protocol choices.

## Auditability expectations for machine-originated actions

Machine-originated actions must be reviewable and attributable at baseline.

Minimum expectations:

1. **Stable actor attribution**
   - Every machine action maps to a durable machine identity.
2. **Operation trace recording**
   - Read/query/proposal operations are recorded as auditable events (or equivalent).
3. **Proposal-to-outcome traceability**
   - Accepted machine-submitted proposals trace to review decisions, applied outcomes, and logs.
4. **Policy-decision observability**
   - Scope denials/redactions and policy-bound decisions are auditable where sensitivity policy permits.

## Explicit non-goals and deferrals (Phase 6 Slice 1)

This slice does **not** define or implement:

- production authentication stack mechanics
- password/session/token lifecycle internals
- SSO/federation architecture specifics
- credential issuance/rotation/revocation workflows
- encryption/key management/storage hardening internals
- deployment topology hardening and runtime network security profiles
- full policy engine internals (RBAC/ABAC evaluator design)
- enterprise-only policy complexity beyond open-source baseline needs

These concerns are intentionally deferred to later bounded Phase 6 slices.

## Drift-check statement

This slice intentionally preserves:

- open-source reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support
- editor-agnostic identity and policy posture
- Obsidian-compatible but not Obsidian-dependent operation
- separation of domain, profile, workspace/project, content type, visibility, and authority
- existing accepted object/model/interface semantics from Phases 2–5

## Next-slice pointer

After this access/authority baseline is established, the next bounded Phase 6 slice should be selected as one of:

1. **Phase 6 Slice 2A — authentication and identity provisioning semantics baseline**, or
2. **Phase 6 Slice 2B — self-hosted deployment/operations baseline semantics**.

Selection should be based on immediate dependency pressure for active implementation needs.
