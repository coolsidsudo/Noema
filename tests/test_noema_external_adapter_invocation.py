from __future__ import annotations

import json
from pathlib import Path

from packages.noema_external_adapter import invoke_request, invoke_tool
from packages.noema_operator.projections import build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_repo(repo: Path, *, workspace: str = "ws-ext") -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / workspace
    workspace_root.mkdir(parents=True)
    _write_object(repo / "raw" / "raw-1.md", "\n".join([
        "id: raw-1",
        "class: raw",
        f"workspace: {workspace}",
        "status: ingested",
        "title: Raw Evidence",
    ]), body="raw body")
    _write_object(repo / "structured" / "target-ready.md", "\n".join([
        "id: target-ready",
        "class: structured",
        f"workspace: {workspace}",
        "status: active",
        "title: Target Ready",
        "supports:",
        "  - raw-1",
    ]), body="structured body")
    _write_object(repo / "structured" / "target-apply.md", "\n".join([
        "id: target-apply",
        "class: structured",
        f"workspace: {workspace}",
        "status: active",
        "title: Target Apply",
    ]))
    _write_object(repo / "proposals" / "ready.md", "\n".join([
        "id: proposal-ready",
        "class: proposals",
        f"workspace: {workspace}",
        "status: under_review",
        "title: Ready Proposal",
        "summary: Existing proposal summary",
        "created_by: maintainer",
        "created_at: 2026-04-01T00:00:00Z",
        "target_ids:",
        "  - target-ready",
        "evidence_ids:",
        "  - raw-1",
        "results_in:",
        "  - target-apply",
    ]), body="proposal body")
    _write_object(repo / "proposals" / "blocked.md", "\n".join([
        "id: proposal-blocked",
        "class: proposals",
        f"workspace: {workspace}",
        "status: under_review",
        "title: Blocked Proposal",
        "summary: Blocked summary",
        "created_at: 2026-04-02T00:00:00Z",
        "target_ids:",
        "  - missing-target",
        "evidence_ids:",
        "  - missing-evidence",
    ]))
    _write_object(repo / "logs" / "log-ready.md", "\n".join([
        "id: log-ready",
        "class: logs",
        f"workspace: {workspace}",
        "status: recorded",
        "event_type: apply_reconciliation",
        "records_event_for:",
        "  - proposal-ready",
        "  - target-ready",
    ]))
    return workspace_root


def _args(repo: Path, workspace: str = "ws-ext") -> dict[str, object]:
    return {"repo_root": str(repo), "workspace": workspace}


def test_validation_errors_are_deterministic() -> None:
    missing = invoke_tool("noema.object.get", {"repo_root": ".", "workspace": "ws"})
    assert missing["ok"] is False
    assert missing["error"]["code"] == "missing_required_argument"
    assert "Traceback" not in json.dumps(missing)

    wrong_type = invoke_tool("noema.objects.list", {"repo_root": ".", "workspace": "ws", "limit": "10"})
    assert wrong_type["error"]["code"] == "invalid_argument_type"

    invalid_enum = invoke_tool("noema.operator.navigation.target.resolve", {"repo_root": ".", "workspace": "ws", "target_id": "review:queue", "format": "obsidian-uri"})
    assert invalid_enum["error"]["code"] == "invalid_argument_value"

    extra = invoke_tool("noema.object.get", {"repo_root": ".", "workspace": "ws", "object_id": "x", "extra": True})
    assert extra["error"]["code"] == "unexpected_argument"

    zero = invoke_tool("noema.traceability.links", {"repo_root": ".", "workspace": "ws", "object_id": "x", "limit": 0})
    assert zero["error"]["code"] == "invalid_argument_value"

    no_selector = invoke_tool("noema.operator.handoff.build", {"repo_root": ".", "workspace": "ws"})
    assert no_selector["error"]["code"] == "invalid_argument_combination"

    multi_selector = invoke_tool("noema.operator.handoff.build", {"repo_root": ".", "workspace": "ws", "target_id": "a", "route_id": "b"})
    assert multi_selector["error"]["code"] == "invalid_argument_combination"


def test_service_tool_invocations_unwrap_service_envelopes(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_repo(repo)

    listed = invoke_tool("noema.objects.list", {**_args(repo), "object_class": "structured", "include_content": False})
    assert listed["ok"] is True
    assert listed["meta"]["side_effect_class"] == "read_only"
    assert [item["id"] for item in listed["data"]["items"]] == ["target-apply", "target-ready"]
    assert "pagination" in listed["data"]
    assert "request_id" not in json.dumps(listed)
    assert "timestamp" not in json.dumps(listed)

    got = invoke_tool("noema.object.get", {**_args(repo), "object_id": "target-ready"})
    assert got["ok"] is True
    assert got["data"]["object"]["id"] == "target-ready"
    assert "content" not in got["data"]["object"]

    links = invoke_tool("noema.traceability.links", {**_args(repo), "object_id": "target-ready", "direction": "outbound"})
    assert links["ok"] is True
    assert links["data"]["seed_ids"] == ["target-ready"]
    assert any(link["to_id"] == "raw-1" for link in links["data"]["links"])

    status = invoke_tool("noema.proposal.status", {**_args(repo), "proposal_id": "proposal-ready"})
    assert status["ok"] is True
    assert status["data"]["id"] == "proposal-ready"
    assert status["data"]["result_links"] == ["target-apply"]


def test_service_backing_error_becomes_deterministic_adapter_error(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_repo(repo)

    result = invoke_tool("noema.object.get", {**_args(repo), "object_id": "missing"})

    assert result["ok"] is False
    assert result["error"]["code"] == "backing_operation_error"
    assert result["error"]["details"]["backing_operation"] == "get_object_by_id"
    assert result["error"]["details"]["backing_code"] == "OBJECT_NOT_FOUND"
    assert "request_id" not in json.dumps(result)
    assert "timestamp" not in json.dumps(result)


def test_proposal_submit_uses_service_core_only_and_is_deterministic_when_created_at_supplied(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_repo(repo)
    before_structured = (repo / "structured" / "target-ready.md").read_text(encoding="utf-8")

    result = invoke_tool("noema.proposal.submit", {
        **_args(repo),
        "proposal_id": "proposal-new",
        "title": "New Proposal",
        "summary": "Summarize this change.",
        "rationale": "Because reasons.",
        "intended_effect": "Improve the structured record after review.",
        "target_ids": ["target-ready"],
        "proposed_by": "agent-x",
        "evidence_ids": ["raw-1"],
        "status": "draft",
        "created_at": "2026-05-01T00:00:00Z",
    })

    assert result["ok"] is True
    assert result["meta"]["side_effect_class"] == "proposal_write"
    assert result["data"]["id"] == "proposal-new"
    assert result["data"]["created_at"] == "2026-05-01T00:00:00Z"
    proposal_file = repo / "proposals" / "ws-ext" / "proposal-new.md"
    text = proposal_file.read_text(encoding="utf-8")
    assert "created_by: agent-x" in text
    assert "intended_effect: Improve the structured record after review." in text
    assert "supporting_raw_ids:\n  - raw-1" in text
    assert (repo / "structured" / "target-ready.md").read_text(encoding="utf-8") == before_structured
    assert "request_id" not in json.dumps(result)
    assert "timestamp" not in json.dumps(result)


def test_operator_tool_invocations(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = _seed_repo(repo)

    built = invoke_tool("noema.operator.projections.build", _args(repo))
    assert built["ok"] is True
    assert built["meta"]["side_effect_class"] == "generated_projection_write"
    assert built["data"]["projection_root"].endswith("projection/operator")
    assert all(not Path(path).is_absolute() for path in built["data"]["output_paths"])

    targets = invoke_tool("noema.operator.navigation.targets.list", _args(repo))
    assert targets["ok"] is True
    target_ids = {target["target_id"] for target in targets["data"]["targets"]}
    assert {"operator:index", "review:queue", "navigation:manifest", "source:target-ready"}.issubset(target_ids)
    assert str(repo) not in json.dumps(targets, sort_keys=True)

    target_filter = invoke_tool("noema.operator.navigation.targets.list", {**_args(repo), "kind": "review_page"})
    assert {target["target_kind"] for target in target_filter["data"]["targets"]} == {"review_page"}

    resolved_rel = invoke_tool("noema.operator.navigation.target.resolve", {**_args(repo), "target_id": "review:queue", "format": "repo-relative-path"})
    assert resolved_rel["ok"] is True
    assert resolved_rel["data"]["value"].endswith("projection/operator/review/queue.md")

    resolved_path = invoke_tool("noema.operator.navigation.target.resolve", {**_args(repo), "target_id": "review:queue", "format": "path"})
    assert Path(resolved_path["data"]["value"]).is_absolute()
    assert (workspace_root / "projection" / "operator" / "review" / "queue.md").as_posix() == Path(resolved_path["data"]["value"]).as_posix()

    routes = invoke_tool("noema.operator.routes.list", _args(repo))
    assert routes["ok"] is True
    assert {route["route_id"] for route in routes["data"]["routes"]} >= {"route:workspace-overview", "route:proposal-triage"}
    assert all("target_count" in route for route in routes["data"]["routes"])

    route = invoke_tool("noema.operator.route.show", {**_args(repo), "route_id": "route:proposal-triage"})
    assert route["ok"] is True
    assert route["data"]["route"]["entry_target_id"] == "review:queue"
    assert route["data"]["route"]["checklist_items"]

    handoff_by_route = invoke_tool("noema.operator.handoff.build", {**_args(repo), "route_id": "route:proposal-triage"})
    assert handoff_by_route["ok"] is True
    handoff_id = handoff_by_route["data"]["handoff"]["handoff_id"]
    assert handoff_id == "handoff:proposal-triage"

    handoff_by_target = invoke_tool("noema.operator.handoff.build", {**_args(repo), "target_id": "review:queue"})
    assert handoff_by_target["ok"] is True
    assert handoff_by_target["data"]["handoff"]["handoff_id"] == "handoff:proposal-triage"

    handoff_by_id = invoke_tool("noema.operator.handoff.build", {**_args(repo), "handoff_id": handoff_id})
    assert handoff_by_id == handoff_by_route


def test_invoke_request_shape(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_repo(repo)

    result = invoke_request({"tool": "noema.objects.list", "arguments": _args(repo)})

    assert result["ok"] is True
    assert result["tool"] == "noema.objects.list"
