"""Check reusable component semantics and exported geometry, not aesthetic scores."""
import importlib.util,io,tempfile,unittest
import matplotlib
matplotlib.use('Agg')
from pathlib import Path
S=Path(__file__).resolve().parents[1]/'skills/research-harness/scripts'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=module('components',S/'publication_components.py')
class PublicationTests(unittest.TestCase):
 def setUp(self):
  import matplotlib.pyplot as plt
  self.plt=plt;self.fig,self.ax=plt.subplots(figsize=(183/25.4,100/25.4))
  self.states={'A':dict(energy=.2,step=1,kind='intermediate'),'B':dict(energy=1.1,step=2,kind='transition_state')}
  self.spec={'from':'A','to':'B','semantic':'activation','x':2.5,'label_xy':[1.5,1.2],'unit':'eV'}
 def tearDown(self):self.plt.close(self.fig)
 def test_physical_grid_respects_margins_gutters_and_row_order(self):
  axes,frames=c.panel_grid(self.fig,self.ax,rows=2,cols=2,margins_mm=[10,10,12,8],gap_mm=[7,9],row_weights=[2,1])
  self.assertAlmostEqual(frames[0][0],10);self.assertAlmostEqual(frames[1][0]-frames[0][0]-frames[0][2],7)
  self.assertAlmostEqual(frames[2][1],8);self.assertGreater(frames[0][1],frames[2][1])
  for ax,f in zip(axes,frames):self.assertAlmostEqual(ax.get_position().width*183,f[2])
  with self.assertRaises(ValueError):c.panel_grid(self.fig,self.ax,rows=2,cols=2,margins_mm=[100,100,10,10])
 def test_source_changes_update_difference_and_drawn_endpoints(self):
  r=c.energy_difference(self.ax,self.states,self.spec,edges={('A','B')});self.assertAlmostEqual(r['difference'],.9)
  self.states['B']['energy']=1.4;r=c.energy_difference(self.ax,self.states,self.spec,edges={('A','B')});self.assertAlmostEqual(r['difference'],1.2)
  self.assertEqual(self.ax.texts[-2].xy,(2.5,1.4))
 def test_activation_requires_reported_adjacent_ts(self):
  with self.assertRaises(ValueError):c.energy_difference(self.ax,self.states,self.spec,edges=set())
  self.states['B']['kind']='intermediate'
  with self.assertRaises(ValueError):c.energy_difference(self.ax,self.states,self.spec,edges={('A','B')})
 def test_desorption_preserves_state_difference_without_inventing_ts(self):
  self.spec['semantic']='desorption';self.states['B']['kind']='intermediate'
  r=c.energy_difference(self.ax,self.states,self.spec);self.assertEqual(r['semantic'],'desorption');self.assertEqual(len(self.ax.collections),0)
 def test_visible_annotation_ids_survive_svg_export(self):
  self.ax.set(xlim=(0,4),ylim=(0,2));r=c.energy_difference(self.ax,self.states,self.spec,edges={('A','B')},bind=lambda a,i:a.set_gid(i))
  out=io.StringIO();self.fig.savefig(out,format='svg')
  for id in r['artist_ids']:self.assertIn('id="'+id+'"',out.getvalue())
 def test_constructed_origin_survives_structure_ingestion(self):
  from ase import Atoms
  from ase.io import write
  renderer=module('structure',S.parents[1]/'ovito-structure/scripts/structure_render.py')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'model.extxyz';a=Atoms('Pd2',positions=[[0,0,0],[2.7,0,0]],cell=[8,8,8]);a.info.update(model_origin='constructed_illustration',not_relaxed=True,not_paper_coordinates=True);write(p,a)
   s=renderer.structure_scene(p,{'bonds':{'mode':'none'}});self.assertEqual(s['source']['model_origin'],'constructed_illustration');self.assertTrue(s['source']['not_paper_coordinates'])
if __name__=='__main__':unittest.main()
