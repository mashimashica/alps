# Versioning

<p align="right">
  <strong>English</strong> | <a href="locales/ja/versioning.md">Japanese</a>
</p>

ALPS uses `MAJOR.MINOR.PATCH` version numbers and releases the repository as one unit.

## Release Unit

A release includes the single distributed Skill and its references, English and Japanese documentation, Plugin and Host manifests, repository validation, and retained branding and legal assets. Individual files and Skill resources do not carry independent versions.

The exact release content is identified by an immutable Git tag and the commit it names. English user-facing sources are authoritative; their Japanese counterparts ship in the same release and remain semantically aligned.

## Initial Development

Versions before `1.0.0` are in initial development.

- A PATCH release corrects content without changing public meaning, required structure, repository path contracts, or machine-consumed formats.
- A MINOR release may add, remove, or change public meaning, required structure, repository path contracts, or machine-consumed formats and may be incompatible with an earlier pre-1.0 version.
- A pre-release identifier, such as `0.6.0-rc.1`, marks a candidate for the corresponding release.

## Stable Releases

Version `1.0.0` will declare the first stable compatibility boundary. After that point, incompatible changes require a MAJOR release, compatible functionality uses MINOR, and backward-compatible corrections use PATCH.

## Identifying Content

Consumers may record the ALPS version, Git tag, commit SHA, repository path, and an artifact digest when stronger identification is needed. Published tags are not moved or reused. The `main` branch represents ongoing development, with pending changes recorded under `Unreleased` in [CHANGELOG.md](../CHANGELOG.md).

## Release Procedure

1. Select the version and update `VERSION` and every Plugin manifest.
2. Add a dated section to `CHANGELOG.md` and prepare a release note under `docs/releases/`.
3. Run the repository's ordinary validation and review the final diff.
4. Commit the release state.
5. When publication is authorized, tag that commit as `vMAJOR.MINOR.PATCH` and publish the matching release note.
6. Confirm the tag identifies the intended immutable commit.
