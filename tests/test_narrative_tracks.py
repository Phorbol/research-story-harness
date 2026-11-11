import copy,csv,importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rh=mod('tracks_rh',BASE/'skills/research-harness/scripts/research.py')
scene=mod('tracks_scene',BASE/'skills/research-harness/scripts/narrative_scene.py')
back=mod('tracks_back',BASE/'skills/research-harness/scripts/scientific_backends.py')
from synthetic_fixtures import make_project, scene_fixture
class NarrativeTrackTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.case=Path(self.temp.name);self.p=make_project(self.case)
 def test_schematic_has_no_measured_dataset_requirement(self):
  p=self.p;p['figures']=[f for f in p['figures'] if f['kind']=='schematic'];p['datasets']=[];p['claims']=[c for c in p['claims'] if c['id'].startswith('CRef')];p['sections']=[]
  self.assertTrue(rh.validate(p,self.case)['checks_passed'])
 def test_missing_or_untyped_connection_is_rejected(self):
  p=scene_fixture();p['connections'][0]['to']='UnknownSpecies';self.assertTrue(scene.check_scene(p,self.case))
  p['connections'][0]['to']=p['connections'][0]['from'];p['connections'][0]['meaning']='unqualified_causality';self.assertTrue(scene.check_scene(p,self.case))
 def test_scene_image_cannot_escape_project(self):
  p=scene_fixture();p['objects'].append({'id':'outside','semantic_id':'image','type':'image','path':'../../outside.png','extent':[1,2,1,2]})
  self.assertTrue(any('escaping' in e for e in scene.check_scene(p,self.case)))
 def test_quantitative_uncertainty_must_be_defined(self):
  dsid=next(f['dataset_id'] for f in self.p['figures'] if f['id']=='SummaryFigure')
  next(d for d in self.p['datasets'] if d['id']==dsid).pop('uncertainty');r=rh.validate(self.p,self.case)
  self.assertTrue(any(c['check']=='summary_uncertainty' and c['status']=='failed' for c in r['checks']))
 def test_text_identity_semantic_color_and_missing_glyph(self):
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  profile=json.loads((BASE/'skills/research-harness/assets/style-profile.json').read_text());fig,ax=plt.subplots()
  t=ax.text(.5,.5,'Reaction');t.set_gid('F:species:label');t._research_color='#D00000';back.style_figure(fig,profile,8)
  r=back.typography_audit(fig,profile,8,'F',lambda *a:None);self.assertTrue(r['passed']);self.assertEqual(t.get_gid(),'F:species:label');self.assertEqual(t.get_color(),'#D00000')
  t.set_text(chr(0x10FFFF));r=back.typography_audit(fig,profile,8,'F',lambda *a:None);self.assertFalse(r['passed']);self.assertTrue(any(x['missing_glyphs'] for x in r['records']));plt.close(fig)
 def test_source_labels_and_separate_raster_objects_survive_export(self):
  p=self.p;p['figures']=[f for f in p['figures'] if f['id']=='Objects'];p['sections']=[]
  with tempfile.TemporaryDirectory() as d:
   report=rh.render(p,self.case,d);self.assertTrue(report['checks_passed'])
   checks=[c for c in report['checks'] if c['check']=='svg_object_binding'];self.assertTrue(checks);self.assertTrue(all(c['status']=='passed' for c in checks))
   binding=json.loads((Path(d)/'Objects.narrative-map.json').read_text());self.assertGreaterEqual(sum(o['type']=='sphere' for o in binding['objects']),62)
if __name__=='__main__':unittest.main()
