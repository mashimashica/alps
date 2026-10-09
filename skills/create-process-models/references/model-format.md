# Process model Plugin format

[日本語](locales/ja/model-format.md)

One process model is one Agent Plugin. This reference defines the ALPS model profile, version 1. It packages Process Descriptions without making every Skill a model member. The profile governs model packages created by this Skill; it does not add required elements to all ALPS Process Descriptions.

## Sources

| Source | Owns |
| --- | --- |
| `plugin.json` | Package identity, release version, and explicit model membership. |
| A listed process Markdown document | Its display name, Purpose, Outcomes, necessary detail, and I/O declarations. |
| `references/artifacts/<id>.md` | One shared information-item, product, or service definition. |
| Optional workspace `alps-harness.yaml` | Concrete artifact locations and execution settings. |

A graph is a projection of these sources. There is no separate model file, type registry, edge list, or persisted copy of Purpose and Outcomes. The model can contain cycles. I/O does not establish execution order, required availability, start permission, approval, or Outcome achievement.

## Manifest

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "service-change",
  "version": "0.1.0",
  "extensions": {
    "io.github.mashimashica.alps": {
      "version": 1,
      "processes": ["./skills/implement-change/SKILL.md"]
    }
  }
}
```

The extension identifies this profile. Its `version` is the model format version; the root `version`, when supplied, is the package release. Neither is repeated in a process or artifact definition. An optional `title` inside the extension supplies a display name, for example a Japanese title. It is not another identifier.

`processes` lists each member document exactly once. Its order is not an execution sequence. An empty list represents an empty model without a draft flag; it does not satisfy a request to describe substantive work. Helper Skills do not become members merely because a host discovers them.

Skills use `./skills/<name>/SKILL.md`. Other work can use ordinary Markdown, such as `./processes/review-change.md`; human work needs no fabricated Skill. All package file paths, including resolved symlinks, must remain within the Plugin root. The portable manifest and Skill formats follow [Agent Plugins](https://agent-plugins.org/specification) and [Agent Skills](https://agentskills.io/specification). A Host adapter is needed only when the requested destination requires it; it does not introduce another model definition.

## Process documents

For `skills/implement-change/SKILL.md`:

```markdown
---
name: implement-change
description: Prepare a verifiable release candidate when implementing an agreed design.
metadata:
  inputs: '["design-description"]'
  outputs: '["release-candidate"]'
---

# Change Implementation

## Purpose

Make the agreed service change available for an informed release decision.

## Outcomes

- The candidate implements the agreed design within its stated scope.
- Relevant verification results and unresolved limitations are available for the release decision.
```

The body contains an H1 Name, a `## Purpose`, and a `## Outcomes` list. Japanese documents can use `## 目的` and `## 成果`. Outcomes are observable success conditions; an Output's existence does not by itself establish them. Include other detail only as needed to understand, apply, or evaluate the work. Metadata does not repeat Purpose or Outcomes. Preserve necessary Controls, Constraints, Enablers, and Entry/Exit Criteria in the body with their sources and scope. Criteria or policies governing the work are Controls; their classification is not changed by the I/O metadata.

A Skill's `name` is its stable process identifier and matches its directory. An ordinary process document uses its filename without `.md` as its identifier and can have the same `metadata` mapping without Skill discovery fields. Process identifiers follow the Agent Skill name syntax: lowercase ASCII letters, digits, and single hyphens, at most 64 characters, without a leading or trailing hyphen. They are unique within the model. Display names belong to the H1 and can change independently.

Agent Skills metadata maps strings to strings. Each present `inputs` or `outputs` value must be a JSON array of unique type identifiers encoded as a string. An omitted field means no declared relationships for that role. There is no `alps.` prefix, duplicate `id`, or per-document schema version. The same type can appear in both I/O roles when work examines and updates it. Conditions governing use belong in the body; do not maintain a second I/O list there.

## Shared definitions

Every referenced type must have a definition. `release-candidate` refers directly to `references/artifacts/release-candidate.md`:

```markdown
---
kind: product
---

# Release candidate

The revision submitted for checking and release. A version or digest identifies it uniquely.
```

The example's input also needs `references/artifacts/design-description.md`:

```markdown
# Design description

The agreed change's scope, intended behavior, and applicable constraints used for implementation and verification. Its revision and agreement status must be identifiable.
```

The filename is the identifier, the H1 is the display name, and the remaining body defines the meaning and necessary properties. Type identifiers contain Unicode letters and numbers, dots, underscores, or hyphens, start with a letter or number, and contain no path separators. References match identifiers exactly, not display text. Missing definitions are errors; readers must not invent types.

`kind`, when needed, is `information`, `product`, or `service`. More detailed sections and links to machine-readable schemas can be included when the work needs them. Neither a schema nor a separate `INTERFACE.md` is mandatory. Referenced definitions form the model's artifact types; no manifest registry duplicates them.

## Workspace and editing

A workspace can contain the Plugin itself. Otherwise `model` in `alps-harness.yaml` points to its `plugin.json`, relative to the workspace. Omit `model` when the manifest is at the workspace root. For example:

```yaml
language: ja
artifacts:
  release-candidate:
    paths: ["releases/*/candidate.json"]
```

The workspace maps type identifiers to concrete paths. It cannot override type meaning or kind, map Processes to different Skills, or add Skill search roots. Agent configuration, guidance, schedules, and attachments remain workspace concerns. Runtime records are not model definitions or Plugin distribution content.

Authoring updates the listed Markdown sources and manifest membership. Preserve unrelated prose and inspect affected references when changing identifiers, types, or membership. Review and validate the resulting package before delivery. `process-model.yaml`, alternative model extensions, Skill-name guessing, and duplicated I/O authorities are not part of this profile. Migration, when requested, changes the canonical sources explicitly and accounts for existing records and references; loading does not fall back to an old format.
