# Noema Self-Hosted Deployment and Operations Baseline

## Purpose and boundary

This document defines the stable baseline semantics for self-hosted deployment posture and operational responsibilities in Noema.

This stable system-definition document is produced for **Phase 6 Slice 2B (current implementation slice under review)** and follows accepted **Phase 6 Slice 1** access/authority semantics and **Phase 6 Slice 2A** authentication/identity provisioning semantics.

The slice is intentionally semantics-first and implementation-light. It defines what baseline self-hosted deployment means, what operators should expect to run and preserve, and which concerns are explicitly deferred.

This slice does **not** implement deployment scripts, container orchestration profiles, production hardening internals, or detailed network/security engineering.

## Why this slice follows Slice 1 and Slice 2A

Phase 6 Slice 1 established policy semantics for visibility and authority. Phase 6 Slice 2A established durable actor identity, authentication meaning, and provisioning posture. Deployment and operations semantics now follow so these accepted policy layers can run coherently in real self-hosted environments.

In baseline terms:

- Slice 1 answers **what operations are policy-allowed**.
- Slice 2A answers **who the authenticated actors are**.
- Slice 2B answers **where and how Noema runs operationally under operator control**.

Without Slice 2B, accepted policy and identity semantics are under-specified for practical NAS/VPS-style operation.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-access-authority-baseline.md`
- `docs/noema-auth-identity-provisioning-baseline.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Core model invariants (Phase 6 Slice 2B)

The following invariants are normative for this baseline:

1. **Noema baseline deployment is single-node-first and operator-controlled.**
2. **NAS/VPS practicality is a design requirement, not an optional profile.**
3. **Human-facing and machine-facing access paths both exist at baseline depth.**
4. **Storage/workspace artifacts remain portable and inspectable.**
5. **Backup/restore semantics prioritize continuity of canonical knowledge and governance history.**
6. **Deployment posture must not redefine accepted Slice 1 or Slice 2A semantics.**

## Baseline deployment posture

### Single-node-first semantics

At baseline depth, Noema assumes a practical single-node deployment model before multi-node topology concerns.

Single-node-first means:

- one operator-managed host is sufficient for baseline operation
- all core baseline components can be run coherently on that host
- later scale-out patterns are deferred rather than implied as baseline requirements

This posture keeps the system usable for early real deployments and avoids forcing enterprise infrastructure assumptions.

### NAS/VPS practicality semantics

Baseline deployment must remain practical on:

- **NAS-class self-hosted environments** (home/lab/team-controlled storage-centric hosts)
- **VPS-class environments** (single operator-managed remote host)

Practicality means the baseline model assumes ordinary operator control over storage, process execution, backup scheduling, and access exposure choice.

### Operator-controlled hosting semantics

Noema baseline assumes hosting control belongs to the operator/administrator of the deployment context.

At baseline depth, operator control includes:

- choosing host environment and runtime shape
- deciding exposure boundaries (LAN, VPN, reverse proxy, or public domain)
- establishing operational maintenance, backup, and upgrade cadence
- retaining authority for local incident response and continuity decisions

## Core deployment components at baseline depth

This slice defines semantic component categories, not implementation stacks.

### 1) Storage and workspace content substrate

The deployment must preserve the Noema knowledge model classes (`raw`, `structured`, `proposals`, `logs`) and related workspace/project content in operator-controlled storage.

Baseline expectations:

- canonical artifacts are durably stored in an inspectable form
- workspace boundaries remain recoverable from stored state
- structured artifacts remain traceable to provenance/review context

### 2) Human-facing access path

A baseline deployment provides a human-facing path for browse/review/edit workflows under accepted policy semantics.

This may be realized through editor-compatible, web, CLI, or equivalent surfaces, but at baseline depth it must preserve:

- Slice 1 visibility/authority boundaries
- Slice 2A authenticated identity attribution
- reviewability of meaningful human-initiated changes

### 3) Machine-facing access path

A baseline deployment provides bounded machine interfaces for agent/service participation.

At baseline depth this path must preserve:

- explicit machine identity attribution (`agent`/`service` semantics from Slice 2A)
- scope-bounded read/query/proposal behavior
- policy enforcement from Slice 1 without bypass through deployment topology

### 4) Identity/auth integration posture

Deployment baseline includes operational availability of identity/auth behavior defined by Slice 2A.

Semantically, this means deployment must support:

- authenticated actor identification
- provisioned identity lifecycle continuity
- workspace scope attachment semantics

This slice does not prescribe concrete identity provider or credential-protocol implementation.

### 5) Operational logs and audit records

Baseline deployments must maintain operational records sufficient for governance continuity and troubleshooting at baseline depth.

Minimum semantic expectation:

- authenticated actor activity and key lifecycle transitions remain attributable
- proposal/review/apply outcomes remain traceable
- operational events relevant to continuity (for example backup/restore and upgrade operations) are loggable/auditable

## Baseline environment boundaries

Noema baseline keeps exposure as an operator decision while preserving policy semantics.

### Local/LAN baseline

A deployment may run as local/LAN-only. This is fully baseline-conformant if policy and identity semantics are preserved.

### VPN/reverse-proxy/public exposure as operator choice

A deployment may also be exposed through operator-chosen mechanisms such as VPN paths, reverse proxies, or public endpoints.

Normative semantic rule:

- exposure method changes **connectivity surface**, not core policy meaning
- Slice 1 and Slice 2A semantics remain authoritative regardless of exposure pattern

This slice does not define detailed network hardening, TLS architecture, or perimeter engineering internals.

## Backup and restore semantics (baseline depth)

Backup/restore is required for operational continuity semantics, not optional convenience.

### What must be restorable

At baseline depth, restore posture must preserve enough state to recover a coherent Noema deployment, including:

1. workspace/project content across knowledge object classes
2. canonical structured knowledge artifacts
3. proposal and review state needed for governance continuity
4. logs/audit records required for attributable history and operational traceability
5. policy-relevant configuration/state needed to re-establish effective visibility/authority and identity scope attachment

### What must remain portable and inspectable

Baseline portability/inspectability expectations include:

- knowledge artifacts are not trapped in opaque platform-only forms
- operators can inspect backed-up content and verify core object continuity
- migration between operator-controlled environments remains feasible without redefining system semantics

This baseline defines semantic requirements; it does not prescribe concrete backup tooling or scheduling implementations.

## Upgrade and change-management baseline posture

Noema baseline assumes ongoing change in software and operational configuration, managed by operators under continuity constraints.

Baseline semantics:

1. upgrades should preserve accepted policy and identity semantics
2. changes should avoid silent model drift across workspace/content/policy boundaries
3. rollback/recovery posture should exist where changes threaten continuity
4. change events affecting governance or availability should be operationally traceable

This slice does not define release engineering pipelines, compatibility matrix internals, or SRE-grade rollout mechanics.

## Operational responsibility boundaries

### Operator/admin responsibilities

At baseline depth, operator/admin responsibility includes:

- hosting/runtime stewardship for the deployment node
- access exposure decisions for local or remote operation
- backup/restore execution and verification posture
- upgrade/change execution and continuity safeguards
- identity admission/provisioning governance at deployment level (as defined by Slice 2A)
- workspace policy stewardship delegation model (as defined by Slice 1)

### What Noema assumes

Noema baseline assumes operators will:

- run deployment components under explicit local control
- maintain continuity artifacts required for recovery
- preserve attributable audit/operational history at baseline depth

### What Noema does not assume

Noema baseline does not assume:

- hyperscale infrastructure or multi-region architecture
- managed enterprise IAM/SRE platforms
- production-grade hardening internals being fully solved in this slice
- container/Kubernetes-specific deployment dependency

## Relationship to accepted access/auth semantics

This slice is additive and non-redefining.

- `docs/noema-access-authority-baseline.md` remains authoritative for visibility/authority meaning.
- `docs/noema-auth-identity-provisioning-baseline.md` remains authoritative for identity/auth/provisioning meaning.
- Deployment topology and operational choices must preserve—not override—those accepted semantics.

Normative clarification:

- filesystem or host-level access convenience is not itself policy authority
- network reachability is not equivalent to authenticated authorization

## Explicit non-goals and deferred concerns

This slice does **not** define or implement:

- deployment scripts or infrastructure-as-code implementations
- Docker/Kubernetes/container-orchestration specifics
- detailed TLS/perimeter/network hardening design
- secret-management and key-management internals
- performance engineering, autoscaling, or SRE internals
- deep production incident-response playbooks
- redefinition of accepted Slice 1 or Slice 2A semantics

These concerns are intentionally deferred to later bounded Phase 6 follow-on slices.

## Drift-check statement

This slice preserves:

- open-source reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support assumptions
- editor-agnostic posture
- Obsidian-compatible but not Obsidian-dependent posture
- strict separation of domain, profile, workspace/project, content type, visibility, authority, identity/auth, and deployment concerns

## Next-slice pointer

After Phase 6 Slice 2B baseline adoption, the next bounded Phase 6 follow-on slice should focus on one of:

1. backup/restore operational guidance refinement, or
2. deployment hardening/profile guidance

Selection should be based on the most substantive remaining semantic gap after Slice 2B review.
