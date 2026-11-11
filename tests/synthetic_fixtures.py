"""Small, explicitly synthetic sources for portable runtime regression tests.

No paper text, workbook, user coordinates, or extracted publisher assets are used.
"""
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def write_json(root, name, value):
    (root / name).write_text(json.dumps(value, indent=2) + '\n')


def scene_fixture():
    return {'schema_version': 1, 'canvas': [100, 80], 'track': 'explanatory',
            'geometry_basis': 'conceptual', 'scope_note': 'Synthetic software fixture only',
            'provenance': {'locator': 'Algorithmically authored test objects'},
            'objects': [{'id': f's{i}', 'semantic_id': f'item{i}', 'type': 'sphere',
                         'box': [5 + (i % 10) * 9, 10 + (i // 10) * 8, 3, 3],
                         'color': '#507a8b'} for i in range(62)] +
                       [{'id': 'label', 'semantic_id': 'label', 'type': 'text',
                         'xy': [5, 70], 'text': 'Synthetic objects'}],
            'connections': [{'id': 'comparison', 'from': 's0', 'to': 's1',
                             'meaning': 'comparison', 'basis': 'conceptual'}]}


def figure(fid, kind, mapping, dataset_id=None):
    result = {'id': fid, 'kind': kind, 'claim_ids': [], 'entity_ids': [], 'relation_ids': [],
              'reader_question': 'Does the software preserve the declared input?',
              'reader_task': 'Inspect test objects and values', 'evidence_role': 'Software fixture only',
              'cannot_infer': ['Scientific accuracy'], 'invariants': ['Object and input identity'],
              'caption': 'Synthetic software regression fixture; no scientific result.',
              'representation': 'schematic' if kind in {'schematic', 'toc'} else 'quantitative',
              'mapping': mapping, 'visual': {'width_mm': 140, 'height_mm': 100, 'font_size': 8}}
    if dataset_id:
        result['dataset_id'] = dataset_id
    return result


def make_project(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    write_json(root, 'scene.json', scene_fixture())
    (root / 'source.txt').write_text('Synthetic observation: compare two arbitrary fixture conditions.\n')
    (root / 'summary.csv').write_text('id,value,sd\nA,1.2,0.1\nB,2.4,0.2\n')
    (root / 'cells.csv').write_text('id,value\n' + ''.join(f'R{i},{i + 1}\n' for i in range(40)))
    (root / 'trace.csv').write_text('id,x,y\nA,0,1\nB,1,2\nTail,,\n')
    (root / 'scan.txt').write_text('10 0.5 11\n2\n5\n3\n')
    (root / 'scan.csv').write_text('id,angle,intensity\nA,10,2\nB,10.5,5\nC,11,3\n')
    (root / 'recipe.py').write_text(
        "def render_figure(spec, project, root, fig, ax, bind, load_data):\n"
        "    rows = load_data(next(d for d in project['datasets'] if d['id'] == spec['dataset_id']), root)\n"
        "    ax.set(xlim=(0,10), ylim=(0,5)); ax.set_axis_off()\n"
        "    for i, row in enumerate(rows):\n"
        "        bind(ax.text(i % 10 + .2, i // 10 + .3, str(int(row['value']))), spec['id'] + ':cell:' + row['id'] + ':value')\n")
    for name in ['style-profile.json', 'journal-profile.json']:
        shutil.copy2(BASE / 'skills/research-harness/assets' / name, root / name)
    source_paths = {'Scene': 'scene.json', 'SummarySource': 'summary.csv', 'CellSource': 'cells.csv',
                    'TraceSource': 'trace.csv', 'RawScan': 'scan.txt', 'ScanCSV': 'scan.csv',
                    'RecipeSource': 'recipe.py'}
    def dataset(did, sid, path, cols, units):
        return {'id': did, 'source_id': sid, 'path': path, 'row_key': 'id', 'columns': {'id': 'string', **cols},
                'units': units, 'conditions': 'Synthetic software fixture', 'uncertainty': 'Not scientific measurements'}
    datasets = [dataset('Summary', 'SummarySource', 'summary.csv', {'value': 'number', 'sd': 'number'}, {'value': 'a.u.', 'sd': 'a.u.'}),
                dataset('Cells', 'CellSource', 'cells.csv', {'value': 'number'}, {'value': 'dimensionless'}),
                dataset('Trace', 'TraceSource', 'trace.csv', {'x': 'number', 'y': 'number'}, {'x': 'a.u.', 'y': 'a.u.'}),
                dataset('Scan', 'ScanCSV', 'scan.csv', {'angle': 'number', 'intensity': 'number'}, {'angle': 'degree', 'intensity': 'a.u.'})]
    datasets[-1]['transforms'] = [{'operation': 'xrd_uniform_grid', 'input_source_id': 'RawScan',
                                  'x_column': 'angle', 'y_column': 'intensity'}]
    project = {'schema_version': 1, 'project': {'title': 'Synthetic regression', 'question': 'Preserve declared inputs?', 'synthetic': True},
               'sources': [{'id': sid, 'path': path, 'kind': 'synthetic', 'verified': True} for sid, path in source_paths.items()],
               'datasets': datasets, 'entities': [], 'relations': [], 'sections': [],
               'claims': [{'id': 'CTest', 'text': 'Fixture condition A differs from B', 'status': 'hypothesis',
                           'scope': 'Synthetic software fixture', 'limitations': ['Not scientific evidence'], 'evidence_ids': []}],
               'style_profile': 'style-profile.json', 'journal_profile': 'journal-profile.json',
               'figures': [figure('Objects', 'schematic', {'scene_source_id': 'Scene'}),
                           figure('SummaryFigure', 'summary', {'value': 'value', 'error': 'sd', 'label': 'id'}, 'Summary'),
                           figure('CellsFigure', 'recipe', {'recipe_source_id': 'RecipeSource'}, 'Cells'),
                           figure('TraceFigure', 'series', {'series': [{'id': 'T', 'x': 'x', 'y': 'y'}], 'missing_policy': 'omit_blank_xy_pairs'}, 'Trace'),
                           figure('LegacyTOC', 'toc', {'layout': 'linear', 'blocks': [{'id': f'B{i}', 'title': f'Step {i}', 'body': 'Fixture', 'claim_ids': ['CTest']} for i in range(4)], 'boundary': 'Legacy template test only'})]}
    write_json(root, 'research.json', project)
    return project


def make_story(root, project):
    root = Path(root)
    plan = {'mode': 'explore', 'brief': {'own_results_status': 'not_provided'}, 'selection': None, 'decisions': [],
            'papers': [{'id': 'Paper', 'path': 'source.txt', 'locator': 'Synthetic source, line 1',
                        'access_scope': 'Complete authored fixture',
                        'snapshot_sha256': hashlib.sha256((root / 'source.txt').read_bytes()).hexdigest()}],
            'observations': [{'id': oid, 'paper_id': 'Paper', 'locator': 'Line 1', 'statement': 'Synthetic comparison',
                              'basis': 'source_observation', 'use': 'literature_synthesis'} for oid in ['OPrimary', 'OSecondary']],
            'panels': [{'id': pid, 'observation_ids': [oid], 'track': 'explanatory', 'state': 'reference_only',
                        'reader_question': 'What changes?', 'reader_action': 'Compare objects',
                        'encoding_rationale': 'Keep identities visible', 'cannot_infer': ['Own scientific results'],
                        'claim_scope': 'literature_synthesis', 'figure_id': 'CellsFigure'}
                       for pid, oid in [('PPrimary', 'OPrimary'), ('PSecondary', 'OSecondary')]],
            'candidates': [{'id': cid, 'proposed_by': 'assistant', 'reader_before': 'An open question',
                            'reader_after': 'A bounded comparison', 'central_question': 'What differs?',
                            'why_this_order': 'Compare before interpreting', 'gaps': ['No own results'],
                            'discussion_question': 'Which comparison matters?',
                            'steps': [{'panel_ids': [pid], 'observation_ids': [oid], 'reader_question': 'What differs?', 'paragraph_job': 'Explain scope'}]}
                           for cid, pid, oid in [('CPrimary', 'PPrimary', 'OPrimary'), ('CSecondary', 'PSecondary', 'OSecondary')]]}
    write_json(root, 'story.json', plan)
    project['story_plan'] = 'story.json'
    return plan
