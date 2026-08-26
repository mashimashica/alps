# Changelog

This file records notable changes to ALPS. ALPS is versioned as a single repository-wide release unit. See [Versioning](docs/versioning.md) for compatibility and release rules.

## [Unreleased]

### Fixed

- Aligned the OpenAI-facing name and icon for `alps-reference-model` with the other distributed Skills and replaced generic ALPS plugin listing metadata with concrete capabilities and starter prompts.

## [0.4.0] - 2026-08-25

Release notes: [ALPS 0.4.0](docs/releases/0.4.0.md).

### Added

- Added explicit Agent Skill representation kinds for Process Model, Process Reference Model, and Process View while retaining Process as the default representation.
- Added the distributed `alps-reference-model` Process Reference Model alongside the `define-alps`, `apply-alps`, and `manage-alps` Processes.
- Added the optional ALPS Markdown Profile v1 Environment Binding, identified as `alps-markdown/v1`, with a typed and bounded checker bundled as an Application Enabler of the repository-development `review-alps` Process.
- Added repository-development `review-alps` and `sync-locales` Process Skills under `.agents/skills/` without registering them as distributed Plugin Skills.

### Changed

- Recentered the Process Framework, ALPS Specification, reference Processes, records, and guidance on Process as the work performed and Agent Skill as its representation.
- Distinguished representation activation from Process Invocation and preserved source provenance and Traceability for Process Views where source elements are referenced.
- Aligned the Markdown Environment Binding with the ALPS semantic boundary: Process Activities and Tasks are optional, and Process Views may contain View-local Activities and Tasks without requiring source inclusion.
- Moved the public normative assets from `.alps/spec/` to `spec/` and moved repository localization metadata from `.alps/localization.yaml` to `localization.yaml`.
- Moved Japanese repository documentation from `docs/ja/` to `docs/locales/ja/`.
- Established `skills/` as the source of truth for the four distributed Skills and `.agents/skills/` as a repository-development discovery view.
- Clarified the logical roles of authoritative representations, Environment Bindings, Application Enablers, output-creation resources, Host metadata, and presentation resources.
- Aligned English and Japanese representation semantics and naturalized remaining Japanese user-facing text.

### Compatibility

- The identifiers `define-alps`, `apply-alps`, and `manage-alps` and their root `skills/` paths remain unchanged from 0.3.0.
- `alps-reference-model` is a new distributed Skill identifier in 0.4.0.
- Consumers using `.alps/spec/`, `.alps/localization.yaml`, or `docs/ja/` must update stored paths, synchronization rules, and pinned references to `spec/`, `localization.yaml`, and `docs/locales/ja/`.
- The distributed `skills/define-alps/scripts/check_skill_description.py` preflight from 0.3.0 is not retained. Repository-development validation is now provided by `.agents/skills/review-alps/scripts/validate_alps_markdown.py` for the optional `alps-markdown/v1` Environment Binding.
- ALPS Markdown Profile v1 intentionally defines a bounded physical representation and may reject noncanonical YAML or Markdown forms; successful profile validation is not an ALPS Conformance claim.
- These normative, representation, path-contract, and Environment Binding changes make this a pre-1.0 MINOR release.

### Status

- This release remains in initial development.
- Compatibility is governed by the pre-1.0 rules in [Versioning](docs/versioning.md).

## [0.3.0] - 2026-08-22

Release notes: [ALPS 0.3.0](docs/releases/0.3.0.md).

### Added

- Added client-specific plugin manifests for Claude Code, Codex, and Cursor alongside the root Agent Plugins manifest.
- Added per-Skill OpenAI interface metadata and bundled ALPS icon assets for clients that consume them.

### Changed

- Restructured the English and Japanese READMEs around adoption, reference Skill selection, ALPS concepts, and repository contents.
- Simplified the English and Japanese installation guidance for `npx plugins add mashimashica/alps`.
- Clarified Japanese Process Description prose and aligned Japanese terminology and adaptation-related wording with the authoritative English sources.

### Compatibility

- Retained the `define-alps`, `apply-alps`, and `manage-alps` identifiers and root `skills/` paths introduced in 0.2.0.
- Consumers already using the 0.2.0 Skill identifiers and package paths do not need to rename them.
- The release adds machine-consumed client manifests and interface metadata and is therefore a pre-1.0 MINOR release.

### Status

- This release remains in initial development.
- Compatibility is governed by the pre-1.0 rules in [Versioning](docs/versioning.md).

## [0.2.0] - 2026-08-19

Release notes: [ALPS 0.2.0](docs/releases/0.2.0.md).

### Changed

- Adopted the Agent Plugins 1.0 package layout with a root `plugin.json` and portable Agent Skills under the root `skills/` directory.
- Renamed the ALPS Reference Model Skills to `define-alps`, `apply-alps`, and `manage-alps` under the `<verb>-alps` naming convention.
- Moved repository-level localization metadata from `.agents/localization.yaml` to `.alps/localization.yaml`.
- Updated English and Japanese documentation and Skill references for the new package paths and identifiers.
- Documented complete-Package installation, explicit reference-Skill invocation, and the canonical minimal `AGENTS.md` policy for consumer repositories.
- Aligned the repository's English and Japanese `AGENTS.md` files with that consumer policy while retaining repository-maintenance rules separately.

### Compatibility

- Removed the former `.agents/skills/` paths and the identifiers `define-agent-lifecycle-process-skills`, `apply-agent-lifecycle-process-skills`, and `manage-agent-lifecycle-process-skills`.
- Consumers must update stored paths, installation records, invocations, and references to the new identifiers and root `skills/` paths.
- Consumers must install the complete Plugin Package, including `.alps/`; copying only `skills/` does not preserve the shared normative references.
- The change modifies repository path contracts and machine-consumed identifiers and is therefore released as a pre-1.0 MINOR version.

### Status

- This release remains in initial development.
- Compatibility is governed by the pre-1.0 rules in [Versioning](docs/versioning.md).

## [0.1.0] - 2026-08-19

Release notes: [ALPS 0.1.0](docs/releases/0.1.0.md).

### Added

- The Process Framework for describing general Processes independently of a particular performer or implementation method.
- The ALPS Specification for applying the Process Framework to Agent Skills.
- Reference Process Skills for defining, applying, and managing Agent Lifecycle Process Skills.
- Authoritative English descriptions and Japanese localizations.
- Templates, record guidance, and mechanical validation scripts.
- Repository documentation, licensing materials, and the project icon.

### Status

- This release is in initial development.
- Compatibility is governed by the pre-1.0 rules in [Versioning](docs/versioning.md).
