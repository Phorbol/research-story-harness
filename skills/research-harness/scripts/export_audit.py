#!/usr/bin/env python3
"""Run scoped export checks. This is not a scientific or aesthetic acceptance gate."""
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf',type=Path)
    p.add_argument('--min-pt',type=float,required=True,help='Minimum effective size for this artifact, not a universal journal rule')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--layout',type=Path,help='Measured panel geometry JSON; omit for non-panel figures')
    a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    vendor=Path(__file__).parent/'vendor'/'nature_figure'
    jobs=[('text',['audit_pdf_text.py',str(a.pdf),'--min-pt',str(a.min_pt),'--json']),('collisions',['audit_figure_collisions.py',str(a.pdf),'--json','--overlay-pdf',str(a.out/'collisions-overlay.pdf')])]
    if a.layout: jobs.append(('panels',['audit_panel_alignment.py',str(a.layout),'--json','--overlay-svg',str(a.out/'panels-overlay.svg')]))
    reports=[]
    for name,args in jobs:
        r=subprocess.run([sys.executable,str(vendor/args[0]),*args[1:]],capture_output=True,text=True)
        try: payload=json.loads(r.stdout)
        except ValueError: payload={'raw_stdout':r.stdout}
        record={'check':name,'returncode':r.returncode,'report':payload,'stderr':r.stderr}
        (a.out/(name+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
        reports.append(record)
    result={'pdf':str(a.pdf.resolve()),'checks':reports,'panel_check':'requested' if a.layout else 'not_requested','visual_acceptance':'not_evaluated','scientific_acceptance':'not_evaluated'}
    (a.out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'reports':str(a.out.resolve()),'returncodes':{r['check']:r['returncode'] for r in reports},'visual_acceptance':'not_evaluated'}))
    return int(any(r['returncode'] for r in reports))
if __name__=='__main__': raise SystemExit(main())
