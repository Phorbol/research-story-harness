# Bind visual acceptance to the requested delivery

Use this optional contract for reference reconstruction or any task where local fixes
could otherwise replace the original outcome. Add a top-level `delivery_target` to
`research.json`. Keep the user's words, relevant references (copied inside the project),
and expression tasks plus quality comparison criteria. The task initiator saves this target before handing off production; the producer develops the story and implementation against it. Mark inferred reading tasks as coordinator interpretations, not verbatim user requirements. If production started first, retain that timing limitation rather than retrospectively calling the run pre-registered. Do not silently rewrite this
object after seeing a disappointing result; changes need actual user authorization.

```json
{
  "delivery_target": {
    "id": "qmmm-original",
    "user_request": "Preserve the QM/MM reference's scientific reading tasks and visual quality",
    "representation": "reference_reconstruction",
    "reference_paths": ["references/original.png"],
    "acceptance": {
      "boundary": "Reader can locate the QM/MM boundary and understand the interaction",
      "fidelity": "Compare the retained scientific detail, hierarchy and quality with the original at final size"
    }
  }
}
```

The coordinator can prepare an empty project before delegation with:

```bash
python3 <skill>/scripts/research.py init <project> --delivery-target <target.json>
```

`target.json` contains the target object itself (not the enclosing `delivery_target` key).
Its reference paths resolve relative to that JSON file. The initializer validates the
fields and reference availability before creating the project, copies those references
inside `references/`, and saves the target into the normal project schema. It creates
no review and gives no quality approval. Existing nonempty projects are not overwritten.
This avoids asking a figure producer to invent a separate project schema or use illegal
parent-relative reference paths. Use the existing project contract for subsequent data
and source registration; a bespoke renderer is not automatically a built-in recipe.

`representation` is `reference_reconstruction`, `redesign`, or `abstract_schematic`,
as appropriate to the actual request. A redesign is not inherently worse. This field
prevents accepting an explicitly different scope without changing the agreed target;
it imposes no universal layout. Acceptance descriptions specify what readers must
learn and the requested quality, rather than mandatory panels or decorative objects.

For `reader`, `layout`, and `publication` records, copy the entire current target into
`delivery_target`. Reader and layout passes remain specialist judgments, never overall
acceptance. Only the existing `publication` category is the final delivery gate here
(not a claim of journal approval); add an `issue_resolution` list and a separate
`overall_delivery` to that record:

```json
{
  "issue_resolution": [{"id": "small-label", "impact": "blocking", "state": "resolved", "observation": "Label readable in the revised PDF"}],
  "overall_delivery": {
    "status": "not_reviewed"
  }
}
```

This is not a passing review. To record a pass, an independent actual inspection must
supply `overall_delivery.status = "passed"`, the matching `representation`, and an
`acceptance` object with exactly the target's task IDs, each carrying `status: "met"`
and a concrete `observation`. The existing version 1 `visual_gate` remains required
for a target pass (artifacts, actual viewing context, four dimensions and issues).
Both issue lists use `impact: blocking/nonblocking` and `state: open/resolved`; an open blocker in either list prevents a pass, while open nonblocking issues are permitted. Closing all issues never generates this judgment. Do not manufacture observations
from successful rendering or valid JSON. Scientific review remains a separate category.

Missing reference assets or real coordinates justify top-level review `status` of
`partial` or `blocked`, with the same overall status and reasons/remaining needs in
the record. These map to `unknown` in check results, not pass. Do not invent coordinates
or silently substitute an abstract schematic to remove that blocker.

```bash
python3 scripts/research.py record-review research.json review-record.json
python3 scripts/research.py check research.json --out reports/check.json
```

Review metadata still needs the existing category, reviewer and project-relative
`record_path` pointing to actual review evidence. The record's signature covers the
target and reference file bytes: changing either makes old reviews stale. Projects
without a target retain legacy behavior; legacy records cannot pass a configured
publication target. The consistency guard rejects explicit contradictions, omitted tasks
and changed scope. It cannot tell whether testimony is honest, determine scientific
validity, or prove that an image is attractive. Human independent comparison remains
necessary, including when every automatic check passes.
