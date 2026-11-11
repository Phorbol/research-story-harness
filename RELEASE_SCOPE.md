# Public package scope / 公开包范围

This package contains the complete selected 11-skill toolchain, its runtime helpers, schemas, templates, portable tests, design documentation, two bundled public-data recipes, and additional public showcase examples. “Complete toolchain” means the capabilities and their required resources are included; external dependencies must still be installed. It does not mean every historical experiment, paper or conversation is public.

本包保留科研材料、论证、写作、图件、结构和学术汇报的 11 个技能及运行资源。历史用户材料不因发布工具链而一并公开。

## Included

- `academic-writing`, `argument-architect`, `context-pack-builder`, `manuscript-auditor`, `manuscript-editor`, `paper-dissector`, `source-harvester`, `scientific-figure`, `research-harness`, `ovito-structure`, and `ansatz-slide`.
- Writing state management, schemas and shared references; figure/project validation, rendering, revision and source binding; the pinned editable-slide CLI and OOXML templates.
- Editable narrative templates, a generated synthetic landscape, synthetic demo inputs and synthetic tagged surface fixtures.
- Public condition-map author data (CC BY 4.0) and the separately identified reaction-energy example (CC BY-NC 3.0). See [attribution](THIRD_PARTY_NOTICES.md).
- Three collateral-response figures based on public PLOS S1 Data, a 20-page RFdiffusion presentation with editable source and required public-paper assets, and explicitly idealized supported nanoparticle models/renders. These are curated public exports; their sources and limits are kept beside them.

## Deliberately not distributed

Private manuscripts, user conversation and assessment records, original user surface coordinates/reference images, complete publisher article PDFs, extracted publisher font subsets, frozen development copies, virtual environments, caches and wholesale historical experiment directories. Selected public figure and slide previews are included explicitly for the showcase.

Project-specific names and application details in general guidance were generalized. Public bibliography, origin/interpretation distinctions and scientific limitations remain. Historical internal quality-comparison PDFs are omitted; the two public examples and editable templates provide the reusable demonstrations.

## Portable tests

Existing runtime regressions now construct synthetic source, scene, story, trace, recipe and geometry fixtures within temporary projects. They preserve checks for source drift, alternative/decision handling, claim bindings, missing values, physical size/baselines, rendered object identity, explicit uncertainty, typography and periodic surface identity. Tests never require private research data or fonts extracted from a paper.

Two old tests of a case-specific `extract_jacs_co.py` workbook-conversion script are not distributed because that analysis script and its external workbook are not part of this toolchain. They are not counted as passing public tests. No core runtime acceptance assertion was deleted to conceal a failure; remaining external-case tests were adapted to controlled inputs with the same behavior checks.

The public synthetic surface fixture checks software behavior, not agreement with a private reference image. The new qualitative landscape is algorithmic illustration, not a recovered original asset. Existing source metadata and limitations remain beside the real-data examples.

## Licensing and verification boundaries

The owner has not assigned a blanket first-party open-source license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for existing component-specific permissions and restrictions.

Unit tests and command-line smoke checks establish only their declared software properties. They do not establish scientific correctness, publication readiness, independent reader comprehension, visual quality on every device, or compatibility with every Office/OVITO environment. Installed dependencies and optional system renderers must be available for the selected workflow.
