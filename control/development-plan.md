# Noema Development Plan

This plan outlines a practical early sequence for building Noema without overcommitting to implementation details too early. The goal is to establish a coherent public baseline, then grow toward a usable self-hosted multi-human and multi-agent platform.

## Active workflow note

The accepted architecture baseline is now actively adopted for implementation workflow through `control/workflow-baseline.md`.

Accepted completed slices: **Phase 0 (architecture baseline), Phase 1 (repository skeleton), and the full Phase 2 definition package (core object conventions, metadata profile, relationship/traceability conventions, and index/catalog baseline)**.

Latest completed/accepted slice: **Phase 5 Slice 9 — deterministic workspace-local object ID uniqueness validation and diagnostics**.

Current execution focus: **Phase 5 Slice 10 — next bounded maintainer workflow slice after accepted Slice 9**.

Next queued slice: **Phase 5 follow-on bounded maintainer workflow slice after Slice 10 (to be declared in-sequence)**.

Phase 5 queue status: **In progress (Slices 1–9 accepted/closed; continuing in bounded sequence with Slice 10 active)**.

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

Support real shared deployment with explicit policy boundaries.

**Key outputs**

- Baseline authentication and user-role model
- Visibility and authority rules at workspace and object levels
- Deployment guidance for NAS and VPS environments
- Backup, restore, and operational baseline for self-hosting

**Why it matters**

Noema is meant to be reusable by others and deployable in real environments. This phase makes the project truly multi-user, governable, and practical to self-host beyond a single experimental setup.
