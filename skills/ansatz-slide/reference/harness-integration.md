# Shared story, multiple representations

Canonical research state remains in the existing project: user brief, selected story, claim/evidence records and sources. The slide renderer consumes a projection; it does not own scientific intent.

| Research object | Slide projection | Preserved meaning / boundary |
|---|---|---|
| explicit brief / selected central claim | deck brief purpose + centralClaim | preserve question, scope, uncertainty; a model-authored brief is not authenticated user consent |
| intended audience | brief audience | medium-specific adaptation is allowed; no new evidence |
| story steps / panels / paragraph roles | sections + page outline | many-to-many mapping; not one figure = one slide |
| claim IDs / supporting source IDs | outline claim/evidence + notes + mapping file | section.sources means page filenames only; external scientific IDs must stay in the mapping |
| explicit user constraints | attributed directive user_requirement | quote real user evidence; preferences inferred by model use model_proposal |
| figures, data, scientific objects | page assets / native elements | use actual source data; asset paths stay within deck project |
| source/claim revision | projection regeneration / targeted review | CLI cannot detect external research-source changes merely named in notes |
| exported figure and PPTX | representations of one story | changing media layout must not silently revise the common claim |

Minimum projection map: canonical project paths; shared intent/claim IDs or their currently missing status; page-source to claim/evidence IDs; output paths; projection status. If the research story is empty, record that and project the explicit user brief; do not create a second permanent story silently.

Read existing research-harness conventions before choosing file names or adding checks. This adapter is intentionally small: it does not install global rules, define a separate science workflow, require subagents, or claim that source freshness proves scientific validity.

For a tested end-to-end example see the separately delivered slide-integration-20261106 study. Its source data are reported literature numbers; no models were trained. Unit tests cover state/revision behavior with mocked renderers; actual three-page rendering is a separate evidence item.
