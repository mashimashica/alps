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

## Capabilities, criteria, and limits

The same measurement operation has several relationships to the [service assessment](../../../examples/assess-service-change/SKILL.md):

| Aspect | Role in the work | Design and evaluation consequence |
| --- | --- | --- |
| Reading measurements, calculating metrics, and comparing values | The script supplies an Enabler. | Check that the capability realizes its specified behavior. |
| The pilot's metric definitions and acceptance limits | These supply Controls; the script implements their calculations and comparisons. | Relate the implemented criteria to the applicable [pilot conditions](../../../examples/assess-service-change/references/pilot-context.md). |
| The required CSV encoding and columns | These constrain use of this tool interface. | Establish whether the available information can be supplied through that interface without changing its meaning. |
| Returned measurements and comparison results | These provide evidence for the assessment. | Interpret them together with the measurement context and applicable criteria. |

The tool's capability and its implementation of criteria are distinct relationships. A rule can be represented in configuration or code when its meaning and applicable scope are identifiable. The pilot example passes acceptance limits explicitly; a tool with fixed criteria would instead need an identifiable basis for those criteria and their applicability. Changing a threshold affects the judgment basis, while changing CSV parsing without changing accepted information or behavior can be an implementation change.

If an available API returns at most 1,000 records per page, that limit applies to the call. A work requirement to assess all records still calls for complete coverage, using pagination or another adequate capability. Evidence from the first page establishes only that page's results. The limit does not establish that the remaining records are irrelevant.

## A tool that changes state

A calendar API can combine conflict detection and event creation in one operation if its guarantees meet the work's requirements. The design still needs to state who can create which events, what state can change, and how concurrent changes affect the result. If a request times out after a possible creation, a supported request identifier and status lookup can establish the effect before retrying. When those capabilities are unavailable, the result remains uncertain until the state is checked; an agent must not infer that a timeout means nothing happened.

## Changed capabilities

After a model update, a design review may find that instructions compensating for weak tool selection are unnecessary. Evaluate a simpler interaction on the affected work. Retain the domain criteria that determine which records may be changed, and retain evidence of the actual effects. A shorter prompt or fewer calls alone does not establish improvement.

Changes to the [service assessment](../../../examples/assess-service-change/SKILL.md) can affect different parts of its evidence:

| Hypothetical change | Design response and evidence scope |
| --- | --- |
| A replacement CLI accepts the same measurements and limits through renamed arguments, preserving calculations and their meanings. | Adapt invocation and check the affected interface and agent interpretation. Applicable measurement evidence remains usable; an interface change alone does not call for fresh service measurements. |
| Within an authorized revision of the pilot conditions, the candidate p95 limit becomes 150 ms instead of 200 ms; measurement conditions are unchanged. | Identify the changed Control and its scope. Retain the applicable measured p95 of 160 ms and reassess against 150 ms: the candidate fails this criterion. Other still-applicable findings remain supported. An accurate negative assessment can satisfy the assessment work without making the candidate suitable. |
| The intended pilot changes from one to ten concurrent clients. | Reconsider the comparability and applicability of the one-client evidence. Obtain a basis for the affected judgment; do not claim ten-client suitability from a successful calculation on the old measurements. Retain the old evidence for the conditions it actually covers. |

The second and third changes concern the work's applicable conditions and follow the Framework's change principles. They are not reasons to redefine success silently to fit a tool or to repeat unaffected checks.
