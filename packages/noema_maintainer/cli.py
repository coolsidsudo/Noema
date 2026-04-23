from __future__ import annotations

import argparse
from pathlib import Path

from .apply_reconcile import execute_policy_governed_apply
from .bounded_loop import execute_bounded_substitution_loop
from .build_projection import build_workspace_projection
from .coordination import (
    emit_coordination_report,
    execute_coordination_claim,
    execute_coordination_conflict_check,
)
from .observe_recover import execute_operator_observability_snapshot
from .checks import validate_records
from .scan import scan_repository


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic Noema maintainer scan/build baseline tool.")
    parser.add_argument("--repo-root", default=".", help="Repository root containing raw/ structured/ proposals/ logs/.")
    parser.add_argument(
        "--workspaces-root",
        default="examples/workspaces/sample-research-workspace/workspaces",
        help="Directory containing workspace folders.",
    )
    parser.add_argument("--workspace", help="Optional workspace name to rebuild.")
    parser.add_argument(
        "--execute-bounded-loop",
        action="store_true",
        help="Execute the Phase 8 Slice 4 bounded maintainer loop reference path for --workspace.",
    )
    parser.add_argument(
        "--execute-governed-apply",
        action="store_true",
        help="Execute the Phase 8 Slice 5 policy-governed apply/reconciliation path for an accepted proposal.",
    )
    parser.add_argument("--proposal-id", help="Accepted proposal id for --execute-governed-apply.")
    parser.add_argument("--policy-gate-ticket", help="Policy gate ticket required by accepted proposal metadata.")
    parser.add_argument(
        "--emit-operator-observability-report",
        action="store_true",
        help="Emit the Phase 8 Slice 6 operator observability/recovery report for --workspace and --proposal-id.",
    )
    parser.add_argument(
        "--execute-coordination-claim",
        action="store_true",
        help="Execute the Phase 8 Slice 7 bounded maintainer coordination claim path for --workspace.",
    )
    parser.add_argument(
        "--execute-coordination-conflict-check",
        action="store_true",
        help="Evaluate whether --coordination-scope would conflict with currently active coordination claims.",
    )
    parser.add_argument(
        "--emit-coordination-report",
        action="store_true",
        help="Emit a deterministic coordination report over current claim state for --workspace.",
    )
    parser.add_argument(
        "--coordination-maintainer-id",
        help="Maintainer identity for coordination claim/conflict-check paths.",
    )
    parser.add_argument(
        "--coordination-scope",
        action="append",
        default=[],
        help="Scope target id to claim/check. Repeat this flag to pass multiple targets.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    workspaces_root = (repo_root / args.workspaces_root).resolve()

    records = scan_repository(repo_root)
    issues = validate_records(records)


    if args.execute_bounded_loop:
        if not args.workspace:
            parser.error("--execute-bounded-loop requires --workspace")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-loop-run"
        result = execute_bounded_substitution_loop(
            repo_root=repo_root,
            workspace=args.workspace,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] bounded loop run "
            f"'{result.run_id}' emitted proposal/log bundle at "
            f"'{output_root.relative_to(repo_root)}'"
        )


    if args.execute_governed_apply:
        if not args.workspace:
            parser.error("--execute-governed-apply requires --workspace")
        if not args.proposal_id:
            parser.error("--execute-governed-apply requires --proposal-id")
        if not args.policy_gate_ticket:
            parser.error("--execute-governed-apply requires --policy-gate-ticket")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-apply-run"
        result = execute_policy_governed_apply(
            repo_root=repo_root,
            workspace=args.workspace,
            proposal_id=args.proposal_id,
            policy_gate_ticket=args.policy_gate_ticket,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] governed apply run "
            f"'{result.apply_id}' reconciled {len(result.reconciled_structured_paths)} structured object(s) "
            f"for proposal '{result.proposal_id}'"
        )


    if args.emit_operator_observability_report:
        if not args.workspace:
            parser.error("--emit-operator-observability-report requires --workspace")
        if not args.proposal_id:
            parser.error("--emit-operator-observability-report requires --proposal-id")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-observability-run"
        result = execute_operator_observability_snapshot(
            repo_root=repo_root,
            workspaces_root=workspaces_root,
            workspace=args.workspace,
            proposal_id=args.proposal_id,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] operator observability snapshot "
            f"for proposal '{result.proposal_id}' emitted at "
            f"'{result.report_path.relative_to(repo_root)}'"
        )

    if args.execute_coordination_claim:
        if not args.workspace:
            parser.error("--execute-coordination-claim requires --workspace")
        if not args.coordination_maintainer_id:
            parser.error("--execute-coordination-claim requires --coordination-maintainer-id")
        if not args.coordination_scope:
            parser.error("--execute-coordination-claim requires --coordination-scope")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-coordination-run"
        result = execute_coordination_claim(
            repo_root=repo_root,
            workspace=args.workspace,
            maintainer_id=args.coordination_maintainer_id,
            scope=args.coordination_scope,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] coordination claim "
            f"'{result.claim_id}' is '{result.claim_status}' with {len(result.conflict_ids)} conflict(s)"
        )

    if args.execute_coordination_conflict_check:
        if not args.workspace:
            parser.error("--execute-coordination-conflict-check requires --workspace")
        if not args.coordination_maintainer_id:
            parser.error("--execute-coordination-conflict-check requires --coordination-maintainer-id")
        if not args.coordination_scope:
            parser.error("--execute-coordination-conflict-check requires --coordination-scope")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-coordination-run"
        result = execute_coordination_conflict_check(
            workspace=args.workspace,
            maintainer_id=args.coordination_maintainer_id,
            scope=args.coordination_scope,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] coordination conflict check "
            f"has_conflict={result['report']['has_conflict']} emitted at "
            f"'{result['report_path'].relative_to(repo_root)}'"
        )

    if args.emit_coordination_report:
        if not args.workspace:
            parser.error("--emit-coordination-report requires --workspace")
        output_root = workspaces_root / args.workspace / "projection" / "maintainer-coordination-run"
        report_path = emit_coordination_report(
            workspace=args.workspace,
            output_root=output_root,
        )
        print(
            "[noema-maintainer] coordination report emitted at "
            f"'{report_path.relative_to(repo_root)}'"
        )

    if args.workspace:
        workspaces = [args.workspace]
    else:
        workspaces = sorted([p.name for p in workspaces_root.iterdir() if p.is_dir()])

    for workspace in workspaces:
        report = build_workspace_projection(
            repo_root=repo_root,
            workspace_root=workspaces_root,
            workspace=workspace,
            records=records,
            issues=issues,
        )
        print(f"[noema-maintainer] rebuilt workspace '{workspace}' with {report['record_count']} records")

    print(f"[noema-maintainer] validation issues: {len(issues)}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
