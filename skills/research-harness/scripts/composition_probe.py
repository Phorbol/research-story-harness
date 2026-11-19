#!/usr/bin/env python3
"""Put actual PDF composition studies side by side, without rescaling or grading.

Requires PyMuPDF (also used by scientific-figure/reference_intake.py).
The optional masks are diagnostic copies, never edits to source PDFs.
"""
import argparse
import html
import json
from pathlib import Path


def build(spec_path, out):
    import fitz
    spec_path, out = Path(spec_path), Path(out)
    spec = json.loads(spec_path.read_text())
    width, height = map(float, spec["dimensions_mm"])
    if width <= 0 or height <= 0:
        raise ValueError("dimensions_mm must be positive")
    pt = 72 / 25.4
    items = spec["items"]
    if not items:
        raise ValueError("Provide actual candidate/reference PDFs")
    # Validate before creating any outputs. Page size is checked, never fitted.
    prepared = []
    for item in items:
        source = (spec_path.parent / item["pdf"]).resolve()
        doc = fitz.open(source)
        n = int(item.get("page", 1)) - 1
        if not 0 <= n < len(doc):
            raise ValueError(f"Invalid page in {source}")
        page = doc[n]
        actual = [page.rect.width / pt, page.rect.height / pt]
        if max(abs(a-b) for a,b in zip(actual, [width,height])) > 0.05:
            raise ValueError(f"{source}: {actual} mm differs from fixed frame {[width,height]}; no auto-fit")
        masks = item.get("explanation_masks_mm", [])
        for rect in masks:
            if len(rect) != 4 or not (0 <= rect[0] < rect[2] <= width and 0 <= rect[1] < rect[3] <= height):
                raise ValueError(f"Mask outside frame: {rect}")
        prepared.append((item, doc, n, actual))
    out.mkdir(parents=True, exist_ok=True)
    gap, margin, head = 8*pt, 8*pt, 14*pt
    board = fitz.open()
    board_page = board.new_page(width=2*margin+len(items)*width*pt+(len(items)-1)*gap,
                               height=2*margin+head+height*pt)
    cards, records = [], []
    for i, (item, doc, n, actual) in enumerate(prepared):
        stem = f"{i+1:02d}"
        label = str(item.get("label", stem))
        page = doc[n]
        page.get_pixmap(matrix=fitz.Matrix(96/72,96/72), alpha=False).save(out/f"{stem}-native.png")
        x = margin+i*(width*pt+gap)
        board_page.insert_text((x,margin+8), label[:100], fontsize=9)
        board_page.show_pdf_page(fitz.Rect(x,margin+head,x+width*pt,margin+head+height*pt),doc,n)
        mask_html = ""
        if item.get("explanation_masks_mm"):
            masked = fitz.open()
            mp = masked.new_page(width=width*pt,height=height*pt)
            mp.show_pdf_page(mp.rect,doc,n)
            for rect in item["explanation_masks_mm"]:
                mp.draw_rect(fitz.Rect(*(v*pt for v in rect)),color=None,fill=(1,1,1),overlay=True)
            mp.get_pixmap(matrix=fitz.Matrix(96/72,96/72),alpha=False).save(out/f"{stem}-without-explanations.png")
            masked.save(out/f"{stem}-diagnostic.pdf")
            masked.close()
            mask_html = f'<p>Diagnostic only: selected explanations hidden</p><img src="{stem}-without-explanations.png">'
        cards.append(f'<section><h2>{html.escape(label)}</h2><img src="{stem}-native.png">{mask_html}</section>')
        records.append({"label":label,"source":str(doc.name),"actual_mm":actual,
                        "explanation_masks_mm":item.get("explanation_masks_mm",[]),
                        "visual_quality":"unassessed"})
    board.save(out/"native-board.pdf")
    board.close()
    for _,doc,_,_ in prepared:
        doc.close()
    (out/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Composition studies</title>'
        f'<style>body{{font-family:Arial;margin:24px}} main{{display:flex;gap:24px;align-items:flex-start}}'
        f'section{{flex:none;width:{width}mm}} img{{width:{width}mm;height:{height}mm}}h2{{font-size:15px}}</style>'
        '<h1>Fixed-frame composition studies</h1><p>Native PDF frames are preserved. '
        'Screen millimetres depend on zoom and display calibration. No visual verdict is computed.</p><main>'
        +''.join(cards)+'</main>',encoding='utf8')
    report = {"dimensions_mm":[width,height],"items":records,"visual_quality":"unassessed",
              "note":"Inspect real objects, reading path and composition; file presence is not evidence of quality."}
    (out/"inspection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec",type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args = parser.parse_args()
    build(args.spec,args.out)
    print(f"Saved unassessed composition board: {args.out}")
