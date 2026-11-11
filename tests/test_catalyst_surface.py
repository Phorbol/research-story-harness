"""Source identity and registration regressions for the reviewed catalyst backend."""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

engine=module('surface_engine_test',BASE/'skills/ovito-structure/scripts/surface_render.py')
adapter=module('surface_adapter_test',BASE/'skills/research-harness/scripts/surface_backend.py')

class CatalystSourceTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        shutil.copytree(BASE/'skills/ovito-structure/assets/synthetic-catalyst-example',self.root/'data')
        self.path=self.root/'data/job.json';self.job=json.loads(self.path.read_text())
    def tearDown(self): self.tmp.cleanup()
    def prepare(self):
        self.path.write_text(json.dumps(self.job))
        return engine.render_surface_job(self.path,project_root=self.root,verify_only=True,write_outputs=False)
    def test_read_only_shared_camera_and_single_copy_adsorbate(self):
        before={p.relative_to(self.root):p.read_bytes()for p in self.root.rglob('*')if p.is_file()}
        meta=self.prepare()
        after={p.relative_to(self.root):p.read_bytes()for p in self.root.rglob('*')if p.is_file()}
        # Our helper reserializes the job; preparation itself must write nothing.
        before.pop(Path('data/job.json'));after.pop(Path('data/job.json'));self.assertEqual(before,after)
        self.assertFalse((self.root/'data/renders').exists())
        self.assertTrue(meta['source_coordinates_unchanged'])
        self.assertEqual(meta['classification'],'source tags')
        for s in meta['states'].values():
            for atom in meta['adsorbate_indices']:self.assertEqual(s['display_source_indices'].count(atom),1)
            self.assertGreater(s['display_atoms'],len(meta['atom_symbols']))
            self.assertFalse(s['transparent_display_atoms'])
    def test_missing_identity_rejected_instead_of_element_guess(self):
        self.job['adsorbate_tag']=999
        with self.assertRaisesRegex(ValueError,'Provide adsorbate_indices'):self.prepare()
    def test_changed_cell_and_changed_tags_rejected(self):
        from ase.io import read,write
        target=self.root/'data'/self.job['states'][1]['path'];original=read(target)
        changed=original.copy();changed.cell[0,0]+=.05;write(target,changed)
        with self.assertRaisesRegex(ValueError,'same cell'):self.prepare()
        changed=original.copy();tags=changed.get_tags();tags[64]=0;changed.set_tags(tags);write(target,changed)
        with self.assertRaisesRegex(ValueError,'tags differ'):self.prepare()
    def test_substrate_focus_maps_to_actual_periodic_display_atom(self):
        # First focus anchors MIC unwrapping; substrate atom 0 is an additional focus.
        self.job['focus_atoms']=[64,65,66,0];meta=self.prepare()
        for s in meta['states'].values():
            index=s['source_to_focus_display']['0']
            self.assertEqual(s['display_source_indices'][index],0)
            self.assertEqual(len(s['display_lattice_images'][index]),3)
            self.assertEqual(len(s['atom_pixels']['0']),2)
    def test_unregistered_state_rejected_and_color_override_kept(self):
        project={'sources':[{'id':'Job','path':'data/job.json'}]}
        spec={'id':'S','mapping':{'job_source_id':'Job'}}
        with self.assertRaisesRegex(ValueError,'registered'):adapter.prepare(spec,project,self.root)
        for i,s in enumerate(self.job['states']):project['sources'].append({'id':str(i),'path':'data/'+s['path']})
        project['semantic_colors']={'element':{'Cu':'#00ff00','O':'#223344'}}
        meta,_=adapter.prepare(spec,project,self.root)
        self.assertEqual(meta['colors']['Cu'],self.job['style']['colors']['Cu'])
        self.assertAlmostEqual(meta['colors']['O'][0],0x22/255)

if __name__=='__main__':unittest.main()
