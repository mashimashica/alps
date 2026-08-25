# Versioning

<p align="right">
  <strong>English</strong> | <a href="locales/ja/versioning.md">Japanese</a>
</p>

ALPS uses version numbers in `MAJOR.MINOR.PATCH` form and releases the repository as one versioned unit.

## Release Unit

An ALPS release includes the Process Framework, the ALPS Specification, the reference Process Skills, their bundled resources, localizations, validation scripts, and repository-level documentation and assets.

English descriptions are authoritative. Japanese localizations are included in the same release and should remain aligned with their authoritative English sources.

Individual documents and Skill Packages do not carry independent version numbers. The exact contents of a release are identified by its Git tag and the commit to which that tag points.

## Initial Development

Versions before `1.0.0` are in initial development. During this period:

- a PATCH release, such as `0.1.1`, contains changes that do not alter normative meaning, applicability, repository path contracts, or machine-consumed formats;
- a MINOR release, such as `0.2.0`, contains any addition, removal, or change to normative meaning, conformance criteria, required structure, repository path contracts, or machine-consumed formats; and
- a pre-release identifier, such as `0.2.0-rc.1`, identifies a candidate that is not yet the corresponding release.

A change that appears editorial but changes normative force, scope, applicability, or interpretation is a MINOR change rather than a PATCH change. MINOR releases before `1.0.0` may be incompatible with earlier versions.

## Stable Releases

Version `1.0.0` declares an initial stable compatibility boundary. After `1.0.0`:

- a MAJOR release contains incompatible changes to the declared compatibility boundary;
- a MINOR release adds functionality or normative content without breaking that boundary; and
- a PATCH release contains backward-compatible corrections.

The compatibility boundary and any supported migration obligations must be documented before `1.0.0` is released.

## Identifying Exact Content

A consumer should record, as applicable:

- the ALPS version;
- the Git tag;
- the commit SHA;
- the repository path; and
- a content digest for an individual artifact when stronger identity is needed.

A tag is immutable once published. A published tag must not be moved or reused for different content. Consumers that synchronize ALPS assets into another repository should pin both the tag and the commit SHA.

The `main` branch represents ongoing development. Changes not yet assigned to a release are recorded under `Unreleased` in [CHANGELOG.md](../CHANGELOG.md).

## Release Procedure

1. Select the version and update `VERSION`.
2. Move completed entries from `Unreleased` into the dated release section in `CHANGELOG.md`.
3. Prepare release notes under `docs/releases/`.
4. Merge the release-preparation pull request into `main`.
5. Create a tag named `vMAJOR.MINOR.PATCH` on the merge commit.
6. Publish a GitHub Release from that tag using the prepared release notes.
7. Confirm that the tag resolves to the intended commit and remains immutable.
