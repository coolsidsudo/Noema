from __future__ import annotations

import json
from pathlib import Path

from packages.noema_maintainer.build_projection import build_workspace_projection
from packages.noema_maintainer.checks import ValidationIssue, validate_records
from packages.noema_maintainer.cli import run
from packages.noema_maintainer.scan import scan_repository


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def test_scan_and_validation_and_build_deterministic(tmp_path: Path) -> None:
    repo = tmp_path

    _write_object(
        repo / "raw" / "sources" / "raw-a.md",
        "\n".join(
            [
                "id: raw-a",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: ingested",
                "title: Raw A",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "struct-a.md",
        "\n".join(
            [
                "id: struct-a",
                "class: structured",
                "created_at: 2026-04-02T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: active",
                "title: Structured A",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-a.md",
        "\n".join(
            [
                "id: proposal-a",
                "class: proposals",
                "created_at: 2026-04-03T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: under_review",
                "target_ids:",
                "  - struct-a",
                "supporting_raw_ids:",
                "  - raw-a",
                "results_in:",
                "  - struct-a",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-a.md",
        "\n".join(
            [
                "id: log-a",
                "class: logs",
                "created_at: 2026-04-04T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: recorded",
                "event_type: rebuild",
                "summary: Rebuilt projection after metadata refresh.",
                "records_event_for:",
                "  - proposal-a",
                "  - struct-a",
                "updated_at: 2026-04-04T01:00:00Z",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-bad.md",
        "\n".join(
            [
                "id: log-bad",
                "class: logs",
                "created_at: 2026-04-04T02:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: recorded",
                "event_type: review_reject",
                "records_event_for:",
                "  - missing-proposal",
            ]
        ),
    )

    _write_object(
        repo / "proposals" / "queue" / "proposal-bad.md",
        "\n".join(
            [
                "id: proposal-bad",
                "class: proposals",
                "created_at: 2026-04-05T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: under_review",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-missing-ref.md",
        "\n".join(
            [
                "id: proposal-missing-ref",
                "class: proposals",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-alpha",
                "status: accepted",
                "target_ids:",
                "  - missing-struct",
                "results_in:",
                "  - missing-result",
            ]
        ),
    )

    ws_root = repo / "workspace-root"
    (ws_root / "ws-alpha").mkdir(parents=True)

    records = scan_repository(repo)
    issues = validate_records(records)
    assert [r.metadata["id"] for r in records] == sorted([r.metadata["id"] for r in records])
    assert any(i.code == "proposal_missing_targets" for i in issues)

    first = run(["--repo-root", str(repo), "--workspaces-root", "workspace-root", "--workspace", "ws-alpha"])
    first_queue = (ws_root / "ws-alpha" / "projection" / "review" / "proposal-queue.md").read_text(encoding="utf-8")
    first_home = (ws_root / "ws-alpha" / "projection" / "home" / "README.md").read_text(encoding="utf-8")
    second = run(["--repo-root", str(repo), "--workspaces-root", "workspace-root", "--workspace", "ws-alpha"])
    assert first == 0
    assert second == 0

    report_path = ws_root / "ws-alpha" / "projection" / "build-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["workspace"] == "ws-alpha"
    assert report["class_counts"]["raw"] == 1
    assert report["validation"]["error_count"] >= 1

    by_class_raw = (ws_root / "ws-alpha" / "projection" / "browse" / "by-class-raw.md").read_text(encoding="utf-8")
    browse_readme = (ws_root / "ws-alpha" / "projection" / "browse" / "README.md").read_text(encoding="utf-8")
    home_readme = (ws_root / "ws-alpha" / "projection" / "home" / "README.md").read_text(encoding="utf-8")
    proposal_queue = (ws_root / "ws-alpha" / "projection" / "review" / "proposal-queue.md").read_text(encoding="utf-8")
    recent_changes = (ws_root / "ws-alpha" / "projection" / "logs" / "recent-changes.md").read_text(encoding="utf-8")
    assert "raw-a" in by_class_raw
    tmp_path_str = str(tmp_path)
    report_text = report_path.read_text(encoding="utf-8")

    assert tmp_path_str not in by_class_raw
    assert tmp_path_str not in report_text
    assert "`raw/sources/raw-a.md`" in by_class_raw
    assert "workspace-root/ws-alpha/projection/browse/by-class-raw.md" in report["outputs"]
    assert "workspace-root/ws-alpha/projection/home/README.md" in report["outputs"]
    assert "workspace-root/ws-alpha/projection/browse/README.md" in report["outputs"]
    assert all(not output.startswith(tmp_path_str) for output in report["outputs"])
    assert all(not error["object_path"].startswith(tmp_path_str) for error in report["validation"]["errors"])
    assert "- `raw` (1): `./by-class-raw.md`" in browse_readme
    assert "- `proposals` (3): `./by-class-proposals.md`" in browse_readme
    assert "- Workspace: `ws-alpha`" in home_readme
    assert "- Total records: `7`" in home_readme
    assert "- `logs`: `2`" in home_readme
    assert "- Browse `structured`: `../browse/by-class-structured.md`" in home_readme
    assert "- Proposal review queue: `../review/proposal-queue.md`" in home_readme
    assert "- Recent changes: `../logs/recent-changes.md`" in home_readme
    assert "- Validation issue count: `4`" in home_readme
    assert "proposal_target_reference_not_found" in home_readme
    assert "proposal_results_in_reference_not_found" in home_readme
    assert "log_records_event_for_reference_not_found" in home_readme
    assert "proposal_missing_targets" in home_readme
    assert "Targets: `struct-a` (`structured/pages/struct-a.md`)" in proposal_queue
    assert "Supporting raw ids: `raw-a` (`raw/sources/raw-a.md`)" in proposal_queue
    assert "Results in: `struct-a` (`structured/pages/struct-a.md`)" in proposal_queue
    assert (
        "Validation warning: unresolved references (proposal_results_in_reference_not_found, "
        "proposal_target_reference_not_found)"
    ) in proposal_queue
    assert "\n\n- `proposal-bad`" in proposal_queue
    assert "- `log-bad` (recorded) — `logs/events/log-bad.md`" in recent_changes
    assert "Event type: `review_reject`" in recent_changes
    assert "Recent timestamp cue (created_at): `2026-04-04T02:00:00Z`" in recent_changes
    assert "Records event for: `missing-proposal` (unresolved)" in recent_changes
    assert (
        "Validation warning: unresolved records_event_for references: "
        "`missing-proposal`"
    ) in recent_changes
    assert "- `log-a` (recorded) — `logs/events/log-a.md`" in recent_changes
    assert "Event type: `rebuild`" in recent_changes
    assert "Recent timestamp cue (updated_at): `2026-04-04T01:00:00Z`" in recent_changes
    assert (
        "Records event for: `proposal-a` (`proposals/queue/proposal-a.md`), "
        "`struct-a` (`structured/pages/struct-a.md`)"
    ) in recent_changes
    assert "Summary: Rebuilt projection after metadata refresh." in recent_changes
    assert recent_changes.index("`log-bad`") < recent_changes.index("`log-a`")
    assert proposal_queue == first_queue
    assert home_readme == first_home


def test_cli_all_workspaces(tmp_path: Path) -> None:
    repo = tmp_path
    _write_object(
        repo / "raw" / "sources" / "raw-a.md",
        "\n".join(
            [
                "id: raw-a",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: ingested",
            ]
        ),
    )
    _write_object(
        repo / "raw" / "sources" / "raw-b.md",
        "\n".join(
            [
                "id: raw-b",
                "class: raw",
                "created_at: 2026-04-02T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: ingested",
            ]
        ),
    )

    ws_root = repo / "workspace-root"
    (ws_root / "ws-one").mkdir(parents=True)
    (ws_root / "ws-two").mkdir(parents=True)

    code = run(["--repo-root", str(repo), "--workspaces-root", "workspace-root"])
    assert code == 0
    assert (ws_root / "ws-one" / "projection" / "build-report.json").exists()
    assert (ws_root / "ws-two" / "projection" / "build-report.json").exists()


def test_report_outputs_no_absolute_paths_when_workspaces_root_is_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _write_object(
        repo / "raw" / "sources" / "raw-ext.md",
        "\n".join(
            [
                "id: raw-ext",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-ext",
                "status: ingested",
            ]
        ),
    )

    external_ws_root = tmp_path / "workspace-root-outside"
    (external_ws_root / "ws-ext").mkdir(parents=True)

    code = run(["--repo-root", str(repo), "--workspaces-root", str(external_ws_root), "--workspace", "ws-ext"])
    assert code == 0

    report_path = external_ws_root / "ws-ext" / "projection" / "build-report.json"
    report_text = report_path.read_text(encoding="utf-8")
    report = json.loads(report_text)

    tmp_path_str = str(tmp_path)
    assert tmp_path_str not in report_text
    assert all(not output.startswith(tmp_path_str) for output in report["outputs"])
    assert "ws-ext/projection/browse/by-class-raw.md" in report["outputs"]


def test_relationship_cross_reference_checks_workspace_local(tmp_path: Path) -> None:
    repo = tmp_path
    ws_root = repo / "workspace-root"
    (ws_root / "ws-one").mkdir(parents=True)
    (ws_root / "ws-two").mkdir(parents=True)

    _write_object(
        repo / "raw" / "sources" / "raw-one.md",
        "\n".join(
            [
                "id: raw-one",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: ingested",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "structured-one.md",
        "\n".join(
            [
                "id: structured-one",
                "class: structured",
                "created_at: 2026-04-02T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: active",
                "supports:",
                "  - raw-one",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-accepted-ok.md",
        "\n".join(
            [
                "id: proposal-accepted-ok",
                "class: proposals",
                "created_at: 2026-04-03T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: accepted",
                "target_ids:",
                "  - structured-one",
                "results_in:",
                "  - structured-one",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-ok.md",
        "\n".join(
            [
                "id: log-ok",
                "class: logs",
                "created_at: 2026-04-04T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: recorded",
                "records_event_for:",
                "  - proposal-accepted-ok",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "structured-supersedes-ok.md",
        "\n".join(
            [
                "id: structured-supersedes-ok",
                "class: structured",
                "created_at: 2026-04-05T00:00:00Z",
                "created_by: tester",
                "workspace: ws-one",
                "status: active",
                "supersedes:",
                "  - structured-one",
            ]
        ),
    )

    _write_object(
        repo / "raw" / "sources" / "raw-two.md",
        "\n".join(
            [
                "id: raw-two",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: ingested",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-bad-target.md",
        "\n".join(
            [
                "id: proposal-bad-target",
                "class: proposals",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: under_review",
                "target_ids:",
                "  - missing-target",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-bad-results.md",
        "\n".join(
            [
                "id: proposal-bad-results",
                "class: proposals",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: accepted",
                "target_ids:",
                "  - raw-two",
                "results_in:",
                "  - missing-result",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-bad-event.md",
        "\n".join(
            [
                "id: log-bad-event",
                "class: logs",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: recorded",
                "records_event_for:",
                "  - missing-event-object",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "structured-bad-support.md",
        "\n".join(
            [
                "id: structured-bad-support",
                "class: structured",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: active",
                "supports:",
                "  - missing-raw",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "structured-bad-supersedes.md",
        "\n".join(
            [
                "id: structured-bad-supersedes",
                "class: structured",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: active",
                "supersedes:",
                "  - missing-prior-object",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-cross-workspace.md",
        "\n".join(
            [
                "id: proposal-cross-workspace",
                "class: proposals",
                "created_at: 2026-04-06T00:00:00Z",
                "created_by: tester",
                "workspace: ws-two",
                "status: under_review",
                "target_ids:",
                "  - structured-one",
            ]
        ),
    )

    records = scan_repository(repo)
    issues = validate_records(records)
    issue_codes = {issue.code for issue in issues}

    assert "proposal_target_reference_not_found" in issue_codes
    assert "proposal_results_in_reference_not_found" in issue_codes
    assert "log_records_event_for_reference_not_found" in issue_codes
    assert "structured_supports_reference_not_found_raw" in issue_codes
    assert "supersedes_reference_not_found" in issue_codes

    ws_one_issues = [issue for issue in issues if issue.workspace == "ws-one"]
    assert all(issue.code not in {
        "proposal_target_reference_not_found",
        "proposal_results_in_reference_not_found",
        "log_records_event_for_reference_not_found",
        "structured_supports_reference_not_found_raw",
        "supersedes_reference_not_found",
    } for issue in ws_one_issues)

    run(["--repo-root", str(repo), "--workspaces-root", "workspace-root", "--workspace", "ws-two"])
    report_path = ws_root / "ws-two" / "projection" / "build-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    error_codes = {error["code"] for error in report["validation"]["errors"]}
    assert "proposal_target_reference_not_found" in error_codes
    assert "proposal_results_in_reference_not_found" in error_codes
    assert "log_records_event_for_reference_not_found" in error_codes
    assert "structured_supports_reference_not_found_raw" in error_codes
    assert "supersedes_reference_not_found" in error_codes


def test_workspace_home_validation_summary_is_bounded(tmp_path: Path) -> None:
    repo = tmp_path
    ws_root = repo / "workspace-root"
    (ws_root / "ws-bounded").mkdir(parents=True)

    _write_object(
        repo / "raw" / "sources" / "raw-bounded.md",
        "\n".join(
            [
                "id: raw-bounded",
                "class: raw",
                "created_at: 2026-04-01T00:00:00Z",
                "created_by: tester",
                "workspace: ws-bounded",
                "status: ingested",
            ]
        ),
    )

    records = scan_repository(repo)
    issues = [
        ValidationIssue(
            code=f"issue-{idx}",
            message=f"Issue {idx}",
            object_path=str(repo / "raw" / "sources" / "raw-bounded.md"),
            object_id="raw-bounded",
            workspace="ws-bounded",
        )
        for idx in range(1, 8)
    ]

    build_workspace_projection(
        repo_root=repo,
        workspace_root=ws_root,
        workspace="ws-bounded",
        records=records,
        issues=issues,
    )

    home_readme = (ws_root / "ws-bounded" / "projection" / "home" / "README.md").read_text(encoding="utf-8")
    assert "- Validation issue count: `7`" in home_readme
    assert "issue-1" in home_readme
    assert "issue-5" in home_readme
    assert "issue-6" not in home_readme
    assert "issue-7" not in home_readme
    assert "_2 more issue code(s) not shown._" in home_readme
