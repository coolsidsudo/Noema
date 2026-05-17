from __future__ import annotations

import http.client
import json
from pathlib import Path
import threading
from typing import Any

from packages.noema_service import create_http_server
from packages.noema_service import cli as noema_cli


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


class RunningServer:
    def __init__(self, repo_root: Path) -> None:
        self.server = create_http_server(repo_root=repo_root, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def request(
        self,
        method: str,
        path: str,
        *,
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, str], dict[str, Any]]:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            response_body = response.read().decode("utf-8")
            return response.status, {name.lower(): value for name, value in response.getheaders()}, json.loads(response_body)
        finally:
            connection.close()

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, str], str]:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            response_body = response.read().decode("utf-8")
            return response.status, {name.lower(): value for name, value in response.getheaders()}, response_body
        finally:
            connection.close()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def _json_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


def _proposal_payload() -> dict[str, Any]:
    return {
        "id": "proposal-http",
        "created_by": "agent-http",
        "status": "draft",
        "target_ids": ["structured-1"],
        "title": "HTTP Proposal",
        "summary": "Submitted through HTTP.",
        "rationale": "Exercise adapter path.",
        "intended_effect": "Prove proposal creation.",
    }


def test_http_get_object_by_id_returns_core_envelope(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, headers, body = server.request("GET", "/v1/workspaces/ws-a/objects/structured-1")
    finally:
        server.close()

    assert status == 200
    assert headers["content-type"].startswith("application/json")
    assert body["ok"] is True
    assert body["operation"] == "get_object_by_id"
    assert body["data"]["object"]["id"] == "structured-1"
    assert body["data"]["object"]["content"] == "structured body"


def test_http_get_object_by_id_include_content_false(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request(
            "GET",
            "/v1/workspaces/ws-a/objects/structured-1?include_content=false",
        )
    finally:
        server.close()

    assert status == 200
    assert "content" not in body["data"]["object"]


def test_http_list_objects_with_filters_and_cursor(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        first_status, _, first = server.request(
            "GET",
            "/v1/workspaces/ws-a/objects?class=structured&status=active&limit=1&sort_by=id",
        )
        cursor = first["meta"]["pagination"]["next_cursor"]
        second_status, _, second = server.request(
            "GET",
            f"/v1/workspaces/ws-a/objects?class=structured&status=active&limit=1&sort_by=id&cursor={cursor}",
        )
    finally:
        server.close()

    assert first_status == 200
    assert first["operation"] == "list_objects"
    assert [item["id"] for item in first["data"]["items"]] == ["structured-1"]
    assert first["meta"]["pagination"]["next_cursor"] == "offset:1"
    assert second_status == 200
    assert [item["id"] for item in second["data"]["items"]] == ["structured-2"]


def test_http_traceability_query(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    payload = {
        "seed_ids": ["proposal-1"],
        "direction": "outbound",
        "link_types": ["targets", "results_in"],
        "limit": 10,
    }
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/traceability-links:query",
            body=json.dumps(payload),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 200
    assert body["operation"] == "get_traceability_links"
    links = {(link["from_id"], link["to_id"], link["type"]) for link in body["data"]["links"]}
    assert ("proposal-1", "structured-1", "targets") in links or (
        "proposal-1",
        "structured-2",
        "results_in",
    ) in links


def test_http_traceability_limit_over_500_preserves_core_invalid_limit(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    payload = {"seed_ids": ["proposal-1"], "limit": 501}
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/traceability-links:query",
            body=json.dumps(payload),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 400
    assert body["ok"] is False
    assert body["operation"] == "get_traceability_links"
    assert body["error"]["category"] == "invalid_request"
    assert body["error"]["code"] == "INVALID_LIMIT"


def test_http_submit_proposal_creates_markdown_and_returns_201(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/proposals",
            body=json.dumps(_proposal_payload()),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 201
    assert body["operation"] == "submit_proposal"
    assert body["ok"] is True
    assert (tmp_path / "proposals" / "ws-a" / "proposal-http.md").exists()


def test_http_submit_proposal_duplicate_returns_409(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    proposal = _proposal_payload()
    try:
        first_status, _, _ = server.request(
            "POST",
            "/v1/workspaces/ws-a/proposals",
            body=json.dumps(proposal),
            headers=_json_headers(),
        )
        second_status, _, second = server.request(
            "POST",
            "/v1/workspaces/ws-a/proposals",
            body=json.dumps(proposal),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert first_status == 201
    assert second_status == 409
    assert second["error"]["category"] == "conflict"
    assert second["error"]["code"] == "PROPOSAL_ALREADY_EXISTS"


def test_http_get_proposal_status(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request("GET", "/v1/workspaces/ws-a/proposals/proposal-1/status")
    finally:
        server.close()

    assert status == 200
    assert body["operation"] == "get_proposal_status"
    assert body["data"]["status"] == "under_review"
    assert body["data"]["result_links"] == ["structured-2"]
    assert body["data"]["log_refs"] == ["log-1"]


def test_http_invalid_boolean_query_returns_json_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, headers, body = server.request(
            "GET",
            "/v1/workspaces/ws-a/objects/structured-1?include_content=yes",
        )
    finally:
        server.close()

    assert status == 400
    assert headers["content-type"].startswith("application/json")
    assert body["ok"] is False
    assert body["error"]["code"] == "INVALID_BOOLEAN"


def test_http_invalid_integer_query_returns_json_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request("GET", "/v1/workspaces/ws-a/objects?limit=abc")
    finally:
        server.close()

    assert status == 400
    assert body["error"]["code"] == "INVALID_INTEGER"


def test_http_malformed_json_returns_json_invalid_request(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/traceability-links:query",
            body='{"seed_ids": ["proposal-1"',
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 400
    assert body["error"]["code"] == "INVALID_JSON"


def test_http_wrong_json_field_type_returns_invalid_body_field(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/traceability-links:query",
            body=json.dumps({"seed_ids": "proposal-1"}),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 400
    assert body["error"]["code"] == "INVALID_BODY_FIELD"


def test_http_unknown_route_returns_json_not_found(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request("GET", "/v1/nope")
    finally:
        server.close()

    assert status == 404
    assert body["operation"] == "http_request"
    assert body["error"]["category"] == "not_found"
    assert body["error"]["code"] == "ROUTE_NOT_FOUND"


def test_http_unsupported_method_returns_json_error(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request("PUT", "/v1/workspaces/ws-a/objects/structured-1")
    finally:
        server.close()

    assert status == 405
    assert body["operation"] == "http_request"
    assert body["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_http_rejects_unknown_query_parameter(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request("GET", "/v1/workspaces/ws-a/objects/structured-1?foo=bar")
    finally:
        server.close()

    assert status == 400
    assert body["error"]["code"] == "UNKNOWN_QUERY_PARAMETER"


def test_http_rejects_unknown_json_body_field(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    server = RunningServer(tmp_path)
    try:
        status, _, body = server.request(
            "POST",
            "/v1/workspaces/ws-a/traceability-links:query",
            body=json.dumps({"seed_ids": ["proposal-1"], "unexpected": True}),
            headers=_json_headers(),
        )
    finally:
        server.close()

    assert status == 400
    assert body["error"]["code"] == "UNKNOWN_BODY_FIELD"


def test_http_unexpected_core_exception_returns_json_internal_error(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    _seed_repo(tmp_path)

    def raise_unexpected_error(**_: Any) -> dict[str, Any]:
        raise RuntimeError("raw exception details must stay private")

    monkeypatch.setattr("packages.noema_service.http_api.get_object_by_id", raise_unexpected_error)
    server = RunningServer(tmp_path)
    try:
        status, headers, raw_body = server.request_raw("GET", "/v1/workspaces/ws-a/objects/structured-1")
    finally:
        server.close()

    body = json.loads(raw_body)
    assert status == 500
    assert headers["content-type"].startswith("application/json")
    assert body["ok"] is False
    assert body["operation"] in {"get_object_by_id", "http_request"}
    assert body["error"]["category"] == "internal_error"
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "raw exception details must stay private" not in raw_body


def test_cli_prints_startup_line_and_handles_keyboard_interrupt(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    class FakeServer:
        def __init__(self) -> None:
            self.shutdown_called = False
            self.server_close_called = False

        def serve_forever(self) -> None:
            raise KeyboardInterrupt

        def shutdown(self) -> None:
            self.shutdown_called = True

        def server_close(self) -> None:
            self.server_close_called = True

    fake_server = FakeServer()
    captured_args: dict[str, Any] = {}

    def fake_create_http_server(*, repo_root: Path, host: str, port: int) -> FakeServer:
        captured_args["repo_root"] = repo_root
        captured_args["host"] = host
        captured_args["port"] = port
        return fake_server

    monkeypatch.setattr(noema_cli, "create_http_server", fake_create_http_server)

    result = noema_cli.main(["--repo-root", str(tmp_path), "--host", "127.0.0.1", "--port", "8765"])
    output = capsys.readouterr().out

    assert result == 0
    assert captured_args == {"repo_root": tmp_path.resolve(), "host": "127.0.0.1", "port": 8765}
    assert "127.0.0.1" in output
    assert "8765" in output
    assert str(tmp_path.resolve()) in output
    assert fake_server.shutdown_called is True
    assert fake_server.server_close_called is True
