# Examples and review cases

[Japanese translation](locales/ja/examples.md)

These fictional cases illustrate the [Framework](../../../spec/process-framework.md); they introduce no additional requirements. Start with the [minimal template](SKILL-template.md), and add only details whose absence would change understanding, application, or evaluation.

## 1. Only the required core

```markdown
---
name: identify-maximum
description: Identify the greatest value in a given non-empty finite set of integers.
---

# Maximum Identification

## Purpose

Determine the greatest value in the given non-empty finite set of integers.

## Outcomes

- The identified value belongs to the given set and is at least as large as every member.
```

The result condition is observable and sufficient for this bounded Purpose. The Purpose identifies the input domain, and the Outcome identifies its maximum without prescribing an algorithm. An empty set falls outside the stated scope; it must not be silently reported as successfully handled.

## 2. One-off, context-specific work

```markdown
---
name: relocate-october-workshop
description: Arrange the replacement location for the 8 October 2026 design workshop after Room A closes.
---

# October Workshop Relocation

## Purpose

Enable the 8 October 2026 design workshop to take place after Room A closes.

## Outcomes

- A replacement room is confirmed for the workshop time.
- The replacement room accommodates every intended participant's attendance and access needs.
- Every intended participant has acknowledged the replacement location before the workshop.
```

The date and occasion supply the necessary scope in the description. Room availability, suitability, and participant acknowledgment can be judged independently. Sending an invitation is an Output; an acknowledgment requires a response. An unidentified access need remains unconfirmed and limits the suitability judgment.

## 3. Work without a fixed artifact

```markdown
---
name: clarify-outcome-and-output
description: Clarify the distinction between an Outcome and an Output when a learner confuses success with producing a deliverable.
---

# Outcome and Output Clarification

## Purpose

Enable the learner to distinguish successful work from the production of a deliverable.

## Outcomes

- The learner correctly distinguishes result conditions from deliverables in an example not used in the explanation.
- The learner explains why a deliverable can exist while the intended result condition remains unmet.
```

An oral exchange can supply observable evidence. Slides, transcripts, and a fixed document are unnecessary unless the context requires them. Delivering an explanation is not evidence that the learner understands it. Representative checks support a judgment about the observed learner and context, not permanent or universal understanding.

## 4. Necessary approval, method, and sequence

This service's production policy requires qualification of a candidate and confirmation of its production behavior. The description adds work detail and conditions to make these obligations clear.

### Production Release

**Purpose:** Make the approved change available to this service's production users with a functioning checkout.

**Outcomes:**

- The approved change is available in production.
- The production health endpoint reports ready.
- A test purchase completes through the user checkout path.

**Activities and Tasks:**

- **Candidate qualification:** The release candidate must be checked against the service's acceptance criteria. Approval for that exact candidate must be obtained from the service owner.
- **Production availability:** The approved candidate must be deployed through the service's authorized release job. The production result must be checked against the acceptance criteria.

Qualification establishes the basis for using a candidate; production work establishes and checks the resulting service state. Both Activities contribute to the Outcomes, and their Tasks state the individual actions. Each can be revisited if the candidate or production evidence changes.

**Control:** For this service, the production policy requires the service owner's approval of the exact checked candidate and use of the authorized release job. The acceptance criteria require a ready health endpoint and a completed test purchase.

**Constraints:** Candidate checks must precede approval; approval must precede deployment; production checks follow deployment. A candidate change invalidates the earlier check and approval basis. Deployment must not occur while approval is missing or unconfirmed.

**Entry Criteria:** The candidate and acceptance criteria are available for qualification. **Exit Criteria:** Achievement of all three Outcomes is supported by production evidence, and the applicable release requirements are satisfied.

**Input:** The release candidate and change request. **Output:** The deployed service revision. **Enablers:** Checking capability and the authorized release job.

A policy directs the work; its approval condition limits deployment. The release job supplies an Enabler. The Entry Criteria allow candidate qualification to begin before deployment approval, while the deployment Constraint still applies to the action it governs.

## 5. Shared information updated by multiple Processes

### Requirements Clarification

**Purpose:** Make the needs for the service change precise enough to guide solution choices.

**Outcomes:** The needs have observable acceptance conditions. Material ambiguities and conflicts are resolved or identified with their consequences for solution choice.

### Feasibility Assessment

**Purpose:** Determine whether candidate solutions can satisfy the clarified needs within the available capacity.

**Outcomes:** Each considered candidate's feasibility is supported by evidence against the needs and available capacity. Unverified assumptions and their effect on the feasibility judgment are explicit.

Both Processes consult and update the same ordinary **change brief**. It contains the needs, candidate assumptions, acceptance conditions, and supporting observations for this service change. Its needs and observations serve as Inputs when examined; its acceptance conditions act as Controls when judging a candidate. Updated information is an Output. These roles can be distinguished within the same document.

| Work | Use of the shared information | Change effect |
| --- | --- | --- |
| Requirements Clarification | Refines needs and acceptance conditions using stakeholder information and feasibility findings. | A changed need or acceptance condition requires reconsidering affected feasibility judgments. |
| Feasibility Assessment | Adds capacity evidence, candidate limits, and questions about the current needs. | A newly exposed limit requires reconsidering affected needs or solution choices. |

For this collaboration, readers must identify the revision used. Updates must distinguish confirmed needs, proposals, and unverified assumptions, and must not silently overwrite conflicting findings. Changed information must be made available to affected work before it relies on superseded judgments. The team's existing document and version tools supply storage and coordination. The two Processes can revisit the brief repeatedly. Their repeated application at the same level is Iteration; applying them separately to the service and its components is Recursion. Integration checks completeness within each level and consistency between levels. Establishing usable portions of the service change is Incremental application. These relationships can be combined according to the change being considered.

The approval conditions in Production Release govern deployment in that Process. Sharing the brief does not make those conditions Entry Criteria for all clarification and assessment work.

## 6. A cross-cutting View

A **release decision view** gives a reviewer links to the relevant source elements:

| Concern | Source | What to inspect |
| --- | --- | --- |
| Adequacy of the need | [Requirements Clarification](#requirements-clarification) | Acceptance conditions and unresolved ambiguity. |
| Support for the solution | [Feasibility Assessment](#feasibility-assessment) | Evidence and limits of candidate feasibility. |
| Permission to affect production | [Production Release](#production-release) | The scoped approval and sequence conditions. |

The view gives access to the source descriptions and explains their relevance to a release decision. The source descriptions retain their Purposes and Outcomes. A reviewer may propose a second approver, explicitly labeled as a proposal. Displaying that proposal does not change the source policy or authorize a release. A change to the applying policy or description must be handled within its own authority and scope.

## 7. Missing-reference review

Suppose a draft requires `service-policy.md`, revision 7, as the criterion for release approval, but only revision 6 is available. These are fictional identifiers, not bundled files.

A review can state: “The required revision 7 was not supplied. Approval authority and release conditions are unconfirmed. The draft's Purpose and Outcome wording have been reviewed against the available Framework, but policy consistency cannot be determined. Deployment cannot rely on this review as approval. Supply the intended revision to complete that part of the assessment.”

Do not substitute revision 6 or a same-named policy. Do not label the policy inapplicable because it is missing. A review-only request returns this finding and its impact; it does not silently rewrite the draft or invent the missing approval conditions.

## 8. Output exists, Outcome unmet

For [Production Release](#production-release), assume the release job produced a deployment log and the intended revision is deployed. The production health endpoint reports ready, but the test purchase fails. The approval evidence has not been supplied.

The deployed revision and log are Outputs. Evaluate the result conditions separately:

| Condition | Evidence and judgment |
| --- | --- |
| The approved change is available in production. | The intended revision is present, but whether it is approved remains unconfirmed. |
| The production health endpoint reports ready. | The observation supports achievement of this Outcome. |
| A test purchase completes through the user checkout path. | The failed purchase shows this Outcome is unmet. |
| The approval requirement is satisfied. | Approval evidence is missing; satisfaction remains unconfirmed. |

The release Exit Criteria are not satisfied. The facts support reporting the failed purchase and requesting the missing approval evidence. They do not establish that approval occurred or never occurred, and the existing Outputs and successful health check do not establish overall success.
