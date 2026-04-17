# Noema Development Plan

This plan outlines a practical early sequence for building Noema without overcommitting to implementation details too early. The goal is to establish a coherent public baseline, then grow toward a usable self-hosted multi-human and multi-agent platform.

## Active workflow note

The accepted architecture baseline is now actively adopted for implementation workflow through `control/workflow-baseline.md`.

Accepted completed slices: **Phase 0 (architecture baseline), Phase 1 (repository skeleton), and the full Phase 2 definition package (core object conventions, metadata profile, relationship/traceability conventions, and index/catalog baseline)**.

Latest completed/accepted slice: **Phase 6 Slice 6 — conformance evidence interoperability refinement scoping**.

Current execution focus: **Slice 6 acceptance-close sync is complete in control-state; Phase 6 Slice 7 remains next queued/proposed and is not yet opened**.

Phase 5 queue status: **Closed (Slices 1–15 accepted/closed with explicit closure criteria satisfied)**.

## Phase 0: Architecture baseline

**Objective**

Define the public framing, core concepts, and initial design language of the project.

**Key outputs**

- Project README with the initial public description
- Original system design document
- Phased development plan
- Clear terminology for domain, profile, workspace, content type, visibility, and authority

**Why it matters**

Without a shared architecture baseline, the repository will drift into vague or conflicting assumptions. This phase establishes what Noema is, what it is not, and how future contributors should think about the system.

## Phase 1: Repository skeleton

**Objective**

Create the first repository structure that reflects the intended platform shape.

**Key outputs**

- Core top-level directories and documentation layout
- Initial conventions for where raw, structured, proposal, and log objects live
- Basic contribution and repository usage guidance
- Minimal sample workspace or reference layout for discussion

**Why it matters**

A repository skeleton turns architecture language into something concrete. It gives contributors a shared place to implement against and reduces the risk that the project collapses into an unstructured collection of notes or scripts.

## Phase 2: Core knowledge model

**Objective**

Define and implement the first durable knowledge-object model.

**Key outputs**

- Object conventions for raw, structured, proposal, and log content
- Metadata and provenance rules
- Relationship model for linking knowledge objects
- Initial indexing or cataloging approach for navigating content

**Why it matters**

This phase creates the backbone of Noema. If the knowledge model is weak, the project will behave like a loose notes repository or an ad hoc retrieval layer instead of a knowledge platform.

## Phase 3: Human client baseline

**Objective**

Provide a useful first human-facing experience.

**Key outputs**

- Obsidian-compatible workspace view or workflow guidance
- Minimal human browse/review path outside of raw filesystem access
- Editing and review conventions for human users
- Basic documentation for owner, reviewer, and reader workflows

**Why it matters**

Noema only works if humans can actually use and govern it. This phase proves that the platform supports human knowledge work while staying editor-agnostic and not collapsing into an Obsidian-only system.

## Phase 4: Agent interface baseline

**Objective**

Expose bounded machine-facing interfaces for agent users.

**Key outputs**

- Initial read/query API surface
- Proposal submission path for machine contributors
- MCP-style interface or equivalent bounded tool surface
- Agent identity and scope model for baseline integrations

**Why it matters**

Agent users are part of the core architecture, not an afterthought. This phase enables machine consumers and contributors without granting uncontrolled write access to the underlying storage.

## Phase 5: Maintainer workflow baseline

**Objective**

Implement the first maintainer/compiler/curator workflows.

**Key outputs**

- Source ingest flow
- Structured compilation and cross-linking flow
- Proposal and review queue behavior
- Linting or consistency-check workflow
- Operational logging for maintainer actions

**Why it matters**

This is the phase where Noema starts behaving like a compounding knowledge system. The maintainer workflow is what turns accumulated sources and questions into a maintained knowledge base rather than a pile of disconnected artifacts.

### Phase 5 closure declaration (Slice 15)

Phase 5 was defined to establish a maintainer/compiler/curator baseline across five capabilities:

1. source ingest flow
2. structured compilation and cross-linking flow
3. proposal and review queue behavior
4. linting/consistency-check workflow
5. operational logging for maintainer actions

Accepted Phase 5 Slices 1–14 implemented deterministic repository scan/build behavior, projection/report generation, relationship/reference checks, accepted-proposal completeness checks, apply-log coverage checks, and results_in structured-class correctness. Slice 15 confirms this accepted baseline now covers all five Phase 5 goal capabilities at a baseline level and does not require additional validator proliferation for Phase 5 closure.

**Phase 5 completion criteria (explicit finish rule):**

- Maintainer scan/build pipeline runs deterministically and emits reproducible projection outputs for workspace review surfaces.
- Cross-link/reference validation covers proposal targets, accepted outcomes (`results_in`), structured support provenance (`supports`), supersession references, and log linkage references within workspace scope.
- Proposal/review surfaces and diagnostics are present in projection outputs (`review/proposal-queue.md`, workspace build report summaries, and class browse pages).
- Operational log traceability is enforced for terminal proposal lifecycle events and accepted proposal outcome application coverage.
- Control documents no longer leave Phase 5 in an open-ended continuation loop and instead declare closure readiness and transition pointer.

**Closure judgment:** Phase 5 is complete after Slice 15. No additional Phase 5 implementation slice is required for baseline closure.

## Phase 6: Multi-user / auth / deployment baseline

**Objective**

Support real shared deployment with explicit policy boundaries by sequencing semantics first, then identity/auth and deployment baselines.

**Key outputs**

- Phase 6 Slice 1 access/authority baseline semantics (accepted prerequisite)
- Phase 6 Slice 2A authentication and identity provisioning semantics baseline (accepted prerequisite)
- Phase 6 Slice 2B deployment/self-hosting operational baseline semantics for NAS/VPS (accepted prerequisite)
- Backup and restore operational guidance refinement baseline semantics (defined prior slice)
- Deployment hardening/profile guidance baseline semantics (accepted Slice 4 prerequisite)
- Implementation-constrained hardening conformance/validation guidance baseline semantics (accepted Slice 5 prerequisite)
- Conformance evidence interoperability refinement scoping (accepted Slice 6 outcome)

**Why it matters**

Noema is meant to be reusable by others and deployable in real environments. Phase 6 makes the project truly multi-user, governable, and practical to self-host beyond a single experimental setup while preserving implementation-light, baseline-first sequencing.

### Phase 6 Slice 1 scope note

Phase 6 Slice 1 defines the baseline scope for multi-user access and authority semantics in `docs/noema-access-authority-baseline.md`, including:

1. baseline human/agent identity categories
2. explicit visibility semantics (`private`, `team`, `public`, `scoped-agent`)
3. explicit authority semantics (`create`, `modify`, `review`, `approve`, `publish/apply`)
4. explicit visibility-vs-authority separation
5. workspace-level defaults with object-level policy refinement
6. baseline role families (`owner`, `reviewer`, `contributor`, `reader`, bounded agent roles)
7. machine-originated action auditability expectations
8. non-goals/deferred Phase 6 concerns (auth internals, credential lifecycle, deployment hardening internals)


### Phase 6 Slice 2A scope note

Phase 6 Slice 2A defines baseline authentication and identity provisioning semantics in `docs/noema-auth-identity-provisioning-baseline.md`, including:

1. baseline identity classes (`human`, `agent`, `service`)
2. durable identity namespace posture and attribution expectations
3. explicit authentication-vs-authorization separation
4. provisioning semantics and baseline identity lifecycle states
5. workspace membership and scope-attachment semantics
6. agent credential/proxy attribution posture at baseline depth
7. authenticated-action auditability requirements
8. non-goals/deferred concerns for production auth-stack/deployment internals

Next bounded continuation pointer: **Phase 6 Slice 2B — deployment/self-hosting operations baseline semantics**.

### Phase 6 Slice 2B scope note

Phase 6 Slice 2B defines baseline self-hosted deployment and operations semantics in `docs/noema-self-hosted-deployment-operations-baseline.md`, including:

1. single-node-first and operator-controlled deployment posture
2. NAS/VPS practicality expectations
3. baseline human-facing and machine-facing access-path semantics
4. storage/workspace portability and inspectability expectations
5. backup/restore continuity semantics at baseline depth
6. upgrade/change-management baseline posture
7. operator/admin responsibility boundaries
8. explicit non-goals and deferred hardening/deployment-engineering concerns

Next bounded continuation pointer: **Phase 6 Slice 3 — backup and restore operational guidance refinement baseline semantics**.


### Phase 6 Slice 3 scope note

Phase 6 Slice 3 defines baseline backup and restore operational guidance semantics in `docs/noema-backup-restore-operational-guidance-baseline.md`, including:

1. backup coverage classes for knowledge, workspace/project, policy/auth, and operational continuity state
2. coherent restore semantics, including explicit full vs partial restore posture
3. governance/history continuity expectations at baseline depth
4. verification posture with inspectability and portability expectations
5. qualitative recovery-point and recovery-time posture (non-SRE-target)
6. explicit operator responsibilities for cadence and restore readiness
7. relationship to accepted Slice 2B deployment baseline
8. explicit non-goals/deferred DR/hardening concerns

Next bounded continuation pointer: **Phase 6 Slice 4 — deployment hardening/profile guidance baseline semantics**.

### Phase 6 Slice 4 scope note

Phase 6 Slice 4 defines deployment hardening/profile guidance baseline semantics in `docs/noema-deployment-hardening-profile-guidance-baseline.md`, including:

1. Noema-specific hardening meaning at semantics-first depth
2. operator profile-guidance posture across exposure/hosting contexts
3. baseline-required hardening expectations vs operator-selected stronger profiles
4. relationship boundaries with accepted Slice 1, Slice 2A, Slice 2B, and Slice 3 semantics
5. minimum hardening concern categories (exposure, secret/config handling, administrative path protection, change/update safeguards, audit/log posture, recovery-sensitive safeguards)
6. explicit baseline operator responsibility boundaries
7. explicit non-goals/deferred implementation internals

Next bounded continuation pointer: **Phase 6 Slice 5 — implementation-constrained hardening conformance/validation guidance baseline semantics**.

### Phase 6 Slice 5 scope note

Phase 6 Slice 5 defines implementation-constrained hardening conformance/validation guidance baseline semantics in `docs/noema-hardening-conformance-validation-guidance-baseline.md`, including:

1. hardening conformance and validation posture meaning in Noema terms
2. selected hardening concern categories with minimum conformance dimensions
3. bounded cross-profile interpretation for baseline-required vs stronger safeguards
4. minimum validation scenario/check classes without harness mandates
5. compatibility mapping guidance for richer local implementation stacks
6. explicit relationship boundaries with accepted Slice 1, Slice 2A, Slice 2B, Slice 3, and Slice 4 semantics

Next bounded continuation pointer: **Phase 6 Slice 6 — conformance evidence interoperability refinement (current under-review scoping slice)**.


### Phase 6 Slice 6 scope note

Phase 6 Slice 6 defines scoping semantics for conformance evidence interoperability refinement in `docs/noema-conformance-evidence-interoperability-refinement-scoping.md`, including:

1. bounded definition of conformance evidence meaning after accepted Slice 5 semantics
2. explicit interoperability-interpretation gap statement without reopening prior slices
3. candidate evidence classes and evidence-shape dimensions for possible follow-on refinement
4. minimum interpretation boundary rules without toolchain/schema/storage mandates
5. explicit relationship boundaries with accepted Slice 4 and Slice 5 semantics
6. explicit out-of-scope and anti-drift guardrails for harness/scanner/benchmark lock-in

Next bounded continuation pointer: **Phase 6 Slice 7 remains next substantive queued/proposed follow-on (evidence interpretation profile/claim-mapping semantics), to be explicitly opened in a separate under-review slice if started**.
