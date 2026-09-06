# Design prompts and examples

[Japanese translation](locales/ja/examples.md)

These are informative aids for [Agent Work System Design](../SKILL.md). Select the detail needed for the requested design. A configuration can be explained in the target Skill and its existing resources; the prompts below do not require a separate document.

## Starting a description

Use the [minimal Process template](../../design-process-description/references/SKILL-template.md) when the target work needs an Agent Skill description. For a supporting design, refer to that description and explain the necessary responsibilities and interactions. Add only detail needed to use, realize, or evaluate the configuration.

Useful questions include: Which source describes the work and its conditions? Which capability performs each responsibility? Where is contextual judgment needed? What information crosses each interface? What evidence supports the work's results? What remains unconfirmed?

## Existing tools and a new combination

For a repository maintenance task, an existing search tool locates candidate files and an existing compiler checks changes. The agent interprets the requested behavior and selects the affected code. A known sequence of generated-file checks can be exposed as one existing build command. Its internal checks remain separately maintainable while the agent selects when that operation applies. No additional script is needed when the build command already provides the required behavior and diagnostics.

## A bundled processing tool

The [service-change example](../../../examples/README.md) uses a target Skill with a script for CSV validation, measurement aggregation, and threshold comparisons. These calculations form one public operation. The agent selects the applicable measurement pair and criteria, assesses comparability, interprets the evidence, and determines whether further measurement is needed. The example's source description holds its Purpose and Outcomes; its supporting design refers to them.

## A tool that changes state

A calendar API can combine conflict detection and event creation in one operation if its guarantees meet the work's requirements. The design still needs to state who can create which events, what state can change, and how concurrent changes affect the result. If a request times out after a possible creation, a supported request identifier and status lookup can establish the effect before retrying. When those capabilities are unavailable, the result remains uncertain until the state is checked; an agent must not infer that a timeout means nothing happened.

## Changed capabilities

After a model update, a design review may find that instructions compensating for weak tool selection are unnecessary. Evaluate a simpler interaction on the affected work. Retain the domain criteria that determine which records may be changed, and retain evidence of the actual effects. A shorter prompt or fewer calls alone does not establish improvement.
