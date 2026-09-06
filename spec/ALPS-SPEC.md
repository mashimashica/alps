# ALPS Specification

[Japanese translation](locales/ja/ALPS-SPEC.md)

## 1. Scope and precedence

This specification integrates Process Description and Agent Work System design in Agent Skills. The [Process Framework](process-framework.md) governs Process meaning, relationships, application, and evaluation. [Design Principles for Agent Work Systems](agent-work-system-design.md) governs the configuration and interaction of agents, tools, information resources, and execution environments. Each source takes precedence within its subject. This specification defines their correspondence and application to Skills.

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

## 3. Work descriptions and supporting systems

Process Description design evaluates whether the meaning, relationships, and applicable conditions of work are coherent and sufficient to understand, apply, and evaluate it. Agent Work System design evaluates the configuration that realizes the work and the evidence of its feasibility and effectiveness. Necessary work detail, methods, and order remain part of the Process Description as defined by the Framework.

When a supporting configuration is described, the agents, tools, and execution environment used to perform work must be related to its description as Enablers. Resources must be classified by the role they play in the particular work: a script used for processing is an Enabler, while a script being produced is an Output. Information examined or transformed can be Input, and information that directs or evaluates work can be Control; its role must be identified for the relevant relationship.

Where a Task relies on tools, the correspondence must explain how the tool operations contribute to the work and how their results support Outcome assessment. Task boundaries and tool interfaces must be designed for their respective responsibilities. The meaning of Process Inputs and Outputs must be related to tool arguments and returned information where needed to perform or evaluate the work.

A work system may support multiple Process Descriptions or Skills, and a description or Skill may be supported by different configurations. Shared work meaning must use a common source description. A supporting design must refer to that source instead of independently maintaining its Purpose and Outcomes. Choices of implementation must preserve applicable Outcomes and conditions; changes to work meaning must follow the Framework's change principles.

Either design responsibility may be undertaken when its basis is sufficient. A work-system design can reveal assumptions that require revisiting the work description. The [work-system design Skill](../skills/design-agent-work-system/SKILL.md) is itself a Process Description: its own meaning follows the Framework, and its design subject is governed by the work-system design principles.

## 4. Sources, resources, and implementation

Each Skill carrying a Process Description must identify one description as the reference point for its meaning. Translations, summaries, and linked materials must make their relationship to that description clear and preserve its meaning and normative force.

A Skill must identify the role and conditions of use of each supporting resource it requires. Necessary references must be accessible under the intended distribution arrangement. Packaged relative links must resolve within that arrangement; external references must identify the intended source and any access conditions. Apply the Framework's rules when a required reference cannot be confirmed.

`SKILL.md` and necessary reference resources must make the work, judgment criteria, applicable conditions, and use of required tools available at the point of use. Existing CLIs or APIs may be used directly. Processing that needs to be bundled with a Skill must be placed in that Skill's `scripts/` directory and documented according to the [Agent Skills script guidance](https://agentskills.io/skill-creation/using-scripts). Tool responsibilities, invocation, arguments and returned information, dependencies, failure handling, and state-changing effects must be described as required by the work-system design principles.

Bundled scripts that perform the target work belong to the target Skill. Scripts included in a design Skill must support the design or evaluation work described by that Skill. The implementation and evaluation of a supporting system must remain within the requested scope; performing the target work is a distinct application with its own applicable conditions.

## 5. Evaluation

Evaluation must distinguish the Process Description's semantic validity, whether the tools and connections meet their specifications, and the work system's effectiveness in representative applications. For each judgment, identify the applicable criteria, evidence, unperformed checks, and limits. Apply the Framework to Outcome judgments and the work-system principles to configuration and interaction evaluation.

Agent Skill and Plugin form checks assess formats, discovery consistency, source identity, and resource availability. They provide evidence about distribution and use, while semantic review and representative work assess meaning and effectiveness.

For support, see [design-process-description](../skills/design-process-description/SKILL.md), [design-agent-work-system](../skills/design-agent-work-system/SKILL.md), the [minimal Process template](../skills/design-process-description/references/SKILL-template.md), and the [working example](../examples/README.md). Templates and examples are informative.
