# ALPS Definition Process Record Templates

Select only the records needed for the representation kind, application context, and risk. Do not fill missing information by conjecture; mark it `Unconfirmed`, `Not applicable`, or `On hold`.

## 1. Representation Need Record

```markdown
# Representation Need Record

- Record ID:
- Status: Candidate / Selected / Deferred / Reconsideration
- Need or concern:
- Intended users and stakeholders:
- Intended contexts of use:
- Existing representations and relevant gaps:
- Selected PF construct: Process / Process Model / Process Reference Model / Process View
- Selection rationale:
- Expected benefits:
- Risks and constraints:
- Required level of detail:
- Unresolved matters:
```

## 2. Representation Traceability

Use stable references suited to the representation and context. For a Process, trace Outcomes, Activities, Tasks, Inputs/Outputs, and evidence. For Models and Views, trace represented or source Processes, canonical Skill references, relationships, and provenance as applicable. When a Process View references an Activity or Task from a source Process, retain enough provenance and Traceability to identify that source relationship.

| Source or element | Relationship | Target or related element | Evidence or reference | Status |
|---|---|---|---|---|
| | | | | Not assessed / Conformant / Defect / Out of scope |

Review points:

- The represented PF construct and declared/default representation kind agree.
- Mandatory canonical Skill references resolve.
- A Process Reference Model retains the same Name, Purpose, and Outcomes as each referenced authoritative Process Description.
- A Process View maintains source provenance and Traceability for referenced source elements and keeps View-local descriptions distinct from changes to source Processes.
- Every provider Output to recipient Input mapping is explicit, and the exchanged meanings and scopes are aligned.

## 3. Verification Record

```markdown
# ALPS Representation Verification Record

- Representation and version under verification:
- Representation kind: process / process-model / process-reference-model / process-view
- Verification scope: authoritative representation / Skill Package / both
- Applicable Conformance subject:
  - Process: Description Conformance; optional Process Conformance claim assessed separately
  - Process Model: Process Model Description Conformance
  - Process Reference Model: Process Reference Model Description Conformance
  - Process View: Process View Description Conformance
- Applicable Process Framework and ALPS clauses:
- Applicable Controls and Constraints:
- Review criteria:
- Independent perspective, when used:
- Representative contexts or concern:

## Results
| Verification item | Evidence | Determination | Defect ID |
|---|---|---|---|
| | | Conformant / Nonconformant / Not assessed | |

## Reference and Semantic Checks
| Reference or semantic center | Expected target or value | Result | Evidence |
|---|---|---|---|
| | | | |

## Defect Treatment
| Defect ID | Description | Impact | Action | Completion condition | Status |
|---|---|---|---|---|---|
| | | | | | |

## Limitations and Assumptions
-
```

## 4. Adoption Decision Gate Record

```markdown
# Adoption Decision Gate

- Representation and version under decision:
- Representation kind:
- Verification evidence consulted:
- Mandatory-reference status:
- Unresolved defects, assumptions, and residual risk:
- Decision criteria:
- Decision: Adopt / Conditionally adopt / Hold / Redefine / Reject
- Rationale:
- Conditions of application:
- Required management state or follow-up:
- Next recipient:
```
