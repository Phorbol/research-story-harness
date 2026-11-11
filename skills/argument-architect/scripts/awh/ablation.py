"""Descriptive paired factorial summary of externally supplied blind ratings."""
import statistics

from .contracts import ContractError

class ExperimentError(ContractError): pass

def summarize(cells, reviews):
    if not cells or len(reviews)<2: raise ExperimentError('Need cells and at least two reviewer records')
    for field in ('model','budget'):
        if any(not isinstance(c[field],str) or not c[field].strip() for c in cells) or len({c[field] for c in cells})!=1:
            raise ExperimentError('Mismatched '+field+' or empty configuration')
    ids={};papers={}
    for c in cells:
        if any(not isinstance(c[f],str) or not c[f].strip() for f in ('draft_id','paper_id','material_sha256')):
            raise ExperimentError('Empty cell identity or material binding')
        k=c['draft_id'];p=c['paper_id'];arm=(c['argument_plan'],c['retrieved_example'])
        if any(type(x) is not int or x not in (0,1) for x in arm):raise ExperimentError('Factors must be 0/1 integers')
        if k in ids or arm in papers.setdefault(p,{}):raise ExperimentError('Duplicate draft or paper cell')
        ids[k]=c;papers[p][arm]=c
    for p,arms in papers.items():
        if set(arms)!={(0,0),(0,1),(1,0),(1,1)}:raise ExperimentError('Incomplete 2x2: '+p)
        for field in ('material_sha256','model','budget'):
            if len({c[field] for c in arms.values()})!=1:raise ExperimentError('Mismatched '+field+': '+p)
    byreview={}
    for r in reviews:
        rid=r['reviewer_id']
        if rid in byreview:raise ExperimentError('Duplicate reviewer')
        ratings={}
        for v in r['ratings']:
            k=v['draft_id']
            if k in ratings or k not in ids:raise ExperimentError('Duplicate or unknown rating')
            for f in ('contribution_score','qualification_score'):
                if type(v[f]) is not int or not 0<=v[f]<=4:raise ExperimentError('Score outside integer 0..4')
            issues=v['scientific_issues'];seen=set()
            for issue in issues:
                key=issue['error_key']
                if not key or key in seen:raise ExperimentError('Repeated distinct-error key within a draft')
                seen.add(key)
                if issue['severity'] not in ('minor','major','critical'):raise ExperimentError('Unknown severity')
                if any(not isinstance(issue[f],str) or not issue[f].strip() for f in ('draft_quote','source_locator','reason')):raise ExperimentError('Missing issue evidence')
            serious=sum(i['severity'] in ('major','critical') for i in issues)
            ratings[k]={'serious_error_incidence':int(serious>0),'serious_error_count':serious,'all_error_count':len(issues),'contribution_score':v['contribution_score'],'qualification_score':v['qualification_score']}
        if set(ratings)!=set(ids):raise ExperimentError('Reviewer did not cover all drafts')
        byreview[rid]=ratings
    metrics=list(next(iter(byreview.values()))[next(iter(ids))])
    averaged={k:{m:statistics.mean(r[k][m] for r in byreview.values()) for m in metrics} for k in ids}
    perpaper=[]
    for p,arms in papers.items():
        vals={str(a)+str(e):averaged[c['draft_id']] for (a,e),c in arms.items()}
        contrasts={}
        for m in metrics:
            v={k:x[m] for k,x in vals.items()}
            contrasts[m]={'plan':(v['10']+v['11']-v['00']-v['01'])/2,'example':(v['01']+v['11']-v['00']-v['10'])/2,'interaction':v['11']-v['10']-v['01']+v['00']}
        perpaper.append({'paper_id':p,'cells':vals,'contrasts':contrasts})
    diagnostics={'no_scientific_issues_detected':all(v['all_error_count']==0 for r in byreview.values() for v in r.values()),
        'qualification_all_at_scale_max':all(v['qualification_score']==4 for r in byreview.values() for v in r.values()),
        'reviewer_disagreement_drafts':{m:sum(len({r[k][m] for r in byreview.values()})>1 for k in ids) for m in metrics},
        'configuration_check_scope':'Declared material/model/budget fields only; no execution telemetry, access isolation or reviewer-independence proof.'}
    return {'diagnostics':diagnostics,'independent_papers':len(papers),'reviewers':list(byreview),'drafts':len(cells),'per_paper':perpaper,
        'arm_means':{a:{m:statistics.mean(x['cells'][a][m] for x in perpaper) for m in metrics} for a in ('00','01','10','11')},
        'mean_contrasts':{m:{f:statistics.mean(x['contrasts'][m][f] for x in perpaper) for f in ('plan','example','interaction')} for m in metrics},
        'reviewer_metrics':byreview,'interpretation':'Descriptive supplied ratings; paper is the independent unit. No significance, automatic semantic validity, or general benefit claim.'}
