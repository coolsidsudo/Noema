from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from packages.noema_maintainer.scan import ObjectRecord
from packages.noema_service.repository import filter_records, load_records

TARGET_REFERENCE_KEYS = (
    "target_ids",
    "target_id",
    "affected_objects",
    "affected_object_ids",
    "object_ids",
)
EVIDENCE_REFERENCE_KEYS = (
    "evidence",
    "evidence_ids",
    "provenance",
    "source_ids",
    "sources",
    "supports",
    "supporting_raw_ids",
    "support_raw_ids",
)
LOG_REFERENCE_KEYS = (
    "records_event_for",
    "proposal_id",
    "target_ids",
    "affected_objects",
    "affected_object_ids",
    "object_ids",
)

READINESS_CLASSIFICATION_ORDER = (
    "blocked_missing_targets",
    "blocked_missing_evidence",
    "recovery_attention_needed",
    "accepted_without_apply_evidence",
    "unknown_status",
    "ready_for_human_review",
    "draft_not_ready",
    "apply_evidence_present",
    "rejected_or_withdrawn_terminal",
)

ATTENTION_FLAG_ORDER = (
    "missing_proposal_id",
    "missing_target_reference",
    "target_references_absent",
    "missing_evidence_reference",
    "evidence_references_absent",
    "accepted_without_apply_evidence",
    "recovery_signal_present",
    "unknown_status",
)

RELATED_LOG_RELATION_ORDER = (
    "references_proposal",
    "references_target",
    "apply_evidence",
    "recovery_evidence",
)

PROPOSAL_STATUS_PRIORITY = {
    "under_review": 0,
    "draft": 1,
    "accepted": 2,
    "rejected": 3,
    "withdrawn": 4,
}
KNOWN_PROPOSAL_STATUSES = frozenset(PROPOSAL_STATUS_PRIORITY)
TERMINAL_NOT_REVIEWABLE_STATUSES = {"rejected", "withdrawn"}

APPLY_EVENT_VALUES = {
    "apply_reconciliation",
    "apply_started",
    "apply_step_succeeded",
    "apply_completed",
    "apply_deferred",
    "apply_resumed",
    "apply_correction",
    "apply_update",
    "reconcile",
    "reconciliation",
}
APPLY_STATE_VALUES = {"pending", "in_progress", "applied", "partial", "failed", "deferred"}
APPLY_CANONICAL_CHANGE_MODES = {"policy-gated-direct-apply"}
RECOVERY_VALUES = {
    "failed",
    "failure",
    "deferred",
    "rollback",
    "rolled_back",
    "manual_intervention",
    "manual-intervention",
    "recovery",
    "retry",
    "resume",
    "correction",
    "corrected",
    "supersede_attempt",
    "abandon",
    "abandoned",
    "compensation",
}

MISSING_VALUE = "—"


@dataclass(frozen=True)
class ReviewRecordRef:
    record_id: str
    object_class: str
    title: str
    status: str
    created_at: str
    updated_at: str
    path: Path


@dataclass(frozen=True)
class RelatedLogRecord:
    record: ReviewRecordRef
    relation_labels: tuple[str, ...]


@dataclass(frozen=True)
class ReviewPacket:
    proposal_id: str
    packet_filename: str
    proposal_path: Path
    proposal_status: str
    proposal_title: str
    created_by: str
    created_at: str
    target_ids: tuple[str, ...]
    resolved_target_records: tuple[ReviewRecordRef, ...]
    missing_target_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    resolved_evidence_records: tuple[ReviewRecordRef, ...]
    missing_evidence_ids: tuple[str, ...]
    related_log_records: tuple[RelatedLogRecord, ...]
    apply_evidence_records: tuple[RelatedLogRecord, ...]
    recovery_evidence_records: tuple[RelatedLogRecord, ...]
    readiness_classifications: tuple[str, ...]
    primary_classification: str
    attention_flags: tuple[str, ...]
    operator_next_steps: tuple[str, ...]


def _metadata_text(record: ObjectRecord, key: str) -> str:
    value = record.metadata.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _record_id(record: ObjectRecord) -> str:
    return _metadata_text(record, "id")


def _proposal_id_raw(record: ObjectRecord) -> str:
    return _metadata_text(record, "proposal_id") or _metadata_text(record, "id")


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _path_fallback_id(path: Path, repo_root: Path) -> str:
    return "missing-proposal-id-" + _slug_base(_repo_relative_path(path, repo_root).removesuffix(".md"))


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return sorted({str(item).strip() for item in value if str(item).strip()})
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _ids_from_keys(metadata: dict[str, object], keys: Iterable[str]) -> tuple[str, ...]:
    ids: set[str] = set()
    for key in keys:
        ids.update(_as_id_list(metadata.get(key)))
    return tuple(sorted(ids))


def _record_ref(record: ObjectRecord) -> ReviewRecordRef:
    return ReviewRecordRef(
        record_id=_record_id(record),
        object_class=record.object_class,
        title=_metadata_text(record, "title"),
        status=_metadata_text(record, "status"),
        created_at=_metadata_text(record, "created_at"),
        updated_at=_metadata_text(record, "updated_at"),
        path=record.path,
    )


def _record_sort_key(record: ObjectRecord) -> tuple[str, str, str, str]:
    return (_record_id(record).lower(), record.object_class, str(record.path), _record_id(record))


def _record_ref_sort_key(ref: ReviewRecordRef) -> tuple[str, str, str]:
    return (ref.record_id.lower(), ref.object_class, str(ref.path))


def _build_id_index(records: list[ObjectRecord]) -> dict[str, ObjectRecord]:
    indexed: dict[str, ObjectRecord] = {}
    for record in sorted(records, key=_record_sort_key):
        record_id = _record_id(record)
        if record_id and record_id not in indexed:
            indexed[record_id] = record
    return indexed


def _resolve_ids(ids: tuple[str, ...], by_id: dict[str, ObjectRecord]) -> tuple[tuple[ReviewRecordRef, ...], tuple[str, ...]]:
    resolved = []
    missing = []
    for object_id in ids:
        record = by_id.get(object_id)
        if record is None:
            missing.append(object_id)
        else:
            resolved.append(_record_ref(record))
    return tuple(sorted(resolved, key=_record_ref_sort_key)), tuple(sorted(missing))


def _normalized_token(value: object) -> str:
    return str(value).strip().lower().replace(" ", "_")


def _field_has_apply_signal(metadata: dict[str, object]) -> bool:
    for key in ("event_type", "event_class", "operation"):
        token = _normalized_token(metadata.get(key, ""))
        if token in APPLY_EVENT_VALUES or token.startswith("apply_") or token in {"reconcile", "reconciliation"}:
            return True
    for key in ("apply_status", "apply_state"):
        if _normalized_token(metadata.get(key, "")) in APPLY_STATE_VALUES:
            return True
    if _normalized_token(metadata.get("canonical_change_mode", "")) in APPLY_CANONICAL_CHANGE_MODES:
        return True
    return False


def _field_has_recovery_signal(metadata: dict[str, object]) -> bool:
    for key in ("recovery_status", "recovery_action"):
        if _normalized_token(metadata.get(key, "")) in RECOVERY_VALUES:
            return True
    for key in ("event_type", "operation", "result", "apply_status", "apply_state", "step_state", "status"):
        token = _normalized_token(metadata.get(key, ""))
        if token in RECOVERY_VALUES:
            return True
        if any(marker in token for marker in ("failed", "failure", "rollback", "manual_intervention", "recovery", "correction", "abandon", "compensation")):
            return True
    return False


def _related_log_record(log: ObjectRecord, proposal_id: str, target_ids: tuple[str, ...]) -> RelatedLogRecord | None:
    proposal_refs: set[str] = set()
    target_refs: set[str] = set()
    target_id_set = set(target_ids)

    for key in LOG_REFERENCE_KEYS:
        refs = set(_as_id_list(log.metadata.get(key)))
        if proposal_id in refs:
            proposal_refs.add(proposal_id)
        target_refs.update(refs & target_id_set)

    labels: list[str] = []
    if proposal_refs:
        labels.append("references_proposal")
    if target_refs:
        labels.append("references_target")
    if not labels:
        return None
    if _field_has_apply_signal(log.metadata):
        labels.append("apply_evidence")
    if _field_has_recovery_signal(log.metadata):
        labels.append("recovery_evidence")
    ordered_labels = tuple(label for label in RELATED_LOG_RELATION_ORDER if label in set(labels))
    return RelatedLogRecord(record=_record_ref(log), relation_labels=ordered_labels)


def _log_sort_key(log: RelatedLogRecord) -> tuple[int, str, str, str]:
    timestamp = log.record.updated_at or log.record.created_at
    return (0 if timestamp else 1, _invert_string(timestamp), log.record.record_id.lower(), str(log.record.path))


def _invert_string(value: str) -> str:
    # A deterministic descending string helper usable inside an ascending tuple sort.
    return "".join(chr(0x10FFFF - ord(char)) for char in value)


def _ordered_subset(values: set[str], order: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(item for item in order if item in values)


def _classify_packet(
    *,
    status: str,
    has_proposal_id: bool,
    target_ids: tuple[str, ...],
    missing_target_ids: tuple[str, ...],
    evidence_ids: tuple[str, ...],
    missing_evidence_ids: tuple[str, ...],
    apply_evidence_records: tuple[RelatedLogRecord, ...],
    recovery_evidence_records: tuple[RelatedLogRecord, ...],
) -> tuple[tuple[str, ...], str, tuple[str, ...]]:
    classifications: set[str] = set()
    flags: set[str] = set()
    normalized_status = status.strip()

    if not has_proposal_id:
        flags.add("missing_proposal_id")
    if normalized_status not in KNOWN_PROPOSAL_STATUSES:
        classifications.add("unknown_status")
        flags.add("unknown_status")

    if missing_target_ids:
        classifications.add("blocked_missing_targets")
        flags.add("missing_target_reference")
    if not target_ids and normalized_status not in {"draft", "rejected", "withdrawn"}:
        classifications.add("blocked_missing_targets")
        flags.add("target_references_absent")

    if missing_evidence_ids:
        classifications.add("blocked_missing_evidence")
        flags.add("missing_evidence_reference")
    if not evidence_ids and normalized_status in {"under_review", "accepted"}:
        classifications.add("blocked_missing_evidence")
        flags.add("evidence_references_absent")

    if recovery_evidence_records:
        classifications.add("recovery_attention_needed")
        flags.add("recovery_signal_present")

    if normalized_status == "accepted":
        if apply_evidence_records:
            classifications.add("apply_evidence_present")
        else:
            classifications.add("accepted_without_apply_evidence")
            flags.add("accepted_without_apply_evidence")
    elif normalized_status == "under_review":
        if not (missing_target_ids or missing_evidence_ids) and target_ids and evidence_ids and not recovery_evidence_records:
            classifications.add("ready_for_human_review")
    elif normalized_status == "draft":
        classifications.add("draft_not_ready")
    elif normalized_status in TERMINAL_NOT_REVIEWABLE_STATUSES:
        classifications.add("rejected_or_withdrawn_terminal")

    ordered_classifications = _ordered_subset(classifications, READINESS_CLASSIFICATION_ORDER)
    if not ordered_classifications:
        ordered_classifications = ("unknown_status",)
        flags.add("unknown_status")
    ordered_flags = _ordered_subset(flags, ATTENTION_FLAG_ORDER)
    return ordered_classifications, ordered_classifications[0], ordered_flags


def _next_steps(
    *,
    classifications: tuple[str, ...],
    attention_flags: tuple[str, ...],
    missing_target_ids: tuple[str, ...],
    missing_evidence_ids: tuple[str, ...],
) -> tuple[str, ...]:
    steps: list[str] = []
    if "target_references_absent" in attention_flags:
        steps.append("Add or confirm explicit target object references before review.")
    for target_id in missing_target_ids:
        steps.append(f"Resolve missing target object reference: {target_id}.")
    if "evidence_references_absent" in attention_flags:
        steps.append("Add or confirm evidence/provenance references before review.")
    for evidence_id in missing_evidence_ids:
        steps.append(f"Resolve missing evidence reference: {evidence_id}.")
    if "accepted_without_apply_evidence" in attention_flags:
        steps.append("Confirm whether accepted proposal has been applied or requires apply/recovery follow-up.")
    if "recovery_signal_present" in attention_flags:
        steps.append("Review related recovery/failure logs before further action.")
    if "ready_for_human_review" in classifications:
        steps.append("Review proposal rationale, target objects, evidence, and related logs.")
    if "draft_not_ready" in classifications:
        steps.append("Confirm draft is ready before routing to review.")
    if "rejected_or_withdrawn_terminal" in classifications:
        steps.append("Confirm terminal proposal state and inspect logs if follow-up is needed.")
    if "unknown_status" in classifications:
        steps.append("Clarify proposal status metadata before review.")
    if not steps:
        steps.append("Inspect packet context before taking operator action.")
    return tuple(steps)


def _slug_base(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "proposal"


def _assign_packet_filenames(packet_inputs: list[dict[str, object]]) -> None:
    used: set[str] = set()
    counts: dict[str, int] = {}
    for item in packet_inputs:
        slug = _slug_base(str(item["proposal_id"]))
        counts[slug] = counts.get(slug, 0) + 1
        ordinal = counts[slug]
        candidate_slug = slug if ordinal == 1 else f"{slug}-{ordinal}"
        while f"{candidate_slug}.md" in used:
            ordinal += 1
            counts[slug] = ordinal
            candidate_slug = f"{slug}-{ordinal}"
        filename = f"{candidate_slug}.md"
        used.add(filename)
        item["packet_filename"] = filename


def _packet_sort_components(item: dict[str, object]) -> tuple[int, int, int, str, str, str]:
    status = str(item["proposal_status"])
    classifications = item["readiness_classifications"]
    primary = classifications[0] if isinstance(classifications, tuple) and classifications else "unknown_status"
    created_at = str(item["created_at"])
    return (
        READINESS_CLASSIFICATION_ORDER.index(primary),
        PROPOSAL_STATUS_PRIORITY.get(status, 99),
        1 if not created_at else 0,
        created_at,
        str(item["proposal_id"]).lower(),
        str(item["proposal_path"]),
    )


def _build_packet_input(proposal: ObjectRecord, *, repo_root: Path, workspace_records: list[ObjectRecord], by_id: dict[str, ObjectRecord]) -> dict[str, object]:
    raw_proposal_id = _proposal_id_raw(proposal)
    has_proposal_id = bool(raw_proposal_id)
    proposal_id = raw_proposal_id or _path_fallback_id(proposal.path, repo_root)
    target_ids = _ids_from_keys(proposal.metadata, TARGET_REFERENCE_KEYS)
    evidence_ids = _ids_from_keys(proposal.metadata, EVIDENCE_REFERENCE_KEYS)
    resolved_targets, missing_targets = _resolve_ids(target_ids, by_id)
    resolved_evidence, missing_evidence = _resolve_ids(evidence_ids, by_id)

    related_logs = tuple(
        sorted(
            (
                related
                for log in workspace_records
                if log.object_class == "logs"
                for related in [_related_log_record(log, proposal_id, target_ids)]
                if related is not None
            ),
            key=_log_sort_key,
        )
    )
    apply_logs = tuple(log for log in related_logs if "apply_evidence" in log.relation_labels)
    recovery_logs = tuple(log for log in related_logs if "recovery_evidence" in log.relation_labels)

    status = _metadata_text(proposal, "status")
    classifications, primary, attention_flags = _classify_packet(
        status=status,
        has_proposal_id=has_proposal_id,
        target_ids=target_ids,
        missing_target_ids=missing_targets,
        evidence_ids=evidence_ids,
        missing_evidence_ids=missing_evidence,
        apply_evidence_records=apply_logs,
        recovery_evidence_records=recovery_logs,
    )
    return {
        "proposal_id": proposal_id,
        "packet_filename": "",
        "proposal_path": proposal.path,
        "proposal_status": status,
        "proposal_title": _metadata_text(proposal, "title"),
        "created_by": _metadata_text(proposal, "created_by"),
        "created_at": _metadata_text(proposal, "created_at"),
        "target_ids": target_ids,
        "resolved_target_records": resolved_targets,
        "missing_target_ids": missing_targets,
        "evidence_ids": evidence_ids,
        "resolved_evidence_records": resolved_evidence,
        "missing_evidence_ids": missing_evidence,
        "related_log_records": related_logs,
        "apply_evidence_records": apply_logs,
        "recovery_evidence_records": recovery_logs,
        "readiness_classifications": classifications,
        "primary_classification": primary,
        "attention_flags": attention_flags,
        "operator_next_steps": _next_steps(
            classifications=classifications,
            attention_flags=attention_flags,
            missing_target_ids=missing_targets,
            missing_evidence_ids=missing_evidence,
        ),
    }


def build_review_packets(*, repo_root: Path, workspace: str, records: list[ObjectRecord] | None = None) -> list[ReviewPacket]:
    resolved_repo_root = Path(repo_root).resolve()
    all_records = load_records(resolved_repo_root) if records is None else records
    workspace_records = filter_records(all_records, workspace=workspace)
    by_id = _build_id_index(workspace_records)
    packet_inputs = [
        _build_packet_input(
            proposal,
            repo_root=resolved_repo_root,
            workspace_records=workspace_records,
            by_id=by_id,
        )
        for proposal in workspace_records
        if proposal.object_class == "proposals"
    ]
    packet_inputs.sort(key=_packet_sort_components)
    _assign_packet_filenames(packet_inputs)
    return [ReviewPacket(**item) for item in packet_inputs]
