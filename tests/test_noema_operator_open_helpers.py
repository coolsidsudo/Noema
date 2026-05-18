from __future__ import annotations

from pathlib import Path

from packages.noema_operator.cli import main as operator_cli_main
from packages.noema_operator.navigation import build_navigation_bundle
from packages.noema_operator.open_helpers import build_open_command, execute_open_command, resolve_open_value
from packages.noema_operator.projections import build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_open_repo(repo: Path) -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-open"
    workspace_root.mkdir(parents=True)
    _write_object(repo / "raw" / "raw-1.md", "\n".join([
        "id: raw-1",
        "class: raw",
        "workspace: ws-open",
        "status: ingested",
    ]))
    _write_object(repo / "structured" / "target.md", "\n".join([
        "id: target-1",
        "class: structured",
        "workspace: ws-open",
        "status: active",
    ]))
    _write_object(repo / "proposals" / "ready.md", "\n".join([
        "id: proposal-ready",
        "class: proposals",
        "workspace: ws-open",
        "status: under_review",
        "target_ids:",
        "  - target-1",
        "evidence_ids:",
        "  - raw-1",
    ]))
    return workspace_root


def test_open_helpers_print_resolution_without_execution(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_open_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-open")
    bundle = build_navigation_bundle(repo_root=repo, workspace="ws-open")

    resolution, value, diagnostics = resolve_open_value(bundle.registry, target_id="review:queue", mode="file")
    assert diagnostics == ()
    assert resolution is not None
    assert value.endswith("projection/operator/review/queue.md")
    resolution, uri, diagnostics = resolve_open_value(bundle.registry, target_id="review:queue", mode="file-uri")
    assert diagnostics == ()
    assert uri.startswith("file://")
    resolution, value, diagnostics = resolve_open_value(bundle.registry, target_id="review:queue", mode="obsidian-uri")
    assert resolution is None
    assert value == ""
    assert diagnostics[0].code == "unsupported_open_mode"


def test_open_helpers_execute_uses_tokenized_fake_runner(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    _seed_open_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-open")
    bundle = build_navigation_bundle(repo_root=repo, workspace="ws-open")
    monkeypatch.setattr("packages.noema_operator.open_helpers.platform.system", lambda: "Darwin")

    command = build_open_command(bundle.registry, target_id="review:queue", mode="file")
    assert command.command[0] == "open"
    assert isinstance(command.command, tuple)
    calls: list[tuple[list[str], bool]] = []

    class Completed:
        returncode = 0

    def fake_runner(cmd, check):
        calls.append((cmd, check))
        return Completed()

    assert execute_open_command(command, runner=fake_runner) == 0
    assert calls == [(list(command.command), False)]


def test_open_helpers_unsupported_platform_diagnostic(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    _seed_open_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-open")
    bundle = build_navigation_bundle(repo_root=repo, workspace="ws-open")
    monkeypatch.setattr("packages.noema_operator.open_helpers.platform.system", lambda: "Plan9")

    command = build_open_command(bundle.registry, target_id="review:queue", mode="file")
    assert command.command == ()
    assert command.diagnostics[0].code == "unsupported_platform_for_execute"


def test_navigation_cli_commands_are_deterministic_and_safe(monkeypatch, tmp_path: Path, capsys) -> None:
    repo = tmp_path
    workspace_root = _seed_open_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-open")

    assert operator_cli_main(["list-navigation-targets", "--repo-root", str(repo), "--workspace", "ws-open"]) == 0
    captured = capsys.readouterr()
    assert "operator:index" in captured.out
    assert "review:queue" in captured.out

    assert operator_cli_main(["list-navigation-targets", "--repo-root", str(repo), "--workspace", "ws-open", "--kind", "review_page"]) == 0
    captured = capsys.readouterr()
    assert "review:queue" in captured.out
    assert "operator:index" not in captured.out

    assert operator_cli_main(["resolve-navigation-target", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "review:queue", "--format", "repo-relative-path"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip().endswith("projection/operator/review/queue.md")

    assert operator_cli_main(["resolve-navigation-target", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "source:raw-1", "--format", "workspace-relative-path"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "—"

    assert operator_cli_main(["resolve-navigation-target", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "review:queue", "--format", "file-uri"]) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("file://")

    assert operator_cli_main(["resolve-navigation-target", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "review:missing"]) != 0
    captured = capsys.readouterr()
    assert "unknown target: review:missing" in captured.err

    assert operator_cli_main(["list-operator-routes", "--repo-root", str(repo), "--workspace", "ws-open"]) == 0
    captured = capsys.readouterr()
    assert "route:proposal-triage" in captured.out

    assert operator_cli_main(["show-operator-route", "--repo-root", str(repo), "--workspace", "ws-open", "--route", "route:proposal-triage"]) == 0
    captured = capsys.readouterr()
    assert "Purpose:" in captured.out
    assert "Entry target: review:queue" in captured.out
    assert "Checklist:" in captured.out

    assert operator_cli_main(["build-operator-handoff", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "review:packet:proposal-ready"]) == 0
    captured = capsys.readouterr()
    assert "Handoff: handoff:packet-review:proposal-ready" in captured.out

    assert operator_cli_main(["build-operator-handoff", "--repo-root", str(repo), "--workspace", "ws-open", "--route", "route:proposal-triage", "--format", "json"]) == 0
    captured = capsys.readouterr()
    assert '"handoff_id": "handoff:proposal-triage"' in captured.out

    assert operator_cli_main(["open-navigation-target", "--repo-root", str(repo), "--workspace", str(workspace_root.relative_to(repo)), "--target", "review:queue", "--mode", "file", "--print"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip().endswith("projection/operator/review/queue.md")

    calls = []

    def fake_execute(command):
        calls.append(command)
        return 0

    monkeypatch.setattr("packages.noema_operator.cli.execute_open_command", fake_execute)
    assert operator_cli_main(["open-navigation-target", "--repo-root", str(repo), "--workspace", "ws-open", "--target", "review:queue", "--mode", "file", "--execute"]) == 0
    assert len(calls) == 1
    assert calls[0].command[0] in {"open", "xdg-open"}
