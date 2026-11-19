# Final-export checks

Run after saving the first complete artifact; preserve that artifact before fixing findings. Select the minimum font size for the actual target dimensions. Do not scale a large canvas down and audit the original instead.

```sh
python3 scripts/export_audit.py figure.pdf --min-pt 7 --out reports/export
```

Collision extraction requires PyMuPDF (`python -m pip install PyMuPDF` in the project environment). The font auditor has bounded PDF support; missing auditable text is not success. Inspect each raw report and collision overlay. Intentional labels inside heatmaps or structural images need visual interpretation; rasterized or outlined text cannot be assumed covered.

For comparable multi-panel plots, pass `--layout measured-layout.json`. Obtain geometry from the rendered backend, not intended coordinates: import `scripts/vendor/nature_figure/audit_panel_alignment.py` and use its Matplotlib extraction functions, or provide the documented JSON geometry. Do not force equal widths on intentional hero panels or insets.

These checks report export defects, not story, scientific validity, readability or publication quality. Review at the requested physical size separately. Preserve pre-fix files, raw findings, interpreted findings and changes so improvements can be attributed to actual feedback.

Upstream files and Apache-2.0 license are retained in `scripts/vendor/nature_figure`; the adapter preserves raw findings. A documented local patch excludes stroke candidates wholly outside explicit rectangular clips; complex and partial clipping remain limitations (see vendor/nature_figure/LOCAL_PATCH.md).
