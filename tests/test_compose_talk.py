import importlib.util
import unittest
from pathlib import Path


path = Path(__file__).resolve().parents[1] / "skills/ansatz-slide/scripts/compose_talk.py"
spec = importlib.util.spec_from_file_location("compose_talk", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TalkProjectionTest(unittest.TestCase):
    def test_order_condition_and_source_survive_without_private_prose(self):
        source = {"pages": [{"id": "B", "title": "Comparison", "audience_question": "private plan", "notes_blocks": [
            {"kind": "definition", "spoken": "Define the observed quantity."},
            {"kind": "evidence", "spoken": "After selection, the reported fraction is 75(2)%.", "source": "PDF p.5 Fig.4e", "visible_text": "Selected sample", "source_excerpt": "private exact quote"},
            {"kind": "transition", "spoken": "What is lost by this selection?"}]},
            {"id": "A", "title": "Cost", "notes": "Existing notes unchanged."}]}
        out, normal, audit = module.compose(source)
        self.assertEqual([p['id'] for p in out['pages']], ['B', 'A'])
        self.assertEqual(out['pages'][0]['notes'], 'Define the observed quantity.\n\nAfter selection, the reported fraction is 75(2)%.\n\nWhat is lost by this selection?')
        self.assertNotIn('notes', source['pages'][0])
        self.assertNotIn('private', normal)
        self.assertIn('PDF p.5 Fig.4e', audit)
        self.assertIn('not verified', audit)
        self.assertEqual(out['pages'][1]['notes'], source['pages'][1]['notes'])

    def test_ambiguous_or_untraceable_inputs_rejected(self):
        for page in [
            {'notes': 'stale', 'notes_blocks': [{'spoken': 'new'}]},
            {'notes_blocks': [{'kind': 'evidence', 'spoken': 'result without locator'}]},
            {'notes_blocks': [{'spoken': ''}]},
        ]:
            with self.subTest(page=page), self.assertRaises(ValueError):
                module.compose({'pages': [page]})


if __name__ == '__main__':
    unittest.main()
