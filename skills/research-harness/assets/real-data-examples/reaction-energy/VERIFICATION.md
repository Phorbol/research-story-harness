# Current v2 addendum

The current v2 package was copied to a fresh temporary directory and run from `/` on 2026-11-09. Exit code 0; PNG pixel-identical to the visually reviewed typography-refinement output. Geometry and typography changes are described in STYLE-REVISION.md. The following record describes the earlier v1 packaging, not the current page size or font sizes.

# Verification record — 2026-11-09

## Source data

The renderer reads four routes from the included energy CSV. TS numeric annotations read the same CSV, rather than retaining stale literal values. The four C–O distances were recalculated from the included source coordinates and cells using the minimum-image convention. Every value agrees exactly with the overlay metadata; see `source-data-check.json`. This is a geometry check, not an independent transition-state verification.

## Portability

The entire example was copied into a new `/tmp/portable-figures-0q09wvpp/reaction-energy` directory, excluding generated output. From working directory `/`, its `run.py` completed with exit code 0. The copied PNG was pixel-identical to the workspace output. Exact command and results: `portability-check.json`.

Environment actually used: NumPy 2.5.4, Matplotlib 3.9.4. No fresh dependency installation or full version-range compatibility test was performed.

## Visual observations

The historical full `network-energy-TS.png`, its B panel and the new standalone PNG were actually opened and compared. A Poppler rendering of the final PDF was also opened. The four early routes, blue continuation, four structure views, four distance leaders, open endpoints and coadsorbate labels remain present. The first standalone crop clipped the panel letter at the top; the top margin was increased and the regenerated output was inspected. The final letter is complete.

The final PDF measures 153.900 × 82.377 mm and retains the historical B panel's physical geometry. The reaction C–O pairs and dashed lines are visible; current distance labels do not cover the reaction atoms. No new collision between numeric labels and curves was observed. Finite substrate image boundaries are preserved from the original structure assets.

Remaining limitations: 5.8 pt legend/footnote text and 6 pt state labels are still small at this width. This is an editable extraction of a dense mature local panel, not a claim of journal-wide typography compliance. Smooth connectors are visual guides, and unresolved later-route mapping remains explicitly marked. Screen inspection is not a physical print proof, an independent blind read or new TS confirmation.
