# Noema Phase 9 Architecture Decision — Obsidian as First-Class Client, Noema as Service-Centered System

## Status

Accepted architecture decision for Phase 9 framing.

## Purpose

This note fixes the Phase 9 architecture stance for human-facing interaction and service exposure.

It answers a specific question:

- should Noema use Obsidian as its user interface,
- should Noema build a separate native app/web UI first,
- or should Obsidian be hooked onto a deeper Noema system surface?

This note establishes the decision so Phase 9 implementation can proceed without UI-model drift.

## Decision

Phase 9 will treat:

- **Noema as the system/backend/governed knowledge platform**
- **Obsidian as a first-class human client hooked onto Noema**
- **a native Noema web/app UI as optional later work, not the default first Phase 9 requirement**

In practical terms:

1. Noema will continue to own the authoritative governed system surface:
   - knowledge-object handling,
   - proposal/review/apply behavior,
   - logs and operational trace,
   - bounded machine interfaces,
   - policy and authority boundaries.

2. Obsidian will be used as the primary early human-facing workspace/client:
   - browsing structured knowledge,
   - viewing indexes and projections,
   - navigating proposal/review context,
   - working in Markdown-native files and views.

3. Phase 9 will **not** treat Obsidian as the authority layer, and will **not** reduce Noema to an Obsidian vault or plugin.

4. Phase 9 will **not** require a broad standalone web application before usable system value exists.

5. If later operator workflows prove awkward or unsafe in Obsidian alone, Noema may add a thin native operator surface for those bounded functions without changing Obsidian’s role as a strong first-class client.

## Why this decision follows the original design

The original system design already establishes the core shape:

- Noema is a self-hosted shared knowledge platform for humans and agents.
- It must expose both human-facing clients and bounded machine interfaces.
- Obsidian should be strongly supported as a human-facing workspace/client.
- Obsidian is **not** the authority layer and **not** the only entrance to the system.
- The platform should remain editor-agnostic.

This means the correct interpretation is not:

- “Obsidian is the system”

and not:

- “Ignore Obsidian and build a separate UI first”

but instead:

- “Obsidian is a strong client attached to a deeper Noema system.”

## Why this decision follows the Karpathy-first direction

Karpathy’s pattern centers on:

- immutable raw source truth,
- a maintained compiled wiki/knowledge layer,
- schema/instructions that guide the maintainer.

Noema extends that pattern into shared operation through:

- governed `proposals/`,
- append-only `logs/`,
- bounded machine access,
- explicit human review and authority.

That means the center of Noema is the maintained governed knowledge system, not the client shell around it.

Obsidian fits as an IDE-like human workspace over that maintained knowledge layer, but it is not the full product identity.

## Architectural consequences

### 1. Noema must own a real service/core layer

Phase 9 should build or expose a bounded Noema service/core that owns:

- object retrieval and listing,
- traceability retrieval,
- proposal submission and status,
- review/apply integration,
- observability/recovery visibility,
- machine-facing bounded interfaces.

This service/core should exist independently of any one client.

### 2. Obsidian should remain a first-class human client

Phase 9 should actively support Obsidian by projecting or generating human-usable views such as:

- workspace home surfaces,
- browse/index pages,
- proposal queue surfaces,
- recent changes / review status surfaces,
- structured navigation views,
- other Markdown-native projections aligned to Noema objects and workflows.

### 3. Obsidian should not become the authority layer

Authority, policy, proposal state, apply state, and machine-facing behavior must not depend on `.obsidian` configuration or local-client-only state.

Opening a vault view must not imply system authority.

### 4. A standalone native UI is optional and bounded

Phase 9 may later introduce a small native operator UI only when a bounded workflow is clearly awkward in Obsidian alone, for example:

- apply/recovery controls,
- sensitive operator actions,
- live operational status views,
- review actions needing stronger guardrails.

Such a UI should be thin and attached to the Noema system surface, not a separate parallel product model.

## What Phase 9 should build first

The preferred Phase 9 order is:

1. bounded Noema service/core surface,
2. Obsidian-facing projections and operator workflow integration,
3. thin machine adapters such as HTTP and/or MCP,
4. optional later thin native operator surface only where justified.

This keeps implementation aligned with the existing architecture:

- file-friendly where useful,
- platform-centered where governance requires it,
- bounded and single-node first,
- implementation-first rather than UI-sprawl-first.

## Explicit non-decisions

This note does **not** decide:

- that Noema will never have a native web UI,
- that Obsidian must be the only human client forever,
- that Phase 9 includes full auth/UI/platform polish,
- that Phase 9 should broaden into enterprise control-plane work.

## Anti-drift guardrails

Phase 9 implementation should avoid these drifts:

- treating Obsidian as the authority layer,
- treating the Noema system as only a vault/browser,
- rebuilding Noema as generic chat/RAG over files,
- introducing a large standalone UI before the bounded system surface is real,
- splitting semantics between client-local behavior and governed backend behavior.

## Summary

The correct Phase 9 architecture stance is:

- **Noema is the governed system**
- **Obsidian is a first-class hooked client**
- **native Noema UI is optional later and should remain thin unless clearly justified**

This preserves the original design, preserves the Karpathy-first maintainer/compiler direction, and keeps Phase 9 implementation focused on the highest-value missing layer: a usable bounded system surface.
