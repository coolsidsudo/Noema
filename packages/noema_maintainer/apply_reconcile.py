from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .bounded_loop import _write_markdown
from .scan import ObjectRecord, scan_repository

DETERMINISTIC_APPLY_TIMESTAMP = "2026-04-23T00:00:00Z"
APPLY_VERSION = "phase8-slice5-v1"


@dataclass(frozen=True)
class GovernedApplyResult:
    apply_id: str
    workspace: str
    proposal_id: str
    reconciled_structured_paths: list[Path]
    apply_log_path: Path
    compensation_path: Path
    report_path: Path


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _is_explicit_true(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _find_accepted_proposal(records: list[ObjectRecord], workspace: str, proposal_id: str) -> ObjectRecord:
    matches = [
        record
        for record in records
        if record.object_class == "proposals"
        and str(record.metadata.get("workspace", "")) == workspace
        and str(record.metadata.get("id", "")).strip() == proposal_id
    ]
    if not matches:
        raise ValueError(f"Proposal '{proposal_id}' was not found in workspace '{workspace}'.")
    proposal = matches[0]
    if str(proposal.metadata.get("status", "")).strip() != "accepted":
        raise ValueError(f"Proposal '{proposal_id}' is not accepted; apply requires status 'accepted'.")
    return proposal


def _structured_targets_by_id(records: list[ObjectRecord], workspace: str) -> dict[str, ObjectRecord]:
    targets: dict[str, ObjectRecord] = {}
    for record in records:
        if record.object_class != "structured":
            continue
        if str(record.metadata.get("workspace", "")) != workspace:
            continue
        object_id = str(record.metadata.get("id", "")).strip()
        if object_id:
            targets[object_id] = record
    return targets


def _append_reconciliation_note(path: Path, proposal_id: str, policy_gate_ticket: str) -> None:
    existing = path.read_text(encoding="utf-8").rstrip() + "\n"
    note = (
        "\n## Reconciliation Note\n"
        f"- Applied by governed maintainer apply path (`{APPLY_VERSION}`).\n"
        f"- Source accepted proposal: `{proposal_id}`.\n"
        f"- Policy gate ticket: `{policy_gate_ticket}`.\n"
        f"- Applied at: `{DETERMINISTIC_APPLY_TIMESTAMP}`.\n"
        "- Compensation posture: use emitted compensation artifact before additional direct mutation.\n"
    )
    path.write_text(existing + note, encoding="utf-8")


def execute_policy_governed_apply(
    *,
    repo_root: Path,
    workspace: str,
    proposal_id: str,
    policy_gate_ticket: str,
    output_root: Path,
) -> GovernedApplyResult:
    records = scan_repository(repo_root)
    proposal = _find_accepted_proposal(records, workspace, proposal_id)

    expected_ticket = str(proposal.metadata.get("approved_policy_gate_ticket", "")).strip()
    if expected_ticket == "":
        raise ValueError(
            f"Accepted proposal '{proposal_id}' is missing approved_policy_gate_ticket metadata required for apply."
        )
    if policy_gate_ticket != expected_ticket:
        raise ValueError(
            f"Policy gate ticket mismatch for proposal '{proposal_id}': provided '{policy_gate_ticket}' does not match required ticket."
        )

    if not _is_explicit_true(proposal.metadata.get("allow_direct_canonical_apply")):
        raise ValueError(
            f"Accepted proposal '{proposal_id}' does not allow direct canonical apply; expected allow_direct_canonical_apply: true."
        )

    result_ids = _as_id_list(proposal.metadata.get("results_in"))
    if not result_ids:
        raise ValueError(f"Accepted proposal '{proposal_id}' is missing results_in targets for reconciliation.")

    structured_by_id = _structured_targets_by_id(records, workspace)
    missing_result_ids = [result_id for result_id in result_ids if result_id not in structured_by_id]
    if missing_result_ids:
        raise ValueError(
            f"Accepted proposal '{proposal_id}' has unresolved results_in structured ids: {', '.join(missing_result_ids)}."
        )

    apply_id = f"apply-{workspace}-{proposal_id}-{APPLY_VERSION}"
    reconciled_paths: list[Path] = []
    for result_id in result_ids:
        target = structured_by_id[result_id]
        _append_reconciliation_note(target.path, proposal_id, policy_gate_ticket)
        reconciled_paths.append(target.path)

    apply_log_path = output_root / "logs" / f"{apply_id}.md"
    compensation_path = output_root / "compensations" / f"{apply_id}-compensation.md"
    report_path = output_root / "apply-report.json"

    log_frontmatter = [
        f"id: {apply_id}",
        "class: logs",
        f"created_at: {DETERMINISTIC_APPLY_TIMESTAMP}",
        f"updated_at: {DETERMINISTIC_APPLY_TIMESTAMP}",
        "created_by: maintainer-agent",
        f"workspace: {workspace}",
        "status: recorded",
        "event_type: apply_reconciliation",
        "event_class: apply_reconciliation",
        f"proposal_id: {proposal_id}",
        f"policy_gate_ticket: {policy_gate_ticket}",
        "canonical_change_mode: policy-gated-direct-apply",
        "compensation_posture: required",
        "records_event_for:",
        f"  - {proposal_id}",
        *[f"  - {result_id}" for result_id in result_ids],
    ]
    _write_markdown(
        apply_log_path,
        log_frontmatter,
        (
            "Policy-governed apply and reconciliation event.\n"
            "This event records canonical structured reconciliation from an accepted proposal under explicit policy gate."
        ),
    )

    compensation_frontmatter = [
        f"id: {apply_id}-compensation",
        "class: proposals",
        f"created_at: {DETERMINISTIC_APPLY_TIMESTAMP}",
        f"updated_at: {DETERMINISTIC_APPLY_TIMESTAMP}",
        "created_by: maintainer-agent",
        f"workspace: {workspace}",
        "status: draft",
        "proposal_state: compensation-ready",
        f"source_apply_id: {apply_id}",
        "operation_type: compensation",
        "target_ids:",
        *[f"  - {result_id}" for result_id in result_ids],
        "non_goals:",
        "  - hidden-reconciliation-rewrite",
    ]
    _write_markdown(
        compensation_path,
        compensation_frontmatter,
        (
            "Compensation placeholder emitted alongside governed apply.\n"
            "If reconciliation correction is required, promote this artifact through normal proposal/review before re-apply."
        ),
    )

    report = {
        "apply_id": apply_id,
        "slice": "phase-8-slice-5",
        "workspace": workspace,
        "proposal_id": proposal_id,
        "policy_gate_ticket": policy_gate_ticket,
        "deterministic_timestamp": DETERMINISTIC_APPLY_TIMESTAMP,
        "reconciled_structured_paths": [str(path.relative_to(repo_root)) for path in reconciled_paths],
        "outputs": {
            "apply_log": str(apply_log_path.relative_to(repo_root)),
            "compensation": str(compensation_path.relative_to(repo_root)),
            "apply_report": str(report_path.relative_to(repo_root)),
        },
        "guards": {
            "accepted_proposal_precondition_verified": True,
            "policy_gate_precondition_verified": True,
            "proposal_review_apply_boundaries_preserved": True,
            "compensation_posture_emitted": True,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return GovernedApplyResult(
        apply_id=apply_id,
        workspace=workspace,
        proposal_id=proposal_id,
        reconciled_structured_paths=reconciled_paths,
        apply_log_path=apply_log_path,
        compensation_path=compensation_path,
        report_path=report_path,
    )
