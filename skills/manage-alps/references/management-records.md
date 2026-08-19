# Management Process Record Aids

## Contents

- [Use](#use)
- [Record Basis](#record-basis)
- [Skill Asset Register](#skill-asset-register)
- [Framework Declaration](#framework-declaration)
- [Tailoring Decision](#tailoring-decision)
- [Assessment and Improvement](#assessment-and-improvement)
- [Decision Gate](#decision-gate)
- [Change, Retirement, and Handoff](#change-retirement-and-handoff)
- [Conformance Claim](#conformance-claim)

## Use

These blocks are optional aids. Select those justified by the application context and risk. Embed the needed blocks in a general Process Instance Record, or keep them as separate management Outputs referenced from that record. Record structure and state vocabulary can be selected to suit the application context.

Record the source and baseline of this management Process separately from the source and baseline of the managed asset. The first determines the Outcomes and Tasks used to assess this Process instance; the second identifies the asset being governed. When traceability is needed, use a resolvable baseline reference and, where useful, include the relevant statement. Reconfirm the correspondence when either baseline changes.

Record decisions, rationale, assumptions, evidence, impacts, communication, reverification, and handoffs as applicable, and include only the blocks in use. Mark missing information as unverified, not applicable, pending, or another context-appropriate term.

Instance-specific success criteria, Activities, Tasks, or other details that do not change the meaning, scope, or normative force of the managed baseline constitute Instantiation. Removing, changing, or adding an Outcome, Activity, Task, representative Input, or representative Output in a way that changes those properties is Tailoring and requires a Tailoring decision.

## Record Basis

Use this optional block when these aids are kept as a separate management Output. Omit it when the containing Process Instance Record already supplies the same basis.

```markdown
# Record Basis

- Record purpose and current status:
- Management Process source and baseline:
- Target asset and managed-asset source and baseline:
- Application context and scope:
- Initiating need or event:
- Known limitations and unresolved information:
```

## Skill Asset Register

| Item | Content |
|---|---|
| Asset name and local reference, if needed | |
| Asset type | |
| Managed-asset source and baseline | |
| Current management disposition | |
| Purpose and scope | |
| Discovery information and location | |
| Verification evidence | |
| Dependencies and users | |
| Applicable Controls and Constraints | |
| Whether and under what conditions Tailoring is permitted | |
| Relevant changes | |
| Review or reverification need and result | |
| Retention, reference, and recovery conditions | |

## Framework Declaration

| Type | Statement or source | Scope | Exceptions | Whether and under what conditions Tailoring is permitted | Rationale |
|---|---|---|---|---|---|
| Control or Enabler | | | | | |

Apply Framework elements according to their declared scope, exceptions, and Tailoring conditions. Classify an information resource as a Control, Input, Output, or Enabler according to its function during execution.

## Tailoring Decision

Use this block only when Tailoring is performed.

```markdown
# Tailoring Decision

- Target asset and managed-asset baseline:
- Application context and period:
- Outcome, Activity, Task, Input, or Output affected:
- Source statement or previous definition:
- Tailored statement or resulting definition:
- Nature and scope of the change:
- Risks, requirements, and complexity:
- Available capabilities and resources:
- Relevant standards:
- Applicable Controls and Constraints:
- Stakeholder expectations and risk tolerance:
- Candidate Skills or lifecycle models evaluated and comparison:
- Affected parties and Input obtained:
- Facts and evidence:
- Assumptions and decision criteria:
- Decision and rationale:
- Decision status and effective conditions:
- Decision authority and approval evidence:
- Outcomes and Activity/Task requirements remaining in scope:
- Required rigor:
- Impact on Inputs, Outputs, and exchanges:
- Monitoring and performance-assessment method:
- Review conditions:
- Conformance claim, if any:
```

For several changes, repeat the block or add a local table that relates each source statement, resulting statement, rationale, and remaining requirement.

Reusing an unassessed tailored baseline, applying measures uniformly without regard to context, applying a single measure, risk, or Control to every target, and excluding affected parties are representative pitfalls described in PF 7.3.

## Assessment and Improvement

```markdown
# Skill Assessment and Improvement

- Target asset, managed-asset baseline, and assessment period:
- Assessment criteria:
- Measures and definitions:
- Data scope and limitations:
- Outcome achievement:
- Performance and effectiveness:
- Strengths and weaknesses:
- Lessons learned:
- Exchange inconsistencies and rework:
- Comparison basis and results for performance, effectiveness, conformance, benefits, and costs:
- Improvement opportunities:
- Priorities and their criteria:
- Decided improvements:
- Implementation result:
- Change and reverification requests:
- Unresolved risks:
- Evidence:
```

## Decision Gate

Use this block only when a Decision Gate is applicable.

```markdown
# Management Decision Gate

- Target and managed-asset baseline:
- Proposed action:
- Basis for requiring the Gate:
- Decision criteria:
- Evidence:
- Impacts and residual risks:
- Decision and any conditions:
- Rationale and assumptions:
- Required communication:
- Required reverification:
- Retention, reference, and recovery conditions:
- Authority or approval evidence:
```

Determine whether a Decision Gate is required from irreversibility, impact, applicable Controls and Constraints, and the execution environment. When a Decision Gate is used, record the decision to apply it, the Decision Criteria, the decision made, and any conditions.

Record permanent deletion as a management action distinct from retirement and relate it to applicable execution-environment Controls and Constraints for deletion, authority, retention, reference, and recovery. These requirements arise from the execution environment rather than from ALPS itself; where applicable, they remain part of the declared execution scope and assessment. When they require a Decision Gate, record satisfaction of the Gate conditions and necessary authority.

## Change, Retirement, and Handoff

Use the applicable fields for a change, retirement, or transfer to the definition or application Process.

```markdown
# Change, Retirement, and Handoff

- Target asset and managed-asset baseline:
- Change or retirement decision:
- Affected Skill Descriptions and accompanying resources:
- Impacts on dependencies and users:
- Communication performed or required:
- Reverification need and result:
- Handling of new invocations:
- Retention, reference, and recovery provisions:
- Recipient and information handed off:
- Meaning, scope, baseline, and readiness of the handoff:
- Actual result and evidence:
- Limitations and unresolved risks:
```

For retirement, distinguish stopping new invocations, impacts on dependencies, communication to users, retention for reference, and recovery. Record permanent deletion separately from retirement and relate it to applicable execution-environment Controls and Constraints.

## Conformance Claim

Omit this block when no Process Conformance is claimed. When making a claim, record its target, scope, management Process baseline, whether Outcomes, Tasks, or both form the basis, the conclusion, evidence, and limitations.

- Full Conformance to Outcomes requires evidence that every Outcome of the referenced management Process baseline is achieved.
- Full Conformance to Tasks requires evidence that every requirement contained in Activities and Tasks of that baseline is satisfied.
- To claim Tailored Conformance when the selected Full Conformance basis is not satisfied, declare the tailored Process and scope and demonstrate satisfaction of every Outcome and Activity/Task requirement that remains within that scope.
- Do not claim independent Process Outcome Conformance for an individual Activity alone.
- Assess Capability separately from Conformance.
