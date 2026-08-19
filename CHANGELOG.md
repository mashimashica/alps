# Changelog

This file records notable changes to ALPS. ALPS is versioned as a single repository-wide release unit. See [Versioning](docs/versioning.md) for compatibility and release rules.

## [Unreleased]

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
