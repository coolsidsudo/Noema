from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
from typing import Iterable

from .review_packets import (
    ATTENTION_FLAG_ORDER,
    MISSING_VALUE,
    READINESS_CLASSIFICATION_ORDER,
    RELATED_LOG_RELATION_ORDER,
    RelatedLogRecord,
    ReviewPacket,
    ReviewRecordRef,
)

EMPTY_NO_PACKETS = "_No review packets found._"
EMPTY_NO_ATTENTION = "_No packets currently need attention._"
EMPTY_NO_MISSING_TARGETS = "_No missing target references._"
EMPTY_NO_MISSING_EVIDENCE = "_No missing evidence references._"
EMPTY_NO_RECOVERY = "_No recovery signals found._"
EMPTY_NO_APPLY = "_No apply evidence found._"

CLASSIFICATION_DESCRIPTIONS = {
    "blocked_missing_targets": "A proposal has unresolved or absent target references required for review.",
    "blocked_missing_evidence": "A proposal has unresolved or absent evidence/provenance references required for review.",
    "recovery_attention_needed": "A related log contains explicit recovery, failure, rollback, correction, compensation, or manual-intervention metadata.",
    "accepted_without_apply_evidence": "An accepted proposal has no related apply/reconcile evidence in metadata-linked logs.",
    "unknown_status": "The proposal status is missing or outside the accepted proposal lifecycle values.",
    "ready_for_human_review": "An under-review proposal has resolved targets and evidence with no recovery signal.",
    "draft_not_ready": "A draft proposal is visible but not classified as ready for human review.",
    "apply_evidence_present": "An accepted proposal has related metadata-linked apply/reconcile evidence.",
    "rejected_or_withdrawn_terminal": "A rejected or withdrawn proposal is terminal for review visibility purposes.",
}


def _format_table_cell(value: object) -> str:
    if value is None:
        return MISSING_VALUE
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return MISSING_VALUE
    return text.replace("|", "\\|")


def _table_row(values: Iterable[object]) -> str:
    return "| " + " | ".join(_format_table_cell(value) for value in values) + " |"


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _markdown_path_link(*, target_path: Path, page_path: Path, repo_root: Path) -> str:
    label = _repo_relative_path(target_path, repo_root)
    relative_target = os.path.relpath(target_path.resolve(), start=page_path.parent.resolve())
    return f"[{_format_table_cell(label)}]({Path(relative_target).as_posix()})"


def _record_link(ref: ReviewRecordRef, *, page_path: Path, repo_root: Path) -> str:
    return _markdown_path_link(target_path=ref.path, page_path=page_path, repo_root=repo_root)


def _packet_link(packet: ReviewPacket, *, page_path: Path) -> str:
    target = page_path.parent / "packets" / packet.packet_filename
    relative_target = os.path.relpath(target.resolve(), start=page_path.parent.resolve())
    return f"[{_format_table_cell(packet.proposal_id)}]({Path(relative_target).as_posix()})"


def _packet_link_from_packet(packet: ReviewPacket, *, target_page: str) -> str:
    return f"[{target_page}](../{target_page})"


def _join(values: Iterable[str]) -> str:
    items = [value for value in values if value]
    return ", ".join(items) if items else MISSING_VALUE


def _count_all_classifications(packets: list[ReviewPacket]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for packet in packets:
        counts.update(packet.readiness_classifications)
    return counts


def _attention_packet_count(packets: list[ReviewPacket]) -> int:
    return sum(1 for packet in packets if packet.attention_flags)


def _missing_target_count(packets: list[ReviewPacket]) -> int:
    return sum(len(packet.missing_target_ids) for packet in packets)


def _missing_evidence_count(packets: list[ReviewPacket]) -> int:
    return sum(len(packet.missing_evidence_ids) for packet in packets)


def _append_table(lines: list[str], headers: list[str], rows: list[list[object]], empty_text: str) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append(_table_row(row))
    if not rows:
        lines.extend(["", empty_text])


def _cleanup_stale_packet_pages(packets_root: Path) -> None:
    packets_root.mkdir(parents=True, exist_ok=True)
    for stale_page in sorted(packets_root.glob("*.md")):
        stale_page.unlink()


def _render_index(*, path: Path, packets: list[ReviewPacket]) -> None:
    counts = _count_all_classifications(packets)
    lines = [
        "# Operator Review Cockpit",
        "",
        "Review packets are derived read-only visibility artifacts. They do not approve, reject, apply, or mutate Noema records.",
        "",
        "## Review Summary",
        f"- Proposal packets: `{len(packets)}`",
        f"- Packets needing attention: `{_attention_packet_count(packets)}`",
        f"- Missing target references: `{_missing_target_count(packets)}`",
        f"- Missing evidence references: `{_missing_evidence_count(packets)}`",
        "",
        "## Readiness Counts",
    ]
    _append_table(
        lines,
        ["classification", "count"],
        [[classification, counts.get(classification, 0)] for classification in READINESS_CLASSIFICATION_ORDER],
        EMPTY_NO_PACKETS,
    )
    lines.extend(["", "## Attention Needed"])
    attention_rows = [
        [flag, sum(1 for packet in packets if flag in packet.attention_flags)]
        for flag in ATTENTION_FLAG_ORDER
        if any(flag in packet.attention_flags for packet in packets)
    ]
    _append_table(lines, ["attention_flag", "packet_count"], attention_rows, EMPTY_NO_ATTENTION)
    lines.extend(
        [
            "",
            "## Review Links",
            "- [Review Queue](./queue.md)",
            "- [Attention Needed](./attention.md)",
            "- [Review Readiness](./readiness.md)",
            "- [Apply and Recovery Visibility](./recovery.md)",
        ]
    )
    _write_markdown(path, lines)


def _render_queue(*, path: Path, packets: list[ReviewPacket]) -> None:
    lines = ["# Review Queue", "", "## Proposal Packets", ""]
    rows = [
        [
            packet.proposal_id,
            packet.proposal_status,
            _join(packet.readiness_classifications),
            _join(packet.attention_flags),
            len(packet.resolved_target_records),
            _join(packet.missing_target_ids),
            _join(packet.missing_evidence_ids),
            len(packet.related_log_records),
            _packet_link(packet, page_path=path),
        ]
        for packet in packets
    ]
    _append_table(
        lines,
        [
            "proposal_id",
            "status",
            "readiness",
            "attention",
            "targets",
            "missing_targets",
            "missing_evidence",
            "related_logs",
            "packet",
        ],
        rows,
        EMPTY_NO_PACKETS,
    )
    _write_markdown(path, lines)


def _render_attention(*, path: Path, packets: list[ReviewPacket]) -> None:
    lines = ["# Attention Needed", "", "## Blocked Packets", ""]
    blocked = [
        packet
        for packet in packets
        if packet.primary_classification in {"blocked_missing_targets", "blocked_missing_evidence"}
    ]
    _append_table(
        lines,
        ["proposal_id", "primary_classification", "attention", "packet"],
        [[packet.proposal_id, packet.primary_classification, _join(packet.attention_flags), _packet_link(packet, page_path=path)] for packet in blocked],
        EMPTY_NO_ATTENTION,
    )
    lines.extend(["", "## Missing Targets", ""])
    target_rows = [
        [packet.proposal_id, missing_id, _packet_link(packet, page_path=path)]
        for packet in packets
        for missing_id in packet.missing_target_ids
    ]
    target_rows.extend(
        [packet.proposal_id, "target references absent", _packet_link(packet, page_path=path)]
        for packet in packets
        if "target_references_absent" in packet.attention_flags
    )
    _append_table(lines, ["proposal_id", "missing_target", "packet"], target_rows, EMPTY_NO_MISSING_TARGETS)
    lines.extend(["", "## Missing Evidence", ""])
    evidence_rows = [
        [packet.proposal_id, missing_id, _packet_link(packet, page_path=path)]
        for packet in packets
        for missing_id in packet.missing_evidence_ids
    ]
    evidence_rows.extend(
        [packet.proposal_id, "evidence references absent", _packet_link(packet, page_path=path)]
        for packet in packets
        if "evidence_references_absent" in packet.attention_flags
    )
    _append_table(lines, ["proposal_id", "missing_evidence", "packet"], evidence_rows, EMPTY_NO_MISSING_EVIDENCE)
    lines.extend(["", "## Recovery Attention", ""])
    recovery_rows = [
        [packet.proposal_id, log.record.record_id, _join(log.relation_labels), _packet_link(packet, page_path=path)]
        for packet in packets
        for log in packet.recovery_evidence_records
    ]
    _append_table(lines, ["proposal_id", "log_id", "relation", "packet"], recovery_rows, EMPTY_NO_RECOVERY)
    _write_markdown(path, lines)


def _render_readiness(*, path: Path, packets: list[ReviewPacket]) -> None:
    lines = [
        "# Review Readiness",
        "",
        "Readiness classifications are visibility evidence for operators, not Noema authority decisions.",
        "",
        "## Classification Rules",
        "",
    ]
    _append_table(
        lines,
        ["classification", "meaning"],
        [[classification, CLASSIFICATION_DESCRIPTIONS[classification]] for classification in READINESS_CLASSIFICATION_ORDER],
        EMPTY_NO_PACKETS,
    )
    lines.extend(["", "## Packets by Classification"])
    for classification in READINESS_CLASSIFICATION_ORDER:
        lines.extend(["", f"### {classification}", ""])
        matching = [packet for packet in packets if classification in packet.readiness_classifications]
        _append_table(
            lines,
            ["proposal_id", "status", "primary", "packet"],
            [[packet.proposal_id, packet.proposal_status, packet.primary_classification, _packet_link(packet, page_path=path)] for packet in matching],
            f"_No packets classified as {classification}._",
        )
    _write_markdown(path, lines)


def _render_recovery(*, path: Path, packets: list[ReviewPacket]) -> None:
    accepted = [packet for packet in packets if packet.proposal_status == "accepted"]
    with_apply = [packet for packet in accepted if packet.apply_evidence_records]
    without_apply = [packet for packet in accepted if not packet.apply_evidence_records]
    lines = [
        "# Apply and Recovery Visibility",
        "",
        "This page summarizes metadata-visible apply and recovery signals only. It does not run apply or recovery.",
        "",
        "## Accepted Proposals",
        "",
    ]
    _append_table(
        lines,
        ["proposal_id", "apply_evidence", "recovery_signals", "packet"],
        [[packet.proposal_id, len(packet.apply_evidence_records), len(packet.recovery_evidence_records), _packet_link(packet, page_path=path)] for packet in accepted],
        "_No accepted proposals found._",
    )
    lines.extend(["", "## Apply Evidence Present", ""])
    _append_table(
        lines,
        ["proposal_id", "apply_logs", "packet"],
        [[packet.proposal_id, _join(log.record.record_id for log in packet.apply_evidence_records), _packet_link(packet, page_path=path)] for packet in with_apply],
        EMPTY_NO_APPLY,
    )
    lines.extend(["", "## Missing Apply Evidence", ""])
    _append_table(
        lines,
        ["proposal_id", "guidance", "packet"],
        [[packet.proposal_id, "Confirm whether accepted proposal has been applied or requires apply/recovery follow-up.", _packet_link(packet, page_path=path)] for packet in without_apply],
        "_No accepted proposals are missing apply evidence._",
    )
    lines.extend(["", "## Recovery Signals", ""])
    recovery_rows = [
        [packet.proposal_id, log.record.record_id, _join(log.relation_labels), _packet_link(packet, page_path=path)]
        for packet in packets
        for log in packet.recovery_evidence_records
    ]
    _append_table(lines, ["proposal_id", "log_id", "relation", "packet"], recovery_rows, EMPTY_NO_RECOVERY)
    lines.extend(
        [
            "",
            "## Operator Guidance",
            "- Treat accepted status as a review decision, not proof of materialization.",
            "- Inspect related apply/recovery logs before taking further operator action.",
            "- Use normal Noema proposal/review/apply governance paths for any follow-up.",
        ]
    )
    _write_markdown(path, lines)


def _record_rows(refs: tuple[ReviewRecordRef, ...], *, page_path: Path, repo_root: Path) -> list[list[object]]:
    return [
        [ref.record_id, ref.object_class, ref.status, ref.title, _record_link(ref, page_path=page_path, repo_root=repo_root)]
        for ref in refs
    ]


def _log_rows(logs: tuple[RelatedLogRecord, ...], *, page_path: Path, repo_root: Path) -> list[list[object]]:
    return [
        [
            log.record.record_id,
            _join(label for label in RELATED_LOG_RELATION_ORDER if label in log.relation_labels),
            log.record.status,
            log.record.title,
            _record_link(log.record, page_path=page_path, repo_root=repo_root),
        ]
        for log in logs
    ]


def _render_packet(*, path: Path, repo_root: Path, packet: ReviewPacket) -> None:
    lines = [
        f"# Review Packet: {packet.proposal_id}",
        "",
        "## Proposal",
        f"- Proposal id: `{_format_table_cell(packet.proposal_id)}`",
        f"- Status: `{_format_table_cell(packet.proposal_status)}`",
        f"- Title: `{_format_table_cell(packet.proposal_title)}`",
        f"- Created by: `{_format_table_cell(packet.created_by)}`",
        f"- Created at: `{_format_table_cell(packet.created_at)}`",
        f"- Source proposal: {_markdown_path_link(target_path=packet.proposal_path, page_path=path, repo_root=repo_root)}",
        "",
        "## Readiness",
        f"- Primary classification: `{packet.primary_classification}`",
        f"- All classifications: `{_format_table_cell(_join(packet.readiness_classifications))}`",
        "",
        "## Attention Flags",
    ]
    if packet.attention_flags:
        lines.extend(f"- `{flag}`" for flag in packet.attention_flags)
    else:
        lines.append("- _No attention flags._")

    lines.extend(["", "## Target Objects", ""])
    _append_table(lines, ["id", "class", "status", "title", "path"], _record_rows(packet.resolved_target_records, page_path=path, repo_root=repo_root), "_No resolved target objects._")
    if packet.missing_target_ids:
        lines.extend(["", "Missing target references:"])
        lines.extend(f"- `{target_id}`" for target_id in packet.missing_target_ids)

    lines.extend(["", "## Evidence / Provenance", ""])
    _append_table(lines, ["id", "class", "status", "title", "path"], _record_rows(packet.resolved_evidence_records, page_path=path, repo_root=repo_root), "_No resolved evidence/provenance records._")
    if packet.missing_evidence_ids:
        lines.extend(["", "Missing evidence references:"])
        lines.extend(f"- `{evidence_id}`" for evidence_id in packet.missing_evidence_ids)

    lines.extend(["", "## Related Logs", ""])
    _append_table(lines, ["id", "relation", "status", "title", "path"], _log_rows(packet.related_log_records, page_path=path, repo_root=repo_root), "_No related logs found._")

    lines.extend(["", "## Apply / Recovery Evidence", "", "### Apply Evidence", ""])
    _append_table(lines, ["id", "relation", "status", "title", "path"], _log_rows(packet.apply_evidence_records, page_path=path, repo_root=repo_root), EMPTY_NO_APPLY)
    lines.extend(["", "### Recovery Evidence", ""])
    _append_table(lines, ["id", "relation", "status", "title", "path"], _log_rows(packet.recovery_evidence_records, page_path=path, repo_root=repo_root), EMPTY_NO_RECOVERY)

    lines.extend(["", "## Operator Next Steps"])
    lines.extend(f"- {step}" for step in packet.operator_next_steps)
    lines.extend(
        [
            "",
            "## Navigation",
            f"- {_packet_link_from_packet(packet, target_page='queue.md')}",
            f"- {_packet_link_from_packet(packet, target_page='attention.md')}",
            f"- {_packet_link_from_packet(packet, target_page='index.md')}",
        ]
    )
    _write_markdown(path, lines)


def render_review_cockpit(*, repo_root: Path, operator_projection_root: Path, packets: list[ReviewPacket]) -> tuple[Path, ...]:
    review_root = operator_projection_root / "review"
    packets_root = review_root / "packets"
    _cleanup_stale_packet_pages(packets_root)

    index_path = review_root / "index.md"
    queue_path = review_root / "queue.md"
    attention_path = review_root / "attention.md"
    readiness_path = review_root / "readiness.md"
    recovery_path = review_root / "recovery.md"

    _render_index(path=index_path, packets=packets)
    _render_queue(path=queue_path, packets=packets)
    _render_attention(path=attention_path, packets=packets)
    _render_readiness(path=readiness_path, packets=packets)
    _render_recovery(path=recovery_path, packets=packets)

    packet_paths: list[Path] = []
    for packet in packets:
        packet_path = packets_root / packet.packet_filename
        _render_packet(path=packet_path, repo_root=Path(repo_root).resolve(), packet=packet)
        packet_paths.append(packet_path)

    return (index_path, queue_path, attention_path, readiness_path, recovery_path, *packet_paths)
