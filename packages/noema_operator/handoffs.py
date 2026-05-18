from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .navigation import (
    HANDOFF_KINDS,
    NavigationBundle,
    NavigationDiagnostic,
    NavigationRegistry,
    OperatorRoute,
    OperatorRouteRegistry,
    _sort_diagnostics,
    build_navigation_bundle,
)


@dataclass(frozen=True)
class OperatorHandoff:
    handoff_id: str
    handoff_kind: str
    title: str
    workspace_id: str
    primary_target_id: str
    route_id: str
    related_target_ids: tuple[str, ...]
    related_route_ids: tuple[str, ...]
    related_packet_ids: tuple[str, ...]
    related_source_record_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_steps: tuple[str, ...]
    summary: str
    diagnostics: tuple[NavigationDiagnostic, ...] = ()


@dataclass(frozen=True)
class OperatorHandoffRegistry:
    workspace_id: str
    handoffs: tuple[OperatorHandoff, ...]
    diagnostics: tuple[NavigationDiagnostic, ...]
    _handoff_by_id: dict[str, OperatorHandoff] = field(default_factory=dict, repr=False, compare=False)

    def lookup(self, handoff_id: str) -> OperatorHandoff | None:
        return self._handoff_by_id.get(handoff_id)

    def suggestions(self, handoff_id: str, *, limit: int = 3) -> tuple[str, ...]:
        from .navigation import _suggestions

        return _suggestions(handoff_id, [handoff.handoff_id for handoff in self.handoffs], limit=limit)


def handoff_sort_key(handoff: OperatorHandoff) -> tuple[int, str]:
    try:
        kind_index = HANDOFF_KINDS.index(handoff.handoff_kind)
    except ValueError:
        kind_index = len(HANDOFF_KINDS)
    return (kind_index, handoff.handoff_id)


def _handoff_id_for_route(route: OperatorRoute) -> str:
    if route.route_id.startswith("route:packet-review:"):
        return "handoff:packet-review:" + route.route_id.removeprefix("route:packet-review:")
    return "handoff:" + route.route_id.removeprefix("route:")


def handoff_id_for_route_id(route_id: str) -> str:
    if route_id.startswith("route:packet-review:"):
        return "handoff:packet-review:" + route_id.removeprefix("route:packet-review:")
    return "handoff:" + route_id.removeprefix("route:")


def _packet_by_id(bundle: NavigationBundle) -> dict[str, object]:
    return {packet.proposal_id: packet for packet in bundle.registry.packets}


def _unique_ordered(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _diagnostics_for_handoff(
    *,
    handoff_id: str,
    route: OperatorRoute,
    registry: NavigationRegistry,
    routes: OperatorRouteRegistry,
) -> tuple[NavigationDiagnostic, ...]:
    diagnostics: list[NavigationDiagnostic] = []
    if not handoff_id:
        diagnostics.append(
            NavigationDiagnostic(
                code="missing_handoff_reference",
                message="Handoff id is missing.",
                route_id=route.route_id,
            )
        )
    if not route.route_id:
        diagnostics.append(
            NavigationDiagnostic(
                code="missing_route_reference",
                message="Handoff route id is missing.",
                handoff_id=handoff_id,
            )
        )
    elif routes.lookup(route.route_id) is None:
        diagnostics.append(
            NavigationDiagnostic(
                code="unresolved_route_reference",
                message=f"Handoff references unresolved route id: {route.route_id}",
                route_id=route.route_id,
                handoff_id=handoff_id,
            )
        )
    for target_id in (route.entry_target_id, *route.ordered_target_ids, *route.recommended_next_target_ids):
        if not target_id:
            diagnostics.append(
                NavigationDiagnostic(
                    code="missing_target_id",
                    message="Handoff route contains an empty target id reference.",
                    route_id=route.route_id,
                    handoff_id=handoff_id,
                )
            )
        elif target_id in registry.ambiguous_target_ids:
            diagnostics.append(
                NavigationDiagnostic(
                    code="ambiguous_target_id",
                    message=f"Handoff route references ambiguous target id: {target_id}",
                    target_id=target_id,
                    route_id=route.route_id,
                    handoff_id=handoff_id,
                )
            )
        elif registry.lookup(target_id) is None:
            diagnostics.append(
                NavigationDiagnostic(
                    code="unresolved_target_reference",
                    message=f"Handoff route references unresolved target id: {target_id}",
                    target_id=target_id,
                    route_id=route.route_id,
                    handoff_id=handoff_id,
                )
            )
    return _sort_diagnostics((*route.diagnostics, *diagnostics))


def _blockers_and_warnings(route: OperatorRoute, bundle: NavigationBundle) -> tuple[tuple[str, ...], tuple[str, ...]]:
    packets = _packet_by_id(bundle)
    blockers: list[str] = []
    warnings: list[str] = []
    for packet_id in route.related_packet_ids:
        packet = packets.get(packet_id)
        if packet is None:
            warnings.append(f"Related packet not found: {packet_id}.")
            continue
        missing_targets = getattr(packet, "missing_target_ids")
        missing_evidence = getattr(packet, "missing_evidence_ids")
        classifications = getattr(packet, "readiness_classifications")
        recovery_logs = getattr(packet, "recovery_evidence_records")
        apply_logs = getattr(packet, "apply_evidence_records")
        status = getattr(packet, "proposal_status")
        if missing_targets:
            blockers.append(f"{packet_id}: missing target references ({', '.join(missing_targets)}).")
        if missing_evidence:
            blockers.append(f"{packet_id}: missing evidence references ({', '.join(missing_evidence)}).")
        if "unknown_status" in classifications:
            blockers.append(f"{packet_id}: unknown proposal status.")
        if status == "accepted" and not apply_logs:
            warnings.append(f"{packet_id}: accepted proposal has no visible apply evidence.")
        if recovery_logs:
            warnings.append(f"{packet_id}: recovery/failure signal present in related logs.")
    return tuple(sorted(set(blockers))), tuple(sorted(set(warnings)))


def _summary_for(route: OperatorRoute, blockers: tuple[str, ...], warnings: tuple[str, ...]) -> str:
    return (
        f"{route.title}: {len(route.related_packet_ids)} packet(s), "
        f"{len(route.related_source_record_ids)} source record(s), "
        f"{len(blockers)} blocker(s), {len(warnings)} warning(s)."
    )


def _handoff_for_route(route: OperatorRoute, bundle: NavigationBundle) -> OperatorHandoff:
    handoff_id = _handoff_id_for_route(route)
    blockers, warnings = _blockers_and_warnings(route, bundle)
    diagnostics = _diagnostics_for_handoff(
        handoff_id=handoff_id,
        route=route,
        registry=bundle.registry,
        routes=bundle.routes,
    )
    next_steps = _unique_ordered((*blockers, *warnings, *route.checklist_items))
    return OperatorHandoff(
        handoff_id=handoff_id,
        handoff_kind=route.route_kind,
        title=route.title.replace("Route", "Handoff"),
        workspace_id=bundle.registry.workspace_id,
        primary_target_id=route.entry_target_id,
        route_id=route.route_id,
        related_target_ids=_unique_ordered((route.entry_target_id, *route.ordered_target_ids, *route.recommended_next_target_ids)),
        related_route_ids=(route.route_id,),
        related_packet_ids=route.related_packet_ids,
        related_source_record_ids=route.related_source_record_ids,
        blockers=blockers,
        warnings=warnings,
        next_steps=next_steps,
        summary=_summary_for(route, blockers, warnings),
        diagnostics=diagnostics,
    )


def build_operator_handoffs(bundle: NavigationBundle) -> OperatorHandoffRegistry:
    handoffs = tuple(sorted((_handoff_for_route(route, bundle) for route in bundle.routes.routes), key=handoff_sort_key))
    diagnostics = _sort_diagnostics(diagnostic for handoff in handoffs for diagnostic in handoff.diagnostics)
    return OperatorHandoffRegistry(
        workspace_id=bundle.registry.workspace_id,
        handoffs=handoffs,
        diagnostics=diagnostics,
        _handoff_by_id={handoff.handoff_id: handoff for handoff in handoffs},
    )


def build_handoff_bundle(*, repo_root, workspace: str) -> tuple[NavigationBundle, OperatorHandoffRegistry]:
    bundle = build_navigation_bundle(repo_root=repo_root, workspace=workspace)
    return bundle, build_operator_handoffs(bundle)
