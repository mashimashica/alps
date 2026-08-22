# ALPS Markdown Repository and Agent Plugins Binding 1.0

## Status and authority

This document defines the repository and Agent Plugins environment binding identified as `alps-markdown-agent-plugins/1.0`.

The Process Framework and the ALPS Specification define the meanings of Process, Process Description, Process Instance, Process Model, Process Reference Model, Process View, Skill, Skill Package, Tailoring, Conformance, and related concepts. This binding defines Markdown representation, repository locations, resolution behavior, compatibility declarations, and mechanical preflight rules. It must not change the meaning or normative force of an asset.

In this binding, **must**, **must not**, **should**, **should not**, and **may** have the meanings inherited from the Process Framework.

## 1. Scope

This binding applies when an ALPS package represents one or more of the following assets in Markdown:

- a default Process Model or Process Reference Model;
- a named Process Model or Process Reference Model;
- a Process View;
- a localization of one of those assets; or
- an Environment Binding declaration that points to those assets.

A Process Model, Process Reference Model, or Process View is not independently invoked as a Skill. Skill Packages remain under `skills/` and use their authoritative `SKILL.md` descriptions.

## 2. Canonical locations

| Asset | Canonical location | Cardinality |
|---|---|---:|
| Default Process Model or Process Reference Model | `.alps/MODEL.md` | 0..1 |
| Named Process Model or Process Reference Model | `.alps/models/<model-id>/MODEL.md` | 0..* |
| Process View | `.alps/views/<view-id>/VIEW.md` | 0..* |

The following rules apply:

1. `<model-id>` and `<view-id>` must be lowercase kebab-case identifiers.
2. `.alps/MODEL.md`, when present, is the package's default Model entry point.
3. A default Model must not be duplicated under `.alps/models/`.
4. A Model or View must not be placed under `skills/`.
5. Each asset is independently identified and versioned, even when the repository is released as one unit.
6. A repository may omit Models and Views entirely.

## 3. Localization

The authoritative language is declared in frontmatter. An English authoritative asset may have localizations at:

```text
.alps/references/locales/<locale>/MODEL.md
.alps/models/<model-id>/references/locales/<locale>/MODEL.md
.alps/views/<view-id>/references/locales/<locale>/VIEW.md
```

A localization must identify the authoritative asset by a relative link. It must not change identifiers, source references, compatibility requirements, normative force, or meaning. When a localization conflicts with its authoritative asset, the authoritative asset governs.

## 4. Common frontmatter

A bound Model or View must begin with YAML frontmatter containing simple scalar values for these keys:

| Key | Requirement |
|---|---|
| `kind` | `process-model`, `process-reference-model`, or `process-view` |
| `id` | Lowercase kebab-case asset identifier |
| `name` | Human-readable asset name |
| `version` | Semantic version |
| `status` | `draft`, `active`, `deprecated`, or `retired` |
| `binding` | `alps-markdown-agent-plugins/1.0` |
| `alps-requires` | Supported ALPS semantic-version range |
| `authoritative-language` | BCP 47 language tag of the authoritative asset |

The default Model must additionally declare `default: true`. A named Model may declare `default: false` or omit `default`. A Process View must declare a comma-separated `source-models` value containing one or more Model references.

Frontmatter is binding metadata and must not replace the asset body.

## 5. Process Model and Process Reference Model representation

A `MODEL.md` body must contain:

- a level-one heading equal to the declared `name`;
- `## Purpose`;
- `## Scope`;
- `## Included Processes`;
- `## Relationships`;
- `## Selection and Application`;
- `## Compatibility`; and
- `## Management`.

A Model should also contain `## Framework-Level Controls and Enablers`, `## Process Views`, and `## Known Gaps` when those matters apply.

### 5.1 Included Processes table

The `Included Processes` section must contain a Markdown table with these columns:

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|

`Skill Source` uses one of these forms:

- `local:<package-relative-directory>` — a Skill Package in the same package;
- `plugin:<plugin-id>/<skill-id>` — a Skill provided by another installed plugin; or
- `uri:<absolute-uri>` — an externally managed source.

A local source must resolve to a directory containing an authoritative `SKILL.md`. An external source can remain unresolved during package-only validation, but its plugin or URI identity must be preserved.

`Status` is one of `adopted`, `candidate`, `deprecated`, or `retired`.

### 5.2 Relationships table

The `Relationships` section must contain a Markdown table with these columns:

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|

The table records representative Output/Input handoffs. It does not impose execution order. The same Process may appear as both provider and recipient, and relationships may be concurrent, iterative, or recursive.

### 5.3 Selection and application

A Model must state that application is determined from the context, target Outcomes, Controls, Constraints, risk, and managed Tailoring decisions. Clause order and table order must not be interpreted as a life-cycle sequence unless an explicit Constraint states one.

### 5.4 Framework-level declarations

When a Model declares a Framework-level Control or Enabler, it must state its scope, exceptions, whether Tailoring is permitted, and how conflicts or missing availability are handled.

## 6. Process View representation

A `VIEW.md` body must contain:

- a level-one heading equal to the declared `name`;
- `## Purpose`;
- `## Outcomes`;
- `## Stakeholders and Concerns`;
- `## Source Models`;
- `## Included Activities and Tasks`;
- `## Handoffs`;
- `## Application Guidance`; and
- `## Compatibility and Conformance`.

### 6.1 Included element table

The `Included Activities and Tasks` section must contain a Markdown table with these columns:

| View Element ID | Origin | Source Process | Source Element | Treatment | Guidance |
|---|---|---|---|---|---|

`Treatment` must be one of:

- `selected` — retains the source element and its normative meaning;
- `adapted` — identifies a changed presentation or application of a source element without changing the source Process Description; or
- `new` — exists only in the Process View.

For every `selected` or `adapted` row, `Source Process` and `Source Element` must identify the source. An `adapted` or `new` element does not contribute to Conformance with a source Process unless managed Tailoring or formal adoption has incorporated it into that Process.

### 6.2 Handoffs

The `Handoffs` section uses the same provider Output to recipient Input table structure as a Model. The table may select Model relationships or add View-specific relationships. A View-specific relationship must be labeled in `Conditions`.

## 7. Compatibility

`alps-requires` declares the ALPS version range with space-separated comparators, for example `alps-requires: ">=0.4.0 <0.5.0"`.

The binding tools support `>`, `>=`, `<`, `<=`, `=`, and `==` comparators over three-part semantic versions. Pre-release and build metadata are permitted in an asset's own `version`, but compatibility evaluation compares the numeric major, minor, and patch components.

A package is compatible only when:

1. the executing ALPS version satisfies `alps-requires`;
2. the asset's `binding` equals a supported binding identifier;
3. every required local Skill source resolves;
4. required source Models resolve for a Process View; and
5. any declared external dependency is available or explicitly accepted as unresolved for the current preflight mode.

Compatibility is a precondition for application, not evidence that the Model or View is suitable for a particular request.

## 8. Resolution

Resolution proceeds as follows:

1. Discover `.alps/MODEL.md` as the default Model when present.
2. Discover named Models under `.alps/models/*/MODEL.md`.
3. Discover Process Views under `.alps/views/*/VIEW.md`.
4. Validate binding metadata and ALPS compatibility.
5. Resolve local Skill sources relative to the package root.
6. Resolve plugin sources through installed plugin roots supplied by the execution environment.
7. Resolve Process View source Models by asset ID or canonical path.
8. Preserve unresolved external identities in the resolution report.
9. Reject ambiguous duplicate asset IDs.

The resolver must not silently substitute another Skill, Process, Model, Process View, version, or source.

## 9. Agent Plugins extension

A portable Agent Plugins manifest may advertise the default entry point with the namespaced extension:

```json
{
  "extensions": {
    "io.github.mashimashica.alps": {
      "binding": "alps-markdown-agent-plugins/1.0",
      "defaultModel": ".alps/MODEL.md",
      "alpsVersion": "0.4.0"
    }
  }
}
```

Clients that do not recognize the extension may ignore it. The extension is a discovery hint; `.alps/MODEL.md` remains the authoritative Model asset.

A dependent plugin must document installation prerequisites and use compatibility preflight before applying its Model.

## 10. Mechanical preflight

`scripts/check_model_view.py` checks binding structure and `scripts/resolve_model_view.py` performs package-level discovery, compatibility evaluation, and source resolution.

Mechanical preflight does not establish semantic adequacy of a Purpose or Outcome, correctness or completeness of Process selection, Outcome achievement, Execution Conformance, fitness for an application context, or adoption approval. Those judgments are performed through the ALPS Reference Model Processes.

## 11. Change and release

Process Models, Process Reference Models, and Process Views are managed assets. Changes must be assessed for impact on included Processes, Skill mappings and versions, Output/Input handoffs, source Models and Process Views, Framework-level Controls and Enablers, compatibility ranges, localizations, and dependent packages.

A changed Model or View must be rechecked and semantically reviewed before adoption. Release publication, Git tagging, and registry publication remain separate actions from preparation of a release candidate.
