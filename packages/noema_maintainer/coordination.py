from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .scan import scan_repository

COORDINATION_VERSION = "phase8-slice7-v1"
DETERMINISTIC_COORDINATION_TIMESTAMP = "2026-04-23T00:00:00Z"


@dataclass(frozen=True)
class CoordinationClaimResult:
    workspace: str
    claim_id: str
    claim_status: str
    claim_path: Path
    state_path: Path
    conflict_ids: list[str]


def _normalize_scope(scope: list[str]) -> list[str]:
    return sorted({item.strip() for item in scope if item.strip()})


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"workspace": "", "version": COORDINATION_VERSION, "claims": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _collect_active_claims(state: dict[str, Any]) -> list[dict[str, Any]]:
    claims = state.get("claims", [])
    if not isinstance(claims, list):
        return []
    return [
        claim
        for claim in claims
        if isinstance(claim, dict) and str(claim.get("status", "")).strip() == "active"
    ]


def _overlap(a: list[str], b: list[str]) -> list[str]:
    return sorted(set(a).intersection(set(b)))


def execute_coordination_claim(
    *,
    repo_root: Path,
    workspace: str,
    maintainer_id: str,
    scope: list[str],
    output_root: Path,
) -> CoordinationClaimResult:
    records = scan_repository(repo_root)
    if not any(
        record.object_class == "structured" and str(record.metadata.get("workspace", "")).strip() == workspace
        for record in records
    ):
        raise ValueError(f"Workspace '{workspace}' has no structured records to coordinate.")

    normalized_scope = _normalize_scope(scope)
    if not normalized_scope:
        raise ValueError("Coordination claim requires at least one non-empty scope target.")

    safe_maintainer_id = maintainer_id.strip()
    if not safe_maintainer_id:
        raise ValueError("Coordination claim requires a non-empty maintainer id.")

    state_path = output_root / "coordination-state.json"
    state = _load_state(state_path)
    if not state.get("workspace"):
        state["workspace"] = workspace
    if str(state.get("workspace", "")).strip() != workspace:
        raise ValueError(
            f"Coordination state workspace mismatch: existing '{state.get('workspace', '')}' vs requested '{workspace}'."
        )

    claim_id = f"claim-{workspace}-{safe_maintainer_id}-{len(state.get('claims', [])) + 1:04d}"
    active_claims = _collect_active_claims(state)
    blocking_claims: list[dict[str, Any]] = []
    for claim in active_claims:
        existing_scope = _normalize_scope([str(item) for item in claim.get("scope", [])])
        overlap = _overlap(normalized_scope, existing_scope)
        if overlap:
            blocking_claims.append(
                {
                    "claim_id": str(claim.get("claim_id", "")).strip(),
                    "maintainer_id": str(claim.get("maintainer_id", "")).strip(),
                    "overlap_scope": overlap,
                }
            )

    status = "blocked_conflict" if blocking_claims else "active"
    attempt = {
        "claim_id": claim_id,
        "workspace": workspace,
        "maintainer_id": safe_maintainer_id,
        "scope": normalized_scope,
        "status": status,
        "created_at": DETERMINISTIC_COORDINATION_TIMESTAMP,
        "coordination_version": COORDINATION_VERSION,
        "conflicts_with": blocking_claims,
        "guards": {
            "proposal_first_posture_preserved": True,
            "policy_gated_apply_posture_preserved": True,
            "direct_canonical_mutation_performed": False,
        },
    }

    claims = state.get("claims", [])
    if not isinstance(claims, list):
        claims = []
    claims.append(attempt)
    state["claims"] = claims
    state["version"] = COORDINATION_VERSION
    _write_json(state_path, state)

    claim_path = output_root / "claims" / f"{claim_id}.json"
    _write_json(claim_path, attempt)

    return CoordinationClaimResult(
        workspace=workspace,
        claim_id=claim_id,
        claim_status=status,
        claim_path=claim_path,
        state_path=state_path,
        conflict_ids=[str(item.get("claim_id", "")).strip() for item in blocking_claims],
    )


def execute_coordination_conflict_check(
    *,
    workspace: str,
    maintainer_id: str,
    scope: list[str],
    output_root: Path,
) -> dict[str, Any]:
    normalized_scope = _normalize_scope(scope)
    state_path = output_root / "coordination-state.json"
    state = _load_state(state_path)
    active_claims = _collect_active_claims(state)

    conflicts = []
    for claim in active_claims:
        overlap = _overlap(normalized_scope, _normalize_scope([str(item) for item in claim.get("scope", [])]))
        if overlap:
            conflicts.append(
                {
                    "claim_id": str(claim.get("claim_id", "")).strip(),
                    "maintainer_id": str(claim.get("maintainer_id", "")).strip(),
                    "overlap_scope": overlap,
                }
            )

    report = {
        "workspace": workspace,
        "requested_by": maintainer_id.strip(),
        "requested_scope": normalized_scope,
        "has_conflict": bool(conflicts),
        "conflicts": conflicts,
        "coordination_version": COORDINATION_VERSION,
        "checked_at": DETERMINISTIC_COORDINATION_TIMESTAMP,
    }
    report_path = output_root / "conflict-check.json"
    _write_json(report_path, report)
    return {"report": report, "report_path": report_path}


def emit_coordination_report(*, workspace: str, output_root: Path) -> Path:
    state_path = output_root / "coordination-state.json"
    state = _load_state(state_path)
    claims = state.get("claims", []) if isinstance(state.get("claims", []), list) else []
    active_claims = [claim for claim in claims if str(claim.get("status", "")).strip() == "active"]
    blocked_claims = [claim for claim in claims if str(claim.get("status", "")).strip() == "blocked_conflict"]

    report = {
        "workspace": workspace,
        "coordination_version": COORDINATION_VERSION,
        "generated_at": DETERMINISTIC_COORDINATION_TIMESTAMP,
        "claims_total": len(claims),
        "active_claims": active_claims,
        "blocked_claims": blocked_claims,
        "guards": {
            "proposal_review_apply_boundaries_preserved": True,
            "policy_gated_apply_posture_preserved": True,
            "hidden_canonical_mutation_enabled": False,
            "distributed_scheduler_introduced": False,
        },
    }
    report_path = output_root / "coordination-report.json"
    _write_json(report_path, report)
    return report_path
