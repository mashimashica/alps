# Unreleased Process Description redesign

[Japanese translation](locales/ja/unreleased-redesign.md)

This is an unreleased breaking redesign intended for the next MINOR after 0.5.0. `VERSION` and every manifest version remain unchanged. The redesigned content is identified by its commit until it is released.

ALPS now focuses on designing and reviewing the meaning of work through a Process Description. The [Framework](../spec/process-framework.md) defines that meaning; the [Specification](../spec/ALPS-SPEC.md) maps it to Agent Skills.

## Compatibility changes

| Previous surface in the baseline files | Current design |
| --- | --- |
| `alps-reference-model`, `define-alps`, `apply-alps`, and `manage-alps` | Only `design-process-description` is distributed. Old names have no aliases. |
| Fixed five-stage lifecycle and three required reference Processes | No ALPS lifecycle or management routing requirement. |
| `skill:` references, Logical Package Scope, and Package Binding | Ordinary links or identifying information, with environment version, commit, or digest when needed. |
| `metadata.alps.kind` and type-specific invocation rules | Ordinary reference materials remain semantically distinct from Process Descriptions. Old metadata is not interpreted. |
| ALPS-specific Conformance schemes and discovery suffix claims | Separate review of descriptions, execution results, and applicable requirements. Mandatory conditions are not waived by an assessment choice. |
| `process_instance_record.py`, `process-instance-record/1`, and record bindings | No ALPS execution record format, CLI, or converter. Storage and records belong to the environment. |
| Comprehensive record and Skill templates | A minimal description template and a small set of examples. |

Existing invocations, references, and integrations that depend on the removed surfaces need deliberate review before using this redesign. A previously issued claim does not establish satisfaction of the current description or requirements. Existing user-authored records and descriptions are neither transformed nor deleted. No compatibility layer or alternate legacy implementation is supplied.

## Process meaning

The Framework retains the distinction between purpose, result conditions, and Outputs; the cohesive relationship between Activities and Tasks; independently assessable Outcomes; boundary roles; Traceability; application relationships; and the distinction between instantiation and changing what applies. Optional detail continues to use defined meanings. Models and views retain distinct roles, and Capability, execution, and requirements remain separate evaluation concerns.

The semantic changes are deliberate:

- An Input can supply information for examination without itself being modified; Outputs can update shared information. Relationships include repeated use and update as well as handoffs.
- A View is reference material and need not define its own Process Purpose and Outcomes. Independently defined work still needs a Process Description.
- Applicable requirements retain their force regardless of the chosen assessment. The Framework does not prescribe a general execution pattern or a management route for deciding flow and changes.
- Names and result statements preserve their semantic functions without mandatory English naming or tense conventions.

## Distribution and review

The complete Plugin retains the root manifest, Claude/Cursor/Codex adapters, presentation assets, English authority, and Japanese counterparts. Keep `spec/` beside `skills/` so the Skill's mandatory references are available. Repository-development Skills remain separate.

Repository tests and format checks assess distributable form and integrity. Semantic review separately checks the purpose and sufficient Outcomes, necessary detail, references and uncertainty, shared-information relationships, contextual conditions, and locale equivalence. An installed package must be checked against its actual contents; a version string alone does not identify an uncommitted development snapshot.
