# Noema Backup and Restore Operational Guidance Baseline

## Purpose and boundary

This document defines the stable baseline semantics for backup and restore operational guidance in Noema.

This stable system-definition document is produced for **Phase 6 Slice 3 (current implementation slice under review)** and follows accepted **Phase 6 Slice 1 (access/authority)**, **Slice 2A (authentication/identity provisioning)**, and **Slice 2B (self-hosted deployment/operations baseline)** semantics.

The slice is intentionally semantics-first and implementation-light. It defines what continuity means at baseline depth for backup scope, restore coherence, verification posture, and operator readiness in self-hosted environments.

This slice does **not** define backup tooling implementation, vendor-specific storage/snapshot systems, detailed disaster-recovery engineering, production SRE objectives, or deployment hardening internals.

## Why this slice follows Phase 6 Slice 2B

Phase 6 Slice 2B established the baseline self-hosted deployment/operations posture and introduced continuity expectations at a high level. The next bounded continuation is to refine backup/restore meaning into explicit operational guidance so continuity expectations become clearer and more inspectable before hardening/profile internals are designed.

In baseline terms:

- Slice 2B answers **where/how Noema is operated** in self-hosted NAS/VPS-practical terms.
- Slice 3 answers **what continuity artifacts must be preserved**, **what counts as coherent recovery**, and **how operators keep restore readiness credible** at baseline depth.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-access-authority-baseline.md`
- `docs/noema-auth-identity-provisioning-baseline.md`
- `docs/noema-self-hosted-deployment-operations-baseline.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Core model invariants (Phase 6 Slice 3)

The following invariants are normative for this baseline:

1. **Backup/restore semantics are continuity semantics, not deployment-topology design.**
2. **Restore coherence must preserve accepted policy and identity semantics, not only file presence.**
3. **Backup scope must include both knowledge artifacts and continuity-critical governance/operational state at baseline depth.**
4. **Verification posture must include recoverability confidence, not merely backup-job completion claims.**
5. **Operator responsibility for cadence and restore readiness is explicit in self-hosted posture.**

## Backup scope semantics (baseline depth)

Backup scope in this slice is defined as continuity coverage classes, not tool-specific implementation detail.

### Required coverage classes

At baseline depth, operator backup posture should cover at least:

1. **Knowledge artifact classes**
   - `raw/` source-facing inputs and attachments
   - `structured/` canonical curated artifacts
   - `proposals/` reviewable candidate changes
   - `logs/` append-oriented operational records
2. **Workspace/project continuity state**
   - workspace-organization state needed to recover active project context
   - index/catalog and relationship traceability artifacts needed for navigability at baseline depth
3. **Policy/auth-related continuity state**
   - policy definitions/bindings that preserve accepted Slice 1 visibility/authority meaning
   - identity and provisioning continuity state required to preserve accepted Slice 2A attribution semantics
4. **Operational baseline state**
   - baseline deployment/operation configuration state needed to recover accepted Slice 2B posture

Equivalent storage layouts are valid if they preserve these semantic coverage classes.

### Coverage posture clarifications

- Backup scope is **not** limited to Markdown content files if governance/identity continuity state exists elsewhere.
- Backing up only runtime binaries or only content artifacts is non-baseline posture.
- Backup scope should preserve inspectable continuity for multi-human and multi-agent workspaces.

## Restore semantics (baseline depth)

Restore semantics define what outcomes count as coherent continuity recovery.

### Coherent restore definition

At baseline depth, a restore is coherent when recovered state allows Noema operation without semantic contradiction across:

1. knowledge artifacts (raw/structured/proposals/logs)
2. workspace/project organization context
3. visibility/authority policy posture
4. identity/auth attribution continuity
5. baseline deployment/operations posture expected by Slice 2B

A restore that brings files back but breaks accepted policy/auth semantics is not considered fully coherent.

### Full vs partial restore posture

This slice distinguishes two recovery postures:

- **Full restore posture**
  - intended to re-establish a deployment/workspace in continuity-complete form
  - expected to preserve governance and attribution continuity alongside content
- **Partial restore posture**
  - allowed for bounded recovery purposes (for example selected artifact classes or selected workspaces)
  - must be explicitly recognized as partial and should not be represented as full continuity restoration

Normative baseline expectation: operators should know which restore paths are full-capable versus partial-only and communicate that distinction explicitly.

### Governance/history continuity expectations

At baseline depth, restored environments should preserve enough history/governance continuity to keep shared operation accountable.

Expected posture includes:

- durable attribution continuity for human/agent/service-originated actions where history exists
- preservation of accepted/proposed lifecycle context at baseline traceability depth
- preservation of policy/identity references needed to interpret past decisions and current authority state

This slice does not require complete enterprise forensic retention or legal-hold frameworks.

## Backup integrity and verification posture

Backup readiness is defined by recoverability confidence rather than schedule completion alone.

### What operators should verify at baseline depth

Operators should verify at baseline depth that:

1. expected coverage classes are present in backup outputs
2. backup artifacts are readable/inspectable with ordinary tools
3. baseline restore paths can reconstruct coherent operational posture
4. recovered state preserves policy/auth attribution meaning at baseline continuity depth
5. integrity checks used by the operator (for example checksums/manifests) are consistently applied

### Inspectability and portability expectations

Consistent with Noema baseline principles:

- backup artifacts should remain inspectable by operators without opaque vendor lock-in assumptions
- backup posture should remain portable enough for NAS/VPS-practical self-hosted continuity
- continuity confidence should not depend on hidden proprietary control-plane state at baseline depth

This does not prohibit using managed services; it constrains baseline semantics so continuity meaning remains operator-governable.

## Recovery-point and recovery-time posture (qualitative)

This slice defines qualitative continuity expectations only.

### Recovery-point posture (qualitative)

Operators should maintain a cadence that limits unacceptable loss of recent meaningful knowledge/governance changes for their workspace risk profile.

### Recovery-time posture (qualitative)

Operators should maintain readiness such that restore to usable baseline operation is feasible within a bounded, operator-understood timeframe appropriate to deployment criticality.

No quantitative RPO/RTO targets are defined in this slice.

## Baseline operator responsibilities

At baseline depth, operator responsibilities include:

1. defining and maintaining backup cadence suitable for workspace continuity needs
2. ensuring required continuity coverage classes are included
3. maintaining restore procedures that distinguish full vs partial recovery paths
4. periodically validating restore readiness (not only backup job success)
5. retaining enough operational documentation to execute recovery without hidden assumptions
6. communicating continuity posture and known limitations to workspace stakeholders

In small deployments these responsibilities may be held by one person; semantics remain the same.

## Relationship to accepted deployment baseline (Slice 2B)

This slice is additive and non-redefining.

- `docs/noema-self-hosted-deployment-operations-baseline.md` remains authoritative for baseline deployment and operations posture.
- This slice refines the backup/restore portion of that posture into stable, explicit operational guidance semantics.
- Nothing in this slice redefines accepted Slice 1 or Slice 2A semantics; restore coherence depends on preserving them.

## Explicit non-goals and deferred concerns

This slice does **not** define or implement:

- backup tooling implementation details or job orchestration internals
- vendor-specific storage/snapshot systems
- detailed disaster-recovery engineering playbooks
- production SRE objectives, quantitative RPO/RTO, or incident-command procedures
- deployment hardening/profile design internals
- cryptographic key-management or secret-rotation engineering specifics
- redefinition of accepted Slice 1, Slice 2A, or Slice 2B semantics

These concerns are intentionally deferred to later bounded Phase 6 follow-on slices.

## Drift-check statement

This slice preserves:

- open-source reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support assumptions
- editor-agnostic posture
- Obsidian-compatible but not Obsidian-dependent posture
- strict separation of domain, profile, workspace/project, content type, visibility, authority, identity/auth, deployment, and backup/recovery concerns

## Next-slice pointer

After Phase 6 Slice 3 baseline adoption, the next bounded Phase 6 follow-on slice should focus on **deployment hardening/profile guidance** while preserving the accepted semantics from Slices 1, 2A, 2B, and 3.
