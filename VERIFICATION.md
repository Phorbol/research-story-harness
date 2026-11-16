# Reproducibility and verification

Recorded environment and checks for the distributed examples and runtime, dated per section (the original bundle checks are from 2026-11-11). Use the commands below to verify your own installation.

## Optional MatterViz preview (2026-11-16)

The [inspection and snapshot workflow](skills/ovito-structure/references/post-model-visualization.md) was exercised with MatterViz v0.9.0, commit `6d3fbfc9f17581a7a6733dbf6558f190ef83aac6`, Node 24.22.3 and Playwright Chromium on Linux/WSL. It reuses the upstream snapshot CLI; no RSH renderer, default dependency or project schema changed.

- Both bundled `examples/supported-nanoparticles/models/illustrative-Pd{Zn,Cu}-ZnO.extxyz` files were supplied directly, without XYZ conversion or cell/PBC removal. They are unrelaxed illustrative models, not experimental structures.
- With the bundled `matterviz-preview.json`, `--width 1000 --height 800 --dpi 72` and the upstream `CI=1` software-WebGPU path, the CLI exited successfully and returned **1,413 sites for each input**. Both PNG dimensions were 1000 × 800 and both source SHA-256 digests were unchanged after rendering.
- Both actual PNGs were viewed: atoms, the supported-particle model and cell were visible, with no inferred bond/polyhedron network. The default view leaves the cell prominent and some sites occluded; this establishes working preview output, not publication-ready framing or visibility of every reaction site. Site-count equality and unchanged input bytes do not validate every detail of the viewer's structural interpretation.
- The first launch failed because Chromium could not locate `libnspr4.so`. The retry supplied browser shared libraries from an existing environment through a process-local loader path. No system packages or global configuration were changed. This is an existing-environment smoke, not a clean installation or cross-platform test. The upstream Three.js deprecation warning remained non-fatal.
- The normal RSH installer copied the new entry, reference and props into an isolated destination; their bytes matched the source. Relative links and `git diff --check` passed. The Python runtime was unchanged and the complete Python test suite was not rerun for these documentation/assets additions.

Interactive editing in this checkout, mixed occupancy, periodic-image identity, shared-camera parity, atom-label projections and alternative operating systems remain outside this smoke. The snapshot captures the 3D canvas only; the existing OVITO publication workflow remains in place.

## Observed results

### MatterViz maintainer rerun and dependency repair (2026-11-17)

The [pinned setup](skills/ovito-structure/references/matterviz-setup.md) and [supported-particle inspection example](examples/supported-nanoparticles/matterviz/README.md) were checked on macOS 26.6 arm64 / Node 26.8.2. These results supplement, rather than replace, the contributor's Linux/WSL record above.

- Unmodified v0.9.0 installation failed: pnpm 11.25.0 and 11.5.0 rejected the Git dependency's prepare step. A local authorization for that dependency revealed a second failure: `svelte-widgets#main` at `412ecfa6e1a5504ad4ecb96d113aa4d839ab7201` lacked exports needed by MatterViz, producing 13 build errors. A separate npm download timeout was resolved and was not treated as an API incompatibility.
- The compatibility change uses the **npm release** `svelte-widgets@1.11.0` (gitHead `29a64aa5cd8e18867fee9b469882b1a0715f8b5a`) and the bundled dependency lockfile. A fresh checkout with no node_modules, dist or build-authorization configuration completed frozen installation and the full prepare build. Downloads were reused from a package cache; this is a fresh-checkout check on an existing OS, not a pristine-machine or cross-platform certification. The installation was bootstrapped by pnpm 11.25.0, which selected the upstream packageManager's **11.5.0**; the documented command selects 11.5.0 directly.
- Playwright 1.65.1's Chromium installation entrypoint succeeded using the existing isolated browser cache. The fresh checkout rendered both models with both the original preview props and the example's display-only props: four actual 1000 × 800 PNGs, 1,413 sites each. The Mac run did not require `CI=1`. Non-fatal Node localStorage and Three.js deprecation warnings remained.
- MatterViz's parser was compared with every source site: elements/occupancy, Cartesian coordinates, tags, cell and all-false PBC matched, with maximum coordinate difference 0 Å. Source SHA-256 digests remained unchanged. This does not extend to mixed occupancy or periodic-image validation.
- The actual default images leave the auxiliary cell prominent and the interface obscured. The adjusted view makes the supported-particle relationship easier to see but remains an inspection preview, not a publication-quality replacement for OVITO. A first manual-camera attempt inherited a 10° field of view and was severely cropped; the example explicitly supplies 45°. These are example-specific display choices, not scientific defaults.
- The local v0.9.0 PdZn viewer was exercised for site-table/coordinate reading, rotation, hover coordinates, coloring by tags and hiding the support group. Screenshots are bundled with the example. A two-point measurement attempt timed out in browser automation before a verified result; measurement is not counted as passed. The timeout alone does not identify a MatterViz defect. VS Code installation, editing/export round trips and other structures remain untested.

The original OVITO images are comparison references, not newly rendered outputs in this check. File/skill validation establishes packaging integrity; actual image inspection and interactive observations establish the limited visual/inspection conclusions above.

### Original bundle checks

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
| Pinned third-party runtime | Bundled ansatz-slide Python runtime matches the recorded upstream commit byte-for-byte |

The initial failing test resolved a scene twice while retaining its generated connection object. That caused the generated connection ID to collide before the intended outside-canvas check ran. Only the synthetic test input was corrected: it now provides an explicit arrow, then tests that moving the endpoint outside the canvas is rejected. Runtime acceptance criteria and the rejection assertion remain unchanged. The failure is not erased from these results; the corrected module passed its targeted rerun, the remaining 90 tests were not rerun after that fixture-only change.

A writing smoke invocation initially requested a draft export outside the project directory; the CLI correctly refused it. Exporting inside the project succeeded. Final-export rejection is an expected check, not an unhandled failure.

The 102-test complete run includes installer refusal to overwrite existing skills and twenty rendered revisions across four demo figure types. The reported count covers the tests distributed in this repository.

## Showcase packaging checks

- The collateral-response example was rebuilt with each of its three public commands. The resulting PNGs matched the selected three outputs pixel-for-pixel; PDF dimensions were 80 × 40, 178 × 94, and 178 × 126 mm. This checks packaging fidelity; the selected figures had already undergone separate visual and source review.
- The 20-page RFdiffusion package passed the current bundled CLI's `validate` and `inspect`. The PPTX contains all 20 pages and speaker notes. The public package keeps existing rendered slides; this pass did not claim a fresh full Office visual review or reproduce model training.
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

The one-page native slide smoke proves export and editable package structure, not presentation quality. Real demonstration figures/decks in the showcase have their own sources and viewing scope. 
