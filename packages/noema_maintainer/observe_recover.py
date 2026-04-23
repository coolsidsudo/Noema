from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .scan import ObjectRecord, parse_frontmatter, scan_repository

OBSERVABILITY_VERSION = "phase8-slice6-v1"
DETERMINISTIC_OBSERVED_AT = "2026-04-23T00:00:00Z"


@dataclass(frozen=True)
class OperatorObservabilityResult:
    workspace: str
    proposal_id: str
    report_path: Path


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _record_index(records: list[ObjectRecord], workspace: str, object_class: str) -> dict[str, ObjectRecord]:
    indexed: dict[str, ObjectRecord] = {}
    for record in records:
        if record.object_class != object_class:
            continue
        if str(record.metadata.get("workspace", "")).strip() != workspace:
            continue
        record_id = str(record.metadata.get("id", "")).strip()
        if record_id:
            indexed[record_id] = record
    return indexed


def _load_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8")) or {}


def execute_operator_observability_snapshot(
    *,
    repo_root: Path,
    workspaces_root: Path,
    workspace: str,
    proposal_id: str,
    output_root: Path,
) -> OperatorObservabilityResult:
    records = scan_repository(repo_root)
    proposals_by_id = _record_index(records, workspace, "proposals")
    structured_by_id = _record_index(records, workspace, "structured")
    raw_by_id = _record_index(records, workspace, "raw")

    if proposal_id not in proposals_by_id:
        raise ValueError(f"Proposal '{proposal_id}' was not found in workspace '{workspace}'.")

    proposal = proposals_by_id[proposal_id]
    results_in_ids = _as_id_list(proposal.metadata.get("results_in"))
    target_ids = _as_id_list(proposal.metadata.get("target_ids"))
    supporting_raw_ids = _as_id_list(proposal.metadata.get("supporting_raw_ids"))

    apply_report_path = workspaces_root / workspace / "projection" / "maintainer-apply-run" / "apply-report.json"
    if not apply_report_path.exists():
        raise ValueError(
            "No governed apply report was found for this workspace; run --execute-governed-apply before snapshotting observability."
        )

    apply_report = json.loads(apply_report_path.read_text(encoding="utf-8"))
    if str(apply_report.get("proposal_id", "")).strip() != proposal_id:
        raise ValueError(
            f"Governed apply report proposal_id '{apply_report.get('proposal_id', '')}' does not match requested '{proposal_id}'."
        )

    outputs = apply_report.get("outputs", {})
    apply_log_rel = str(outputs.get("apply_log", "")).strip()
    compensation_rel = str(outputs.get("compensation", "")).strip()
    apply_log_path = repo_root / apply_log_rel if apply_log_rel else Path()
    compensation_path = repo_root / compensation_rel if compensation_rel else Path()

    apply_log_meta = _load_frontmatter(apply_log_path)
    compensation_meta = _load_frontmatter(compensation_path)

    structured_lineage: list[dict[str, Any]] = []
    unresolved_result_ids: list[str] = []
    for result_id in results_in_ids:
        record = structured_by_id.get(result_id)
        if record is None:
            unresolved_result_ids.append(result_id)
            continue
        text = record.path.read_text(encoding="utf-8")
        structured_lineage.append(
            {
                "id": result_id,
                "path": str(record.path.relative_to(repo_root)),
                "reconciliation_note_present": "## Reconciliation Note" in text,
                "supports": _as_id_list(record.metadata.get("supports")),
            }
        )

    resolved_raw_sources: list[dict[str, str]] = []
    unresolved_raw_ids: list[str] = []
    for raw_id in supporting_raw_ids:
        raw_record = raw_by_id.get(raw_id)
        if raw_record is None:
            unresolved_raw_ids.append(raw_id)
            continue
        resolved_raw_sources.append(
            {
                "id": raw_id,
                "path": str(raw_record.path.relative_to(repo_root)),
            }
        )

    report = {
        "slice": "phase-8-slice-6",
        "version": OBSERVABILITY_VERSION,
        "observed_at": DETERMINISTIC_OBSERVED_AT,
        "workspace": workspace,
        "proposal_id": proposal_id,
        "lineage": {
            "source_context": {
                "supporting_raw_ids": supporting_raw_ids,
                "resolved_raw_sources": resolved_raw_sources,
                "unresolved_raw_ids": unresolved_raw_ids,
            },
            "proposal": {
                "id": proposal_id,
                "status": str(proposal.metadata.get("status", "")).strip(),
                "path": str(proposal.path.relative_to(repo_root)),
                "target_ids": target_ids,
                "results_in": results_in_ids,
                "approved_policy_gate_ticket": str(proposal.metadata.get("approved_policy_gate_ticket", "")).strip(),
                "allow_direct_canonical_apply": bool(proposal.metadata.get("allow_direct_canonical_apply", False)),
            },
            "apply_reconciliation": {
                "apply_id": str(apply_report.get("apply_id", "")).strip(),
                "apply_report_path": str(apply_report_path.relative_to(repo_root)),
                "apply_log_path": apply_log_rel,
                "apply_log_event_type": str(apply_log_meta.get("event_type", "")).strip(),
                "records_event_for": _as_id_list(apply_log_meta.get("records_event_for")),
                "reconciled_structured_paths": apply_report.get("reconciled_structured_paths", []),
                "structured_lineage": structured_lineage,
                "unresolved_result_ids": unresolved_result_ids,
            },
            "compensation_recovery": {
                "compensation_path": compensation_rel,
                "compensation_status": str(compensation_meta.get("status", "")).strip(),
                "proposal_state": str(compensation_meta.get("proposal_state", "")).strip(),
                "operation_type": str(compensation_meta.get("operation_type", "")).strip(),
                "source_apply_id": str(compensation_meta.get("source_apply_id", "")).strip(),
                "recovery_boundary": "correction-must-flow-through-proposal-review-before-any-additional-canonical-direct-mutation",
                "operator_recovery_steps": [
                    "Inspect apply_report, apply log, and reconciled structured objects.",
                    "If correction is needed, evolve emitted compensation artifact as a governed proposal.",
                    "Complete review/acceptance before any further policy-gated apply execution.",
                ],
            },
        },
        "guards": {
            "proposal_review_apply_boundaries_preserved": True,
            "recovery_path_operator_facing": True,
            "hidden_canonical_mutation_enabled": False,
            "platform_sprawl_introduced": False,
        },
    }

    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / f"{proposal_id}-observability-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return OperatorObservabilityResult(
        workspace=workspace,
        proposal_id=proposal_id,
        report_path=report_path,
    )
