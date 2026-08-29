# ALPS Management Process Record Aids

These blocks are optional aids for recording management of ALPS representations and their application. Select only those justified by the application context and risk. Record the ALPS Management Process baseline separately from the baseline of the representation being governed.

## Managed Representation Register

| Item | Content |
|---|---|
| Representation name and reference | |
| Representation kind: Process / Process Model / Process Reference Model / Process View | |
| Managed baseline | |
| Current management disposition | |
| Purpose or concern and scope | |
| Discovery and loading information | |
| Mandatory references and resolution status | |
| Verification evidence | |
| Dependencies, referenced Processes, and users | |
| Applicable Controls and Constraints | |
| Tailoring conditions, when applicable | |
| Relevant changes and affected representations | |
| Review or reverification need and result | |
| Retirement, retention, and recovery conditions | |

## Reference-Integrity and Change Record

```markdown
# Reference-Integrity and Change Record

- Target representation and baseline:
- Representation kind:
- Proposed or observed change:
- Authoritative semantic center affected:
- Referencing or referenced representations affected:
- Canonical Skill references affected:
- Compatibility or resolution impact:
- Required redefinition or reverification:
- Communication and migration impact:
- Decision and rationale:
- Evidence and unresolved risks:
```

A change that alters the authoritative meaning of a representation is handed to the ALPS Definition Process for redefinition and verification. A management decision does not silently redefine the authoritative representation.

## Tailoring Decision

Use this block for context-specific Tailoring of a Process or applicable Process Model selection. A Process View can inform the decision, but View-specific or modified Activities and Tasks do not themselves establish Tailoring. Route an authoritative source-Process change to the ALPS Definition Process as Process redefinition.

```markdown
# Tailoring Decision

- Target Process or applicable model and managed baseline:
- Application context and scope:
- Candidate Processes or lifecycle models evaluated, criteria, and result:
- Change classification: context-specific Tailoring / authoritative redefinition
- Elements affected:
- Source statements or relationships:
- Tailored result:
- Process Name before and after Tailoring, when changed:
- Name consistency with Purpose and Outcomes, and Traceability to the source Process:
- Applicable Controls and Constraints:
- Risks and evidence:
- Affected parties and Input obtained:
- Decision and rationale:
- Every Outcome remaining in scope and every in-scope requirement stated with `must` or `must not` in an Activity or Task:
- Impact on Inputs, Outputs, handoffs, and references:
- Monitoring or assessment method:
- Review conditions:
- Conformance claim, if any:
```

## Representation and Process Assessment and Improvement

```markdown
# Representation and Process Assessment and Improvement

- Target representation and baseline:
- Representation kind:
- Representation-assessment criteria:
- Evidence scope and limitations:
- Reference integrity and resolvability:
- Internal consistency:
- For a Process representation: Description Conformance and usability:
- Described Process and baseline, when separately assessed:
- Applicable Process Conformance claim and evidence, when assessed:
- Process Instance identity and baseline, when separately assessed:
- Execution Conformance, Outcome achievement, performance, and effectiveness, when assessed:
- For a Process Model: Process coverage, relationship coherence, resolvability, and applicability to its intended Purpose:
- For a Process Reference Model: Process identification, Name/Purpose/Outcomes consistency, relationship coherence, resolvability, and suitability as a frame of reference:
- For a Process View: Purpose and Outcomes, source provenance and Traceability for referenced elements, preservation of source meaning, handoffs, application guidance, and usefulness:
- Lessons learned:
- Improvement opportunities and priorities:
- Decided action:
- Required redefinition or reverification:
- Unresolved risks:
```

## Decision Gate

```markdown
# Management Decision Gate

- Target representation and baseline:
- Proposed action:
- Basis for requiring the Gate:
- Decision criteria:
- Evidence:
- Impacts and residual risks:
- Decision and conditions:
- Rationale and assumptions:
- Required communication or reverification:
- Authority or approval evidence:
```

## Retirement and Handoff

```markdown
# Retirement and Handoff

- Target representation and baseline:
- Retirement decision and effective conditions:
- Affected references, dependencies, and users:
- Handling of future activation or invocation, as applicable:
- Communication performed or required:
- Retention and recovery provisions:
- Recipient Process and information handed off:
- Meaning, scope, baseline, and readiness of the handoff:
- Evidence, limitations, and unresolved risks:
```

## Reference Process Conformance Claim

Omit this block when no Conformance to the ALPS Management Process is claimed. A claim identifies the ALPS Management Process baseline, scope, whether Outcome Conformance, Task Conformance, or both form the basis, the conclusion, evidence, and limitations. A Full Conformance claim using Outcome Conformance as its basis requires every Outcome of that baseline. A Full Conformance claim using Task Conformance as its basis requires every in-scope requirement stated with `must` or `must not` in an Activity or Task; recommendations, permissions, and typical actions remain non-mandatory. A Tailored Conformance claim identifies the tailored Process scope and demonstrates every Outcome remaining in scope and every in-scope requirement stated with `must` or `must not` in an Activity or Task. Capability is assessed separately from Conformance.
