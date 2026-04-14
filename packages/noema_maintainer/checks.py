from __future__ import annotations

from dataclasses import dataclass

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



def validate_records(records: list[ObjectRecord]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for record in records:
        metadata = record.metadata
        object_id = str(metadata.get("id", ""))
        workspace = str(metadata.get("workspace", ""))

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
                issues.append(
                    ValidationIssue(
                        code="proposal_missing_targets",
                        message="Non-draft proposals must include at least one target_id.",
                        object_path=str(record.path),
                        object_id=object_id,
                        workspace=workspace,
                    )
                )

    issues.sort(key=lambda i: (i.workspace, i.code, i.object_path, i.object_id))
    return issues
