"""Compose one or multiple unchanged transparent structures; retain independent source identities."""
import argparse,json,base64,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('spec');p.add_argument('--out',required=True);a=p.parse_args();sp=Path(a.spec).resolve();s=json.loads(sp.read_text());out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
w,h=s['size'];y,x=np.mgrid[0:h,0:w];v=np.exp(-(((x-w*.55)/(w*.6))**2+((y-h*.4)/(h*.8))**2));lo=np.array(s['background'][0]);hi=np.array(s['background'][1]);bg=Image.fromarray((lo+v[:,:,None]*(hi-lo)).astype('uint8')).convert('RGBA');bg.save(out/'background.png');im=bg.copy();placements=[]
def uri(path):return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><image width="{w}" height="{h}" href="{uri(out/"background.png")}"/>'
for i,obj in enumerate(s.get('subjects',[{'box':s.get('subject_box')}])):
 path=Path(obj['image']) if 'image' in obj else Path(a.image).resolve()
 if not path.is_absolute():path=sp.parent/path
 subject=Image.open(path).convert('RGBA');crop=subject.getchannel('A').getbbox()
 if crop is None:raise ValueError('Empty subject')
 subject=subject.crop(crop);xx,yy,bw,bh=obj['box'];scale=min(bw/subject.width,bh/subject.height);sw,sh=round(subject.width*scale),round(subject.height*scale);px,py=round(xx+(bw-sw)/2),round(yy+(bh-sh)/2)
 if px<0 or py<0 or px+sw>w or py+sh>h:raise ValueError('Subject would be clipped')
 im.alpha_composite(subject.resize((sw,sh),Image.Resampling.LANCZOS),(px,py));file=out/f'subject-{i}.png';subject.save(file)
 svg+=f'<image x="{px}" y="{py}" width="{sw}" height="{sh}" href="{uri(file)}"/>'
 placements.append({'source':str(path),'crop':crop,'placement':[px,py,sw,sh]})
im.save(out/'image-only.png');d=ImageDraw.Draw(im)
for t in s.get('text',[]):
 f=ImageFont.truetype(t.get('font_path',s['font_path']),t['size']);anchor=t.get('anchor','lt');d.text(tuple(t['position']),t['value'],font=f,fill=t['color'],anchor=anchor)
 tx,ty=t['position'];ta={'mt':'middle','rt':'end','lt':'start'}[anchor];svg+=f'<text x="{tx}" y="{ty}" text-anchor="{ta}" dominant-baseline="text-before-edge" font-family="{html.escape(t.get("font_family",s["font_family"]))}" font-size="{t["size"]}" fill="{t["color"]}">{html.escape(t["value"])}</text>'
(out/'cover.svg').write_text(svg+'</svg>');im.save(out/'cover.png');im.convert('RGB').save(out/'cover.jpg',quality=95)
for width in s.get('thumbnail_widths',[320]):im.resize((width,round(h*width/w)),Image.Resampling.LANCZOS).convert('RGB').save(out/f'thumbnail-{width}.jpg',quality=95)
(out/'composition.json').write_text(json.dumps({'spec':s,'subjects':placements,'note':'Only complete alpha margins trimmed; no structure pixels edited. Each subject retains independent provenance.'},indent=2,ensure_ascii=False))
