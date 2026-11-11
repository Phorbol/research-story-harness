#!/usr/bin/env python3
"""Inspect a local or publicly accessible PDF; semantic fields remain unassessed."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import urllib.request


def inspect_pdf(data, out, pages, source):
    if not data.startswith(b'%PDF-'):
        raise ValueError('Response is not PDF: HTML/login/challenge pages are not paper files')
    import fitz
    doc=fitz.open(stream=data,filetype='pdf')
    if any(p<1 or p>len(doc) for p in pages):
        raise ValueError('Page numbers must be within the actual PDF (one-based)')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'source.pdf').write_bytes(data)
    report={'source':source,'sha256':hashlib.sha256(data).hexdigest(),'page_count':len(doc),
            'metadata':doc.metadata,'access_status':'pdf_parsed','visual_inspection_status':'unassessed','pages':[]}
    for n in pages:
        page=doc[n-1];page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(out/f'page-{n}.png')
        (out/f'page-{n}.txt').write_text(page.get_text(),encoding='utf8')
        spans=[]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    spans.append({k:span[k] for k in ('text','font','size','flags','color','bbox')})
        report['pages'].append({'pdf_page':n,'text_spans':spans,'scope':'Whole-page extraction, including body text; figure regions need explicit identification'})
    (out/'inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    card={'source':source,'source_sha256':report['sha256'],'version_family':None,'figure_locator':None,
          'caption_locator':None,'body_locator':None,'observed_pages':pages,'status':'unassessed',
          'layers':{k:{'value':None,'origin':'unknown','locator':None,'confidence':None} for k in
                    ('scientific_objects','relations','argument_role','visual_encoding','layout','surface_style')},
          'task_tags':[],'layout_tags':[],'style_tags':[],'transfer_conditions':[],'do_not_transfer':[]}
    (out/'pattern-card.json').write_text(json.dumps(card,ensure_ascii=False,indent=2),encoding='utf8')
    return report


def extract_regions(data, out, regions, source, scale=3):
    """Export explicit PDF rectangles with context, not automatic semantic crops."""
    if not data.startswith(b'%PDF-'):
        raise ValueError('Response is not PDF: HTML/login/challenge pages are not paper files')
    import fitz
    if not isinstance(regions, list) or not regions:
        raise ValueError('regions must be a non-empty list')
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('scale must be positive')
    doc = fitz.open(stream=data, filetype='pdf')
    prepared, ids = [], set()
    # Validate the whole request before producing assets.
    for item in regions:
        name = item['id']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', name) or name in ids:
            raise ValueError('region ids must be unique, filename-safe identifiers')
        ids.add(name)
        n = item['page']
        if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= len(doc):
            raise ValueError('region page must be a one-based PDF page number')
        box = item['rect_pt']
        if len(box) != 4 or not all(math.isfinite(v) for v in box):
            raise ValueError('rect_pt requires four finite PDF point coordinates')
        page, rect = doc[n - 1], fitz.Rect(box)
        if rect.is_empty or not page.rect.contains(rect):
            raise ValueError('region rectangle must have positive area inside the PDF page')
        target = item.get('target_px')
        if target is not None and (len(target) != 2 or not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in target)):
            raise ValueError('target_px requires two positive integer display pixel dimensions')
        prepared.append((item, page, rect, target))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report = {'source': source, 'source_sha256': hashlib.sha256(data).hexdigest(),
              'coordinate_system': 'PDF page points, top-left origin; explicit rect_pt, not screenshot pixels',
              'visual_inspection_status': 'unassessed', 'regions': []}
    for item, page, rect, target in prepared:
        name = item['id']
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=rect, alpha=False)
        png = pix.tobytes('png')
        (out / f'{name}.png').write_bytes(png)
        # Margin belongs only to the review image, never silently to the crop.
        context = fitz.Rect(rect.x0-24, rect.y0-24, rect.x1+24, rect.y1+24) & page.rect
        review = fitz.open()
        rp = review.new_page(width=context.width, height=context.height)
        rp.show_pdf_page(rp.rect, doc, page.number, clip=context)
        rp.draw_rect(fitz.Rect(rect.x0-context.x0, rect.y0-context.y0,
                               rect.x1-context.x0, rect.y1-context.y0), color=(0.9, 0.1, 0.1), width=0.7)
        rp.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(out / f'{name}-context.png')
        review.close()
        crossing = []
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    sr = fitz.Rect(span['bbox'])
                    if sr.intersects(rect) and not rect.contains(sr):
                        crossing.append({'text': span['text'], 'bbox_pt': list(sr)})
        entry = {'id': name, 'page': item['page'], 'rect_pt': list(rect),
                 'asset': f'{name}.png', 'context': f'{name}-context.png',
                 'context_rect_pt': list(context), 'asset_pixels': [pix.width, pix.height],
                 'text_crossing_crop_edge': crossing,
                 'note': 'Text hints miss raster labels, paths and scientific object boundaries; visual judgment required.'}
        if target is not None:
            width, height = target
            factor = min(width/pix.width, height/pix.height)
            fw, fh = pix.width*factor, pix.height*factor
            fitted = fitz.Rect((width-fw)/2, (height-fh)/2, (width+fw)/2, (height+fh)/2)
            preview = fitz.open()
            pp = preview.new_page(width=width, height=height)
            pp.insert_image(fitted, stream=png)
            pp.get_pixmap(alpha=False).save(out / f'{name}-target.png')
            preview.close()
            entry.update({'target_px': target, 'contain_image_rect_px': list(fitted),
                          'target_preview': f'{name}-target.png'})
        report['regions'].append(entry)
    doc.close()
    (out / 'regions.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',help='Local PDF path or explicitly selected public HTTP(S) PDF URL')
    ap.add_argument('--pages',help='Comma-separated one-based PDF page numbers')
    ap.add_argument('--regions',help='JSON list of id/page/rect_pt, optional target_px; exports crops plus context')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    if bool(args.pages) == bool(args.regions):
        ap.error('choose exactly one of --pages or --regions')
    if args.source.startswith(('https://','http://')):
        req=urllib.request.Request(args.source,headers={'User-Agent':'ScientificFigureReferenceIntake/1.0'})
        with urllib.request.urlopen(req,timeout=40) as response:data=response.read()
    else:data=Path(args.source).read_bytes()
    if args.regions:
        report=extract_regions(data,args.out,json.loads(Path(args.regions).read_text()),args.source)
        print(json.dumps({'regions':len(report['regions']),'visual_inspection_status':report['visual_inspection_status']}))
    else:
        report=inspect_pdf(data,args.out,[int(p) for p in args.pages.split(',')],args.source)
        print(json.dumps({k:report[k] for k in ('page_count','access_status','visual_inspection_status')}))

if __name__=='__main__':main()
