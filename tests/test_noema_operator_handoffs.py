from __future__ import annotations

import json
from pathlib import Path

from packages.noema_operator.handoffs import build_operator_handoffs
from packages.noema_operator.navigation import build_navigation_bundle
from packages.noema_operator.navigation_projection import render_navigation_workbench
from packages.noema_operator.projections import build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_handoff_repo(repo: Path) -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-handoff"
    workspace_root.mkdir(parents=True)
    _write_object(repo / "raw" / "raw-1.md", "\n".join([
        "id: raw-1",
        "class: raw",
        "workspace: ws-handoff",
        "status: ingested",
    ]))
    _write_object(repo / "structured" / "target-ready.md", "\n".join([
        "id: target-ready",
        "class: structured",
        "workspace: ws-handoff",
        "status: active",
    ]))
    _write_object(repo / "structured" / "target-apply.md", "\n".join([
        "id: target-apply",
        "class: structured",
        "workspace: ws-handoff",
        "status: active",
    ]))
    _write_object(repo / "proposals" / "ready.md", "\n".join([
        "id: proposal-ready",
        "class: proposals",
        "workspace: ws-handoff",
        "status: under_review",
        "created_at: 2026-04-01T00:00:00Z",
        "target_ids:",
        "  - target-ready",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "proposals" / "blocked.md", "\n".join([
        "id: proposal-blocked",
        "class: proposals",
        "workspace: ws-handoff",
        "status: under_review",
        "created_at: 2026-04-02T00:00:00Z",
        "target_ids:",
        "  - missing-target",
        "evidence_ids:",
        "  - missing-evidence",
    ]))
    _write_object(repo / "proposals" / "accepted-applied.md", "\n".join([
        "id: proposal-accepted-applied",
        "class: proposals",
        "workspace: ws-handoff",
        "status: accepted",
        "created_at: 2026-04-03T00:00:00Z",
        "target_ids:",
        "  - target-apply",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "proposals" / "accepted-no-apply.md", "\n".join([
        "id: proposal-accepted-no-apply",
        "class: proposals",
        "workspace: ws-handoff",
        "status: accepted",
        "created_at: 2026-04-04T00:00:00Z",
        "target_ids:",
        "  - target-ready",
        "evidence_ids:",
        "  - raw-1",
    ]))
    _write_object(repo / "logs" / "apply-log.md", "\n".join([
        "id: log-apply",
        "class: logs",
        "workspace: ws-handoff",
        "status: recorded",
        "event_type: apply_reconciliation",
        "records_event_for:",
        "  - proposal-accepted-applied",
        "  - target-apply",
    ]))
    _write_object(repo / "logs" / "recovery-log.md", "\n".join([
        "id: log-recovery",
        "class: logs",
        "workspace: ws-handoff",
        "status: recorded",
        "event_type: apply_step_failed",
        "records_event_for:",
        "  - proposal-accepted-applied",
    ]))
    return workspace_root


def test_operator_handoffs_are_deterministic_and_packet_aware(tmp_path: Path) -> None:
    repo = tmp_path
    _seed_handoff_repo(repo)
    build_operator_projections(repo_root=repo, workspace="ws-handoff")

    bundle = build_navigation_bundle(repo_root=repo, workspace="ws-handoff")
    first = build_operator_handoffs(bundle)
    second = build_operator_handoffs(bundle)
    assert [handoff.handoff_id for handoff in first.handoffs] == [handoff.handoff_id for handoff in second.handoffs]

    by_id = {handoff.handoff_id: handoff for handoff in first.handoffs}
    assert {"handoff:workspace-overview", "handoff:proposal-triage", "handoff:blocked-review", "handoff:ready-review", "handoff:accepted-apply-audit", "handoff:recovery-audit"}.issubset(by_id)
    assert "handoff:packet-review:proposal-ready" in by_id

    blocked = by_id["handoff:blocked-review"]
    assert blocked.primary_target_id == "review:attention"
    assert blocked.route_id == "route:blocked-review"
    assert any("missing target references" in item for item in blocked.blockers)
    assert any("missing evidence references" in item for item in blocked.blockers)
    assert "proposal-blocked" in blocked.related_packet_ids

    audit = by_id["handoff:accepted-apply-audit"]
    assert any("accepted proposal has no visible apply evidence" in item for item in audit.warnings)
    assert any("recovery/failure signal" in item for item in audit.warnings)

    recovery = by_id["handoff:recovery-audit"]
    assert recovery.related_packet_ids == ("proposal-accepted-applied",)
    assert any("recovery" in step.lower() for step in recovery.next_steps)

    packet = by_id["handoff:packet-review:proposal-ready"]
    assert packet.primary_target_id == "review:packet:proposal-ready"
    assert "source:proposal-ready" in packet.related_target_ids
    assert "raw-1" in packet.related_source_record_ids
    assert json.dumps([handoff.__dict__ for handoff in first.handoffs], sort_keys=True, default=str) == json.dumps([handoff.__dict__ for handoff in second.handoffs], sort_keys=True, default=str)


def test_navigation_workbench_projection_and_manifest(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = _seed_handoff_repo(repo)
    result = build_operator_projections(repo_root=repo, workspace="ws-handoff")
    first_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in result.output_paths}
    second = build_operator_projections(repo_root=repo, workspace=str(workspace_root.relative_to(repo)))
    second_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in second.output_paths}

    assert first_contents == second_contents
    for rel_path in (
        "projection/operator/navigation/index.md",
        "projection/operator/navigation/targets.md",
        "projection/operator/navigation/routes.md",
        "projection/operator/navigation/handoffs.md",
        "projection/operator/navigation/open-commands.md",
        "projection/operator/navigation/manifest.json",
    ):
        assert rel_path in first_contents
    assert "# Operator Navigation Workbench" in first_contents["projection/operator/navigation/index.md"]
    assert "## Navigation Summary" in first_contents["projection/operator/navigation/index.md"]
    assert "# Navigation Targets" in first_contents["projection/operator/navigation/targets.md"]
    assert "source:raw-1" in first_contents["projection/operator/navigation/targets.md"]
    assert "# Operator Routes" in first_contents["projection/operator/navigation/routes.md"]
    assert "route:proposal-triage" in first_contents["projection/operator/navigation/routes.md"]
    assert "_No source inspection routes generated in this tranche._" in first_contents["projection/operator/navigation/routes.md"]
    assert "# Operator Handoffs" in first_contents["projection/operator/navigation/handoffs.md"]
    assert "handoff:accepted-apply-audit" in first_contents["projection/operator/navigation/handoffs.md"]
    assert "_No source handoffs generated in this tranche._" in first_contents["projection/operator/navigation/handoffs.md"]
    assert "# Local Open Helpers" in first_contents["projection/operator/navigation/open-commands.md"]
    assert "--execute" in first_contents["projection/operator/navigation/open-commands.md"]
    assert str(tmp_path) not in "\n".join(first_contents.values())

    manifest = json.loads(first_contents["projection/operator/navigation/manifest.json"])
    assert manifest["schema_version"] == "operator-navigation-workbench-v1"
    assert manifest["authority"] == "derived_non_authoritative"
    assert manifest["workspace_id"] == "ws-handoff"
    assert {target["target_id"] for target in manifest["targets"]} >= {"navigation:index", "review:queue", "source:raw-1"}
    source = [target for target in manifest["targets"] if target["target_id"] == "source:raw-1"][0]
    assert source["repo_relative_path"] == "raw/raw-1.md"
    assert "workspace_relative_path" not in source
    assert {route["route_id"] for route in manifest["routes"]} >= {"route:workspace-overview", "route:proposal-triage"}
    assert {handoff["handoff_id"] for handoff in manifest["handoffs"]} >= {"handoff:workspace-overview", "handoff:proposal-triage"}
    assert "diagnostics" in manifest
    assert str(tmp_path) not in json.dumps(manifest, sort_keys=True)
