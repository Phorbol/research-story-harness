import os;os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys,json
from pathlib import Path
import numpy as np
from ovito.data import DataCollection,Particles
from ovito.pipeline import Pipeline,StaticSource
from ovito.vis import Viewport,TachyonRenderer
p=Path(sys.argv[1]);s=json.loads(p.read_text());out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
def rgb(h):return [int(h[i:i+2],16)/255 for i in [1,3,5]]
d=DataCollection();a=Particles(count=len(s['positions']));d.objects.append(a)
a.create_property('Position',data=s['positions']);a.create_property('Color',data=[rgb(s['colors'][e]) for e in s['elements']]);a.create_property('Radius',data=[s['radii'][e] for e in s['elements']])
if s['bonds']:
 b=a.create_bonds(count=len(s['bonds']));b.create_property('Topology',data=[[x['a'],x['b']] for x in s['bonds']]);b.vis.width=.17
pipe=Pipeline(source=StaticSource(data=d));pipe.add_to_scene()
c=s['camera'];direction=np.array(c['direction']);direction/=np.linalg.norm(direction);target=np.array(c['target'])
v=Viewport(type=Viewport.Type.Ortho,camera_dir=tuple(direction),camera_up=tuple(c['up']));v.camera_pos=tuple(target-direction*150);v.fov=c['halfheight']
renderer=TachyonRenderer(ambient_occlusion=True,ambient_occlusion_brightness=.78,ambient_occlusion_samples=32,antialiasing_samples=8,direct_light_intensity=.72,shadows=False)
v.render_image(filename=str(out),size=tuple(s['size']),renderer=renderer,alpha=True,crop=False)
(out.with_suffix('.json')).write_text(json.dumps({'backend':'OVITO Tachyon','scene':str(p),'camera_pos':list(v.camera_pos),'camera_dir':list(v.camera_dir),'halfheight':v.fov,'size':s['size'],'atom_count':len(s['positions'])},indent=2))
pipe.remove_from_scene();print(out)
