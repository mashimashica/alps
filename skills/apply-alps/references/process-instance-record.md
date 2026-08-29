# Optional Process Instance Record Aid

Use this human-readable aid only when risk, a Decision Gate, a handoff, Tailoring, an audit, or an explicit Conformance claim justifies a durable record. It is not an ALPS profile, schema, or machine-readable binding. Rename, reorder, repeat, or omit headings and labels according to the situation while preserving the meaning needed by the record.

## Application

- **Source:** the invoked Process and its authoritative representation or managed baseline
- **Context:** the application situation and need
- **Scope:** the declared application scope and relevant exclusions

## Outcome Evidence

Repeat this block for each Outcome that needs durable evidence.

- **Outcome:** the applicable Outcome
- **Result:** the observed result
- **Evidence:** supporting evidence or a resolvable reference to it
- **Limitations:** evidence gaps, uncertainty, or other limitations

## Handoff

Use when a provider Output is mapped to a recipient Input.

- **Provider:** the providing Process or Process Instance
- **Output:** the provided Output
- **Recipient:** the receiving Process or Process Instance
- **Input:** the recipient Input
- **Correspondence:** aligned meaning, scope, and quality conditions
- **Status:** the handoff status

## Decision or Tailoring

Use only for an actual decision or managed Tailoring.

- **Decision:** the decision made
- **Scope:** the affected application or elements
- **Basis:** applicable risk, requirements, criteria, Controls, Constraints, or evidence
- **Affected parties:** affected parties and their relevant Input
- **Rationale:** the reason for the decision

## Conformance Claim

Add only when making an explicit claim. This block records the assessment result; it does not establish the claim by its presence.

- **Subject:** the representation, Process, Reference Process, or Process Instance assessed
- **Process basis:** the applicable Process and authoritative Process Description when the claim concerns a Process or Process Instance
- **Scope:** the claim scope
- **Basis:** the applicable baseline and selected Conformance basis
- **Claim:** the assessment conclusion
- **Evidence:** evidence supporting the conclusion
- **Limitations:** exclusions, evidence gaps, uncertainty, or other limitations
