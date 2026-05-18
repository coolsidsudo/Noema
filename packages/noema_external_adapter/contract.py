from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ADAPTER_VERSION = "external-adapter-v1"
MANIFEST_SCHEMA_VERSION = "noema-external-tool-manifest-v1"
AUTHORITY = "bounded_adapter_over_accepted_noema_surfaces"

SIDE_EFFECT_CLASSES = ("read_only", "proposal_write", "generated_projection_write")
CATEGORIES = ("service", "operator", "manifest")

ERROR_CODES = (
    "unknown_tool",
    "missing_required_argument",
    "invalid_argument_type",
    "invalid_argument_value",
    "unexpected_argument",
    "invalid_argument_combination",
    "backing_operation_error",
)

_UNSET = object()


@dataclass(frozen=True)
class ToolArgumentSpec:
    name: str
    argument_type: str
    required: bool
    description: str
    default: Any = _UNSET
    allowed_values: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "argument_type": self.argument_type,
            "required": self.required,
            "description": self.description,
        }
        if self.default is not _UNSET:
            payload["default"] = self.default
        if self.allowed_values:
            payload["allowed_values"] = list(self.allowed_values)
        return payload


@dataclass(frozen=True)
class ToolSpec:
    name: str
    title: str
    description: str
    category: str
    side_effect_class: str
    authority_boundary: str
    input_arguments: tuple[ToolArgumentSpec, ...]
    output_shape: dict[str, object]
    backed_by: str
    errors: tuple[str, ...] = ERROR_CODES

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "side_effect_class": self.side_effect_class,
            "authority_boundary": self.authority_boundary,
            "arguments": [argument.to_dict() for argument in self.input_arguments],
            "output_shape": self.output_shape,
            "backed_by": self.backed_by,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class AdapterValidationError(Exception):
    code: str
    message: str
    details: dict[str, object] = field(default_factory=dict)


class ToolCatalog:
    def __init__(self, tools: tuple[ToolSpec, ...]) -> None:
        sorted_tools = tuple(sorted(tools, key=lambda tool: tool.name))
        names = [tool.name for tool in sorted_tools]
        if len(names) != len(set(names)):
            raise ValueError("tool names must be unique")
        self.version = ADAPTER_VERSION
        self.tools = sorted_tools
        self._by_name = {tool.name: tool for tool in sorted_tools}

    def list_tools(self) -> list[ToolSpec]:
        return list(self.tools)

    def get_tool_spec(self, name: str) -> ToolSpec:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise AdapterValidationError(
                code="unknown_tool",
                message="Unknown external adapter tool.",
                details={"tool": name},
            ) from exc

    def to_manifest_tools(self) -> list[dict[str, object]]:
        return [tool.to_dict() for tool in self.tools]


def arg(
    name: str,
    argument_type: str,
    required: bool,
    description: str,
    *,
    default: Any = _UNSET,
    allowed_values: tuple[str, ...] = (),
) -> ToolArgumentSpec:
    return ToolArgumentSpec(
        name=name,
        argument_type=argument_type,
        required=required,
        description=description,
        default=default,
        allowed_values=allowed_values,
    )


def _base_args() -> tuple[ToolArgumentSpec, ToolArgumentSpec]:
    return (
        arg("repo_root", "string", True, "Local Noema repository root."),
        arg("workspace", "string", True, "Workspace id, repo-relative workspace path, or absolute workspace path accepted by the backing operation."),
    )


AUTHORITY_BOUNDARY = (
    "External adapter over accepted Noema service/operator surfaces only; not a new authority layer."
)


def build_catalog() -> ToolCatalog:
    tools = (
        ToolSpec(
            name="noema.objects.list",
            title="List Noema objects",
            description="List workspace-scoped objects using the accepted service-core list operation.",
            category="service",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("object_class", "string", False, "Optional object class filter."),
                arg("status", "string", False, "Optional status filter."),
                arg("limit", "integer", False, "Optional positive page limit."),
                arg("cursor", "string", False, "Optional service-core cursor."),
                arg("sort_by", "string", False, "Optional service-core sort field."),
                arg("sort_order", "string", False, "Optional sort order.", allowed_values=("asc", "desc")),
                arg("include_content", "boolean", False, "Include Markdown body content when supported.", default=False),
            ),
            output_shape={"data": {"items": "list[object]", "pagination": "object if returned"}},
            backed_by="packages.noema_service.core.list_objects",
        ),
        ToolSpec(
            name="noema.object.get",
            title="Get Noema object",
            description="Fetch one workspace-scoped object by id.",
            category="service",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("object_id", "string", True, "Object id to fetch."),
                arg("include_content", "boolean", False, "Include Markdown body content when supported.", default=False),
            ),
            output_shape={"data": {"object": "object"}},
            backed_by="packages.noema_service.core.get_object_by_id",
        ),
        ToolSpec(
            name="noema.traceability.links",
            title="Get traceability links",
            description="Return traceability links for one object/proposal/log id.",
            category="service",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("object_id", "string", True, "Single seed object/proposal/log id; mapped to seed_ids=[object_id]."),
                arg("direction", "string", False, "Traceability direction.", allowed_values=("outbound", "inbound", "both")),
                arg("link_types", "list[string]", False, "Optional accepted traceability link type filters."),
                arg("limit", "integer", False, "Optional positive link limit."),
            ),
            output_shape={"data": {"seed_ids": "list[string]", "links": "list[link]"}},
            backed_by="packages.noema_service.core.get_traceability_links",
        ),
        ToolSpec(
            name="noema.proposal.status",
            title="Get proposal status",
            description="Return derived proposal status through the accepted service-core operation.",
            category="service",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("proposal_id", "string", True, "Proposal id."),
            ),
            output_shape={"data": "proposal status payload"},
            backed_by="packages.noema_service.core.get_proposal_status",
        ),
        ToolSpec(
            name="noema.proposal.submit",
            title="Submit proposal",
            description="Submit a proposal through the accepted service-core proposal operation.",
            category="service",
            side_effect_class="proposal_write",
            authority_boundary="Proposal creation only through accepted service-core submit_proposal; no approve/reject/apply/canonical mutation.",
            input_arguments=(
                *_base_args(),
                arg("proposal_id", "string", True, "Proposal id to create."),
                arg("title", "string", True, "Proposal title."),
                arg("summary", "string", True, "Proposal summary."),
                arg("rationale", "string", True, "Proposal rationale."),
                arg("intended_effect", "string", True, "Intended effect required by accepted service-core submit_proposal."),
                arg("target_ids", "list[string]", True, "Target object ids."),
                arg("proposed_by", "string", False, "Submitting actor; defaults to external_adapter."),
                arg("evidence_ids", "list[string]", False, "Evidence ids mapped to supporting_raw_ids."),
                arg("status", "string", False, "Initial proposal status.", allowed_values=("draft", "under_review")),
                arg("created_at", "string", False, "Optional deterministic created_at passed through to service-core."),
            ),
            output_shape={"data": "service-core proposal submission payload"},
            backed_by="packages.noema_service.core.submit_proposal",
        ),
        ToolSpec(
            name="noema.operator.projections.build",
            title="Build operator projections",
            description="Build accepted generated operator projections for a workspace.",
            category="operator",
            side_effect_class="generated_projection_write",
            authority_boundary="Generated projection writes only; no source record mutation and no review/apply authority.",
            input_arguments=_base_args(),
            output_shape={"data": {"output_paths": "repo-relative generated paths"}},
            backed_by="packages.noema_operator.projections.build_operator_projections",
        ),
        ToolSpec(
            name="noema.operator.navigation.targets.list",
            title="List navigation targets",
            description="List derived operator navigation targets.",
            category="operator",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("kind", "string", False, "Optional navigation target kind filter."),
            ),
            output_shape={"data": {"targets": "list[target]"}},
            backed_by="packages.noema_operator.navigation.build_navigation_bundle",
        ),
        ToolSpec(
            name="noema.operator.navigation.target.resolve",
            title="Resolve navigation target",
            description="Resolve one navigation target to a stable path/link representation without opening or executing it.",
            category="operator",
            side_effect_class="read_only",
            authority_boundary="Resolution only; no opening, execution, or authority action.",
            input_arguments=(
                *_base_args(),
                arg("target_id", "string", True, "Navigation target id."),
                arg("format", "string", True, "Resolution output format.", allowed_values=("path", "repo-relative-path", "workspace-relative-path", "file-uri", "markdown-link")),
            ),
            output_shape={"data": {"target_id": "string", "target_kind": "string", "format": "string", "value": "string"}},
            backed_by="packages.noema_operator.navigation.NavigationRegistry.resolve",
        ),
        ToolSpec(
            name="noema.operator.routes.list",
            title="List operator routes",
            description="List derived operator routes.",
            category="operator",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("kind", "string", False, "Optional route kind filter."),
            ),
            output_shape={"data": {"routes": "list[route summary]"}},
            backed_by="packages.noema_operator.navigation.build_operator_routes",
        ),
        ToolSpec(
            name="noema.operator.route.show",
            title="Show operator route",
            description="Show one derived operator route with targets and checklist.",
            category="operator",
            side_effect_class="read_only",
            authority_boundary=AUTHORITY_BOUNDARY,
            input_arguments=(
                *_base_args(),
                arg("route_id", "string", True, "Operator route id."),
            ),
            output_shape={"data": {"route": "route"}},
            backed_by="packages.noema_operator.navigation.OperatorRouteRegistry.lookup",
        ),
        ToolSpec(
            name="noema.operator.handoff.build",
            title="Build operator handoff",
            description="Build one derived operator handoff from exactly one target, route, or handoff id.",
            category="operator",
            side_effect_class="read_only",
            authority_boundary="Derived handoff only; no durable authority record and no source mutation.",
            input_arguments=(
                *_base_args(),
                arg("target_id", "string", False, "Select handoff by related target id."),
                arg("route_id", "string", False, "Select handoff by route id."),
                arg("handoff_id", "string", False, "Select handoff by handoff id."),
            ),
            output_shape={"data": {"handoff": "handoff"}},
            backed_by="packages.noema_operator.handoffs.build_operator_handoffs",
        ),
    )
    return ToolCatalog(tools)


CATALOG = build_catalog()
