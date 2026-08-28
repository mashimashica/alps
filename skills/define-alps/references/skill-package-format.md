# Logical Composition of an ALPS-Conformant Skill Package

This material is an informative example of the logical composition of a Skill Package under ALPS 5.7. ALPS does not prescribe filenames, file formats, metadata formats, physical storage structures, distribution mechanisms, or vendor-specific registration and presentation specifications. The Process Framework and ALPS apply to the meaning and logical integrity of the represented PF construct; the rules of the target environment apply to representation and deployment. The authoritative Agent Skill representation is the semantic source for the PF construct represented by the Package. When the Agent Skill represents a Process, its authoritative content is the Skill Description, including the discovery-layer and execution-layer information defined by ALPS. An Environment Binding may project discovery or registration information into frontmatter or a separate registration record and may keep representation and deployment information separate, but it must not change the meaning or normative force of the authoritative Agent Skill representation.

## Logical Composition

| Logical component | Cardinality | Representative role | Conditions of use |
|---|---:|---|---|
| Authoritative Agent Skill representation | 1 | Semantic and normative basis for the Process, Process Model, Process Reference Model, or Process View represented by the Package | Include one per Package. Make the authoritative representation uniquely identifiable regardless of representation or storage location. For a Process representation, the Skill Description is its authoritative content. |
| Reference information and Controls | 0..* | Standards, policies, schemas, detailed explanations, and other material that directs or supports understanding or application | May be included as needed. Mandatory references must be resolvable in the target environment. |
| Application Enablers | 0..* | Scripts, declarative rules, modules, tools, or connections to services that support use of the represented PF construct | Their roles and conditions of use must be identifiable from the authoritative representation. Compatibility conditions and limitations should be stated when relevant. |
| Output-creation resources | 0..* | Templates, media, fonts, schemas, and other support for creating Outputs when the represented construct is used in Process execution | Their functional classification and conditions of use must be identifiable from the authoritative representation. |
| Environment Binding | 0..* | Mapping to loading, registration, capability, permission, integration, or presentation specifications of the target environment | The target environment determines names, locations, formats, and schemas. The Environment Binding must not redefine the authoritative Agent Skill representation. |
| Presentation resources | 0..* | Icons, previews, display strings, colors, and other presentation support | May be included as needed for the target environment. Their presentation role alone does not demonstrate ALPS Conformance. |

The functional role of a resource must be determined from the function it performs when the represented PF construct is understood or applied rather than only from its storage location or file extension. When the same physical resource has multiple roles, each role and its conditions of use must be identifiable.

## Concrete Repository Role Mapping

| Scope | Resource | Logical role | Boundary |
|---|---|---|---|
| `define-alps` Package | [`SKILL.md`](../SKILL.md) | Authoritative Agent Skill representation | Governs the represented Define ALPS Process. |
| `define-alps` Package | [`SKILL-template.md`](SKILL-template.md) and [`record-templates.md`](record-templates.md) | Output-creation resources | Inform drafting and record creation; they do not add ALPS requirements. |
| `define-alps` Package | This `skill-package-format.md` | Reference information | Explains logical resource roles; it is not an Environment Binding. |
| `define-alps` Package | [`agents/openai.yaml`](../agents/openai.yaml) | Environment Binding | Maps discovery and presentation metadata for a target Host. |
| `define-alps` Package | [`assets/alps.svg`](../assets/alps.svg) | Presentation resource | Supports presentation only. |
| Repository review | [`spec/alps-markdown-v2.md`](../../../spec/alps-markdown-v2.md) | Environment Binding | Defines the optional `alps-markdown/v2` physical representation; it is not ALPS itself. |
| Repository review | [`validate_alps_markdown.py`](../../../.agents/skills/review-alps/scripts/validate_alps_markdown.py) | Application Enabler | Supports the repository-development `review-alps` Process by validating `alps-markdown/v2`; it is not part of the distributed `define-alps` Package and does not establish ALPS Conformance. |

## Representative Environment Binding Items

- Target execution environment and applicable version
- Resolvable reference to the authoritative Agent Skill representation
- Representation kind and any required binding metadata
- Mappings for discovery, loading, capabilities, permissions, registration, and presentation information
- Referenced metadata schema or registration rules
- References to required Enablers and presentation resources
- Compatibility conditions, known limitations, and reverification conditions

These items can be stored in one file or divided among multiple resources or registration records. This example assumes no particular name, directory, notation, or serialization format.

## Package Review Criteria

- The Package must contain one authoritative Agent Skill representation.
- The represented PF construct must be identifiable from the authoritative representation, including the applicable `metadata.alps.kind` declaration for a non-Process representation.
- The functional role and conditions of use of every accompanying resource must be identifiable from the authoritative representation.
- Mandatory references must be resolvable by the declared method of the target environment, such as local, embedded, Registry, or URI resolution.
- An Environment Binding must not alter the meaning or normative force of the authoritative Agent Skill representation.
- Unnecessary duplication or conflict must not arise between the authoritative representation and accompanying resources.
- The Package should contain only artifacts, resources, Bindings, and registration information that directly support understanding or applying the represented PF construct or creating Outputs from Process execution.
- The impact of changes to the Package or Environment Binding should be assessed, and affected Agent Skill representations, accompanying resources, references, and mappings should be identified and reverified as needed.
