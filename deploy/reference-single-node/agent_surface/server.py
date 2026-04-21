#!/usr/bin/env python3
"""Bounded executable machine-facing facade for the reference single-node package.

This service supports read/query behavior plus proposal-lane submission continuity.
Canonical apply/publish remains out of scope.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from dataclasses import dataclass
from typing import Any
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ALLOWED_CLASSES = ("raw", "structured", "proposals", "logs")
OBJECT_EXTENSIONS = {".md", ".json", ".yml", ".yaml", ".txt"}
DEFAULT_LIMIT = 50
MAX_LIMIT = 200
DEFAULT_RECENT_CONTINUITY_LIMIT = 10
MAX_RECENT_CONTINUITY_LIMIT = 50
PROPOSAL_SCHEMA_VERSION = "phase7-slice7-reference"
PROPOSAL_REVIEW_LOG_PATH = Path("logs/operations/proposal-review-events.jsonl")
PROPOSAL_ALLOWED_TRANSITIONS = {
    "draft": {"under_review", "withdrawn"},
    "under_review": {"accepted", "rejected", "withdrawn"},
    "accepted": set(),
    "rejected": set(),
    "withdrawn": set(),
}
PROPOSAL_LEGACY_STATUS_ALIASES = {
    "submitted": "draft",
}


@dataclass(frozen=True)
class ContinuityValidationError(ValueError):
    """Structured fail-closed error for proposal continuity validation surfaces."""

    code: str
    message: str
    phase: str
    event_id: str | None = None
    log_record_id: str | None = None
    log_path: str | None = None
    expected_log_path: str | None = None

    def __str__(self) -> str:
        return self.message

    def as_diagnostics(self, proposal_id: str) -> dict[str, Any]:
        return {
            "category": "proposal_review_continuity",
            "proposal_id": proposal_id,
            "failure_code": self.code,
            "message": self.message,
            "phase": self.phase,
            "event_id": self.event_id,
            "log_record_id": self.log_record_id,
            "log_path": self.log_path,
            "expected_log_path": self.expected_log_path,
        }


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


def _parse_recent_continuity_limit(raw_limit: str) -> int:
    try:
        limit = int(raw_limit)
    except ValueError as exc:
        raise ValueError("limit must be an integer between 1 and 50") from exc
    if limit < 1 or limit > MAX_RECENT_CONTINUITY_LIMIT:
        raise ValueError("limit must be an integer between 1 and 50")
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


def _normalize_proposal_request(payload: dict) -> dict[str, str]:
    title = str(payload.get("title", "")).strip()
    body = str(payload.get("body", "")).strip()
    author = str(payload.get("author", "agent")).strip() or "agent"
    workspace = str(payload.get("workspace", "default")).strip() or "default"
    visibility = str(payload.get("visibility", "team")).strip() or "team"

    if not title:
        raise ValueError("title is required")
    if not body:
        raise ValueError("body is required")
    if len(title) > 200:
        raise ValueError("title must be 200 characters or fewer")
    if len(body) > 20000:
        raise ValueError("body must be 20000 characters or fewer")

    return {
        "title": title,
        "body": body,
        "author": author,
        "workspace": workspace,
        "visibility": visibility,
    }


def _proposal_artifact_path(repo_root: Path, proposal_id: str) -> Path:
    if not proposal_id or "/" in proposal_id or "\\" in proposal_id:
        raise ValueError("proposal_id must be a simple identifier")

    proposals_root = _safe_class_root(repo_root, "proposals")
    return proposals_root / "submitted" / f"{proposal_id}.json"


def _iso_now() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _bool_query_flag(raw_value: str) -> bool:
    return raw_value.lower() in {"1", "true", "yes", "on"}


def _normalize_stored_proposal(stored: dict) -> dict:
    normalized = dict(stored)
    proposal_id = str(normalized.get("proposal_id", "unknown-proposal"))
    submitted_at = str(normalized.get("submitted_at", _iso_now()))
    current_status = str(normalized.get("status", "draft"))
    canonical_status = PROPOSAL_LEGACY_STATUS_ALIASES.get(current_status, current_status)
    if canonical_status not in PROPOSAL_ALLOWED_TRANSITIONS:
        raise ValueError(f"unsupported proposal status: {current_status}")

    normalized["status"] = canonical_status
    normalized.setdefault("submitted_at", submitted_at)
    normalized.setdefault("updated_at", submitted_at)

    if "review_history" not in normalized or not isinstance(normalized["review_history"], list):
        event_id = f"evt-{sha256(f'{proposal_id}:{canonical_status}:{submitted_at}'.encode('utf-8')).hexdigest()[:12]}"
        normalized["review_history"] = [
            {
                "event_id": event_id,
                "from_state": None,
                "to_state": canonical_status,
                "actor_id": str(normalized.get("request", {}).get("author", "legacy")),
                "actor_type": "agent",
                "timestamp": submitted_at,
                "notes": "normalized legacy proposal state",
            }
        ]

    return normalized


def submit_proposal(repo_root: Path, payload: dict) -> dict[str, str]:
    normalized = _normalize_proposal_request(payload)
    proposals_root = _safe_class_root(repo_root, "proposals")
    submissions_root = proposals_root / "submitted"
    submissions_root.mkdir(parents=True, exist_ok=True)

    submitted_at = _iso_now()
    identity_input = json.dumps(normalized, sort_keys=True, ensure_ascii=False).encode("utf-8")
    digest = sha256(identity_input).hexdigest()[:12]
    date_prefix = datetime.now(tz=UTC).strftime("%Y%m%d")
    proposal_id = f"proposal-{date_prefix}-{digest}"

    output_path = _proposal_artifact_path(repo_root, proposal_id)
    event_id = f"evt-{sha256(f'{proposal_id}:draft:{submitted_at}'.encode('utf-8')).hexdigest()[:12]}"
    output_record = {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "submitted_at": submitted_at,
        "updated_at": submitted_at,
        "status": "draft",
        "authority": "proposal-only",
        "canonical_apply": "out-of-scope",
        "request": normalized,
        "review_history": [
            {
                "event_id": event_id,
                "from_state": None,
                "to_state": "draft",
                "actor_id": normalized["author"],
                "actor_type": "agent",
                "timestamp": submitted_at,
                "notes": "proposal submitted",
            }
        ],
    }
    output_path.write_text(json.dumps(output_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    relative_path = output_path.resolve().relative_to(repo_root.resolve())
    return {
        "proposal_id": proposal_id,
        "status": "draft",
        "authority": "proposal-only",
        "canonical_apply": "out-of-scope",
        "artifact_path": str(relative_path),
    }


def get_proposal_status(
    repo_root: Path,
    proposal_id: str,
    *,
    include_review_history: bool = True,
    include_result_links: bool = True,
) -> dict:
    proposal_path = _proposal_artifact_path(repo_root, proposal_id)
    if not proposal_path.exists():
        raise FileNotFoundError(proposal_id)

    stored = json.loads(proposal_path.read_text(encoding="utf-8"))
    stored = _normalize_stored_proposal(stored)
    request = stored.get("request", {})
    result = {
        "proposal": {
            "id": stored["proposal_id"],
            "status": stored["status"],
            "created_at": stored["submitted_at"],
            "updated_at": stored.get("updated_at", stored["submitted_at"]),
            "created_by": request.get("author", "unknown"),
            "workspace": request.get("workspace", "default"),
            "summary": request.get("title", ""),
            "visibility": request.get("visibility", "team"),
        },
        "artifact_path": str(proposal_path.resolve().relative_to(repo_root.resolve())),
        "authority": stored.get("authority", "proposal-only"),
        "canonical_apply": stored.get("canonical_apply", "out-of-scope"),
    }

    if include_review_history:
        result["review_history"] = stored.get("review_history", [])
        result["log_links"] = [entry["log_link"] for entry in result["review_history"] if "log_link" in entry]
    if include_result_links:
        result["result_links"] = stored.get("results_in", [])
    return result


def _normalize_review_request(payload: dict) -> dict[str, str]:
    proposal_id = str(payload.get("proposal_id", "")).strip()
    to_state = str(payload.get("to_state", "")).strip()
    actor_id = str(payload.get("actor_id", "reviewer")).strip() or "reviewer"
    actor_type = str(payload.get("actor_type", "human")).strip() or "human"
    notes = str(payload.get("notes", "")).strip()
    evidence = payload.get("evidence", [])

    if not proposal_id:
        raise ValueError("proposal_id is required")
    if not to_state:
        raise ValueError("to_state is required")
    if to_state not in PROPOSAL_ALLOWED_TRANSITIONS:
        raise ValueError("to_state must be one of draft|under_review|accepted|rejected|withdrawn")
    if actor_type not in {"human", "agent", "service"}:
        raise ValueError("actor_type must be one of human|agent|service")

    normalized_evidence = _normalize_review_evidence(evidence)

    return {
        "proposal_id": proposal_id,
        "to_state": to_state,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "notes": notes,
        "evidence": normalized_evidence,
    }


def _normalize_review_evidence(raw_evidence: object) -> list[dict[str, str]]:
    if raw_evidence in (None, ""):
        return []
    if not isinstance(raw_evidence, list):
        raise ValueError("evidence must be a list of objects")
    if len(raw_evidence) > 10:
        raise ValueError("evidence must contain at most 10 entries")

    normalized: list[dict[str, str]] = []
    for item in raw_evidence:
        if not isinstance(item, dict):
            raise ValueError("evidence entries must be objects")
        kind = str(item.get("kind", "")).strip()
        ref = str(item.get("ref", "")).strip()
        digest = str(item.get("sha256", "")).strip()
        note = str(item.get("note", "")).strip()
        if not kind:
            raise ValueError("evidence.kind is required")
        if not ref:
            raise ValueError("evidence.ref is required")
        if len(kind) > 60:
            raise ValueError("evidence.kind must be 60 characters or fewer")
        if len(ref) > 500:
            raise ValueError("evidence.ref must be 500 characters or fewer")
        if digest and len(digest) != 64:
            raise ValueError("evidence.sha256 must be 64 characters when provided")
        if note and len(note) > 500:
            raise ValueError("evidence.note must be 500 characters or fewer")
        normalized.append({"kind": kind, "ref": ref, "sha256": digest, "note": note})
    return normalized


def _append_review_log_event(repo_root: Path, payload: dict) -> dict[str, str]:
    log_path = (repo_root / PROPOSAL_REVIEW_LOG_PATH).resolve()
    repo_root_resolved = repo_root.resolve()
    if repo_root_resolved not in log_path.parents:
        raise ValueError("review log path escapes repository root")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    record_id = f"log-{sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()[:12]}"
    record = dict(payload)
    record["record_id"] = record_id
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")

    return {
        "log_path": str(log_path.relative_to(repo_root_resolved)),
        "log_record_id": record_id,
    }


def _load_review_log_entries(repo_root: Path) -> dict[str, dict]:
    log_path = (repo_root / PROPOSAL_REVIEW_LOG_PATH).resolve()
    repo_root_resolved = repo_root.resolve()
    if repo_root_resolved not in log_path.parents:
        raise ValueError("review log path escapes repository root")
    if not log_path.exists():
        return {}

    indexed: dict[str, dict] = {}
    with log_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("proposal review log contains malformed jsonl entry") from exc
            if not isinstance(record, dict):
                raise ValueError("proposal review log entry must be an object")
            record_id = str(record.get("record_id", "")).strip()
            if not record_id:
                raise ValueError("proposal review log entry missing record_id")
            indexed[record_id] = record
    return indexed


def _validate_review_history_entry_shape(entry: object) -> dict:
    if not isinstance(entry, dict):
        raise ValueError("review history entries must be objects")
    event_id = str(entry.get("event_id", "")).strip()
    to_state = str(entry.get("to_state", "")).strip()
    timestamp = str(entry.get("timestamp", "")).strip()
    actor_id = str(entry.get("actor_id", "")).strip()
    actor_type = str(entry.get("actor_type", "")).strip()
    if not event_id:
        raise ValueError("review history entry missing event_id")
    if not to_state:
        raise ValueError("review history entry missing to_state")
    if not timestamp:
        raise ValueError("review history entry missing timestamp")
    if not actor_id:
        raise ValueError("review history entry missing actor_id")
    if actor_type not in {"human", "agent", "service"}:
        raise ValueError("review history entry actor_type must be one of human|agent|service")

    evidence = entry.get("evidence", [])
    normalized_evidence = _normalize_review_evidence(evidence)
    normalized = dict(entry)
    normalized["event_id"] = event_id
    normalized["to_state"] = to_state
    normalized["timestamp"] = timestamp
    normalized["actor_id"] = actor_id
    normalized["actor_type"] = actor_type
    normalized["evidence"] = normalized_evidence
    return normalized


def review_proposal_status(repo_root: Path, payload: dict) -> dict[str, str]:
    normalized = _normalize_review_request(payload)
    proposal_path = _proposal_artifact_path(repo_root, normalized["proposal_id"])
    if not proposal_path.exists():
        raise FileNotFoundError(normalized["proposal_id"])

    stored = json.loads(proposal_path.read_text(encoding="utf-8"))
    stored = _normalize_stored_proposal(stored)
    current_state = stored.get("status", "draft")
    to_state = normalized["to_state"]
    allowed_targets = PROPOSAL_ALLOWED_TRANSITIONS.get(current_state, set())
    if to_state not in allowed_targets:
        raise ValueError(f"invalid transition: {current_state} -> {to_state}")

    changed_at = _iso_now()
    event_id = f"evt-{sha256(f'{stored['proposal_id']}:{current_state}:{to_state}:{changed_at}'.encode('utf-8')).hexdigest()[:12]}"
    history_entry = {
        "event_id": event_id,
        "from_state": current_state,
        "to_state": to_state,
        "actor_id": normalized["actor_id"],
        "actor_type": normalized["actor_type"],
        "timestamp": changed_at,
        "notes": normalized["notes"],
    }
    if normalized["evidence"]:
        history_entry["evidence"] = normalized["evidence"]
    if to_state in {"accepted", "rejected"}:
        history_entry["decision"] = to_state
    history_entry["log_link"] = _append_review_log_event(
        repo_root,
        {
            "proposal_id": stored["proposal_id"],
            "event_id": event_id,
            "from_state": current_state,
            "to_state": to_state,
            "actor_id": normalized["actor_id"],
            "actor_type": normalized["actor_type"],
            "timestamp": changed_at,
            "notes": normalized["notes"],
            "evidence_count": len(normalized["evidence"]),
        },
    )

    review_history = stored.setdefault("review_history", [])
    review_history.append(history_entry)
    stored["status"] = to_state
    stored["updated_at"] = changed_at
    proposal_path.write_text(json.dumps(stored, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "proposal_id": stored["proposal_id"],
        "status": to_state,
        "previous_status": current_state,
        "authority": "proposal-only",
        "canonical_apply": "out-of-scope",
        "artifact_path": str(proposal_path.resolve().relative_to(repo_root.resolve())),
    }


def get_proposal_review_evidence(repo_root: Path, proposal_id: str) -> dict:
    status = get_proposal_status(
        repo_root,
        proposal_id,
        include_review_history=True,
        include_result_links=False,
    )
    review_history = status.get("review_history", [])
    if not isinstance(review_history, list):
        raise ValueError("proposal review_history must be a list")
    log_records = _load_review_log_entries(repo_root)
    expected_log_path = str(PROPOSAL_REVIEW_LOG_PATH)
    events = []
    continuity_checked_events = 0
    for entry in review_history:
        normalized_entry = _validate_review_history_entry_shape(entry)
        from_state = normalized_entry.get("from_state")
        log_link = normalized_entry.get("log_link")
        if from_state is not None:
            if not isinstance(log_link, dict):
                raise ContinuityValidationError(
                    code="CONTINUITY_REVIEW_EVENT_MISSING_LOG_LINK",
                    message="review continuity event missing log_link",
                    phase="review_history_log_link_presence",
                    event_id=normalized_entry["event_id"],
                )
            log_path = str(log_link.get("log_path", "")).strip()
            record_id = str(log_link.get("log_record_id", "")).strip()
            if log_path != expected_log_path:
                raise ContinuityValidationError(
                    code="CONTINUITY_LOG_PATH_OUT_OF_SCOPE",
                    message="review continuity event log_path is out of bounded continuity scope",
                    phase="review_history_log_link_scope",
                    event_id=normalized_entry["event_id"],
                    log_record_id=record_id or None,
                    log_path=log_path or None,
                    expected_log_path=expected_log_path,
                )
            if not record_id:
                raise ContinuityValidationError(
                    code="CONTINUITY_REVIEW_EVENT_MISSING_LOG_RECORD_ID",
                    message="review continuity event missing log_record_id",
                    phase="review_history_log_record_id_presence",
                    event_id=normalized_entry["event_id"],
                    log_path=log_path,
                    expected_log_path=expected_log_path,
                )
            linked_record = log_records.get(record_id)
            if linked_record is None:
                raise ContinuityValidationError(
                    code="CONTINUITY_LOG_RECORD_MISSING",
                    message="review continuity event references missing append-only log record",
                    phase="append_only_log_record_lookup",
                    event_id=normalized_entry["event_id"],
                    log_record_id=record_id,
                    log_path=log_path,
                    expected_log_path=expected_log_path,
                )
            if str(linked_record.get("proposal_id", "")) != proposal_id:
                raise ContinuityValidationError(
                    code="CONTINUITY_LOG_RECORD_PROPOSAL_ID_MISMATCH",
                    message="review continuity log_link proposal_id mismatch",
                    phase="append_only_log_record_consistency",
                    event_id=normalized_entry["event_id"],
                    log_record_id=record_id,
                    log_path=log_path,
                    expected_log_path=expected_log_path,
                )
            if str(linked_record.get("event_id", "")) != normalized_entry["event_id"]:
                raise ContinuityValidationError(
                    code="CONTINUITY_LOG_RECORD_EVENT_ID_MISMATCH",
                    message="review continuity log_link event_id mismatch",
                    phase="append_only_log_record_consistency",
                    event_id=normalized_entry["event_id"],
                    log_record_id=record_id,
                    log_path=log_path,
                    expected_log_path=expected_log_path,
                )
            continuity_checked_events += 1

        events.append(
            {
                "event_id": normalized_entry["event_id"],
                "from_state": from_state,
                "to_state": normalized_entry["to_state"],
                "timestamp": normalized_entry["timestamp"],
                "actor_id": normalized_entry["actor_id"],
                "actor_type": normalized_entry["actor_type"],
                "evidence": normalized_entry["evidence"],
                "log_link": log_link if isinstance(log_link, dict) else None,
            }
        )
    return {
        "proposal_id": status["proposal"]["id"],
        "status": status["proposal"]["status"],
        "artifact_path": status["artifact_path"],
        "review_events": events,
        "continuity": {
            "validated_review_events": continuity_checked_events,
            "missing_log_links": 0,
            "log_path": expected_log_path,
            "diagnostics_mode": "bounded-fail-closed",
        },
        "authority": "proposal-review-evidence-read-only",
        "canonical_apply": "out-of-scope",
    }


def list_recent_continuity_validation_outcomes(
    repo_root: Path, *, limit: int = DEFAULT_RECENT_CONTINUITY_LIMIT
) -> dict[str, Any]:
    proposals_root = _safe_class_root(repo_root, "proposals")
    submitted_root = proposals_root / "submitted"
    if not submitted_root.exists():
        return {
            "items": [],
            "summary": {"validated": 0, "failed": 0, "total": 0},
            "limit": limit,
        }

    bounded_limit = max(1, min(limit, MAX_RECENT_CONTINUITY_LIMIT))
    proposal_artifacts = sorted(submitted_root.glob("*.json"), key=lambda path: path.name, reverse=True)
    items: list[dict[str, Any]] = []

    for artifact in proposal_artifacts:
        if len(items) >= bounded_limit:
            break
        proposal_id = artifact.stem
        try:
            evidence = get_proposal_review_evidence(repo_root, proposal_id)
            events = evidence.get("review_events", [])
            latest_event = events[-1] if events else None
            items.append(
                {
                    "proposal_id": proposal_id,
                    "artifact_path": evidence.get("artifact_path"),
                    "proposal_status": evidence.get("status"),
                    "outcome_class": "validated",
                    "continuity": {
                        "validated_review_events": evidence.get("continuity", {}).get("validated_review_events", 0),
                        "log_path": evidence.get("continuity", {}).get("log_path"),
                        "diagnostics_mode": evidence.get("continuity", {}).get("diagnostics_mode"),
                    },
                    "latest_event": {
                        "event_id": (latest_event or {}).get("event_id"),
                        "timestamp": (latest_event or {}).get("timestamp"),
                        "to_state": (latest_event or {}).get("to_state"),
                    },
                }
            )
        except ContinuityValidationError as exc:
            items.append(
                {
                    "proposal_id": proposal_id,
                    "artifact_path": str(artifact.resolve().relative_to(repo_root.resolve())),
                    "proposal_status": None,
                    "outcome_class": "failed",
                    "continuity": {"failure_code": exc.code, "phase": exc.phase},
                    "latest_event": {"event_id": exc.event_id, "timestamp": None, "to_state": None},
                    "diagnostics": exc.as_diagnostics(proposal_id),
                }
            )
        except ValueError as exc:
            items.append(
                {
                    "proposal_id": proposal_id,
                    "artifact_path": str(artifact.resolve().relative_to(repo_root.resolve())),
                    "proposal_status": None,
                    "outcome_class": "failed",
                    "continuity": {
                        "failure_code": "CONTINUITY_VALIDATION_INPUT_ERROR",
                        "phase": "review_history_shape_validation",
                    },
                    "latest_event": {"event_id": None, "timestamp": None, "to_state": None},
                    "diagnostics": {
                        "category": "proposal_review_continuity",
                        "proposal_id": proposal_id,
                        "failure_code": "CONTINUITY_VALIDATION_INPUT_ERROR",
                        "message": str(exc),
                        "phase": "review_history_shape_validation",
                    },
                }
            )

    validated = sum(1 for item in items if item["outcome_class"] == "validated")
    failed = len(items) - validated
    return {
        "items": items,
        "summary": {"validated": validated, "failed": failed, "total": len(items)},
        "limit": bounded_limit,
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
            self._write_json({"status": "ok", "surface": "bounded-read-query-plus-proposal-submit"})
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
                    "status": "method-required",
                    "message": "submit_proposal is executable in Phase 7 Slice 6 via POST with JSON body.",
                },
                status=HTTPStatus.METHOD_NOT_ALLOWED,
            )
            return

        if parsed.path == "/v1/get_proposal_status":
            proposal_id = query.get("id", [""])[0]
            if not proposal_id:
                self._write_json({"error": "id query parameter is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            include_review_history = _bool_query_flag(query.get("include_review_history", ["true"])[0])
            include_result_links = _bool_query_flag(query.get("include_result_links", ["true"])[0])
            try:
                proposal = get_proposal_status(
                    self.config.repo_root,
                    proposal_id,
                    include_review_history=include_review_history,
                    include_result_links=include_result_links,
                )
            except FileNotFoundError:
                self._write_json({"error": "proposal not found"}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            self._write_json({"operation": "get_proposal_status", "result": proposal})
            return

        if parsed.path == "/v1/get_proposal_review_evidence":
            proposal_id = query.get("id", [""])[0]
            if not proposal_id:
                self._write_json({"error": "id query parameter is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                evidence = get_proposal_review_evidence(self.config.repo_root, proposal_id)
            except ContinuityValidationError as exc:
                self._write_json(
                    {
                        "error": exc.message,
                        "error_code": exc.code,
                        "diagnostics": exc.as_diagnostics(proposal_id),
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            except FileNotFoundError:
                self._write_json({"error": "proposal not found"}, status=HTTPStatus.NOT_FOUND)
                return
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json({"operation": "get_proposal_review_evidence", "result": evidence})
            return

        if parsed.path == "/v1/list_recent_continuity_validation_outcomes":
            raw_limit = query.get("limit", [str(DEFAULT_RECENT_CONTINUITY_LIMIT)])[0]
            try:
                limit = _parse_recent_continuity_limit(raw_limit)
                outcomes = list_recent_continuity_validation_outcomes(self.config.repo_root, limit=limit)
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json({"operation": "list_recent_continuity_validation_outcomes", "result": outcomes})
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

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/v1/submit_proposal":
            if parsed.path != "/v1/review_proposal_status":
                self._write_json({"error": "route not found"}, status=HTTPStatus.NOT_FOUND)
                return

        length_header = self.headers.get("Content-Length", "0")
        try:
            content_length = int(length_header)
        except ValueError:
            self._write_json({"error": "invalid content-length"}, status=HTTPStatus.BAD_REQUEST)
            return

        if content_length <= 0:
            self._write_json({"error": "json body is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._write_json({"error": "request body must be valid utf-8 json"}, status=HTTPStatus.BAD_REQUEST)
            return

        if not isinstance(payload, dict):
            self._write_json({"error": "request body must be a json object"}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/v1/submit_proposal":
            try:
                result = submit_proposal(self.config.repo_root, payload)
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json({"operation": "submit_proposal", "result": result}, status=HTTPStatus.CREATED)
            return

        try:
            result = review_proposal_status(self.config.repo_root, payload)
        except FileNotFoundError:
            self._write_json({"error": "proposal not found"}, status=HTTPStatus.NOT_FOUND)
            return
        except ValueError as exc:
            self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._write_json({"operation": "review_proposal_status", "result": result}, status=HTTPStatus.OK)


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
