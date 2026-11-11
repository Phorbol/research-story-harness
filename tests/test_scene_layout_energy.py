"""Behavioral tests for observed geometry/identity failures; no aesthetic scores."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SCRIPTS=BASE/'skills/research-harness/scripts'
def load(name):
    s=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
layout=load('scene_layout');scene=load('narrative_scene');energy=load('energy_network');rh=load('research')

def example():
    return dict(schema_version=2,canvas=[90,40],track='explanatory',geometry_basis='conceptual',scope_note='Synthetic controlled software fixture',provenance={'locator':'test fixture'},
        objects=[dict(id=i,type='rect',semantic_id=i) for i in ['A','B']]+[dict(id='label',type='text',semantic_id='A',text='A',anchor={'object':'A','port':'center'})],
        layout={'groups':[{'box':[5,10,80,20],'direction':'row','gap':10,'children':['A','B']}]},
        connections=[dict(id='transfer',**{'from':'A','to':'B'},meaning='data_flow',basis='conceptual',draw={'from_port':'east','to_port':'west'})])

class LayoutTests(unittest.TestCase):
    def test_moving_group_moves_labels_and_bound_arrow(self):
        s=example();old=layout.resolve(s);s['layout']['groups'][0]['box'][1]+=4;new=layout.resolve(s)
        for id,key in [('label','xy'),('connection-transfer','start'),('connection-transfer','end')]:
            a=next(o for o in old['objects'] if o['id']==id)[key];b=next(o for o in new['objects'] if o['id']==id)[key]
            self.assertEqual(b,[a[0],a[1]+4])
        self.assertNotIn('box',s['objects'][0])
    def test_previous_outside_arrow_probe_now_fails(self):
        case=BASE;s=example();s['connections'][0].pop('draw');s['objects'].append(dict(id='probe-arrow',type='arrow',semantic_id='transfer',start=[40,20],end=[50,20]))
        self.assertEqual(scene.check_scene(s,case),[])
        next(o for o in s['objects'] if o['type']=='arrow')['end']=[9999,9999]
        self.assertTrue(any('outside canvas' in x for x in scene.check_scene(s,case)))
    def test_missing_anchor_and_cycle_rejected(self):
        s=example();s['objects'][-1]['anchor']['object']='gone';self.assertTrue(scene.check_scene(s,BASE))
        s=example();s['objects'][-1]['anchor']['object']='label';self.assertTrue(any('Cyclic' in x for x in scene.check_scene(s,BASE)))
    def test_rendered_arrow_really_uses_resolved_ports(self):
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots();s=example();records=scene.draw_scene(s,BASE,ax,lambda a,i:a.set_gid(i),'Test');fig.canvas.draw()
        edge=next(r for r in records if r['connection']);self.assertEqual(edge['geometry']['start'],[40,20]);self.assertEqual(edge['geometry']['end'],[50,20])
        from matplotlib.patches import FancyArrowPatch
        a=next(p for p in ax.patches if isinstance(p,FancyArrowPatch));self.assertEqual(a._posA_posB,[[40,20],[50,20]])
        plt.close(fig)
    def test_title_and_color_changes_reopen_interpretation(self):
        self.assertEqual(rh.classify('/figures/0/visual/title'),'interpretive')
        self.assertEqual(rh.classify('/figures/0/visual/colors'),'interpretive')
        self.assertEqual(rh.classify('/figures/0/visual/font_size'),'presentation')
    def test_arrow_collision_ignores_closepoly_placeholder_but_detects_visible_crossing(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyArrowPatch
        fig,ax=plt.subplots(figsize=(183/25.4,78/25.4));ax.set_position([0,0,1,1]);ax.set(xlim=(0,183),ylim=(0,78));ax.set_axis_off()
        a=FancyArrowPatch((31,41.34),(37,41.34),arrowstyle='-|>',mutation_scale=8,shrinkA=0,shrinkB=0);a.set_gid('actual-arrow');ax.add_patch(a)
        ax.text(11,12,'Water activation',fontsize=7.6,va='center')
        self.assertEqual(scene.text_collisions(fig)['arrow_text_intersections'],[])
        ax.text(31,41.34,'Real crossing',fontsize=7.6,va='center')
        self.assertEqual([x['text'] for x in scene.text_collisions(fig)['arrow_text_intersections']],['Real crossing']);plt.close(fig)
    def test_init_copies_new_dependencies(self):
        with tempfile.TemporaryDirectory() as d:
            rh.init_project(Path(d)/'project')
            for name in ['scene_layout','energy_network','legacy_mattergen_toc']:
                self.assertTrue((Path(d)/'project/scripts'/(name+'.py')).is_file())
    def test_generic_toc_renders_supplied_scene_without_legacy_scientific_text(self):
        import matplotlib.pyplot as plt
        backend=load('scientific_backends')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=example();s['objects'][-1]['text']='User-defined research story'
            (root/'scene.json').write_text(json.dumps(s));spec=dict(id='NewTOC',kind='toc',mapping={'scene_source_id':'Scene'},visual={})
            fig,ax=plt.subplots();backend.render_advanced(spec,{'sources':[{'id':'Scene','path':'scene.json'}]},root,fig,ax,lambda a,i:a.set_gid(i),root,lambda *args:[])
            labels=[t.get_text() for t in ax.texts];self.assertEqual(labels,['User-defined research story'])
            self.assertTrue((root/'NewTOC.narrative-map.json').is_file());plt.close(fig)

class EnergyTests(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(id=s,energy=e,step=x,kind='intermediate') for s,e,x in [('A',0,0),('B',1,1),('C',2,1),('D',-.5,2)]]
        self.spec=dict(id='F',dataset_id='D',entity_ids=['A','B','C','D'],relation_ids=['AB','BD','AC','CD'],mapping={'value':'energy','x':'step','state_kind':'kind','paths':[{'id':'p','label':'p','states':['A','B','D']},{'id':'q','label':'q','states':['A','C','D']}]},visual={})
        self.ds=dict(id='D',row_key='id',columns={'energy':'number','step':'number'},reference='same reactant',energy_type='Gibbs energy',uncertainty='not reported')
        self.maps={'datasets':{'D':self.ds},'relations':{i:dict(type='transformation',**{'from':i[0],'to':i[1]}) for i in self.spec['relation_ids']}}
    def failures(self):
        failed=[];energy.validate(self.spec,{},self.maps,{'D':self.rows},lambda ok,name,*args:failed.append(name) if not ok else None,lambda *a:None);return failed
    def test_shared_state_two_paths(self):self.assertEqual(self.failures(),[])
    def test_wrong_branch_and_missing_reference_rejected(self):
        self.maps['relations']['AB']['to']='C';self.assertIn('path_topology',self.failures())
        self.ds.pop('reference');self.assertIn('path_reference',self.failures())
    def test_missing_energy_and_silent_omission_rejected(self):
        self.rows[1]['energy']=None;self.assertIn('path_values',self.failures())
        self.spec['mapping']['paths']=self.spec['mapping']['paths'][:1];self.assertIn('path_coverage',self.failures())
    def test_render_keeps_shared_value_once_without_inventing_ts(self):
        import matplotlib.pyplot as plt
        self.ds.update(units={'energy':'eV'});self.spec['visual']['font_size']=8
        with tempfile.TemporaryDirectory() as d:
            fig,ax=plt.subplots();ids=[];energy.render(self.spec,{'datasets':[self.ds]},BASE,fig,ax,lambda a,i:ids.append(i),d,lambda *a:self.rows)
            self.assertEqual(ids.count('F:state:A'),1);self.assertFalse(any(':ts:' in i for i in ids))
            output=json.loads((Path(d)/'F.data-map.json').read_text());self.assertEqual(output['states'],self.rows);plt.close(fig)

if __name__=='__main__':unittest.main()
