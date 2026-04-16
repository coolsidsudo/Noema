# Noema

Noema is an open-source, self-hosted knowledge platform for multiple humans and multiple agent users. It is designed to turn raw knowledge inputs into durable, structured, reviewable workspaces that can be used through human-facing tools and bounded machine interfaces.

## Status

Noema has a documented architecture baseline and core system-definition package in `docs/`.

Repository implementation planning and active execution tracking are maintained separately in `control/`.

## Key principles

- **Self-hosted and portable:** Noema should be deployable on infrastructure ordinary users can control, including a NAS or a VPS.
- **Multi-human, multi-agent:** The system is meant for shared knowledge work across multiple human users and multiple agent users.
- **Open and reusable:** The project should be usable by anyone, not framed as a personal-only setup.
- **Compiled knowledge over disposable chat:** The platform should maintain durable knowledge artifacts, not just regenerate answers from raw files every time.
- **Editor-agnostic and Obsidian-compatible:** Obsidian is a first-class human client, but Noema must not depend on Obsidian as its only interface or authority.
- **Clear policy boundaries:** Domain, profile, workspace, content type, visibility, and authority are separate concerns.
- **Bounded machine access:** Agents should interact through scoped APIs and MCP-style interfaces rather than unrestricted access.

## High-level architecture

- **Raw knowledge inputs** are ingested and preserved as source material.
- **Structured knowledge objects** are compiled and curated into durable pages, records, indexes, and relationships.
- **Proposal and review flows** let humans and agents suggest changes without collapsing review and authority into the same step.
- **Workspace/project instances** organize concrete bodies of knowledge across domains and usage profiles.
- **Human clients** can browse, review, and edit through Markdown-friendly tools such as Obsidian and future web or CLI interfaces.
- **Machine clients** can query and contribute through bounded APIs and MCP-style interfaces.
- **Access policy** separates who may see content from who may modify or approve it.


## Repository skeleton

Phase 1 introduces a minimal, architecture-aligned structure:

- `raw/` — source-facing inputs
- `structured/` — curated canonical knowledge artifacts
- `proposals/` — reviewable candidate changes
- `logs/` — append-oriented operational records
- `schemas/` — future schema and validation conventions
- `packages/` — future services and libraries
- `deploy/` — deployment assets and templates
- `examples/` — sample/reference layouts

See `CONTRIBUTING.md` for baseline-first contribution guidance.

## Development vs System Documentation

- `docs/` defines the Noema system itself (what Noema is and how it works).
- `control/` contains repository development/control workflow artifacts (how this repository is currently building Noema).
- External users should rely on `docs/` for system definition.

## Documents

- [Original system design](docs/noema-original-system-design.md)
- [Access and authority baseline](docs/noema-access-authority-baseline.md)
- [Authentication and identity provisioning baseline](docs/noema-auth-identity-provisioning-baseline.md)
- [Self-hosted deployment and operations baseline](docs/noema-self-hosted-deployment-operations-baseline.md)
- [Core knowledge object conventions](docs/noema-core-object-conventions.md)
- [Baseline relationship and traceability conventions](docs/noema-relationship-traceability-conventions.md)
- [Baseline object metadata profile (v0)](docs/noema-object-metadata-profile-v0.md)
- [Baseline index/catalog approach](docs/noema-index-catalog-baseline.md)
- [Human client baseline](docs/noema-human-client-baseline.md)
- [Agent interface baseline](docs/noema-agent-interface-baseline.md)
- [Agent surface contract](docs/noema-agent-surface-contract.md)
- [Agent operation-state semantics](docs/noema-agent-operation-state-semantics.md)
- [Review/apply execution interoperability semantics](docs/noema-review-apply-interoperability-semantics.md)
- [Review/apply interoperability hardening semantics](docs/noema-review-apply-hardening-semantics.md)
- [Apply/recovery policy-profile refinement interoperability baseline](docs/noema-apply-recovery-policy-profiles.md)
- [Apply/recovery interoperability consistency and conformance guidance](docs/noema-apply-recovery-conformance-guidance.md)
- [Contributing guide](CONTRIBUTING.md)
- [Control layer overview](control/README.md)
- [Repository development plan](control/development-plan.md)
- [Repository workflow baseline](control/workflow-baseline.md)

## Inspiration

Noema is inspired in part by Andrej Karpathy's ["llm-wiki" gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), especially the idea of a persistent, interlinked knowledge layer that is incrementally maintained instead of being re-derived from raw sources on every query.

It is also informed by Obsidian's documentation on [how Obsidian stores data](https://obsidian.md/help/data-storage): vault content lives as Markdown files on the local file system, with vault-specific configuration stored separately in `.obsidian`. In Noema, that file-based model is valuable because it keeps human-facing knowledge portable and inspectable. Obsidian is therefore a first-class Markdown client for Noema workspaces, but it is not the whole system.
