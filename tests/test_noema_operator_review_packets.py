from __future__ import annotations

from pathlib import Path

from packages.noema_operator.review_packets import build_review_packets


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _packet_by_id(packets):
    return {packet.proposal_id: packet for packet in packets}


def test_review_packets_resolve_workspace_targets_evidence_logs_apply_and_recovery(tmp_path: Path) -> None:
    repo = tmp_path
    _write_object(
        repo / "raw" / "raw-1.md",
        "\n".join([
            "id: raw-1",
            "class: raw",
            "workspace: ws-a",
            "status: ingested",
            "title: Raw Evidence",
        ]),
    )
    _write_object(
        repo / "structured" / "target-1.md",
        "\n".join([
            "id: target-1",
            "class: structured",
            "workspace: ws-a",
            "status: active",
            "title: Target One",
        ]),
    )
    _write_object(
        repo / "structured" / "target-apply.md",
        "\n".join([
            "id: target-apply",
            "class: structured",
            "workspace: ws-a",
            "status: active",
            "title: Target Apply",
        ]),
    )
    _write_object(
        repo / "structured" / "target-no-apply.md",
        "\n".join([
            "id: target-no-apply",
            "class: structured",
            "workspace: ws-a",
            "status: active",
            "title: Target No Apply",
        ]),
    )
    _write_object(
        repo / "structured" / "other-target.md",
        "\n".join([
            "id: target-1",
            "class: structured",
            "workspace: ws-b",
            "status: active",
            "title: Other Workspace Target",
        ]),
    )
    _write_object(
        repo / "proposals" / "ready.md",
        "\n".join([
            "id: internal-ready",
            "proposal_id: proposal-ready",
            "class: proposals",
            "workspace: ws-a",
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
            "workspace: ws-a",
            "status: accepted",
            "title: Accepted Applied",
            "created_by: tester",
            "created_at: 2026-04-02T00:00:00Z",
            "target_ids:",
            "  - target-apply",
            "supporting_raw_ids:",
            "  - raw-1",
        ]),
    )
    _write_object(
        repo / "proposals" / "accepted-missing-apply.md",
        "\n".join([
            "id: proposal-accepted-missing-apply",
            "class: proposals",
            "workspace: ws-a",
            "status: accepted",
            "title: Accepted Missing Apply",
            "created_by: tester",
            "created_at: 2026-04-03T00:00:00Z",
            "target_ids:",
            "  - target-no-apply",
            "supports:",
            "  - raw-1",
        ]),
    )
    _write_object(
        repo / "proposals" / "missing-refs.md",
        "\n".join([
            "id: proposal-missing-refs",
            "class: proposals",
            "workspace: ws-a",
            "status: under_review",
            "title: Missing Refs",
            "created_by: tester",
            "created_at: 2026-04-04T00:00:00Z",
            "affected_object_ids:",
            "  - missing-target",
            "sources:",
            "  - missing-source",
        ]),
    )
    _write_object(
        repo / "proposals" / "draft.md",
        "\n".join([
            "id: proposal-draft",
            "class: proposals",
            "workspace: ws-a",
            "status: draft",
            "title: Draft",
        ]),
    )
    _write_object(
        repo / "proposals" / "unknown.md",
        "\n".join([
            "class: proposals",
            "workspace: ws-a",
            "status: surprising",
            "title: Unknown Missing Id",
        ]),
    )
    _write_object(
        repo / "proposals" / "other.md",
        "\n".join([
            "id: proposal-other",
            "class: proposals",
            "workspace: ws-b",
            "status: under_review",
            "target_ids:",
            "  - target-1",
        ]),
    )

    _write_object(
        repo / "logs" / "proposal-log.md",
        "\n".join([
            "id: log-proposal",
            "class: logs",
            "workspace: ws-a",
            "status: recorded",
            "title: Proposal Log",
            "created_at: 2026-04-06T00:00:00Z",
            "records_event_for:",
            "  - proposal-ready",
        ]),
    )
    _write_object(
        repo / "logs" / "target-log.md",
        "\n".join([
            "id: log-target",
            "class: logs",
            "workspace: ws-a",
            "status: recorded",
            "title: Target Log",
            "created_at: 2026-04-07T00:00:00Z",
            "records_event_for:",
            "  - target-1",
        ]),
    )
    _write_object(
        repo / "logs" / "apply-log.md",
        "\n".join([
            "id: log-apply",
            "class: logs",
            "workspace: ws-a",
            "status: recorded",
            "title: Apply Log",
            "created_at: 2026-04-08T00:00:00Z",
            "event_type: apply_reconciliation",
            "proposal_id: proposal-accepted-applied",
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
            "workspace: ws-a",
            "status: recorded",
            "title: Recovery Log",
            "created_at: 2026-04-09T00:00:00Z",
            "event_type: apply_step_failed",
            "records_event_for:",
            "  - proposal-accepted-applied",
        ]),
    )
    _write_object(
        repo / "logs" / "unrelated-apply-log.md",
        "\n".join([
            "id: log-unrelated-apply",
            "class: logs",
            "workspace: ws-a",
            "status: recorded",
            "event_type: apply_completed",
            "records_event_for:",
            "  - unrelated-proposal",
        ]),
    )

    packets = build_review_packets(repo_root=repo, workspace="ws-a")
    by_id = _packet_by_id(packets)

    assert set(by_id) == {
        "proposal-ready",
        "proposal-accepted-applied",
        "proposal-accepted-missing-apply",
        "proposal-missing-refs",
        "proposal-draft",
        "missing-proposal-id-proposals-unknown",
    }
    ready = by_id["proposal-ready"]
    assert ready.resolved_target_records[0].record_id == "target-1"
    assert ready.resolved_evidence_records[0].record_id == "raw-1"
    assert ready.readiness_classifications == ("ready_for_human_review",)
    assert ready.primary_classification == "ready_for_human_review"
    assert {label for log in ready.related_log_records for label in log.relation_labels} == {
        "references_proposal",
        "references_target",
    }

    missing = by_id["proposal-missing-refs"]
    assert missing.missing_target_ids == ("missing-target",)
    assert missing.missing_evidence_ids == ("missing-source",)
    assert missing.primary_classification == "blocked_missing_targets"
    assert missing.readiness_classifications == ("blocked_missing_targets", "blocked_missing_evidence")
    assert missing.attention_flags == ("missing_target_reference", "missing_evidence_reference")
    assert "Resolve missing target object reference: missing-target." in missing.operator_next_steps

    accepted_applied = by_id["proposal-accepted-applied"]
    assert "apply_evidence_present" in accepted_applied.readiness_classifications
    assert "recovery_attention_needed" in accepted_applied.readiness_classifications
    assert [log.record.record_id for log in accepted_applied.apply_evidence_records] == ["log-recovery", "log-apply"]
    assert [log.record.record_id for log in accepted_applied.recovery_evidence_records] == ["log-recovery"]
    assert all(log.record.record_id != "log-unrelated-apply" for log in accepted_applied.apply_evidence_records)

    accepted_missing = by_id["proposal-accepted-missing-apply"]
    assert "accepted_without_apply_evidence" in accepted_missing.readiness_classifications
    assert "accepted_without_apply_evidence" in accepted_missing.attention_flags

    draft = by_id["proposal-draft"]
    assert draft.readiness_classifications == ("draft_not_ready",)

    unknown = by_id["missing-proposal-id-proposals-unknown"]
    assert "missing_proposal_id" in unknown.attention_flags
    assert "unknown_status" in unknown.attention_flags
    assert "unknown_status" in unknown.readiness_classifications


def test_review_packet_slug_collisions_are_deterministic(tmp_path: Path) -> None:
    repo = tmp_path
    for proposal_id in ("Proposal Alpha", "proposal_alpha", "proposal/alpha"):
        _write_object(
            repo / "proposals" / f"{proposal_id.replace('/', '-')}.md",
            "\n".join([
                f"id: {proposal_id}",
                "class: proposals",
                "workspace: ws-a",
                "status: draft",
            ]),
        )

    first = build_review_packets(repo_root=repo, workspace="ws-a")
    second = build_review_packets(repo_root=repo, workspace="ws-a")

    assert [(packet.proposal_id, packet.packet_filename) for packet in first] == [
        ("Proposal Alpha", "proposal-alpha.md"),
        ("proposal/alpha", "proposal-alpha-2.md"),
        ("proposal_alpha", "proposal-alpha-3.md"),
    ]
    assert [(packet.proposal_id, packet.packet_filename) for packet in first] == [
        (packet.proposal_id, packet.packet_filename) for packet in second
    ]
