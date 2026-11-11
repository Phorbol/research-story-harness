# Current v2 addendum

The current v2 package was copied to a fresh temporary directory and run from `/` on 2026-11-09. Exit code 0; PNG pixel-identical to the visually reviewed typography-refinement output. Geometry and typography changes are described in STYLE-REVISION.md. The following record describes the earlier v1 packaging, not the current page size or font sizes.

# Verification record — 2026-11-09

## Source data

Included author H5 arrays were compared field by field with the editable CSVs: 200, 200, 62500 and 40000 rows, maximum absolute difference 0 for every array. The initial comparison mistakenly included the CSV identity column and failed with a shape mismatch; excluding the non-numeric identity column corrected the check, without changing data. See `source-data-check.json`.

In the isolated copy, `extract_source.py` recreated CSVs byte-identical to the delivered files. The optional extraction used h5py from an existing verification environment; rendering itself does not need h5py.

## Portability

The entire example was copied into a new `/tmp/portable-figures-0q09wvpp/condition-map` directory, excluding generated output. From working directory `/`, the copied `run.py` completed with exit code 0. Its PNG was pixel-identical to the workspace output. The exact command and results are in `portability-check.json`.

Environment actually used: NumPy 2.5.4, Matplotlib 3.9.4. No fresh dependency installation or full version-range compatibility test was performed.

## Visual observations

The historical `CatalystConditions.png`, the new PNG and a Poppler rendering of the final PDF were actually opened and compared. The four-panel arrangement, curve shapes, reference lines, equality contour, color scale and undefined double-zero cells are retained. DejaVu Sans is slightly wider than the original Arial. Axis titles, panel titles and neighboring plots remain separated; no clipped lettering or lost curve information was observed in the current export.

The PDF page is 148.160 × 126.000 mm. Body/axes use 7.2 pt and ticks 6.6 pt. These dimensions and point sizes were inspected in the PDF; the screen preview is not a physical print proof.

Remaining limitations: the lower-left temperature-map region retains the source grid's granular undefined cells; no unsupported filling was applied. Model uncertainty intervals remain absent. There was no independent reader test or scientific validation of the kinetic model. Successful execution and these bounded visual observations are not publication approval.
