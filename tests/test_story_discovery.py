import copy,importlib.util,json,tempfile,unittest,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
story=mod('story_test',BASE/'skills/research-harness/scripts/story.py')
batch=mod('paper_batch_test',BASE/'skills/research-harness/scripts/paper_batch.py')
rh=mod('story_rh',BASE/'skills/research-harness/scripts/research.py')
from synthetic_fixtures import make_project, make_story
class StoryDiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.case=Path(self.temp.name);self.project=make_project(self.case);self.plan=make_story(self.case,self.project)
 def test_unclear_intent_can_start_without_story_or_chart(self):
  p=json.loads((BASE/'skills/research-harness/assets/story-blank.json').read_text())
  self.assertTrue(story.validate(p,self.case)['checks_passed']);self.assertIsNone(p['selection']);self.assertEqual(p['candidates'],[])
 def test_batch_indexes_caption_and_multiple_prose_references_without_claiming_understanding(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'paper.xml';p.write_text('<article><body><p>Compare<xref rid="f1 f2">both figures</xref>.</p><fig id="f1"><label>Fig1</label><caption><p>A conditional comparison</p></caption></fig></body></article>')
   r=batch.extract(p,{'id':'Paper','doi':'fixture','path':'paper.xml'});f=r['figures'][0];self.assertTrue(f['prose_references']);self.assertIsNone(f['reader_task']);self.assertEqual(f['review_status'],'text_extracted_not_interpreted')
 def test_source_grounded_alternatives_remain_open(self):
  r=story.validate(self.plan,self.case,self.project);self.assertTrue(r['checks_passed']);self.assertIsNone(r['selected_story'])
 def test_style_or_assistant_advice_cannot_select_scientific_story(self):
  for origin,scope in [('assistant','story'),('user','style')]:
   p=copy.deepcopy(self.plan);cid=p['candidates'][0]['id'];p['decisions']=[dict(id='D',origin=origin,scope=scope,action='choose_for_draft',candidate_id=cid,verbatim='test fixture only')];p['selection']=dict(candidate_id=cid,decision_id='D')
   self.assertFalse(story.validate(p,self.case)['checks_passed'])
 def test_explicit_choice_record_is_consistent_but_not_authenticated(self):
  p=self.plan;cid=p['candidates'][0]['id'];p['decisions']=[dict(id='D',origin='user',scope='story',action='choose_for_draft',candidate_id=cid,verbatim='fixture, not an actual human choice')];p['selection']=dict(candidate_id=cid,decision_id='D')
  r=story.validate(p,self.case);self.assertTrue(r['checks_passed']);self.assertIn('do not authenticate',r['guarantee'])
 def test_new_bound_preview_can_be_rendered_before_it_exists(self):
  self.plan['panels'][0]['preview']='build/not-rendered-yet.png'
  self.assertTrue(story.validate(self.plan,self.case,self.project)['checks_passed'])
  self.assertFalse(story.validate(self.plan,self.case)['checks_passed'])
 def test_missing_own_results_cannot_become_project_claim(self):
  self.plan['panels'][0]['claim_scope']='own_result';self.assertFalse(story.validate(self.plan,self.case)['checks_passed'])
 def test_changed_source_reopens_observations(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'s.txt').write_text('new evidence');p=copy.deepcopy(self.plan);p['papers']=p['papers'][:1];p['papers'][0]['path']='s.txt';p['observations']=[];p['panels']=[];p['candidates']=[]
   r=story.validate(p,root);self.assertFalse(r['checks_passed']);self.assertIn('source changed',' '.join(r['errors']))
 def test_evidence_change_reaches_dependent_figures_and_stories(self):
  r=story.affected(self.plan,'OPrimary');self.assertIn('PPrimary',r['panels']);self.assertTrue(r['candidates_to_reopen']);self.assertNotIn('PSecondary',r['panels'])
 def test_story_revision_invalidates_previously_rendered_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'story.json').write_text(json.dumps(self.plan));p=copy.deepcopy(self.project);p['sources']=[];p['datasets']=[];p['sections']=[];p.pop('style_profile');p.pop('journal_profile');before=rh.signature(p,root)
   self.plan['candidates'][0]['reader_after']='A changed reader judgment';(root/'story.json').write_text(json.dumps(self.plan));self.assertNotEqual(before,rh.signature(p,root))
 def test_recipe_export_preserves_values_objects_and_font_audit(self):
  p=self.project;p['figures']=[f for f in p['figures'] if f['id']=='CellsFigure'];p['sections']=[];p.pop('story_plan')
  with tempfile.TemporaryDirectory() as d:
   r=rh.render(p,self.case,d);self.assertTrue(r['checks_passed']);svg=(Path(d)/'CellsFigure.svg').read_text();self.assertEqual(svg.count('id="CellsFigure:cell:'),40)
   audit=json.loads((Path(d)/'typography.json').read_text());self.assertTrue(audit['passed']);self.assertTrue(any(c['check']=='recipe_semantics' and c['status']=='unknown' for c in r['checks']))
if __name__=='__main__':unittest.main()
