"""The guard prevents contradictory acceptance, not bad taste or false testimony."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("research", Path(__file__).parents[1] / "scripts/research.py")
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class VisualReviewTests(unittest.TestCase):
    def test_acceptance_requires_consistent_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "actual.png").write_bytes(b"fixture: existence only, not image validation")
            ready = {"status": "passed", "visual_gate": {
                "version": 1, "artifact_paths": ["actual.png"],
                "viewing": {"inspected": True, "context": "80 x 40 mm PDF rendering"},
                "dimensions": {k: {"status": "ready", "observation": "Recorded concrete observation"}
                               for k in ("story", "hierarchy", "aesthetics", "legibility")}, "issues": []}}
            self.assertEqual(research.visual_review_consistency(ready, root), [])
            bad = copy.deepcopy(ready)
            bad["visual_gate"]["issues"] = [{"id": "small-core-label", "impact": "blocking", "state": "open"}]
            self.assertTrue(research.visual_review_consistency(bad, root))
            bad["status"] = "failed"
            self.assertEqual(research.visual_review_consistency(bad, root), [])
            for name in ready["visual_gate"]["dimensions"]:
                bad = copy.deepcopy(ready)
                bad["visual_gate"]["dimensions"][name]["status"] = "not_reviewed"
                self.assertTrue(research.visual_review_consistency(bad, root))
            bad = copy.deepcopy(ready)
            bad["visual_gate"]["viewing"]["inspected"] = False
            self.assertTrue(research.visual_review_consistency(bad, root))
            bad = copy.deepcopy(ready)
            bad["visual_gate"]["viewing"]["context"] = None
            self.assertTrue(research.visual_review_consistency(bad, root))
            bad = copy.deepcopy(ready)
            bad["visual_gate"]["dimensions"]["aesthetics"]["observation"] = None
            self.assertTrue(research.visual_review_consistency(bad, root))
            bad = copy.deepcopy(ready)
            bad["visual_gate"]["artifact_paths"] = ["missing.png"]
            self.assertTrue(research.visual_review_consistency(bad, root))
            self.assertEqual(research.visual_review_consistency({"status": "passed"}, root), [])


if __name__ == "__main__":
    unittest.main()
