from __future__ import annotations

import argparse
from pathlib import Path

from .projections import build_operator_projections


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Noema operator Markdown projections.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-projections", help="Build workspace-local operator projections.")
    build_parser.add_argument("--repo-root", default=".", help="Noema repository root. Defaults to current directory.")
    build_parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace id, repo-relative workspace path, or absolute workspace path.",
    )

    args = parser.parse_args(argv)

    if args.command == "build-projections":
        repo_root = Path(args.repo_root).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            build_parser.error(f"--repo-root must be an existing directory: {repo_root}")
        try:
            result = build_operator_projections(repo_root=repo_root, workspace=args.workspace)
        except ValueError as exc:
            build_parser.error(str(exc))
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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
