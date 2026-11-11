import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

p = Path(__file__).parents[1] / 'skills/research-harness/scripts/representations.py'
spec = importlib.util.spec_from_file_location('representations', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SharedStory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, value in {'research.json': '{"claims":[{"id":"C1"}]}', 'story.json': '{}',
                            'brief.txt': 'intent', 'figure.svg': '<svg/>', 'deck.pptx': 'deck'}.items():
            (self.root / name).write_text(value)
        self.mapping = self.root / 'map.json'
        self.mapping.write_text(json.dumps({'representations': [
            {'id': 'F', 'medium': 'figure', 'path': 'figure.svg', 'claim_ids': ['C1']},
            {'id': 'S', 'medium': 'slides', 'path': 'deck.pptx', 'claim_ids': ['C1']}]}))
        self.record = self.root / 'binding.json'
        m.capture(self.root, self.mapping, self.record)

    def test_story_change_invalidates_both_without_rewriting_artifacts(self):
        self.assertFalse(m.check(self.record)['needs_review'])
        (self.root / 'story.json').write_text('{"selection":"new"}')
        self.assertEqual([r['needs_review'] for r in m.check(self.record)['representations']], [True, True])
        self.assertEqual((self.root / 'figure.svg').read_text(), '<svg/>')
        self.assertEqual((self.root / 'deck.pptx').read_text(), 'deck')

    def test_artifact_change_only_invalidates_its_representation(self):
        (self.root / 'deck.pptx').write_text('revised')
        self.assertEqual([r['needs_review'] for r in m.check(self.record)['representations']], [False, True])

    def test_unknown_claim_rejected(self):
        value = json.loads(self.mapping.read_text())
        value['representations'][0]['claim_ids'] = ['invented']
        self.mapping.write_text(json.dumps(value))
        with self.assertRaises(ValueError):
            m.capture(self.root, self.mapping, self.record)
