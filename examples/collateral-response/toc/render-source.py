from pathlib import Path
import os, json, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'collateral-example-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import fitz
matplotlib.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
version=sys.argv[1] if len(sys.argv)>1 else 'first'
out=ROOT/version
out.mkdir(exist_ok=True);(out/'native-96dpi').mkdir(exist_ok=True)
DATA=json.loads((ROOT/'data.json').read_text())
COL={'positive':'#C35D37','negative':'#176E96','zero':'#E4E8EA','ink':'#243746','muted':'#697983'}
fig=plt.figure(figsize=(80/25.4,40/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,80);ax.set_ylim(0,40);ax.axis('off')
texts=[]
def txt(x,y,s,size=6.5,weight='normal',color=None,ha='left',style='normal',gid=None):
 t=ax.text(x,y,s,fontsize=size,fontweight=weight,fontstyle=style,color=color or COL['ink'],ha=ha,va='center',linespacing=1.16)
 if gid:t.set_gid(gid)
 texts.append(t);return t
def line(x,y,xx,yy,color='#CCD4D9',lw=.5):ax.plot([x,xx],[y,yy],color=color,lw=lw,solid_capstyle='round')
# A single continuous illustration; exact outcomes remain independent editable vector annotations.
asset=Image.open(ROOT/'assets/four-independent-cultures.png')
ax.imshow(asset,extent=(18,81,8.2,34.98),zorder=0)
txt(2.5,37.1,'E. faecalis',7.2,style='italic')
txt(22.5,37.1,'Independent evolution',7.5,'bold')
txt(2.5,31.8,'DAP',8.5,'bold')
txt(2.5,28.7,'selection',6.5)
txt(2.5,22.3,'CRO',8.5,'bold')
txt(2.5,19.2,'response',6.5)
# Selecting-to-testing relation, not an evolutionary time series.
ax.annotate('',xy=(6.5,24.8),xytext=(6.5,26.5),arrowprops={'arrowstyle':'-|>','lw':.65,'color':COL['muted'],'mutation_scale':6})
centers=[18+63*x/1920 for x in [380,766,1154,1542]]
glyphmap=[]
for x,r in zip(centers,[r for r in DATA if r['selecting']=='DAP']):
 v=r['value'];kind='positive' if v>0 else 'negative' if v<0 else 'zero';s='+' if v>0 else '−' if v<0 else '0'
 txt(x,29.0,str(r['replicate']),6.5,ha='center',gid=r['id']+'-identity')
 p=Rectangle((x-3.7,20.3),7.4,5.4,facecolor=COL[kind],edgecolor='white',lw=.25,zorder=4);p.set_gid(r['id']+'-response');ax.add_patch(p)
 t=txt(x,23,s,11,'bold',COL['ink'] if kind=='zero' else 'white','center',gid=r['id']+'-sign');t.set_zorder(5)
 glyphmap.append({**r,'glyph_id':r['id']+'-response','sign':s,'color':COL[kind],'geometry':'equal-sized vector rectangle over conceptual population illustration; not quantitative area'})
# Only the source outcome badge is colored; illustration biology is neutral.
txt(2.5,15.8,'+ Resistant',6.1,color=COL['positive'])
txt(2.5,12.8,'− Sensitive',6.1,color=COL['negative'])
txt(2.5,9.8,'Threshold zero',6.1,color=COL['muted'])
line(2.5,7.1,77.5,7.1)
txt(2.5,3.6,'CRO → RIF',7.2,'bold')
for x,r in zip([37,43,49,55],[r for r in DATA if r['selecting']=='CRO']):
 p=Rectangle((x-2.45,1.6),4.9,4.0,facecolor=COL['negative'],edgecolor='none');p.set_gid(r['id']+'-response');ax.add_patch(p)
 txt(x,3.7,'−',8,'bold','white','center',gid=r['id']+'-sign')
 glyphmap.append({**r,'glyph_id':r['id']+'-response','sign':'−','color':COL['negative'],'geometry':'equal-sized vector rectangle (4.9 x 4.0 mm); replicate 1–4 left to right'})
txt(59.5,3.7,'All sensitive',6.3,color=COL['negative'])
fig.savefig(out/'TOC.pdf',dpi=600,facecolor='white');fig.savefig(out/'TOC.svg',dpi=600,facecolor='white');fig.savefig(out/'TOC.png',dpi=600,facecolor='white')
fig.canvas.draw();renderer=fig.canvas.get_renderer();layout=[]
for t in texts:
 box=t.get_window_extent(renderer).transformed(fig.dpi_scale_trans.inverted());layout.append({'text':t.get_text(),'font_size_pt':t.get_fontsize(),'bounds_inches':list(box.bounds),'object_id':t.get_gid()})
(out/'layout.json').write_text(json.dumps(layout,indent=2))
doc=fitz.open(out/'TOC.pdf');page=doc[0];page.get_pixmap(dpi=96,alpha=False).save(out/'native-96dpi/TOC.png')
(out/'source-map.json').write_text(json.dumps({'source':'Maltas and Wood (2019), S1 Data, Figure1','source_file':'assets/pbio.3000515.s017.xlsx','records':glyphmap,'concept_illustration':'assets/four-independent-cultures.png; image generation, no empirical data or measurements','zero':'Source threshold zero: absolute IC50 difference did not exceed 3 × ancestral SEM; not missing and not proof of zero biological effect'},indent=2))
(out/'verification.json').write_text(json.dumps({'pdf_mm':[page.rect.width*25.4/72,page.rect.height*25.4/72],'png_96dpi':list(Image.open(out/'native-96dpi/TOC.png').size),'data_values':[r['value'] for r in DATA],'pdf_text':page.get_text(),'glyph_count':len(glyphmap),'bounds_check':all(b['bounds_inches'][0]>=0 and b['bounds_inches'][1]>=0 and b['bounds_inches'][0]+b['bounds_inches'][2]<=80/25.4 and b['bounds_inches'][1]+b['bounds_inches'][3]<=40/25.4 for b in layout)},indent=2))
if Path(__file__).resolve() != (out/'render-source.py').resolve():
 shutil.copy2(__file__,out/'render-source.py')
if ROOT.resolve() != out.resolve():
 shutil.copytree(ROOT/'assets',out/'assets',dirs_exist_ok=True)
 shutil.copy2(ROOT/'data.json',out/'data.json')
print(out)
