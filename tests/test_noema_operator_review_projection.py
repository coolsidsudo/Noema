from __future__ import annotations

from pathlib import Path

from packages.noema_maintainer.scan import scan_repository
from packages.noema_operator.projections import build_operator_projections


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_repo(repo: Path) -> Path:
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-review"
    workspace_root.mkdir(parents=True)
    (workspace_root / "projection" / "operator" / "review" / "packets").mkdir(parents=True)
    (workspace_root / "projection" / "operator" / "review" / "packets" / "stale-packet.md").write_text(
        "# stale\n", encoding="utf-8"
    )
    (workspace_root / ".obsidian").mkdir()

    _write_object(
        repo / "raw" / "raw-1.md",
        "\n".join([
            "id: raw-1",
            "class: raw",
            "workspace: ws-review",
            "status: ingested",
            "title: Raw Evidence",
        ]),
    )
    _write_object(
        repo / "structured" / "target-1.md",
        "\n".join([
            "id: target-1",
            "class: structured",
            "workspace: ws-review",
            "status: active",
            "title: Target One",
        ]),
    )
    _write_object(
        repo / "structured" / "target-apply.md",
        "\n".join([
            "id: target-apply",
            "class: structured",
            "workspace: ws-review",
            "status: active",
            "title: Target Apply",
        ]),
    )
    _write_object(
        repo / "structured" / "target-no-apply.md",
        "\n".join([
            "id: target-no-apply",
            "class: structured",
            "workspace: ws-review",
            "status: active",
            "title: Target No Apply",
        ]),
    )
    _write_object(
        repo / "proposals" / "ready.md",
        "\n".join([
            "id: proposal-ready",
            "class: proposals",
            "workspace: ws-review",
            "status: under_review",
            "title: Ready Proposal",
            "created_by: tester",
            "created_at: 2026-04-01T00:00:00Z",
            "target_ids:",
            "  - target-1",
            "evidence_ids:",
            "  - raw-1",
        ]),
    )
    _write_object(
        repo / "proposals" / "accepted-applied.md",
        "\n".join([
            "id: proposal-accepted-applied",
            "class: proposals",
            "workspace: ws-review",
            "status: accepted",
            "title: Accepted Applied",
            "created_by: tester",
            "created_at: 2026-04-02T00:00:00Z",
            "target_ids:",
            "  - target-apply",
            "evidence_ids:",
            "  - raw-1",
        ]),
    )
    _write_object(
        repo / "proposals" / "accepted-no-apply.md",
        "\n".join([
            "id: proposal-accepted-no-apply",
            "class: proposals",
            "workspace: ws-review",
            "status: accepted",
            "title: Accepted No Apply",
            "created_by: tester",
            "created_at: 2026-04-03T00:00:00Z",
            "target_ids:",
            "  - target-no-apply",
            "evidence_ids:",
            "  - raw-1",
        ]),
    )
    _write_object(
        repo / "proposals" / "blocked.md",
        "\n".join([
            "id: proposal-blocked",
            "class: proposals",
            "workspace: ws-review",
            "status: under_review",
            "title: Blocked Proposal",
            "created_by: tester",
            "created_at: 2026-04-04T00:00:00Z",
            "target_ids:",
            "  - missing-target",
            "evidence_ids:",
            "  - missing-evidence",
        ]),
    )
    _write_object(
        repo / "logs" / "ready-log.md",
        "\n".join([
            "id: log-ready",
            "class: logs",
            "workspace: ws-review",
            "status: recorded",
            "title: Ready Log",
            "created_at: 2026-04-05T00:00:00Z",
            "records_event_for:",
            "  - proposal-ready",
        ]),
    )
    _write_object(
        repo / "logs" / "apply-log.md",
        "\n".join([
            "id: log-apply",
            "class: logs",
            "workspace: ws-review",
            "status: recorded",
            "title: Apply Log",
            "created_at: 2026-04-06T00:00:00Z",
            "event_type: apply_reconciliation",
            "records_event_for:",
            "  - proposal-accepted-applied",
            "  - target-apply",
        ]),
    )
    _write_object(
        repo / "logs" / "recovery-log.md",
        "\n".join([
            "id: log-recovery",
            "class: logs",
            "workspace: ws-review",
            "status: recorded",
            "title: Recovery Log",
            "created_at: 2026-04-07T00:00:00Z",
            "event_type: apply_step_failed",
            "records_event_for:",
            "  - proposal-accepted-applied",
        ]),
    )
    return workspace_root


def test_build_projections_generates_review_cockpit_and_packets(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = _seed_repo(repo)

    result = build_operator_projections(repo_root=repo, workspace="ws-review")
    first_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in result.output_paths}
    second = build_operator_projections(repo_root=repo, workspace=str(workspace_root.relative_to(repo)))
    second_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in second.output_paths}

    assert first_contents == second_contents
    assert "projection/operator/review/packets/stale-packet.md" not in {
        path.relative_to(workspace_root).as_posix() for path in result.output_paths
    }
    assert not (workspace_root / "projection" / "operator" / "review" / "packets" / "stale-packet.md").exists()

    expected_review_paths = {
        "projection/operator/review/index.md",
        "projection/operator/review/queue.md",
        "projection/operator/review/attention.md",
        "projection/operator/review/readiness.md",
        "projection/operator/review/recovery.md",
        "projection/operator/review/packets/proposal-blocked.md",
        "projection/operator/review/packets/proposal-accepted-no-apply.md",
        "projection/operator/review/packets/proposal-accepted-applied.md",
        "projection/operator/review/packets/proposal-ready.md",
    }
    assert expected_review_paths.issubset(set(first_contents))

    operator_index = first_contents["projection/operator/index.md"]
    assert "- [Review Cockpit](./review/index.md)" in operator_index
    assert "# Objects" in first_contents["projection/operator/objects.md"]
    assert "# Proposal Queue" in first_contents["projection/operator/proposals.md"]
    assert "# Recent Activity" in first_contents["projection/operator/recent.md"]

    index = first_contents["projection/operator/review/index.md"]
    assert "# Operator Review Cockpit" in index
    assert "## Review Summary" in index
    assert "## Readiness Counts" in index
    assert "## Attention Needed" in index
    assert "## Review Links" in index
    assert "- Proposal packets: `4`" in index
    assert "- Missing target references: `1`" in index
    assert "- [Review Queue](./queue.md)" in index

    queue = first_contents["projection/operator/review/queue.md"]
    assert "| proposal_id | status | readiness | attention | targets | missing_targets | missing_evidence | related_logs | packet |" in queue
    assert "[proposal-blocked](packets/proposal-blocked.md)" in queue
    assert queue.index("proposal-blocked") < queue.index("proposal-accepted-no-apply")

    attention = first_contents["projection/operator/review/attention.md"]
    assert "# Attention Needed" in attention
    assert "## Blocked Packets" in attention
    assert "## Missing Targets" in attention
    assert "missing-target" in attention
    assert "## Missing Evidence" in attention
    assert "missing-evidence" in attention
    assert "## Recovery Attention" in attention
    assert "log-recovery" in attention

    readiness = first_contents["projection/operator/review/readiness.md"]
    assert "# Review Readiness" in readiness
    assert "Readiness classifications are visibility evidence" in readiness
    assert "## Classification Rules" in readiness
    assert "## Packets by Classification" in readiness
    assert "### ready_for_human_review" in readiness
    assert "proposal-ready" in readiness

    recovery = first_contents["projection/operator/review/recovery.md"]
    assert "# Apply and Recovery Visibility" in recovery
    assert "## Accepted Proposals" in recovery
    assert "## Apply Evidence Present" in recovery
    assert "proposal-accepted-applied" in recovery
    assert "## Missing Apply Evidence" in recovery
    assert "proposal-accepted-no-apply" in recovery
    assert "## Recovery Signals" in recovery
    assert "This page summarizes metadata-visible apply and recovery signals only. It does not run apply or recovery." in recovery

    packet = first_contents["projection/operator/review/packets/proposal-accepted-applied.md"]
    for heading in (
        "# Review Packet: proposal-accepted-applied",
        "## Proposal",
        "## Readiness",
        "## Attention Flags",
        "## Target Objects",
        "## Evidence / Provenance",
        "## Related Logs",
        "## Apply / Recovery Evidence",
        "## Operator Next Steps",
        "## Navigation",
    ):
        assert heading in packet
    assert "references_proposal" in packet
    assert "references_target" in packet
    assert "apply_evidence" in packet
    assert "recovery_evidence" in packet
    assert "../queue.md" in packet
    assert str(tmp_path) not in "\n".join(first_contents.values())

    scanned_records = scan_repository(repo)
    scanned_ids = {record.metadata.get("id") for record in scanned_records}
    assert "proposal-ready" in scanned_ids
    assert "stale-packet" not in scanned_ids
    assert all("projection/operator/review" not in record.path.as_posix() for record in scanned_records)


def test_empty_workspace_generates_stable_empty_review_pages(tmp_path: Path) -> None:
    repo = tmp_path
    workspace_root = repo / "examples" / "workspaces" / "sample-research-workspace" / "workspaces" / "ws-empty"
    workspace_root.mkdir(parents=True)

    result = build_operator_projections(repo_root=repo, workspace=str(workspace_root))
    first_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in result.output_paths}
    second = build_operator_projections(repo_root=repo, workspace="ws-empty")
    second_contents = {path.relative_to(workspace_root).as_posix(): path.read_text(encoding="utf-8") for path in second.output_paths}

    assert first_contents == second_contents
    for rel_path in (
        "projection/operator/review/index.md",
        "projection/operator/review/queue.md",
        "projection/operator/review/attention.md",
        "projection/operator/review/readiness.md",
        "projection/operator/review/recovery.md",
    ):
        assert rel_path in first_contents
    assert "_No review packets found._" in first_contents["projection/operator/review/queue.md"]
    assert "_No packets currently need attention._" in first_contents["projection/operator/review/attention.md"]
    assert "_No recovery signals found._" in first_contents["projection/operator/review/recovery.md"]
    assert (workspace_root / "projection" / "operator" / "review" / "packets").is_dir()
    assert list((workspace_root / "projection" / "operator" / "review" / "packets").glob("*.md")) == []
