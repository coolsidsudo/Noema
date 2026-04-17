# Noema Deployment Hardening and Profile Guidance Baseline

## Purpose and boundary

This document defines the stable baseline semantics for deployment hardening and deployment-profile guidance in Noema.

This stable system-definition document is produced for **Phase 6 Slice 4 (accepted prior substantive slice)** and extends accepted Phase 6 semantics without redefining them.

The slice is intentionally semantics-first and implementation-light. It defines what hardening means in Noema terms, which hardening concern categories are baseline-relevant in self-hosted operation, and how operator-selected deployment profiles should be interpreted.

This slice does **not** define concrete credential protocols, detailed network/TLS/perimeter engineering, container/Kubernetes implementation specifics, full production SRE playbooks, or managed-service-dependent architecture.

## Why this slice follows accepted Phase 6 work

Accepted Phase 6 slices already established:

- **Slice 1:** access/authority semantics
- **Slice 2A:** authentication and identity provisioning semantics
- **Slice 2B:** self-hosted deployment and operations baseline semantics

Slice 3 then refined backup/restore continuity guidance at baseline depth.

Phase 6 Slice 4 defines deployment hardening/profile guidance as a bounded semantic layer so operators can choose stronger deployment posture without collapsing established policy, identity, deployment, or continuity meanings.

In baseline terms:

- prior slices define **policy, identity, deployment, and continuity semantics**
- this slice defines **how hardening posture is interpreted across operator-selected exposure profiles**

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-access-authority-baseline.md`
- `docs/noema-auth-identity-provisioning-baseline.md`
- `docs/noema-self-hosted-deployment-operations-baseline.md`
- `docs/noema-backup-restore-operational-guidance-baseline.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Core invariants for hardening/profile semantics

The following invariants are normative for this slice:

1. **Hardening semantics are additive safeguards, not semantic replacement of prior slices.**
2. **Deployment profile is an operator-selected exposure/operating posture, not a substitute for identity, authority, or visibility policy.**
3. **Baseline-required hardening expectations apply across all conformant deployments.**
4. **Stronger hardening profiles may add safeguards, but must not weaken baseline-required expectations.**
5. **No hardening profile may bypass accepted policy, identity, or auditability semantics.**
6. **Self-hosted NAS/VPS practicality remains required; profile guidance must stay practical for operator-controlled hosting.**

## What “deployment hardening” means in Noema terms

At baseline depth, deployment hardening means: 

- reducing avoidable exposure and abuse paths for deployed Noema systems
- preserving policy/authentication/attribution integrity under real operational conditions
- constraining administrative and change paths to reduce accidental or unauthorized impact
- maintaining continuity-sensitive safeguards so recovery posture is not silently undermined

Hardening in this slice is semantic and categorical. It identifies required safeguard classes and profile posture expectations, without prescribing exact stack or tooling implementations.

## Baseline-required hardening expectations vs profile-selectable strengthening

### Baseline-required expectations (all deployment profiles)

At baseline depth, every Noema deployment should uphold all of the following, regardless of selected profile:

1. **Exposure intentionality**
   - active service exposure boundaries are explicit, operator-chosen, and reviewable
2. **Identity and access-path integrity**
   - accepted Slice 1 and Slice 2A semantics remain enforceable under actual deployment access paths
3. **Administrative path protection**
   - administrative/change-capable paths are explicitly bounded and not treated as ambient/default access
4. **Secret/config handling posture**
   - sensitive configuration and credential material is handled as controlled operational state, not casual plaintext sprawl
5. **Change/update safeguards**
   - update and configuration changes follow an operator-governed path that preserves continuity and rollback awareness
6. **Audit/log continuity posture**
   - security-relevant operational activity remains attributable and retained according to operator policy compatible with baseline governance needs
7. **Recovery-sensitive safeguard continuity**
   - hardening posture does not silently invalidate backup/restore coherence expectations from Slice 3

### Profile-selectable strengthening (operator choice)

Operators may choose stronger profiles that tighten boundaries beyond baseline-required posture. Stronger profiles may add stricter controls, higher verification frequency, narrower exposure windows, or tighter administrative constraints.

Normative rule: stronger profile posture is valid only when it remains semantically consistent with accepted access/authority, identity/auth, deployment/operations, and backup/restore baselines.

## Deployment profile guidance semantics

Deployment profiles are semantic operating-context categories that help operators reason about expected hardening posture.

### Profile A: LAN-constrained/local-trust-minimized

Typical context:

- local or LAN-focused deployment
- limited direct remote/public exposure

Guidance semantics:

- prioritize explicit local exposure boundaries
- avoid treating “inside LAN” as equivalent to policy trust bypass
- preserve full identity/auth and authority semantics for local actors
- apply baseline-required hardening expectations as non-optional

### Profile B: mediated remote exposure (VPN/reverse-proxy/front-door mediated)

Typical context:

- remote access mediated through operator-selected access layer
- exposure is present but intentionally bounded through mediation

Guidance semantics:

- preserve attribution and policy semantics end-to-end across mediation layers
- maintain clear accountability for where authentication and authorization decisions occur
- protect administrative paths from accidental broad exposure
- keep mediated exposure assumptions explicit and auditable

### Profile C: direct public-exposed deployment

Typical context:

- internet-reachable service endpoints
- elevated adversarial exposure likelihood

Guidance semantics:

- treat exposure surface minimization and administrative path separation as high-priority posture
- use stronger operator-selected safeguards beyond baseline where feasible
- preserve strict policy/auth/audit semantics under public-path operation
- ensure update/change and recovery-sensitive safeguards are deliberately managed

### Profile D: tighter shared deployment (higher governance sensitivity)

Typical context:

- multi-human/multi-agent shared environments with stronger governance needs
- elevated sensitivity around authority boundaries, history continuity, and operational accountability

Guidance semantics:

- prioritize least-privilege interpretation of authority and admin paths
- strengthen audit/log retention and review posture consistent with governance needs
- emphasize explicit change control and continuity validation cadence
- maintain profile consistency with self-hosted practicality (no mandatory enterprise-only assumptions)

## Minimum hardening concern categories (baseline semantics)

This slice establishes the following baseline concern categories as mandatory semantic coverage classes.

### 1) Exposure surface posture

At baseline depth, operators explicitly define and periodically validate intended exposure surfaces for human and machine paths. Unintended exposure is treated as non-baseline posture.

### 2) Secret and sensitive configuration handling posture

Sensitive configuration state (for example credentials, tokens, or equivalent secret material) is treated as controlled state with explicit operator stewardship. Hardening posture should avoid uncontrolled duplication or disclosure pathways.

### 3) Administrative path protection

Administrative capabilities (deployment changes, policy-impacting operations, identity provisioning changes, apply-capable workflows) must be constrained with tighter handling than ordinary read/use paths.

### 4) Update/change safeguards

Changes that can impact security, policy integrity, availability, or continuity should follow an explicit operator-governed path with traceable intent and practical rollback/recovery awareness.

### 5) Audit/log retention posture

Operational and governance-relevant records should be retained in a way that preserves attribution and supports post-change/post-incident interpretation at baseline depth, subject to visibility/sensitivity policy.

### 6) Recovery-sensitive safeguards

Hardening posture should preserve recoverability semantics, including coherent restore expectations and continuity of policy/identity/governance interpretation defined in Slice 3.

## Relationship to accepted baseline semantics

This slice is additive and non-redefining.

### Relationship to access/authority baseline (Slice 1)

Hardening profile posture does not alter the meaning of visibility or authority. It constrains deployment risk conditions around those meanings.

### Relationship to auth/identity provisioning baseline (Slice 2A)

Hardening profile posture does not redefine identity classes, authentication semantics, or provisioning lifecycle semantics. It strengthens operational conditions that protect those semantics.

### Relationship to deployment/operations baseline (Slice 2B)

This slice refines the previously deferred hardening area into bounded semantic guidance while preserving single-node-first, self-hosted NAS/VPS practicality and operator-controlled hosting assumptions.

### Relationship to backup/restore guidance baseline (Slice 3)

Hardening is constrained by continuity coherence: safeguards should improve operational resilience without making restore posture opaque, unverifiable, or semantically inconsistent with established recovery guidance.

## Operator responsibility boundaries (baseline depth)

At baseline depth, operators are responsible for:

1. selecting and documenting an intended deployment profile posture
2. meeting all baseline-required hardening expectations regardless of profile
3. choosing stronger safeguards where exposure/governance context warrants
4. maintaining explicit protection for administrative/change-capable paths
5. maintaining accountable handling of secrets and sensitive configuration state
6. preserving auditability and retention posture sufficient for governance continuity
7. ensuring hardening choices remain compatible with backup/restore coherence
8. communicating known posture limitations to deployment stakeholders

In small deployments these responsibilities may be held by one person; semantics remain unchanged.

## Explicit non-goals and deferrals

This slice does **not** define or implement:

- concrete TLS/network/perimeter architecture or certificate operations
- concrete credential protocol mechanics (token/session/password internals)
- platform-specific hardening benchmarks or CIS/STIG mapping detail
- container/Kubernetes runtime hardening implementation
- detailed vulnerability management tooling/process definition
- full incident response or forensics playbook design
- external managed-service dependency assumptions
- redefinition of accepted Slice 1, Slice 2A, Slice 2B, or Slice 3 semantics

These concerns remain deferred to later bounded implementation guidance or future semantic slices if required.

## Drift-check statement

This slice preserves:

- open-source reusable framing
- self-hosted NAS/VPS practicality
- multi-human and multi-agent support assumptions
- editor-agnostic posture
- Obsidian-compatible but not Obsidian-dependent posture
- strict separation of domain, profile, workspace/project, content type, visibility, authority, identity/auth, deployment/operations, hardening/profile posture, and backup/recovery continuity semantics

## Next-slice pointer

After this deployment hardening/profile guidance baseline semantics slice, the next bounded follow-on should focus on **implementation-constrained conformance guidance and validation posture for selected hardening concerns**, while preserving accepted semantics and avoiding implementation-stack lock-in.
