from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .scan import ObjectRecord, scan_repository

DETERMINISTIC_TIMESTAMP = "2026-04-22T00:00:00Z"
RUN_VERSION = "phase8-slice4-v1"


@dataclass(frozen=True)
class BoundedLoopResult:
    run_id: str
    workspace: str
    proposal_path: Path
    log_event_path: Path
    report_path: Path


def _as_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return []


def _first_structured_target(records: list[ObjectRecord], workspace: str) -> ObjectRecord:
    structured_records = [
        record
        for record in records
        if record.object_class == "structured" and str(record.metadata.get("workspace", "")) == workspace
    ]
    if not structured_records:
        raise ValueError(f"No structured records found for workspace '{workspace}'.")
    return sorted(structured_records, key=lambda r: (str(r.metadata.get("id", "")), str(r.path)))[0]


def _workspace_raw_ids(records: list[ObjectRecord], workspace: str) -> list[str]:
    raw_ids = {
        str(record.metadata.get("id", "")).strip()
        for record in records
        if record.object_class == "raw" and str(record.metadata.get("workspace", "")) == workspace
    }
    return sorted([raw_id for raw_id in raw_ids if raw_id])


def _write_markdown(path: Path, frontmatter_lines: list[str], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = "\n".join(frontmatter_lines)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


def execute_bounded_substitution_loop(*, repo_root: Path, workspace: str, output_root: Path) -> BoundedLoopResult:
    records = scan_repository(repo_root)
    target_record = _first_structured_target(records, workspace)
    target_id = str(target_record.metadata.get("id", "")).strip()
    if target_id == "":
        raise ValueError("Structured target record is missing required id metadata.")

    support_ids = _as_id_list(target_record.metadata.get("supports"))
    if not support_ids:
        support_ids = _workspace_raw_ids(records, workspace)

    if not support_ids:
        raise ValueError(
            f"No supporting raw ids found for workspace '{workspace}'. At least one raw object is required."
        )

    run_id = f"maintainer-loop-{workspace}-{RUN_VERSION}"
    proposal_id = f"proposal-{workspace}-{RUN_VERSION}"
    event_id = f"event-{workspace}-{RUN_VERSION}"
    log_id = f"log-{workspace}-{RUN_VERSION}"

    proposal_path = output_root / "proposals" / f"{proposal_id}.md"
    log_event_path = output_root / "logs" / f"{log_id}.md"
    report_path = output_root / "run-report.json"

    proposal_frontmatter = [
        f"id: {proposal_id}",
        "class: proposals",
        f"created_at: {DETERMINISTIC_TIMESTAMP}",
        f"updated_at: {DETERMINISTIC_TIMESTAMP}",
        "created_by: maintainer-agent",
        f"workspace: {workspace}",
        "status: under_review",
        f"proposal_id: {proposal_id}",
        "proposal_version: 1",
        "proposal_state: under-review",
        "emitted_by: maintainer-agent",
        "impact_class: moderate",
        "operation_type: update",
        f"change_scope: bounded-maintainer-pass-on-{target_id}",
        "problem_statement: coverage-gap-detected-during-bounded-maintainer-pass",
        "rationale: preserve-proposal-first-canonical-governance",
        "intended_outcome: reviewer-visible-canonical-change-candidate",
        "non_goals:",
        "  - direct-canonical-structured-apply",
        "  - runtime-expansion-beyond-bounded-substitution-path",
        "target_ids:",
        f"  - {target_id}",
        "results_in:",
        f"  - {target_id}",
        "supporting_raw_ids:",
        *[f"  - {support_id}" for support_id in support_ids],
        "authority_posture: proposal-first",
        "apply_mode: proposal-only",
    ]
    proposal_body = (
        "Deterministic Phase 8 Slice 4 bounded maintainer run output.\n"
        "This artifact requests reviewer-governed canonical updates and intentionally avoids direct structured writes."
    )
    _write_markdown(proposal_path, proposal_frontmatter, proposal_body)

    log_frontmatter = [
        f"id: {log_id}",
        "class: logs",
        f"created_at: {DETERMINISTIC_TIMESTAMP}",
        f"updated_at: {DETERMINISTIC_TIMESTAMP}",
        "created_by: maintainer-agent",
        f"workspace: {workspace}",
        "status: recorded",
        "event_type: proposal_lifecycle",
        f"event_id: {event_id}",
        "event_class: proposal_lifecycle",
        "event_version: 1",
        "event_sequence: 1",
        "actor_id: maintainer-agent",
        "actor_type: maintainer-agent",
        f"workspace_ref: {workspace}",
        f"run_id: {run_id}",
        f"occurred_at: {DETERMINISTIC_TIMESTAMP}",
        f"recorded_at: {DETERMINISTIC_TIMESTAMP}",
        "time_source: fixed-deterministic",
        "action_summary: emit-proposal-for-canonical-impacting-structured-update",
        "outcome_status: success",
        f"outcome_notes: emitted-{proposal_id}",
        "correlation_id: phase8-slice4-bounded-maintainer-loop",
        "follow_up_expected: true",
        "affected_objects:",
        f"  - {target_id}",
        f"  - {proposal_id}",
        "related_artifacts:",
        f"  - {proposal_id}",
        "records_event_for:",
        f"  - {proposal_id}",
        f"  - {target_id}",
        "canonical_change_mode: proposal-emitted",
        f"compile_scope: workspace:{workspace}",
    ]
    log_body = (
        "Deterministic maintainer operational trace for bounded substitution path execution.\n"
        "This event records proposal emission and preserves append-oriented visibility."
    )
    _write_markdown(log_event_path, log_frontmatter, log_body)

    report = {
        "run_id": run_id,
        "slice": "phase-8-slice-4",
        "workspace": workspace,
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "target_structured_id": target_id,
        "supporting_raw_ids": support_ids,
        "outputs": {
            "proposal": str(proposal_path.relative_to(repo_root)),
            "log_event": str(log_event_path.relative_to(repo_root)),
            "run_report": str(report_path.relative_to(repo_root)),
        },
        "guards": {
            "proposal_first_canonical_posture": True,
            "direct_canonical_structured_apply_performed": False,
            "append_log_emitted": True,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return BoundedLoopResult(
        run_id=run_id,
        workspace=workspace,
        proposal_path=proposal_path,
        log_event_path=log_event_path,
        report_path=report_path,
    )
