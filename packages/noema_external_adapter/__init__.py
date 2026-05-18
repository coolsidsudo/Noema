"""Noema external adapter contract and deterministic local invocation harness."""

from .adapter import emit_manifest, get_tool_spec, invoke_request, invoke_tool, list_tools
from .contract import ADAPTER_VERSION, AUTHORITY, CATALOG

__all__ = [
    "ADAPTER_VERSION",
    "AUTHORITY",
    "CATALOG",
    "emit_manifest",
    "get_tool_spec",
    "invoke_request",
    "invoke_tool",
    "list_tools",
]
