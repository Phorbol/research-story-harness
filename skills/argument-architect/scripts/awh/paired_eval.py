"""Descriptive version-paired analysis,not a semantic judge."""
import statistics
from .ablation import summarize,ExperimentError
EXTRA=('domain_register_score','terminology_consistency_score')
def analyze(cells,reviews,version_order):
 versions=list(version_order)
 if len(versions)!=len(set(versions)) or set(versions)!={x['version'] for x in cells}:raise ExperimentError('Explicit version order must cover distinct observed versions')
 allids={x['draft_id'] for x in cells}
 if len(allids)!=len(cells):raise ExperimentError('Duplicate draft identity across version cells')
 for review in reviews:
  observed=[x['draft_id'] for x in review['ratings']]
  if len(observed)!=len(set(observed)) or set(observed)!=allids:raise ExperimentError('Global review coverage mismatch')
 if len(versions)!=2:raise ExperimentError('Exactly two declared versions required')
 for v in versions:
  if not any(x['version']==v for x in cells):raise ExperimentError('Missing version')
 # Shared material and declared execution configuration for every matched paper/arm.
 pairs={}
 for c in cells:
  pair=(c['paper_id'],c['argument_plan'],c['retrieved_example']);group=pairs.setdefault(pair,{})
  if c['version'] in group:raise ExperimentError('Repeated version cell')
  group[c['version']]=c
 for pair,group in pairs.items():
  if set(group)!=set(versions):raise ExperimentError('Unpaired version cell')
  for f in ('material_sha256','model','budget'):
   if len({x[f] for x in group.values()})!=1:raise ExperimentError('Version mismatch: '+f)
 byversion={}
 for version in versions:
  subset=[x for x in cells if x['version']==version];ids={x['draft_id'] for x in subset}
  rv=[{**r,'ratings':[x for x in r['ratings'] if x['draft_id'] in ids]} for r in reviews]
  base=summarize(subset,rv)
  extras={}
  for c in subset:
   values=[x for r in rv for x in r['ratings'] if x['draft_id']==c['draft_id']]
   for x in values:
    for f in EXTRA:
     if type(x[f]) is not int or not 0<=x[f]<=4:raise ExperimentError('Extra score outside integer0..4')
    if not isinstance(x['unnecessary_defensive_clauses'],list):raise ExperimentError('Defensive clauses must be annotations')
   extras[c['draft_id']]={**{f:statistics.mean(x[f] for x in values) for f in EXTRA},'unnecessary_defensive_clause_count':statistics.mean(len(x['unnecessary_defensive_clauses']) for x in values)}
  for paper in base['per_paper']:
   p=paper['paper_id']
   for c in subset:
    if c['paper_id']==p:paper['cells'][str(c['argument_plan'])+str(c['retrieved_example'])].update(extras[c['draft_id']])
   for f in (*EXTRA,'unnecessary_defensive_clause_count'):
    v={arm:score[f] for arm,score in paper['cells'].items()};paper['contrasts'][f]={'plan':(v['10']+v['11']-v['00']-v['01'])/2,'example':(v['01']+v['11']-v['00']-v['10'])/2,'interaction':v['11']-v['10']-v['01']+v['00']}
  metrics=next(iter(base['per_paper'][0]['cells'].values())).keys()
  base['arm_means']={a:{m:statistics.mean(p['cells'][a][m] for p in base['per_paper']) for m in metrics} for a in ('00','01','10','11')}
  base['mean_contrasts']={m:{f:statistics.mean(p['contrasts'][m][f] for p in base['per_paper']) for f in ('plan','example','interaction')} for m in metrics}
  byversion[version]=base
 v0,v1=versions;papers=sorted({x['paper_id'] for x in cells});paired=[]
 for paper in papers:
  p0=next(x for x in byversion[v0]['per_paper'] if x['paper_id']==paper);p1=next(x for x in byversion[v1]['per_paper'] if x['paper_id']==paper)
  diffs={a:{m:p1['cells'][a][m]-p0['cells'][a][m] for m in metrics} for a in ('00','01','10','11')}
  paired.append({'paper_id':paper,'cell_deltas':diffs,'mean_version_delta':{m:statistics.mean(diffs[a][m] for a in diffs) for m in metrics}})
 return {'version_order':versions,'independent_papers':len(papers),'by_version':byversion,'paired_version_effects':paired,'mean_version_delta':{m:statistics.mean(x['mean_version_delta'][m] for x in paired) for m in metrics},'interpretation':'Descriptive paired supplied ratings. No natural-error accuracy,significance,fullharness quality or general improvement proof.'}
