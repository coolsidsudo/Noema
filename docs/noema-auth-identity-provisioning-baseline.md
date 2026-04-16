# Noema Authentication and Identity Provisioning Baseline

## Purpose and boundary

This document defines the stable baseline semantics for authentication and identity provisioning in Noema.

This stable system-definition document is produced for **Phase 6 Slice 2A (current implementation slice under review)** and follows the accepted **Phase 6 Slice 1** access/authority baseline.

The slice is intentionally semantics-first and implementation-light. It defines minimum durable meaning for identity categories, authentication outcomes, provisioning lifecycle, and workspace scope attachment in a multi-human, multi-agent, self-hosted Noema deployment.

This slice does **not** implement production authentication stacks, credential cryptography internals, federation internals, or deployment hardening internals.

## Why this slice follows Phase 6 Slice 1

Phase 6 Slice 1 stabilized visibility/authority semantics and policy layering. Authentication and identity provisioning must now be stabilized so policy decisions have consistent, attributable subjects.

In baseline terms:

- Slice 1 answers **what** actions are allowed and where.
- Slice 2A answers **who** is acting, **how identity is established**, and **how identities become known/scoped** before authorization is evaluated.

Without this layer, authorization semantics remain under-specified in real shared deployments.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-access-authority-baseline.md`
- `docs/noema-agent-interface-baseline.md`
- `docs/noema-agent-surface-contract.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Core model invariants (Phase 6 Slice 2A)

The following invariants are normative for this baseline:

1. **Identity/auth semantics are distinct from authorization semantics.**
2. **Authentication establishes actor identity claims; authorization evaluates allowed actions.**
3. **Human and agent identities are first-class and durably attributable.**
4. **Service/automation identities are bounded identities, not implicit superusers.**
5. **Workspace scope attachment is explicit and auditable, not inferred from client/tool access alone.**
6. **Machine-originated authenticated activity remains reviewable and attributable.**

## Baseline identity categories

Identity categories in this slice are semantic categories, not transport/protocol implementation details.

### Human identities

Human identities represent real people operating as owners, reviewers, contributors, readers, or delegated administrative actors under workspace policy.

Baseline expectations:

- durable identity reference in Noema policy/audit records
- distinguishable from non-human identities
- capable of holding multiple role families under explicit policy assignment

### Agent identities

Agent identities represent machine actors participating through bounded machine interfaces.

Baseline expectations:

- durable, namespaced actor identity (for example `agent:<id>`)
- explicit scope and operation bounds
- attribution in proposals, logs, and policy decisions
- never treated as anonymous background execution

### Service/maintainer identities

Service or maintainer identities represent automation processes (for example scheduled maintenance or apply/reconciliation operations) that need authenticated execution posture.

Baseline expectations:

- explicit bounded identity class (for example `service:<id>`)
- policy-governed scope attachment
- auditable distinction from both humans and non-service agent users
- no implicit bypass authority by virtue of being internal automation

## Identity namespace and durability semantics

### Namespace posture

Identity references should be globally unambiguous within a deployment and class-distinguishable at baseline depth.

Recommended baseline pattern:

- `human:<id>`
- `agent:<id>`
- `service:<id>`

Equivalent patterns are valid if they preserve class-distinguishable, durable identity semantics.

### Durability posture

At baseline, identity references used in policy bindings, proposals, and logs should be stable over time.

Implications:

- historical records must remain attributable even if display names rotate
- identity renaming/alias changes must preserve durable linkage
- deactivated identities remain resolvable in historical audit context

This slice defines semantic durability, not storage-key implementation internals.

## Authentication semantics (baseline depth)

### What authentication establishes

At baseline, successful authentication establishes:

1. asserted actor identity class and identifier (`human|agent|service` + id)
2. a valid authenticated session/context for bounded operation execution
3. optional context attributes needed for policy evaluation (for example workspace claim hints, client/runtime posture identifiers)

Authentication is about claim establishment and actor attribution, not permission grant.

### Authentication vs authorization (explicit separation)

Normative baseline rule:

- **Authentication answers:** “Who is this actor in Noema terms?”
- **Authorization answers:** “Given this authenticated actor, what operations are allowed in this scope?”

Consequences:

- a successfully authenticated actor may still be denied operations
- workspace membership and role assignment are authorization inputs, not authentication outcomes
- client/tool access (for example opening an Obsidian-compatible view) is not itself an authorization grant

### Baseline failure semantics

At semantics level, authentication outcomes should differentiate:

- identity unknown/unrecognized
- authentication failed/invalid
- authentication succeeded but scope/authorization denies requested action

Implementations may map these to concrete error codes differently while preserving semantic distinctions.

## Provisioning semantics

Provisioning defines how identities become known to a deployment and eligible for workspace-scoped policy assignment.

### Deployment-level identity registration

At baseline, a deployment should support explicit identity registration/admission for each identity class (human/agent/service).

Provisioning should minimally establish:

- durable identity reference
- identity class
- optional metadata (display name, purpose, owner/maintainer linkage)
- initial lifecycle state

### Baseline lifecycle states

This slice defines semantic lifecycle states sufficient for policy and audit clarity:

1. **pending**
   - identity declared but not yet active for normal operations
2. **active**
   - identity may authenticate and operate within assigned scope
3. **suspended**
   - identity temporarily blocked from normal authenticated operations
4. **deactivated**
   - identity no longer allowed for new operations; historical attribution retained

Implementations may add internal sub-states if baseline meaning is preserved.

### Provisioning posture by identity class

- **Human:** admission can be owner/admin-governed and may require manual acceptance.
- **Agent:** admission must include explicit scope intent and responsible human/owner linkage.
- **Service:** admission must include explicit operational purpose and bounded execution scope.

This slice does not prescribe invitation UX, bootstrap scripts, federation connectors, or enterprise directory internals.

## Workspace membership and scope attachment semantics

Workspace/project is the primary policy operating unit.

### Membership attachment

Authenticated identities become operationally meaningful through explicit workspace attachment semantics:

- identity admitted to workspace membership class
- role-family and authority bindings assigned per Slice 1 semantics
- visibility scope and object constraints resolved at workspace/object policy layers

### Scope attachment rules (baseline)

1. no workspace access without explicit membership/scope attachment
2. membership does not automatically grant all authority actions
3. object-level constraints may narrow workspace-level permissions
4. scope changes (grant/revoke/update) are auditable state transitions

### Cross-workspace posture

Identity existence at deployment scope does not imply blanket cross-workspace membership.

Each workspace attachment is explicit and policy-governed.

## Agent credential/proxy posture (baseline depth)

This slice does not define concrete token/session/secret mechanisms, but it establishes baseline semantic posture for machine authentication flows:

1. machine credentials/proxies represent a specific durable `agent` or `service` identity
2. credentials/proxy usage must not erase underlying actor attribution
3. delegated/proxy execution should preserve both effective actor and delegation context where applicable
4. shared/unattributed machine credentials are non-baseline posture and should be avoided

If an intermediary service executes on behalf of an agent, logs should preserve attributable linkage to the originating identity context where policy allows.

## Auditability requirements for authenticated actions

Auditability expectations from prior slices remain mandatory and are extended to authenticated identity events.

Minimum baseline expectations:

1. **Authentication event traceability**
   - authentication success/failure outcomes are recorded with actor/class context where policy permits
2. **Provisioning/change traceability**
   - identity lifecycle and workspace-scope changes are recorded as auditable events
3. **Action attribution continuity**
   - authenticated action records retain durable actor identity linkage across proposals/reviews/apply/log flows
4. **Policy-decision observability**
   - denials and redactions remain observable/auditable within sensitivity limits

These requirements preserve machine-originated accountability and human governance transparency.

## Interaction with accepted Slice 1 access/authority semantics

This slice is additive and non-redefining.

- Slice 1 remains authoritative for visibility and authority action-family semantics.
- Slice 2A provides subject identity/auth/provisioning semantics consumed by Slice 1 policy evaluation.
- No change is made to established role-family semantics (`owner`, `reviewer`, `contributor`, `reader`, bounded agent roles).
- No change is made to established object-class semantics (`raw`, `structured`, `proposals`, `logs`).

## Explicit non-goals and deferred concerns

This slice does **not** define or implement:

- production password hashing/session/token protocol internals
- SSO/OIDC/OAuth/federation implementation specifics
- secret storage, key management, or encryption internals
- deployment topology/network hardening mechanics
- runtime authorization engine evaluator internals
- enterprise IAM synchronization or directory schema details
- end-user client authentication UX specifics

These concerns remain deferred to later bounded Phase 6 slices.

## Drift-check statement

This slice preserves:

- open-source reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support
- editor-agnostic identity posture
- Obsidian-compatible but not Obsidian-dependent operation
- strict separation of domain, profile, workspace/project, content type, visibility, authority, and identity/auth concerns
- previously accepted Slice 1 access/authority semantics

## Next-slice pointer

After this Phase 6 Slice 2A baseline, proceed to **Phase 6 Slice 2B — deployment/self-hosting operations baseline semantics**, unless a tighter dependency is identified during review.
