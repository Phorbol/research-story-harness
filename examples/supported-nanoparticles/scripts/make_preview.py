"""Compose the two existing renders at a shared scale; do not rerender or alter atoms."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import matplotlib.font_manager as fm
ROOT=Path(__file__).resolve().parents[1]
ims=[Image.open(ROOT/'renders'/f'{n}-ZnO.png').convert('RGBA') for n in ['PdZn','PdCu']]
boxes=[im.getchannel('A').getbbox() for im in ims]
bbox=(max(0,min(b[0] for b in boxes)-48),max(0,min(b[1] for b in boxes)-48),min(ims[0].width,max(b[2] for b in boxes)+48),min(ims[0].height,max(b[3] for b in boxes)+48))
width=780;scale=width/(bbox[2]-bbox[0]);height=round((bbox[3]-bbox[1])*scale)
canvas=Image.new('RGBA',(1800,1000),(249,250,250,255));d=ImageDraw.Draw(canvas)
def font(size,bold=False):return ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans',weight='bold' if bold else 'normal')),size)
ink='#253845';muted='#62727A'
d.text((80,56),'Supported nanoparticle models',font=font(43,True),fill=ink)
d.text((80,116),'Idealized, unrelaxed structures · ASE construction · OVITO / Tachyon rendering',font=font(23),fill=muted)
for i,(im,title) in enumerate(zip(ims,['Pd–Zn particle on ZnO','Pd–Cu particle on ZnO'])):
 x=80+i*860;d.text((x,184),title,font=font(29,True),fill=ink)
 picture=im.crop(bbox).resize((width,height),Image.Resampling.LANCZOS)
 canvas.alpha_composite(picture,(x,240))
d=ImageDraw.Draw(canvas)
legend_y=886
for x,(sym,color) in zip([570,750,930,1110],[('Pd','#AAB8C6'),('Zn','#D1BF8C'),('Cu','#BD7C58'),('O','#B85E55')]):
 d.ellipse((x,legend_y-8,x+24,legend_y+16),fill=color)
 d.text((x+35,legend_y-12),sym,font=font(24),fill=ink)
d.text((80,949),'Same coordinates and substitution sites. Constructed illustrations, not paper coordinates.',font=font(22),fill=muted)
canvas.convert('RGB').save(ROOT/'nanoparticles-preview.png')
print(ROOT/'nanoparticles-preview.png')
