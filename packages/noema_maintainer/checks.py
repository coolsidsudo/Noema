from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .scan import ObjectRecord

REQUIRED_FIELDS = ("id", "class", "created_at", "created_by", "workspace", "status")
VALID_STATUS_BY_CLASS = {
    "raw": {"ingested", "superseded", "archived"},
    "structured": {"draft", "active", "deprecated", "archived"},
    "proposals": {"draft", "under_review", "accepted", "rejected", "withdrawn"},
    "logs": {"recorded", "corrected"},
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    object_path: str
    object_id: str
    workspace: str


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _is_explicit_true(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _index_records_by_workspace(records: list[ObjectRecord]) -> dict[str, dict[str, list[ObjectRecord]]]:
    indexed: dict[str, dict[str, list[ObjectRecord]]] = {}
    for record in records:
        workspace = str(record.metadata.get("workspace", ""))
        object_id = str(record.metadata.get("id", ""))
        if workspace == "" or object_id == "":
            continue
        workspace_index = indexed.setdefault(workspace, {})
        workspace_index.setdefault(object_id, []).append(record)
    return indexed


def _append_missing_reference_issue(
    *,
    issues: list[ValidationIssue],
    code: str,
    message: str,
    record: ObjectRecord,
    object_id: str,
    workspace: str,
) -> None:
    issues.append(
        ValidationIssue(
            code=code,
            message=message,
            object_path=str(record.path),
            object_id=object_id,
            workspace=workspace,
        )
    )


def _is_known_reference(
    workspace_index: dict[str, list[ObjectRecord]],
    reference_id: str,
    expected_class: str | None = None,
) -> bool:
    referenced_records = workspace_index.get(reference_id, [])
    if not referenced_records:
        return False
    if expected_class is None:
        return True
    return any(r.object_class == expected_class for r in referenced_records)


def _portable_path_hint(record: ObjectRecord) -> str:
    path = Path(record.path)
    parts = path.parts
    if record.object_class in parts:
        class_idx = parts.index(record.object_class)
        return Path(*parts[class_idx:]).as_posix()
    return path.name



def validate_records(records: list[ObjectRecord]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_workspace = _index_records_by_workspace(records)

    for workspace, objects_by_id in by_workspace.items():
        for object_id, duplicate_records in objects_by_id.items():
            if len(duplicate_records) < 2:
                continue
            ordered_duplicates = sorted(duplicate_records, key=lambda r: str(r.path))
            duplicate_paths = [_portable_path_hint(record) for record in ordered_duplicates]
            preview_paths = ", ".join(duplicate_paths[:3])
            if len(duplicate_paths) > 3:
                preview_paths += f", +{len(duplicate_paths) - 3} more"
            message = (
                f"Object id '{object_id}' is duplicated in workspace '{workspace}' "
                f"across {len(duplicate_paths)} objects: {preview_paths}"
            )
            for duplicate_record in ordered_duplicates:
                issues.append(
                    ValidationIssue(
                        code="duplicate_object_id_in_workspace",
                        message=message,
                        object_path=str(duplicate_record.path),
                        object_id=object_id,
                        workspace=workspace,
                    )
                )

    for record in records:
        metadata = record.metadata
        object_id = str(metadata.get("id", ""))
        workspace = str(metadata.get("workspace", ""))
        workspace_index = by_workspace.get(workspace, {})

        for field in REQUIRED_FIELDS:
            value = metadata.get(field)
            if value is None or value == "" or value == []:
                issues.append(
                    ValidationIssue(
                        code="missing_required_metadata",
                        message=f"Missing required metadata field '{field}'.",
                        object_path=str(record.path),
                        object_id=object_id,
                        workspace=workspace,
                    )
                )

        declared_class = metadata.get("class")
        if declared_class and declared_class != record.object_class:
            issues.append(
                ValidationIssue(
                    code="class_mismatch",
                    message=f"Metadata class '{declared_class}' does not match directory class '{record.object_class}'.",
                    object_path=str(record.path),
                    object_id=object_id,
                    workspace=workspace,
                )
            )

        status = metadata.get("status")
        if status and status not in VALID_STATUS_BY_CLASS[record.object_class]:
            issues.append(
                ValidationIssue(
                    code="invalid_status",
                    message=f"Status '{status}' is invalid for class '{record.object_class}'.",
                    object_path=str(record.path),
                    object_id=object_id,
                    workspace=workspace,
                )
            )

        if record.object_class == "proposals" and status and status != "draft":
            target_ids = metadata.get("target_ids")
            if not isinstance(target_ids, list) or len(target_ids) == 0:
                _append_missing_reference_issue(
                    issues=issues,
                    code="proposal_missing_targets",
                    message="Non-draft proposals must include at least one target_id.",
                    record=record,
                    object_id=object_id,
                    workspace=workspace,
                )
            else:
                for target_id in _as_id_list(target_ids):
                    if not _is_known_reference(workspace_index, target_id):
                        _append_missing_reference_issue(
                            issues=issues,
                            code="proposal_target_reference_not_found",
                            message=f"Proposal target_id '{target_id}' does not resolve in workspace '{workspace}'.",
                            record=record,
                            object_id=object_id,
                            workspace=workspace,
                        )

        if record.object_class == "proposals" and status == "accepted":
            for result_id in _as_id_list(metadata.get("results_in")):
                if not _is_known_reference(workspace_index, result_id):
                    _append_missing_reference_issue(
                        issues=issues,
                        code="proposal_results_in_reference_not_found",
                        message=f"Proposal results_in reference '{result_id}' does not resolve in workspace '{workspace}'.",
                        record=record,
                        object_id=object_id,
                        workspace=workspace,
                    )

        if record.object_class == "logs":
            for event_for_id in _as_id_list(metadata.get("records_event_for")):
                if not _is_known_reference(workspace_index, event_for_id):
                    _append_missing_reference_issue(
                        issues=issues,
                        code="log_records_event_for_reference_not_found",
                        message=f"Log records_event_for reference '{event_for_id}' does not resolve in workspace '{workspace}'.",
                        record=record,
                        object_id=object_id,
                        workspace=workspace,
                    )

        if record.object_class == "structured":
            support_ids = _as_id_list(metadata.get("supports"))
            support_exempt = _is_explicit_true(metadata.get("support_exempt"))
            if status == "active" and not support_ids and not support_exempt:
                _append_missing_reference_issue(
                    issues=issues,
                    code="structured_missing_required_supports_raw",
                    message=(
                        "Active structured objects must include at least one raw support reference "
                        "via 'supports' unless explicitly exempt with support_exempt: true."
                    ),
                    record=record,
                    object_id=object_id,
                    workspace=workspace,
                )
            for support_id in support_ids:
                if not _is_known_reference(workspace_index, support_id, expected_class="raw"):
                    _append_missing_reference_issue(
                        issues=issues,
                        code="structured_supports_reference_not_found_raw",
                        message=f"Structured supports reference '{support_id}' does not resolve to a raw object in workspace '{workspace}'.",
                        record=record,
                        object_id=object_id,
                        workspace=workspace,
                    )

        for superseded_id in _as_id_list(metadata.get("supersedes")):
            if not _is_known_reference(workspace_index, superseded_id):
                _append_missing_reference_issue(
                    issues=issues,
                    code="supersedes_reference_not_found",
                    message=f"Supersedes reference '{superseded_id}' does not resolve in workspace '{workspace}'.",
                    record=record,
                    object_id=object_id,
                    workspace=workspace,
                )

    issues.sort(key=lambda i: (i.workspace, i.code, i.object_path, i.object_id))
    return issues
