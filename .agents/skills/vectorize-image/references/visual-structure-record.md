# Visual Structure Record

This resource is an informative aid for applying the Layered Vector Reconstruction Process. It helps make visual interpretation, layer planning, and reconstruction decisions inspectable. It does not define an ALPS requirement, require one drawing method, or establish Conformance by being completed.

## 1. Subject and Authority

| Field | Record |
|---|---|
| Asset or subject name | |
| Intended use | |
| Authoritative reference | |
| Supporting references | |
| Reference version or checksum | |
| Reference dimensions and color conditions | |
| Representative display conditions | |
| Required output and compatibility | |
| Required independent editability | |
| Decision authority or reviewer | |

## 2. Provenance and Rights

Record what permits the reconstruction and what conditions travel with the result.

| Concern | Record |
|---|---|
| Source and provenance | |
| Owner or licensor | |
| Authorization or license basis | |
| Trademark or brand conditions | |
| Attribution requirement | |
| Privacy or personal-data concern | |
| Redistribution or modification restriction | |
| Unresolved rights question | |

Do not infer authorization from possession of an image. A technical reconstruction can be successful while use or redistribution remains prohibited.

## 3. Reference Conditions

Identify conditions that can change how the reference is interpreted.

- Cropping or missing margins:
- Transparency and background assumptions:
- Compression, resampling, sharpening, or antialiasing:
- Color profile, gamut, or unknown color conversion:
- Blur, noise, scan artifacts, or screenshot artifacts:
- Perspective, lens, lighting, or photographic effects:
- Known source variants or inconsistencies:
- Features whose authority is uncertain:

## 4. Significant Visual Structure

The following categories are diagnostic prompts. Use only the categories that matter to the intended use.

### 4.1 Composition and Geometry

- Outer silhouette and composition bounds:
- Negative spaces and openings:
- Principal contours and directional axes:
- Alignment anchors and landmarks:
- Relative proportions and spacing:
- Symmetry, asymmetry, repetition, or rhythm:
- Small-scale features that remain necessary:
- Features that may disappear at representative small sizes:

### 4.2 Regions and Relationships

- Major regions or facets:
- Foreground, middle-ground, and background:
- Overlap and z-order:
- Clipping and masking relationships:
- Shared boundaries between regions:
- Region seams that must remain invisible:
- Regions requiring independent selection, recoloring, hiding, or replacement:

### 4.3 Paint and Appearance

- Flat colors and their relationships:
- Gradients and gradient direction:
- Strokes, caps, joins, and dash behavior:
- Opacity and compositing:
- Shadows, highlights, glows, and filters:
- Texture or noise that is structurally meaningful:
- Color differences that are likely incidental raster variation:

### 4.4 Text and Symbols

- Text content and language:
- Typeface authority and availability:
- Live-text, outline, or replacement requirement:
- Typographic alignment and spacing:
- Symbol meaning and recognizability:
- Accessibility name or description:

## 5. Layer and Element Plan

Use stable identifiers when downstream work needs to address a visual region directly.

| ID or proposed ID | Reference region | Visual role | Geometry or paint responsibility | Z-order / relation | Independent editability needed | Confidence / ambiguity |
|---|---|---|---|---|---|---|
| | | | | | | |

The plan should explain visual responsibilities rather than mirror every color cluster or trace fragment. Multiple paths can form one coherent layer, and one path can serve more than one appearance role through clipping or reuse when that remains understandable.

## 6. Detail and Simplification Decisions

| Reference feature | Preserve, approximate, omit, replace, or separate | Rationale tied to intended use | Verification needed |
|---|---|---|---|
| | | | |

Typical questions include:

- Does the detail change the silhouette, negative space, landmark, or region identity?
- Is it still visible at representative sizes?
- Is it a deliberate design decision or an artifact of rasterization?
- Would simplifying it make editing clearer without changing perception?
- Does retaining it create unnecessary control points, seams, or paint resources?

## 7. Acceptance Basis

State how the reconstructed asset will be judged. Avoid an unexplained scalar threshold.

- Significant features that must match closely:
- Features for which controlled approximation is acceptable:
- Representative sizes, backgrounds, and export conditions:
- Structural checks:
- Editability checks:
- Perceptual comparison methods:
- Quantitative diagnostics, if any:
- Decision authority and disposition method:

## 8. Decisions, Deviations, and Unknowns

| Item | Decision or current state | Evidence | Consequence | Disposition owner |
|---|---|---|---|---|
| | | | | |

## 9. Traceability to Process Outcomes

| Outcome | Evidence location | Status | Limitation or follow-up |
|---|---|---|---|
| a) Use, authority, display conditions, and fidelity boundary are identified. | | | |
| b) Significant structure is distinguished from raster artifacts. | | | |
| c) Significant geometry and visual hierarchy are preserved. | | | |
| d) Required regions and overlap relationships remain identifiable and editable. | | | |
| e) Complexity is proportionate to significant structure. | | | |
| f) Verification, provenance, rights, assumptions, deviations, and limitations support a decision. | | | |
