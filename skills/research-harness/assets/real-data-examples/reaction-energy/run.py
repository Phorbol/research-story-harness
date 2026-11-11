"""Local energy + true-coordinate structure panel; not the full reaction network."""
from pathlib import Path
import argparse,json,os,tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'reaction-energy-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np
from energy_panel import draw_energy_panel,BLUE,RED,INK,SIZE,WEIGHT
ROOT=Path(__file__).resolve().parent
cfg=json.loads((ROOT/'config.json').read_text())
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'output');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':cfg['font_family'],'font.weight':WEIGHT['body'],'font.style':'normal','font.size':SIZE['body'],'svg.fonttype':'none','pdf.fonttype':42,'image.composite_image':False,'axes.linewidth':.6})
W,H=cfg['figure_mm']
f=plt.figure(figsize=(W/25.4,H/25.4),facecolor='white')
draw_energy_panel(f)
O=json.loads((ROOT/'assets/vector-overlays.json').read_text());S=ROOT/'assets'
import csv
rows=list(csv.DictReader((ROOT/'data/energy-values.csv').open()))
f.text(.025,.325,'b',fontsize=SIZE['panel'],weight=WEIGHT['panel'],color=INK)
f.text(.085,.325,'Transition states · relative free energies',fontsize=SIZE['title'],color=INK)
for state,x in [('TS1',.08),('TS2',.31),('TS3',.54),('TS4',.77)]:
 sa=f.add_axes([x,.04,.205,.22]);im=plt.imread(S/f'refined_{state}.png');sa.imshow(im);sa.axis('off')
 meta=json.loads((S/f'{state}-metadata.json').read_text())['states'][state]['atom_pixels']
 idx=O[state][0]['indices'];points=np.array([meta[str(j)] for j in idx])
 sa.plot(points[:,0],points[:,1],ls=(0,(3,2)),lw=.85,color='#258F86')
 lx,ly,align={'TS1':(.03,.26,'left'),'TS2':(.04,.55,'left'),'TS3':(.98,.44,'right'),'TS4':(.04,.71,'left')}[state]
 tx,ty=lx*im.shape[1],ly*im.shape[0]
 sa.annotate(f"{O[state][0]['distance_A']:.2f} Å",xy=points.mean(axis=0),xytext=(tx,ty),fontsize=SIZE['distance'],color=INK,ha=align,
             arrowprops={'arrowstyle':'-','color':INK,'lw':.5},bbox={'facecolor':'white','alpha':.94,'edgecolor':'none','pad':1})
 col=BLUE if state in ['TS1','TS4'] else RED
 value=float(next(r['G'] for r in rows if r['state']==state))
 f.text(x,.275,state,fontsize=SIZE['title'],weight=WEIGHT['emphasis'],color=col)
 f.text(x+.067,.275,f'{value:.3f} eV',fontsize=SIZE['body'],color=INK)
f.text(.085,.015,r'473 K; $G[\mathrm{glycerol(g)}]=0$.  ○ Later-state mapping unresolved; blue: within-route continuation.',fontsize=SIZE['footnote'],color=INK)
for ext in ['png','pdf','svg']:f.savefig(a.out/f'reaction-energy.{ext}',dpi=cfg['dpi'])
plt.close(f)
print(a.out.resolve())
