# Noema Original System Design

## 1. Purpose

Noema is intended to be an open-source, self-hosted knowledge platform for shared work between humans and agents. Its job is to preserve raw knowledge inputs, compile them into durable and navigable knowledge objects, and expose them through both human-facing clients and bounded machine interfaces.

The system is meant to be reusable by anyone. It should run on infrastructure users can control, including a NAS or a VPS, and remain accessible from anywhere the operator chooses to expose it.

Noema is not framed as a personal-only vault, a notes app, an Obsidian plugin, or a thin wrapper around retrieval. It is a shared knowledge platform with human roles, agent roles, storage conventions, review workflows, and explicit authority boundaries.

## 2. Design Goals

- Build a public, open-source foundation that is reusable beyond any one user, team, or domain.
- Support multiple human users and multiple agent users from the beginning.
- Keep the system self-hosted, portable, and practical to deploy on a NAS or VPS.
- Treat knowledge as a durable, compounding system artifact rather than temporary chat output.
- Preserve transparent and portable storage, with strong support for Markdown-based workflows.
- Keep the platform editor-agnostic while making Obsidian a strong first-class human client.
- Separate what knowledge is about from how it is used, who can see it, and who can change it.
- Provide bounded machine interfaces such as APIs and MCP-style integrations.
- Make machine contributions reviewable, attributable, and safe to govern in shared environments.
- Leave room for open-source extension through packs, integrations, and alternate clients.

## 3. Non-Goals

- Noema is not intended to be only a personal note-taking setup.
- It is not an Obsidian-only product and not an Obsidian plugin in disguise.
- It is not merely a Markdown folder convention with no platform model around it.
- It is not just a RAG wrapper over uploaded files.
- It is not limited to one domain, one workflow style, or one type of user.
- It does not assume that every agent should have blanket write access to knowledge.
- It does not require fully autonomous operation before human review exists.
- It does not need full-scale enterprise complexity in the first implementation slice.

## 4. Inspiration and Attribution

Noema takes important inspiration from Andrej Karpathy's ["llm-wiki" gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). That pattern emphasizes a persistent, interlinked knowledge layer that is maintained over time, instead of repeatedly reconstructing answers from raw documents at query time. The ideas of raw sources, a compiled wiki layer, schema-guided maintenance, and ongoing linting/curation are especially relevant.

Noema is also informed by Obsidian Help's page on [how Obsidian stores data](https://obsidian.md/help/data-storage). Obsidian stores notes as Markdown plain-text files in a vault on the local file system, and keeps vault-specific configuration in `.obsidian`. That model is valuable because it keeps human-facing knowledge portable, inspectable, and editable with ordinary filesystem tools.

Noema generalizes these ideas into a broader public platform. The goal is not to recreate Karpathy's pattern as a personal-only workflow, and not to reduce the system to an Obsidian vault. Instead, Noema extends the underlying lessons into a multi-user, multi-agent, self-hosted system with shared workspaces, explicit policy boundaries, and bounded machine access.

## 5. Core Concepts

The following axes are intentionally independent. Keeping them separate is one of the main architectural rules of Noema.

| Axis | Meaning | Example values |
| --- | --- | --- |
| **Domain** | What the knowledge is about | medical, investment, sports, arts, literature, technology, history, economics |
| **Profile** | How the knowledge is used | course-learning, research, team knowledge base, hobby deep dive, project memory, decision support |
| **Workspace/project** | A concrete ongoing instance of work | a shared research workspace, a team handbook workspace, a decision support project |
| **Content type** | What kind of knowledge object it is | raw source, summary, entity page, concept page, procedure, proposal, log entry |
| **Visibility** | Who may access it | private, team, organization, public, scoped agent visibility |
| **Authority** | Who may modify or approve it | owner, reviewer group, maintainer agent, service account, public contributor with review |

Important clarifications:

- **Domain is not profile.** A domain answers what the knowledge concerns. A profile answers how the knowledge is used. For example, "course-learning" is a profile, not a domain. It can apply to history, economics, technology, literature, or other domains.
- **Domain is not visibility.** Medical knowledge can be private, team-visible, or public. Investment knowledge can be private or public. Visibility is a separate policy axis.
- **Workspace/project is the concrete operating unit.** A workspace brings together a selected domain, one or more profiles, participants, policies, and active knowledge objects.
- **Content types cut across the whole system.** The same domain and workspace can contain raw material, structured artifacts, proposals, and logs at the same time.
- **Authority is not the same as authorship.** An agent may draft a proposal without having authority to publish it. A human reviewer may approve changes without having created the original content.

## 6. System Roles

Noema assumes several distinct roles.

### Human users

- **Owners** define workspace purpose, membership, and operating rules.
- **Reviewers** validate proposed changes, resolve conflicts, and approve authoritative updates.
- **Readers** consume knowledge, ask questions, and use the system without necessarily changing authoritative content.

A single human may hold more than one role in a small deployment, but the roles remain conceptually distinct.

### Maintainer / compiler / curator agent

Noema should support a management model or agent whose main job is maintenance rather than open-ended authorship. This maintainer role acts as a **compiler and curator** of knowledge. It can ingest sources, draft summaries, update indexes, cross-link pages, surface contradictions, prepare proposals, and help keep the knowledge base coherent over time.

This role is important because it turns accumulated knowledge into a maintained system artifact. It should usually operate through bounded workflows and auditable outputs, not through unrestricted authority.

### Agent users

Agent users are bounded machine consumers and contributors. They may query knowledge, read structured artifacts, classify material, draft proposals, or perform maintenance tasks. They should be treated as first-class users with scoped permissions, identities, and audit trails rather than as invisible background implementation details.

## 7. Knowledge Model

Noema's knowledge model should distinguish several major classes of knowledge objects.

### Raw

Raw objects are source-facing materials that the system preserves for reference. Examples include documents, transcripts, imports, clipped articles, attachments, source snapshots, and externally captured records. Raw content should generally remain immutable or append-protected after ingest, because it anchors provenance.

### Structured

Structured objects are the compiled and curated knowledge layer. Examples include summaries, entity pages, concept pages, glossaries, procedures, timelines, decision records, relationship maps, and other canonical artifacts that help humans and agents navigate what is known.

### Proposals

Proposals are candidate changes or candidate artifacts that have not yet been accepted as authoritative. They allow agents and humans to contribute safely in shared environments. A proposal may introduce a new page, suggest edits to an existing object, recommend a reclassification, or surface a contradiction for review.

### Logs

Logs are append-oriented records of what happened in the system. They capture ingests, queries, maintenance runs, review decisions, sync activity, and other operational history. Logs are not the same thing as structured knowledge, but they are essential for auditability and maintenance.

These classes should be linkable to one another. Structured content should be able to point back to raw provenance. Proposals should point to the objects they affect. Logs should record the actions that created or updated raw, structured, or proposal objects.

## 8. Storage Model

Noema should prefer a transparent and portable storage model.

- Human-facing knowledge should be representable in ordinary files, with Markdown as a first-class format.
- Raw assets should be preserved separately from compiled knowledge.
- Structured knowledge should remain easy to inspect, diff, version, and back up.
- Machine-readable metadata can live in frontmatter, sidecar files, indexes, or service-managed records, depending on what the implementation needs.

Obsidian matters here, but in a specific way. Because Obsidian stores notes as Markdown files in a filesystem vault, it is a strong human-facing workspace/client for file-based knowledge. Noema should therefore be **Obsidian-compatible** where useful.

However, Obsidian is **not** the authority layer and **not** the only entrance to the system. The authoritative model also includes workspace boundaries, access policy, provenance, proposals, logs, and machine interfaces. Some of that state may be projected into a vault view, but it should not depend on Obsidian's local configuration to exist.

The platform should remain editor-agnostic. A user should be able to interact through Obsidian, another text editor, a future web client, or a CLI without changing the system's core identity.

## 9. Access and Authority Model

Noema must keep access and authority separate.

- **Visibility** answers who may discover or read a given object.
- **Authority** answers who may create, modify, approve, or publish changes to that object.

This distinction is essential in a multi-user, multi-agent system.

- Someone may have read access without write authority.
- An agent may have authority to draft proposals without authority to publish canonical changes.
- A reviewer may approve changes even when they are not the original author.
- Publicly visible knowledge may still have tightly restricted authority.

Policies should be applicable at the system, workspace, and content-object levels. They should also be auditable: machine-originated changes need attributable identities, and sensitive write paths should be reviewable.

Obsidian access does not override Noema policy. Being able to open a vault view is not the same thing as having authority over all corresponding knowledge objects.

## 10. Multi-User and Multi-Agent Model

Noema is designed for shared knowledge work by default.

### Multiple humans

A workspace may have several human participants with different responsibilities. One person may own the workspace, another may review domain-specific updates, and others may be readers or contributors. Shared ownership and shared review should be normal, not an afterthought.

### Multiple agents

A workspace may also have several agent users with different scopes. For example, one agent might focus on ingestion, another on linting and cross-linking, and another on structured query support. Their identities, permissions, and action histories should remain visible.

### Bounded interfaces

Agent users should not depend on ad hoc filesystem access. Instead, Noema should expose bounded machine surfaces such as APIs and MCP-style interfaces for reading, querying, proposing changes, and retrieving structured context.

### Review and attribution

In a shared environment, agent output should usually flow through structured review paths. The system should make it clear which changes came from humans, which came from agents, and which objects are canonical versus proposed.

## 11. Deployment Model

Noema is intended to be self-hosted and accessible everywhere the operator wants it to be.

Initial deployment assumptions:

- It should be practical to run on a NAS or a VPS.
- It should be suitable for single-node deployment first.
- It should be compatible with normal backup, sync, and version-control practices.
- It should support secure remote access through whichever mechanism the operator chooses, such as LAN access, VPN, reverse proxy, or public domain exposure.

The system should not assume hyperscale infrastructure before it becomes useful. Portability, transparency, and operator control matter more in the baseline architecture slice.

## 12. Extension Model

Noema should be easy for an open-source community to extend.

### Domain packs

Domain packs can provide conventions, taxonomies, templates, and helper behaviors for specific subject areas such as medical, investment, sports, arts, literature, technology, history, or economics.

### Workflow/profile packs

Workflow or profile packs can provide reusable patterns for course-learning, research, team knowledge bases, hobby deep dives, project memory, decision support, and similar usage modes.

### Integrations

Integrations can connect Noema to external tools and systems for import, export, sync, notification, capture, search, or automation.

### Machine interfaces

Open APIs and MCP-style interfaces should allow external tools and agent systems to consume or contribute bounded functionality without forking the core architecture.

The core platform should stay generic while extension packs carry domain- or workflow-specific opinionation.

## 13. Initial Implementation Direction

The first implementation direction should stay small, coherent, and public-facing.

1. Establish shared architecture language and repository docs.
2. Create a repository skeleton that reflects the core knowledge model.
3. Define initial conventions for raw, structured, proposal, and log objects.
4. Support an Obsidian-compatible human workspace view without making Obsidian the authority.
5. Expose bounded machine access for read/query and proposal submission.
6. Add maintainer workflows for ingest, compile, cross-linking, and review support.
7. Add multi-user policy, authentication, and deployment packaging after the baseline model is proven.

This direction keeps the project grounded: file-friendly where that helps, platform-oriented where shared use requires it, and open to later extension without prematurely over-engineering the core.
