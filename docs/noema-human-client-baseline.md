# Noema Human Client Baseline

## Purpose

This document defines the stable human client baseline for Noema.

This stable system-definition document originated from the accepted Phase 3 Slice 1 baseline.

The scope is intentionally narrow: provide a practical, GUI-first browse/review projection over the accepted Phase 2 knowledge model without changing core architecture semantics.

## Baseline references

This slice extends and aligns with:

- `README.md`
- `docs/noema-original-system-design.md`
- `control/development-plan.md`
- `docs/noema-core-object-conventions.md`
- `docs/noema-object-metadata-profile-v0.md`
- `docs/noema-relationship-traceability-conventions.md`
- `docs/noema-index-catalog-baseline.md`
- `control/workflow-baseline.md`

## Slice goals

1. Give humans a clear workspace home for day-to-day browsing.
2. Provide browse-by-class entry points for raw, structured, proposals, and logs.
3. Provide a proposal review queue view that surfaces target and support context links.
4. Provide a recent changes/logs view for operational traceability.
5. Keep authority and policy outside any single editor client.

## GUI-first browse/review expectations

The baseline human experience should work primarily through point-and-click navigation in a Markdown-capable GUI client (for example Obsidian, a web Markdown browser, or another GUI editor).

At minimum, each workspace projection should include:

- **Workspace home page** with role-oriented entry links.
- **Browse-by-class pages/manifests** for canonical discoverability.
- **Proposal review queue** ordered for reviewer triage.
- **Recent changes view** from logs for situational awareness.

The CLI may still be used for maintenance and rebuilding generated manifests, but ordinary reading/review should not require shell navigation through repository folders.

## Obsidian compatibility without authority collapse

Noema remains editor-agnostic. Obsidian is treated as a supported projection target because it reads Markdown directly from the filesystem, but it is not an authority layer.

Baseline rules:

- Authoritative semantics stay in Noema object metadata, relationship conventions, and review workflow state.
- Projection artifacts are navigational aids, not independent policy or authority sources.
- Any GUI client that can open Markdown files and links can use the same projection.

## Baseline human workflows

### Owner workflow (baseline)

1. Open workspace `home/README.md`.
2. Verify workspace purpose, scope, and active review posture.
3. Use `review/proposal-queue.md` to monitor unresolved proposals.
4. Use `logs/recent-changes.md` to inspect operational movement.
5. Delegate or assign reviewer attention using normal collaboration channels.

### Reviewer workflow (baseline)

1. Open `review/proposal-queue.md` and filter for `under_review` (and optionally `draft`) items.
2. For a selected proposal, follow target links and supporting raw/structured links.
3. Validate proposal intent, provenance support, and expected structured outcome.
4. Record decision through normal proposal/log object updates according to Phase 2 conventions.
5. Confirm changes appear in recent changes/log entries.

### Reader workflow (baseline)

1. Start from workspace home.
2. Navigate by class using `browse/` manifests, prioritizing `structured/` for canonical knowledge.
3. Optionally inspect proposal queue and logs for confidence and context.
4. Avoid treating raw or draft proposal content as canonical unless accepted.

## Generic projection layout (sample)

A baseline human projection can use this generic structure inside a workspace:

- `projection/home/README.md`
- `projection/browse/README.md`
- `projection/browse/by-class-raw.md`
- `projection/browse/by-class-structured.md`
- `projection/browse/by-class-proposals.md`
- `projection/browse/by-class-logs.md`
- `projection/review/proposal-queue.md`
- `projection/logs/recent-changes.md`
- `projection/REBUILD.md`

This layout is intentionally file-friendly and portable.

## Deterministic rebuild posture (lightweight)

For this baseline, projection pages may be maintained by either:

- deterministic generated manifests, or
- deterministic documented manual refresh steps.

The sample workspace includes a documented rebuild process in `projection/REBUILD.md` with stable sorting and predictable output sections.

## Drift checks for this slice

This baseline explicitly avoids:

- VHF-specific framing
- Obsidian-only authority assumptions
- auth/system deployment concerns (Phase 6)
- agent APIs and machine interface implementation (Phase 4)
- maintainer automation implementation (Phase 5)
- redefinition of accepted Phase 2 object, metadata, relationship, or index semantics

## Next-slice pointer

After this human client baseline slice, the next planned execution pointer remains:

- **Phase 4 — Agent interface baseline**
