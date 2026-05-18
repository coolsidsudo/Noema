from __future__ import annotations

import json
from pathlib import Path

from packages.noema_external_adapter.cli import main as adapter_cli_main


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_cli_repo(repo: Path) -> None:
    workspace = "ws-cli"
    (repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / workspace).mkdir(parents=True)
    _write_object(repo / "raw" / "raw-1.md", "\n".join([
        "id: raw-1",
        "class: raw",
        f"workspace: {workspace}",
        "status: ingested",
    ]))
    _write_object(repo / "structured" / "target-1.md", "\n".join([
        "id: target-1",
        "class: structured",
        f"workspace: {workspace}",
        "status: active",
        "title: Target One",
    ]))


def test_list_tools_table_and_json_are_deterministic(capsys) -> None:
    assert adapter_cli_main(["list-tools"]) == 0
    first = capsys.readouterr().out
    assert first.splitlines()[0] == "name\tcategory\tside_effect_class\tdescription"
    assert "noema.objects.list" in first
    assert "noema.proposal.submit" in first

    assert adapter_cli_main(["list-tools", "--format", "json"]) == 0
    second = capsys.readouterr().out
    parsed = json.loads(second)
    assert [tool["name"] for tool in parsed] == sorted(tool["name"] for tool in parsed)

    assert adapter_cli_main(["list-tools", "--category", "service", "--format", "json"]) == 0
    filtered = json.loads(capsys.readouterr().out)
    assert {tool["category"] for tool in filtered} == {"service"}
    assert len(filtered) == 5


def test_describe_tool_and_unknown(capsys) -> None:
    assert adapter_cli_main(["describe-tool", "--tool", "noema.object.get"]) == 0
    out = capsys.readouterr().out
    assert "Tool: noema.object.get" in out
    assert "object_id" in out

    assert adapter_cli_main(["describe-tool", "--tool", "noema.object.get", "--format", "json"]) == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["name"] == "noema.object.get"

    assert adapter_cli_main(["describe-tool", "--tool", "noema.missing"]) != 0
    captured = capsys.readouterr()
    assert "Unknown external adapter tool." in captured.err


def test_emit_manifest_is_deterministic(capsys) -> None:
    assert adapter_cli_main(["emit-manifest"]) == 0
    first = capsys.readouterr().out
    assert adapter_cli_main(["emit-manifest", "--format", "json"]) == 0
    second = capsys.readouterr().out

    assert first == second
    manifest = json.loads(first)
    assert manifest["schema_version"] == "noema-external-tool-manifest-v1"
    assert manifest["generated_policy"]["no_absolute_local_paths"] is True


def test_invoke_tool_cli_success_and_failure(capsys, tmp_path: Path) -> None:
    repo = tmp_path
    _seed_cli_repo(repo)
    args_json = json.dumps({"repo_root": str(repo), "workspace": "ws-cli"})

    assert adapter_cli_main(["invoke-tool", "--tool", "noema.objects.list", "--args-json", args_json]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["ok"] is True
    assert first["tool"] == "noema.objects.list"
    assert "request_id" not in json.dumps(first)
    assert "timestamp" not in json.dumps(first)

    request_json = json.dumps({"tool": "noema.object.get", "arguments": {"repo_root": str(repo), "workspace": "ws-cli", "object_id": "target-1"}})
    assert adapter_cli_main(["invoke-tool", "--request-json", request_json]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["ok"] is True
    assert second["data"]["object"]["id"] == "target-1"

    assert adapter_cli_main(["invoke-tool", "--tool", "noema.object.get", "--args-json", args_json]) != 0
    failure = json.loads(capsys.readouterr().out)
    assert failure["ok"] is False
    assert failure["error"]["code"] == "missing_required_argument"

    assert adapter_cli_main(["invoke-tool", "--tool", "noema.objects.list", "--args-json", "{"]) != 0
    malformed = json.loads(capsys.readouterr().out)
    assert malformed["ok"] is False
    assert malformed["error"]["code"] == "invalid_argument_value"

    assert adapter_cli_main(["invoke-tool", "--request-json", json.dumps({"tool": "noema.objects.list", "arguments": {"repo_root": str(repo), "workspace": "ws-cli", "extra": True}})]) != 0
    extra = json.loads(capsys.readouterr().out)
    assert extra["error"]["code"] == "unexpected_argument"


def test_cli_requires_no_http_server_or_obsidian(capsys, tmp_path: Path) -> None:
    repo = tmp_path
    _seed_cli_repo(repo)
    assert not (repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-cli" / ".obsidian").exists()

    assert adapter_cli_main(["invoke-tool", "--request-json", json.dumps({"tool": "noema.objects.list", "arguments": {"repo_root": str(repo), "workspace": "ws-cli"}})]) == 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["ok"] is True
