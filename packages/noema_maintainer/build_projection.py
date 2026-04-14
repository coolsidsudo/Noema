from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .checks import ValidationIssue
from .scan import OBJECT_CLASSES, ObjectRecord


def _render_repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _render_output_path(path: Path, repo_root: Path, workspace_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path.relative_to(workspace_root))


def _object_line(record: ObjectRecord, repo_root: Path) -> str:
    title = str(record.metadata.get("title", ""))
    rel_path = _render_repo_relative_path(record.path, repo_root)
    base = f"- `{record.metadata.get('id', '')}`"
    if title:
        base += f": {title}"
    base += f" ({record.metadata.get('status', '')})"
    base += f" — `{rel_path}`"
    return base


def _write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", "", *lines, ""]
    path.write_text("\n".join(body), encoding="utf-8")


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _render_reference_with_hint(
    object_id: str,
    path_hint_by_id: dict[str, str],
) -> str:
    path_hint = path_hint_by_id.get(object_id)
    if path_hint:
        return f"`{object_id}` (`{path_hint}`)"
    return f"`{object_id}` (unresolved)"


def _render_proposal_queue_lines(
    proposal_records: list[ObjectRecord],
    *,
    repo_root: Path,
    workspace_records: list[ObjectRecord],
    issues: list[ValidationIssue],
    workspace: str,
) -> list[str]:
    path_hint_by_id: dict[str, str] = {}
    for record in sorted(
        workspace_records,
        key=lambda r: (
            str(r.metadata.get("id", "")),
            r.object_class,
            str(r.path),
        ),
    ):
        object_id = str(record.metadata.get("id", ""))
        if object_id and object_id not in path_hint_by_id:
            path_hint_by_id[object_id] = _render_repo_relative_path(record.path, repo_root)

    unresolved_issue_codes_by_proposal: dict[str, set[str]] = {}
    for issue in issues:
        if issue.workspace != workspace:
            continue
        if "_reference_not_found" not in issue.code:
            continue
        if not issue.object_id:
            continue
        unresolved_issue_codes_by_proposal.setdefault(issue.object_id, set()).add(issue.code)

    lines: list[str] = []
    for proposal in proposal_records:
        proposal_id = str(proposal.metadata.get("id", ""))
        lines.append(_object_line(proposal, repo_root))

        target_ids = _as_id_list(proposal.metadata.get("target_ids"))
        if target_ids:
            rendered_targets = ", ".join(
                _render_reference_with_hint(target_id, path_hint_by_id) for target_id in target_ids
            )
            lines.append(f"  - Targets: {rendered_targets}")

        support_ids: list[str] = []
        for key in ("supporting_raw_ids", "support_raw_ids", "supports"):
            support_ids.extend(_as_id_list(proposal.metadata.get(key)))
        support_ids = sorted(set(support_ids))
        if support_ids:
            rendered_support = ", ".join(
                _render_reference_with_hint(support_id, path_hint_by_id) for support_id in support_ids
            )
            lines.append(f"  - Supporting raw ids: {rendered_support}")

        result_ids = _as_id_list(proposal.metadata.get("results_in"))
        if result_ids:
            rendered_results = ", ".join(
                _render_reference_with_hint(result_id, path_hint_by_id) for result_id in result_ids
            )
            lines.append(f"  - Results in: {rendered_results}")

        unresolved_codes = sorted(unresolved_issue_codes_by_proposal.get(proposal_id, set()))
        if unresolved_codes:
            preview_codes = unresolved_codes[:2]
            remaining_count = len(unresolved_codes) - len(preview_codes)
            if remaining_count > 0:
                code_summary = f"{', '.join(preview_codes)} (+{remaining_count} more)"
            else:
                code_summary = ", ".join(preview_codes)
            lines.append(f"  - ⚠ Validation warning: unresolved references ({code_summary})")

        lines.append("")

    if not lines:
        return ["- _No proposals found._"]

    while lines and lines[-1] == "":
        lines.pop()
    return lines


def build_workspace_projection(
    repo_root: Path,
    workspace_root: Path,
    workspace: str,
    records: list[ObjectRecord],
    issues: list[ValidationIssue],
) -> dict[str, Any]:
    workspace_records = [r for r in records if str(r.metadata.get("workspace", "")) == workspace]
    workspace_records.sort(key=lambda r: (r.object_class, str(r.metadata.get("id", "")), str(r.path)))

    projection_root = workspace_root / workspace / "projection"
    browse_root = projection_root / "browse"
    review_root = projection_root / "review"
    logs_root = projection_root / "logs"

    outputs: list[str] = []

    for object_class in OBJECT_CLASSES:
        page_records = [r for r in workspace_records if r.object_class == object_class]
        lines = [_object_line(r, repo_root) for r in page_records]
        if not lines:
            lines = ["- _No records found._"]
        output_path = browse_root / f"by-class-{object_class}.md"
        _write_markdown(output_path, f"Browse by class: {object_class}", lines)
        outputs.append(_render_output_path(output_path, repo_root, workspace_root))

    proposal_records = [r for r in workspace_records if r.object_class == "proposals"]
    status_priority = {"under_review": 0, "draft": 1, "accepted": 2, "rejected": 3, "withdrawn": 4}
    proposal_records.sort(
        key=lambda r: (
            status_priority.get(str(r.metadata.get("status", "")), 99),
            str(r.metadata.get("created_at", "")),
            str(r.metadata.get("id", "")),
        )
    )
    proposal_lines = _render_proposal_queue_lines(
        proposal_records,
        repo_root=repo_root,
        workspace_records=workspace_records,
        issues=issues,
        workspace=workspace,
    )
    proposal_queue = review_root / "proposal-queue.md"
    _write_markdown(proposal_queue, "Proposal review queue", proposal_lines)
    outputs.append(_render_output_path(proposal_queue, repo_root, workspace_root))

    log_records = [r for r in workspace_records if r.object_class == "logs"]
    log_records.sort(
        key=lambda r: (
            str(r.metadata.get("updated_at", r.metadata.get("created_at", ""))),
            str(r.metadata.get("id", "")),
        ),
        reverse=True,
    )
    log_lines = [_object_line(r, repo_root) for r in log_records] or ["- _No recent log changes found._"]
    recent_changes = logs_root / "recent-changes.md"
    _write_markdown(recent_changes, "Recent changes", log_lines)
    outputs.append(_render_output_path(recent_changes, repo_root, workspace_root))

    workspace_issues = [i for i in issues if i.workspace == workspace]
    report = {
        "workspace": workspace,
        "record_count": len(workspace_records),
        "class_counts": {cls: len([r for r in workspace_records if r.object_class == cls]) for cls in OBJECT_CLASSES},
        "validation": {
            "error_count": len(workspace_issues),
            "errors": [
                {
                    "code": i.code,
                    "message": i.message,
                    "object_path": _render_repo_relative_path(Path(i.object_path), repo_root),
                    "object_id": i.object_id,
                }
                for i in workspace_issues
            ],
        },
        "outputs": sorted(outputs),
    }

    report_path = projection_root / "build-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return report
