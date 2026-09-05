# ALPS Specification

[Japanese translation](locales/ja/ALPS-SPEC.md)

## 1. Scope and authority

This specification maps a Process Description to an Agent Skill. The [Process Framework](process-framework.md) defines Process meaning, relationships, normative language, and evaluation. It takes precedence over this specification.

The [Agent Skills format](https://agentskills.io/specification) governs the physical `SKILL.md` form. The correspondence below applies to Skills that describe Processes.

## 2. Correspondence

| Agent Skill content | Process meaning |
| --- | --- |
| Frontmatter `name` | Skill identifier used for discovery. |
| Frontmatter `description` | Summary of the work and when the Skill applies. |
| Body title | Process Name. |
| Purpose and Outcomes in the body | The objective and observable result conditions of the work. |
| Other body content and linked resources, when needed | Work detail, boundary elements, application conditions, or reference information with the meanings defined by the Framework. |

The body must contain Name, Purpose, and one or more Outcomes. Additional elements are included according to the detail needed. Activities and Tasks can be expressed through headings and statements that make their grouping, contribution, and normative force clear. The document structure must preserve the distinction between work relationships and execution order.

Frontmatter and Host displays must remain consistent with the description's meaning and scope. Discovery information summarizes the description; it does not replace it. Loading a Skill does not establish that its work has been performed. Reference material must remain distinguishable from a Process Description.

## 3. Authority and resources

Each Skill carrying a Process Description must have one identifiable authoritative description. Translations, summaries, and linked materials must preserve its meaning and normative force, with their relationship to the source clear.

A Skill must identify the role and conditions of use of each supporting resource it requires. Necessary references must be accessible under the intended distribution arrangement. Packaged relative links must resolve within that arrangement; external references must identify the intended source and any access conditions. Apply the Framework's rules when a required reference cannot be confirmed.

Review of Process meaning and review of Agent Skill form are distinct. The latter checks the applicable format, discovery consistency, source identity, and availability of required resources.

For authoring support, see [design-process-description](../skills/design-process-description/SKILL.md), its [minimal template](../skills/design-process-description/references/SKILL-template.md), and its [examples](../skills/design-process-description/references/examples.md). The template and examples are informative.
