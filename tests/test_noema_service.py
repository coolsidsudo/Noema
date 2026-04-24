from __future__ import annotations

from pathlib import Path

from packages.noema_service import (
    get_object_by_id,
    get_proposal_status,
    get_traceability_links,
    list_objects,
    submit_proposal,
)


def _write_object(path: Path, frontmatter: str, body: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def _seed_repo(repo: Path) -> None:
    _write_object(
        repo / "raw" / "sources" / "raw-1.md",
        "\n".join(
            [
                "id: raw-1",
                "class: raw",
                "workspace: ws-a",
                "status: ingested",
                "title: Alpha source",
                "created_at: 2026-04-01T00:00:00Z",
                "updated_at: 2026-04-01T00:00:00Z",
            ]
        ),
        body="raw body",
    )
    _write_object(
        repo / "structured" / "pages" / "structured-1.md",
        "\n".join(
            [
                "id: structured-1",
                "class: structured",
                "workspace: ws-a",
                "status: active",
                "title: Alpha concept",
                "created_at: 2026-04-02T00:00:00Z",
                "updated_at: 2026-04-03T00:00:00Z",
                "supports:",
                "  - raw-1",
            ]
        ),
        body="structured body",
    )
    _write_object(
        repo / "structured" / "pages" / "structured-2.md",
        "\n".join(
            [
                "id: structured-2",
                "class: structured",
                "workspace: ws-a",
                "status: active",
                "title: Beta concept",
                "created_at: 2026-04-02T00:00:00Z",
                "updated_at: 2026-04-03T00:00:00Z",
                "supersedes:",
                "  - structured-1",
            ]
        ),
        body="structured body 2",
    )
    _write_object(
        repo / "proposals" / "queue" / "proposal-1.md",
        "\n".join(
            [
                "id: proposal-1",
                "class: proposals",
                "workspace: ws-a",
                "status: under_review",
                "title: Proposal One",
                "summary: Existing proposal summary",
                "created_by: maintainer",
                "created_at: 2026-04-04T00:00:00Z",
                "updated_at: 2026-04-04T00:00:00Z",
                "target_ids:",
                "  - structured-1",
                "results_in:",
                "  - structured-2",
            ]
        ),
        body="proposal body",
    )
    _write_object(
        repo / "logs" / "events" / "log-1.md",
        "\n".join(
            [
                "id: log-1",
                "class: logs",
                "workspace: ws-a",
                "status: recorded",
                "title: Event One",
                "created_at: 2026-04-05T00:00:00Z",
                "updated_at: 2026-04-05T00:00:00Z",
                "records_event_for:",
                "  - proposal-1",
            ]
        ),
        body="log body",
    )
    _write_object(
        repo / "structured" / "pages" / "structured-other.md",
        "\n".join(
            [
                "id: structured-other",
                "class: structured",
                "workspace: ws-b",
                "status: active",
                "title: Other workspace",
                "created_at: 2026-04-06T00:00:00Z",
                "updated_at: 2026-04-06T00:00:00Z",
            ]
        ),
        body="other body",
    )


def test_get_object_by_id_returns_expected_envelope(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_object_by_id(repo_root=tmp_path, workspace="ws-a", id="structured-1")

    assert result["ok"] is True
    assert result["operation"] == "get_object_by_id"
    assert result["request_id"].startswith("req_")
    assert result["timestamp"].endswith("Z")
    assert result["data"]["object"]["id"] == "structured-1"
    assert result["data"]["object"]["class"] == "structured"
    assert result["data"]["object"]["content"] == "structured body"


def test_get_object_by_id_omits_content_when_disabled(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_object_by_id(repo_root=tmp_path, workspace="ws-a", id="structured-1", include_content=False)

    assert result["ok"] is True
    assert "content" not in result["data"]["object"]


def test_list_objects_returns_bounded_filtered_results(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = list_objects(
        repo_root=tmp_path,
        workspace="ws-a",
        object_class="structured",
        status="active",
        title_contains="alpha",
        limit=1,
        sort_by="title",
    )

    assert result["ok"] is True
    assert len(result["data"]["items"]) == 1
    assert result["data"]["items"][0]["id"] == "structured-1"
    assert result["meta"]["pagination"]["limit"] == 1


def test_list_objects_cursor_pagination_uses_offset_format(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    first = list_objects(repo_root=tmp_path, workspace="ws-a", limit=2, sort_by="id")
    assert first["ok"] is True
    assert len(first["data"]["items"]) == 2
    assert first["meta"]["pagination"]["next_cursor"] == "offset:2"
    assert first["meta"]["pagination"]["has_more"] is True

    second = list_objects(
        repo_root=tmp_path,
        workspace="ws-a",
        limit=2,
        sort_by="id",
        cursor=first["meta"]["pagination"]["next_cursor"],
    )
    assert second["ok"] is True
    assert len(second["data"]["items"]) == 2


def test_invalid_cursor_format_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = list_objects(repo_root=tmp_path, workspace="ws-a", cursor="bad-cursor")

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "INVALID_CURSOR"


def test_invalid_limit_returns_limit_specific_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = list_objects(repo_root=tmp_path, workspace="ws-a", limit=0)

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "INVALID_LIMIT"
    assert result["error"]["message"] == "limit must be >= 1"
    assert result["error"]["details"] == {"limit": 0}


def test_workspace_scoping_is_preserved(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = list_objects(repo_root=tmp_path, workspace="ws-b")

    assert result["ok"] is True
    assert [item["id"] for item in result["data"]["items"]] == ["structured-other"]


def test_relationship_hints_are_included_only_when_requested(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    hidden = get_object_by_id(repo_root=tmp_path, workspace="ws-a", id="proposal-1")
    shown = get_object_by_id(
        repo_root=tmp_path,
        workspace="ws-a",
        id="proposal-1",
        include_relationship_hints=True,
    )

    assert "relationship_hints" not in hidden["data"]["object"]
    assert shown["data"]["object"]["relationship_hints"]["target_ids"] == ["structured-1"]
    assert shown["data"]["object"]["relationship_hints"]["results_in"] == ["structured-2"]


def test_get_traceability_links_returns_bounded_direct_outbound_links(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    result = get_traceability_links(
        repo_root=tmp_path,
        workspace="ws-a",
        seed_ids=["proposal-1"],
        direction="outbound",
        link_types=["targets", "results_in"],
        limit=1,
    )

    assert result["ok"] is True
    assert result["data"]["seed_ids"] == ["proposal-1"]
    assert len(result["data"]["links"]) == 1
    assert result["data"]["links"][0]["direction"] == "outbound"
    assert result["data"]["truncation"]["truncated"] is True


def test_get_traceability_links_empty_seed_ids_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_traceability_links(repo_root=tmp_path, workspace="ws-a", seed_ids=[])

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "EMPTY_SEED_IDS"
    assert result["error"]["message"] == "seed_ids must contain at least one id."
    assert result["error"]["details"] == {"seed_ids": []}


def test_get_traceability_links_returns_inbound_links_when_requested(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    result = get_traceability_links(
        repo_root=tmp_path,
        workspace="ws-a",
        seed_ids=["structured-1"],
        direction="inbound",
        link_types=["targets", "supersedes"],
        include_node_summaries=True,
    )

    assert result["ok"] is True
    assert {link["from_id"] for link in result["data"]["links"]} == {"proposal-1", "structured-2"}
    assert {link["type"] for link in result["data"]["links"]} == {"targets", "supersedes"}
    assert "nodes" in result["data"]


def test_get_traceability_links_multi_seed_inbound_includes_seed_to_seed_edges(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    result = get_traceability_links(
        repo_root=tmp_path,
        workspace="ws-a",
        seed_ids=["proposal-1", "structured-1"],
        direction="inbound",
        link_types=["targets"],
    )

    assert result["ok"] is True
    assert {
        (link["from_id"], link["to_id"], link["type"], link["direction"])
        for link in result["data"]["links"]
    } == {("proposal-1", "structured-1", "targets", "inbound")}


def test_get_traceability_links_unsupported_link_types_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_traceability_links(
        repo_root=tmp_path,
        workspace="ws-a",
        seed_ids=["proposal-1"],
        link_types=["foo"],
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "UNSUPPORTED_LINK_TYPES"


def test_get_traceability_links_invalid_direction_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_traceability_links(repo_root=tmp_path, workspace="ws-a", seed_ids=["proposal-1"], direction="sideways")

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "INVALID_DIRECTION"


def test_get_traceability_links_invalid_limit_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_traceability_links(repo_root=tmp_path, workspace="ws-a", seed_ids=["proposal-1"], limit=0)

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "INVALID_LIMIT"


def test_submit_proposal_writes_markdown_file_with_expected_path_and_shape(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    payload = {
        "id": "proposal-new",
        "created_by": "agent-x",
        "status": "draft",
        "target_ids": ["structured-1"],
        "title": "New Proposal",
        "summary": "Summarize this change.",
        "rationale": "Because reasons.",
        "intended_effect": "Improve structure.",
        "created_at": "2026-04-08T00:00:00Z",
    }

    result = submit_proposal(repo_root=tmp_path, workspace="ws-a", proposal=payload)

    assert result["ok"] is True
    proposal_file = tmp_path / "proposals" / "ws-a" / "proposal-new.md"
    assert proposal_file.exists()

    lines = proposal_file.read_text(encoding="utf-8").splitlines()
    expected_order = [
        "id: proposal-new",
        "workspace: ws-a",
        "class: proposals",
        "status: draft",
        "created_at: 2026-04-08T00:00:00Z",
        "created_by: agent-x",
        "title: New Proposal",
        "summary: Summarize this change.",
        "rationale: Because reasons.",
        "intended_effect: Improve structure.",
        "target_ids:",
        "  - structured-1",
        "supporting_raw_ids: []",
        "requested_reviewers: []",
        "results_in: []",
    ]
    for index, line in enumerate(expected_order, start=1):
        assert lines[index] == line

    body = "\n".join(lines)
    assert "# Proposal: New Proposal" in body
    assert "## Summary\nSummarize this change." in body
    assert "## Rationale\nBecause reasons." in body
    assert "## Intended effect\nImprove structure." in body


def test_submit_proposal_duplicate_returns_conflict(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    payload = {
        "id": "proposal-dupe",
        "created_by": "agent-x",
        "status": "draft",
        "target_ids": ["structured-1"],
        "title": "Dup",
        "summary": "sum",
        "rationale": "why",
        "intended_effect": "effect",
    }

    first = submit_proposal(repo_root=tmp_path, workspace="ws-a", proposal=payload)
    second = submit_proposal(repo_root=tmp_path, workspace="ws-a", proposal=payload)

    assert first["ok"] is True
    assert second["ok"] is False
    assert second["error"]["category"] == "conflict"


def test_submit_proposal_invalid_status_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    result = submit_proposal(
        repo_root=tmp_path,
        workspace="ws-a",
        proposal={
            "id": "proposal-invalid-status",
            "created_by": "agent-x",
            "status": "approved",
            "target_ids": ["structured-1"],
            "title": "Bad",
            "summary": "sum",
            "rationale": "why",
            "intended_effect": "effect",
        },
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "INVALID_PROPOSAL_STATUS"


def test_submit_proposal_empty_target_ids_returns_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    result = submit_proposal(
        repo_root=tmp_path,
        workspace="ws-a",
        proposal={
            "id": "proposal-empty-targets",
            "created_by": "agent-x",
            "status": "draft",
            "target_ids": [],
            "title": "Bad",
            "summary": "sum",
            "rationale": "why",
            "intended_effect": "effect",
        },
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "invalid_request"
    assert result["error"]["code"] == "EMPTY_TARGET_IDS"


def test_get_proposal_status_returns_stored_summary_fields(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_proposal_status(repo_root=tmp_path, workspace="ws-a", proposal_id="proposal-1")

    assert result["ok"] is True
    assert result["data"]["id"] == "proposal-1"
    assert result["data"]["status"] == "under_review"
    assert result["data"]["created_at"] == "2026-04-04T00:00:00Z"
    assert result["data"]["created_by"] == "maintainer"
    assert result["data"]["target_ids"] == ["structured-1"]
    assert result["data"]["summary"] == "Existing proposal summary"


def test_get_proposal_status_returns_result_links_from_metadata(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_proposal_status(repo_root=tmp_path, workspace="ws-a", proposal_id="proposal-1")

    assert result["ok"] is True
    assert result["data"]["result_links"] == ["structured-2"]


def test_get_proposal_status_returns_log_refs_from_logs(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_proposal_status(repo_root=tmp_path, workspace="ws-a", proposal_id="proposal-1")

    assert result["ok"] is True
    assert result["data"]["log_refs"] == ["log-1"]


def test_get_proposal_status_include_review_history_returns_empty_list(tmp_path: Path) -> None:
    _seed_repo(tmp_path)

    result = get_proposal_status(
        repo_root=tmp_path,
        workspace="ws-a",
        proposal_id="proposal-1",
        include_review_history=True,
    )

    assert result["ok"] is True
    assert result["data"]["review_history"] == []
