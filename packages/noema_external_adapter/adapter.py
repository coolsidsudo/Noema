from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable

from packages.noema_operator.handoffs import OperatorHandoff, build_operator_handoffs, handoff_id_for_route_id
from packages.noema_operator.navigation import (
    ROUTE_KINDS,
    TARGET_KINDS,
    NavigationDiagnostic,
    NavigationTarget,
    OperatorRoute,
    build_navigation_bundle,
    format_resolution,
)
from packages.noema_operator.projections import build_operator_projections
from packages.noema_service.core import (
    get_object_by_id,
    get_proposal_status,
    get_traceability_links,
    list_objects as service_list_objects,
    submit_proposal,
)

from .contract import ADAPTER_VERSION, AUTHORITY, CATALOG, AdapterValidationError, ToolSpec
from .manifest import emit_manifest as manifest_emit


def list_tools() -> list[ToolSpec]:
    return CATALOG.list_tools()


def get_tool_spec(name: str) -> ToolSpec:
    return CATALOG.get_tool_spec(name)


def emit_manifest() -> dict[str, object]:
    return manifest_emit()


def make_error_envelope(
    *,
    tool: str | None,
    code: str,
    message: str,
    details: dict[str, object] | None = None,
    side_effect_class: str = "unknown",
) -> dict[str, object]:
    return {
        "ok": False,
        "tool": tool,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": _meta(side_effect_class),
    }


def invoke_request(request: dict[str, object]) -> dict[str, object]:
    if not isinstance(request, dict):
        return make_error_envelope(
            tool=None,
            code="invalid_argument_type",
            message="Request must be a JSON object.",
            details={"expected": "object"},
        )
    tool = request.get("tool")
    if not isinstance(tool, str):
        return make_error_envelope(
            tool=None,
            code="missing_required_argument" if "tool" not in request else "invalid_argument_type",
            message="Request field 'tool' must be a string.",
            details={"field": "tool"},
        )
    arguments = request.get("arguments")
    if not isinstance(arguments, dict):
        return make_error_envelope(
            tool=tool,
            code="missing_required_argument" if "arguments" not in request else "invalid_argument_type",
            message="Request field 'arguments' must be an object.",
            details={"field": "arguments"},
            side_effect_class=_side_effect_for_tool(tool),
        )
    return invoke_tool(tool, arguments)


def invoke_tool(name: str, arguments: dict[str, object]) -> dict[str, object]:
    try:
        spec = CATALOG.get_tool_spec(name)
    except AdapterValidationError as exc:
        return make_error_envelope(tool=name, code=exc.code, message=exc.message, details=exc.details)

    try:
        normalized = _validate_arguments(spec, arguments)
        data = _DISPATCH[name](normalized)
    except AdapterValidationError as exc:
        return make_error_envelope(
            tool=name,
            code=exc.code,
            message=exc.message,
            details=exc.details,
            side_effect_class=spec.side_effect_class,
        )
    except Exception as exc:  # Normalized backing failure; no tracebacks in envelope.
        return make_error_envelope(
            tool=name,
            code="backing_operation_error",
            message="Backing operation failed.",
            details={"message": str(exc), "exception_type": type(exc).__name__},
            side_effect_class=spec.side_effect_class,
        )

    return {
        "ok": True,
        "tool": name,
        "data": data,
        "error": None,
        "meta": _meta(spec.side_effect_class),
    }


def _meta(side_effect_class: str) -> dict[str, object]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "side_effect_class": side_effect_class,
        "authority": AUTHORITY,
    }


def _side_effect_for_tool(tool: str) -> str:
    try:
        return CATALOG.get_tool_spec(tool).side_effect_class
    except AdapterValidationError:
        return "unknown"


def _validate_arguments(spec: ToolSpec, arguments: dict[str, object]) -> dict[str, object]:
    if not isinstance(arguments, dict):
        raise AdapterValidationError(
            code="invalid_argument_type",
            message="Tool arguments must be an object.",
            details={"tool": spec.name, "expected": "object"},
        )

    by_name = {argument.name: argument for argument in spec.input_arguments}
    unexpected = sorted(set(arguments) - set(by_name))
    if unexpected:
        raise AdapterValidationError(
            code="unexpected_argument",
            message="Unexpected tool argument.",
            details={"tool": spec.name, "arguments": unexpected},
        )

    normalized = dict(arguments)
    for name, argument in by_name.items():
        if name not in normalized:
            if argument.required:
                raise AdapterValidationError(
                    code="missing_required_argument",
                    message="Missing required tool argument.",
                    details={"tool": spec.name, "argument": name},
                )
            if "default" in argument.to_dict():
                normalized[name] = argument.default
            continue
        _validate_value(spec.name, name, normalized[name], argument.argument_type)
        if argument.allowed_values and normalized[name] not in argument.allowed_values:
            raise AdapterValidationError(
                code="invalid_argument_value",
                message="Unsupported argument value.",
                details={"tool": spec.name, "argument": name, "value": normalized[name], "allowed_values": list(argument.allowed_values)},
            )

    for limit_name in ("limit",):
        if limit_name in normalized and normalized[limit_name] is not None:
            value = normalized[limit_name]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise AdapterValidationError(
                    code="invalid_argument_value",
                    message="Limit must be a positive integer.",
                    details={"tool": spec.name, "argument": limit_name, "value": value},
                )

    if spec.name == "noema.operator.handoff.build":
        selectors = [name for name in ("target_id", "route_id", "handoff_id") if normalized.get(name)]
        if len(selectors) != 1:
            raise AdapterValidationError(
                code="invalid_argument_combination",
                message="Exactly one of target_id, route_id, or handoff_id must be supplied.",
                details={"tool": spec.name, "supplied_selectors": selectors},
            )

    return normalized


def _validate_value(tool: str, name: str, value: object, expected: str) -> None:
    ok = False
    if expected == "string":
        ok = isinstance(value, str)
    elif expected == "integer":
        ok = isinstance(value, int) and not isinstance(value, bool)
    elif expected == "boolean":
        ok = isinstance(value, bool)
    elif expected == "list[string]":
        ok = isinstance(value, list) and all(isinstance(item, str) for item in value)
    else:
        raise AssertionError(f"unsupported argument type: {expected}")
    if not ok:
        raise AdapterValidationError(
            code="invalid_argument_type",
            message="Invalid argument type.",
            details={"tool": tool, "argument": name, "expected": expected},
        )


def _repo_root(args: dict[str, object]) -> Path:
    return Path(str(args["repo_root"])).expanduser().resolve()


def _service_data(envelope: dict[str, Any]) -> dict[str, object]:
    if envelope.get("ok") is True:
        data = dict(envelope.get("data") or {})
        meta = envelope.get("meta")
        if isinstance(meta, dict) and "pagination" in meta:
            data["pagination"] = meta["pagination"]
        return data
    error = envelope.get("error")
    details: dict[str, object] = {}
    if isinstance(error, dict):
        details = {
            "backing_operation": str(envelope.get("operation", "")),
            "backing_category": str(error.get("category", "")),
            "backing_code": str(error.get("code", "")),
            "backing_message": str(error.get("message", "")),
        }
        if isinstance(error.get("details"), dict):
            details["backing_details"] = error["details"]
    raise AdapterValidationError(
        code="backing_operation_error",
        message="Accepted backing operation returned an error.",
        details=details,
    )


def _repo_relative_or_empty(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return ""


def _diagnostic_dict(diagnostic: NavigationDiagnostic) -> dict[str, object]:
    return {
        "code": diagnostic.code,
        "handoff_id": diagnostic.handoff_id,
        "message": diagnostic.message,
        "references": list(diagnostic.references),
        "route_id": diagnostic.route_id,
        "target_id": diagnostic.target_id,
    }


def _target_dict(target: NavigationTarget) -> dict[str, object]:
    repo_relative_path = "" if Path(target.repo_relative_path).is_absolute() else target.repo_relative_path
    workspace_relative_path = "" if Path(target.workspace_relative_path).is_absolute() else target.workspace_relative_path
    projection_relative_path = "" if Path(target.projection_relative_path).is_absolute() else target.projection_relative_path
    payload: dict[str, object] = {
        "target_id": target.target_id,
        "target_kind": target.target_kind,
        "title": target.title,
        "repo_relative_path": repo_relative_path,
        "description": target.description,
        "exists": target.exists,
        "tags": list(target.tags),
    }
    if projection_relative_path:
        payload["projection_relative_path"] = projection_relative_path
    if workspace_relative_path:
        payload["workspace_relative_path"] = workspace_relative_path
    if target.source_record_id:
        payload["source_record_id"] = target.source_record_id
    if target.source_object_class:
        payload["source_object_class"] = target.source_object_class
    if target.proposal_id:
        payload["proposal_id"] = target.proposal_id
    if target.packet_filename:
        payload["packet_filename"] = target.packet_filename
    return payload


def _route_summary_dict(route: OperatorRoute) -> dict[str, object]:
    return {
        "route_id": route.route_id,
        "route_kind": route.route_kind,
        "title": route.title,
        "entry_target_id": route.entry_target_id,
        "target_count": len(route.ordered_target_ids),
        "purpose": route.purpose,
    }


def _route_dict(route: OperatorRoute) -> dict[str, object]:
    return {
        "route_id": route.route_id,
        "route_kind": route.route_kind,
        "title": route.title,
        "purpose": route.purpose,
        "entry_target_id": route.entry_target_id,
        "ordered_target_ids": list(route.ordered_target_ids),
        "recommended_next_target_ids": list(route.recommended_next_target_ids),
        "related_packet_ids": list(route.related_packet_ids),
        "related_source_record_ids": list(route.related_source_record_ids),
        "attention_summary": route.attention_summary,
        "checklist_items": list(route.checklist_items),
        "diagnostics": [_diagnostic_dict(diagnostic) for diagnostic in route.diagnostics],
    }


def _handoff_dict(handoff: OperatorHandoff) -> dict[str, object]:
    return {
        "handoff_id": handoff.handoff_id,
        "handoff_kind": handoff.handoff_kind,
        "title": handoff.title,
        "primary_target_id": handoff.primary_target_id,
        "route_id": handoff.route_id,
        "related_target_ids": list(handoff.related_target_ids),
        "related_route_ids": list(handoff.related_route_ids),
        "related_packet_ids": list(handoff.related_packet_ids),
        "related_source_record_ids": list(handoff.related_source_record_ids),
        "blockers": list(handoff.blockers),
        "warnings": list(handoff.warnings),
        "next_steps": list(handoff.next_steps),
        "summary": handoff.summary,
        "diagnostics": [_diagnostic_dict(diagnostic) for diagnostic in handoff.diagnostics],
    }


def _invoke_objects_list(args: dict[str, object]) -> dict[str, object]:
    return _service_data(
        service_list_objects(
            repo_root=_repo_root(args),
            workspace=str(args["workspace"]),
            object_class=args.get("object_class") or None,
            status=args.get("status") or None,
            limit=args.get("limit"),
            cursor=args.get("cursor") or None,
            sort_by=str(args.get("sort_by") or "id"),
            sort_order=str(args.get("sort_order") or "asc"),
            include_content=bool(args.get("include_content", False)),
        )
    )


def _invoke_object_get(args: dict[str, object]) -> dict[str, object]:
    return _service_data(
        get_object_by_id(
            repo_root=_repo_root(args),
            workspace=str(args["workspace"]),
            id=str(args["object_id"]),
            include_content=bool(args.get("include_content", False)),
        )
    )


def _invoke_traceability_links(args: dict[str, object]) -> dict[str, object]:
    return _service_data(
        get_traceability_links(
            repo_root=_repo_root(args),
            workspace=str(args["workspace"]),
            seed_ids=[str(args["object_id"])],
            direction=str(args.get("direction") or "both"),
            link_types=args.get("link_types"),
            limit=args.get("limit"),
        )
    )


def _invoke_proposal_status(args: dict[str, object]) -> dict[str, object]:
    return _service_data(
        get_proposal_status(
            repo_root=_repo_root(args),
            workspace=str(args["workspace"]),
            proposal_id=str(args["proposal_id"]),
        )
    )


def _invoke_proposal_submit(args: dict[str, object]) -> dict[str, object]:
    proposal: dict[str, object] = {
        "id": args["proposal_id"],
        "created_by": args.get("proposed_by") or "external_adapter",
        "status": args.get("status") or "draft",
        "target_ids": args["target_ids"],
        "title": args["title"],
        "summary": args["summary"],
        "rationale": args["rationale"],
        "intended_effect": args["intended_effect"],
        "supporting_raw_ids": args.get("evidence_ids") or [],
    }
    if args.get("created_at"):
        proposal["created_at"] = args["created_at"]
    return _service_data(submit_proposal(repo_root=_repo_root(args), workspace=str(args["workspace"]), proposal=proposal))


def _invoke_projections_build(args: dict[str, object]) -> dict[str, object]:
    repo_root = _repo_root(args)
    result = build_operator_projections(repo_root=repo_root, workspace=str(args["workspace"]))
    return {
        "workspace_id": result.workspace_id,
        "workspace_root": _repo_relative_or_empty(result.workspace_root, repo_root),
        "projection_root": _repo_relative_or_empty(result.projection_root, repo_root),
        "output_paths": [_repo_relative_or_empty(path, repo_root) for path in result.output_paths if _repo_relative_or_empty(path, repo_root)],
        "record_count": result.record_count,
    }


def _invoke_targets_list(args: dict[str, object]) -> dict[str, object]:
    kind = args.get("kind") or None
    if kind is not None and kind not in TARGET_KINDS:
        raise AdapterValidationError(
            code="invalid_argument_value",
            message="Unsupported navigation target kind.",
            details={"argument": "kind", "value": kind, "allowed_values": list(TARGET_KINDS)},
        )
    bundle = build_navigation_bundle(repo_root=_repo_root(args), workspace=str(args["workspace"]))
    targets = [target for target in bundle.registry.targets if kind is None or target.target_kind == kind]
    return {"targets": [_target_dict(target) for target in targets]}


def _invoke_target_resolve(args: dict[str, object]) -> dict[str, object]:
    bundle = build_navigation_bundle(repo_root=_repo_root(args), workspace=str(args["workspace"]))
    resolution = bundle.registry.resolve(str(args["target_id"]))
    return {
        "target_id": resolution.target_id,
        "target_kind": resolution.target_kind,
        "format": args["format"],
        "value": format_resolution(resolution, str(args["format"])),
    }


def _invoke_routes_list(args: dict[str, object]) -> dict[str, object]:
    kind = args.get("kind") or None
    if kind is not None and kind not in ROUTE_KINDS:
        raise AdapterValidationError(
            code="invalid_argument_value",
            message="Unsupported operator route kind.",
            details={"argument": "kind", "value": kind, "allowed_values": list(ROUTE_KINDS)},
        )
    bundle = build_navigation_bundle(repo_root=_repo_root(args), workspace=str(args["workspace"]))
    routes = [route for route in bundle.routes.routes if kind is None or route.route_kind == kind]
    return {"routes": [_route_summary_dict(route) for route in routes]}


def _invoke_route_show(args: dict[str, object]) -> dict[str, object]:
    bundle = build_navigation_bundle(repo_root=_repo_root(args), workspace=str(args["workspace"]))
    route = bundle.routes.lookup(str(args["route_id"]))
    if route is None:
        raise AdapterValidationError(
            code="backing_operation_error",
            message="Accepted backing operation returned an error.",
            details={"backing_operation": "OperatorRouteRegistry.lookup", "backing_code": "ROUTE_NOT_FOUND", "backing_message": f"unknown route: {args['route_id']}"},
        )
    return {"route": _route_dict(route)}


def _select_handoff(args: dict[str, object]) -> OperatorHandoff:
    bundle = build_navigation_bundle(repo_root=_repo_root(args), workspace=str(args["workspace"]))
    handoffs = build_operator_handoffs(bundle)
    if args.get("handoff_id"):
        handoff = handoffs.lookup(str(args["handoff_id"]))
        if handoff is None:
            raise ValueError(f"unknown handoff: {args['handoff_id']}")
        return handoff
    if args.get("route_id"):
        route = bundle.routes.lookup(str(args["route_id"]))
        if route is None:
            raise ValueError(f"unknown route: {args['route_id']}")
        handoff = handoffs.lookup(handoff_id_for_route_id(route.route_id))
        if handoff is None:
            raise ValueError(f"unknown handoff for route: {args['route_id']}")
        return handoff
    target_id = str(args["target_id"])
    if bundle.registry.lookup(target_id) is None:
        raise ValueError(f"unknown target: {target_id}")
    exact = [handoff for handoff in handoffs.handoffs if handoff.primary_target_id == target_id]
    related = [handoff for handoff in handoffs.handoffs if target_id in handoff.related_target_ids]
    matches = exact or related
    if not matches:
        raise ValueError(f"unknown handoff for target: {target_id}")
    return matches[0]


def _invoke_handoff_build(args: dict[str, object]) -> dict[str, object]:
    return {"handoff": _handoff_dict(_select_handoff(args))}


_DISPATCH: dict[str, Callable[[dict[str, object]], dict[str, object]]] = {
    "noema.objects.list": _invoke_objects_list,
    "noema.object.get": _invoke_object_get,
    "noema.traceability.links": _invoke_traceability_links,
    "noema.proposal.status": _invoke_proposal_status,
    "noema.proposal.submit": _invoke_proposal_submit,
    "noema.operator.projections.build": _invoke_projections_build,
    "noema.operator.navigation.targets.list": _invoke_targets_list,
    "noema.operator.navigation.target.resolve": _invoke_target_resolve,
    "noema.operator.routes.list": _invoke_routes_list,
    "noema.operator.route.show": _invoke_route_show,
    "noema.operator.handoff.build": _invoke_handoff_build,
}
