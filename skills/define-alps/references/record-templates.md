# Definition Process Record Templates

Select only the records that are needed and tailor them to the context of application and risk. Do not fill blanks by conjecture; mark them `Unconfirmed`, `Not applicable`, or `On hold`.

## 1. Skill Need Record

```markdown
# Skill Need Record

- Record ID:
- Status: Candidate / Selected / Deferred / Reconsideration
- Need or problem:
- Intended users:
- Stakeholders and expectations:
- Intended contexts of use:
- Recurrence or impact:
- Duplication, adjacency, or gap relative to existing Skills:
- Expected benefits:
- Risks:
- Costs or constraints:
- Decision:
- Rationale and evidence:
- Unresolved matters:
```

## 2. Traceability Among Elements

For Outcome and Task references, use a reference method suited to the context of application, such as a stable identifier, short name, heading, list position, or brief quotation.

| Outcome reference | Contributing Activity | Contributing Task reference | Related Input/Output | Verification evidence | Status |
|---|---|---|---|---|---|
| | | | | | Not assessed / Conformant / Defect / Out of scope |

Review points:

- The set of Activities and any separated Skills must cover every Outcome.
- Relationships among Outcomes, Activities, and Tasks should be identifiable.
- For external exchanges, the names, meanings, and scopes of provider Outputs and recipient Inputs should be aligned.
- When an Output change affects another Skill's Input, the affected Skill and mapping should be identified and the necessary reassessment should be performed.

## 3. Verification Record

```markdown
# Skill Verification Record

- Skill and version under verification:
- Verification scope: Skill Description / Skill Package / Both
- Conformance subject: Description / Reference Model / Execution
- Conformance mode (for a Reference Model or Execution subject): Full / Tailored
- Conformance basis:
  - Description: applicable ALPS clauses
  - Full: Outcomes / Tasks / Both
  - Tailored: Tailored Skill or Process and scope of application, with every Outcome and Activity/Task requirement remaining in scope
- Applicable norms and Controls:
- Review criteria:
- Independent perspective:
- Representative contexts of use:
- Boundary cases:

## Results
| Verification item | Evidence | Determination | Defect ID |
|---|---|---|---|
| | | Conformant / Nonconformant / Not assessed | |

## Defect Treatment
| Defect ID | Description | Impact | Action | Completion condition | Due date | Status |
|---|---|---|---|---|---|---|
| | | | | | | |

## Limitations and Assumptions
-
```

## 4. Adoption Decision Gate Record

```markdown
# Adoption Decision Gate

- Skill and version under decision:
- Decision Criteria:
- Evidence consulted:
- Unresolved defects and residual risk:
- Decision: Adopt / Conditionally adopt / Hold / Redesign / Reject
- Rationale:
- Assumptions:
- Conditions of application:
- Next recipient:
```
