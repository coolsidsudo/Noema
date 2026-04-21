from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = REPO_ROOT / "deploy" / "reference-single-node" / "agent_surface" / "server.py"
CONFORMANCE_CHECK_PATH = REPO_ROOT / "deploy" / "reference-single-node" / "checks" / "check_reference_package.py"
CONTRACT_PATH = REPO_ROOT / "deploy" / "reference-single-node" / "contracts" / "agent-surface-baseline.json"


def _load_server_module():
    spec = importlib.util.spec_from_file_location("agent_surface_server", SERVER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_list_objects_and_get_object_by_id_are_bounded(tmp_path: Path) -> None:
    module = _load_server_module()

    target = tmp_path / "structured" / "pages" / "example.md"
    target.parent.mkdir(parents=True)
    target.write_text("hello", encoding="utf-8")

    objects = module.list_objects(tmp_path, "structured", limit=5)
    assert objects == [{"object_id": "structured/pages/example.md", "object_class": "structured"}]

    obj = module.get_object_by_id(tmp_path, "structured/pages/example.md")
    assert obj["object_class"] == "structured"
    assert obj["content"] == "hello"

    try:
        module.get_object_by_id(tmp_path, "../outside.md")
    except ValueError as exc:
        assert "escapes repository root" in str(exc)
    else:
        raise AssertionError("path traversal must be rejected")


def test_list_objects_invalid_limit_returns_bounded_client_error(tmp_path: Path) -> None:
    module = _load_server_module()

    server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.AgentSurfaceHandler)
    server.surface_config = module.SurfaceConfig(repo_root=tmp_path, contract_path=CONTRACT_PATH)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            urlopen(f"{base_url}/v1/list_objects?class=structured&limit=abc")
        except HTTPError as exc:
            assert exc.code == 400
            payload = json.loads(exc.read().decode("utf-8"))
            assert payload["error"] == "limit must be an integer between 1 and 200"
        else:
            raise AssertionError("invalid limit must return a client error")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_submit_proposal_http_route_is_executable(tmp_path: Path) -> None:
    module = _load_server_module()

    server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.AgentSurfaceHandler)
    server.surface_config = module.SurfaceConfig(repo_root=tmp_path, contract_path=CONTRACT_PATH)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        request = Request(
            f"{base_url}/v1/submit_proposal",
            method="POST",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"title": "HTTP proposal", "body": "Via route"}).encode("utf-8"),
        )
        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert response.status == 201
        assert payload["result"]["status"] == "draft"
        assert (tmp_path / payload["result"]["artifact_path"]).exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_submit_proposal_writes_bounded_proposal_artifact(tmp_path: Path) -> None:
    module = _load_server_module()
    result = module.submit_proposal(
        tmp_path,
        {
            "title": "Executable continuity proposal",
            "body": "Bounded proposal-lane write only.",
            "author": "pytest",
            "workspace": "tests",
            "visibility": "team",
        },
    )

    proposal_path = tmp_path / result["artifact_path"]
    assert proposal_path.exists()
    assert result["status"] == "draft"
    assert result["authority"] == "proposal-only"
    assert "proposals/submitted/" in result["artifact_path"]
    assert not (tmp_path / "structured").exists()
    assert not (tmp_path / "raw").exists()
    assert not (tmp_path / "logs").exists()

    created = json.loads(proposal_path.read_text(encoding="utf-8"))
    assert created["request"]["title"] == "Executable continuity proposal"
    assert created["canonical_apply"] == "out-of-scope"
    assert created["status"] == "draft"
    assert created["review_history"][0]["to_state"] == "draft"
    proposal_path.unlink()


def test_submit_proposal_rejects_invalid_payload(tmp_path: Path) -> None:
    module = _load_server_module()
    try:
        module.submit_proposal(tmp_path, {"title": "", "body": ""})
    except ValueError as exc:
        assert "title is required" in str(exc)
    else:
        raise AssertionError("invalid payload must fail")


def test_get_and_review_proposal_status_are_executable_and_bounded(tmp_path: Path) -> None:
    module = _load_server_module()
    submitted = module.submit_proposal(
        tmp_path,
        {
            "title": "Review continuity proposal",
            "body": "Keep status/review continuity bounded to proposal artifacts.",
            "author": "pytest",
            "workspace": "tests",
        },
    )
    proposal_id = submitted["proposal_id"]

    status_before = module.get_proposal_status(tmp_path, proposal_id)
    assert status_before["proposal"]["status"] == "draft"
    assert status_before["review_history"][0]["to_state"] == "draft"

    reviewed = module.review_proposal_status(
        tmp_path,
        {
            "proposal_id": proposal_id,
            "to_state": "under_review",
            "actor_id": "reviewer-1",
            "actor_type": "human",
            "evidence": [{"kind": "test", "ref": "pytest://review/1", "note": "bounded evidence"}],
        },
    )
    assert reviewed["status"] == "under_review"
    assert reviewed["previous_status"] == "draft"
    assert "proposals/submitted/" in reviewed["artifact_path"]

    status_after = module.get_proposal_status(tmp_path, proposal_id, include_result_links=False)
    assert status_after["proposal"]["status"] == "under_review"
    assert len(status_after["review_history"]) == 2
    assert status_after["review_history"][-1]["from_state"] == "draft"
    assert status_after["review_history"][-1]["to_state"] == "under_review"
    assert status_after["review_history"][-1]["evidence"][0]["kind"] == "test"
    assert status_after["log_links"][-1]["log_path"] == "logs/operations/proposal-review-events.jsonl"
    review_log = tmp_path / "logs" / "operations" / "proposal-review-events.jsonl"
    assert review_log.exists()
    assert len(review_log.read_text(encoding="utf-8").strip().splitlines()) == 1
    assert not (tmp_path / "structured").exists()
    assert not (tmp_path / "raw").exists()
    assert (tmp_path / "logs").exists()


def test_get_proposal_review_evidence_route_returns_review_event_links(tmp_path: Path) -> None:
    module = _load_server_module()
    submitted = module.submit_proposal(tmp_path, {"title": "T", "body": "B", "author": "pytest"})
    proposal_id = submitted["proposal_id"]
    module.review_proposal_status(
        tmp_path,
        {
            "proposal_id": proposal_id,
            "to_state": "under_review",
            "actor_id": "reviewer",
            "actor_type": "human",
            "evidence": [{"kind": "checklist", "ref": "pytest://review/checklist"}],
        },
    )

    evidence = module.get_proposal_review_evidence(tmp_path, proposal_id)
    assert evidence["proposal_id"] == proposal_id
    assert evidence["review_events"][-1]["to_state"] == "under_review"
    assert evidence["review_events"][-1]["evidence"][0]["kind"] == "checklist"
    assert evidence["review_events"][-1]["log_link"]["log_path"] == "logs/operations/proposal-review-events.jsonl"


def test_review_proposal_status_rejects_invalid_transition(tmp_path: Path) -> None:
    module = _load_server_module()
    submitted = module.submit_proposal(tmp_path, {"title": "T", "body": "B"})
    try:
        module.review_proposal_status(
            tmp_path,
            {"proposal_id": submitted["proposal_id"], "to_state": "accepted", "actor_id": "reviewer"},
        )
    except ValueError as exc:
        assert "invalid transition" in str(exc)
    else:
        raise AssertionError("invalid transition must fail")


def test_review_proposal_status_rejects_invalid_evidence_payload(tmp_path: Path) -> None:
    module = _load_server_module()
    submitted = module.submit_proposal(tmp_path, {"title": "T", "body": "B"})
    try:
        module.review_proposal_status(
            tmp_path,
            {"proposal_id": submitted["proposal_id"], "to_state": "under_review", "evidence": "not-a-list"},
        )
    except ValueError as exc:
        assert "evidence must be a list of objects" in str(exc)
    else:
        raise AssertionError("invalid evidence payload must fail")


def test_legacy_submitted_artifact_is_normalized_for_status_reads(tmp_path: Path) -> None:
    module = _load_server_module()
    artifact = tmp_path / "proposals" / "submitted" / "proposal-legacy-0001.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        json.dumps(
            {
                "schema_version": "phase7-slice4-reference",
                "proposal_id": "proposal-legacy-0001",
                "submitted_at": "2026-04-20T00:00:00+00:00",
                "status": "submitted",
                "authority": "proposal-only",
                "canonical_apply": "out-of-scope",
                "request": {"title": "Legacy", "author": "legacy-agent"},
            }
        ),
        encoding="utf-8",
    )

    status = module.get_proposal_status(tmp_path, "proposal-legacy-0001")
    assert status["proposal"]["status"] == "draft"
    assert status["proposal"]["updated_at"] == "2026-04-20T00:00:00+00:00"
    assert status["review_history"][0]["to_state"] == "draft"


def test_legacy_submitted_artifact_is_normalized_for_review_transitions(tmp_path: Path) -> None:
    module = _load_server_module()
    artifact = tmp_path / "proposals" / "submitted" / "proposal-legacy-0002.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        json.dumps(
            {
                "schema_version": "phase7-slice4-reference",
                "proposal_id": "proposal-legacy-0002",
                "submitted_at": "2026-04-20T00:00:00+00:00",
                "status": "submitted",
                "authority": "proposal-only",
                "canonical_apply": "out-of-scope",
                "request": {"title": "Legacy 2", "author": "legacy-agent"},
            }
        ),
        encoding="utf-8",
    )

    reviewed = module.review_proposal_status(
        tmp_path,
        {
            "proposal_id": "proposal-legacy-0002",
            "to_state": "under_review",
            "actor_id": "reviewer",
            "actor_type": "human",
        },
    )
    assert reviewed["previous_status"] == "draft"
    assert reviewed["status"] == "under_review"
    updated = json.loads(artifact.read_text(encoding="utf-8"))
    assert updated["status"] == "under_review"
    assert isinstance(updated["review_history"], list)
    assert len(updated["review_history"]) == 2


def test_reference_package_conformance_script_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(CONFORMANCE_CHECK_PATH)],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr + "\n" + result.stdout
    assert "All reference-single-node conformance checks passed." in result.stdout
