# Attribution and licensing / 来源与许可

Original Research Story Harness code, skill instructions, templates and documentation are licensed under [Apache-2.0](LICENSE), copyright 2026 Phorbol and contributors. Third-party components and paper-derived assets retain the licenses listed below. The root license does not replace these component-specific terms.

本项目原创代码、skills、模板和文档采用 Apache-2.0。第三方代码、论文图像、数据及其改编图保留原有许可；尤其注意反应能量示例中的 CC BY-NC 3.0 非商业条件。

| 内容范围 | 许可 |
|---|---|
| 原创运行代码、skills、模板、文档 | Apache-2.0 |
| `skills/ansatz-slide/python/ansatz_slide/` 及其上游 OOXML 模板、原文档 | MIT，保留上游版权；详见下文 |
| 条件地图作者数据；PLOS 与 RFdiffusion 论文来源图像、数据及改编 | CC BY 4.0，保留对应归属与改动说明 |
| `skills/research-harness/assets/real-data-examples/reaction-energy/` 中论文来源数据、坐标和改编图 | CC BY-NC 3.0；其中独立原创绘图代码仍为 Apache-2.0 |
| 原创理想颗粒构造脚本、配置及合成测试输入 | Apache-2.0 |
| 其他预览、模型文件及生成式插画 | 按对应示例的来源说明使用；根协议不对第三方权利另作授权 |

## ansatz-slide

- Upstream: [ansatzX/ansatz-slides](https://github.com/ansatzX/ansatz-slides).
- Pinned commit: `2c5669a795722d9da9bdba81572d45db35b5d3c9`; upstream version 0.0.1.
- Copyright (c) 2026 Binaryify Zhuang. [Full MIT license](skills/ansatz-slide/LICENSE).
- The vendored `python/ansatz_slide/` runtime and its bundled OOXML templates match the pinned upstream source. The existing CLI launcher, Python runtime locator and equation launcher are preserved.
- Scoped skill instructions, several reference documents and the speaking-notes composer were added or modified locally. See the exact [provenance record](skills/ansatz-slide/provenance.json) and [original entrypoint archive](skills/ansatz-slide/reference/upstream-archive.md). Upstream MIT terms remain applicable to upstream material and substantial portions of it; this notice does not remove those permissions.

## Public author-data example: condition-map

Worakul, Laplaza, Das, Wodrich and Corminboeuf, *Microkinetic Molecular Volcano Plots for Enhanced Catalyst Selectivity and Activity Predictions*, ACS Catalysis 2024, 14, 9829–9839. [DOI](https://doi.org/10.1021/acscatal.4c01175).

The included HDF5 author data are from [mikimo v1.0.1, Zenodo record 12731466](https://zenodo.org/records/12731466), dated 2024-07-12. The saved record states **CC BY 4.0**. The example extracts selected arrays and redraws selected comparisons; it does not rerun the authors' simulation. Preserve attribution, the license link, source version and change descriptions when reusing these data.

[Example source and modifications](skills/research-harness/assets/real-data-examples/condition-map/SOURCES.md) · [Saved source metadata](skills/research-harness/assets/real-data-examples/condition-map/source/zenodo-record.json) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The local plotting code is an adaptation authored for this project, not the paper authors' plotting program. No publisher article PDF or extracted publisher font is included.

## Noncommercial paper-derived example: reaction-energy

Pei-Lin Kang, Yun-Fei Shi, Cheng Shang and Zhi-Pan Liu, *Artificial intelligence pathway search to resolve catalytic glycerol hydrogenolysis selectivity*, Chemical Science 2022, 13, 8148–8160. [DOI](https://doi.org/10.1039/D2SC02107B).

The saved article permissions state **CC BY-NC 3.0**; copyright The Royal Society of Chemistry (2022). The corresponding paper-derived energies, author supplementary coordinates and adapted visualizations retain that attribution and noncommercial restriction. They are an optional example, separately scoped from executable library code; do not relicense them as unrestricted MIT/Apache assets.

[Source, coordinate mapping and derivation](skills/research-harness/assets/real-data-examples/reaction-energy/SOURCES.md) · [Saved permissions](skills/research-harness/assets/real-data-examples/reaction-energy/source/article-permissions.xml) · [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/).

The example covers a bounded local path/transition-state comparison; unresolved later-state mappings remain disclosed. It is not a full reaction-network reproduction or a new scientific calculation.

## Synthetic examples and local methods

- The public surface fixture is [explicitly synthetic](skills/ovito-structure/assets/synthetic-catalyst-example/PROVENANCE.md); it exercises atom identity and rendering configuration using constructed test coordinates.
- The original surface-rendering adapter and configuration tools are covered by the root Apache-2.0 license. Rendering methods are documented in [catalyst-surfaces.md](skills/ovito-structure/references/catalyst-surfaces.md); ASE and OVITO retain their own dependency licenses.
- The [narrative templates](skills/research-harness/assets/narrative-examples/PROVENANCE.md) contain generic diagram constructions and a newly generated, labeled synthetic landscape. Scientific-looking objects in those templates are not data.
- Tests use Matplotlib's installed DejaVu Sans font without copying it into this repository. Matplotlib and its fonts retain their own upstream licenses.

## Additional public showcase examples

- **Collateral-response figures:** Maltas & Wood, *PLOS Biology* (2019), DOI 10.1371/journal.pbio.3000515. Public S1 Data retain CC BY 4.0 attribution; three new layouts and neutral generated culture artwork are described in [the example attribution](examples/collateral-response/source/ATTRIBUTION.md). The culture artwork is not experimental evidence or artwork by the paper authors.
- **RFdiffusion talk:** Watson et al., *Nature* (2023), DOI 10.1038/s41586-023-06415-8. Selected paper images and data retain CC BY 4.0, with cropping, layout and Chinese narration identified as adaptations. See [permission text](examples/rfdiffusion/source/article-permissions.txt) and [example scope](examples/rfdiffusion/README.md). No endorsement by the original authors is implied.
- **Supported nanoparticles:** locally constructed idealized, unrelaxed ASE models and their existing OVITO renders. They are not recovered paper coordinates. See [model assumptions and render provenance](examples/supported-nanoparticles/README.md). The original construction and composition scripts use the root Apache-2.0 license. Render and model provenance remain documented with the example.
- README composite previews preserve these component-level attributions; see [image index](docs/images/README.md).

## Runtime dependency licenses

Matplotlib, NumPy, ASE, OVITO, PyMuPDF, PyYAML, Pillow and optional h5py are installed separately. Their own licenses, distribution requirements and platform availability apply. This repository does not vendor their distributions or replace their terms. Install only the dependencies needed for the selected workflow; see the root requirements files and individual example documentation.
