"""Exercise recipe title ownership through actual SVG/PDF/PNG rendering.

The tiny dataset is a controlled software fixture, not scientific evidence.
Run with: python -m unittest discover -s tests -p 'test_recipe_titles.py' -v
Requires the renderer's Matplotlib environment plus PyMuPDF for PDF inspection.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import fitz


SKILL = Path(__file__).resolve().parents[1] / "skills/research-harness"
loader = importlib.util.spec_from_file_location("research", SKILL / "scripts/research.py")
research = importlib.util.module_from_spec(loader)
loader.loader.exec_module(research)


class RecipeTitleExportTests(unittest.TestCase):
    def render_text(self, *, synthetic=False, explicit_title=None, recipe_title=True):
        with tempfile.TemporaryDirectory(prefix="recipe-title-") as directory:
            root = Path(directory)
            (root / "data.csv").write_text("id,value\nFixture,1\n")
            (root / "recipe.py").write_text(
                "def render_figure(spec, project, root, fig, ax, bind, load_data):\n"
                "    rows = load_data(project['datasets'][0], root)\n"
                "    bind(ax.plot([0], [rows[0]['value']], 'o')[0], 'fixture-point')\n"
                "    fig.text(.1, .93, 'Recipe figure heading')\n"
                + ("    ax.set_title('Recipe axis heading', loc='left')\n" if recipe_title else "")
            )
            visual = {"width_mm": 120, "height_mm": 80, "font_size": 8}
            if explicit_title is not None:
                visual["title"] = explicit_title
            project = {
                "schema_version": 1,
                "project": {"question": "Does the recipe retain title ownership?", "synthetic": synthetic},
                "sources": [
                    {"id": "Data", "kind": "file", "path": "data.csv", "verified": True},
                    {"id": "Recipe", "kind": "file", "path": "recipe.py", "verified": True},
                ],
                "datasets": [{"id": "Dataset", "source_id": "Data", "path": "data.csv",
                              "row_key": "id", "columns": {"id": "string", "value": "number"},
                              "units": {"value": "dimensionless"}, "conditions": "Software fixture only",
                              "uncertainty": "Not applicable to this rendering fixture"}],
                "entities": [], "relations": [], "claims": [], "sections": [],
                "figures": [{"id": "InternalRecipeIdentifier", "kind": "recipe", "dataset_id": "Dataset",
                             "claim_ids": [], "entity_ids": [], "relation_ids": [],
                             "reader_question": "Which title is exported?", "reader_task": "Read titles",
                             "evidence_role": "Software regression fixture", "cannot_infer": ["Scientific accuracy"],
                             "invariants": ["Title text ownership"], "caption": "Controlled rendering fixture.",
                             "representation": "quantitative", "mapping": {"recipe_source_id": "Recipe"},
                             "visual": visual}],
            }
            report = research.render(project, root, root / "build")
            self.assertTrue(report["automated_checks_passed"], report)
            with fitz.open(root / "build/InternalRecipeIdentifier.pdf") as document:
                return " ".join(page.get_text() for page in document).replace("\n", " ")

    def test_recipe_heading_survives_without_visual_title(self):
        text = self.render_text()
        self.assertIn("Recipe figure heading", text)
        self.assertIn("Recipe axis heading", text)
        self.assertNotIn("InternalRecipeIdentifier", text)
        self.assertNotIn("SYNTHETIC DEMO", text)

    def test_explicit_visual_title_still_overrides_left_axis_title(self):
        text = self.render_text(explicit_title="Configured title")
        self.assertIn("Configured title", text)
        self.assertIn("Recipe figure heading", text)
        self.assertNotIn("Recipe axis heading", text)
        self.assertNotIn("InternalRecipeIdentifier", text)

    def test_synthetic_marker_preserves_recipe_axis_title(self):
        text = self.render_text(synthetic=True)
        self.assertIn("SYNTHETIC DEMO | Recipe axis heading", text)
        self.assertIn("Recipe figure heading", text)
        self.assertNotIn("InternalRecipeIdentifier", text)

    def test_synthetic_marker_preserves_explicit_title(self):
        text = self.render_text(synthetic=True, explicit_title="Configured title")
        self.assertIn("SYNTHETIC DEMO | Configured title", text)
        self.assertNotIn("InternalRecipeIdentifier", text)

    def test_synthetic_marker_without_recipe_axis_title_does_not_leak_id(self):
        text = self.render_text(synthetic=True, recipe_title=False)
        self.assertIn("SYNTHETIC DEMO", text)
        self.assertIn("Recipe figure heading", text)
        self.assertNotIn("InternalRecipeIdentifier", text)


if __name__ == "__main__":
    unittest.main()
