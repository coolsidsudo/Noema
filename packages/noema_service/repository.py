from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from packages.noema_maintainer.scan import ObjectRecord, scan_repository

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

TRACEABILITY_DEFAULT_LIMIT = 100
TRACEABILITY_MAX_LIMIT = 500
SUPPORTED_TRACEABILITY_LINK_TYPES = {
    "supports",
    "targets",
    "results_in",
    "records_event_for",
    "supersedes",
}
TRACEABILITY_DIRECTIONS = {"outbound", "inbound", "both"}

RELATIONSHIP_KEYS_BY_CLASS: dict[str, tuple[str, ...]] = {
    "structured": ("supports", "supersedes"),
    "proposals": ("target_ids", "results_in", "supports", "supporting_raw_ids", "supersedes"),
    "logs": ("records_event_for", "supersedes"),
    "raw": ("supersedes",),
}

TRACEABILITY_METADATA_KEYS: dict[str, tuple[str, ...]] = {
    "supports": ("supports", "supporting_raw_ids", "support_raw_ids"),
    "targets": ("target_ids",),
    "results_in": ("results_in",),
    "records_event_for": ("records_event_for",),
    "supersedes": ("supersedes",),
}


@dataclass(frozen=True)
class CursorPage:
    items: list[ObjectRecord]
    limit: int
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True)
class TraceabilityLink:
    from_id: str
    to_id: str
    type: str
    direction: str


@dataclass(frozen=True)
class TraceabilityResult:
    seed_ids: list[str]
    links: list[TraceabilityLink]
    nodes: dict[str, ObjectRecord]
    truncation: dict[str, Any] | None


@dataclass(frozen=True)
class ProposalStatusDerivation:
    proposal_record: ObjectRecord
    result_links: list[str]
    log_refs: list[str]


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _frontmatter_list_lines(key: str, values: list[str]) -> list[str]:
    if not values:
        return [f"{key}: []"]
    lines = [f"{key}:"]
    lines.extend(f"  - {value}" for value in values)
    return lines


def _utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def normalize_traceability_limit(limit: int | None) -> int:
    if limit is None:
        return TRACEABILITY_DEFAULT_LIMIT
    if limit <= 0 or limit > TRACEABILITY_MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {TRACEABILITY_MAX_LIMIT}")
    return limit


def validate_traceability_direction(direction: str) -> str:
    if direction not in TRACEABILITY_DIRECTIONS:
        raise ValueError("direction must be one of: outbound, inbound, both")
    return direction


def validate_traceability_link_types(link_types: list[str] | None) -> list[str]:
    if link_types is None:
        return sorted(SUPPORTED_TRACEABILITY_LINK_TYPES)
    invalid = sorted({item for item in link_types if item not in SUPPORTED_TRACEABILITY_LINK_TYPES})
    if invalid:
        raise ValueError(f"unsupported link_types: {', '.join(invalid)}")
    return sorted(set(link_types))


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


def collect_traceability_links(
    records: list[ObjectRecord],
    *,
    workspace: str,
    seed_ids: list[str],
    link_types: list[str],
    direction: str,
    limit: int,
) -> TraceabilityResult:
    workspace_records = filter_records(records, workspace=workspace)
    by_id = {str(record.metadata.get("id", "")).strip(): record for record in workspace_records}

    links: list[TraceabilityLink] = []
    seen: set[tuple[str, str, str, str]] = set()
    truncated = False

    def append_link(from_id: str, to_id: str, link_type: str, edge_direction: str) -> None:
        nonlocal truncated
        if len(links) >= limit:
            truncated = True
            return
        edge_key = (from_id, to_id, link_type, edge_direction)
        if edge_key in seen:
            return
        seen.add(edge_key)
        links.append(
            TraceabilityLink(
                from_id=from_id,
                to_id=to_id,
                type=link_type,
                direction=edge_direction,
            )
        )

    for seed_id in seed_ids:
        seed_record = by_id[seed_id]

        if direction in {"outbound", "both"}:
            for link_type in link_types:
                for metadata_key in TRACEABILITY_METADATA_KEYS[link_type]:
                    for target_id in _as_id_list(seed_record.metadata.get(metadata_key)):
                        append_link(seed_id, target_id, link_type, "outbound")

        if direction in {"inbound", "both"}:
            for source_id, candidate in by_id.items():
                for link_type in link_types:
                    for metadata_key in TRACEABILITY_METADATA_KEYS[link_type]:
                        if seed_id in _as_id_list(candidate.metadata.get(metadata_key)):
                            append_link(source_id, seed_id, link_type, "inbound")

    node_ids = set(seed_ids)
    for link in links:
        node_ids.add(link.from_id)
        node_ids.add(link.to_id)

    nodes = {node_id: by_id[node_id] for node_id in node_ids if node_id in by_id}
    truncation = None
    if truncated:
        truncation = {"limit": limit, "returned_links": len(links), "truncated": True}

    return TraceabilityResult(seed_ids=seed_ids, links=links, nodes=nodes, truncation=truncation)


def proposal_path(*, repo_root: Path, workspace: str, proposal_id: str) -> Path:
    return repo_root / "proposals" / workspace / f"{proposal_id}.md"


def write_proposal_markdown(
    *,
    repo_root: Path,
    workspace: str,
    proposal: dict[str, Any],
) -> Path:
    proposal_id = str(proposal["id"])
    destination = proposal_path(repo_root=repo_root, workspace=workspace, proposal_id=proposal_id)
    if destination.exists():
        raise FileExistsError(f"proposal already exists: {proposal_id}")

    created_at = str(proposal.get("created_at") or _utc_timestamp())
    supporting_raw_ids = [str(item) for item in proposal.get("supporting_raw_ids", [])]
    requested_reviewers = [str(item) for item in proposal.get("requested_reviewers", [])]
    results_in = [str(item) for item in proposal.get("results_in", [])]
    target_ids = [str(item) for item in proposal.get("target_ids", [])]

    frontmatter_lines: list[str] = [
        "id: " + proposal_id,
        "workspace: " + workspace,
        "class: proposals",
        "status: " + str(proposal["status"]),
        "created_at: " + created_at,
        "created_by: " + str(proposal["created_by"]),
        "title: " + str(proposal["title"]),
        "summary: " + str(proposal["summary"]),
        "rationale: " + str(proposal["rationale"]),
        "intended_effect: " + str(proposal["intended_effect"]),
    ]
    frontmatter_lines.extend(_frontmatter_list_lines("target_ids", target_ids))
    frontmatter_lines.extend(_frontmatter_list_lines("supporting_raw_ids", supporting_raw_ids))
    frontmatter_lines.extend(_frontmatter_list_lines("requested_reviewers", requested_reviewers))
    frontmatter_lines.extend(_frontmatter_list_lines("results_in", results_in))

    markdown = "\n".join(
        [
            "---",
            *frontmatter_lines,
            "---",
            "",
            f"# Proposal: {proposal['title']}",
            "",
            "## Summary",
            str(proposal["summary"]),
            "",
            "## Rationale",
            str(proposal["rationale"]),
            "",
            "## Intended effect",
            str(proposal["intended_effect"]),
            "",
        ]
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")
    return destination


def derive_proposal_status(
    records: list[ObjectRecord],
    *,
    workspace: str,
    proposal_id: str,
) -> ProposalStatusDerivation | None:
    workspace_records = filter_records(records, workspace=workspace)
    proposal_record = next(
        (
            record
            for record in workspace_records
            if record.object_class == "proposals" and str(record.metadata.get("id", "")).strip() == proposal_id
        ),
        None,
    )
    if proposal_record is None:
        return None

    result_links = _as_id_list(proposal_record.metadata.get("results_in"))
    log_refs = sorted(
        {
            str(record.metadata.get("id", "")).strip()
            for record in workspace_records
            if record.object_class == "logs" and proposal_id in _as_id_list(record.metadata.get("records_event_for"))
        }
    )
    return ProposalStatusDerivation(proposal_record=proposal_record, result_links=result_links, log_refs=log_refs)
