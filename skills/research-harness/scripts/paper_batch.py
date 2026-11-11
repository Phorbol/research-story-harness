#!/usr/bin/env python3
"""Index local JATS XML figures and their prose references before host-agent interpretation."""
import argparse,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path

def extract(path,paper):
 path=Path(path);tree=ET.parse(path);out=[]
 def words(node):return ' '.join(''.join(node.itertext()).split()) if node is not None else ''
 for fig in tree.findall('.//fig'):
  fid=fig.get('id');refs=[words(p) for p in tree.findall('.//body//p') if any(fid in x.get('rid','').split() for x in p.findall('.//xref'))]
  out.append(dict(id=fid,label=words(fig.find('label')),caption=words(fig.find('caption')),assets=[g.get('{http://www.w3.org/1999/xlink}href') for g in fig.findall('.//graphic') if g.get('content-type')!='thumb'],prose_references=refs,reader_task=None,argument_role=None,comparison_or_control=None,scope_and_alternatives=None,review_status='text_extracted_not_interpreted'))
 return dict(paper_id=paper['id'],doi=paper.get('doi'),source_path=paper['path'],source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),access_scope='Local JATS XML text and declared graphic references; images are not visually inspected by this command',figures=out,table_count=len(tree.findall('.//table-wrap')),scientific_review='pending_host_interpretation')

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('manifest');a.add_argument('--out',required=True);args=a.parse_args();manifest=Path(args.manifest).resolve();root=manifest.parent;rows=[];errors=[]
 for paper in json.loads(manifest.read_text())['papers']:
  p=(root/paper['path']).resolve()
  if not p.is_relative_to(root):raise ValueError('Source escapes batch root')
  try:rows.append(extract(p,paper))
  except (OSError,ET.ParseError) as e:errors.append(dict(paper_id=paper['id'],error=str(e)))
 out={'purpose':'Source location and figure/prose inventory for later human-agent synthesis; not a completed paper dissection','papers':rows,'errors':errors};Path(args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'papers_extracted':len(rows),'figures_located':sum(len(x['figures']) for x in rows),'errors':len(errors),'interpretation':'pending'}));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
