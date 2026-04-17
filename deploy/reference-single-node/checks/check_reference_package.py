#!/usr/bin/env python3
"""Conformance checks for the reference single-node executable machine-facing facade."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEPLOY_ROOT = REPO_ROOT / "deploy" / "reference-single-node"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_executable_surface_substitution() -> None:
    compose = (DEPLOY_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    _assert("agent_surface/server.py" in compose, "noema-agent-surface is not running executable facade code")
    _assert("http.server" not in compose, "static placeholder http.server command still present")
    _assert(":/repo:ro" in compose, "bounded read-only repository mount missing for executable facade")


def check_bounded_operations_contract() -> None:
    contract = json.loads((DEPLOY_ROOT / "contracts" / "agent-surface-baseline.json").read_text(encoding="utf-8"))
    operations = {entry["name"]: entry for entry in contract.get("operations", [])}
    _assert("get_object_by_id" in operations, "get_object_by_id missing from machine-facing contract")
    _assert("list_objects" in operations, "list_objects missing from machine-facing contract")
    _assert("read/query" in operations["get_object_by_id"]["authority"], "get_object_by_id authority is not bounded read/query")
    _assert("read/query" in operations["list_objects"]["authority"], "list_objects authority is not bounded read/query")

    submit = operations.get("submit_proposal")
    _assert(submit is not None, "submit_proposal continuity operation missing")
    _assert("non-executable" in submit["notes"], "submit_proposal is not explicitly deferred/non-executable")


def check_docs_operator_mapping() -> None:
    readme = (DEPLOY_ROOT / "README.md").read_text(encoding="utf-8")
    bootstrap = (DEPLOY_ROOT / "operator" / "bootstrap.md").read_text(encoding="utf-8")

    _assert("minimal executable facade" in readme.lower(), "README does not describe executable machine-facing facade")
    _assert("/v1/list_objects" in bootstrap, "bootstrap guide missing executable list_objects validation")
    _assert("/v1/get_object_by_id" in bootstrap, "bootstrap guide missing executable get_object_by_id validation")


def main() -> int:
    checks = [
        check_executable_surface_substitution,
        check_bounded_operations_contract,
        check_docs_operator_mapping,
    ]

    for check in checks:
        check()
        print(f"PASS: {check.__name__}")

    print("All reference-single-node conformance checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
