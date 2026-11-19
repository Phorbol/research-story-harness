"""The guard prevents contradictory acceptance, not bad taste or false testimony."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import sys
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

    def test_delivery_scope_cannot_be_replaced_by_local_issue_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference.png").write_bytes(b"reference fixture")
            (root / "actual.png").write_bytes(b"not even a real image: no quality inference")
            target = {"id": "qmmm", "user_request": "Retain the original QM/MM reading tasks and visual quality",
                      "representation": "reference_reconstruction", "reference_paths": ["reference.png"],
                      "acceptance": {"boundary": "Explain QM/MM boundary", "fidelity": "Compare richness and visual quality to original"}}
            review = {"category": "publication", "status": "passed", "delivery_target": copy.deepcopy(target),
                      "issue_resolution": [{"id": "tiny-label", "impact": "blocking", "state": "resolved"}],
                      "overall_delivery": {"status": "not_reviewed"}}
            self.assertTrue(research.visual_review_consistency(review, root, target))
            specialist = {"category": "layout", "status": "passed", "delivery_target": copy.deepcopy(target)}
            self.assertEqual(research.visual_review_consistency(specialist, root, target), [])
            review["overall_delivery"] = {"status": "passed", "representation": "abstract_schematic",
                "acceptance": {"boundary": {"status": "met", "observation": "Boundary visible"}}}
            self.assertTrue(research.visual_review_consistency(review, root, target))
            review["overall_delivery"]["representation"] = target["representation"]
            review["overall_delivery"]["acceptance"]["fidelity"] = {"status": "met", "observation": "Human assessment, not program proof"}
            review["visual_gate"] = {"version": 1, "artifact_paths": ["actual.png"],
                "viewing": {"inspected": True, "context": "Final size, alongside original"},
                "dimensions": {k: {"status": "ready", "observation": "Human judgment"}
                    for k in ("story", "hierarchy", "aesthetics", "legibility")}, "issues": []}
            # Consistent testimony is accepted even with non-image bytes: never a beauty proof.
            self.assertEqual(research.visual_review_consistency(review, root, target), [])
            review["issue_resolution"][0]["state"] = "open"
            self.assertTrue(any("open blocking issue" in e for e in research.visual_review_consistency(review, root, target)))
            review["issue_resolution"][0]["impact"] = "nonblocking"
            self.assertEqual(research.visual_review_consistency(review, root, target), [])
            review["issue_resolution"] = [{"state": "resolved"}]
            self.assertTrue(research.visual_review_consistency(review, root, target))
            review["issue_resolution"] = []
            self.assertTrue(research.visual_review_consistency({"status": "passed"}, root, target))
            project = {"delivery_target": target}
            signature = research.signature(project, root)
            target["acceptance"]["fidelity"] = "User explicitly revised the quality criterion"
            self.assertNotEqual(signature, research.signature(project, root))
            self.assertTrue(research.visual_review_consistency(review, root, target))
            signature = research.signature(project, root)
            (root / "reference.png").write_bytes(b"changed reference")
            self.assertNotEqual(signature, research.signature(project, root))
            (root / "reference.png").unlink()
            review.update(status="blocked", delivery_target=copy.deepcopy(target),
                          overall_delivery={"status": "blocked", "reason": "Missing reference and real coordinates"})
            self.assertEqual(research.visual_review_consistency(review, root, target), [])

    def test_record_review_cli_preserves_blocked_and_stales_on_target_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            research.init_project(root, demo=True)
            project_path = root / "research.json"
            project = research.read_json(project_path)
            target = {"id": "qmmm", "user_request": "Match reference quality", "representation": "reference_reconstruction",
                      "reference_paths": ["missing.png"], "acceptance": {"fidelity": "Compare to original"}}
            project["delivery_target"] = target
            research.write_json(project_path, project)
            (root / "review.txt").write_text("Blocked: required reference is missing")
            record = {"category": "publication", "status": "blocked", "reviewer": "external reviewer",
                      "record_path": "review.txt", "delivery_target": target,
                      "issue_resolution": [], "overall_delivery": {"status": "blocked"}}
            record_path = root / "review.json"
            research.write_json(record_path, record)
            result = subprocess.run([sys.executable, str(Path(research.__file__)), "record-review", str(project_path), str(record_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            project = research.read_json(project_path)
            checks = research.validate(project, root)["checks"]
            layout = next(c for c in checks if c["check"] == "manual:publication")
            self.assertEqual(layout["status"], "unknown")
            self.assertIn("Recorded assessment", layout["detail"])
            project["delivery_target"]["acceptance"]["fidelity"] = "Changed task"
            checks = research.validate(project, root)["checks"]
            self.assertIn("stale", next(c for c in checks if c["check"] == "manual:publication")["detail"])
            # A legacy pass cannot be rebound to the target merely by record-review.
            record.pop("delivery_target")
            record["status"] = "passed"
            research.write_json(record_path, record)
            result = subprocess.run([sys.executable, str(Path(research.__file__)), "record-review", str(project_path), str(record_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("current delivery_target", result.stderr)

    def test_invalid_reference_entry_reports_schema_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            research.init_project(root, demo=True)
            path = root / "research.json"
            project = research.read_json(path)
            project["delivery_target"] = {"id": "qmmm", "user_request": "Keep original quality",
                "representation": "reference_reconstruction", "reference_paths": [None],
                "acceptance": {"fidelity": "Compare to original"}}
            research.write_json(path, project)
            report = root / "check.json"
            result = subprocess.run([sys.executable, str(Path(research.__file__)), "check", str(path), "--out", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            checks = research.read_json(report)["checks"]
            target = next(c for c in checks if c["check"] == "delivery_target")
            self.assertEqual(target["status"], "failed")
            self.assertIn("reference_paths", target["detail"])
            self.assertNotIn("Traceback", result.stderr)


    def test_init_hands_off_target_and_reference_before_production(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference.png").write_bytes(b"reference bytes; not a visual test")
            target = {"id": "commission", "user_request": "Retain the original reader task and quality",
                      "representation": "redesign", "reference_paths": ["reference.png"],
                      "acceptance": {"quality": "Compare the whole artifact with the reference"}}
            research.write_json(root / "target.json", target)
            research.init_project(root / "project", delivery_target_path=root / "target.json")
            project = research.read_json(root / "project/research.json")
            delivered = project["delivery_target"]
            self.assertEqual(delivered["acceptance"], target["acceptance"])
            self.assertEqual(delivered["user_request"], target["user_request"])
            self.assertEqual((root / "project" / delivered["reference_paths"][0]).read_bytes(),
                             (root / "reference.png").read_bytes())
            self.assertEqual(project["reviews"], [])
            with self.assertRaises(ValueError):
                research.init_project(root / "project", delivery_target_path=root / "target.json")
            target["reference_paths"] = ["absent.png"]
            research.write_json(root / "missing.json", target)
            with self.assertRaisesRegex(ValueError, "reference missing"):
                research.init_project(root / "missing-project", delivery_target_path=root / "missing.json")
            self.assertFalse((root / "missing-project").exists())


if __name__ == "__main__":
    unittest.main()
