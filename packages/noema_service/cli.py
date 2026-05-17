from __future__ import annotations

import argparse
from pathlib import Path

from .http_api import create_http_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local Noema service HTTP adapter.")
    parser.add_argument("--repo-root", default=".", help="Noema repository root. Defaults to the current directory.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Defaults to 127.0.0.1.")
    parser.add_argument("--port", default=8765, type=int, help="Port to bind. Defaults to 8765.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        parser.error(f"--repo-root must be an existing directory: {repo_root}")

    server = create_http_server(repo_root=repo_root, host=args.host, port=args.port)
    print(f"Noema HTTP adapter listening on {args.host}:{args.port} with repo_root={repo_root}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
