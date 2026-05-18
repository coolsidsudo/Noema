from __future__ import annotations

from .contract import ADAPTER_VERSION, AUTHORITY, CATALOG, CATEGORIES, MANIFEST_SCHEMA_VERSION, SIDE_EFFECT_CLASSES

NON_GOALS = (
    "MCP server or MCP protocol transport",
    "HTTP server or HTTP route changes",
    "native web UI",
    "auth, TLS, CORS, or public deployment hardening",
    "Obsidian plugin, API integration, URI generation, or .obsidian config writes",
    "proposal approval, rejection, apply, publish, or canonical object mutation",
    "direct proposal file writing outside accepted service-core submit_proposal",
    "direct log mutation",
    "new service-core semantic operations",
    "broad query, search, RAG, or chat behavior",
    "arbitrary shell execution or open helper execution",
)


def emit_manifest() -> dict[str, object]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "authority": AUTHORITY,
        "tools": CATALOG.to_manifest_tools(),
        "side_effect_classes": list(SIDE_EFFECT_CLASSES),
        "categories": list(CATEGORIES),
        "non_goals": list(NON_GOALS),
        "generated_policy": {
            "no_timestamps": True,
            "deterministic_ordering": True,
            "no_authority_expansion": True,
            "no_absolute_local_paths": True,
        },
    }
