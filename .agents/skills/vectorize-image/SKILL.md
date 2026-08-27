---
name: vectorize-image
description: Reconstruct raster or flattened visual references as layered, editable vector assets and verify that significant visual structure is preserved. Use for icons, logos, flat illustrations, diagrams, or related graphics when semantic layers, simplification, and evidence matter more than automatic tracing or pixel equality. Repository-development Skill; not part of the distributed ALPS Plugin. ALPS-conformant.
---

# Layered Vector Reconstruction

## Purpose

This Process establishes an editable vector representation of a visual reference that preserves its significant visual structure for the intended use.

This Process is intended for visual assets whose identity depends on interpretable geometry, regions, overlap, negative space, and paint relationships. It does not require literal reproduction of incidental raster artifacts.

## Outcomes

Success of this Process establishes the following conditions.

- a) The intended use, authoritative visual reference, representative display conditions, and required fidelity boundary are identified.
- b) Significant visual structure and visually coherent regions are distinguished from incidental raster artifacts.
- c) Significant geometry, negative space, region boundaries, spatial relationships, and visual hierarchy are preserved in the vector representation.
- d) Visually coherent regions and overlap relationships remain identifiable and independently editable where the intended use requires them.
- e) Geometric and paint complexity is proportionate to the significant visual structure rather than inherited mechanically from the raster reference.
- f) Verification evidence, provenance, rights conditions, assumptions, deviations, and limitations support an informed acceptance and reuse decision.

## Activities & Tasks

The headings, Activities, Tasks, and numbers below organize the work content and do not prescribe an execution sequence, performer allocation, tool, tracing method, or acceptance metric. Activities can be revisited when reconstruction or verification evidence reveals a structural error or unresolved ambiguity.

### Reference Qualification

This Activity establishes the subject, use context, and fidelity boundary of the reconstruction. It primarily contributes to Outcomes a) and f).

1. The intended use and representative display conditions must be identified.
2. The authoritative visual reference and any supporting references must be identified.
3. Reference resolution, compression, transparency, cropping, color behavior, and other conditions that can affect interpretation must be assessed.
4. Applicable ownership, authorization, license, trademark, privacy, brand, and attribution conditions must be identified.
5. Required output format, dimensions, coordinate system, editability, compatibility, and transfer conditions should be identified.
6. Features that require exact preservation, controlled approximation, omission, replacement, or separate treatment must be distinguished.
7. Unresolved authority, rights, or fidelity conditions must remain explicit in reconstruction claims.

### Visual Structure Analysis

This Activity identifies the visual decisions that the vector representation must preserve. It primarily contributes to Outcomes b), c), d), and e).

1. The silhouette, negative spaces, principal contours, alignment anchors, landmarks, proportions, and spatial relationships must be identified.
2. Major visual regions, facets, strokes, text, repeated motifs, gradients, shadows, masks, clipping boundaries, and transparency relationships must be identified where applicable.
3. Overlap relationships and z-order that affect the visible composition must be identified.
4. Visually coherent regions must be distinguished from antialiasing, compression artifacts, color noise, and other incidental raster variation.
5. Ambiguous boundaries and features unsupported by the available references must be identified.
6. A vector element and layer plan should be established to map significant reference regions and relationships to independently understandable vector elements.
7. The planned level of geometric and paint detail should be justified by the intended use and representative display conditions.

### Vector Reconstruction

This Activity establishes the editable vector representation. It primarily contributes to Outcomes c), d), and e).

1. Vector geometry and paint relationships must be established for the significant visual structure identified in the analysis.
2. The coordinate system, composition bounds, clipping, masking, overlap, and z-order must preserve the intended visible relationships.
3. Visually coherent regions should be organized into stable groups or identifiable elements when independent editing, recoloring, replacement, or inspection is required.
4. Geometry must be simplified or regularized when redundant detail represents raster artifacts rather than significant structure.
5. Simplification must not remove a landmark, boundary, negative space, proportion, or relationship required by the intended use.
6. Repeated definitions and shared paint resources should remain reusable where doing so preserves clarity and editability.
7. Embedded raster content, external references, live text, outlined text, filters, or other transfer dependencies must be explicit and justified when present.
8. Active content and unnecessary external dependencies should be excluded from a passive visual asset.
9. Known approximations and unsupported effects must remain traceable to the affected reference features.

### Visual Verification and Refinement

This Activity determines whether the vector representation preserves the intended structure in use. It primarily contributes to Outcomes c), d), e), and f).

1. The vector representation must be rendered under representative dimensions, backgrounds, scaling, and export conditions.
2. The rendered result must be compared with the authoritative reference for silhouette, negative space, landmarks, proportions, principal boundaries, alignment, overlap, z-order, color relationships, and visual hierarchy as applicable.
3. Legibility and structural stability should be assessed at the smallest and largest representative display conditions.
4. Independent editability should be assessed by inspecting, selecting, hiding, recoloring, or replacing visually coherent regions where that capability is required.
5. Structural facts such as element counts, identifiers, embedded content, active content, and external references should be inspected mechanically where practical.
6. Quantitative image-comparison measures may support the assessment, but must not be treated as sufficient evidence of structural fidelity, editability, or aesthetic quality.
7. A discrepancy that affects a significant feature or intended use must be corrected or explicitly dispositioned.
8. Verification evidence, unresolved defects, accepted deviations, assumptions, and limitations must be recorded.

### Transfer Preparation

This Activity makes the verified representation usable without obscuring its authority or limitations. It primarily contributes to Outcomes d) and f).

1. The authoritative vector asset and any derived variants must be distinguishable.
2. The coordinate, accessibility, metadata, and compatibility information required by the intended recipient or execution environment must be established in or with the asset.
3. Preview renders and verification records should identify the asset version and the reference version they assess.
4. Layer and element identities needed for downstream use must remain stable or have a documented mapping.
5. The asset, structure record, verification evidence, provenance, rights conditions, and known limitations must be prepared for transfer together when the recipient requires them.

## Inputs

Representative Inputs include:

- an authoritative raster or flattened visual reference;
- supporting visual references, prior variants, or source material;
- intended use and representative display conditions;
- required output, dimension, coordinate, compatibility, and editability conditions;
- applicable visual identity, brand, accessibility, licensing, rights, attribution, privacy, and security requirements; and
- acceptance criteria or prior review findings.

## Outputs

Representative Outputs include:

- a layered and editable vector asset;
- a visual structure and layer plan;
- representative rendered previews or comparison artifacts;
- a verification and deviation record; and
- provenance, rights-condition, dependency, and limitation information.

## Entry Criteria

- At least one visual reference can be inspected.
- The intended use and representative display conditions can be identified, or their absence can be recorded as a material limitation.
- The authoritative reference can be selected, or authority conflict can be made explicit.
- The applicable authorization and rights conditions are sufficient to permit the reconstruction work.
- The required fidelity and transfer boundary can be established or proposed for acceptance.

## Exit Criteria

- Achievement of every applicable Outcome has been assessed with observable evidence.
- The vector asset parses and renders in the intended environment or any compatibility limitation is explicit.
- Significant visual regions required for reuse can be identified and edited independently.
- Representative visual comparisons and structural inspections have been completed.
- Unresolved defects, approximations, provenance, rights conditions, dependencies, assumptions, and limitations are recorded.
- The authoritative asset and its evidence can be transferred without confusing it with a derived preview or unsupported variant.

## Controls

- Apply the repository [Process Framework](../../../spec/process-framework.md) and [ALPS Specification](../../../spec/ALPS-SPEC.md). If they conflict, the Process Framework takes precedence.
- Apply repository instructions and the requirements of the intended execution or delivery environment.
- Apply applicable copyright, trademark, license, contract, attribution, privacy, security, accessibility, and brand requirements.
- Apply the accepted visual authority, intended use, fidelity boundary, and compatibility conditions for the Process Instance.
- Apply the relevant vector format and consumer requirements within their declared scope.

## Constraints

- This general Process must not normatively prescribe a performer, editor, tracing algorithm, drawing technique, comparison metric, or execution sequence.
- A reconstruction must not be performed when the applicable rights or authorization prohibit it.
- An automatic trace must not be treated as evidence that significant structure, layer semantics, or editability has been preserved.
- Pixel equality must not be required when it would preserve incidental raster artifacts, and pixel similarity must not be treated as the sole acceptance basis.
- Geometric simplification must not remove significant visual structure solely to reduce element or control-point count.
- An embedded raster fallback, external dependency, active-content feature, or unsupported effect must not be hidden from the recipient.
- A quantitative image score must not be presented as a direct measure of aesthetic quality or semantic correctness.
- Completion must not be declared when reference ambiguity or missing evidence prevents the applicable Outcomes from being assessed.

## Enablers

- Vector editing or programmatic vector-generation capability.
- Reliable vector rendering and raster export capability.
- Visual design, iconography, illustration, typography, color, and accessibility expertise appropriate to the subject.
- Image comparison, edge inspection, overlay, magnification, and multi-size preview capability.
- The bundled SVG structural inspector and other passive-asset inspection tools.
- Stakeholder or visual-authority review capability.
- High-resolution, uncropped, color-managed, or source references when available.

## Conformance

This Skill represents the Layered Vector Reconstruction Process and claims Description Conformance against the applicable Process Framework and ALPS requirements. A Process execution may be assessed against Outcomes, Tasks, or both; the selected basis, intended use, representative display conditions, and evidence must be stated. A structurally valid SVG, a successful render, or a high image-similarity score does not by itself establish Process Conformance or acceptable visual fidelity.

## Interfaces & Traceability

| Information item provided | Primary recipient | Related information |
|---|---|---|
| Visual structure and layer plan | Vector reconstruction or subsequent revision | Reference identity, significant regions, z-order, editability needs, and ambiguity. |
| Layered vector asset | Asset integration, publication, or downstream design work | Coordinate system, dependencies, authoritative version, and intended use. |
| Rendered previews and comparison evidence | Visual acceptance or quality review | Display conditions, reference version, observed deviations, and limitations. |
| Verification and deviation record | Acceptance, asset management, or controlled improvement | Outcome evidence, defects, dispositions, assumptions, and approval basis. |
| Provenance and rights conditions | Asset recipient and repository maintenance | Source authority, authorization, attribution, restrictions, and reuse conditions. |

## Bundled Resources

- [Visual Structure Record](references/visual-structure-record.md) is an informative output-creation resource for reference qualification, significant-feature analysis, layer planning, and decision traceability.
- [Verification Guide](references/verification-guide.md) is informative guidance for structural, perceptual, editability, and transfer assessment without reducing acceptance to one metric.
- [ALPS Icon Representative Trial](references/alps-icon-trial.md) records a representative reconstruction assessment and Outcome-achievability evidence from the earlier ALPS mountain icon work.
- [`scripts/inspect_svg.py`](scripts/inspect_svg.py) reports passive structural facts about an SVG. It does not assess visual fidelity, aesthetic quality, rights, or ALPS Conformance.

## Common Approach

This section is reference information and has no normative force.

- Begin with silhouette, negative space, landmarks, and overlap before refining local facets or paint details.
- Treat automatic tracing as one source of candidate geometry rather than as the reconstructed asset.
- Prefer a small number of intentional regions over a large number of paths that merely encode antialiasing or compression variation.
- Compare both the complete composition and isolated layers at native, smaller, and larger representative sizes.
- Use quantitative comparisons to locate differences, then judge those differences against the intended use and significant-feature analysis.
- Preserve stable identifiers for regions expected to be recolored, hidden, animated, replaced, or inspected downstream.
