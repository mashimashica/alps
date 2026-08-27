# Verification Guide

This resource provides informative guidance for verifying a layered vector reconstruction. It does not prescribe one tool, metric, sequence, or universal threshold. Verification should be designed around the intended use, authoritative reference, significant-feature analysis, and representative display conditions.

## Verification Perspectives

A useful verification combines four perspectives. None is sufficient by itself.

| Perspective | Primary question | Typical evidence |
|---|---|---|
| Structural | Does the vector scene express the intended elements and relationships? | Element and group inspection, IDs, z-order, clipping, masks, gradients, dependency and active-content inspection. |
| Perceptual | Does the rendered result preserve the significant visible structure? | Side-by-side comparison, overlays, flicker comparison, edge or difference maps, multi-size renders, reviewer observations. |
| Editability | Can required regions be changed without unintended collateral change? | Selection, isolation, hide/show, recolor, replace, transform, or export trials. |
| Transfer | Can the recipient use the asset with its authority and limitations intact? | Parse/render checks, metadata, compatibility, provenance, rights, version, and dependency records. |

## Representative Display Matrix

Record only conditions that can change the acceptance judgment.

| Condition | Examples | Selected instance conditions |
|---|---|---|
| Dimensions | native size, minimum icon size, enlarged display | |
| Pixel density | 1×, 2×, 3× | |
| Background | transparent, light, dark, branded | |
| Export | direct SVG, raster preview, platform conversion | |
| Color | standard gamut, managed profile, monochrome variant | |
| Rendering engine | browser, design tool, host application | |
| Interaction | static, recolored, animated, masked, composited | |

## Structural Verification

Inspect facts that can be determined without judging appearance.

- The file parses as the intended vector format.
- Coordinate dimensions and view box are present and appropriate.
- Required layers or groups are identifiable.
- IDs needed by downstream work are present and unique.
- Z-order, clipping, masking, shared definitions, and paint resources are understandable.
- Embedded raster content is absent or explicitly justified.
- External references and transfer dependencies are explicit.
- Active content, event handlers, scripts, or unsupported foreign content are absent from a passive asset unless explicitly required and accepted.
- Derived variants are distinguishable from the authoritative asset.

The bundled `inspect_svg.py` can report some of these facts for SVG files. Its output is evidence, not an acceptance decision.

## Perceptual Verification

### Composition

- Outer silhouette and composition bounds.
- Negative spaces and openings.
- Principal axes, alignment, balance, and spacing.
- Landmark positions and relative proportions.

### Regions and Depth

- Major region boundaries and facets.
- Overlap, z-order, clipping, and masking.
- Shared seams and gaps.
- Foreground/background separation and visual hierarchy.

### Paint

- Dominant colors and relative contrast.
- Gradient direction and extent.
- Stroke weight, caps, joins, and alignment.
- Opacity, shadow, highlight, and compositing behavior.

### Use-Scale Behavior

- Recognizability and legibility at the minimum representative size.
- Absence of unintended gaps, slivers, cusps, or seams after scaling.
- Stability of rounded corners, thin strokes, and small negative spaces.
- Appropriate detail when enlarged.

## Editability Verification

Choose operations that correspond to the intended reuse rather than testing arbitrary editability.

- Isolate each required coherent region.
- Hide and restore a region without exposing unintended gaps.
- Recolor a region without affecting unrelated regions.
- Replace a symbol, text element, or facet while preserving its relationships.
- Change a shared gradient or paint definition and confirm the intended scope.
- Export or render after the edit and inspect for changed seams, clipping, or z-order.

A file can render correctly while remaining unsuitable for reuse because its paths are fused, unnamed, unnecessarily fragmented, or dependent on an embedded raster.

## Quantitative Diagnostics

Metrics can reveal where to inspect. They cannot determine whether the right visual structure was reconstructed.

| Diagnostic | What it can indicate | What it does not establish |
|---|---|---|
| Alpha-mask intersection over union | Silhouette and occupied-area disagreement | Internal structure, layer semantics, color, or aesthetics |
| Pixel MAE or RMSE | Aggregate raster difference | Perceptual importance or structural correctness |
| SSIM or related image similarity | Broad local luminance/contrast/structure similarity | Editability, semantic layering, or exact design intent |
| Edge distance or contour overlap | Boundary displacement | Correct region identity, z-order, or paint |
| Color difference | Color mismatch under a stated color model | Composition, hierarchy, or rights |
| Element/control-point counts | Complexity and possible fragmentation | Appropriate simplicity or visual fidelity |

Do not optimize a reconstruction against one metric without inspecting the resulting structure and appearance. Thresholds should be justified by the intended use and reference conditions, not copied across unrelated assets.

## Discrepancy Classification

| Class | Meaning | Typical disposition |
|---|---|---|
| Significant defect | Changes identity, silhouette, negative space, landmark, hierarchy, z-order, required editability, or intended use. | Correct before acceptance or explicitly reject the reconstruction. |
| Material deviation | Visible or structural difference with bounded impact that may be acceptable under stated conditions. | Correct or accept with rationale and scope. |
| Incidental difference | Antialiasing, subpixel rasterization, or other difference that does not affect significant structure in use. | Record only when useful; do not preserve it mechanically. |
| Unresolved ambiguity | The reference does not support a defensible interpretation. | Obtain authority, retain alternatives, or state the limitation; do not present conjecture as fidelity. |

## Verification Record

### Identity

- Vector asset and version:
- Authoritative reference and version:
- Intended use:
- Display matrix exercised:
- Verification date and reviewer:

### Results

| Perspective or feature | Evidence | Result | Deviation / limitation | Disposition |
|---|---|---|---|---|
| | | | | |

### Quantitative diagnostics

| Metric | Configuration | Result | Interpretation and limitation |
|---|---|---|---|
| | | | |

### Outcome conclusion

- Outcomes assessed:
- Outcomes achieved:
- Outcomes not achieved or not assessable:
- Accepted deviations:
- Unresolved rights or provenance conditions:
- Acceptance decision or required next action:
