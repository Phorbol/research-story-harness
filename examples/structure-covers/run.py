#!/usr/bin/env python3
"""Recompose the published cover variants, or regenerate structures with Blender."""
import argparse,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;K=R.parents[1]/'skills/structure-cover/scripts'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=R/'build');p.add_argument('--blender',help='Blender executable; omitted means use supplied lossless renders');p.add_argument('--font-cjk');p.add_argument('--font-latin');a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
def font(explicit,candidates):
 for v in ([explicit] if explicit else [])+candidates:
  if v and Path(v).is_file():return str(Path(v).resolve())
 raise SystemExit('Font not found: supply --font-cjk and --font-latin (with chemical subscripts).')
cjk=font(a.font_cjk,['/System/Library/Fonts/Hiragino Sans GB.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','C:/Windows/Fonts/msyh.ttc'])
latin=font(a.font_latin,['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf'])
images={n:R/'renders'/f'{n}.webp' for n in ['satin-metal','caffeine','aspirin']}
if a.blender:
 for name,source,recipe in [('satin-metal','particle','satin-metal'),('metal-strip','particle','metal-strip'),('caffeine','caffeine','molecule-editorial'),('aspirin','aspirin',None)]:
  path=out/'renders'/f'{name}.png';cmd=[a.blender,'--background','--python',str(K/'render_blender.py'),'--',str(R/'inputs'/f'{source}.json'),str(path)]
  if recipe:cmd.append(str(R/'recipes'/f'{recipe}.json'))
  subprocess.run(cmd,check=True);images[name]=path
for name in ['particle-centred','caffeine-centred','molecules-paired','caffeine-square']:
 s=json.loads((R/'recipes'/f'{name}.json').read_text());s['font_path']=cjk
 for t in s['text']:
  if t.get('font_path')=='FONT_LATIN':t['font_path']=latin;t['font_family']='Arial, DejaVu Sans, sans-serif'
 for sub in s['subjects']:sub['image']=str(images[Path(sub['image']).stem])
 config=out/f'{name}.json';config.write_text(json.dumps(s,ensure_ascii=False,indent=2))
 subprocess.run([sys.executable,str(K/'compose_cover.py'),s['subjects'][0]['image'],str(config),'--out',str(out/name)],check=True)
print('Created four editable cover variants in',out)
