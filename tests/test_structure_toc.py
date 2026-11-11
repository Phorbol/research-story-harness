import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from synthetic_fixtures import make_project
BASE=Path(__file__).resolve().parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


rh=module('rh_extended',BASE/'skills/research-harness/scripts/research.py')
sr=module('structure_renderer',BASE/'skills/ovito-structure/scripts/structure_render.py')
back=module('backends_extended',BASE/'skills/research-harness/scripts/scientific_backends.py')


class StructureAndTOCTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.cif=self.root/'mixed.cif'
        self.cif.write_text('''data_mixed
_cell_length_a 4
_cell_length_b 4
_cell_length_c 4
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
_space_group_name_H-M_alt 'P 1'
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_occupancy
Ta1 Ta 0 0 0 0.3333333333333333
Cr1 Cr 0 0 0 0.6666666666666666
O1 O 0.5 0.5 0.5 1
''')
        self.spec={'repeat':[1,1,1],'occupancy_mode':'weighted_color','bonds':{'mode':'none'}}

    def tearDown(self):self.temp.cleanup()

    def test_mixed_occupancy_preserves_minor_element(self):
        scene=sr.structure_scene(self.cif,self.spec)
        self.assertAlmostEqual(scene['weighted_composition']['Ta'],1/3)
        self.assertAlmostEqual(scene['weighted_composition']['Cr'],2/3)
        self.assertEqual(len(scene['particles']),2)
        self.assertIn('Ta',scene['particles'][0]['occupancy'])

    def test_replicas_keep_source_identity_and_translation(self):
        s=copy.deepcopy(self.spec);s['repeat']=[2,1,1]
        scene=sr.structure_scene(self.cif,s)
        self.assertEqual(len(scene['particles']),4)
        a,b=scene['particles'][0],scene['particles'][2]
        self.assertEqual(a['source_index'],b['source_index'])
        self.assertAlmostEqual(b['position'][0]-a['position'][0],4)
        self.assertEqual(b['occupancy'],a['occupancy'])

    def test_dominant_species_shortcut_is_rejected(self):
        self.spec['occupancy_mode']='dominant_only'
        with self.assertRaisesRegex(ValueError,'Mixed/partial'):sr.structure_scene(self.cif,self.spec)

    def test_required_sites_cannot_be_selected_away(self):
        self.spec.update(selection=[1],must_show_sites=[0])
        with self.assertRaisesRegex(ValueError,'required source site'):sr.structure_scene(self.cif,self.spec)

    def test_fractional_element_must_remain_in_selection(self):
        self.spec.update(selection=[1],must_show_elements=['Ta'])
        with self.assertRaisesRegex(ValueError,'required element'):sr.structure_scene(self.cif,self.spec)

    def test_periodic_neighbor_uses_lattice_shift(self):
        from ase import Atoms
        from ase.io import write
        atoms=Atoms('HH',positions=[[.1,0,0],[1.9,0,0]],cell=[2,4,4],pbc=True)
        xyz=self.root/'pbc.extxyz';write(xyz,atoms)
        spec={'repeat':[2,1,1],'bonds':{'mode':'cutoff','cutoff_angstrom':.3,'meaning':'distance neighbours'}}
        scene=sr.structure_scene(xyz,spec)
        self.assertTrue(scene['bonds'])
        self.assertTrue(all(abs(e['distance_angstrom']-.2)<1e-8 for e in scene['bonds']))
        self.assertTrue(any(any(e['periodic_shift']) for e in scene['bonds']))

    def test_changed_structure_invalidates_source_digest(self):
        old=sr.structure_scene(self.cif,self.spec)['source']['sha256']
        self.cif.write_text(self.cif.read_text().replace('_cell_length_a 4','_cell_length_a 4.1'))
        self.assertNotEqual(old,sr.structure_scene(self.cif,self.spec)['source']['sha256'])

    def test_display_preset_preserves_structure_and_legacy_radius(self):
        from ase.data import covalent_radii, atomic_numbers
        legacy=sr.structure_scene(self.cif,self.spec)
        styled=sr.structure_scene(self.cif,{**self.spec,'style_preset':'solid'})
        for key in ['source_sites','particles','bonds','weighted_composition','base_cell','pbc']:
            self.assertEqual(legacy[key],styled[key])
        old=sr.particle_styles(legacy)[1];new=sr.particle_styles(styled)[1]
        expected=(covalent_radii[atomic_numbers['Ta']]/3+2*covalent_radii[atomic_numbers['Cr']]/3)*.42
        self.assertAlmostEqual(old[0],expected)
        self.assertTrue(all(b>a for a,b in zip(old,new)))

    def test_display_override_preserves_fractional_site_and_explicit_choices(self):
        scene=sr.structure_scene(self.cif,{**self.spec,'style_preset':'solid','radius_scale':.65,
            'element_radii_angstrom':{'Ta':1.4,'Cr':1.0},'render_settings':{'shadows':True}})
        self.assertEqual(scene['spec']['radius_scale'],.65)
        self.assertTrue(scene['spec']['render_settings']['shadows'])
        self.assertAlmostEqual(sr.particle_styles(scene)[1][0],1.4/3+2/3)
        self.assertEqual(scene['particles'][0]['occupancy'],{'Ta':1/3,'Cr':2/3})

    def test_typography_detects_accidental_bold_and_font_mix(self):
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        profile=json.loads((BASE/'skills/research-harness/assets/style-profile.json').read_text())
        fig,ax=plt.subplots();label=ax.text(.5,.5,'Axis-consistent text')
        back.style_figure(fig,profile,8);fig.canvas.draw();back.style_figure(fig,profile,8)
        self.assertTrue(back.typography_audit(fig,profile,8,'F',lambda *a:None)['passed'])
        label.set_fontweight('bold')
        self.assertFalse(back.typography_audit(fig,profile,8,'F',lambda *a:None)['passed'])
        label.set_fontweight('normal');label.set_fontfamily('DejaVu Serif')
        self.assertFalse(back.typography_audit(fig,profile,8,'F',lambda *a:None)['passed'])
        label.set_fontfamily(profile["font_family"]);label.set_color("red")
        self.assertFalse(back.typography_audit(fig,profile,8,"F",lambda *a:None)["passed"])
        plt.close(fig)

    def test_unknown_font_is_not_silently_substituted(self):
        import matplotlib.pyplot as plt
        profile=json.loads((BASE/'skills/research-harness/assets/style-profile.json').read_text());profile['font_family']='NoSuchResearchFont_942'
        fig,ax=plt.subplots();ax.text(.5,.5,'Visible text');back.style_figure(fig,profile,8)
        with self.assertRaises(ValueError):back.typography_audit(fig,profile,8,'F',lambda *a:None)
        plt.close(fig)

    def test_toc_claim_and_asset_bindings_are_checked(self):
        project=make_project(self.root)
        project['figures'][-1]['mapping']['blocks'][0]['claim_ids']=['Unfounded']
        report=rh.validate(project,self.root)
        self.assertTrue(any(c['check']=='toc_claim_binding' and c['status']=='failed' for c in report['checks']))

    def test_raw_trace_blank_tails_are_explicit_and_unmatched_data_fail(self):
        project=make_project(self.root)
        project['figures'][3]['mapping'].pop('missing_policy')
        report=rh.validate(project,self.root)
        self.assertTrue(any(c['check']=='trace_completeness' and c['status']=='failed' for c in report['checks']))

    def test_xrd_derived_values_are_verified_against_raw_scan(self):
        project=make_project(self.root)
        report=rh.validate(project,self.root)
        self.assertTrue(any(c['check']=='analysis_reproduction' and c['status']=='passed' for c in report['checks']))


if __name__=='__main__':unittest.main()
