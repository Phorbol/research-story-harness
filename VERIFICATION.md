# Public-package verification / 公开包验证

Date: 2026-11-11. Checks below were run against the independent public package, not only the original development workspace. They establish software behavior within their stated scope, not scientific validity or a universal visual-quality result.

## Observed results

| Check | Result |
|---|---|
| All selected skill frontmatter/naming checks | 11/11 passed using the existing skill-creator validator |
| Repository tests, initial complete run | 102 ran; 101 passed, 1 failed in a newly adapted synthetic test fixture |
| Targeted rerun after correcting that fixture | All 12 tests in `test_scene_layout_energy.py` passed |
| Additional skill-local review consistency tests | 1/1 passed |
| Writing CLI | Initialized project; registered synthetic claim/unit; audit ran; draft export succeeded and contained the registered text |
| Writing acceptance boundary | Unreviewed final export returned code 2 and created no final file |
| Slide CLI | Synthetic one-page YAML validate, native PPTX export and package inspect succeeded; native editable text confirmed inside the PPTX XML |
| Public data examples | condition-map and reaction-energy each generated PNG, PDF and SVG successfully from the bundled public inputs |
| Public source hygiene | Scoped personal-path, project-name and common credential-pattern scan found no matches at core-package handoff |
| Pinned third-party runtime | Bundled ansatz-slide Python runtime matches the recorded upstream commit byte-for-byte |

The initial failing test resolved a scene twice while retaining its generated connection object. That caused the generated connection ID to collide before the intended outside-canvas check ran. Only the synthetic test input was corrected: it now provides an explicit arrow, then tests that moving the endpoint outside the canvas is rejected. Runtime acceptance criteria and the rejection assertion remain unchanged. The failure is not erased from these results; the corrected module passed its targeted rerun, and the other 90 tests were not needlessly repeated.

A writing smoke invocation initially requested a draft export outside the project directory; the CLI correctly refused it. Exporting inside the project succeeded. Final-export rejection is an expected check, not an unhandled failure.

The 102-test complete run includes installer refusal to overwrite existing skills and twenty rendered revisions across four demo figure types. Two historical workbook-extractor tests are outside the public package because their case-specific analysis script is not distributed; see [RELEASE_SCOPE.md](RELEASE_SCOPE.md). They are not counted as public passes.

## Showcase packaging checks

- The collateral-response example was rebuilt with each of its three public commands. The resulting PNGs matched the selected three outputs pixel-for-pixel; PDF dimensions were 80 × 40, 178 × 94, and 178 × 126 mm. This checks packaging fidelity; the selected figures had already undergone separate visual and source review.
- The 20-page RFdiffusion package passed the current bundled CLI's `validate` and `inspect`. Its 98 PPTX XML/relationship files, including all 20 notes, and selected page sources/PDF text were checked for the known internal-project names and personal-path patterns. The public package keeps existing rendered slides; this pass did not claim a fresh full Office visual review or reproduce model training.
- Supported nanoparticle coordinates were matched to the recorded OVITO scenes; existing PNGs and their alpha channels were retained. Render metadata identify OVITO Tachyon CPU 3.16.0. The model construction and OVITO renderer were not rerun during public packaging. The comparison preview was composed and viewed.
- README's condition-map and reaction-energy images were regenerated from the public package and opened for inspection. The cover and full-deck overview are composites of existing outputs, with no changes to scientific data.

## Re-running the tests

From the repository root in the configured Python environment:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s skills/research-harness/tests -v

# The corrected module can be run independently:
python -m unittest discover -s tests -p test_scene_layout_energy.py -v
```

The tests create their own temporary synthetic projects. They do not need historical case folders, private coordinates, publisher fonts or downloaded research papers. Rendering regressions may take longer on a fresh font cache.

## Environment and limits

Observed environment: Python 3.12.14, Matplotlib 3.9.4, NumPy 2.5.4, ASE 3.26.0, OVITO 3.16.0, PyMuPDF 1.26.5, PyYAML 6.0.2 and Pillow 13.0.0. The package retains upstream's PyYAML 6.0.3 pin for installation; these smoke checks used the already available 6.0.2 environment. A clean dependency installation was not run, and no claim of Windows/Linux/Office-version compatibility follows from these checks.

ASE/NumPy and Matplotlib/pyparsing emitted deprecation warnings without failing the tests. These were not suppressed by changing test assertions. h5py was not installed in this environment; HDF5 re-extraction was not repeated, while the condition-map plot used the already included CSVs. Actual OVITO image rendering and Office visual preview are separate workflow checks; the portable surface tests exercise read-only identity and display preparation.

The one-page native slide smoke proves export and editable package structure, not presentation quality. Real demonstration figures/decks in the showcase have their own sources and viewing scope. Pattern scans are bounded checks, not a proof that every possible sensitive string is absent. Publication and external upload are separate actions from this local package verification.
