#!/usr/bin/env python3
"""Bounded executable machine-facing facade for the reference single-node package.

This service intentionally supports read/query behavior only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ALLOWED_CLASSES = ("raw", "structured", "proposals", "logs")
OBJECT_EXTENSIONS = {".md", ".json", ".yml", ".yaml", ".txt"}
DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@dataclass(frozen=True)
class SurfaceConfig:
    repo_root: Path
    contract_path: Path


def _safe_class_root(repo_root: Path, object_class: str) -> Path:
    if object_class not in ALLOWED_CLASSES:
        raise ValueError(f"unsupported class: {object_class}")
    return (repo_root / object_class).resolve()


def _parse_list_limit(raw_limit: str) -> int:
    try:
        limit = int(raw_limit)
    except ValueError as exc:
        raise ValueError("limit must be an integer between 1 and 200") from exc

    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError("limit must be an integer between 1 and 200")
    return limit


def _is_supported_object(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in OBJECT_EXTENSIONS


def list_objects(repo_root: Path, object_class: str, limit: int = DEFAULT_LIMIT) -> list[dict[str, str]]:
    class_root = _safe_class_root(repo_root, object_class)
    if not class_root.exists():
        return []

    bounded_limit = max(1, min(limit, MAX_LIMIT))
    objects: list[dict[str, str]] = []
    for candidate in sorted(class_root.rglob("*")):
        if len(objects) >= bounded_limit:
            break
        if not _is_supported_object(candidate):
            continue
        object_id = str(candidate.resolve().relative_to(repo_root.resolve()))
        objects.append(
            {
                "object_id": object_id,
                "object_class": object_class,
            }
        )

    return objects


def get_object_by_id(repo_root: Path, object_id: str) -> dict[str, str]:
    candidate = (repo_root / object_id).resolve()
    repo_root_resolved = repo_root.resolve()
    if repo_root_resolved not in candidate.parents and candidate != repo_root_resolved:
        raise ValueError("object_id escapes repository root")
    if not _is_supported_object(candidate):
        raise FileNotFoundError(object_id)

    relative_path = candidate.relative_to(repo_root_resolved)
    object_class = relative_path.parts[0] if relative_path.parts else ""
    if object_class not in ALLOWED_CLASSES:
        raise ValueError("object class is out of bounded surface scope")

    content = candidate.read_text(encoding="utf-8")
    return {
        "object_id": str(relative_path),
        "object_class": object_class,
        "content": content,
    }


class AgentSurfaceHandler(BaseHTTPRequestHandler):
    server_version = "NoemaAgentSurface/0.1"

    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @property
    def config(self) -> SurfaceConfig:
        return self.server.surface_config  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/healthz":
            self._write_json({"status": "ok", "surface": "bounded-read-query"})
            return

        if parsed.path == "/v1/list_objects":
            object_class = query.get("class", ["structured"])[0]
            raw_limit = query.get("limit", [str(DEFAULT_LIMIT)])[0]
            try:
                limit = _parse_list_limit(raw_limit)
                items = list_objects(self.config.repo_root, object_class, limit)
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json({"operation": "list_objects", "items": items})
            return

        if parsed.path == "/v1/get_object_by_id":
            object_id = query.get("id", [""])[0]
            if not object_id:
                self._write_json({"error": "id query parameter is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                item = get_object_by_id(self.config.repo_root, object_id)
            except FileNotFoundError:
                self._write_json({"error": "object not found"}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json({"operation": "get_object_by_id", "item": item})
            return

        if parsed.path == "/v1/submit_proposal":
            self._write_json(
                {
                    "operation": "submit_proposal",
                    "status": "deferred",
                    "message": "submit_proposal remains non-executable in Phase 7 Slice 3; proposal-only posture preserved.",
                },
                status=HTTPStatus.NOT_IMPLEMENTED,
            )
            return

        if parsed.path == "/v1/contract":
            try:
                contract = json.loads(self.config.contract_path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                self._write_json({"error": "contract file not found"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            self._write_json(contract)
            return

        self._write_json({"error": "route not found"}, status=HTTPStatus.NOT_FOUND)


def run_server() -> None:
    host = os.environ.get("NOEMA_AGENT_HOST", "0.0.0.0")
    port = int(os.environ.get("NOEMA_AGENT_PORT", "8787"))
    repo_root = Path(os.environ.get("NOEMA_MACHINE_REPO_ROOT", "/repo"))
    contract_path = Path(os.environ.get("NOEMA_AGENT_CONTRACT_PATH", "/surface/contracts/agent-surface-baseline.json"))

    server = ThreadingHTTPServer((host, port), AgentSurfaceHandler)
    server.surface_config = SurfaceConfig(repo_root=repo_root, contract_path=contract_path)  # type: ignore[attr-defined]
    print(f"noema-agent-surface running on {host}:{port} repo_root={repo_root}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
