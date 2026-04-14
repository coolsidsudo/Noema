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


def _build_path_hint_by_id(workspace_records: list[ObjectRecord], repo_root: Path) -> dict[str, str]:
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
    return path_hint_by_id


def _issue_codes_for_record(
    *,
    record: ObjectRecord,
    repo_root: Path,
    workspace_issues: list[ValidationIssue],
) -> list[str]:
    object_id = str(record.metadata.get("id", ""))
    rel_path = _render_repo_relative_path(record.path, repo_root)
    codes: set[str] = set()
    for issue in workspace_issues:
        if issue.object_id and object_id and issue.object_id == object_id:
            codes.add(issue.code)
            continue
        issue_rel_path = _render_repo_relative_path(Path(issue.object_path), repo_root)
        if issue_rel_path == rel_path:
            codes.add(issue.code)
    return sorted(codes)


def _render_enriched_browse_lines(
    *,
    object_class: str,
    page_records: list[ObjectRecord],
    repo_root: Path,
    workspace_records: list[ObjectRecord],
    workspace_issues: list[ValidationIssue],
) -> list[str]:
    if not page_records:
        return ["- _No records found._"]

    path_hint_by_id = _build_path_hint_by_id(workspace_records, repo_root)
    lines: list[str] = []
    for record in page_records:
        lines.append(_object_line(record, repo_root))

        recency_source = "updated_at" if record.metadata.get("updated_at") else "created_at"
        recency_value = str(record.metadata.get(recency_source, "")).strip()
        if recency_value:
            lines.append(f"  - Timestamp cue ({recency_source}): `{recency_value}`")

        summary = str(record.metadata.get("summary", "")).strip()
        if summary:
            lines.append(f"  - Summary: {summary}")

        tags = _as_id_list(record.metadata.get("tags"))
        if tags:
            rendered_tags = ", ".join(f"`{tag}`" for tag in sorted(set(tags)))
            lines.append(f"  - Tags: {rendered_tags}")

        if object_class == "structured":
            support_ids = _as_id_list(record.metadata.get("supports"))
            if support_ids:
                rendered_support = ", ".join(
                    _render_reference_with_hint(support_id, path_hint_by_id) for support_id in support_ids
                )
                lines.append(f"  - Supports: {rendered_support}")

        if object_class == "proposals":
            target_ids = _as_id_list(record.metadata.get("target_ids"))
            if target_ids:
                rendered_targets = ", ".join(
                    _render_reference_with_hint(target_id, path_hint_by_id) for target_id in target_ids
                )
                lines.append(f"  - Targets: {rendered_targets}")

            result_ids = _as_id_list(record.metadata.get("results_in"))
            if result_ids:
                rendered_results = ", ".join(
                    _render_reference_with_hint(result_id, path_hint_by_id) for result_id in result_ids
                )
                lines.append(f"  - Results in: {rendered_results}")

        if object_class == "logs":
            event_for_ids = _as_id_list(record.metadata.get("records_event_for"))
            if event_for_ids:
                rendered_event_for = ", ".join(
                    _render_reference_with_hint(event_for_id, path_hint_by_id) for event_for_id in event_for_ids
                )
                lines.append(f"  - Records event for: {rendered_event_for}")

        supersedes_ids = _as_id_list(record.metadata.get("supersedes"))
        if supersedes_ids:
            rendered_supersedes = ", ".join(
                _render_reference_with_hint(superseded_id, path_hint_by_id) for superseded_id in supersedes_ids
            )
            lines.append(f"  - Supersedes: {rendered_supersedes}")

        issue_codes = _issue_codes_for_record(
            record=record,
            repo_root=repo_root,
            workspace_issues=workspace_issues,
        )
        if issue_codes:
            preview_codes = issue_codes[:3]
            remaining_count = len(issue_codes) - len(preview_codes)
            if remaining_count > 0:
                code_summary = f"{', '.join(preview_codes)} (+{remaining_count} more)"
            else:
                code_summary = ", ".join(preview_codes)
            lines.append(f"  - ⚠ Validation warning: {code_summary}")

        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return lines


def _render_proposal_queue_lines(
    proposal_records: list[ObjectRecord],
    *,
    repo_root: Path,
    workspace_records: list[ObjectRecord],
    issues: list[ValidationIssue],
    workspace: str,
) -> list[str]:
    path_hint_by_id = _build_path_hint_by_id(workspace_records, repo_root)

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


def _render_recent_changes_lines(
    log_records: list[ObjectRecord],
    *,
    repo_root: Path,
    workspace_records: list[ObjectRecord],
    issues: list[ValidationIssue],
    workspace: str,
) -> list[str]:
    if not log_records:
        return ["- _No recent log changes found._"]

    path_hint_by_id = _build_path_hint_by_id(workspace_records, repo_root)

    unresolved_issue_codes_by_log: dict[str, set[str]] = {}
    for issue in issues:
        if issue.workspace != workspace:
            continue
        if issue.code != "log_records_event_for_reference_not_found":
            continue
        if not issue.object_id:
            continue
        unresolved_issue_codes_by_log.setdefault(issue.object_id, set()).add(issue.code)

    lines: list[str] = []
    for log_record in log_records:
        log_id = str(log_record.metadata.get("id", ""))
        lines.append(_object_line(log_record, repo_root))

        event_type = str(log_record.metadata.get("event_type", "")).strip()
        if event_type:
            lines.append(f"  - Event type: `{event_type}`")

        recency_source = "updated_at" if log_record.metadata.get("updated_at") else "created_at"
        recency_value = str(log_record.metadata.get(recency_source, "")).strip()
        if recency_value:
            lines.append(f"  - Recent timestamp cue ({recency_source}): `{recency_value}`")

        event_for_ids = _as_id_list(log_record.metadata.get("records_event_for"))
        if event_for_ids:
            rendered_event_for = ", ".join(
                _render_reference_with_hint(event_for_id, path_hint_by_id) for event_for_id in event_for_ids
            )
            lines.append(f"  - Records event for: {rendered_event_for}")

        summary = str(log_record.metadata.get("summary", "")).strip()
        if summary:
            lines.append(f"  - Summary: {summary}")

        unresolved_codes = sorted(unresolved_issue_codes_by_log.get(log_id, set()))
        if unresolved_codes:
            unresolved_event_for_ids = sorted(event_for_id for event_for_id in event_for_ids if event_for_id not in path_hint_by_id)
            if unresolved_event_for_ids:
                unresolved_preview = ", ".join(f"`{event_for_id}`" for event_for_id in unresolved_event_for_ids[:3])
                remaining_count = len(unresolved_event_for_ids) - 3
                if remaining_count > 0:
                    unresolved_preview = f"{unresolved_preview} (+{remaining_count} more)"
                lines.append(
                    f"  - ⚠ Validation warning: unresolved records_event_for references: {unresolved_preview}"
                )
            else:
                lines.append("  - ⚠ Validation warning: unresolved records_event_for references detected")

        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return lines


def _render_workspace_home_lines(
    *,
    workspace: str,
    class_counts: dict[str, int],
    workspace_issues: list[ValidationIssue],
) -> list[str]:
    lines: list[str] = [
        "Welcome to the deterministic workspace projection landing page.",
        "",
        "## Workspace summary",
        f"- Workspace: `{workspace}`",
        f"- Total records: `{sum(class_counts.values())}`",
        "",
        "### Class counts",
    ]
    for object_class in OBJECT_CLASSES:
        lines.append(f"- `{object_class}`: `{class_counts[object_class]}`")

    lines.extend(
        [
            "",
            "## Navigation",
            "- Browse all classes: `../browse/README.md`",
        ]
    )
    for object_class in OBJECT_CLASSES:
        lines.append(f"- Browse `{object_class}`: `../browse/by-class-{object_class}.md`")
    lines.extend(
        [
            "- Proposal review queue: `../review/proposal-queue.md`",
            "- Recent changes: `../logs/recent-changes.md`",
            "- Build report: `../build-report.json`",
            "",
            "## Validation summary",
        ]
    )

    if not workspace_issues:
        lines.append("- ✅ No validation issues detected for this workspace.")
        return lines

    lines.append(f"- Validation issue count: `{len(workspace_issues)}`")
    code_counts: dict[str, int] = {}
    for issue in workspace_issues:
        code_counts[issue.code] = code_counts.get(issue.code, 0) + 1
    lines.append("- Top issue codes:")
    for code, count in sorted(code_counts.items(), key=lambda item: (-item[1], item[0]))[:5]:
        lines.append(f"  - `{code}`: `{count}`")

    remaining = len(code_counts) - 5
    if remaining > 0:
        lines.append(f"  - _{remaining} more issue code(s) not shown._")
    lines.append("- See `../build-report.json` for full issue details.")
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
    class_counts = {cls: len([r for r in workspace_records if r.object_class == cls]) for cls in OBJECT_CLASSES}
    workspace_issues = [i for i in issues if i.workspace == workspace]

    home_lines = _render_workspace_home_lines(
        workspace=workspace,
        class_counts=class_counts,
        workspace_issues=workspace_issues,
    )
    home_page = projection_root / "home" / "README.md"
    _write_markdown(home_page, "Workspace Home", home_lines)
    outputs.append(_render_output_path(home_page, repo_root, workspace_root))

    for object_class in OBJECT_CLASSES:
        page_records = [r for r in workspace_records if r.object_class == object_class]
        lines = _render_enriched_browse_lines(
            object_class=object_class,
            page_records=page_records,
            repo_root=repo_root,
            workspace_records=workspace_records,
            workspace_issues=workspace_issues,
        )
        output_path = browse_root / f"by-class-{object_class}.md"
        _write_markdown(output_path, f"Browse by class: {object_class}", lines)
        outputs.append(_render_output_path(output_path, repo_root, workspace_root))

    browse_index_lines = ["Browse workspace records by object class:"]
    browse_index_lines.extend(
        [f"- `{object_class}` ({class_counts[object_class]}): `./by-class-{object_class}.md`" for object_class in OBJECT_CLASSES]
    )
    browse_readme = browse_root / "README.md"
    _write_markdown(browse_readme, "Browse by class", browse_index_lines)
    outputs.append(_render_output_path(browse_readme, repo_root, workspace_root))

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
    log_lines = _render_recent_changes_lines(
        log_records,
        repo_root=repo_root,
        workspace_records=workspace_records,
        issues=issues,
        workspace=workspace,
    )
    recent_changes = logs_root / "recent-changes.md"
    _write_markdown(recent_changes, "Recent changes", log_lines)
    outputs.append(_render_output_path(recent_changes, repo_root, workspace_root))

    report = {
        "workspace": workspace,
        "record_count": len(workspace_records),
        "class_counts": class_counts,
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
