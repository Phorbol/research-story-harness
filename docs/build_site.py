"""Build the public static gallery using only assets already in this repository."""
import argparse
import shutil
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def build(out):
    out.mkdir(parents=True, exist_ok=True)
    assets = out / 'assets'
    assets.mkdir(exist_ok=True)
    for src, dst in [('structure-covers.html','index.html'),('showcase.css','style.css'),('showcase.js','app.js')]:
        shutil.copyfile(ROOT / 'docs' / src, out / dst)
    covers = ROOT / 'examples/structure-covers'
    images = {
        'particle.jpg': covers/'covers/particle-centred.jpg',
        'caffeine.jpg': covers/'covers/caffeine-centred.jpg',
        'paired.jpg': covers/'covers/molecules-paired.jpg',
        'square.jpg': covers/'covers/caffeine-square.jpg',
        'material.jpg': covers/'previews/material-comparison.jpg',
        'mobile.jpg': covers/'previews/mobile-wide.jpg',
        'particle-thumb.jpg': covers/'previews/particle-centred-320.jpg',
        'caffeine-thumb.jpg': covers/'previews/caffeine-centred-320.jpg',
        'paired-thumb.jpg': covers/'previews/molecules-paired-320.jpg',
        'toc.webp': ROOT/'docs/images/toc-before-after.png',
        'ovito.webp': ROOT/'docs/images/supported-nanoparticles.png',
    }
    images.update({f'science-{n.lower()}.webp':ROOT/f'examples/collateral-response/figures/{n}.png' for n in ['TOC','Fig1','Evidence']})
    images.update({f'{n}-before.webp':ROOT/f'docs/images/revisions/{n}-before.webp' for n in ['toc','fig1','evidence','condition']})
    images['science-condition.webp']=ROOT/'docs/images/condition-map.png'
    images.update({f'slide-{i:02d}.webp':ROOT/f'examples/rfdiffusion/slides/{i:02d}.png' for i in range(1,21)})
    for name, src in images.items():
        if name.endswith('.webp'):
            im=Image.open(src).convert('RGB')
            im.thumbnail((2000,1400),Image.Resampling.LANCZOS)
            im.save(assets/name,quality=90,method=6)
        else:
            shutil.copyfile(src,assets/name)
    # Split the existing three-column contact sheet at its exact panel boundaries.
    # No structure pixels are discarded; the original sheet remains downloadable.
    sheet=Image.open(covers/'previews/material-comparison.jpg')
    for i in range(3):
        sheet.crop((i*sheet.width//3,0,(i+1)*sheet.width//3,sheet.height)).save(assets/f'material-{i+1}.jpg',quality=95)
    # Reserve image space before download so deep links and mobile reading do not jump.
    page=out/'index.html'
    def dimensions(match):
        tag=match.group(0)
        src=re.search(r'src="(assets/[^"]+)"',tag)
        if not src or re.search(r'\bwidth=',tag):
            return tag
        with Image.open(out/src.group(1)) as im:
            return tag[:-1]+f' width="{im.width}" height="{im.height}">'
    page.write_text(re.sub(r'<img\b[^>]*>',dimensions,page.read_text()))
    print(f'Built gallery with {len(images)+3} public images: {out}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'build/site')
    build(parser.parse_args().out.resolve())
