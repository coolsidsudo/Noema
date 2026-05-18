from __future__ import annotations

import json
from pathlib import Path

import pytest

from packages.noema_external_adapter import emit_manifest, get_tool_spec, invoke_tool, list_tools
from packages.noema_external_adapter.contract import ADAPTER_VERSION, AUTHORITY, SIDE_EFFECT_CLASSES, AdapterValidationError

EXPECTED_TOOLS = [
    "noema.object.get",
    "noema.objects.list",
    "noema.operator.handoff.build",
    "noema.operator.navigation.target.resolve",
    "noema.operator.navigation.targets.list",
    "noema.operator.projections.build",
    "noema.operator.route.show",
    "noema.operator.routes.list",
    "noema.proposal.status",
    "noema.proposal.submit",
    "noema.traceability.links",
]


def test_catalog_contains_exact_stable_tools() -> None:
    tools = list_tools()

    assert [tool.name for tool in tools] == EXPECTED_TOOLS
    assert [tool.name for tool in tools] == sorted(tool.name for tool in tools)
    assert {tool.side_effect_class for tool in tools} == set(SIDE_EFFECT_CLASSES)
    assert {tool.category for tool in tools} == {"service", "operator"}
    assert [tool.name for tool in tools if tool.side_effect_class == "proposal_write"] == ["noema.proposal.submit"]
    assert [tool.name for tool in tools if tool.side_effect_class == "generated_projection_write"] == ["noema.operator.projections.build"]


def test_each_tool_spec_has_required_contract_fields() -> None:
    for tool in list_tools():
        spec = tool.to_dict()
        assert spec["name"]
        assert spec["title"]
        assert spec["description"]
        assert spec["category"] in {"service", "operator"}
        assert spec["side_effect_class"] in set(SIDE_EFFECT_CLASSES)
        assert spec["authority_boundary"]
        assert spec["arguments"]
        assert spec["output_shape"]
        assert spec["backed_by"]
        assert "backing_operation_error" in spec["errors"]


def test_proposal_submit_contract_exposes_intended_effect_explicitly() -> None:
    spec = get_tool_spec("noema.proposal.submit")
    arguments = {argument.name: argument for argument in spec.input_arguments}

    assert arguments["rationale"].required is True
    assert arguments["intended_effect"].required is True
    assert arguments["created_at"].required is False
    assert "summary" in arguments


def test_manifest_is_deterministic_and_bounded() -> None:
    first = emit_manifest()
    second = emit_manifest()
    first_json = json.dumps(first, sort_keys=True)
    second_json = json.dumps(second, sort_keys=True)

    assert first == second
    assert first_json == second_json
    assert first["schema_version"] == "noema-external-tool-manifest-v1"
    assert first["adapter_version"] == ADAPTER_VERSION
    assert first["authority"] == AUTHORITY
    assert first["side_effect_classes"] == ["read_only", "proposal_write", "generated_projection_write"]
    assert first["categories"] == ["service", "operator", "manifest"]
    assert [tool["name"] for tool in first["tools"]] == EXPECTED_TOOLS
    assert first["generated_policy"] == {
        "no_timestamps": True,
        "deterministic_ordering": True,
        "no_authority_expansion": True,
        "no_absolute_local_paths": True,
    }
    assert str(Path.cwd()) not in first_json


def test_unknown_tool_lookup_and_invocation_fail_deterministically() -> None:
    with pytest.raises(AdapterValidationError) as exc:
        get_tool_spec("noema.unknown")
    assert exc.value.code == "unknown_tool"
    assert exc.value.details == {"tool": "noema.unknown"}

    first = invoke_tool("noema.unknown", {})
    second = invoke_tool("noema.unknown", {})
    assert first == second
    assert first["ok"] is False
    assert first["error"]["code"] == "unknown_tool"
    assert first["meta"]["side_effect_class"] == "unknown"
