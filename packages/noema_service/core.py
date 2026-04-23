from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .repository import filter_records, load_records, normalize_limit, paginate_records, record_to_object, sort_records

SUPPORTED_CLASSES = {"raw", "structured", "proposals", "logs"}
SUPPORTED_SORT_FIELDS = {"id", "title", "status", "created_at", "updated_at"}
SUPPORTED_SORT_ORDER = {"asc", "desc"}


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
