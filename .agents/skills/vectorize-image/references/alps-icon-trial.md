# ALPS Icon Representative Trial

This record documents a representative trial of the Layered Vector Reconstruction Process using retained artifacts from the earlier ALPS mountain icon work. It demonstrates Outcome achievability; it does not make the metrics below normative, establish rights for unrelated source material, or claim that every prior editing action followed the final Process Description.

## Trial Subject

- Reference: retained 2048 × 2048 RGBA PNG of the blue ALPS mountain icon.
- Reconstruction: retained 1024 × 1024 layered SVG produced during the earlier icon reconstruction work.
- Intended use: a scalable application or Plugin icon with recognizable mountain, snow, facet, and rounded-square structure.
- Representative comparison: both assets rendered or retained at 2048 × 2048 on a transparent background.

The source PNG is not redistributed through this repository. The trial record retains derived structural facts and comparison results rather than adding another authoritative visual asset.

## Significant Structure Identified

The trial treated the following as significant:

- the rounded-square occupied silhouette and transparent exterior;
- the vertical blue sky gradient and central light glow;
- three principal mountain peaks and their relative positions;
- white snow regions and pale transition facets;
- dark and mid-blue mountain facets;
- the long diagonal foreground facet;
- overlap and z-order among sky, mountain body, dark facets, and snow; and
- recognition and legibility at icon scale.

Antialiasing along vector boundaries and isolated subpixel color differences were treated as rasterization effects rather than design regions.

## Vector Structure Observed

A passive structural inspection of the retained SVG found:

| Fact | Result |
|---|---:|
| View box | `0 0 1024 1024` |
| Groups | 3 total |
| Named semantic groups | `mountain`, `snow` |
| Paths | 8 |
| Rectangles | 2 |
| Linear gradients | 1 |
| Radial gradients | 1 |
| Clip paths | 1 |
| Embedded raster images | 0 |
| Scripts | 0 |

The reconstruction therefore expressed the composition with vector geometry and shared paint resources rather than embedding the reference raster.

## Render Comparison

The SVG was rendered at 2048 × 2048 with CairoSVG 2.8.2. The result was compared with the retained PNG using normalized RGBA values and scikit-image structural similarity.

| Diagnostic | Result |
|---|---:|
| Alpha-mask intersection over union | 0.998160 |
| RGB SSIM | 0.995081 |
| Interior RGB mean absolute error | 0.000946 |
| Pixels with maximum RGBA difference no greater than 1/255 | 97.4613% |
| Occupied-union pixels with maximum RGB difference no greater than 2/255 | 98.7524% |

These values corroborated close raster correspondence. They did not determine whether the grouping was meaningful or whether the icon was aesthetically successful.

## Perceptual and Editability Findings

- The outer occupied silhouette, rounded-square boundary, mountain peaks, snow regions, dominant facets, and diagonal foreground relationship were preserved.
- The sky gradient and central light behavior were preserved at the assessed size.
- The `mountain` and `snow` groups permitted those major regions to be inspected or changed independently.
- The rendered and reference images differed primarily around antialiased and clipped boundaries.
- Individual facet paths did not carry stable IDs. This did not prevent the intended static icon use, but stable element identities would improve downstream facet-specific recoloring or replacement.
- The trial did not assess alternate rendering engines, very small icon sizes, color-managed print use, or accessibility metadata.

## Outcome Evidence

| Outcome | Evidence | Trial conclusion |
|---|---|---|
| a) Use, authority, display conditions, and fidelity boundary are identified. | Trial subject and comparison conditions above. | Achievable and demonstrated for the retained icon pair. |
| b) Significant structure is distinguished from raster artifacts. | Significant-structure list and treatment of antialiasing. | Achievable and demonstrated. |
| c) Significant geometry and visual hierarchy are preserved. | Perceptual findings, alpha overlap, and image-similarity diagnostics. | Achievable and demonstrated at the assessed condition. |
| d) Required regions and overlap relationships remain identifiable and editable. | Named `mountain` and `snow` groups, vector-only structure, and z-order inspection. | Achievable for major regions; facet-specific identity remains a recorded limitation. |
| e) Complexity is proportionate to significant structure. | Eight paths, two paint rectangles, two shared gradients, and no embedded raster. | Achievable and demonstrated for the assessed icon. |
| f) Verification, provenance, rights, assumptions, deviations, and limitations support a decision. | This record, retained artifact identity, comparison configuration, and explicit limitations. | Achievable and demonstrated; source redistribution remains outside this record. |

## Trial Conclusion

The retained ALPS icon pair demonstrates that a flattened visual reference can be reconstructed as a compact, passive, layered SVG while preserving the significant visual structure needed for icon use. The trial also shows why structural inspection and human interpretation must accompany image-similarity metrics: a high raster match alone would not reveal whether meaningful regions remained editable or whether incidental raster artifacts had been encoded as geometry.
