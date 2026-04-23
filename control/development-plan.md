# Noema Development Plan (Long-Horizon Roadmap)

This document is the **stable long-horizon roadmap** for building Noema.

It describes phase intent, rationale, and sequencing at a durable level. It does **not** act as a live execution tracker.

For live repository execution state (latest accepted slice, any current under-review slice, next queued continuation, and brief continuity notes), see `control/development-tracker.md`.

## Scope and authority

`control/development-plan.md` owns:

- long-horizon phase structure
- phase objectives, key outputs, and why each phase matters
- stable sequencing rationale across the program

It does **not** own per-issue or per-slice live status.

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

## Phase 6: Multi-user / auth / deployment baseline

**Objective**

Support real shared deployment with explicit policy boundaries by sequencing semantics first, then identity/auth and deployment baselines.

**Key outputs**

- Access/authority baseline semantics
- Authentication and identity provisioning baseline semantics
- Deployment/self-hosting operations baseline semantics
- Backup/restore continuity guidance baseline semantics
- Deployment hardening/profile guidance baseline semantics
- Hardening conformance/validation guidance baseline semantics
- Conformance evidence interoperability refinement scope

**Why it matters**

Noema is meant to be reusable by others and deployable in real environments. Phase 6 makes the project truly multi-user, governable, and practical to self-host beyond a single experimental setup while preserving implementation-light, baseline-first sequencing.

## Phase 7: Reference deployment packaging baseline

**Objective**

Move from accepted semantics into a bounded, concrete, single-node reference deployment package that operators can stand up and understand.

**Key outputs**

- Minimal repo-native reference deployment package under `deploy/`
- Operator bootstrap guidance for single-node self-hosted setup
- Minimal configuration and layout artifacts for practical bootstrap
- Explicit mapping across storage substrate, human path, machine path, and maintainer path
- Continuity-aware posture aligned with accepted backup/restore semantics

**Why it matters**

Accepted baseline semantics are broad enough that practical realizability matters. This phase anchors semantics in a concrete reference package while staying implementation-light and avoiding orchestration/enterprise drift.

**Phase boundary note (why Phase 7 stops here)**

Phase 7 is intentionally complete once Noema has a coherent, practical, bounded reference package that proves deployability and path separation on single-node self-hosted infrastructure. Additional package micro-polish after this point has diminishing strategic value relative to the next major differentiator.

Once the baseline package is understandable and bootstrappable, the highest-leverage continuation is not broader packaging complexity, but making the maintainer/compiler direction contractually concrete. That shift preserves the original Noema framing as an AI-maintained knowledge system rather than a generic deployment template.

## Phase 8: Maintainer-agent execution contract and bounded realization

**Objective**

Realize the post-Phase 7 maintainer-agent direction by translating the accepted maintainer schema into executable, testable, governance-preserving contracts and an initial bounded runtime loop.

**Why this is the next major direction**

The original system design establishes the maintainer/compiler/curator role as central to Noema's compounding-knowledge behavior. The accepted maintainer-agent schema (`docs/noema-maintainer-agent-skill-management-schema-v0.md`) then defines seam-level behavior, class-lane write posture, proposal/review boundaries, and logging requirements in Karpathy-first terms.

Phase 8 is therefore the bridge from accepted architecture/control semantics to concrete maintainer execution behavior. This is the key differentiator work: proving that Noema can operate as a governed AI-maintained knowledge system, not merely as file conventions, chat retrieval, or packaging scaffolding.

**What Phase 8 is for**

Phase 8 is a contract-realization phase for maintainer execution. It should:

- make ingest/compile/lint/propose/query-support seams concrete,
- make maintainer-emitted proposal and log artifacts structurally consistent,
- preserve explicit proposal/review/apply boundaries,
- keep direct canonical apply tightly bounded and policy-gated,
- stay implementation-light enough to avoid premature runtime sprawl.

It should **not** be treated as a mandate for broad autonomy or platform-wide orchestration.

### Phase 8 staged roadmap (initial bounded slices)

#### Phase 8 Slice 1 — Maintainer loop contract baseline

Define and validate the minimum end-to-end maintainer loop contract:

- seam-level operation contract for ingest/compile/lint/propose/query-support,
- class-lane read/write boundary contract across `raw/`, `structured/`, `proposals/`, and `logs/`,
- explicit default posture: canonical-impacting structured changes emit proposals,
- explicit exception posture: direct canonical apply remains auditable and policy-gated.

Primary output type: stable contract/spec guidance with conformance checks for boundary violations.

#### Phase 8 Slice 2 — Proposal payload, evidence, and provenance contract

Define the required maintainer-emitted proposal shape for canonical-impacting edits:

- minimum proposal payload fields for rationale, affected objects, and intended outcomes,
- evidence/provenance linkage requirements back to source/compiled context,
- contradiction and uncertainty signaling requirements,
- acceptance-readiness criteria that keep review decisions well-scoped.

Primary output type: proposal schema/profile baseline plus validation guidance.

#### Phase 8 Slice 3 — Maintainer log/event schema and operational trace contract

Define append-log contracts for maintainer operations so execution can be reconstructed and audited:

- event classes for ingest, compile, lint/coherence, proposal emission, and query-discovered maintenance,
- required event identity, actor, timing, and affected-object trace fields,
- event/proposal/structured linkage rules,
- guardrails separating operational logs from canonical structured knowledge.

Primary output type: log/event schema baseline and traceability interpretation guidance.

#### Phase 8 Slice 4 — Initial executable maintainer loop realization (bounded substitution path)

Implement or substitute a first bounded executable maintainer loop that conforms to Slices 1–3 contracts:

- deterministic loop execution over approved seams,
- proposal-first canonical-impact behavior by default,
- contract validation hooks for proposals and events,
- bounded runtime profile that avoids broad agent-platform expansion.

Primary output type: minimal executable reference behavior proving contract realism without authority broadening.

**Early Phase 8 anti-drift boundaries (explicit out-of-scope)**

During Slices 1–4, the roadmap excludes:

- uncontrolled expansion of canonical direct-write authority,
- recentering Noema as generic chat/RAG over files,
- broad multi-agent swarm architecture/programming,
- enterprise/platform sprawl (orchestration stacks, IAM suites, distributed control planes),
- schema rewrites that invalidate accepted Phase 5/6/7 and NOE-67 continuity.

**How Phase 8 connects to later major work**

Once maintainer loop contracts are concrete and a bounded executable realization exists, likely follow-on directions include:

1. stronger policy-governed apply pathways and reconciliation ergonomics for accepted maintainer output,
2. deeper operator observability and recovery tooling built on stable maintainer event/proposal traces,
3. selective multi-maintainer and/or multi-agent coordination patterns that preserve bounded authority semantics,
4. broader deployment profiles only after maintainer execution semantics remain stable across environments.

These continuations should remain downstream of the Phase 8 contract baseline, not substitutes for it.

## Phase 9: Bounded service surface and operator workflow integration

**Objective**

Turn the accepted maintainer-governance execution core into a usable bounded system surface for human operators and external agents, while preserving Noema’s editor-agnostic identity and Obsidian-compatible human path.

**Why this is the next major direction**

The original system design requires Noema to expose both human-facing clients and bounded machine interfaces, while remaining Obsidian-compatible without making Obsidian the authority layer. Earlier phases established the human-client baseline, agent-interface baseline, maintainer workflow baseline, and bounded maintainer execution core. The next highest-leverage step is therefore not more Phase 8 semantics, but integrating those accepted capabilities into a real bounded service surface.

Phase 9 should interpret this as:
- Noema as the governed system/service layer,
- Obsidian as a strong first-class human client,
- optional native operator UI only where bounded workflows are awkward or unsafe in Obsidian alone.

**What Phase 9 is for**

Phase 9 is an implementation-first integration phase. It should:

- expose a bounded service/core surface over Noema objects, proposals, traces, and apply/recovery state,
- reuse accepted Phase 8 runtime pieces rather than redefining them,
- strengthen operator workflow integration for browse/review/apply/observability use,
- support Obsidian through generated/projection-based human-facing views,
- preserve editor-agnostic identity and avoid client-local authority drift.

It should **not** be treated as a mandate to build a broad standalone web application before the bounded system surface exists.

### Phase 9 staged roadmap (initial bounded slices)

#### Phase 9 Slice 1 — Service core and bounded machine surface

Implement a transport-neutral service/core layer and first bounded machine-facing surface for:
- object retrieval/listing,
- traceability retrieval,
- proposal submission,
- proposal status retrieval.

Primary output type: executable service behavior with bounded interfaces and tests.

#### Phase 9 Slice 2 — Operator workflow integration and Obsidian-facing projections

Integrate accepted review/apply/observability behavior into operator-usable workflows and Markdown-native projections such as:
- workspace home,
- browse/index surfaces,
- proposal/review queues,
- recent changes / operational status views.

Primary output type: executable operator-facing integration over accepted runtime behavior.

#### Phase 9 Slice 3 — Thin external adapter surface

Expose the accepted bounded operation layer through additional adapters such as MCP and/or equivalent thin integration surfaces without redefining Noema semantics.

Primary output type: adapter-level interoperability over the same bounded core.

**Early Phase 9 anti-drift boundaries (explicit out-of-scope)**

During initial Phase 9 work, the roadmap excludes:

- treating Obsidian as the authority layer,
- reducing Noema to an Obsidian-only product,
- broad standalone UI/platform expansion before service-core value is proven,
- uncontrolled direct canonical-write authority,
- recentering Noema as generic chat/RAG over files,
- enterprise/orchestration sprawl.

**How Phase 9 connects to later major work**

Once the bounded system surface is usable for both human operators and external agents, likely follow-on directions include:

1. stronger multi-user/operator ergonomics,
2. selective native operator UI for bounded high-friction workflows,
3. broader deployment profiles after the bounded surface remains stable,
4. richer extension/integration packs built on the same governed system core.

