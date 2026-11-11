# Repository contents

Research Story Harness combines eleven optional skills with local writing, figure and presentation tools. Install only the dependencies needed for your workflow; see [DEPENDENCIES.md](DEPENDENCIES.md).

| Directory | Contents |
|---|---|
| `skills/` | Skill entrypoints, reference guidance, runtime code, schemas and templates |
| `examples/collateral-response/` | TOC, Fig1 and data figures with public source data and editable exports |
| `examples/supported-nanoparticles/` | Idealized ASE models, OVITO renders, construction code and camera/style configuration |
| `examples/rfdiffusion/` | A complete Chinese presentation, PPTX/PDF, page sources, images and speaker notes |
| `skills/research-harness/assets/real-data-examples/` | Runnable condition-map and reaction-energy recipes |
| `docs/images/` | Showcase previews and their attribution index |
| `tests/` | Self-contained software regressions with synthetic fixtures |
| `design/` | Architecture and workflow design |

## What you supply

Your research materials, scientific conclusions, target audience and output requirements belong in a separate project. The installed skills provide guidance and tools; they do not contain your project data or run an autonomous background service. Agent access, model availability and network retrieval depend on the host application.

## Reuse

Original code and documentation are [Apache-2.0](LICENSE). Third-party software and example materials retain their [component-specific terms](THIRD_PARTY_NOTICES.md), including the noncommercial restriction on the reaction-energy paper assets.

Examples record their source, transformation, editing entrypoints and scientific limits. Software checks and known environment coverage are described in [VERIFICATION.md](VERIFICATION.md).
