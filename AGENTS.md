# AGENTS.md

[Japanese translation](docs/ja/AGENTS.md)

## ALPS

This repository contains Agent Skill representations governed by ALPS (Agent Lifecycle Process Skills).

A Process representation is the default ALPS case: its `SKILL.md` is the authoritative Process Description used to understand, invoke, and assess the Process. An Agent Skill may also represent a Process Model, Process Reference Model, or Process View when `metadata.alps.kind` declares that non-Process kind. Loading one of those representations provides selection or composition context; it does not invoke a Process.

The ALPS Reference Model is represented by `alps-reference-model` and relates three reference Processes:

- `define-alps` defines and verifies Process Descriptions and other ALPS representations.
- `apply-alps` selects and loads applicable representations, resolves Processes, and invokes only Process representations.
- `manage-alps` governs adoption, change, Tailoring, assessment, improvement, and retirement.

A Process View organizes Activities and Tasks across Processes for a Concern or Purpose. View-local or modified content does not change a Source Process or establish Source Process Conformance. Change the applicable Source Process through managed Tailoring, or change its authoritative Process Description through controlled redefinition with `define-alps`.

## Skill layout

`skills/` is the single source of truth for Agent Skills registered and exposed as distributed ALPS Plugin Skills. It contains one distributable Process Reference Model and three distributable reference Processes:

- `skills/alps-reference-model/`
- `skills/define-alps/`
- `skills/apply-alps/`
- `skills/manage-alps/`

`.agents/skills/` is the integrated discovery view for repository-development Agents that are configured to inspect that path. It is not assumed to be a universal Host convention. Plugin Hosts continue to discover distributed Skills through `skills/` and their applicable Host adapters.

The four distributed Agent Skill representations appear under `.agents/skills/` only as relative symbolic links to `skills/`; do not duplicate their contents.

Repository-development Skills live as real directories under `.agents/skills/`:

- `review-alps` reviews changes across the Process Framework, ALPS Specification, ALPS Reference Model, reference Processes, checker behavior, record bindings, locale counterparts, and the complete change diff.
- `sync-locales` checks semantic equivalence and update coverage between authoritative English assets and supported Japanese counterparts.

These repository-development Skills are not registered, exposed, or discovered as distributed Plugin Skills. They can still be present as ordinary files in a repository checkout or package archive.

Add another repository-development Skill only after a repeated task has emerged that does not fit clearly within `review-alps` or `sync-locales`.

## Repository workflow

- Keep one source of truth for each information item and use relative links from consumers.
- Inspect repository state before editing and preserve unrelated or user changes.
- Use `sync-locales` whenever English or Japanese paired assets change.
- Use `review-alps` whenever a change can affect semantics across the PF, ALPS Specification, ALPS Reference Model, reference Processes, checker, bindings, or locales.
- Follow the applicable Skill validation requirements. At minimum, check whitespace, changed relative links, canonical references, locale counterparts, and the complete task-owned diff.
- Treat `skills/define-alps/scripts/check_alps_asset.py` as a structural and semantic preflight for the repository's Markdown Agent Skill representation. It does not by itself determine ALPS Conformance.
- Do not commit, push, publish, open or update a pull request, or make another external change unless the user requests it.
