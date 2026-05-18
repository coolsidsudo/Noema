from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .adapter import emit_manifest, get_tool_spec, invoke_request, invoke_tool, list_tools, make_error_envelope
from .contract import CATEGORIES, SIDE_EFFECT_CLASSES, AdapterValidationError


def _json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _print_table(headers: list[str], rows: list[list[object]]) -> None:
    print("\t".join(headers))
    for row in rows:
        print("\t".join(str(item) for item in row))


def _parse_json_object(raw: str, *, label: str) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, make_error_envelope(
            tool=None,
            code="invalid_argument_value",
            message=f"Malformed JSON in {label}.",
            details={"line": exc.lineno, "column": exc.colno},
        )
    if not isinstance(value, dict):
        return None, make_error_envelope(
            tool=None,
            code="invalid_argument_type",
            message=f"{label} must decode to a JSON object.",
            details={"expected": "object"},
        )
    return value, None


def _describe_text(spec) -> str:
    lines = [
        f"Tool: {spec.name}",
        f"Title: {spec.title}",
        f"Category: {spec.category}",
        f"Side effect: {spec.side_effect_class}",
        f"Backed by: {spec.backed_by}",
        f"Description: {spec.description}",
        "Arguments:",
    ]
    for argument in spec.input_arguments:
        suffix = "required" if argument.required else "optional"
        lines.append(f"- {argument.name}: {argument.argument_type} ({suffix})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and invoke the local Noema external adapter tool contract.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-tools", help="List stable external adapter tools.")
    list_parser.add_argument("--category", choices=CATEGORIES)
    list_parser.add_argument("--side-effect", choices=SIDE_EFFECT_CLASSES)
    list_parser.add_argument("--format", choices=("table", "json"), default="table")

    describe_parser = subparsers.add_parser("describe-tool", help="Describe one external adapter tool.")
    describe_parser.add_argument("--tool", required=True)
    describe_parser.add_argument("--format", choices=("text", "json"), default="text")

    manifest_parser = subparsers.add_parser("emit-manifest", help="Emit deterministic external tool manifest.")
    manifest_parser.add_argument("--format", choices=("json",), default="json")

    invoke_parser = subparsers.add_parser("invoke-tool", help="Invoke one external adapter tool.")
    invoke_group = invoke_parser.add_mutually_exclusive_group(required=True)
    invoke_group.add_argument("--request-json")
    invoke_group.add_argument("--tool")
    invoke_parser.add_argument("--args-json")

    args = parser.parse_args(argv)

    if args.command == "list-tools":
        tools = [tool for tool in list_tools() if (not args.category or tool.category == args.category) and (not args.side_effect or tool.side_effect_class == args.side_effect)]
        if args.format == "json":
            print(_json([tool.to_dict() for tool in tools]))
        else:
            _print_table(
                ["name", "category", "side_effect_class", "description"],
                [[tool.name, tool.category, tool.side_effect_class, tool.description] for tool in tools],
            )
        return 0

    if args.command == "describe-tool":
        try:
            spec = get_tool_spec(args.tool)
        except AdapterValidationError as exc:
            print(f"[noema-external-adapter] error: {exc.message}", file=sys.stderr)
            return 2
        print(_json(spec.to_dict()) if args.format == "json" else _describe_text(spec))
        return 0

    if args.command == "emit-manifest":
        print(_json(emit_manifest()))
        return 0

    if args.command == "invoke-tool":
        if args.request_json is not None:
            request, error = _parse_json_object(args.request_json, label="--request-json")
            envelope = error if error is not None else invoke_request(request or {})
        else:
            if args.args_json is None:
                envelope = make_error_envelope(
                    tool=args.tool,
                    code="missing_required_argument",
                    message="--args-json is required when --tool is supplied.",
                    details={"argument": "--args-json"},
                )
            else:
                parsed_args, error = _parse_json_object(args.args_json, label="--args-json")
                envelope = error if error is not None else invoke_tool(args.tool, parsed_args or {})
        print(_json(envelope))
        return 0 if envelope.get("ok") is True else 2

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
