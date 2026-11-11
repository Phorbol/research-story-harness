"""Regression checks for physical geometry; these do not certify aesthetics."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rh=load('pub_geometry_rh',BASE/'skills/research-harness/scripts/research.py')
scene=load('pub_geometry_scene',BASE/'skills/research-harness/scripts/narrative_scene.py')
from synthetic_fixtures import make_project, write_json
class PublicationGeometryTests(unittest.TestCase):
 def test_exact_canvas_preserves_pdf_size_and_source_baseline(self):
  import fitz
  with tempfile.TemporaryDirectory() as d:
   case=Path(d);p=make_project(case);p['figures']=[p['figures'][0]];f=p['figures'][0]
   f['visual'].update(width_mm=247*25.4/72,height_mm=63*25.4/72,layout_mode='exact_canvas')
   write_json(case,'scene.json',{'canvas':[247,63],'track':'explanatory','geometry_basis':'conceptual','scope_note':'Synthetic baseline regression','provenance':{'locator':'Authored fixture'},'objects':[{'id':'label','semantic_id':'label','type':'text','text':'AB(g)','xy':[30,33],'va':'baseline'}]})
   result=rh.render(p,case,case/'build');self.assertTrue(result['automated_checks_passed'])
   with fitz.open(case/'build/Objects.pdf')as pdf:
    page=pdf[0];self.assertAlmostEqual(page.rect.width,247,places=3);self.assertAlmostEqual(page.rect.height,63,places=3)
    spans=[s for b in page.get_text('dict')['blocks']for line in b.get('lines',[])for s in line['spans']]
    actual=next(s for s in spans if s['text']=='AB(g)')
    self.assertAlmostEqual(actual['origin'][0],30,delta=.05);self.assertAlmostEqual(actual['origin'][1],30,delta=.05)
 def test_json_dash_and_rotated_baseline_anchor_render(self):
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  fig,ax=plt.subplots();s={'canvas':[100,100],'objects':[{'id':'d','semantic_id':'boundary','type':'line','points':[[0,5],[100,5]],'linestyle':[0,[4,3]],'lw':1},{'id':'t','semantic_id':'label','type':'text','text':'Sample','xy':[30,40],'va':'baseline','rotation':90,'rotation_mode':'anchor'}]}
  scene.draw_scene(s,BASE,ax,lambda a,i:a.set_gid(i),'F');fig.canvas.draw();self.assertEqual(ax.texts[0].get_rotation_mode(),'anchor');self.assertEqual(ax.texts[0].get_verticalalignment(),'baseline');self.assertEqual(ax.lines[0]._unscaled_dash_pattern,(0,(4,3)));plt.close(fig)
if __name__=='__main__':unittest.main()
