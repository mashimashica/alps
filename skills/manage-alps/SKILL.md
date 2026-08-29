---
name: manage-alps
description: Govern adopted ALPS representations and their application. Use when adopting or registering a representation, maintaining discoverability and application conditions, controlling change or retirement, making or reviewing a Tailoring decision, assessing a representation or Process Instance, prioritizing improvements, or requesting redefinition or reverification. Use define-alps to create or authoritatively redefine a representation and apply-alps to select representations and invoke Processes.
---

# ALPS Management Process

## Purpose

This Process governs ALPS representations and their application and maintains the continual availability of suitable, coherent, and trustworthy ALPS assets.

## Outcomes

Success of this Process establishes the following conditions.

- a) Policies and guidance for managing, deploying, Tailoring, and adopting ALPS representations are established.
- b) Adopted ALPS representations are discoverable with their identity, kind, status, version, and applicable conditions under management.
- c) Changes and retirement are controlled with their impacts, reference integrity, and affected users or representations identified.
- d) Tailoring, formal adoption, and other management decisions are traceable to applicable Controls, Constraints, scope, evidence, and rationale.
- e) Process execution is assessed using criteria appropriate to its declared subject, including Conformance, performance, and effectiveness where relevant.
- f) Managed ALPS representations are assessed using criteria appropriate to their kind, including semantic consistency, Description Conformance, relationship coherence, and applicability where relevant.
- g) Improvement opportunities are prioritized from execution evidence, lessons learned, representation assessments, and change impacts.
- h) Decided improvements are implemented through controlled change.
- i) Representations affected by implemented improvements are reverified.
- j) Resulting management states are updated.

## Activities & Tasks

### Asset Governance

1. Guidance for management, deployment, adoption, and Tailoring must be established.
2. A representation must be adopted and registered with its identity, kind, version, status, and applicable conditions.
3. Affected references, dependencies, representations, and users must be identified.
4. Changes, communication, and retirement must be controlled.
5. The resulting management state must be updated.

### Tailoring Control

1. The context, risks, requirements, complexity, resources, and affected parties must be identified.
2. Context-specific Tailoring must be distinguished from authoritative redefinition.
3. Candidate Processes or life cycle models must be evaluated.
4. The Tailoring decision must be recorded with its scope, changes, applicable Controls, rationale, and Traceability.
5. Tailoring effectiveness must be controlled during application through review and revision when needed.

### Assessment and Improvement

1. Assessment criteria must be selected for the declared subject and representation kind.
2. Assessment must distinguish a representation, its described Process, and a Process Instance.
3. Defects, duplication, lessons, and improvement opportunities must be prioritized.
4. Assessment results must be routed by subject: semantic changes to the ALPS Definition Process and application conditions to the ALPS Application Process.
5. Representations affected by implemented changes must be reverified, and the resulting management state must be updated.

| Activity | Outcomes |
| --- | --- |
| Asset Governance | a), b), c), h), j) |
| Tailoring Control | a), d) |
| Assessment and Improvement | e), f), g), h), i), j) |

## Inputs

- Verified ALPS representations and adoption, change, retirement, Tailoring, assessment, or improvement requests.
- Managed identities, versions, status, dependencies, application conditions, and change history.
- Selection rationale, execution and Outcome evidence, handoffs, decisions, lessons, assessment results, and affected-party information.

## Outputs

- Managed representations, status, application conditions, and updated management states.
- Adoption, change, retirement, and Tailoring decisions with their rationale and Traceability.
- Assessment results and prioritized improvements.
- Redefinition, reverification, or application-condition handoffs.

## Entry Criteria

- A management trigger concerning adoption, change, retirement, Tailoring, assessment, or improvement is identified.
- The subject, representation kind, baseline, and scope can be identified.
- Applicable Controls, Constraints, authority, and Decision Gates can be determined when needed.

## Exit Criteria

- Management decisions, rationale, evidence, and affected references are traceable.
- Change, retirement, Tailoring, adoption, assessment, and improvement impacts have been addressed as applicable.
- Required redefinition, reverification, and application-condition handoffs are explicit.
- The resulting management state has been updated.

## Enablers

- A managed representation register, version and status information, dependency information, and change history.
- Governance, risk, domain, and assessment expertise.

## Normative Basis

The [Process Framework](../../spec/process-framework.md) governs Process semantics, and the [ALPS Specification](../../spec/ALPS-SPEC.md) governs representation management, Tailoring, assessment subjects, and the ALPS-specific requirements applied by this Process.

## Bundled Resources

- [Japanese localization](references/locales/ja/SKILL.md): use for Japanese-language work; the English description remains authoritative.
- [management-records.md](references/management-records.md): optional record aid when a management decision, handoff, assessment, or change history needs to be durable.
