from __future__ import annotations

from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit
from uuid import uuid4

from .core import (
    get_object_by_id,
    get_proposal_status,
    get_traceability_links,
    list_objects,
    submit_proposal,
)

MAX_REQUEST_BODY_BYTES = 1024 * 1024

ERROR_STATUS_BY_CATEGORY = {
    "invalid_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "conflict": 409,
    "limit_exceeded": 400,
    "rate_limited": 429,
    "temporarily_unavailable": 503,
    "internal_error": 500,
}

ADAPTER_ERROR_STATUS_BY_CODE = {
    "ROUTE_NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "REQUEST_BODY_TOO_LARGE": 400,
}

GET_OBJECT_QUERY_PARAMS = {"include_content", "include_relationship_hints"}
LIST_OBJECTS_QUERY_PARAMS = {
    "class",
    "status",
    "ids",
    "title_contains",
    "limit",
    "cursor",
    "sort_by",
    "sort_order",
    "include_content",
    "include_relationship_hints",
}
PROPOSAL_STATUS_QUERY_PARAMS = {"include_review_history", "include_result_links", "include_log_refs"}
TRACEABILITY_BODY_FIELDS = {"seed_ids", "link_types", "direction", "limit", "include_node_summaries"}
PROPOSAL_BODY_FIELDS = {
    "id",
    "created_by",
    "status",
    "target_ids",
    "title",
    "summary",
    "rationale",
    "intended_effect",
    "supporting_raw_ids",
    "requested_reviewers",
    "results_in",
    "created_at",
}
PROPOSAL_STRING_FIELDS = {
    "id",
    "created_by",
    "status",
    "title",
    "summary",
    "rationale",
    "intended_effect",
    "created_at",
}
PROPOSAL_LIST_FIELDS = {"target_ids", "supporting_raw_ids", "requested_reviewers", "results_in"}


class AdapterRequestError(Exception):
    def __init__(
        self,
        *,
        operation: str,
        category: str,
        code: str,
        message: str,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.category = category
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details


def _timestamp_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request_id() -> str:
    return f"req_{uuid4().hex}"


def _adapter_error(
    *,
    operation: str,
    category: str,
    code: str,
    message: str,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error_payload: dict[str, Any] = {
        "category": category,
        "code": code,
        "message": message,
        "retryable": retryable,
    }
    if details is not None:
        error_payload["details"] = details

    return {
        "ok": False,
        "operation": operation,
        "request_id": _request_id(),
        "timestamp": _timestamp_now(),
        "error": error_payload,
    }


def _http_status_for_envelope(envelope: dict[str, Any], *, success_status: int = 200) -> int:
    if envelope.get("ok") is True:
        return success_status
    error = envelope.get("error")
    if not isinstance(error, dict):
        return 500
    category = error.get("category")
    if not isinstance(category, str):
        return 500
    return ERROR_STATUS_BY_CATEGORY.get(category, 500)


def _http_status_for_adapter_error(envelope: dict[str, Any]) -> int:
    error = envelope.get("error")
    if not isinstance(error, dict):
        return 500
    code = error.get("code")
    if isinstance(code, str) and code in ADAPTER_ERROR_STATUS_BY_CODE:
        return ADAPTER_ERROR_STATUS_BY_CODE[code]
    category = error.get("category")
    if isinstance(category, str):
        return ERROR_STATUS_BY_CATEGORY.get(category, 500)
    return 500


def _decode_path_variable(raw_value: str, *, name: str, operation: str) -> str:
    decoded = unquote(raw_value)
    if decoded == "" or "/" in decoded or "\\" in decoded:
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_PATH_PARAMETER",
            message="Invalid path parameter.",
            details={"parameter": name, "value": decoded},
        )
    return decoded


def _strict_query(
    raw_query: str,
    *,
    allowed_params: set[str],
    operation: str,
) -> dict[str, str]:
    parsed = parse_qs(raw_query, keep_blank_values=True)
    result: dict[str, str] = {}
    for key, values in parsed.items():
        if key not in allowed_params:
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="UNKNOWN_QUERY_PARAMETER",
                message="Unknown query parameter.",
                details={"parameter": key},
            )
        if len(values) != 1:
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="DUPLICATE_QUERY_PARAMETER",
                message="Duplicate query parameter.",
                details={"parameter": key},
            )
        result[key] = values[0]
    return result


def _optional_string(params: dict[str, str], name: str, *, operation: str) -> str | None:
    if name not in params:
        return None
    value = params[name]
    if value == "":
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="EMPTY_QUERY_PARAMETER",
            message="Empty query parameter.",
            details={"parameter": name},
        )
    return value


def _optional_bool(params: dict[str, str], name: str, *, operation: str, default: bool) -> bool:
    if name not in params:
        return default
    value = params[name]
    if value == "true":
        return True
    if value == "false":
        return False
    raise AdapterRequestError(
        operation=operation,
        category="invalid_request",
        code="INVALID_BOOLEAN",
        message="Invalid boolean query parameter.",
        details={"parameter": name, "value": value},
    )


def _optional_int(params: dict[str, str], name: str, *, operation: str) -> int | None:
    if name not in params:
        return None
    value = params[name]
    try:
        return int(value, 10)
    except ValueError:
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_INTEGER",
            message="Invalid integer query parameter.",
            details={"parameter": name, "value": value},
        ) from None


def _optional_ids(params: dict[str, str], name: str, *, operation: str) -> list[str] | None:
    if name not in params:
        return None
    value = params[name]
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(token == "" for token in tokens):
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="EMPTY_QUERY_PARAMETER",
            message="Empty query parameter.",
            details={"parameter": name, "value": value},
        )
    return tokens


def _ensure_list_of_strings(value: Any, *, field: str, operation: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_BODY_FIELD",
            message="Invalid JSON body field.",
            details={"field": field, "expected": "list[str]"},
        )


def _ensure_string(value: Any, *, field: str, operation: str) -> None:
    if not isinstance(value, str):
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_BODY_FIELD",
            message="Invalid JSON body field.",
            details={"field": field, "expected": "str"},
        )


def _ensure_integer(value: Any, *, field: str, operation: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_BODY_FIELD",
            message="Invalid JSON body field.",
            details={"field": field, "expected": "int"},
        )


def _ensure_bool(value: Any, *, field: str, operation: str) -> None:
    if not isinstance(value, bool):
        raise AdapterRequestError(
            operation=operation,
            category="invalid_request",
            code="INVALID_BODY_FIELD",
            message="Invalid JSON body field.",
            details={"field": field, "expected": "bool"},
        )


class NoemaHTTPRequestHandler(BaseHTTPRequestHandler):
    server: ThreadingHTTPServer

    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")

    def do_PUT(self) -> None:
        self._method_not_allowed()

    def do_PATCH(self) -> None:
        self._method_not_allowed()

    def do_DELETE(self) -> None:
        self._method_not_allowed()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _repo_root(self) -> Path:
        return self.server.noema_repo_root  # type: ignore[attr-defined]

    def _handle(self, method: str) -> None:
        parsed = urlsplit(self.path)
        raw_path = parsed.path
        segments = raw_path.split("/")
        internal_error_operation = "http_request"
        try:
            route_name = self._recognized_route_name(segments)
            if route_name is not None:
                internal_error_operation = route_name
            if route_name is not None:
                allowed = self._allowed_methods_for_route(route_name)
                if method not in allowed:
                    self._send_adapter_error(
                        operation="http_request",
                        category="invalid_request",
                        code="METHOD_NOT_ALLOWED",
                        message="Method not allowed.",
                        details={"method": method, "path": raw_path},
                        status=405,
                        allow=allowed,
                    )
                    return

            if method == "GET":
                envelope, status = self._handle_get(segments, parsed.query, raw_path)
            elif method == "POST":
                envelope, status = self._handle_post(segments, parsed.query, raw_path)
            else:
                self._method_not_allowed()
                return
            self._send_json(status, envelope)
        except AdapterRequestError as exc:
            envelope = _adapter_error(
                operation=exc.operation,
                category=exc.category,
                code=exc.code,
                message=exc.message,
                retryable=exc.retryable,
                details=exc.details,
            )
            self._send_json(_http_status_for_adapter_error(envelope), envelope)
        except Exception:
            self._send_internal_error(operation=internal_error_operation)

    def _handle_get(self, segments: list[str], raw_query: str, raw_path: str) -> tuple[dict[str, Any], int]:
        if self._is_get_object_route(segments):
            operation = "get_object_by_id"
            workspace = _decode_path_variable(segments[3], name="workspace", operation=operation)
            object_id = _decode_path_variable(segments[5], name="id", operation=operation)
            query = _strict_query(raw_query, allowed_params=GET_OBJECT_QUERY_PARAMS, operation=operation)
            envelope = get_object_by_id(
                repo_root=self._repo_root(),
                workspace=workspace,
                id=object_id,
                include_content=_optional_bool(query, "include_content", operation=operation, default=True),
                include_relationship_hints=_optional_bool(
                    query,
                    "include_relationship_hints",
                    operation=operation,
                    default=False,
                ),
            )
            return envelope, _http_status_for_envelope(envelope)

        if self._is_list_objects_route(segments):
            operation = "list_objects"
            workspace = _decode_path_variable(segments[3], name="workspace", operation=operation)
            query = _strict_query(raw_query, allowed_params=LIST_OBJECTS_QUERY_PARAMS, operation=operation)
            envelope = list_objects(
                repo_root=self._repo_root(),
                workspace=workspace,
                object_class=_optional_string(query, "class", operation=operation),
                status=_optional_string(query, "status", operation=operation),
                ids=_optional_ids(query, "ids", operation=operation),
                title_contains=_optional_string(query, "title_contains", operation=operation),
                limit=_optional_int(query, "limit", operation=operation),
                cursor=_optional_string(query, "cursor", operation=operation),
                sort_by=_optional_string(query, "sort_by", operation=operation) or "id",
                sort_order=_optional_string(query, "sort_order", operation=operation) or "asc",
                include_content=_optional_bool(query, "include_content", operation=operation, default=False),
                include_relationship_hints=_optional_bool(
                    query,
                    "include_relationship_hints",
                    operation=operation,
                    default=False,
                ),
            )
            return envelope, _http_status_for_envelope(envelope)

        if self._is_get_proposal_status_route(segments):
            operation = "get_proposal_status"
            workspace = _decode_path_variable(segments[3], name="workspace", operation=operation)
            proposal_id = _decode_path_variable(segments[5], name="proposal_id", operation=operation)
            query = _strict_query(raw_query, allowed_params=PROPOSAL_STATUS_QUERY_PARAMS, operation=operation)
            envelope = get_proposal_status(
                repo_root=self._repo_root(),
                workspace=workspace,
                proposal_id=proposal_id,
                include_review_history=_optional_bool(
                    query,
                    "include_review_history",
                    operation=operation,
                    default=False,
                ),
                include_result_links=_optional_bool(query, "include_result_links", operation=operation, default=True),
                include_log_refs=_optional_bool(query, "include_log_refs", operation=operation, default=True),
            )
            return envelope, _http_status_for_envelope(envelope)

        return self._route_not_found(raw_path)

    def _handle_post(self, segments: list[str], raw_query: str, raw_path: str) -> tuple[dict[str, Any], int]:
        if self._is_traceability_route(segments):
            operation = "get_traceability_links"
            workspace = _decode_path_variable(segments[3], name="workspace", operation=operation)
            _strict_query(raw_query, allowed_params=set(), operation=operation)
            body = self._read_json_object(operation=operation)
            self._validate_body_fields(body, allowed_fields=TRACEABILITY_BODY_FIELDS, operation=operation)
            if "seed_ids" not in body:
                raise AdapterRequestError(
                    operation=operation,
                    category="invalid_request",
                    code="INVALID_BODY_FIELD",
                    message="Invalid JSON body field.",
                    details={"field": "seed_ids", "expected": "list[str]"},
                )
            _ensure_list_of_strings(body["seed_ids"], field="seed_ids", operation=operation)
            if "link_types" in body:
                _ensure_list_of_strings(body["link_types"], field="link_types", operation=operation)
            if "direction" in body:
                _ensure_string(body["direction"], field="direction", operation=operation)
            if "limit" in body:
                _ensure_integer(body["limit"], field="limit", operation=operation)
            if "include_node_summaries" in body:
                _ensure_bool(body["include_node_summaries"], field="include_node_summaries", operation=operation)

            envelope = get_traceability_links(
                repo_root=self._repo_root(),
                workspace=workspace,
                seed_ids=body["seed_ids"],
                link_types=body.get("link_types"),
                direction=body.get("direction", "both"),
                limit=body.get("limit"),
                include_node_summaries=body.get("include_node_summaries", False),
            )
            return envelope, _http_status_for_envelope(envelope)

        if self._is_submit_proposal_route(segments):
            operation = "submit_proposal"
            workspace = _decode_path_variable(segments[3], name="workspace", operation=operation)
            _strict_query(raw_query, allowed_params=set(), operation=operation)
            body = self._read_json_object(operation=operation)
            self._validate_body_fields(body, allowed_fields=PROPOSAL_BODY_FIELDS, operation=operation)
            for field in PROPOSAL_STRING_FIELDS:
                if field in body:
                    _ensure_string(body[field], field=field, operation=operation)
            for field in PROPOSAL_LIST_FIELDS:
                if field in body:
                    _ensure_list_of_strings(body[field], field=field, operation=operation)

            envelope = submit_proposal(repo_root=self._repo_root(), workspace=workspace, proposal=body)
            return envelope, _http_status_for_envelope(envelope, success_status=201)

        return self._route_not_found(raw_path)

    def _read_json_object(self, *, operation: str) -> dict[str, Any]:
        raw_content_length = self.headers.get("Content-Length")
        if raw_content_length is None:
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="MISSING_CONTENT_LENGTH",
                message="Missing Content-Length header.",
            )
        try:
            content_length = int(raw_content_length, 10)
        except ValueError:
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="INVALID_CONTENT_LENGTH",
                message="Invalid Content-Length header.",
                details={"value": raw_content_length},
            ) from None
        if content_length < 0:
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="INVALID_CONTENT_LENGTH",
                message="Invalid Content-Length header.",
                details={"value": raw_content_length},
            )
        if content_length > MAX_REQUEST_BODY_BYTES:
            raise AdapterRequestError(
                operation=operation,
                category="limit_exceeded",
                code="REQUEST_BODY_TOO_LARGE",
                message="Request body too large.",
                details={"max_bytes": MAX_REQUEST_BODY_BYTES, "content_length": content_length},
            )

        raw_body = self.rfile.read(content_length)
        try:
            parsed = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="INVALID_JSON",
                message="Malformed JSON body.",
            ) from None
        if not isinstance(parsed, dict):
            raise AdapterRequestError(
                operation=operation,
                category="invalid_request",
                code="INVALID_JSON_OBJECT",
                message="JSON body must be an object.",
            )
        return parsed

    def _validate_body_fields(self, body: dict[str, Any], *, allowed_fields: set[str], operation: str) -> None:
        for field in body:
            if field not in allowed_fields:
                raise AdapterRequestError(
                    operation=operation,
                    category="invalid_request",
                    code="UNKNOWN_BODY_FIELD",
                    message="Unknown JSON body field.",
                    details={"field": field},
                )

    def _method_not_allowed(self) -> None:
        parsed = urlsplit(self.path)
        route_name = self._recognized_route_name(parsed.path.split("/"))
        allow = self._allowed_methods_for_route(route_name) if route_name is not None else None
        self._send_adapter_error(
            operation="http_request",
            category="invalid_request",
            code="METHOD_NOT_ALLOWED",
            message="Method not allowed.",
            details={"method": self.command, "path": parsed.path},
            status=405,
            allow=allow,
        )

    def _send_adapter_error(
        self,
        *,
        operation: str,
        category: str,
        code: str,
        message: str,
        details: dict[str, Any],
        status: int,
        allow: set[str] | None = None,
    ) -> None:
        envelope = _adapter_error(
            operation=operation,
            category=category,
            code=code,
            message=message,
            retryable=False,
            details=details,
        )
        headers = {"Allow": ", ".join(sorted(allow))} if allow else None
        self._send_json(status, envelope, extra_headers=headers)

    def _send_json(self, status: int, payload: dict[str, Any], extra_headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_internal_error(self, *, operation: str) -> None:
        envelope = _adapter_error(
            operation=operation,
            category="internal_error",
            code="INTERNAL_ERROR",
            message="Internal server error.",
            retryable=False,
        )
        self._send_json(500, envelope)

    def _route_not_found(self, raw_path: str) -> tuple[dict[str, Any], int]:
        envelope = _adapter_error(
            operation="http_request",
            category="not_found",
            code="ROUTE_NOT_FOUND",
            message="Route not found.",
            retryable=False,
            details={"method": self.command, "path": raw_path},
        )
        return envelope, 404

    def _recognized_route_name(self, segments: list[str]) -> str | None:
        if self._is_get_object_route(segments):
            return "get_object_by_id"
        if self._is_list_objects_route(segments):
            return "list_objects"
        if self._is_traceability_route(segments):
            return "get_traceability_links"
        if self._is_submit_proposal_route(segments):
            return "submit_proposal"
        if self._is_get_proposal_status_route(segments):
            return "get_proposal_status"
        return None

    def _allowed_methods_for_route(self, route_name: str | None) -> set[str] | None:
        if route_name in {"get_object_by_id", "list_objects", "get_proposal_status"}:
            return {"GET"}
        if route_name in {"get_traceability_links", "submit_proposal"}:
            return {"POST"}
        return None

    def _is_get_object_route(self, segments: list[str]) -> bool:
        return len(segments) == 6 and segments[:3] == ["", "v1", "workspaces"] and segments[4] == "objects"

    def _is_list_objects_route(self, segments: list[str]) -> bool:
        return len(segments) == 5 and segments[:3] == ["", "v1", "workspaces"] and segments[4] == "objects"

    def _is_traceability_route(self, segments: list[str]) -> bool:
        return len(segments) == 5 and segments[:3] == ["", "v1", "workspaces"] and segments[4] == "traceability-links:query"

    def _is_submit_proposal_route(self, segments: list[str]) -> bool:
        return len(segments) == 5 and segments[:3] == ["", "v1", "workspaces"] and segments[4] == "proposals"

    def _is_get_proposal_status_route(self, segments: list[str]) -> bool:
        return (
            len(segments) == 7
            and segments[:3] == ["", "v1", "workspaces"]
            and segments[4] == "proposals"
            and segments[6] == "status"
        )


def create_http_server(*, repo_root: Path, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), NoemaHTTPRequestHandler)
    server.noema_repo_root = Path(repo_root)  # type: ignore[attr-defined]
    return server


def run_http_server(*, repo_root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    server = create_http_server(repo_root=repo_root, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
