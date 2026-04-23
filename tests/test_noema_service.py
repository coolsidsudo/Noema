from __future__ import annotations

from pathlib import Path

from packages.noema_service import get_object_by_id, list_objects


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
        repo / "proposals" / "queue" / "proposal-1.md",
        "\n".join(
            [
                "id: proposal-1",
                "class: proposals",
                "workspace: ws-a",
                "status: under_review",
                "title: Proposal One",
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
