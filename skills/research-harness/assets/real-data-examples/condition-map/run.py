"""Run from any current working directory; all paths resolve beside this file."""
from pathlib import Path
import argparse, os, tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'condition-map-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from figure import draw, CONFIG
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'output');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
f=plt.figure();draw(f,ROOT)
for ext in ['png','pdf','svg']:f.savefig(a.out/f'condition-map.{ext}',dpi=CONFIG['dpi'])
plt.close(f)
print(a.out.resolve())
