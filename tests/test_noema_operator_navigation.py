from __future__ import annotations

import json
from pathlib import Path

import pytest

from packages.noema_operator.navigation import build_navigation_bundle, build_navigation_registry
from packages.noema_operator.projections import build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_navigation_repo(repo: Path, *, duplicate: bool = False) -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-nav"
    workspace_root.mkdir(parents=True)
    (workspace_root / ".obsidian").mkdir()
    _write_object(workspace_root / "projection" / "operator" / "navigation" / "generated-record.md", "\n".join([
        "id: generated-navigation-record",
        "class: structured",
        "workspace: ws-nav",
        "status: active",
    ]))
    _write_object(repo / "raw" / "raw-1.md", "\n".join([
        "id: raw-1",
        "class: raw",
        "workspace: ws-nav",
        "status: ingested",
        "title: Raw Evidence",
    ]))
    _write_object(repo / "structured" / "target-ready.md", "\n".join([
        "id: target-ready",
        "class: structured",
        "workspace: ws-nav",
        "status: active",
        "title: Target Ready",
    ]))
    _write_object(repo / "structured" / "target-apply.md", "\n".join([
        "id: target-apply",
        "class: structured",
        "workspace: ws-nav",
        "status: active",
        "title: Target Apply",
    ]))
    _write_object(repo / "structured" / "target-no-apply.md", "\n".join([
        "id: target-no-apply",
        "class: structured",
        "workspace: ws-nav",
        "status: active",
        "title: Target No Apply",
    ]))
    _write_object(repo / "structured" / "other.md", "\n".join([
        "id: target-other",
        "class: structured",
        "workspace: ws-other",
        "status: active",
    ]))
    _write_object(repo / "proposals" / "ready.md", "\n".join([
        "id: proposal-ready-record",
        "proposal_id: proposal-ready",
        "class: proposals",
        "workspace: ws-nav",
        "status: under_review",
        "title: Ready Proposal",
        "created_at: 2026-04-01T00:00:00Z",
        "target_ids:",
        "  - target-ready",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "proposals" / "blocked.md", "\n".join([
        "id: proposal-blocked",
        "class: proposals",
        "workspace: ws-nav",
        "status: under_review",
        "title: Blocked Proposal",
        "created_at: 2026-04-02T00:00:00Z",
        "target_ids:",
        "  - missing-target",
        "evidence_ids:",
        "  - missing-evidence",
    ]))
    _write_object(repo / "proposals" / "accepted-applied.md", "\n".join([
        "id: proposal-accepted-applied",
        "class: proposals",
        "workspace: ws-nav",
        "status: accepted",
        "title: Accepted Applied",
        "created_at: 2026-04-03T00:00:00Z",
        "target_ids:",
        "  - target-apply",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "proposals" / "accepted-no-apply.md", "\n".join([
        "id: proposal-accepted-no-apply",
        "class: proposals",
        "workspace: ws-nav",
        "status: accepted",
        "title: Accepted Missing Apply",
        "created_at: 2026-04-04T00:00:00Z",
        "target_ids:",
        "  - target-no-apply",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "proposals" / "unknown.md", "\n".join([
        "id: proposal-unknown",
        "class: proposals",
        "workspace: ws-nav",
        "status: surprising",
        "title: Unknown Status",
        "created_at: 2026-04-05T00:00:00Z",
    ]))
    _write_object(repo / "logs" / "ready-log.md", "\n".join([
        "id: log-ready",
        "class: logs",
        "workspace: ws-nav",
        "status: recorded",
        "created_at: 2026-04-06T00:00:00Z",
        "records_event_for:",
        "  - proposal-ready",
        "  - target-ready",
    ]))
    _write_object(repo / "logs" / "apply-log.md", "\n".join([
        "id: log-apply",
        "class: logs",
        "workspace: ws-nav",
        "status: recorded",
        "created_at: 2026-04-07T00:00:00Z",
        "event_type: apply_reconciliation",
        "records_event_for:",
        "  - proposal-accepted-applied",
        "  - target-apply",
    ]))
    _write_object(repo / "logs" / "recovery-log.md", "\n".join([
        "id: log-recovery",
        "class: logs",
        "workspace: ws-nav",
        "status: recorded",
        "created_at: 2026-04-08T00:00:00Z",
        "event_type: apply_step_failed",
        "records_event_for:",
        "  - proposal-accepted-applied",
    ]))
    if duplicate:
        _write_object(repo / "structured" / "duplicate-a.md", "\n".join([
            "id: duplicate-target",
            "class: structured",
            "workspace: ws-nav",
            "status: active",
        ]))
        _write_object(repo / "raw" / "duplicate-b.md", "\n".join([
            "id: duplicate-target",
            "class: raw",
            "workspace: ws-nav",
            "status: ingested",
        ]))
    return workspace_root


def test_navigation_registry_builds_stable_targets_and_resolutions(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = _seed_navigation_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-nav")

    first = build_navigation_registry(repo_root=repo, workspace="ws-nav")
    second = build_navigation_registry(repo_root=repo, workspace=str(workspace_root.relative_to(repo)))

    assert [target.target_id for target in first.targets] == [target.target_id for target in second.targets]
    target_ids = {target.target_id for target in first.targets}
    assert {"operator:index", "operator:objects", "operator:proposals", "operator:recent"}.issubset(target_ids)
    assert {"review:index", "review:queue", "review:attention", "review:readiness", "review:recovery"}.issubset(target_ids)
    assert {"navigation:index", "navigation:targets", "navigation:routes", "navigation:handoffs", "navigation:open-commands", "navigation:manifest"}.issubset(target_ids)
    assert "review:packet:proposal-ready" in target_ids
    assert "source:raw-1" in target_ids
    assert "source:proposal-ready-record" in target_ids
    assert "source:target-other" not in target_ids
    assert "source:generated-navigation-record" not in target_ids

    source = first.lookup("source:raw-1")
    assert source is not None
    assert source.repo_relative_path == "raw/raw-1.md"
    assert source.workspace_relative_path == ""
    assert first.resolve("review:queue").repo_relative_path.endswith("projection/operator/review/queue.md")
    assert first.suggestions("review:qu") == ("review:queue",)
    with pytest.raises(ValueError) as exc:
        first.resolve("review:missing")
    assert "unknown target: review:missing" in str(exc.value)
    assert str(tmp_path) not in json.dumps([target.__dict__ for target in first.targets], sort_keys=True)


def test_navigation_registry_collision_diagnostics_are_deterministic(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_navigation_repo(repo, duplicate=True)

    registry = build_navigation_registry(repo_root=repo, workspace="ws-nav")

    assert "source:duplicate-target" in registry.ambiguous_target_ids
    assert registry.lookup("source:duplicate-target") is None
    diagnostic = [item for item in registry.diagnostics if item.code == "ambiguous_target_id"][0]
    assert diagnostic.target_id == "source:duplicate-target"
    assert diagnostic.references == tuple(sorted(diagnostic.references))


def test_operator_routes_reflect_review_packet_state(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_navigation_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-nav")

    bundle = build_navigation_bundle(repo_root=repo, workspace="ws-nav")
    routes = {route.route_id: route for route in bundle.routes.routes}

    assert {"route:workspace-overview", "route:proposal-triage", "route:blocked-review", "route:ready-review", "route:accepted-apply-audit", "route:recovery-audit"}.issubset(routes)
    assert "route:packet-review:proposal-ready" in routes
    assert routes["route:workspace-overview"].ordered_target_ids == ("operator:index", "operator:objects", "operator:proposals", "operator:recent", "review:index", "navigation:index")
    assert "proposal-blocked" in routes["route:blocked-review"].related_packet_ids
    assert "proposal-unknown" in routes["route:blocked-review"].related_packet_ids
    assert "proposal-ready" in routes["route:ready-review"].related_packet_ids
    assert set(routes["route:accepted-apply-audit"].related_packet_ids) == {"proposal-accepted-applied", "proposal-accepted-no-apply"}
    assert routes["route:recovery-audit"].related_packet_ids == ("proposal-accepted-applied",)
    packet_route = routes["route:packet-review:proposal-ready"]
    assert packet_route.entry_target_id == "review:packet:proposal-ready"
    assert "source:proposal-ready-record" in packet_route.ordered_target_ids
    assert "Review proposal rationale, target objects, evidence, and related logs." in packet_route.checklist_items
    assert all(bundle.registry.lookup(target_id) is not None for route in bundle.routes.routes for target_id in route.ordered_target_ids)
