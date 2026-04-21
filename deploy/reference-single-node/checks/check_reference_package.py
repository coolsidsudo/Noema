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
    _assert(
        "/proposals:/repo/proposals" in compose,
        "proposal-lane writable mount missing for bounded submit_proposal continuity",
    )


def check_bounded_operations_contract() -> None:
    contract = json.loads((DEPLOY_ROOT / "contracts" / "agent-surface-baseline.json").read_text(encoding="utf-8"))
    _assert(contract.get("version") == "phase7-slice7-reference", "contract version is not phase7-slice7-reference")
    operations = {entry["name"]: entry for entry in contract.get("operations", [])}
    _assert("get_object_by_id" in operations, "get_object_by_id missing from machine-facing contract")
    _assert("list_objects" in operations, "list_objects missing from machine-facing contract")
    _assert("read/query" in operations["get_object_by_id"]["authority"], "get_object_by_id authority is not bounded read/query")
    _assert("read/query" in operations["list_objects"]["authority"], "list_objects authority is not bounded read/query")

    submit = operations.get("submit_proposal")
    _assert(submit is not None, "submit_proposal continuity operation missing")
    _assert("Executable in this slice" in submit["notes"], "submit_proposal executable continuity note missing")
    _assert("proposal layer only" in submit["authority"], "submit_proposal is not bounded to proposal authority")
    status = operations.get("get_proposal_status")
    _assert(status is not None, "get_proposal_status continuity operation missing")
    _assert("proposal layer" in status["authority"], "get_proposal_status authority is not proposal-layer bounded")
    review = operations.get("review_proposal_status")
    _assert(review is not None, "review_proposal_status continuity operation missing")
    _assert(
        "proposal review continuity" in review["authority"],
        "review_proposal_status authority is not bounded review continuity",
    )
    _assert(
        "append-only continuity log-link records" in review["notes"],
        "review_proposal_status notes missing bounded append-only log-link continuity statement",
    )
    evidence = operations.get("get_proposal_review_evidence")
    _assert(evidence is not None, "get_proposal_review_evidence continuity operation missing")
    _assert(
        "log-link continuity" in evidence["authority"],
        "get_proposal_review_evidence authority is not bounded to evidence/log-link continuity",
    )
    _assert(
        "log-link continuity validation" in evidence["notes"],
        "get_proposal_review_evidence notes missing explicit continuity validation guarantee",
    )


def check_review_evidence_continuity_invariants() -> None:
    server_source = (DEPLOY_ROOT / "agent_surface" / "server.py").read_text(encoding="utf-8")
    _assert("_load_review_log_entries" in server_source, "review evidence log index loader invariant missing")
    _assert(
        "_validate_review_history_entry_shape" in server_source,
        "review history shape validation invariant missing",
    )
    _assert(
        "review continuity event references missing append-only log record" in server_source,
        "missing continuity failure invariant for absent linked log records",
    )
    _assert(
        "review continuity event log_path is out of bounded continuity scope" in server_source,
        "missing bounded continuity scope invariant for log-link path",
    )


def check_docs_operator_mapping() -> None:
    readme = (DEPLOY_ROOT / "README.md").read_text(encoding="utf-8")
    bootstrap = (DEPLOY_ROOT / "operator" / "bootstrap.md").read_text(encoding="utf-8")

    _assert("minimal executable facade" in readme.lower(), "README does not describe executable machine-facing facade")
    _assert("/v1/list_objects" in bootstrap, "bootstrap guide missing executable list_objects validation")
    _assert("/v1/get_object_by_id" in bootstrap, "bootstrap guide missing executable get_object_by_id validation")
    _assert("POST /v1/submit_proposal" in bootstrap, "bootstrap guide missing executable submit_proposal validation")
    _assert("GET /v1/get_proposal_status" in bootstrap, "bootstrap guide missing get_proposal_status validation")
    _assert("POST /v1/review_proposal_status" in bootstrap, "bootstrap guide missing review_proposal_status validation")
    _assert(
        "GET /v1/get_proposal_review_evidence" in bootstrap,
        "bootstrap guide missing get_proposal_review_evidence validation",
    )


def main() -> int:
    checks = [
        check_executable_surface_substitution,
        check_bounded_operations_contract,
        check_review_evidence_continuity_invariants,
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
