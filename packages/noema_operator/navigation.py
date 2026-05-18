from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import difflib
import os
from typing import Iterable

from packages.noema_maintainer.scan import OBJECT_CLASSES, ObjectRecord
from packages.noema_service.repository import filter_records, load_records

from .projections import ResolvedWorkspace, _resolve_workspace
from .review_packets import ReviewPacket, ReviewRecordRef, build_review_packets

TARGET_KINDS = (
    "operator_page",
    "review_page",
    "review_packet",
    "source_record",
    "navigation_page",
    "navigation_manifest",
)
ROUTE_KINDS = (
    "workspace_overview",
    "proposal_triage",
    "blocked_review",
    "ready_review",
    "accepted_apply_audit",
    "recovery_audit",
    "packet_review",
)
HANDOFF_KINDS = (
    "workspace_overview",
    "proposal_triage",
    "blocked_review",
    "ready_review",
    "accepted_apply_audit",
    "recovery_audit",
    "packet_review",
)
DIAGNOSTIC_CODE_ORDER = (
    "missing_target_id",
    "unresolved_target_reference",
    "ambiguous_target_id",
    "missing_route_reference",
    "unresolved_route_reference",
    "missing_handoff_reference",
    "unresolved_handoff_reference",
    "unsupported_open_mode",
    "unsupported_platform_for_execute",
)
MISSING_VALUE = "—"

OPERATOR_PAGE_TARGETS = (
    ("operator:index", "Operator Workspace", "index.md", "Workspace operator landing page."),
    ("operator:objects", "Objects", "objects.md", "Workspace source record index."),
    ("operator:proposals", "Proposals", "proposals.md", "Workspace proposal queue projection."),
    ("operator:recent", "Recent Activity", "recent.md", "Workspace recent activity projection."),
)
REVIEW_PAGE_TARGETS = (
    ("review:index", "Operator Review Cockpit", "review/index.md", "Review cockpit landing page."),
    ("review:queue", "Review Queue", "review/queue.md", "Proposal review queue."),
    ("review:attention", "Attention Needed", "review/attention.md", "Blocked and attention-needed review packets."),
    ("review:readiness", "Review Readiness", "review/readiness.md", "Review readiness classification overview."),
    ("review:recovery", "Apply and Recovery Visibility", "review/recovery.md", "Apply evidence and recovery visibility."),
)
NAVIGATION_PAGE_TARGETS = (
    ("navigation:index", "Operator Navigation Workbench", "navigation/index.md", "Navigation workbench landing page."),
    ("navigation:targets", "Navigation Targets", "navigation/targets.md", "Deterministic navigation target registry."),
    ("navigation:routes", "Operator Routes", "navigation/routes.md", "Deterministic operator workflow routes."),
    ("navigation:handoffs", "Operator Handoffs", "navigation/handoffs.md", "Deterministic operator handoff packets."),
    ("navigation:open-commands", "Local Open Helpers", "navigation/open-commands.md", "Copy-pasteable local resolution and open helper examples."),
    ("navigation:manifest", "Navigation Manifest", "navigation/manifest.json", "Machine-readable derived workbench manifest."),
)


@dataclass(frozen=True)
class NavigationDiagnostic:
    code: str
    message: str
    target_id: str = ""
    route_id: str = ""
    handoff_id: str = ""
    references: tuple[str, ...] = ()


@dataclass(frozen=True)
class NavigationTarget:
    target_id: str
    target_kind: str
    title: str
    workspace_id: str
    repo_relative_path: str
    workspace_relative_path: str = ""
    projection_relative_path: str = ""
    source_record_id: str = ""
    source_object_class: str = ""
    proposal_id: str = ""
    packet_filename: str = ""
    description: str = ""
    exists: bool = False
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class NavigationResolution:
    target_id: str
    target_kind: str
    path: Path
    repo_relative_path: str
    workspace_relative_path: str
    file_uri: str
    markdown_link: str


@dataclass(frozen=True)
class NavigationRegistry:
    workspace_id: str
    workspace_root: Path
    repo_root: Path
    targets: tuple[NavigationTarget, ...]
    diagnostics: tuple[NavigationDiagnostic, ...]
    packets: tuple[ReviewPacket, ...]
    records: tuple[ObjectRecord, ...]
    ambiguous_target_ids: tuple[str, ...] = ()
    _target_by_id: dict[str, NavigationTarget] = field(default_factory=dict, repr=False, compare=False)

    def lookup(self, target_id: str) -> NavigationTarget | None:
        return self._target_by_id.get(target_id)

    def suggestions(self, target_id: str, *, limit: int = 3) -> tuple[str, ...]:
        return _suggestions(target_id, [target.target_id for target in self.targets], limit=limit)

    def resolve(self, target_id: str) -> NavigationResolution:
        if target_id in self.ambiguous_target_ids:
            raise ValueError(_unknown_message("ambiguous target id", target_id, ()))
        target = self.lookup(target_id)
        if target is None:
            raise ValueError(_unknown_message("unknown target", target_id, self.suggestions(target_id)))
        path = (self.repo_root / target.repo_relative_path).resolve()
        return NavigationResolution(
            target_id=target.target_id,
            target_kind=target.target_kind,
            path=path,
            repo_relative_path=target.repo_relative_path,
            workspace_relative_path=target.workspace_relative_path,
            file_uri=path.as_uri(),
            markdown_link=f"[{target.title or target.target_id}]({target.repo_relative_path})",
        )


@dataclass(frozen=True)
class OperatorRoute:
    route_id: str
    route_kind: str
    title: str
    purpose: str
    workspace_id: str
    entry_target_id: str
    ordered_target_ids: tuple[str, ...]
    recommended_next_target_ids: tuple[str, ...]
    related_packet_ids: tuple[str, ...]
    related_source_record_ids: tuple[str, ...]
    attention_summary: str
    checklist_items: tuple[str, ...]
    diagnostics: tuple[NavigationDiagnostic, ...] = ()


@dataclass(frozen=True)
class OperatorRouteRegistry:
    workspace_id: str
    routes: tuple[OperatorRoute, ...]
    diagnostics: tuple[NavigationDiagnostic, ...]
    _route_by_id: dict[str, OperatorRoute] = field(default_factory=dict, repr=False, compare=False)

    def lookup(self, route_id: str) -> OperatorRoute | None:
        return self._route_by_id.get(route_id)

    def suggestions(self, route_id: str, *, limit: int = 3) -> tuple[str, ...]:
        return _suggestions(route_id, [route.route_id for route in self.routes], limit=limit)


@dataclass(frozen=True)
class NavigationBundle:
    workspace: ResolvedWorkspace
    registry: NavigationRegistry
    routes: OperatorRouteRegistry


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _workspace_relative_path(path: Path, workspace_root: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return ""


def _projection_relative_path(path: Path, projection_root: Path) -> str:
    try:
        return path.resolve().relative_to(projection_root.resolve()).as_posix()
    except ValueError:
        return ""


def _source_record_id(record: ObjectRecord) -> str:
    return str(record.metadata.get("id", "")).strip()


def _metadata_text(record: ObjectRecord, key: str) -> str:
    return str(record.metadata.get(key, "")).strip()


def _record_title(record: ObjectRecord) -> str:
    return _metadata_text(record, "title") or _source_record_id(record) or record.path.name


def _record_tags(record: ObjectRecord) -> tuple[str, ...]:
    value = record.metadata.get("tags")
    if isinstance(value, list):
        return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _packet_target_suffix(packet: ReviewPacket) -> str:
    return Path(packet.packet_filename).stem


def _sort_diagnostics(diagnostics: Iterable[NavigationDiagnostic]) -> tuple[NavigationDiagnostic, ...]:
    code_order = {code: index for index, code in enumerate(DIAGNOSTIC_CODE_ORDER)}
    return tuple(
        sorted(
            diagnostics,
            key=lambda item: (
                code_order.get(item.code, len(code_order)),
                item.target_id,
                item.route_id,
                item.handoff_id,
                item.message,
                item.references,
            ),
        )
    )


def _target_kind_order(kind: str) -> int:
    try:
        return TARGET_KINDS.index(kind)
    except ValueError:
        return len(TARGET_KINDS)


def _route_kind_order(kind: str) -> int:
    try:
        return ROUTE_KINDS.index(kind)
    except ValueError:
        return len(ROUTE_KINDS)


def _target_sort_key(target: NavigationTarget) -> tuple[int, str]:
    return (_target_kind_order(target.target_kind), target.target_id)


def route_sort_key(route: OperatorRoute) -> tuple[int, str]:
    return (_route_kind_order(route.route_kind), route.route_id)


def _suggestions(value: str, candidates: Iterable[str], *, limit: int = 3) -> tuple[str, ...]:
    ordered = sorted(set(candidates))
    if not value:
        return tuple(ordered[:limit])
    contains = [candidate for candidate in ordered if value.lower() in candidate.lower() or candidate.lower() in value.lower()]
    if contains:
        return tuple(contains[:limit])
    matches = difflib.get_close_matches(value, ordered, n=limit, cutoff=0.35)
    return tuple(matches)


def _unknown_message(label: str, value: str, suggestions: tuple[str, ...]) -> str:
    if suggestions:
        return f"{label}: {value}. Suggestions: {', '.join(suggestions)}"
    return f"{label}: {value}"


def _projection_target(
    *,
    workspace_id: str,
    repo_root: Path,
    workspace_root: Path,
    projection_root: Path,
    target_id: str,
    target_kind: str,
    title: str,
    projection_relative: str,
    description: str,
    tags: tuple[str, ...],
) -> NavigationTarget:
    path = projection_root / projection_relative
    return NavigationTarget(
        target_id=target_id,
        target_kind=target_kind,
        title=title,
        workspace_id=workspace_id,
        repo_relative_path=_repo_relative_path(path, repo_root),
        workspace_relative_path=_workspace_relative_path(path, workspace_root),
        projection_relative_path=_projection_relative_path(path, projection_root),
        description=description,
        exists=path.exists(),
        tags=tags,
    )


def _source_target(*, workspace_id: str, repo_root: Path, workspace_root: Path, record: ObjectRecord) -> NavigationTarget | NavigationDiagnostic:
    record_id = _source_record_id(record)
    if not record_id:
        return NavigationDiagnostic(
            code="missing_target_id",
            message=f"Workspace source record has no id metadata: {_repo_relative_path(record.path, repo_root)}",
            references=(_repo_relative_path(record.path, repo_root),),
        )
    return NavigationTarget(
        target_id=f"source:{record_id}",
        target_kind="source_record",
        title=_record_title(record),
        workspace_id=workspace_id,
        repo_relative_path=_repo_relative_path(record.path, repo_root),
        workspace_relative_path=_workspace_relative_path(record.path, workspace_root),
        source_record_id=record_id,
        source_object_class=record.object_class,
        description=f"Workspace {record.object_class} source record.",
        exists=record.path.exists(),
        tags=(record.object_class, *_record_tags(record)),
    )


def build_navigation_registry(*, repo_root: Path, workspace: str, records: list[ObjectRecord] | None = None) -> NavigationRegistry:
    resolved_repo_root = Path(repo_root).resolve()
    resolved_workspace = _resolve_workspace(resolved_repo_root, workspace)
    all_records = load_records(resolved_repo_root) if records is None else records
    workspace_records = filter_records(all_records, workspace=resolved_workspace.workspace_id)
    packets = build_review_packets(repo_root=resolved_repo_root, workspace=resolved_workspace.workspace_id, records=workspace_records)
    projection_root = resolved_workspace.workspace_root / "projection" / "operator"

    candidates: list[NavigationTarget] = []
    diagnostics: list[NavigationDiagnostic] = []

    for target_id, title, relative, description in OPERATOR_PAGE_TARGETS:
        candidates.append(
            _projection_target(
                workspace_id=resolved_workspace.workspace_id,
                repo_root=resolved_repo_root,
                workspace_root=resolved_workspace.workspace_root,
                projection_root=projection_root,
                target_id=target_id,
                target_kind="operator_page",
                title=title,
                projection_relative=relative,
                description=description,
                tags=("operator",),
            )
        )
    for target_id, title, relative, description in REVIEW_PAGE_TARGETS:
        candidates.append(
            _projection_target(
                workspace_id=resolved_workspace.workspace_id,
                repo_root=resolved_repo_root,
                workspace_root=resolved_workspace.workspace_root,
                projection_root=projection_root,
                target_id=target_id,
                target_kind="review_page",
                title=title,
                projection_relative=relative,
                description=description,
                tags=("review",),
            )
        )
    for packet in packets:
        packet_path = projection_root / "review" / "packets" / packet.packet_filename
        candidates.append(
            NavigationTarget(
                target_id=f"review:packet:{_packet_target_suffix(packet)}",
                target_kind="review_packet",
                title=f"Review Packet: {packet.proposal_id}",
                workspace_id=resolved_workspace.workspace_id,
                repo_relative_path=_repo_relative_path(packet_path, resolved_repo_root),
                workspace_relative_path=_workspace_relative_path(packet_path, resolved_workspace.workspace_root),
                projection_relative_path=_projection_relative_path(packet_path, projection_root),
                proposal_id=packet.proposal_id,
                packet_filename=packet.packet_filename,
                description="Packet-specific proposal review page.",
                exists=packet_path.exists(),
                tags=("review", "packet", packet.primary_classification),
            )
        )
    for record in sorted(workspace_records, key=lambda item: (OBJECT_CLASSES.index(item.object_class) if item.object_class in OBJECT_CLASSES else 99, _source_record_id(item).lower(), str(item.path))):
        target_or_diagnostic = _source_target(
            workspace_id=resolved_workspace.workspace_id,
            repo_root=resolved_repo_root,
            workspace_root=resolved_workspace.workspace_root,
            record=record,
        )
        if isinstance(target_or_diagnostic, NavigationDiagnostic):
            diagnostics.append(target_or_diagnostic)
        else:
            candidates.append(target_or_diagnostic)
    for target_id, title, relative, description in NAVIGATION_PAGE_TARGETS:
        kind = "navigation_manifest" if relative.endswith(".json") else "navigation_page"
        candidates.append(
            _projection_target(
                workspace_id=resolved_workspace.workspace_id,
                repo_root=resolved_repo_root,
                workspace_root=resolved_workspace.workspace_root,
                projection_root=projection_root,
                target_id=target_id,
                target_kind=kind,
                title=title,
                projection_relative=relative,
                description=description,
                tags=("navigation",),
            )
        )

    grouped: dict[str, list[NavigationTarget]] = {}
    for target in candidates:
        grouped.setdefault(target.target_id, []).append(target)
    ambiguous = tuple(sorted(target_id for target_id, matches in grouped.items() if len(matches) > 1))
    for target_id in ambiguous:
        diagnostics.append(
            NavigationDiagnostic(
                code="ambiguous_target_id",
                message=f"Navigation target id is ambiguous: {target_id}",
                target_id=target_id,
                references=tuple(sorted(target.repo_relative_path for target in grouped[target_id])),
            )
        )

    targets = tuple(sorted(candidates, key=_target_sort_key))
    target_by_id = {target_id: matches[0] for target_id, matches in grouped.items() if len(matches) == 1}
    return NavigationRegistry(
        workspace_id=resolved_workspace.workspace_id,
        workspace_root=resolved_workspace.workspace_root,
        repo_root=resolved_repo_root,
        targets=targets,
        diagnostics=_sort_diagnostics(diagnostics),
        packets=tuple(packets),
        records=tuple(workspace_records),
        ambiguous_target_ids=ambiguous,
        _target_by_id=target_by_id,
    )


def _route_diagnostics(route_id: str, target_ids: Iterable[str], registry: NavigationRegistry) -> tuple[NavigationDiagnostic, ...]:
    diagnostics: list[NavigationDiagnostic] = []
    for target_id in target_ids:
        if not target_id:
            diagnostics.append(
                NavigationDiagnostic(
                    code="missing_target_id",
                    message="Route contains an empty target id reference.",
                    route_id=route_id,
                )
            )
        elif target_id in registry.ambiguous_target_ids:
            diagnostics.append(
                NavigationDiagnostic(
                    code="ambiguous_target_id",
                    message=f"Route references ambiguous target id: {target_id}",
                    target_id=target_id,
                    route_id=route_id,
                )
            )
        elif registry.lookup(target_id) is None:
            diagnostics.append(
                NavigationDiagnostic(
                    code="unresolved_target_reference",
                    message=f"Route references unresolved target id: {target_id}",
                    target_id=target_id,
                    route_id=route_id,
                )
            )
    return _sort_diagnostics(diagnostics)


def _source_id_for_ref(ref: ReviewRecordRef) -> str:
    return ref.record_id


def _packet_source_ids(packet: ReviewPacket, registry: NavigationRegistry | None = None) -> tuple[str, ...]:
    ids = {packet.proposal_id}
    if registry is not None:
        for record in registry.records:
            if record.path.resolve() == packet.proposal_path.resolve():
                record_id = _source_record_id(record)
                if record_id:
                    ids.add(record_id)
                break
    ids.update(ref.record_id for ref in packet.resolved_target_records)
    ids.update(ref.record_id for ref in packet.resolved_evidence_records)
    ids.update(log.record.record_id for log in packet.related_log_records)
    return tuple(sorted(item for item in ids if item))


def _packet_source_target_ids(packet: ReviewPacket, registry: NavigationRegistry) -> tuple[str, ...]:
    candidates = [f"source:{source_id}" for source_id in _packet_source_ids(packet, registry)]
    return tuple(target_id for target_id in candidates if registry.lookup(target_id) is not None)


def _packet_attention_target(packet: ReviewPacket) -> str:
    if packet.attention_flags or packet.primary_classification in {"blocked_missing_targets", "blocked_missing_evidence", "recovery_attention_needed", "unknown_status"}:
        return "review:attention"
    return "review:readiness"


def _attention_summary(packets: Iterable[ReviewPacket]) -> str:
    packet_list = list(packets)
    blocked = sum(1 for packet in packet_list if packet.primary_classification in {"blocked_missing_targets", "blocked_missing_evidence"})
    recovery = sum(1 for packet in packet_list if packet.recovery_evidence_records)
    missing_apply = sum(1 for packet in packet_list if "accepted_without_apply_evidence" in packet.readiness_classifications)
    return f"{len(packet_list)} packet(s); {blocked} blocked; {recovery} recovery attention; {missing_apply} accepted without apply evidence."


def _base_route(
    *,
    registry: NavigationRegistry,
    route_id: str,
    route_kind: str,
    title: str,
    purpose: str,
    entry_target_id: str,
    ordered_target_ids: tuple[str, ...],
    recommended_next_target_ids: tuple[str, ...],
    related_packets: Iterable[ReviewPacket],
    checklist_items: tuple[str, ...],
) -> OperatorRoute:
    packet_tuple = tuple(related_packets)
    source_ids: set[str] = set()
    for packet in packet_tuple:
        source_ids.update(_packet_source_ids(packet, registry))
    diagnostics = _route_diagnostics(route_id, (entry_target_id, *ordered_target_ids, *recommended_next_target_ids), registry)
    return OperatorRoute(
        route_id=route_id,
        route_kind=route_kind,
        title=title,
        purpose=purpose,
        workspace_id=registry.workspace_id,
        entry_target_id=entry_target_id,
        ordered_target_ids=ordered_target_ids,
        recommended_next_target_ids=recommended_next_target_ids,
        related_packet_ids=tuple(sorted(packet.proposal_id for packet in packet_tuple)),
        related_source_record_ids=tuple(sorted(source_ids)),
        attention_summary=_attention_summary(packet_tuple),
        checklist_items=checklist_items,
        diagnostics=diagnostics,
    )


def build_operator_routes(registry: NavigationRegistry) -> OperatorRouteRegistry:
    packets = list(registry.packets)
    blocked_packets = [packet for packet in packets if packet.primary_classification in {"blocked_missing_targets", "blocked_missing_evidence"} or "unknown_status" in packet.readiness_classifications or packet.recovery_evidence_records]
    ready_packets = [packet for packet in packets if "ready_for_human_review" in packet.readiness_classifications]
    accepted_apply_packets = [packet for packet in packets if packet.proposal_status == "accepted"]
    recovery_packets = [packet for packet in packets if packet.recovery_evidence_records]

    routes: list[OperatorRoute] = [
        _base_route(
            registry=registry,
            route_id="route:workspace-overview",
            route_kind="workspace_overview",
            title="Workspace Overview",
            purpose="Orient the operator to the workspace, current objects, proposal posture, recent activity, review cockpit, and navigation workbench.",
            entry_target_id="operator:index",
            ordered_target_ids=("operator:index", "operator:objects", "operator:proposals", "operator:recent", "review:index", "navigation:index"),
            recommended_next_target_ids=("operator:objects", "review:index", "navigation:routes"),
            related_packets=packets,
            checklist_items=(
                "Start at the operator index and confirm workspace identity.",
                "Inspect object, proposal, and recent activity summaries.",
                "Use the review cockpit and navigation workbench for focused follow-up.",
            ),
        ),
        _base_route(
            registry=registry,
            route_id="route:proposal-triage",
            route_kind="proposal_triage",
            title="Proposal Triage",
            purpose="Review the proposal queue, attention page, and readiness page before selecting packet-level follow-up.",
            entry_target_id="review:queue",
            ordered_target_ids=("review:index", "review:queue", "review:attention", "review:readiness"),
            recommended_next_target_ids=("review:attention", "review:readiness"),
            related_packets=packets,
            checklist_items=(
                "Inspect the full proposal queue before acting on any individual packet.",
                "Prioritize blocked, unknown-status, and recovery-attention packets.",
                "Use packet-specific routes for proposal-level context.",
            ),
        ),
        _base_route(
            registry=registry,
            route_id="route:blocked-review",
            route_kind="blocked_review",
            title="Blocked Review",
            purpose="Inspect missing target references, missing evidence, unknown statuses, and recovery signals blocking review confidence.",
            entry_target_id="review:attention",
            ordered_target_ids=("review:attention", "review:queue", "review:readiness"),
            recommended_next_target_ids=("review:attention",),
            related_packets=blocked_packets,
            checklist_items=(
                "Inspect missing target references and unresolved evidence references.",
                "Clarify unknown proposal status metadata before review.",
                "Inspect recovery or failure signals before further operator action.",
            ),
        ),
        _base_route(
            registry=registry,
            route_id="route:ready-review",
            route_kind="ready_review",
            title="Ready Review",
            purpose="Inspect packets classified as ready for human review with resolved targets and evidence.",
            entry_target_id="review:readiness",
            ordered_target_ids=("review:readiness", "review:queue"),
            recommended_next_target_ids=("review:readiness",),
            related_packets=ready_packets,
            checklist_items=(
                "Inspect proposal rationale, targets, evidence, and related logs.",
                "Confirm readiness is evidence for review, not an approval decision.",
                "Use normal Noema review governance for any decision.",
            ),
        ),
        _base_route(
            registry=registry,
            route_id="route:accepted-apply-audit",
            route_kind="accepted_apply_audit",
            title="Accepted Apply Audit",
            purpose="Audit accepted proposals with and without visible apply evidence without executing apply.",
            entry_target_id="review:recovery",
            ordered_target_ids=("review:recovery", "review:queue", "review:attention"),
            recommended_next_target_ids=("review:recovery",),
            related_packets=accepted_apply_packets,
            checklist_items=(
                "Distinguish accepted proposals with apply evidence from accepted proposals missing apply evidence.",
                "Inspect related logs before concluding materialization state.",
                "Do not execute apply from this route.",
            ),
        ),
        _base_route(
            registry=registry,
            route_id="route:recovery-audit",
            route_kind="recovery_audit",
            title="Recovery Audit",
            purpose="Inspect packets and logs with recovery, failure, rollback, correction, compensation, or manual-intervention signals.",
            entry_target_id="review:recovery",
            ordered_target_ids=("review:recovery", "review:attention", "review:queue"),
            recommended_next_target_ids=("review:recovery", "review:attention"),
            related_packets=recovery_packets,
            checklist_items=(
                "Inspect recovery/failure/rollback/manual-intervention evidence.",
                "Confirm whether follow-up belongs in normal review/apply governance.",
                "Do not mutate proposals, logs, or canonical objects from this route.",
            ),
        ),
    ]

    for packet in packets:
        packet_target_id = f"review:packet:{_packet_target_suffix(packet)}"
        source_target_ids = _packet_source_target_ids(packet, registry)
        tail_target = _packet_attention_target(packet)
        ordered_targets = (packet_target_id, *source_target_ids, tail_target)
        checklist = tuple(dict.fromkeys((*packet.operator_next_steps, "Inspect source proposal, target, evidence, and log records linked from this packet.", "Use normal Noema governance for any review/apply follow-up.")))
        diagnostics = _route_diagnostics(f"route:packet-review:{_packet_target_suffix(packet)}", ordered_targets, registry)
        routes.append(
            OperatorRoute(
                route_id=f"route:packet-review:{_packet_target_suffix(packet)}",
                route_kind="packet_review",
                title=f"Packet Review: {packet.proposal_id}",
                purpose=f"Inspect packet-specific context for proposal {packet.proposal_id}.",
                workspace_id=registry.workspace_id,
                entry_target_id=packet_target_id,
                ordered_target_ids=ordered_targets,
                recommended_next_target_ids=(tail_target,),
                related_packet_ids=(packet.proposal_id,),
                related_source_record_ids=_packet_source_ids(packet, registry),
                attention_summary=_attention_summary([packet]),
                checklist_items=checklist,
                diagnostics=diagnostics,
            )
        )

    routes = sorted(routes, key=route_sort_key)
    diagnostics = _sort_diagnostics(diagnostic for route in routes for diagnostic in route.diagnostics)
    return OperatorRouteRegistry(
        workspace_id=registry.workspace_id,
        routes=tuple(routes),
        diagnostics=diagnostics,
        _route_by_id={route.route_id: route for route in routes},
    )


def build_navigation_bundle(*, repo_root: Path, workspace: str, records: list[ObjectRecord] | None = None) -> NavigationBundle:
    resolved_repo_root = Path(repo_root).resolve()
    resolved_workspace = _resolve_workspace(resolved_repo_root, workspace)
    all_records = load_records(resolved_repo_root) if records is None else records
    workspace_records = filter_records(all_records, workspace=resolved_workspace.workspace_id)
    registry = build_navigation_registry(repo_root=resolved_repo_root, workspace=str(resolved_workspace.workspace_root), records=workspace_records)
    routes = build_operator_routes(registry)
    return NavigationBundle(workspace=resolved_workspace, registry=registry, routes=routes)


def format_resolution(resolution: NavigationResolution, output_format: str) -> str:
    if output_format == "path":
        return str(resolution.path)
    if output_format == "repo-relative-path":
        return resolution.repo_relative_path
    if output_format == "workspace-relative-path":
        return resolution.workspace_relative_path or MISSING_VALUE
    if output_format == "file-uri":
        return resolution.file_uri
    if output_format == "markdown-link":
        return resolution.markdown_link
    raise ValueError(f"unsupported format: {output_format}")


def relative_markdown_link(*, target: NavigationTarget, page_path: Path, registry: NavigationRegistry, label: str | None = None) -> str:
    target_path = registry.repo_root / target.repo_relative_path
    relative_target = os.path.relpath(target_path.resolve(), start=page_path.parent.resolve())
    return f"[{label or target.target_id}]({Path(relative_target).as_posix()})"
