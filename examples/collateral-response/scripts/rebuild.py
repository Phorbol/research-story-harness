"""Rebuild one selected figure without regenerating unrelated figures."""
from pathlib import Path
import argparse,subprocess,sys,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'collateral-example-mpl'))
p=argparse.ArgumentParser();p.add_argument('figure',choices=['TOC','Fig1','Evidence']);p.add_argument('--out',default='build');a=p.parse_args()
out=Path(a.out);out=out if out.is_absolute() else ROOT/out;out.mkdir(parents=True,exist_ok=True)
if a.figure=='TOC':
 subprocess.run([sys.executable,str(ROOT/'toc/render-source.py'),str(out.resolve())],check=True)
else:
 import fitz
 import matplotlib.pyplot as plt
 if a.figure=='Fig1':
  from fig1 import draw
 else:
  from evidence import evidence_final as draw
 f=draw()
 for ext in ['pdf','svg','png']:f.savefig(out/f'{a.figure}.{ext}',dpi=600,facecolor='white')
 plt.close(f);(out/'native-96dpi').mkdir(exist_ok=True)
 pdf=fitz.open(out/f'{a.figure}.pdf');pdf[0].get_pixmap(dpi=96,alpha=False).save(out/'native-96dpi'/f'{a.figure}.png')
 print(out)
