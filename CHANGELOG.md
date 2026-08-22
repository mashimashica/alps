# Changelog

This file records notable changes to ALPS. ALPS is versioned as a single repository-wide release unit. See [Versioning](docs/versioning.md) for compatibility and release rules.

## [Unreleased]

## [0.4.0] - 2026-08-22

Release notes: [ALPS 0.4.0](docs/releases/0.4.0.md).

### Added

- Added the `alps-markdown-agent-plugins/1.0` binding for `.alps/MODEL.md`, named Models, and Process Views.
- Added English and Japanese Model/View templates, a structural checker, and a compatibility/source resolver.
- Added the authoritative ALPS Reference Model at `.alps/MODEL.md`.
- Added a namespaced Agent Plugins manifest extension for the default Model entry point.

### Changed

- Extended `define-alps`, `apply-alps`, and `manage-alps` to cover Model/View definition, resolution, application, compatibility, governance, release, and retirement.
- Updated English and Japanese documentation and package metadata to version 0.4.0.

### Compatibility

- Retained the `define-alps`, `apply-alps`, and `manage-alps` identifiers and root `skills/` paths.
- Model/View assets using this binding declare `>=0.4.0 <0.5.0`.
- Packages without Models or Views remain valid.
- Clients may ignore the namespaced manifest extension when unsupported.

### Status

- This release remains in initial development.
- The release candidate does not create a Git tag or publish a release.

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
