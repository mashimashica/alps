# Changelog

This file records notable changes to ALPS. ALPS is versioned as a single repository-wide release unit. See [Versioning](docs/versioning.md) for compatibility and release rules.

## [Unreleased]

### Changed

- Redesigned ALPS as one distributed `reusable-work-design` Skill representing
  the `Reusable Work Design Process`, while retaining `alps` as the Plugin and
  repository brand.
- Reduced the ALPS Specification to a thin Agent Skill profile. The Process
  Framework remains authoritative for general Process semantics, and the Host
  remains responsible for Skill discovery, selection, activation, and execution.
- Reworked English and Japanese guidance, Host metadata, validation, and
  repository-development review around one Process, one Purpose, proportionate
  detail, and separation of self-application from self-certification.

### Removed

- Removed the distributed `alps-reference-model`, `define-alps`, `apply-alps`,
  and `manage-alps` Skills and their duplicate metadata and icon copies.
- Removed active typed representation kinds, ALPS-specific logical Skill
  references, Logical Package Scope, Package Binding, and resolver requirements.
- Removed the discovery-description Conformance suffix requirement.
- Removed the Process Instance Record references, generator, checker, and tests.
- Removed the all-sections Skill template, record templates, management records,
  and redundant Skill-package-format guidance.
- Removed the ALPS Reference Model diagrams from the active documentation surface.

### Compatibility

- This is a breaking pre-1.0 redesign intended for the next MINOR release
  (0.6.0). Release preparation remains separate, so `VERSION` and manifest
  versions are unchanged in this change.
- Consumers must replace the four removed Skill identifiers with
  `reusable-work-design` for Process Skill creation, review, or revision.
- Ordinary execution and general Skill selection are delegated to the Agent
  Skills Host. Adoption, versioning, change, retirement, and governance remain
  repository or organizational responsibilities.
- Consumers of removed representation metadata, logical references, or Process
  Instance Record bindings must migrate. No compatibility wrapper, redirect
  Skill, legacy parser, or replacement resolver is provided.

## [0.5.0] - 2026-08-29

Release notes: [ALPS 0.5.0](docs/releases/0.5.0.md).

### Added

- Added pull-request and main-branch validation for the official Agent Skills form, the root Agent Plugins schema, the official Claude Plugin form, repository integrity, Process Instance Record behavior, relative Markdown links, and whitespace errors.

### Changed

- Normalized the Process Framework and ALPS Specification so PF remains the sole source for general Process semantics, the ALPS Reference Model owns the reference relationship structure, and each reference Process Skill owns its complete Process Description.
- Defined versioned logical Skill resolution through Logical Package Scope and Package Binding, including package ID, exact version, and Skill name as the complete logical identity, an `alps` same-version Release Package, and distinct resolution scopes for package-qualified and same-scope short references.
- Declared same-scope resolution context explicitly instead of inferring it from repository paths and retained package ID, exact version, and Skill name as the complete logical identity at the normative ALPS layer.
- Renamed the three Reference Process display Names to the noun phrases ALPS Definition Process, ALPS Application Process, and ALPS Management Process while retaining the stable `define-alps`, `apply-alps`, and `manage-alps` Skill identifiers.
- Integrated the Process Skill example, file-based Skill Package example, Agent ecosystem context, and PF/ALPS responsibility allocation into the paired ALPS Specification documents as informative subclauses, while placing related Process standards with the paired Process Framework documents.
- Removed the former paired Appendix D guidance on Human Oversight, Accountability, and Evidence without relocation.
- Clarified general Process semantics derived from the standards crosswalk, including Instance-specific responsibility, maturity and information-item meaning, Incremental application, structural levels, Name Tailoring, conditions of application, governance accountability, and measurement chains. Standard-specific organization, profile, and tailoring rules remain outside PF.
- Reworked the paired README around user Outcomes, a concise installation path, plain-language usage examples, and paired English/Japanese ALPS Reference Model diagrams.

### Removed

- Removed the optional ALPS Markdown Profile v1 from the current specification and withdrew v2 without ratification or a compatibility layer.
- Removed the bundled profile checker, typed intermediate representation, parser, resolver, locale comparator, fixtures, and checker-specific tests.
- Replaced the profile-checking responsibility with separate official Agent Skills and Plugin validation, repository-integrity checks, and proposition-level cross-layer semantic review.

### Fixed

- Closed a proposition-level semantic-preservation ledger for the Process Framework and ALPS Specification, restoring lost requirements, recommendations, permissions, possibilities, expectations, conditions, quantifiers, negation scope, and authoritative-reference connections in English and Japanese.
- Aligned Task Conformance summaries with PF 8.3, including requirements stated in Activities, and aligned the canonical Apply ALPS handoff Task with the unconditional provider-Output to recipient-Input mapping requirement.
- Restored Framework-level Constraint semantics alongside shared Controls and Enablers and clarified the specification-declared Logical Package Scope for ALPS reference assets.
- Aligned informative record bindings with the normative sources by requiring Tailoring scope, recording candidate evaluation and Process Name Traceability, using typed representation-assessment subjects, and projecting unconditional handoff mappings.
- Separated Description Conformance, Process Conformance, Reference Process Conformance, and Execution Conformance by subject, and aligned the reference Process Outcomes, atomic Tasks, and record bindings with those claim boundaries.
- Aligned the OpenAI-facing name and icon for `alps-reference-model` with the other distributed Skills and replaced generic ALPS plugin listing metadata with concrete capabilities and starter prompts.

### Compatibility

- The package ID `alps`, the distributed Skill identifiers `alps-reference-model`, `define-alps`, `apply-alps`, and `manage-alps`, and their root `skills/` paths remain unchanged from 0.4.0.
- The current specification no longer includes `alps-markdown/v1`, and the bundled profile checker is not retained. Consumers that require that physical binding must remain pinned to the immutable `v0.4.0` release or migrate to the applicable Agent Skill and Host forms.
- The unratified `alps-markdown/v2` draft is withdrawn without becoming a released compatibility target. No wrapper, deprecation layer, legacy parser, or replacement ALPS-specific Markdown language is provided.
- Logical Skill identity remains `(package ID, exact version, Skill name)`, while physical Package Binding remains the responsibility of the applicable Host. This repository does not add a multi-package or multi-version resolver.
- These normative, Conformance, representation, and machine-consumed validation changes make this a pre-1.0 MINOR release.

### Status

- This release remains in initial development.
- Compatibility is governed by the pre-1.0 rules in [Versioning](docs/versioning.md).

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
