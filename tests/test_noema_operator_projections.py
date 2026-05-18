from __future__ import annotations

from pathlib import Path

from packages.noema_operator.cli import main as operator_cli_main
from packages.noema_operator.projections import MISSING_VALUE, _format_table_cell, build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_operator_repo(repo: Path) -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-alpha"
    workspace_root.mkdir(parents=True)

    _write_object(
        workspace_root / "projection" / "operator" / "stale-generated-record.md",
        "\n".join(
            [
                "id: generated-operator-artifact",
                "class: structured",
                "workspace: ws-alpha",
                "status: active",
                "title: This generated file must not be scanned",
            ]
        ),
    )

    _write_object(
        repo / "raw" / "sources" / "raw-a.md",
        "\n".join(
            [
                "id: raw-a",
                "class: raw",
                "workspace: ws-alpha",
                "status: ingested",
                "title: Raw | Source",
                "created_at: 2026-04-01T00:00:00Z",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "struct-new.md",
        "\n".join(
            [
                "id: struct-new",
                "class: structured",
                "workspace: ws-alpha",
                "status: active",
                "title: New Structured",
                "created_at: 2026-04-02T00:00:00Z",
                "updated_at: 2026-04-05T00:00:00Z",
                "supports:",
                "  - raw-a",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "struct-missing-date.md",
        "\n".join(
            [
                "id: struct-missing-date",
                "class: structured",
                "workspace: ws-alpha",
                "status: active",
                "title: Missing Date Structured",
                "supports:",
                "  - raw-a",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-display.md",
        "\n".join(
            [
                "id: proposal-underlying",
                "proposal_id: proposal-display",
                "class: proposals",
                "workspace: ws-alpha",
                "status: under_review",
                "title: Proposal Display",
                "summary: Existing proposal summary",
                "created_by: agent:operator-test",
                "created_at: 2026-04-04T00:00:00Z",
                "target_ids:",
                "  - struct-new",
                "  - raw-a",
            ]
        ),
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-empty.md",
        "\n".join(
            [
                "id: proposal-empty",
                "class: proposals",
                "workspace: ws-alpha",
                "status: draft",
                "created_at: 2026-04-03T00:00:00Z",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-new.md",
        "\n".join(
            [
                "id: log-new",
                "class: logs",
                "workspace: ws-alpha",
                "status: recorded",
                "title: New Log",
                "created_at: 2026-04-06T00:00:00Z",
                "records_event_for:",
                "  - proposal-display",
            ]
        ),
    )
    _write_object(
        repo / "logs" / "events" / "log-missing-date.md",
        "\n".join(
            [
                "id: log-missing-date",
                "class: logs",
                "workspace: ws-alpha",
                "status: recorded",
                "title: Missing Date Log",
            ]
        ),
    )
    _write_object(
        repo / "structured" / "pages" / "struct-other.md",
        "\n".join(
            [
                "id: struct-other",
                "class: structured",
                "workspace: ws-beta",
                "status: active",
                "title: Other workspace",
                "updated_at: 2026-04-07T00:00:00Z",
            ]
        ),
    )
    return workspace_root


def test_table_cells_escape_markdown_and_missing_values() -> None:
    assert _format_table_cell(None) == MISSING_VALUE
    assert _format_table_cell("") == MISSING_VALUE
    assert _format_table_cell("alpha|beta\ngamma\rdelta") == "alpha\\|beta gamma delta"


def test_build_operator_projections_writes_deterministic_markdown(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = _seed_operator_repo(repo)

    result = build_operator_projections(repo_root=repo, workspace=str(workspace_root.relative_to(repo)))
    first_contents = {path.name: path.read_text(encoding="utf-8") for path in result.output_paths}
    second = build_operator_projections(repo_root=repo, workspace="ws-alpha")
    second_contents = {path.name: path.read_text(encoding="utf-8") for path in second.output_paths}

    assert result.workspace_id == "ws-alpha"
    assert result.record_count == 7
    assert first_contents == second_contents
    assert {path.relative_to(workspace_root).as_posix() for path in result.output_paths} == {
        "projection/operator/index.md",
        "projection/operator/objects.md",
        "projection/operator/proposals.md",
        "projection/operator/recent.md",
    }

    index = first_contents["index.md"]
    assert "# Operator Workspace" in index
    assert "## Workspace" in index
    assert "## Object Counts by Class" in index
    assert "## Object Counts by Status" in index
    assert "## Operator Links" in index
    assert "| raw | 1 |" in index
    assert "| structured | 2 |" in index
    assert "| proposals | 2 |" in index
    assert "| logs | 2 |" in index
    assert "- [Objects](./objects.md)" in index
    assert "- [Proposals](./proposals.md)" in index
    assert "- [Recent Activity](./recent.md)" in index

    objects = first_contents["objects.md"]
    assert "| id | class | status | title | updated_at | path |" in objects
    assert "Raw \\| Source" in objects
    assert "[raw/sources/raw-a.md](" in objects
    assert "generated-operator-artifact" not in objects
    assert "struct-other" not in objects
    assert objects.index("| raw-a | raw |") < objects.index("| struct-missing-date | structured |")
    assert objects.index("| struct-new | structured |") < objects.index("| proposal-empty | proposals |")

    proposals = first_contents["proposals.md"]
    assert "| proposal_id | status | title | target_ids | created_by | created_at | path |" in proposals
    assert "| proposal-display | under_review | Proposal Display | raw-a, struct-new | agent:operator-test | 2026-04-04T00:00:00Z |" in proposals
    assert "| proposal-empty | draft | — | — | — | 2026-04-03T00:00:00Z |" in proposals
    assert proposals.index("proposal-display") < proposals.index("proposal-empty")

    recent = first_contents["recent.md"]
    assert "# Recent Activity" in recent
    assert "## Recent Logs" in recent
    assert "## Recent Proposals" in recent
    assert "## Recent Structured Updates" in recent
    assert "| id | status | title | timestamp | path |" in recent
    assert "| proposal_id | status | title | created_at | path |" in recent
    assert "| id | status | title | updated_at | path |" in recent
    assert recent.index("log-new") < recent.index("log-missing-date")
    assert recent.index("proposal-display") < recent.index("proposal-empty")
    assert recent.index("struct-new") < recent.index("struct-missing-date")

    combined = "\n".join(first_contents.values())
    assert str(tmp_path) not in combined


def test_empty_workspace_path_still_generates_stable_empty_pages(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-empty"
    workspace_root.mkdir(parents=True)

    result = build_operator_projections(repo_root=repo, workspace=str(workspace_root))

    assert result.record_count == 0
    assert (workspace_root / "projection" / "operator" / "objects.md").read_text(encoding="utf-8").endswith(
        "_No objects found._\n"
    )
    assert "_No proposals found._" in (workspace_root / "projection" / "operator" / "proposals.md").read_text(
        encoding="utf-8"
    )
    recent = (workspace_root / "projection" / "operator" / "recent.md").read_text(encoding="utf-8")
    assert "_No recent logs found._" in recent
    assert "_No recent proposals found._" in recent
    assert "_No recent structured updates found._" in recent


def test_operator_cli_build_projections(tmp_path: Path, capsys) -> None:
    repo = tmp_path
    workspace_root = _seed_operator_repo(repo)

    exit_code = operator_cli_main(
        [
            "build-projections",
            "--repo-root",
            str(repo),
            "--workspace",
            "examples/workspaces/sample-research-workspace/workspaces/ws-alpha",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[noema-operator] rebuilt operator projections for workspace 'ws-alpha'" in captured.out
    assert (workspace_root / "projection" / "operator" / "index.md").exists()
    assert (workspace_root / "projection" / "operator" / "objects.md").exists()
    assert (workspace_root / "projection" / "operator" / "proposals.md").exists()
    assert (workspace_root / "projection" / "operator" / "recent.md").exists()
