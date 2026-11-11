"""Summarize supplied gold labels and externally adjudicated issue matches."""
from .contracts import ContractError

class CalibrationError(ContractError): pass

def summarize(gold,reviews,matches):
 bydraft={};goldids={}
 for d in gold:
  if d['draft_id'] in bydraft:raise CalibrationError('Duplicate gold draft')
  bydraft[d['draft_id']]=d
  for g in d['errors']:
   if g['gold_id'] in goldids:raise CalibrationError('Duplicate gold proposition')
   goldids[g['gold_id']]=d['draft_id']
 if not bydraft or not reviews:raise CalibrationError('Need gold and independent supplied reviews')
 predictions={};reviewids=set()
 for r in reviews:
  rid=r['reviewer_id']
  if rid in reviewids:raise CalibrationError('Duplicate reviewer')
  reviewids.add(rid);ratings=r['ratings']
  if len(ratings)!=len(bydraft) or {x['draft_id'] for x in ratings}!=set(bydraft):raise CalibrationError('Review coverage mismatch')
  for d in ratings:
   for i,issue in enumerate(d['scientific_issues']):
    if not all(isinstance(issue.get(f),str) and issue[f].strip() for f in ('draft_quote','reason','source_locator')):raise CalibrationError('Missing predicted issue evidence')
    predictions[(rid,d['draft_id'],i)]=issue
 assigned={};seen_gold=set()
 for m in matches:
  k=(m['reviewer_id'],m['draft_id'],m['issue_index']);g=m['gold_id'];pair=(m['reviewer_id'],g)
  if k not in predictions or g not in goldids or goldids[g]!=m['draft_id']:raise CalibrationError('Match refers to wrong draft,issue or gold')
  if k in assigned or pair in seen_gold:raise CalibrationError('Duplicate match;deduplicate propositions before scoring')
  assigned[k]=g;seen_gold.add(pair)
 out=[];controls={d for d,v in bydraft.items() if not v['errors']}
 for rid in reviewids:
  p={k for k in predictions if k[0]==rid};tp=sum(k in assigned for k in p);fp=len(p)-tp;fn=len(goldids)-tp;falsecontrols={k[1] for k in p if k[1] in controls};tn=len(controls)-len(falsecontrols)
  out.append({'reviewer_id':rid,'tp':tp,'fp':fp,'fn':fn,'true_negative_control_drafts':tn,'false_positive_control_drafts':len(falsecontrols),'precision':tp/len(p) if p else None,'recall':tp/len(goldids) if goldids else None,'specificity':tn/len(controls) if controls else None})
 return {'gold_propositions':len(goldids),'control_drafts':len(controls),'reviewers':sorted(out,key=lambda x:x['reviewer_id']),'interpretation':'Supplied source-derived gold and externally adjudicated matches. No automatic entailment or natural-error validity. Zero denominators are unknown,null.'}
