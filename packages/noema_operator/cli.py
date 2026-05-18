from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .handoffs import OperatorHandoff, build_operator_handoffs, handoff_id_for_route_id
from .navigation import (
    HANDOFF_KINDS,
    ROUTE_KINDS,
    TARGET_KINDS,
    NavigationTarget,
    OperatorRoute,
    build_navigation_bundle,
    format_resolution,
)
from .open_helpers import build_open_command, execute_open_command, resolve_open_value
from .projections import build_operator_projections


def _emit_error(message: str) -> int:
    print(f"[noema-operator] error: {message}", file=sys.stderr)
    return 2


def _json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _target_dict(target: NavigationTarget) -> dict[str, object]:
    return {
        "description": target.description,
        "exists": target.exists,
        "packet_filename": target.packet_filename,
        "projection_relative_path": target.projection_relative_path,
        "proposal_id": target.proposal_id,
        "repo_relative_path": target.repo_relative_path,
        "source_object_class": target.source_object_class,
        "source_record_id": target.source_record_id,
        "tags": list(target.tags),
        "target_id": target.target_id,
        "target_kind": target.target_kind,
        "title": target.title,
        "workspace_relative_path": target.workspace_relative_path,
    }


def _route_dict(route: OperatorRoute) -> dict[str, object]:
    return {
        "attention_summary": route.attention_summary,
        "checklist_items": list(route.checklist_items),
        "diagnostics": [diagnostic.__dict__ for diagnostic in route.diagnostics],
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


def _handoff_dict(handoff: OperatorHandoff) -> dict[str, object]:
    return {
        "blockers": list(handoff.blockers),
        "diagnostics": [diagnostic.__dict__ for diagnostic in handoff.diagnostics],
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


def _print_table(headers: list[str], rows: list[list[object]]) -> None:
    print("\t".join(headers))
    for row in rows:
        print("\t".join(str(item) for item in row))


def _load_bundle(repo_root: Path, workspace: str):
    return build_navigation_bundle(repo_root=repo_root, workspace=workspace)


def _load_bundle_and_handoffs(repo_root: Path, workspace: str):
    bundle = _load_bundle(repo_root, workspace)
    return bundle, build_operator_handoffs(bundle)


def _show_route_text(route: OperatorRoute) -> str:
    lines = [
        f"Route: {route.route_id}",
        f"Title: {route.title}",
        f"Purpose: {route.purpose}",
        f"Entry target: {route.entry_target_id}",
        "Ordered targets:",
    ]
    lines.extend(f"- {target_id}" for target_id in route.ordered_target_ids)
    lines.append("Checklist:")
    lines.extend(f"- {item}" for item in route.checklist_items)
    lines.append(f"Related handoff: {handoff_id_for_route_id(route.route_id)}")
    return "\n".join(lines)


def _show_handoff_text(handoff: OperatorHandoff) -> str:
    lines = [
        f"Handoff: {handoff.handoff_id}",
        f"Title: {handoff.title}",
        f"Summary: {handoff.summary}",
        f"Primary target: {handoff.primary_target_id}",
        f"Route: {handoff.route_id}",
        "Next steps:",
    ]
    lines.extend(f"- {step}" for step in handoff.next_steps)
    return "\n".join(lines)


def _show_handoff_markdown(handoff: OperatorHandoff) -> str:
    lines = [
        f"# Operator Handoff: {handoff.handoff_id}",
        "",
        f"- Kind: `{handoff.handoff_kind}`",
        f"- Primary target: `{handoff.primary_target_id}`",
        f"- Route: `{handoff.route_id}`",
        "",
        "## Summary",
        handoff.summary,
        "",
        "## Blockers",
    ]
    lines.extend(f"- {item}" for item in handoff.blockers) if handoff.blockers else lines.append("- _No blockers._")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in handoff.warnings) if handoff.warnings else lines.append("- _No warnings._")
    lines.extend(["", "## Next Steps"])
    lines.extend(f"- {item}" for item in handoff.next_steps)
    return "\n".join(lines)


def _select_handoff(*, bundle, handoffs, target_id: str | None, route_id: str | None, handoff_id: str | None) -> OperatorHandoff | str:
    if handoff_id:
        handoff = handoffs.lookup(handoff_id)
        if handoff is None:
            suggestions = handoffs.suggestions(handoff_id)
            return f"unknown handoff: {handoff_id}" + (f". Suggestions: {', '.join(suggestions)}" if suggestions else "")
        return handoff
    if route_id:
        route = bundle.routes.lookup(route_id)
        if route is None:
            suggestions = bundle.routes.suggestions(route_id)
            return f"unknown route: {route_id}" + (f". Suggestions: {', '.join(suggestions)}" if suggestions else "")
        wanted = handoff_id_for_route_id(route.route_id)
        handoff = handoffs.lookup(wanted)
        if handoff is None:
            return f"unknown handoff: {wanted}"
        return handoff
    if target_id:
        target = bundle.registry.lookup(target_id)
        if target is None:
            suggestions = bundle.registry.suggestions(target_id)
            return f"unknown target: {target_id}" + (f". Suggestions: {', '.join(suggestions)}" if suggestions else "")
        exact = [handoff for handoff in handoffs.handoffs if handoff.primary_target_id == target_id]
        related = [handoff for handoff in handoffs.handoffs if target_id in handoff.related_target_ids]
        matches = exact or related
        if not matches:
            return f"unknown handoff for target: {target_id}"
        return matches[0]
    return "one of --target, --route, or --handoff is required"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and inspect Noema operator Markdown projections.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-projections", help="Build workspace-local operator projections.")
    build_parser.add_argument("--repo-root", default=".", help="Noema repository root. Defaults to current directory.")
    build_parser.add_argument("--workspace", required=True, help="Workspace id, repo-relative workspace path, or absolute workspace path.")

    list_targets = subparsers.add_parser("list-navigation-targets", help="List deterministic navigation targets.")
    list_targets.add_argument("--repo-root", default=".")
    list_targets.add_argument("--workspace", required=True)
    list_targets.add_argument("--kind")
    list_targets.add_argument("--format", choices=("table", "json"), default="table")

    resolve_target = subparsers.add_parser("resolve-navigation-target", help="Resolve one navigation target.")
    resolve_target.add_argument("--repo-root", default=".")
    resolve_target.add_argument("--workspace", required=True)
    resolve_target.add_argument("--target", required=True)
    resolve_target.add_argument("--format", choices=("path", "repo-relative-path", "workspace-relative-path", "file-uri", "markdown-link"), default="repo-relative-path")

    list_routes = subparsers.add_parser("list-operator-routes", help="List deterministic operator routes.")
    list_routes.add_argument("--repo-root", default=".")
    list_routes.add_argument("--workspace", required=True)
    list_routes.add_argument("--kind")
    list_routes.add_argument("--format", choices=("table", "json"), default="table")

    show_route = subparsers.add_parser("show-operator-route", help="Show one operator route.")
    show_route.add_argument("--repo-root", default=".")
    show_route.add_argument("--workspace", required=True)
    show_route.add_argument("--route", required=True)
    show_route.add_argument("--format", choices=("text", "json"), default="text")

    build_handoff = subparsers.add_parser("build-operator-handoff", help="Build and print a deterministic handoff packet.")
    build_handoff.add_argument("--repo-root", default=".")
    build_handoff.add_argument("--workspace", required=True)
    selector = build_handoff.add_mutually_exclusive_group(required=True)
    selector.add_argument("--target")
    selector.add_argument("--route")
    selector.add_argument("--handoff")
    build_handoff.add_argument("--format", choices=("markdown", "json", "text"), default="text")

    open_target = subparsers.add_parser("open-navigation-target", help="Print or execute a local open helper for one target.")
    open_target.add_argument("--repo-root", default=".")
    open_target.add_argument("--workspace", required=True)
    open_target.add_argument("--target", required=True)
    open_target.add_argument("--mode", default="file")
    open_group = open_target.add_mutually_exclusive_group()
    open_group.add_argument("--print", dest="print_only", action="store_true")
    open_group.add_argument("--execute", action="store_true")

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        return _emit_error(f"--repo-root must be an existing directory: {repo_root}")

    try:
        if args.command == "build-projections":
            result = build_operator_projections(repo_root=repo_root, workspace=args.workspace)
            try:
                rendered_projection_root = result.projection_root.relative_to(repo_root)
            except ValueError:
                rendered_projection_root = result.projection_root
            print(
                "[noema-operator] rebuilt operator projections "
                f"for workspace '{result.workspace_id}' at "
                f"'{rendered_projection_root}'"
            )
            return 0

        if args.command == "list-navigation-targets":
            if args.kind and args.kind not in TARGET_KINDS:
                return _emit_error(f"invalid target kind: {args.kind}. Expected one of: {', '.join(TARGET_KINDS)}")
            bundle = _load_bundle(repo_root, args.workspace)
            targets = [target for target in bundle.registry.targets if not args.kind or target.target_kind == args.kind]
            if args.format == "json":
                print(_json([_target_dict(target) for target in targets]))
            else:
                _print_table(["target_id", "kind", "title", "repo_relative_path"], [[target.target_id, target.target_kind, target.title, target.repo_relative_path] for target in targets])
            return 0

        if args.command == "resolve-navigation-target":
            bundle = _load_bundle(repo_root, args.workspace)
            try:
                resolution = bundle.registry.resolve(args.target)
            except ValueError as exc:
                return _emit_error(str(exc))
            print(format_resolution(resolution, args.format))
            return 0

        if args.command == "list-operator-routes":
            if args.kind and args.kind not in ROUTE_KINDS:
                return _emit_error(f"invalid route kind: {args.kind}. Expected one of: {', '.join(ROUTE_KINDS)}")
            bundle = _load_bundle(repo_root, args.workspace)
            routes = [route for route in bundle.routes.routes if not args.kind or route.route_kind == args.kind]
            if args.format == "json":
                print(_json([_route_dict(route) for route in routes]))
            else:
                _print_table(["route_id", "kind", "title", "entry_target"], [[route.route_id, route.route_kind, route.title, route.entry_target_id] for route in routes])
            return 0

        if args.command == "show-operator-route":
            bundle = _load_bundle(repo_root, args.workspace)
            route = bundle.routes.lookup(args.route)
            if route is None:
                suggestions = bundle.routes.suggestions(args.route)
                return _emit_error(f"unknown route: {args.route}" + (f". Suggestions: {', '.join(suggestions)}" if suggestions else ""))
            print(_json(_route_dict(route)) if args.format == "json" else _show_route_text(route))
            return 0

        if args.command == "build-operator-handoff":
            bundle, handoffs = _load_bundle_and_handoffs(repo_root, args.workspace)
            selected = _select_handoff(bundle=bundle, handoffs=handoffs, target_id=args.target, route_id=args.route, handoff_id=args.handoff)
            if isinstance(selected, str):
                return _emit_error(selected)
            if args.format == "json":
                print(_json(_handoff_dict(selected)))
            elif args.format == "markdown":
                print(_show_handoff_markdown(selected))
            else:
                print(_show_handoff_text(selected))
            return 0

        if args.command == "open-navigation-target":
            bundle = _load_bundle(repo_root, args.workspace)
            if args.execute:
                command = build_open_command(bundle.registry, target_id=args.target, mode=args.mode)
                if command.diagnostics:
                    return _emit_error(command.diagnostics[0].message)
                return execute_open_command(command)
            try:
                _resolution, value, diagnostics = resolve_open_value(bundle.registry, target_id=args.target, mode=args.mode)
            except ValueError as exc:
                return _emit_error(str(exc))
            if diagnostics:
                return _emit_error(diagnostics[0].message)
            print(value)
            return 0

    except ValueError as exc:
        return _emit_error(str(exc))

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
