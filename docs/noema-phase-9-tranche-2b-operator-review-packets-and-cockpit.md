# Noema Phase 9 Tranche 2B — Operator Review Packets and Markdown Review Cockpit

## Purpose

Phase 9 Tranche 2B adds a deterministic operator review packet model and a Markdown review cockpit over proposals, evidence/provenance references, logs, apply visibility, recovery signals, and conservative readiness classifications.

Review packets are derived, read-only visibility artifacts. They compile existing repo metadata into operator-facing context; they do not approve, reject, apply, mutate, publish, or create authority.

## Generated location

The existing operator projection command now also writes review cockpit pages under:

```text
<workspace-root>/projection/operator/review/
```

Generated files:

- `index.md`
- `queue.md`
- `attention.md`
- `readiness.md`
- `recovery.md`
- `packets/<safe-proposal-id>.md`

The parent operator index also links to `./review/index.md`.

## Rebuild command

```bash
python -m packages.noema_operator.cli build-projections --repo-root . --workspace examples/workspaces/sample-research-workspace/workspaces/ai-literature-mapping
```

The command remains filesystem/repo-backed. It does not require an HTTP server, `.obsidian`, an Obsidian API, or an Obsidian URI helper.

`--workspace` retains the Phase 9 Tranche 2A behavior: it may be a repo-relative workspace path, an absolute workspace path, or a known workspace id under the sample workspace layout. Workspace filtering remains an exact frontmatter `workspace` match to the resolved workspace id.

## Review packet extraction

A review packet represents one workspace-scoped proposal record. The packet includes:

- proposal identity, source path, status, title, creator, and creation time;
- target ids, resolved target records, and missing target ids;
- evidence/provenance ids, resolved evidence records, and missing evidence ids;
- related logs with relation labels;
- apply evidence logs and recovery evidence logs;
- all readiness classifications plus one primary classification;
- deterministic attention flags;
- packet-specific operator next steps;
- deterministic packet filename.

The packet model is in-memory only. It is rebuilt from current records and is not stored as a canonical Noema object.

## Matching rules

### Proposal identity

- Use `proposal_id` when present.
- Fall back to `id`.
- If both are absent, include the proposal with a deterministic path-derived fallback id and classify it conservatively.

### Target references

Candidate proposal fields:

- `target_ids`
- `target_id`
- `affected_objects`
- `affected_object_ids`
- `object_ids`

References resolve against workspace-scoped record `id` metadata. Unresolved references become `missing_target_ids`.

### Evidence/provenance references

Candidate proposal fields:

- `evidence`
- `evidence_ids`
- `provenance`
- `source_ids`
- `sources`
- `supports`
- `supporting_raw_ids`
- `support_raw_ids`

References resolve against workspace-scoped record `id` metadata. Unresolved references become `missing_evidence_ids`. Freeform body text is not parsed.

### Related logs

A log is related to a packet only when metadata explicitly references the proposal id or one of the packet target ids through:

- `records_event_for`
- `proposal_id`
- `target_ids`
- `affected_objects`
- `affected_object_ids`
- `object_ids`

Relation labels are preserved as:

- `references_proposal`
- `references_target`
- `apply_evidence`
- `recovery_evidence`

### Apply evidence

A log counts as apply evidence only when it is already related to the packet and also has apply-like metadata in `event_type`, `event_class`, `operation`, `apply_status`, `apply_state`, or `canonical_change_mode`.

Recognized apply-like values include accepted apply/reconcile conventions such as `apply_reconciliation`, `apply_started`, `apply_step_succeeded`, `apply_completed`, `apply_deferred`, `apply_resumed`, `apply_correction`, `apply_update`, `reconcile`, `reconciliation`, apply state values, and `policy-gated-direct-apply`.

### Recovery evidence

A log counts as recovery evidence only when it is already related to the packet and also has explicit recovery/failure/rollback/manual-intervention metadata in fields such as `recovery_status`, `recovery_action`, `event_type`, `operation`, `result`, `apply_status`, `apply_state`, `step_state`, or `status`.

Recognized signals include failure, deferred, rollback, manual intervention, recovery, retry, resume, correction, superseding attempt, abandon/abandoned, and compensation markers.

## Readiness classifications

A packet can have multiple classifications. The first classification by fixed severity order is the primary classification used for queue sorting.

Severity order:

1. `blocked_missing_targets`
2. `blocked_missing_evidence`
3. `recovery_attention_needed`
4. `accepted_without_apply_evidence`
5. `unknown_status`
6. `ready_for_human_review`
7. `draft_not_ready`
8. `apply_evidence_present`
9. `rejected_or_withdrawn_terminal`

Readiness is informational operator visibility. It is not a review decision, approval, rejection, apply result, or policy override.

## Attention flags

Attention flags are deterministic and sorted by fixed order:

1. `missing_proposal_id`
2. `missing_target_reference`
3. `target_references_absent`
4. `missing_evidence_reference`
5. `evidence_references_absent`
6. `accepted_without_apply_evidence`
7. `recovery_signal_present`
8. `unknown_status`

Flags drive checklist generation and attention pages; they do not mutate source records.

## Packet filenames and stale cleanup

Packet filenames are deterministic:

- lowercase proposal id;
- replace unsafe characters with `-`;
- collapse repeated separators;
- strip leading/trailing separators;
- empty slug becomes `proposal`;
- collisions are suffixed deterministically with `-2`, `-3`, and so on.

The `projection/operator/review/packets/` directory is treated as generated output. Before current packet pages are written, existing `*.md` files in that directory are removed. No files outside that generated packet directory are deleted.

## Markdown cockpit pages

The cockpit pages are generated from review packets, not by re-deriving readiness logic in the renderer.

- `index.md` summarizes counts, attention, and review links.
- `queue.md` lists one row per proposal packet.
- `attention.md` surfaces blockers, missing references, and recovery attention.
- `readiness.md` documents classifications and groups packets.
- `recovery.md` separates accepted proposals with and without visible apply evidence and lists recovery signals.
- Per-packet pages link to source proposal, target/evidence/log records, missing references, classifications, attention flags, and operator next steps.

All links are relative Markdown links. Generated Markdown does not include absolute local filesystem paths.

## Obsidian-friendly, not Obsidian-dependent

The cockpit is plain Markdown. Obsidian can browse it as a first-class Markdown client, but Noema remains the governed system/service layer. Opening, editing, or viewing a projection file does not confer authority.

## Explicitly out of scope

This tranche does not implement:

- proposal approval command;
- proposal rejection command;
- canonical apply command;
- canonical object mutation;
- proposal or log mutation;
- new service-core operations or semantic changes;
- HTTP adapter changes;
- Obsidian plugin/API/URI integration;
- native web UI;
- MCP;
- auth, TLS, CORS, or public deployment hardening;
- broad search/RAG/chat behavior.

## Known limits

Metadata matching is intentionally conservative. Nested proposal payloads and freeform Markdown bodies are not parsed as evidence/log linkage. If a proposal or log does not expose explicit metadata references, it will not be inferred into a packet relation.
