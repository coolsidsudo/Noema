from __future__ import annotations

import argparse
from pathlib import Path

from .bounded_loop import execute_bounded_substitution_loop
from .build_projection import build_workspace_projection
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
