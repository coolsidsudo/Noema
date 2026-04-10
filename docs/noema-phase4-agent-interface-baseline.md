# Noema Phase 4 Agent Interface Baseline (Slice 1)

## Purpose and boundary

This document defines the first bounded Phase 4 baseline for machine-facing agent interaction in Noema.

The slice is intentionally documentation-first and interface-definition-first. It defines what agent users may read/query and how they may submit proposals while preserving Noema's accepted architecture semantics.

This baseline does **not** grant direct canonical-write authority to agents and does **not** require any specific transport, runtime, or deployment packaging.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `docs/noema-index-catalog-baseline.md`
- `docs/noema-phase3-human-client-baseline.md`
- `control/development-plan.md`
- `control/workflow-baseline.md`

## Phase 4 objective (Slice 1)

Define the minimum practical machine-facing interface layer for agent users to participate safely in Noema through bounded read/query and proposal submission paths.

## Agent user types at baseline

Noema supports multiple agent users with explicit identity and scoped behavior. At baseline, these categories are sufficient:

1. **Reader agents**
   - Consume discoverable object metadata and object content through bounded read/query interfaces.
   - Do not submit modifications directly.

2. **Analyst agents**
   - Perform bounded query operations over cataloged raw/structured/proposal/log records.
   - May produce analysis outputs external to canonical storage unless explicitly submitted as proposals.

3. **Contributor agents**
   - Can submit proposal objects that target raw/structured objects.
   - Cannot directly publish canonical structured updates.

4. **Maintainer-support agents (bounded)**
   - Can assist with maintenance-oriented query and proposal generation.
   - Remain review-bounded in this slice; maintainer workflow automation is deferred to Phase 5.

These are behavioral categories, not hard-coded product roles.

## Bounded read/query interface expectations

The baseline machine-facing read/query surface should expose bounded operations over existing objects and metadata.

### Required capability shape

At baseline, agent interfaces should support:

- **Get by ID** for known object IDs.
- **List/filter** by workspace, class, status, timestamps, and lightweight metadata cues (for example `title`, `tags`).
- **Traceability-oriented retrieval** of direct relationship pointers (for example support/target/result/event linkage cues).
- **Catalog-aware pagination and bounded result size** to prevent unbounded scans.

### Read/query boundaries

- Read/query access is policy-scoped by workspace and object visibility.
- Query responses should expose only allowed objects/fields for the requesting agent scope.
- Interfaces should avoid granting arbitrary filesystem traversal semantics.
- Query semantics should map to Noema object classes and metadata conventions, not ad hoc per-client schemas.

### Baseline query posture

This slice defines interface expectations, not a single query language. Implementations may use REST, RPC, local service APIs, or other bounded forms if they preserve equivalent semantics and policy boundaries.

## Proposal submission interface expectations

Agent write participation at baseline is limited to **proposal submission**.

### Required capability shape

A bounded proposal submission path should require, at minimum:

- proposer identity (`created_by`) with stable agent attribution
- proposal class/status metadata aligned with baseline profile
- target object reference(s) (`target_ids` or equivalent)
- explicit rationale and intended effect
- workspace scope

### Proposal submission outcomes

- Successful submission creates/updates a **proposal object**, not canonical structured state.
- Proposal lifecycle state remains explicit (`draft`, `under_review`, `accepted`, `rejected`, `withdrawn`).
- Review and apply steps remain separate from submission.

### Authority boundary

- Agent submission authority is limited to proposal-layer artifacts in this slice.
- Canonical structured publish/update authority remains human-governed review/apply.

## MCP-style posture and equivalent bounded API posture

Noema supports MCP-style interfaces as one valid transport/protocol shape for bounded machine interaction.

Baseline posture:

- MCP-style tool exposure is supported for read/query and proposal submission.
- Equivalent bounded API surfaces (for example HTTP or local service endpoints) are equally valid.
- Noema is **not MCP-only**; protocol choice must not redefine core semantics.
- Protocol adapters should preserve consistent identity, scope, and audit behavior.

In other words: protocol is replaceable; semantics are not.

## Agent identity model (baseline depth)

Agent operations must be attributable. At baseline:

- Every machine action should map to a stable agent identity.
- Agent identities should be namespaced and durable (for example `agent:<id>`), consistent with metadata conventions.
- Agent identity should be distinguishable from human identity in logs and proposal metadata.
- Optional execution context identifiers (session/run/request IDs) may be attached for stronger traceability.

This slice does not define full auth provisioning, credential lifecycle, or enterprise identity federation.

## Agent scope/permission model (baseline depth)

Agent scope is explicit and bounded across at least these axes:

- workspace scope (which workspace/project instances may be accessed)
- class scope (which object classes may be read/query/submitted against)
- operation scope (read/query only vs read/query + proposal submission)
- field/detail scope when sensitive metadata needs minimization

Baseline permission examples:

- Agent A: read/query `structured` and `proposals` in workspace `w1`
- Agent B: read/query all classes in `w2`; submit proposals targeting `structured` in `w2`
- Agent C: read/query only approved/active canonical slices, no proposal authority

This slice defines scope semantics, not a finalized policy engine.

## Auditability and attribution requirements

Machine participation must remain reviewable.

At baseline:

- Proposal submissions must record agent identity, timestamp, and target references.
- Query and submission operations should generate log records or equivalent auditable events.
- Review decisions affecting machine-submitted proposals should be traceable to reviewer identity and decision time.
- Accepted proposals should map to concrete structured outcomes and corresponding log events.

These requirements align with the raw -> structured -> proposals -> logs traceability chain already established.

## Relationship to raw / structured / proposals / logs

Phase 4 baseline preserves established class semantics:

- **Raw**: source-facing evidence inputs available for bounded read/query.
- **Structured**: canonical artifacts available for bounded read/query; not directly writable by agents in this slice.
- **Proposals**: machine/human candidate changes; primary write surface for agent contributions.
- **Logs**: operational and decision history supporting attribution and auditability.

Agent interfaces consume and produce class-aligned objects; they do not redefine object classes.

## Non-goals and deferred concerns

This slice explicitly does **not** define or implement:

- full authentication, user management, or credential lifecycle (Phase 6)
- deployment packaging/runtime hardening choices (Phase 6)
- full maintainer/compiler automation workflows (Phase 5)
- direct canonical structured-write authority for agents
- replacement of Noema semantics with one protocol implementation
- domain-specific or personal-only machine interface behavior
- final query language standardization across all implementations

## Drift checks for this slice

This baseline explicitly avoids:

- redefining object classes (`raw`, `structured`, `proposals`, `logs`)
- redefining metadata profile semantics
- redefining relationship/traceability semantics
- redefining index/catalog semantics
- changing Phase 3 human client semantics
- mixing repository development workflow content into system-definition semantics

## Next-slice pointer

After this Phase 4 Slice 1 baseline, the next planned execution pointer remains:

- **Phase 5 — Maintainer workflow baseline**
