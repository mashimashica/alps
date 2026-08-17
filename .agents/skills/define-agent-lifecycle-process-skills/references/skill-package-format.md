# Logical Composition of an ALPS-Conformant Skill Package

This material is an informative example of the logical composition of a Skill Package under ALPS 5.7. ALPS does not prescribe filenames, file formats, metadata formats, physical storage structures, distribution mechanisms, or vendor-specific registration and presentation specifications. The Process Framework and ALPS apply to the meaning and logical integrity of a Skill; the rules of the target environment apply to representation and deployment. Environment-specific representation and deployment information can be recorded in an Environment Binding separate from the authoritative Skill Description.

## Logical Composition

| Logical component | Cardinality | Representative role | Conditions of use |
|---|---:|---|---|
| Authoritative Skill Description | 1 | Normative basis for the Skill's Name, Purpose, Outcomes, discovery information, and execution information | Include one per Package. Make the authoritative basis uniquely identifiable regardless of representation or storage location. |
| Reference information and Controls | 0..* | Standards, policies, schemas, detailed explanations, and other material that directs or supports understanding | May be included as needed. Mandatory references must be resolvable in the target environment. |
| Execution Enablers | 0..* | Scripts, declarative rules, modules, tools, or connections to services | The role and conditions of use must be identifiable from the Skill Description. Compatibility conditions and limitations should be stated when relevant. |
| Output-creation resources | 0..* | Templates, media, fonts, schemas, and other support for creating Outputs | Functional classification and conditions of use must be identifiable from the Skill Description. |
| Environment Binding | 0..* | Mapping to loading, registration, capability, permission, integration, or presentation specifications of the target environment | The target environment determines names, locations, formats, and schemas. The Environment Binding must not redefine the authoritative Skill Description. |
| Presentation resources | 0..* | Icons, previews, display strings, colors, and other presentation support | May be included as needed for the target environment. Their presentation role alone does not demonstrate ALPS Conformance. |

The functional role of a resource must be determined from its function during Skill execution rather than only its storage location or file extension. When the same physical resource has multiple roles, each role and its conditions of use must be identifiable.

## Representative Environment Binding Items

- Target execution environment and applicable version
- Resolvable reference to the authoritative Skill Description
- Mappings for discovery information, execution information, capabilities, permissions, and presentation information
- Referenced metadata schema or registration rules
- References to required Enablers and presentation resources
- Compatibility conditions, known limitations, and reverification conditions

These items can be stored in one file or divided among multiple resources or registration records. This example assumes no particular name, directory, notation, or serialization format.

## Package Review Criteria

- The Package must contain one authoritative Skill Description.
- The functional role and conditions of use of every accompanying resource must be identifiable from the Skill Description.
- Mandatory references must be resolvable by the declared method of the target environment, such as local, embedded, Registry, or URI resolution.
- An Environment Binding must not alter the meaning or normative force of the authoritative Skill Description.
- Unnecessary duplication or conflict must not arise between the Skill Description and accompanying resources.
- The Package should contain only Artifacts, resources, Bindings, and registration information that directly support understanding or executing the Skill or creating an Output.
- The impact of changes to the Package or Environment Binding should be assessed, and affected Skill Descriptions, accompanying resources, and mappings should be identified and reverified as needed.
