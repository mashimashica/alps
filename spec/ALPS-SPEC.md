# ALPS Specification

[Japanese translation](locales/ja/ALPS-SPEC.md)

## 1. Scope and authority

ALPS applies the [Process Framework](process-framework.md) to the design and review of Process Descriptions carried by Agent Skills. The Framework supplies the Process concepts, normative language, and rules for boundaries, references, change, and evaluation. It takes precedence over this specification.

ALPS supplies one Skill for that work: [design-process-description](../skills/design-process-description/SKILL.md). Its description is subject to the same rules as the descriptions it helps produce. ALPS provides no execution engine, scheduler, asset-management system, approval system, or certification regime. Execution and persistence are responsibilities of the applying environment.

## 2. Mapping to Agent Skills

The [Agent Skills format](https://agentskills.io/specification) governs the physical `SKILL.md` form. ALPS adds the following correspondence, not a replacement format.

| Agent Skill content | Process meaning |
| --- | --- |
| Frontmatter `name` | Skill identifier used for discovery. |
| Frontmatter `description` | Summary of the work and when the Skill applies. |
| Body title | Process Name. |
| Purpose and Outcomes in the body | Why the work is undertaken and the observable conditions for success. |
| Other body content and linked resources, when needed | Necessary detail, conditions, or clearly identified reference material. |

The frontmatter must remain consistent with the authoritative description and must not replace it. The body must contain Name, Purpose, and one or more Outcomes as defined by the Framework. ALPS requires no other universal field or section. Ordinary Agent Skill metadata does not add Process requirements.

Each Skill carrying a Process Description must have one identifiable authoritative description of that Process. In this distribution, the root `skills/design-process-description/SKILL.md` is the English authority for that Process. The Japanese counterpart is a translation. Discovery strings, Host displays, templates, and examples must preserve the authority and scope of the source they describe.

Loading a Skill or reading a summary does not establish that work has been performed. Reference material that organizes Processes or presents a View must remain distinguishable from a Process Description; it needs no ALPS-specific type declaration.

## 3. Resources and distribution

A Skill must identify the role and conditions of use of each supporting resource it requires. Necessary references must be available from the distributed package using ordinary links or identifying information. An unresolved required reference must be reported with the affected work; a different version or same-named source must not be substituted.

The ALPS Plugin includes `skills/`, the shared `spec/` sources and their Japanese translations, and the applicable Host manifests and presentation assets. The Skill's relative specification links depend on this Plugin root layout. Distributing only the Skill directory does not provide those required sources. Repository-development Skills under `.agents/skills/` are not Plugin Skills.

Host manifests retain their Host-specific forms. They locate or present content and must not redefine Process meaning. The repository's integrity checks assess this distribution boundary, paths, resources, translations, and version consistency. They do not determine semantic correctness.

## 4. Design and review resources

The [minimal template](../skills/design-process-description/references/SKILL-template.md) starts with ordinary frontmatter and Name, Purpose, and Outcomes. The [examples](../skills/design-process-description/references/examples.md) show when to add detail and how to review uncertain or unsuccessful cases. Both are informative; they must not introduce universal requirements.

Review of a Process Description must apply the Framework to the intended work and scope. Review of its Agent Skill form must separately check the applicable format, discovery consistency, required resources, and authority. A favorable result in one review must not be substituted for another, for execution evidence, or for satisfaction of external requirements.
