from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .repository import (
    SUPPORTED_TRACEABILITY_LINK_TYPES,
    collect_traceability_links,
    derive_proposal_status,
    filter_records,
    load_records,
    normalize_limit,
    normalize_traceability_limit,
    paginate_records,
    record_to_object,
    sort_records,
    validate_traceability_direction,
    validate_traceability_link_types,
    write_proposal_markdown,
)

SUPPORTED_CLASSES = {"raw", "structured", "proposals", "logs"}
SUPPORTED_SORT_FIELDS = {"id", "title", "status", "created_at", "updated_at"}
SUPPORTED_SORT_ORDER = {"asc", "desc"}
SUPPORTED_PROPOSAL_STATUSES = {"draft", "under_review"}


def _timestamp_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request_id() -> str:
    return f"req_{uuid4().hex}"


def _success(operation: str, data: dict[str, Any], meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "operation": operation,
        "request_id": _request_id(),
        "timestamp": _timestamp_now(),
        "data": data,
    }
    if meta is not None:
        payload["meta"] = meta
    return payload


def _error(
    operation: str,
    *,
    category: str,
    code: str,
    message: str,
    retryable: bool,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error_payload: dict[str, Any] = {
        "category": category,
        "code": code,
        "message": message,
        "retryable": retryable,
    }
    if details is not None:
        error_payload["details"] = details

    return {
        "ok": False,
        "operation": operation,
        "request_id": _request_id(),
        "timestamp": _timestamp_now(),
        "error": error_payload,
    }


def get_object_by_id(
    *,
    repo_root: Path,
    workspace: str,
    id: str,
    include_content: bool = True,
    include_relationship_hints: bool = False,
) -> dict[str, Any]:
    operation = "get_object_by_id"
    records = filter_records(load_records(repo_root), workspace=workspace, ids=[id])
    if not records:
        return _error(
            operation,
            category="not_found",
            code="OBJECT_NOT_FOUND",
            message="Object not found in workspace scope.",
            retryable=False,
            details={"workspace": workspace, "id": id},
        )

    obj = record_to_object(
        records[0],
        include_content=include_content,
        include_relationship_hints=include_relationship_hints,
    )
    return _success(operation, data={"object": obj})


def list_objects(
    *,
    repo_root: Path,
    workspace: str,
    object_class: str | None = None,
    status: str | None = None,
    ids: list[str] | None = None,
    title_contains: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    include_content: bool = False,
    include_relationship_hints: bool = False,
) -> dict[str, Any]:
    operation = "list_objects"

    if object_class and object_class not in SUPPORTED_CLASSES:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_CLASS",
            message="Unsupported class filter.",
            retryable=False,
            details={"class": object_class},
        )

    if sort_by not in SUPPORTED_SORT_FIELDS:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_SORT_FIELD",
            message="Unsupported sort field.",
            retryable=False,
            details={"sort_by": sort_by},
        )

    if sort_order not in SUPPORTED_SORT_ORDER:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_SORT_ORDER",
            message="Unsupported sort order.",
            retryable=False,
            details={"sort_order": sort_order},
        )

    records = filter_records(
        load_records(repo_root),
        workspace=workspace,
        object_class=object_class,
        status=status,
        ids=ids,
        title_contains=title_contains,
    )
    sorted_records = sort_records(records, sort_by=sort_by, sort_order=sort_order)

    try:
        normalized_limit = normalize_limit(limit)
    except ValueError as exc:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_LIMIT",
            message=str(exc),
            retryable=False,
            details={"limit": limit},
        )

    try:
        page = paginate_records(sorted_records, limit=normalized_limit, cursor=cursor)
    except ValueError as exc:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_CURSOR",
            message=str(exc),
            retryable=False,
            details={"cursor": cursor},
        )

    items = [
        record_to_object(
            record,
            include_content=include_content,
            include_relationship_hints=include_relationship_hints,
        )
        for record in page.items
    ]

    return _success(
        operation,
        data={"items": items},
        meta={
            "pagination": {
                "limit": page.limit,
                "next_cursor": page.next_cursor,
                "has_more": page.has_more,
            }
        },
    )


def get_traceability_links(
    *,
    repo_root: Path,
    workspace: str,
    seed_ids: list[str],
    link_types: list[str] | None = None,
    direction: str = "both",
    limit: int | None = None,
    include_node_summaries: bool = False,
) -> dict[str, Any]:
    operation = "get_traceability_links"
    if not seed_ids:
        return _error(
            operation,
            category="invalid_request",
            code="EMPTY_SEED_IDS",
            message="seed_ids must contain at least one id.",
            retryable=False,
            details={"seed_ids": seed_ids},
        )

    try:
        normalized_direction = validate_traceability_direction(direction)
    except ValueError as exc:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_DIRECTION",
            message=str(exc),
            retryable=False,
            details={"direction": direction},
        )

    try:
        normalized_limit = normalize_traceability_limit(limit)
    except ValueError as exc:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_LIMIT",
            message=str(exc),
            retryable=False,
            details={"limit": limit},
        )

    try:
        normalized_link_types = validate_traceability_link_types(link_types)
    except ValueError as exc:
        return _error(
            operation,
            category="invalid_request",
            code="UNSUPPORTED_LINK_TYPES",
            message=str(exc),
            retryable=False,
            details={"link_types": link_types, "supported": sorted(SUPPORTED_TRACEABILITY_LINK_TYPES)},
        )

    records = load_records(repo_root)
    workspace_records = filter_records(records, workspace=workspace)
    workspace_ids = {str(record.metadata.get("id", "")).strip() for record in workspace_records}
    missing_seed_ids = [seed_id for seed_id in seed_ids if seed_id not in workspace_ids]
    if missing_seed_ids:
        return _error(
            operation,
            category="not_found",
            code="SEED_NOT_FOUND",
            message="One or more seed ids were not found in workspace scope.",
            retryable=False,
            details={"workspace": workspace, "missing_seed_ids": missing_seed_ids},
        )

    collected = collect_traceability_links(
        records,
        workspace=workspace,
        seed_ids=seed_ids,
        link_types=normalized_link_types,
        direction=normalized_direction,
        limit=normalized_limit,
    )

    data: dict[str, Any] = {
        "seed_ids": collected.seed_ids,
        "links": [
            {
                "from_id": link.from_id,
                "to_id": link.to_id,
                "type": link.type,
                "direction": link.direction,
            }
            for link in collected.links
        ],
    }

    if include_node_summaries:
        data["nodes"] = [
            {
                "id": node_id,
                "class": node.object_class,
                "workspace": str(node.metadata.get("workspace", "")),
                "status": str(node.metadata.get("status", "")),
                "title": str(node.metadata.get("title", "")),
            }
            for node_id, node in sorted(collected.nodes.items())
        ]

    if collected.truncation is not None:
        data["truncation"] = collected.truncation

    return _success(operation, data=data)


def submit_proposal(
    *,
    repo_root: Path,
    workspace: str,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    operation = "submit_proposal"
    required_fields = [
        "id",
        "created_by",
        "status",
        "target_ids",
        "title",
        "summary",
        "rationale",
        "intended_effect",
    ]
    missing_fields = [field for field in required_fields if field not in proposal]
    if missing_fields:
        return _error(
            operation,
            category="invalid_request",
            code="MISSING_PROPOSAL_FIELDS",
            message="Missing required proposal fields.",
            retryable=False,
            details={"missing_fields": missing_fields},
        )

    status = str(proposal.get("status", "")).strip()
    if status not in SUPPORTED_PROPOSAL_STATUSES:
        return _error(
            operation,
            category="invalid_request",
            code="INVALID_PROPOSAL_STATUS",
            message="Unsupported proposal status for initial submission.",
            retryable=False,
            details={"status": status, "allowed_statuses": sorted(SUPPORTED_PROPOSAL_STATUSES)},
        )

    target_ids = proposal.get("target_ids")
    if not isinstance(target_ids, list) or not [str(item).strip() for item in target_ids if str(item).strip()]:
        return _error(
            operation,
            category="invalid_request",
            code="EMPTY_TARGET_IDS",
            message="proposal.target_ids must contain at least one id.",
            retryable=False,
            details={"target_ids": target_ids},
        )

    payload = dict(proposal)
    payload["status"] = status
    payload["target_ids"] = [str(item).strip() for item in target_ids if str(item).strip()]

    try:
        destination = write_proposal_markdown(repo_root=repo_root, workspace=workspace, proposal=payload)
    except FileExistsError:
        return _error(
            operation,
            category="conflict",
            code="PROPOSAL_ALREADY_EXISTS",
            message="Proposal already exists in workspace.",
            retryable=False,
            details={"workspace": workspace, "proposal_id": str(proposal.get('id', ''))},
        )

    response_data = {
        "id": str(payload["id"]),
        "workspace": workspace,
        "status": payload["status"],
        "created_by": str(payload["created_by"]),
        "created_at": str(payload.get("created_at") or ""),
        "title": str(payload["title"]),
        "summary": str(payload["summary"]),
        "target_ids": payload["target_ids"],
        "proposal_path": str(destination.relative_to(repo_root)),
    }
    if not response_data["created_at"]:
        refreshed = derive_proposal_status(load_records(repo_root), workspace=workspace, proposal_id=str(payload["id"]))
        if refreshed is not None:
            response_data["created_at"] = str(refreshed.proposal_record.metadata.get("created_at", ""))
    return _success(operation, data=response_data)


def get_proposal_status(
    *,
    repo_root: Path,
    workspace: str,
    proposal_id: str,
    include_review_history: bool = False,
    include_result_links: bool = True,
    include_log_refs: bool = True,
) -> dict[str, Any]:
    operation = "get_proposal_status"

    derived = derive_proposal_status(load_records(repo_root), workspace=workspace, proposal_id=proposal_id)
    if derived is None:
        return _error(
            operation,
            category="not_found",
            code="PROPOSAL_NOT_FOUND",
            message="Proposal not found in workspace scope.",
            retryable=False,
            details={"workspace": workspace, "proposal_id": proposal_id},
        )

    metadata = derived.proposal_record.metadata
    data: dict[str, Any] = {
        "id": str(metadata.get("id", "")),
        "status": str(metadata.get("status", "")),
        "created_at": str(metadata.get("created_at", "")),
        "created_by": str(metadata.get("created_by", "")),
        "target_ids": metadata.get("target_ids", []),
        "summary": str(metadata.get("summary", "")),
    }

    if include_review_history:
        data["review_history"] = []
    if include_result_links:
        data["result_links"] = derived.result_links
    if include_log_refs:
        data["log_refs"] = derived.log_refs

    return _success(operation, data=data)
