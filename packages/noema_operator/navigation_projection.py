from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from .handoffs import OperatorHandoff, OperatorHandoffRegistry, build_operator_handoffs, handoff_id_for_route_id
from .navigation import (
    DIAGNOSTIC_CODE_ORDER,
    HANDOFF_KINDS,
    NAVIGATION_PAGE_TARGETS,
    ROUTE_KINDS,
    TARGET_KINDS,
    NavigationBundle,
    NavigationDiagnostic,
    NavigationRegistry,
    NavigationTarget,
    OperatorRoute,
    build_navigation_bundle,
)

MISSING_VALUE = "—"
GENERATED_NAV_TARGET_IDS = {target_id for target_id, *_ in NAVIGATION_PAGE_TARGETS}


def _format_table_cell(value: object) -> str:
    if value is None:
        return MISSING_VALUE
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return MISSING_VALUE
    return text.replace("|", "\\|")


def _table_row(values: Iterable[object]) -> str:
    return "| " + " | ".join(_format_table_cell(value) for value in values) + " |"


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _target_path(target: NavigationTarget, registry: NavigationRegistry) -> Path:
    return registry.repo_root / target.repo_relative_path


def _target_link(target_id: str, *, page_path: Path, registry: NavigationRegistry, label: str | None = None) -> str:
    target = registry.lookup(target_id)
    if target is None:
        return f"`{_format_table_cell(target_id)}`"
    relative = os.path.relpath(_target_path(target, registry).resolve(), start=page_path.parent.resolve())
    return f"[{_format_table_cell(label or target_id)}]({Path(relative).as_posix()})"


def _target_display_path(target: NavigationTarget) -> str:
    if target.target_kind == "source_record":
        return target.repo_relative_path
    return target.projection_relative_path or target.workspace_relative_path or target.repo_relative_path


def _append_table(lines: list[str], headers: list[str], rows: list[list[object]], empty_text: str) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append(_table_row(row))
    if not rows:
        lines.extend(["", empty_text])


def _targets_by_kind(registry: NavigationRegistry, kind: str) -> list[NavigationTarget]:
    return [target for target in registry.targets if target.target_kind == kind]


def _routes_by_kind(routes: Iterable[OperatorRoute], kind: str) -> list[OperatorRoute]:
    return [route for route in routes if route.route_kind == kind]


def _handoffs_by_kind(handoffs: Iterable[OperatorHandoff], kind: str) -> list[OperatorHandoff]:
    return [handoff for handoff in handoffs if handoff.handoff_kind == kind]


def _join(values: Iterable[str], *, limit: int | None = None) -> str:
    items = [value for value in values if value]
    if limit is not None and len(items) > limit:
        return ", ".join(items[:limit]) + f" (+{len(items) - limit} more)"
    return ", ".join(items) if items else MISSING_VALUE


def _render_index(*, path: Path, bundle: NavigationBundle, handoffs: OperatorHandoffRegistry) -> None:
    registry = bundle.registry
    routes = bundle.routes.routes
    blocked_handoffs = [handoff for handoff in handoffs.handoffs if handoff.blockers or handoff.warnings]
    packet_routes = [route for route in routes if route.route_kind == "packet_review"]
    lines = [
        "# Operator Navigation Workbench",
        "",
        "Navigation targets, routes, and handoffs are derived read-only guidance. They do not approve, reject, apply, mutate, or publish Noema records.",
        "",
        "## Workspace",
        f"- Workspace id: `{_format_table_cell(registry.workspace_id)}`",
        f"- Workspace path: `{_format_table_cell(registry.workspace_root.name)}`",
        "",
        "## Navigation Summary",
        f"- Targets: `{len(registry.targets)}`",
        f"- Routes: `{len(routes)}`",
        f"- Handoffs: `{len(handoffs.handoffs)}`",
        f"- Packet review routes: `{len(packet_routes)}`",
        f"- Attention handoffs: `{len(blocked_handoffs)}`",
        "",
        "## Primary Routes",
    ]
    primary_rows = [
        [route.route_id, route.title, _target_link(route.entry_target_id, page_path=path, registry=registry), route.purpose]
        for route in routes
        if route.route_kind in {"workspace_overview", "proposal_triage", "ready_review"}
    ]
    _append_table(lines, ["route_id", "title", "entry_target", "purpose"], primary_rows, "_No primary routes found._")
    lines.extend(["", "## Attention Routes"])
    attention_rows = [
        [route.route_id, route.title, _target_link(route.entry_target_id, page_path=path, registry=registry), route.attention_summary]
        for route in routes
        if route.route_kind in {"blocked_review", "accepted_apply_audit", "recovery_audit"}
    ]
    _append_table(lines, ["route_id", "title", "entry_target", "attention_summary"], attention_rows, "_No attention routes found._")
    lines.extend(["", "## Handoff Summary"])
    handoff_rows = [[handoff.handoff_kind, sum(1 for item in handoffs.handoffs if item.handoff_kind == handoff.handoff_kind)] for handoff in handoffs.handoffs]
    seen: set[str] = set()
    compact_handoff_rows: list[list[object]] = []
    for kind, count in handoff_rows:
        if kind in seen:
            continue
        seen.add(kind)
        compact_handoff_rows.append([kind, count])
    _append_table(lines, ["handoff_kind", "count"], compact_handoff_rows, "_No handoffs found._")
    lines.extend(
        [
            "",
            "## Navigation Links",
            "- [Navigation Targets](./targets.md)",
            "- [Operator Routes](./routes.md)",
            "- [Operator Handoffs](./handoffs.md)",
            "- [Local Open Helpers](./open-commands.md)",
            "- [Machine-readable Manifest](./manifest.json)",
        ]
    )
    _write_markdown(path, lines)


def _target_rows(targets: Iterable[NavigationTarget], *, page_path: Path, registry: NavigationRegistry) -> list[list[object]]:
    rows: list[list[object]] = []
    for target in targets:
        rows.append([
            target.target_id,
            target.target_kind,
            target.title,
            _target_link(target.target_id, page_path=page_path, registry=registry, label=_target_display_path(target)),
            target.description,
        ])
    return rows


def _render_targets(*, path: Path, registry: NavigationRegistry) -> None:
    lines = ["# Navigation Targets", ""]
    sections = (
        ("## Operator Pages", _targets_by_kind(registry, "operator_page"), "_No operator page targets found._"),
        ("## Review Pages", _targets_by_kind(registry, "review_page"), "_No review page targets found._"),
        ("## Review Packets", _targets_by_kind(registry, "review_packet"), "_No review packet targets found._"),
        ("## Source Records", _targets_by_kind(registry, "source_record"), "_No source record targets found._"),
        ("## Navigation Pages", [target for target in registry.targets if target.target_kind in {"navigation_page", "navigation_manifest"}], "_No navigation page targets found._"),
    )
    for heading, targets, empty in sections:
        lines.extend([heading, ""])
        _append_table(lines, ["target_id", "kind", "title", "path", "description"], _target_rows(targets, page_path=path, registry=registry), empty)
        lines.append("")
    _write_markdown(path, lines)


def _route_rows(routes: Iterable[OperatorRoute], *, page_path: Path, registry: NavigationRegistry) -> list[list[object]]:
    rows: list[list[object]] = []
    for route in routes:
        rows.append([
            route.route_id,
            route.route_kind,
            route.title,
            _target_link(route.entry_target_id, page_path=page_path, registry=registry),
            len(route.ordered_target_ids),
            handoff_id_for_route_id(route.route_id),
            route.purpose,
        ])
    return rows


def _render_routes(*, path: Path, bundle: NavigationBundle, handoffs: OperatorHandoffRegistry) -> None:
    routes = list(bundle.routes.routes)
    lines = [
        "# Operator Routes",
        "",
        "Routes are deterministic operator workflow guidance and do not perform policy decisions.",
        "",
        "## Route Summary",
    ]
    summary_rows = [[kind, sum(1 for route in routes if route.route_kind == kind)] for kind in ROUTE_KINDS]
    _append_table(lines, ["route_kind", "count"], summary_rows, "_No routes found._")
    sections = (
        ("## Workspace Routes", [route for route in routes if route.route_kind == "workspace_overview"], "_No workspace routes found._"),
        ("## Review Routes", [route for route in routes if route.route_kind in {"proposal_triage", "blocked_review", "ready_review", "accepted_apply_audit", "recovery_audit"}], "_No review routes found._"),
        ("## Packet Review Routes", _routes_by_kind(routes, "packet_review"), "_No packet review routes found._"),
        ("## Source Inspection Routes", [], "_No source inspection routes generated in this tranche._"),
    )
    for heading, route_group, empty in sections:
        lines.extend(["", heading, ""])
        _append_table(lines, ["route_id", "kind", "title", "entry_target", "target_count", "handoff", "purpose"], _route_rows(route_group, page_path=path, registry=bundle.registry), empty)
    _write_markdown(path, lines)


def _handoff_rows(handoffs: Iterable[OperatorHandoff], *, page_path: Path, registry: NavigationRegistry) -> list[list[object]]:
    rows: list[list[object]] = []
    for handoff in handoffs:
        rows.append([
            handoff.handoff_id,
            handoff.handoff_kind,
            _target_link(handoff.primary_target_id, page_path=page_path, registry=registry),
            handoff.route_id,
            _join(handoff.related_target_ids, limit=4),
            _join(handoff.next_steps, limit=2),
        ])
    return rows


def _render_handoffs(*, path: Path, registry: NavigationRegistry, handoffs: OperatorHandoffRegistry) -> None:
    handoff_list = list(handoffs.handoffs)
    lines = [
        "# Operator Handoffs",
        "",
        "Handoffs are derived guidance bundles and are not durable authority records.",
        "",
        "## Handoff Summary",
    ]
    summary_rows = [[kind, sum(1 for handoff in handoff_list if handoff.handoff_kind == kind)] for kind in HANDOFF_KINDS]
    _append_table(lines, ["handoff_kind", "count"], summary_rows, "_No handoffs found._")
    sections = (
        ("## Workspace Handoffs", _handoffs_by_kind(handoff_list, "workspace_overview"), "_No workspace handoffs found._"),
        ("## Review Handoffs", [handoff for handoff in handoff_list if handoff.handoff_kind in {"proposal_triage", "blocked_review", "ready_review", "accepted_apply_audit", "recovery_audit"}], "_No review handoffs found._"),
        ("## Packet Handoffs", _handoffs_by_kind(handoff_list, "packet_review"), "_No packet handoffs found._"),
        ("## Source Handoffs", [], "_No source handoffs generated in this tranche._"),
    )
    for heading, handoff_group, empty in sections:
        lines.extend(["", heading, ""])
        _append_table(lines, ["handoff_id", "kind", "primary_target", "route", "related_targets", "next_steps"], _handoff_rows(handoff_group, page_path=path, registry=registry), empty)
    _write_markdown(path, lines)


def _render_open_commands(*, path: Path, registry: NavigationRegistry) -> None:
    try:
        workspace_arg = registry.workspace_root.resolve().relative_to(registry.repo_root.resolve()).as_posix()
    except ValueError:
        workspace_arg = registry.workspace_id
    lines = [
        "# Local Open Helpers",
        "",
        "These commands resolve or print local navigation references by default. Opening a file is not approval, rejection, apply, or publication.",
        "",
        "## Resolve Targets",
        "```bash",
        f"python -m packages.noema_operator.cli resolve-navigation-target --repo-root . --workspace {workspace_arg} --target review:queue --format repo-relative-path",
        "```",
        "",
        "## Resolve Routes",
        "```bash",
        f"python -m packages.noema_operator.cli show-operator-route --repo-root . --workspace {workspace_arg} --route route:proposal-triage",
        "```",
        "",
        "## Resolve Handoffs",
        "```bash",
        f"python -m packages.noema_operator.cli build-operator-handoff --repo-root . --workspace {workspace_arg} --route route:proposal-triage --format text",
        "```",
        "",
        "## File Paths",
        "Use `--format repo-relative-path` for source records and generated projection pages.",
        "",
        "## File URIs",
        "Use `--format file-uri` to print a local `file://` URI without launching any application.",
        "",
        "## Optional Open Commands",
        "```bash",
        f"python -m packages.noema_operator.cli open-navigation-target --repo-root . --workspace {workspace_arg} --target review:queue --mode file --print",
        f"python -m packages.noema_operator.cli open-navigation-target --repo-root . --workspace {workspace_arg} --target review:queue --mode file --execute",
        "```",
        "",
        "## Safety Notes",
        "- `--execute` is explicit and optional.",
        "- Execution uses tokenized local commands and never `shell=True`.",
        "- Obsidian URI mode is intentionally not implemented in 2C v1.",
        "- No network URLs or arbitrary shell commands are accepted.",
    ]
    _write_markdown(path, lines)


def _diagnostic_to_manifest(diagnostic: NavigationDiagnostic) -> dict[str, object]:
    return {
        "code": diagnostic.code,
        "handoff_id": diagnostic.handoff_id,
        "message": diagnostic.message,
        "references": list(diagnostic.references),
        "route_id": diagnostic.route_id,
        "target_id": diagnostic.target_id,
    }


def _target_to_manifest(target: NavigationTarget, registry: NavigationRegistry) -> dict[str, object]:
    exists = target.exists or target.target_id in GENERATED_NAV_TARGET_IDS or _target_path(target, registry).exists()
    payload: dict[str, object] = {
        "description": target.description,
        "exists": exists,
        "repo_relative_path": target.repo_relative_path,
        "tags": list(target.tags),
        "target_id": target.target_id,
        "target_kind": target.target_kind,
        "title": target.title,
    }
    if target.workspace_relative_path:
        payload["workspace_relative_path"] = target.workspace_relative_path
    if target.projection_relative_path:
        payload["projection_relative_path"] = target.projection_relative_path
    if target.source_record_id:
        payload["source_record_id"] = target.source_record_id
    if target.source_object_class:
        payload["source_object_class"] = target.source_object_class
    if target.proposal_id:
        payload["proposal_id"] = target.proposal_id
    if target.packet_filename:
        payload["packet_filename"] = target.packet_filename
    return payload


def _route_to_manifest(route: OperatorRoute) -> dict[str, object]:
    return {
        "attention_summary": route.attention_summary,
        "checklist_items": list(route.checklist_items),
        "diagnostics": [_diagnostic_to_manifest(diagnostic) for diagnostic in route.diagnostics],
        "entry_target_id": route.entry_target_id,
        "ordered_target_ids": list(route.ordered_target_ids),
        "purpose": route.purpose,
        "recommended_next_target_ids": list(route.recommended_next_target_ids),
        "related_packet_ids": list(route.related_packet_ids),
        "related_source_record_ids": list(route.related_source_record_ids),
        "route_id": route.route_id,
        "route_kind": route.route_kind,
        "title": route.title,
    }


def _handoff_to_manifest(handoff: OperatorHandoff) -> dict[str, object]:
    return {
        "blockers": list(handoff.blockers),
        "diagnostics": [_diagnostic_to_manifest(diagnostic) for diagnostic in handoff.diagnostics],
        "handoff_id": handoff.handoff_id,
        "handoff_kind": handoff.handoff_kind,
        "next_steps": list(handoff.next_steps),
        "primary_target_id": handoff.primary_target_id,
        "related_packet_ids": list(handoff.related_packet_ids),
        "related_route_ids": list(handoff.related_route_ids),
        "related_source_record_ids": list(handoff.related_source_record_ids),
        "related_target_ids": list(handoff.related_target_ids),
        "route_id": handoff.route_id,
        "summary": handoff.summary,
        "title": handoff.title,
        "warnings": list(handoff.warnings),
    }


def _manifest(bundle: NavigationBundle, handoffs: OperatorHandoffRegistry) -> dict[str, object]:
    diagnostics = [*bundle.registry.diagnostics, *bundle.routes.diagnostics, *handoffs.diagnostics]
    handoff_ids = {handoff.handoff_id for handoff in handoffs.handoffs}
    for route in bundle.routes.routes:
        expected_handoff_id = handoff_id_for_route_id(route.route_id)
        if expected_handoff_id not in handoff_ids:
            diagnostics.append(
                NavigationDiagnostic(
                    code="unresolved_handoff_reference",
                    message=f"Route has no corresponding handoff: {expected_handoff_id}",
                    route_id=route.route_id,
                    handoff_id=expected_handoff_id,
                )
            )
    code_order = {code: index for index, code in enumerate(DIAGNOSTIC_CODE_ORDER)}
    diagnostics = sorted(
        diagnostics,
        key=lambda item: (code_order.get(item.code, len(code_order)), item.target_id, item.route_id, item.handoff_id, item.message, item.references),
    )
    return {
        "authority": "derived_non_authoritative",
        "diagnostics": [_diagnostic_to_manifest(diagnostic) for diagnostic in diagnostics],
        "handoffs": [_handoff_to_manifest(handoff) for handoff in handoffs.handoffs],
        "routes": [_route_to_manifest(route) for route in bundle.routes.routes],
        "schema_version": "operator-navigation-workbench-v1",
        "targets": [_target_to_manifest(target, bundle.registry) for target in bundle.registry.targets],
        "workspace_id": bundle.registry.workspace_id,
    }


def render_navigation_workbench(*, repo_root: Path, workspace: str, operator_projection_root: Path) -> tuple[Path, ...]:
    bundle = build_navigation_bundle(repo_root=repo_root, workspace=workspace)
    handoffs = build_operator_handoffs(bundle)
    navigation_root = operator_projection_root / "navigation"
    index_path = navigation_root / "index.md"
    targets_path = navigation_root / "targets.md"
    routes_path = navigation_root / "routes.md"
    handoffs_path = navigation_root / "handoffs.md"
    open_commands_path = navigation_root / "open-commands.md"
    manifest_path = navigation_root / "manifest.json"

    _render_index(path=index_path, bundle=bundle, handoffs=handoffs)
    _render_targets(path=targets_path, registry=bundle.registry)
    _render_routes(path=routes_path, bundle=bundle, handoffs=handoffs)
    _render_handoffs(path=handoffs_path, registry=bundle.registry, handoffs=handoffs)
    _render_open_commands(path=open_commands_path, registry=bundle.registry)
    _write_json(manifest_path, _manifest(bundle, handoffs))
    return (index_path, targets_path, routes_path, handoffs_path, open_commands_path, manifest_path)
