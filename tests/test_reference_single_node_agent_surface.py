from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


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


def test_submit_proposal_deferred_marker_present() -> None:
    contents = SERVER_PATH.read_text(encoding="utf-8")
    assert "submit_proposal remains non-executable" in contents


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
