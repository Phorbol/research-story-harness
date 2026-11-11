# Source-bound Fig. 5 structure assets

Use `final/copper_*.png` (8 transparent 1800×1400 OVITO Tachyon renders), `asset-handoff.json` (identities, source pages, exact atom pixels), and `vector-overlays.json` (C–O and nearest Cu–O geometric endpoint pairs). Do not use the low-sampling `preview/` in publication. No text is burned into the PNGs.

`coordinates/` contains all 44 structures extracted from the author's coordinate supplement SC-013-D2SC02107B-s002.pdf. Source atom order, Å coordinates, cell and PBC are preserved. `source-mapping.json` records the PDF page ranges and path/Str identifiers. The source's absolute “Free energy from VASP” values are raw metadata; they are **not** the 473 K relative Gibbs energy curve and must not be substituted for it.

TS1–TS4 labels are correspondences established from the supplement path heading, alternating minimum/TS sequence, local geometry, and article Fig. 5 (article PDF page 8, journal p. 8155):

| Figure label | Supplement structure | C–O pair (0 based) | Extracted distance / Å | Article snapshot / Å |
|---|---|---|---:|---:|
| TS1 | 1,2-PDO-dehydrogenation Str 6 | 11–14 | 1.884 | 1.88 |
| TS2 | 1,3-PDO-dehydrogenation Str 6 | 10–13 | 2.009 | 2.00 |
| TS3 | 1,3-PDO-dehydration Str 4 | 10–13 | 2.286 | 2.29 |
| TS4 | 1,2-PDO-dehydration Str 4 | 11–14 | 2.560 | 2.56 |

DHA is path 1 Str 5, figure state 6 is path 1 Str 7, acetol is path 1 Str 9, glycerol is path 1 Str 1. PDF Str numbers must not be equated with figure state numbers. TS matching is a supported mapping, not an explicit TS label supplied inside the coordinate tables or an independent saddle-point verification.

Display transformations are explicit: bottom Cu atoms wrapped near z=20 Å are translated by −c into the contiguous slab; adsorbates are minimum-image unwrapped around source C10; each full frame is rigidly centered; Cu images are regenerated per state because independent states wrap substrate atoms differently. `display-transforms.json` and final scene metadata retain these mappings. The shared surface view direction, scale, radii and colors are fixed. State6 is centered using all C/O atoms to keep its detached OH fully inside the frame. No selected reaction atom is deleted. Only the top two Cu layers and a finite periodic surface patch are displayed.

`surface_render_transparent.py` is a local adaptation of the frozen surface script: transparent output, carbon anchoring via job, per-state substrate image patch, and recorded rigid centering. Frozen originals remain untouched. Distances and sticks are geometric adjacency, not evidence of bond order, transition-state validation, electron flow, or mechanism by themselves.

`molecules/` contains source-coordinate molecular cutouts for glycerol, DHA, acetol, 1,2-PDO, and 1,3-PDO. These omit the slab and disconnected coadsorbates, use distance connectivity to select the carbon-containing component, and preserve source atom indices. These are identity assets rather than full reaction states. Glycerol uses an individually chosen view to expose its carbon/oxygen skeleton; compare internal geometry from coordinates, not these identity-view camera orientations.

Verification: all 44 structures have finite coordinates and exactly 64 Cu atoms; expected totals are 80 or 77. Eight final surface PNGs are RGBA, 1800×1400, with transparency. All final surface and molecular assets were actually viewed. The low-preview faceting vanished in the final 64-AO/8-AA renders. A same-coordinate OSPRay comparison was inspected and retained in `ospray-check/`, but was darker and was not chosen. Source coordinates were not optimized or reconstructed from raster imagery. Metal initialization required authorized execution of the same rendering commands.
