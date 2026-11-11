import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / 'skills/research-harness/scripts/research.py'
spec = importlib.util.spec_from_file_location('research', SCRIPT)
rh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rh)


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'project'
        rh.init_project(self.root, demo=True)
        self.path = self.root / 'research.json'
        self.project = rh.read_json(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def check(self, project=None, export=None):
        return rh.validate(project or self.project, self.root, export)

    def assertFailure(self, name, project=None, export=None):
        report = self.check(project, export)
        self.assertTrue(any(c['check'] == name and c['status'] == 'failed' for c in report['checks']), report)

    def test_demo_contract_is_valid_but_not_fully_verified(self):
        result = self.check()
        self.assertTrue(result['automated_checks_passed'])
        self.assertFalse(result['fully_verified'])
        self.assertEqual(result['counts']['unknown'], 6)
        self.assertTrue(any(c['check']=='story_choice' and c['status']=='unknown' for c in result['checks']))
        self.assertEqual(result['counts']['not_implemented'], 1)

    def test_blank_initializes_without_fake_scientific_content(self):
        blank = self.root.parent / 'blank'
        rh.init_project(blank)
        result = rh.validate(rh.read_json(blank/'research.json'), blank)
        self.assertFalse(result['automated_checks_passed'])
        self.assertTrue((blank/'AGENTS.md').is_file())

    def test_existing_project_is_not_overwritten(self):
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            rh.init_project(self.root)
        self.assertEqual(before, self.path.read_bytes())

    def test_duplicate_pair_identity_is_located(self):
        p = self.root/'data/paired.csv'
        p.write_text(p.read_text().replace('S02', 'S01'))
        self.assertFailure('csv_identity_and_values')

    def test_missing_pair_is_not_silently_dropped(self):
        p = self.root/'data/paired.csv'
        p.write_text(p.read_text().replace('S01,4.2,5.1', 'S01,4.2,'))
        self.assertFailure('paired_completeness')

    def test_missing_and_zero_remain_distinct(self):
        rows = rh.load_data(self.project['datasets'][1], self.root)
        self.assertIsNone(rows[2]['score'])
        self.assertEqual(rows[3]['score'], 0)

    def test_nonfinite_data_rejected(self):
        p=self.root/'data/paired.csv'
        p.write_text(p.read_text().replace('4.2', 'NaN'))
        self.assertFailure('csv_identity_and_values')

    def test_incompatible_pair_units_rejected(self):
        self.project['datasets'][0]['units']['after']='eV'
        self.assertFailure('paired_units')

    def test_reference_is_required(self):
        self.project['datasets'][2]['reference']=''
        self.assertFailure('energy_reference')

    def test_ts_connected_to_wrong_state_is_located(self):
        self.project['relations'][0]['to']='P'
        self.assertFailure('energy_edge_alignment')
        self.assertFailure('energy_edge_coverage')

    def test_repeated_edge_cannot_hide_missing_path(self):
        self.project['figures'][2]['relation_ids']=['E1','E1','E3']
        self.assertFailure('references:relations')
        self.assertFailure('energy_edge_coverage')

    def test_clipping_observations_is_interpretive_failure(self):
        self.project['figures'][0]['visual']['y_limits']=[4,5]
        self.assertFailure('visible_values')

    def test_parallel_to_serial_change_matches_external_topology(self):
        self.project['relations'][4]['from']='branchA'
        self.assertFailure('method_source_topology')

    def test_unknown_relations_are_rejected(self):
        self.project['relations'][0]['type']='arrow'
        self.assertFailure('relation_type')

    def test_broken_claim_reference_is_located(self):
        self.project['figures'][0]['claim_ids']=['Missing']
        self.assertFailure('references:claims')

    def test_unknown_scientific_claim_does_not_gain_evidence(self):
        self.project['claims'][0]['evidence_ids']=[]
        self.assertFailure('supported_claim_evidence')

    def test_synthetic_cannot_be_silently_relabelled_real(self):
        self.project['project']['synthetic']=False
        self.assertFailure('synthetic_label')

    def test_unimplemented_domain_is_not_passed(self):
        self.project['figures'][0]['kind']='atomic3d'
        report=self.check()
        self.assertTrue(any(c['check']=='renderer' and c['status']=='not_implemented' for c in report['checks']))
        with self.assertRaises(ValueError):
            rh.render(self.project,self.root,self.root/'build')

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            rh.resolve(self.root,'../../private.txt')

    def test_mislabeled_revision_does_not_write(self):
        before=self.path.read_bytes()
        op={'type':'presentation','allowed_change':['/figures/0/mapping/before'],
            'changes':[{'path':'/figures/0/mapping/before','value':'after'}]}
        with self.assertRaises(ValueError): rh.revise(self.path,op)
        self.assertEqual(before,self.path.read_bytes())
        self.assertFalse((self.root/'.research-history').exists())

    def test_accepted_requirement_survives_later_revisions(self):
        path='/figures/0/visual/font_size'
        rh.revise(self.path,{'type':'presentation','allowed_change':[path],
            'changes':[{'path':path,'value':10}],'must_preserve':['/datasets']})
        rh.revise(self.path,{'type':'interpretive','allowed_change':['/figures/0/visual/title'],
            'changes':[{'path':'/figures/0/visual/title','value':'Accepted label'}],'must_preserve':[path]})
        before=self.path.read_bytes()
        with self.assertRaises(ValueError):
            rh.revise(self.path,{'type':'presentation','allowed_change':[path],
                'changes':[{'path':path,'value':11}]})
        self.assertEqual(before,self.path.read_bytes())

    def test_five_revisions_for_each_of_four_figures(self):
        original=copy.deepcopy(self.project)
        for index in range(4):
            changes=[('interpretive','title','Accepted '+original['figures'][index]['id']),
                     ('presentation','font_size',10),('interpretive','width_mm',150),
                     ('interpretive','colors',['#009E73','#CC79A7']),('interpretive','height_mm',100)]
            for turn in range(5):
                category,field,value=changes[turn]
                path='/figures/%d/visual/%s'%(index,field)
                op={'type':category,'reason':'Synthetic edit %d'%(turn+1),'allowed_change':[path],
                    'changes':[{'path':path,'value':value}],
                    'must_preserve':['/datasets','/entities','/relations','/claims', '/figures/%d/mapping'%index,
                                     '/figures/%d/caption'%index]}
                if turn>0: op['must_preserve'].append('/figures/%d/visual/title'%index)
                if turn>1: op['must_preserve'].append('/figures/%d/visual/font_size'%index)
                report=rh.revise(self.path,op)
                self.assertTrue(report['automated_checks_passed'])
                current=rh.read_json(self.path)
                for key in ['datasets','entities','relations','claims']:
                    self.assertEqual(original[key],current[key])
                rendered=rh.render(current,self.root,self.root/'rounds'/str(current['revision']))
                self.assertTrue(rendered['automated_checks_passed'])
        current=rh.read_json(self.path)
        self.assertEqual(current['revision'],20)
        self.assertEqual(len(list((self.root/'.research-history').glob('*.json'))),20)

    def test_data_replacement_retains_identity_and_old_file(self):
        new=self.root/'data/paired-v2.csv'
        new.write_text((self.root/'data/paired.csv').read_text().replace('4.2','4.3'))
        rh.revise(self.path,{'type':'data','allowed_change':['/datasets/0/path'],
            'changes':[{'path':'/datasets/0/path','value':'data/paired-v2.csv'}],
            'must_preserve':['/figures/0/mapping','/entities','/figures/0/visual']})
        self.assertTrue((self.root/'data/paired.csv').is_file())
        self.assertEqual(rh.read_json(self.path)['datasets'][0]['path'],'data/paired-v2.csv')

    def test_manuscript_map_has_both_figure_and_section_links(self):
        text=rh.argument_map(self.project)
        self.assertIn('Fpaired',text)
        self.assertIn('Results',text)
        self.assertIn('Dpaired',text)

    def test_nonindependent_reader_record_remains_unknown_and_stales(self):
        path=self.root/'reviews/reader.md';path.parent.mkdir();path.write_text('Actual self-review notes')
        review={'category':'reader','status':'passed','independent':False,'reviewer':'test tool',
                'record_path':'reviews/reader.md','record_digest':rh.digest(path.read_bytes()),
                'signature':rh.signature(self.project,self.root)}
        self.project['reviews']=[review]
        self.assertEqual(next(c['status'] for c in self.check()['checks'] if c['check']=='manual:reader'),'unknown')
        review['independent']=True
        self.assertEqual(next(c['status'] for c in self.check()['checks'] if c['check']=='manual:reader'),'passed')
        path.write_text('Changed assessment')
        self.assertEqual(next(c['status'] for c in self.check()['checks'] if c['check']=='manual:reader'),'unknown')

    def test_source_change_stales_review(self):
        path=self.root/'review.md';path.write_text('Scientific review fixture')
        self.project['reviews']=[{'category':'scientific','status':'passed','signature':rh.signature(self.project,self.root),
                                 'record_path':'review.md','record_digest':rh.digest(path.read_bytes())}]
        source=self.root/'data/paired.csv';source.write_text(source.read_text().replace('4.2','4.3'))
        self.assertEqual(next(c['status'] for c in self.check()['checks'] if c['check']=='manual:scientific'),'unknown')

    def test_recorded_manual_failure_is_separate_from_automatic_checks(self):
        path=self.root/'review.md';path.write_text('Reader could not interpret the direction')
        self.project['reviews']=[{'category':'layout','status':'failed','signature':rh.signature(self.project,self.root),
                                 'record_path':'review.md','record_digest':rh.digest(path.read_bytes())}]
        report=self.check()
        self.assertTrue(report['automated_checks_passed'])
        self.assertFalse(report['checks_passed'])
        self.assertFalse(report['fully_verified'])

    def test_installer_does_not_overwrite_existing_skills(self):
        install_spec=importlib.util.spec_from_file_location('installer',BASE/'install_skills.py')
        installer=importlib.util.module_from_spec(install_spec)
        install_spec.loader.exec_module(installer)
        destination=self.root.parent/'installed'
        installer.install(destination)
        existing=destination/'academic-writing/SKILL.md'
        existing.write_text('User customization')
        with self.assertRaises(FileExistsError): installer.install(destination)
        self.assertEqual(existing.read_text(),'User customization')

    def test_strict_cli_distinguishes_unknown_from_failure(self):
        normal=subprocess.run([sys.executable,str(SCRIPT),'check',str(self.path)],capture_output=True)
        strict=subprocess.run([sys.executable,str(SCRIPT),'check',str(self.path),'--strict'],capture_output=True)
        self.assertEqual(normal.returncode,0)
        self.assertEqual(strict.returncode,1)

    def test_all_exports_bound_and_tampering_is_detected(self):
        out=self.root/'build'
        report=rh.render(self.project,self.root,out)
        self.assertTrue(report['automated_checks_passed'],report)
        manifest=rh.read_json(out/'manifest.json')
        self.assertEqual(len(manifest['figures']),4)
        for fid,figure in manifest['figures'].items():
            self.assertTrue(figure['object_ids'])
            for ext in ['svg','pdf','png']:
                self.assertGreater((out/(fid+'.'+ext)).stat().st_size,100)
        # Missing and zero remain visible in the actual exported vector text.
        svg=(out/'Ftable.svg').read_text()
        self.assertIn('>NA<',svg)
        self.assertIn('>0.00<',svg)
        path=out/'Fpaired.svg';path.write_text(path.read_text().replace('</svg>','<!--external edit--></svg>'))
        self.assertFailure('export_integrity',export=out)
        source=self.root/'data/paired.csv';source.write_text(source.read_text().replace('4.2','4.3'))
        self.assertFailure('export_inputs',export=out)


if __name__=='__main__':
    unittest.main()
