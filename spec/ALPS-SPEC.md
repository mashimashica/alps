# ALPS — Agent Skill Process Profile

ALPS applies the [Process Framework](process-framework.md) (PF) to Agent Skills.
It is a thin profile for representing reusable Process knowledge in the
portable discovery and description surface of an Agent Skill.

## 1. Scope

This specification establishes the requirements specific to representing a
Process as an Agent Skill, projecting that Process for discovery, including
optional detail and accompanying resources, describing composition handoffs,
and interpreting validation results.

This specification does not define general Process semantics, Host discovery or
routing, Skill selection or activation, execution of the represented Process,
adoption, distribution policy, version management, retirement, organizational
governance, or a general life-cycle engine.

## 2. Normative Sources and Precedence

PF is the authoritative source for Process, Process Description, Process
Instance, Name, Purpose, Outcomes, Activities, Tasks, Inputs, Outputs, Controls,
Constraints, Enablers, Entry Criteria, Exit Criteria, handoffs, Tailoring,
assessment, Process Model, Process Reference Model, Process View, and all other
general Process constructs.

If this specification conflicts with PF, PF must take precedence. ALPS must not
weaken a PF requirement, permit an action that PF prohibits, or redefine a PF
construct.

The [Agent Skills specification](https://agentskills.io/specification) governs
the physical form of an Agent Skill. ALPS does not restate that form.

Normative words and their meanings are those defined by PF. This specification
inherits them and does not redefine them.

## 3. Process Skill Representation

By default, one Agent Skill represents one Process. ALPS does not establish
additional typed representation kinds for other PF constructs.

A Skill Package must contain exactly one identifiable authoritative Process
Description. The authoritative Process Description must contain the Process
Name, Purpose, and Outcomes required by PF. Every optional Process element that
it includes must follow PF.

The Skill `name` is a discovery identifier. The Process Name is the PF identity
of the represented work and must be presented as the heading of the authoritative
Process Description. A project, product, or package brand must not replace the
Process Name unless that brand is itself the central concern of the represented
work.

The distributed [Reusable Work Design Process](../skills/reusable-work-design/SKILL.md)
is the primary example of this profile. Its Skill identifier is
`reusable-work-design`; its Process Name is `Reusable Work Design Process`; and
the Plugin brand remains `alps`.

## 4. Discovery Projection

The Skill `name` and discovery `description` are projections of the represented
Process for Host discovery. They must not replace the authoritative Process
Description.

The discovery `description` must remain consistent with the Process Name,
Purpose, Outcomes, Process boundary, and applicable conditions. It should state
the information needed to decide whether the Skill applies, including material
conditions under which it does not apply.

A discovery projection must not be treated as assurance evidence merely because
it contains a textual claim about the representation.

## 5. Optional Detail and Skill Package Resources

Optional Process detail must be included in proportion to the intended
discovery, application, composition, and assessment needs. Detail that does not
materially support those needs should be omitted or kept as clearly identified
reference information.

Accompanying resources may support understanding or application. Their roles
and conditions of use must be identifiable, mandatory references must resolve,
and they must not conflict with or create a second authoritative Process
Description.

Physical directories, files, metadata, and loading behavior remain subject to
the Agent Skills specification and the applicable Host. They do not change
Process semantics.

## 6. Composition Handoffs

When Process composition is described, every provider Process Output to
recipient Process Input mapping must be explicit. The direction and exchanged
item must be identifiable so that the handoff can be understood and assessed.

This handoff requirement does not make ALPS a Skill router, resolver, or
execution engine.

## 7. Validation and Assessment Boundary

Form validation, loading, parsing, activation, template completion, or a textual
self-claim must not by itself establish semantic Conformance, Outcome
achievement, or Execution Conformance.

Assessment of a Process Skill representation and assessment of an execution of
the represented Process are distinct. A Conformance claim must identify its
subject, criteria, scope, and evidence. PF governs the applicable general
assessment and Conformance semantics; ALPS adds no separate Conformance
taxonomy.
