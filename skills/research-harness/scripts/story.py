#!/usr/bin/env python3
"""Review a source-grounded story discussion; the host agent supplies scientific interpretation."""
import argparse,copy,hashlib,html,json
from pathlib import Path


def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def local(root,name):
 p=(Path(root)/name).resolve()
 if not p.is_relative_to(Path(root).resolve()):raise ValueError('Story asset escapes project: '+name)
 return p

def validate(plan,root,project=None):
 errors=[];pending=[]
 def index(group):
  rows=plan.get(group,[]);ids=[x.get('id') for x in rows]
  if len(ids)!=len(set(ids)) or any(not i for i in ids):errors.append(group+': unique nonempty IDs required')
  return {x['id']:x for x in rows if x.get('id')}
 papers=index('papers');obs=index('observations');panels=index('panels');stories=index('candidates');decisions=index('decisions')
 if plan.get('mode') not in {'explore','draft'}:errors.append('mode must be explore or draft')
 if plan.get('brief',{}).get('own_results_status') not in {'not_provided','partial','provided'}:errors.append('Declare own-results availability')
 for p in papers.values():
  if not p.get('locator') or not p.get('access_scope'):errors.append(p['id']+': paper locator and actual access scope required')
  if p.get('path'):
   path=local(root,p['path'])
   if not path.is_file():errors.append(p['id']+': missing source snapshot')
   elif p.get('snapshot_sha256') and hashlib.sha256(path.read_bytes()).hexdigest()!=p['snapshot_sha256']:errors.append(p['id']+': source changed; reopen observations and dependent story')
 for o in obs.values():
  if o.get('paper_id') not in papers or not o.get('locator') or not o.get('statement'):errors.append(o['id']+': source observation needs paper, locator and statement')
  if o.get('basis') not in {'source_observation','source_interpretation','assistant_inference'}:errors.append(o['id']+': separate observations from interpretation')
  if o.get('use') not in {'scientific_evidence','visual_reference','literature_synthesis'}:errors.append(o['id']+': source use required')
 for p in panels.values():
  if any(i not in obs for i in p.get('observation_ids',[])):errors.append(p['id']+': unknown source observation')
  if p.get('track') not in {'explanatory','quantitative','mixed'}:errors.append(p['id']+': declare visual track')
  for key in ['reader_question','reader_action','encoding_rationale','cannot_infer']:
   if not p.get(key):errors.append(p['id']+': missing '+key)
  if p.get('state')=='ready' and p.get('track') in {'quantitative','mixed'}:
   if not p.get('data_source') or not p.get('uncertainty'):errors.append(p['id']+': ready evidence panel needs data source and uncertainty')
  if p.get('state')!='ready':pending.append(p['id']+': '+p.get('state','unplanned'))
  if p.get('preview') and not local(root,p['preview']).is_file():
   if project and p.get('figure_id') in {f['id'] for f in project.get('figures',[])}:pending.append(p['id']+': preview awaits rendering; export must be checked afterward')
   else:errors.append(p['id']+': missing preview')
  if p.get('claim_scope')=='own_result' and plan['brief']['own_results_status']=='not_provided':errors.append(p['id']+': literature figures cannot become absent own results')
 for c in stories.values():
  for k in ['reader_before','reader_after','central_question','why_this_order','gaps','discussion_question']:
   if k not in c:errors.append(c['id']+': missing '+k)
  if c.get('proposed_by') not in {'assistant','user'}:errors.append(c['id']+': proposal origin required')
  for step in c.get('steps',[]):
   if any(x not in panels for x in step.get('panel_ids',[])):errors.append(c['id']+': unknown panel')
   if any(x not in obs for x in step.get('observation_ids',[])):errors.append(c['id']+': unknown observation')
   if not step.get('reader_question') or not step.get('paragraph_job'):errors.append(c['id']+': steps link reader question and prose task')
  if c.get('status')=='selected' and not plan.get('selection'):errors.append(c['id']+': selection needs an actual author decision record')
 selection=plan.get('selection')
 if selection:
  c=stories.get(selection.get('candidate_id'));d=decisions.get(selection.get('decision_id'))
  if not c or not d or d.get('origin')!='user' or d.get('scope')!='story' or d.get('action')!='choose_for_draft' or d.get('candidate_id')!=selection.get('candidate_id') or not d.get('verbatim'):errors.append('Story selection must reference an explicit user story choice; style preference or assistant recommendation is not a choice')
 else:pending.append('Author story choice is open; keep alternatives, do not infer agreement from silence')
 if project:
  fs={f['id']:f for f in project.get('figures',[])}
  for p in panels.values():
   if p.get('figure_id') and p['figure_id'] not in fs:errors.append(p['id']+': project figure link missing')
 return {'checks_passed':not errors,'errors':errors,'pending':pending,'selected_story':selection.get('candidate_id') if selection else None,'guarantee':'IDs, input availability, source drift and declared decision consistency only. The host must verify the actual human conversation; origin labels do not authenticate a person. No automatic scientific synthesis, causal inference or aesthetic certification.'}

def brief(plan):
 lines=['# 故事讨论：从材料与读者判断开始','',plan['brief'].get('starting_point','意图尚未明确'),'','项目自身结果：'+plan['brief']['own_results_status'],'','## 先帮助作者辨认要表达什么','']
 if plan['brief'].get('user_intent'):lines+=['当前表达意图（保留原话与代理解释的区别）：'+str(plan['brief']['user_intent']),'']
 for q in plan.get('guidance',[]):lines+=['- '+q['prompt']+'（'+q['when']+'）']
 for c in plan.get('candidates',[]):
  lines+=['','## '+c['id']+' · '+c['title'],'','读者起点：'+c['reader_before'],'','希望读者理解：'+c['reader_after'],'','叙事顺序的理由：'+c['why_this_order'],'']
  for step in c['steps']:lines+=['- '+step['reader_question']+' → '+', '.join(step['panel_ids'])+'；正文任务：'+step['paragraph_job']]
  lines+=['','证据缺口：'+'；'.join(c['gaps']),'','用于讨论的问题：'+c['discussion_question']]
 return '\n'.join(lines)+'\n'

def board(plan,out):
 # A local discussion surface; it does not run an LLM or turn browsing into scientific synthesis.
 esc=lambda s:html.escape(str(s));panels={p['id']:p for p in plan.get('panels',[])};blocks=[]
 for c in plan.get('candidates',[]):
  cards=[]
  for s in c['steps']:
   ps=[]
   for id in s['panel_ids']:
    p=panels[id];im='<a href="'+esc(p['preview'])+'"><img src="'+esc(p['preview'])+'" alt="'+esc(p['reader_question'])+'"></a>' if p.get('preview') else '<div class="missing">'+esc({'needs_project_data':'仍需数据','reference_only':'文献参考','ready':'已有图稿'}.get(p.get('state'),p.get('state','需材料')))+' · '+esc('；'.join(p.get('required_inputs',[])))+'</div>'
    ps.append('<article><p class="limit">'+esc(p.get('preview_label',p.get('state','讨论材料')))+' · '+esc({'ready':'已有图稿','needs_project_data':'仍需项目数据','reference_only':'文献参考'}.get(p.get('state'),p.get('state','')))+'</p>'+im+'<h4>'+esc(p['reader_question'])+'</h4><p>读者动作：'+esc(p['reader_action'])+'</p><p>为什么用这种表达：'+esc(p['encoding_rationale'])+'</p><p class="limit">不能推出：'+esc('；'.join(p['cannot_infer']))+'</p></article>')
   cards.append('<section class="step"><h3>'+esc(s['reader_question'])+'</h3><div class="panels">'+''.join(ps)+'</div><p>正文衔接：'+esc(s['paragraph_job'])+'</p></section>')
  blocks.append('<section class="candidate" id="'+esc(c['id'])+'"><h2>'+esc(c['title'])+'</h2><p><b>读者原来：</b>'+esc(c['reader_before'])+'</p><p><b>看完之后：</b>'+esc(c['reader_after'])+'</p><p>'+esc(c['why_this_order'])+'</p>'+'<div class="journey">'+''.join(cards)+'</div><p class="limit">还缺：'+esc('；'.join(c['gaps']))+'</p><label>'+esc(c['discussion_question'])+'<textarea placeholder="可以写：更接近哪一部分、哪里不符合我的意思、想保留什么……"></textarea></label><button data-story="'+esc(c['id'])+'">导出这段反馈供继续讨论</button><output role="status"></output></section>')
 qs=''.join('<p><b>'+esc(x['when'])+'</b> · '+esc(x['prompt'])+'</p>' for x in plan.get('guidance',[]))
 if plan.get('brief',{}).get('user_intent'):qs='<p><b>当前表达意图</b> · '+esc(plan['brief']['user_intent'])+'</p><p class="limit">对照候选判断是否仍在讲同一个故事；此摘要不自动代表作者选择或科学结论。</p>'+qs
 own=plan.get('brief',{}).get('own_results_status','not_provided')
 notice=('项目自身研究结果尚未提供。' if own=='not_provided' else '项目自身结果的可用范围：'+own+'。')+('故事尚未由作者选择。' if not plan.get('selection') else '已有声明的故事选择，仍需核对真实作者决定与证据。')+'文献原图/重绘用于文献讨论与表达参考，不能冒充项目结果。页面导出反馈文件，后续解释与修订由作者和代理完成。'
 synthesis=plan.get('synthesis',{})
 themes=''.join('<li>'+esc(x.get('title',x.get('question',x.get('id',''))))+' · '+esc(x.get('insight',x.get('summary',x.get('agreement','')))+' '+x.get('tension',''))+' <small>'+esc(', '.join(x.get('observation_ids',[])))+'</small></li>' for x in synthesis.get('themes',[]))
 notes=''.join('<li>'+esc(x)+'</li>' for key in ['agreements','tensions','disagreements','comparability_limits'] for x in synthesis.get(key,[]))
 evidence='<details><summary>查看材料归纳与比较边界（不是项目新结果）</summary><ul>'+themes+notes+'</ul><ul>'+''.join('<li>'+esc(o['id'])+' · '+esc(o['statement'])+'<br><small>'+esc(o['paper_id'])+' · '+esc(o['locator'])+' · '+esc(o['basis'])+' / '+esc(o['use'])+'</small></li>' for o in plan.get('observations',[]))+'</ul></details>'
 links='<nav>'+''.join('<a href="'+esc(x['href'])+'">'+esc(x['title'])+'</a>' for x in plan.get('links',[]))+'</nav>'
 data=json.dumps({'plan_id':plan.get('id'),'selection':plan.get('selection')},ensure_ascii=False).replace('<','\\u003c')
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>从材料找故事 · 图文协作台</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f5f2;color:#20343c;font:16px/1.7 Arial,"PingFang SC",sans-serif}main{max-width:1400px;margin:auto;padding:32px}h1{line-height:1.3}h2{border-bottom:2px solid #829eaa;padding-bottom:12px}.notice,.guide{padding:18px 22px;background:#e8eff0;border-left:4px solid #59818b}.candidate{margin:32px 0;background:white;padding:26px}.journey{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:22px;margin:24px 0}.step{margin:0;min-width:0}.step h3{font-size:17px;min-height:56px}.panels p{font-size:14px}h4{font-size:16px}.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}article{padding:16px;border:1px solid #dbe3e4}article img{max-width:100%;max-height:300px;object-fit:contain}.missing{min-height:140px;background:#f1f2ef;padding:25px;color:#6a7375}.limit{color:#806446;font-size:14px}textarea{display:block;width:100%;min-height:100px;margin:12px 0;font:inherit;padding:12px}button{font:inherit;background:#365e69;color:white;border:0;padding:12px 20px;cursor:pointer}nav a{display:inline-block;margin:8px 18px 0 0;color:#326370}footer{font-size:13px;color:#687578} @media(max-width:600px){main{padding:16px}.candidate{padding:16px}}</style><main><h1>先一起找出要讲什么，再决定画什么。</h1>'''+links+'''<p class="notice">这是材料驱动的讨论稿。'''+esc(notice)+'''</p><div class="guide">'''+qs+'</div>'+evidence+'<nav>'+''.join('<a href="#'+esc(c['id'])+'">'+esc(c['title'])+'</a>' for c in plan.get('candidates',[]))+'</nav>'+''.join(blocks)+'''<footer>当前讨论未自动确认任何故事。导出的反馈也是待核对的意见，不会自动改写科学主张或图件。</footer></main><script>const context='''+data+''';document.querySelectorAll('button[data-story]').forEach(b=>b.onclick=()=>{const value=b.closest('.candidate').querySelector('textarea').value;if(!value.trim())return;const feedback={plan_id:context.plan_id,candidate_id:b.dataset.story,action:'feedback_for_discussion',verbatim:value,selection:null};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(feedback,null,2)],{type:'application/json'}));a.download='story-feedback.json';a.click();URL.revokeObjectURL(a.href);b.closest('.candidate').querySelector('output').textContent='反馈已导出，故事仍未自动选定。'});</script></html>'''
 Path(out).write_text(page,encoding='utf8')

def affected(plan,observation_id):
 ps=[p['id'] for p in plan.get('panels',[]) if observation_id in p.get('observation_ids',[])]
 cs=[c['id'] for c in plan.get('candidates',[]) if any(observation_id in s.get('observation_ids',[]) or any(p in ps for p in s.get('panel_ids',[])) for s in c['steps'])]
 return {'observation_id':observation_id,'panels':ps,'candidates_to_reopen':cs,'action':'Re-read source, reconsider claims and candidate order before polishing affected figures; no auto-rewrite'}

def main():
 ap=argparse.ArgumentParser(description=__doc__);subs=ap.add_subparsers(dest='cmd',required=True)
 for command in ['check','brief','board','impact']:
  p=subs.add_parser(command);p.add_argument('plan');p.add_argument('--project');p.add_argument('--out')
  if command=='impact':p.add_argument('observation_id')
 args=ap.parse_args()
 if args.cmd in {'brief','board'} and not args.out:ap.error('--out is required for brief/board')
 plan=read(args.plan);root=Path(args.plan).resolve().parent;project=read(args.project) if args.project else None;r=validate(plan,root,project)
 if not r['checks_passed']:print(json.dumps(r,ensure_ascii=False));return 1
 if args.cmd=='check':
  if args.out:write(args.out,r)
  print(json.dumps(r,ensure_ascii=False))
 elif args.cmd=='impact':
  result=affected(plan,args.observation_id)
  if args.out:write(args.out,result)
  print(json.dumps(result,ensure_ascii=False))
 elif args.cmd=='brief':Path(args.out).write_text(brief(plan),encoding='utf8')
 else:board(plan,args.out)
 return 0
if __name__=='__main__':raise SystemExit(main())
