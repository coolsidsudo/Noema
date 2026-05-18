from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Iterable

from packages.noema_maintainer.scan import OBJECT_CLASSES, ObjectRecord
from packages.noema_service.repository import filter_records, load_records

MISSING_VALUE = "—"
PROPOSAL_STATUS_PRIORITY = {
    "under_review": 0,
    "draft": 1,
    "accepted": 2,
    "rejected": 3,
    "withdrawn": 4,
}


@dataclass(frozen=True)
class ResolvedWorkspace:
    workspace_id: str
    workspace_root: Path


@dataclass(frozen=True)
class OperatorProjectionResult:
    workspace_id: str
    workspace_root: Path
    projection_root: Path
    output_paths: tuple[Path, ...]
    record_count: int


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _resolve_workspace(repo_root: Path, workspace: str) -> ResolvedWorkspace:
    raw_workspace = Path(workspace).expanduser()
    candidate_path = raw_workspace if raw_workspace.is_absolute() else repo_root / raw_workspace
    if candidate_path.exists() and candidate_path.is_dir():
        resolved = candidate_path.resolve()
        return ResolvedWorkspace(workspace_id=resolved.name, workspace_root=resolved)

    if raw_workspace.is_absolute() or len(raw_workspace.parts) > 1:
        raise ValueError(f"workspace path does not exist: {workspace}")

    workspace_id = workspace.strip()
    if not workspace_id:
        raise ValueError("workspace must not be empty")

    examples_root = repo_root / "examples" / "workspaces"
    matches = sorted(
        path.resolve()
        for path in examples_root.glob("*/workspaces/*")
        if path.is_dir() and path.name == workspace_id
    )
    if len(matches) == 1:
        return ResolvedWorkspace(workspace_id=workspace_id, workspace_root=matches[0])
    if len(matches) > 1:
        rendered = ", ".join(_repo_relative_path(path, repo_root) for path in matches)
        raise ValueError(f"workspace id is ambiguous: {workspace_id} ({rendered})")
    raise ValueError(f"workspace id not found: {workspace_id}")


def _metadata_text(record: ObjectRecord, key: str) -> str:
    value = record.metadata.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _object_id(record: ObjectRecord) -> str:
    return _metadata_text(record, "id")


def _proposal_id(record: ObjectRecord) -> str:
    return _metadata_text(record, "proposal_id") or _metadata_text(record, "id")


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return sorted({str(item).strip() for item in value if str(item).strip()})
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _format_table_cell(value: object) -> str:
    if value is None:
        return MISSING_VALUE
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return MISSING_VALUE
    return text.replace("|", "\\|")


def _table_row(values: Iterable[object]) -> str:
    return "| " + " | ".join(_format_table_cell(value) for value in values) + " |"


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _markdown_path_link(*, record_path: Path, page_path: Path, repo_root: Path) -> str:
    label = _repo_relative_path(record_path, repo_root)
    relative_target = os.path.relpath(record_path.resolve(), start=page_path.parent.resolve())
    return f"[{label}]({Path(relative_target).as_posix()})"


def _date_value(record: ObjectRecord, *keys: str) -> str:
    for key in keys:
        value = _metadata_text(record, key)
        if value:
            return value
    return ""


def _date_missing(value: str) -> int:
    return 1 if not value else 0


def _class_order(object_class: str) -> int:
    try:
        return OBJECT_CLASSES.index(object_class)
    except ValueError:
        return len(OBJECT_CLASSES)


def _sort_objects(records: list[ObjectRecord], repo_root: Path) -> list[ObjectRecord]:
    return sorted(
        records,
        key=lambda record: (
            _class_order(record.object_class),
            _object_id(record).lower(),
            _repo_relative_path(record.path, repo_root),
        ),
    )


def _sort_proposals(records: list[ObjectRecord]) -> list[ObjectRecord]:
    return sorted(
        records,
        key=lambda record: (
            PROPOSAL_STATUS_PRIORITY.get(_metadata_text(record, "status"), 99),
            _date_missing(_metadata_text(record, "created_at")),
            _metadata_text(record, "created_at"),
            _proposal_id(record).lower(),
            str(record.path),
        ),
    )


def _sort_by_date_desc(records: list[ObjectRecord], *date_keys: str, id_getter=_object_id) -> list[ObjectRecord]:
    dated = [record for record in records if _date_value(record, *date_keys)]
    missing = [record for record in records if not _date_value(record, *date_keys)]
    dated.sort(key=lambda record: (id_getter(record).lower(), str(record.path)))
    dated.sort(key=lambda record: _date_value(record, *date_keys), reverse=True)
    missing.sort(key=lambda record: (id_getter(record).lower(), str(record.path)))
    return dated + missing


def _render_index(
    *,
    path: Path,
    repo_root: Path,
    workspace: ResolvedWorkspace,
    records: list[ObjectRecord],
) -> None:
    class_counts = Counter(record.object_class for record in records)
    status_counts = Counter(_metadata_text(record, "status") or MISSING_VALUE for record in records)

    lines = [
        "# Operator Workspace",
        "",
        "## Workspace",
        f"- Workspace id: `{_format_table_cell(workspace.workspace_id)}`",
        f"- Workspace path: `{_format_table_cell(_repo_relative_path(workspace.workspace_root, repo_root))}`",
        "",
        "## Object Counts by Class",
        "| class | count |",
        "| --- | ---: |",
    ]
    for object_class in OBJECT_CLASSES:
        lines.append(_table_row([object_class, class_counts.get(object_class, 0)]))

    lines.extend([
        "",
        "## Object Counts by Status",
        "| status | count |",
        "| --- | ---: |",
    ])
    if status_counts:
        for status in sorted(status_counts, key=lambda value: (value == MISSING_VALUE, value)):
            lines.append(_table_row([status, status_counts[status]]))
    else:
        lines.append(_table_row([MISSING_VALUE, 0]))

    lines.extend([
        "",
        "## Operator Links",
        "- [Objects](./objects.md)",
        "- [Proposals](./proposals.md)",
        "- [Recent Activity](./recent.md)",
    ])
    _write_markdown(path, lines)


def _render_objects(*, path: Path, repo_root: Path, records: list[ObjectRecord]) -> None:
    lines = [
        "# Objects",
        "",
        "## Object Index",
        "",
        "| id | class | status | title | updated_at | path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    sorted_records = _sort_objects(records, repo_root)
    for record in sorted_records:
        lines.append(
            _table_row(
                [
                    _object_id(record),
                    record.object_class,
                    _metadata_text(record, "status"),
                    _metadata_text(record, "title"),
                    _metadata_text(record, "updated_at"),
                    _markdown_path_link(record_path=record.path, page_path=path, repo_root=repo_root),
                ]
            )
        )
    if not sorted_records:
        lines.extend(["", "_No objects found._"])
    _write_markdown(path, lines)


def _render_proposals(*, path: Path, repo_root: Path, records: list[ObjectRecord]) -> None:
    proposal_records = [record for record in records if record.object_class == "proposals"]
    lines = [
        "# Proposal Queue",
        "",
        "## Proposals",
        "",
        "| proposal_id | status | title | target_ids | created_by | created_at | path |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    sorted_records = _sort_proposals(proposal_records)
    for record in sorted_records:
        target_ids = _as_id_list(record.metadata.get("target_ids"))
        lines.append(
            _table_row(
                [
                    _proposal_id(record),
                    _metadata_text(record, "status"),
                    _metadata_text(record, "title"),
                    ", ".join(target_ids) if target_ids else MISSING_VALUE,
                    _metadata_text(record, "created_by"),
                    _metadata_text(record, "created_at"),
                    _markdown_path_link(record_path=record.path, page_path=path, repo_root=repo_root),
                ]
            )
        )
    if not sorted_records:
        lines.extend(["", "_No proposals found._"])
    _write_markdown(path, lines)


def _append_recent_table(
    lines: list[str],
    *,
    headers: list[str],
    rows: list[list[object]],
    empty_text: str,
) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append(_table_row(row))
    if not rows:
        lines.extend(["", empty_text])


def _render_recent(*, path: Path, repo_root: Path, records: list[ObjectRecord]) -> None:
    lines = ["# Recent Activity", "", "## Recent Logs", ""]

    log_rows = [
        [
            _object_id(record),
            _metadata_text(record, "status"),
            _metadata_text(record, "title"),
            _date_value(record, "updated_at", "created_at"),
            _markdown_path_link(record_path=record.path, page_path=path, repo_root=repo_root),
        ]
        for record in _sort_by_date_desc(
            [record for record in records if record.object_class == "logs"], "updated_at", "created_at"
        )
    ]
    _append_recent_table(
        lines,
        headers=["id", "status", "title", "timestamp", "path"],
        rows=log_rows,
        empty_text="_No recent logs found._",
    )

    lines.extend(["", "## Recent Proposals", ""])
    proposal_rows = [
        [
            _proposal_id(record),
            _metadata_text(record, "status"),
            _metadata_text(record, "title"),
            _metadata_text(record, "created_at"),
            _markdown_path_link(record_path=record.path, page_path=path, repo_root=repo_root),
        ]
        for record in _sort_by_date_desc(
            [record for record in records if record.object_class == "proposals"],
            "created_at",
            id_getter=_proposal_id,
        )
    ]
    _append_recent_table(
        lines,
        headers=["proposal_id", "status", "title", "created_at", "path"],
        rows=proposal_rows,
        empty_text="_No recent proposals found._",
    )

    lines.extend(["", "## Recent Structured Updates", ""])
    structured_rows = [
        [
            _object_id(record),
            _metadata_text(record, "status"),
            _metadata_text(record, "title"),
            _date_value(record, "updated_at", "created_at"),
            _markdown_path_link(record_path=record.path, page_path=path, repo_root=repo_root),
        ]
        for record in _sort_by_date_desc(
            [record for record in records if record.object_class == "structured"], "updated_at", "created_at"
        )
    ]
    _append_recent_table(
        lines,
        headers=["id", "status", "title", "updated_at", "path"],
        rows=structured_rows,
        empty_text="_No recent structured updates found._",
    )
    _write_markdown(path, lines)


def build_operator_projections(*, repo_root: Path, workspace: str) -> OperatorProjectionResult:
    resolved_repo_root = Path(repo_root).resolve()
    resolved_workspace = _resolve_workspace(resolved_repo_root, workspace)
    records = filter_records(load_records(resolved_repo_root), workspace=resolved_workspace.workspace_id)
    projection_root = resolved_workspace.workspace_root / "projection" / "operator"

    index_path = projection_root / "index.md"
    objects_path = projection_root / "objects.md"
    proposals_path = projection_root / "proposals.md"
    recent_path = projection_root / "recent.md"

    _render_index(path=index_path, repo_root=resolved_repo_root, workspace=resolved_workspace, records=records)
    _render_objects(path=objects_path, repo_root=resolved_repo_root, records=records)
    _render_proposals(path=proposals_path, repo_root=resolved_repo_root, records=records)
    _render_recent(path=recent_path, repo_root=resolved_repo_root, records=records)

    return OperatorProjectionResult(
        workspace_id=resolved_workspace.workspace_id,
        workspace_root=resolved_workspace.workspace_root,
        projection_root=projection_root,
        output_paths=(index_path, objects_path, proposals_path, recent_path),
        record_count=len(records),
    )
