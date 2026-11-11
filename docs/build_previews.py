"""Compose gallery previews from already rendered public examples; no data edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/images'
FONT=Path(matplotlib.get_data_path())/'fonts/ttf'
def font(size,bold=False):
    return ImageFont.truetype(str(FONT/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
INK='#203744'; MUTED='#61737c'; TEAL='#15888c'; BG='#eef3f4'
def place(canvas,path,box):
    im=Image.open(path).convert('RGBA')
    if path.name == 'PdZn-ZnO.png':
        # Trim transparent margins only; preserve every visible atom.
        im=im.crop(im.getchannel('A').getbbox())
    im=ImageOps.contain(im,(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    x=box[0]+(box[2]-box[0]-im.width)//2; y=box[1]+(box[3]-box[1]-im.height)//2
    canvas.paste(im,(x,y),im)

def cover():
    im=Image.new('RGB',(1800,1160),BG); d=ImageDraw.Draw(im)
    d.text((48,34),'Research Story Harness',font=font(54,True),fill=INK)
    d.text((50,105),'Intent into evidence. Evidence into scientific expression.',font=font(26),fill=MUTED)
    cards=[('01  Graphical abstracts','collateral-toc.png'),
           ('02  OVITO structures · idealized models','../../examples/supported-nanoparticles/renders/PdZn-ZnO.png'),
           ('03  Source-backed data figures','condition-map.png'),
           ('04  Complete editable research talks','rfdiffusion-08.png')]
    for i,(title,src) in enumerate(cards):
        x=48+(i%2)*864; y=174+(i//2)*466
        d.rounded_rectangle((x,y,x+840,y+440),radius=18,fill='white')
        d.text((x+24,y+20),title,font=font(25,True),fill=INK)
        d.line((x+24,y+64,x+816,y+64),fill='#dce5e8',width=2)
        place(im,OUT/src,(x+24,y+80,x+816,y+420))
    d.text((50,1122),'Actual rendered examples  /  Sources and editing entry points in the repository',font=font(21),fill=MUTED)
    im.save(OUT/'showcase-cover.png',optimize=True)

def deck_overview():
    im=Image.new('RGB',(1800,1470),BG); d=ImageDraw.Draw(im)
    d.text((38,25),'RFdiffusion | 20-slide research talk',font=font(38,True),fill=INK)
    d.text((40,82),'18 main slides + 2 backup slides · actual exported pages · paper material CC BY 4.0',font=font(21),fill=MUTED)
    for i in range(20):
        x=38+(i%4)*438; y=140+(i//4)*260
        d.rounded_rectangle((x-2,y-2,x+414,y+238),radius=8,fill='white')
        place(im,ROOT/f'examples/rfdiffusion/slides/{i+1:02d}.png',(x,y,x+412,y+232))
        d.text((x,y+236),f'{i+1:02d}',font=font(17,True),fill=TEAL)
    im.save(OUT/'rfdiffusion-overview.png',optimize=True)

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    cover();deck_overview()
    print('Composed showcase cover and complete deck overview from existing outputs.')
