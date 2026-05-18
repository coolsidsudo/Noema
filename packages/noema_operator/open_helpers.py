from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import platform
import subprocess

from .navigation import NavigationDiagnostic, NavigationRegistry, NavigationResolution, format_resolution

SUPPORTED_OPEN_MODES = ("file", "file-uri")


@dataclass(frozen=True)
class OpenCommand:
    target_id: str
    mode: str
    value: str
    command: tuple[str, ...]
    diagnostics: tuple[NavigationDiagnostic, ...] = ()


def resolve_open_value(registry: NavigationRegistry, *, target_id: str, mode: str) -> tuple[NavigationResolution | None, str, tuple[NavigationDiagnostic, ...]]:
    if mode not in SUPPORTED_OPEN_MODES:
        diagnostic = NavigationDiagnostic(
            code="unsupported_open_mode",
            message=f"Unsupported open mode: {mode}",
            target_id=target_id,
        )
        return None, "", (diagnostic,)
    resolution = registry.resolve(target_id)
    _ensure_inside_repo(registry=registry, resolution=resolution)
    if mode == "file":
        return resolution, format_resolution(resolution, "path"), ()
    if mode == "file-uri":
        return resolution, format_resolution(resolution, "file-uri"), ()
    raise AssertionError("unreachable")


def build_open_command(registry: NavigationRegistry, *, target_id: str, mode: str) -> OpenCommand:
    resolution, value, diagnostics = resolve_open_value(registry, target_id=target_id, mode=mode)
    if diagnostics:
        return OpenCommand(target_id=target_id, mode=mode, value=value, command=(), diagnostics=diagnostics)
    assert resolution is not None
    system = platform.system().lower()
    if system == "darwin":
        command = ("open", value)
    elif system == "linux":
        command = ("xdg-open", value)
    else:
        return OpenCommand(
            target_id=target_id,
            mode=mode,
            value=value,
            command=(),
            diagnostics=(
                NavigationDiagnostic(
                    code="unsupported_platform_for_execute",
                    message=f"Unsupported platform for execute: {platform.system()}",
                    target_id=target_id,
                ),
            ),
        )
    return OpenCommand(target_id=target_id, mode=mode, value=value, command=command)


def execute_open_command(command: OpenCommand, *, runner=subprocess.run) -> int:
    if command.diagnostics:
        raise ValueError(command.diagnostics[0].message)
    if not command.command:
        raise ValueError("open command is empty")
    completed = runner(list(command.command), check=False)
    return int(getattr(completed, "returncode", 0))


def _ensure_inside_repo(*, registry: NavigationRegistry, resolution: NavigationResolution) -> None:
    repo_root = registry.repo_root.resolve()
    path = resolution.path.resolve()
    try:
        path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"resolved target path is outside repo root: {resolution.target_id}") from exc
