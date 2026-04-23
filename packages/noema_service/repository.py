from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packages.noema_maintainer.scan import ObjectRecord, scan_repository

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

RELATIONSHIP_KEYS_BY_CLASS: dict[str, tuple[str, ...]] = {
    "structured": ("supports", "supersedes"),
    "proposals": ("target_ids", "results_in", "supports", "supporting_raw_ids", "supersedes"),
    "logs": ("records_event_for", "supersedes"),
    "raw": ("supersedes",),
}


@dataclass(frozen=True)
class CursorPage:
    items: list[ObjectRecord]
    limit: int
    next_cursor: str | None
    has_more: bool


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def parse_offset_cursor(cursor: str | None) -> int:
    if cursor is None or cursor == "":
        return 0
    prefix = "offset:"
    if not cursor.startswith(prefix):
        raise ValueError("Cursor must use format offset:<integer>")
    raw_value = cursor[len(prefix) :]
    if not raw_value.isdigit():
        raise ValueError("Cursor must use format offset:<integer>")
    return int(raw_value)


def normalize_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    if limit <= 0:
        raise ValueError("limit must be >= 1")
    return min(limit, MAX_LIMIT)


def load_records(repo_root: Path) -> list[ObjectRecord]:
    return scan_repository(repo_root)


def filter_records(
    records: list[ObjectRecord],
    *,
    workspace: str,
    object_class: str | None = None,
    status: str | None = None,
    ids: list[str] | None = None,
    title_contains: str | None = None,
) -> list[ObjectRecord]:
    normalized_ids = {item.strip() for item in (ids or []) if item.strip()}
    lowered_title = title_contains.lower() if title_contains else None

    def keep(record: ObjectRecord) -> bool:
        metadata = record.metadata
        if str(metadata.get("workspace", "")).strip() != workspace:
            return False
        if object_class and record.object_class != object_class:
            return False
        if status and str(metadata.get("status", "")).strip() != status:
            return False
        if normalized_ids and str(metadata.get("id", "")).strip() not in normalized_ids:
            return False
        if lowered_title:
            title = str(metadata.get("title", "")).lower()
            if lowered_title not in title:
                return False
        return True

    return [record for record in records if keep(record)]


def sort_records(records: list[ObjectRecord], *, sort_by: str, sort_order: str) -> list[ObjectRecord]:
    reverse = sort_order == "desc"

    def sort_value(record: ObjectRecord) -> tuple[str, str]:
        value = str(record.metadata.get(sort_by, "")).lower()
        object_id = str(record.metadata.get("id", "")).lower()
        return (value, object_id)

    return sorted(records, key=sort_value, reverse=reverse)


def paginate_records(records: list[ObjectRecord], *, limit: int | None, cursor: str | None) -> CursorPage:
    normalized_limit = normalize_limit(limit)
    offset = parse_offset_cursor(cursor)
    page_items = records[offset : offset + normalized_limit]
    next_offset = offset + len(page_items)
    has_more = next_offset < len(records)
    next_cursor = f"offset:{next_offset}" if has_more else None
    return CursorPage(items=page_items, limit=normalized_limit, next_cursor=next_cursor, has_more=has_more)


def load_markdown_content(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return text.strip()

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body = "\n".join(lines[index + 1 :]).strip()
            return body
    return text.strip()


def relationship_hints_for(record: ObjectRecord) -> dict[str, list[str]]:
    hints: dict[str, list[str]] = {}
    keys = RELATIONSHIP_KEYS_BY_CLASS.get(record.object_class, ())
    for key in keys:
        values = _as_id_list(record.metadata.get(key))
        if values:
            hints[key] = values
    return hints


def record_to_object(
    record: ObjectRecord,
    *,
    include_content: bool,
    include_relationship_hints: bool,
) -> dict[str, Any]:
    metadata = dict(record.metadata)
    data: dict[str, Any] = {
        "id": str(metadata.get("id", "")),
        "class": record.object_class,
        "workspace": str(metadata.get("workspace", "")),
        "status": str(metadata.get("status", "")),
        "metadata": metadata,
    }

    if include_content:
        data["content"] = load_markdown_content(record.path)
    if include_relationship_hints:
        data["relationship_hints"] = relationship_hints_for(record)
    return data
