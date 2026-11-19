import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];p=Path(args[0]);s=json.loads(p.read_text());out=Path(args[1]);out.parent.mkdir(parents=True,exist_ok=True)
recipe=json.loads(Path(args[2]).read_text()) if len(args)>2 else {}
style=recipe.get('name','studio')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in [1,3,5]]
 return [x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4 for x in v]
def material(name,col,metal=0,rough=.3):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb(col),1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
mats={e:material(e,col,.65 if e in ['Pd','Cu'] else .0,.40 if e in ['Pd','Cu'] else .48) for e,col in s['colors'].items()}
for e,m in mats.items():
 bs=m.node_tree.nodes.get('Principled BSDF');v=recipe.get('materials',{}).get(e,recipe.get('default_material',{}))
 for key,slot in [('metallic','Metallic'),('roughness','Roughness'),('specular','Specular IOR Level')]:
  if key in v:bs.inputs[slot].default_value=v[key]
# Shared smooth sphere mesh; every source site remains a separate named object.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16);proto=bpy.context.object;mesh=proto.data;mesh.name='unit_atom'
for f in mesh.polygons:f.use_smooth=True
bpy.data.objects.remove(proto,do_unlink=True)
meshes={}
for e in set(s['elements']):
 m=mesh.copy();m.materials.clear();m.materials.append(mats[e]);meshes[e]=m
for i,(xyz,e) in enumerate(zip(s['positions'],s['elements'])):
 o=bpy.data.objects.new(f'atom_{i:04d}_{e}',meshes[e]);bpy.context.collection.objects.link(o);o.location=xyz;o.scale=(s['radii'][e],)*3;o['source_index']=i
for bond in s['bonds']:
 start=Vector(s['positions'][bond['a']]);end=Vector(s['positions'][bond['b']]);mid=(start+end)/2
 for x,y,e in [(start,mid,s['elements'][bond['a']]),(mid,end,s['elements'][bond['b']])]:
  dv=y-x;bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.085,depth=dv.length,location=(x+y)/2)
  o=bpy.context.object;o.name='connectivity';o.rotation_euler=dv.to_track_quat('Z','Y').to_euler();o.data.materials.append(mats[e])
  for f in o.data.polygons:f.use_smooth=True
c=s['camera'];target=Vector(c['target']);direction=Vector(c['direction']).normalized();extent=2*c['halfheight']
bpy.ops.object.camera_add(location=target-direction*150);cam=bpy.context.object;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*s['size'][0]/s['size'][1];cam.data.clip_end=1000;bpy.context.scene.camera=cam
# Area lights positioned in camera basis, so recipes survive changed scientific orientation.
right=direction.cross(Vector((0,0,1))).normalized();up=right.cross(direction).normalized()
def area(name,x,y,z,power,size,color):
 loc=target+right*x+up*y-direction*z;bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color
scale=extent/42
if recipe.get('lights'):
 for light in recipe['lights']:
  x,y,z=light['position'];area(light['name'],x*scale,y*scale,z*scale,light['power']*scale**2,light['size']*scale,tuple(light['color']))
  if 'size_y' in light:
   bpy.context.object.data.shape='RECTANGLE';bpy.context.object.data.size_y=light['size_y']*scale
else:
 area('large soft key',-25*scale,35*scale,35*scale,35000*scale**2,30*scale,(.86,.93,1))
 area('warm edge',28*scale,10*scale,-10*scale,25000*scale**2,22*scale,(1,.73,.43))
 area('front fill',12*scale,-4*scale,30*scale,6000*scale**2,25*scale,(.6,.8,1))
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=48;sc.cycles.use_denoising=True
sc.render.resolution_x=s['size'][0];sc.render.resolution_y=s['size'][1];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.45,.52,.65,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=recipe.get('world_strength',.35)
sc.view_settings.view_transform='AgX';sc.render.filepath=str(out)
bpy.ops.wm.save_as_mainfile(filepath=str(out.with_suffix('.blend')))
bpy.ops.render.render(write_still=True)
(out.with_suffix('.json')).write_text(json.dumps({'backend':'Blender Cycles CPU','version':bpy.app.version_string,'scene':str(p),'atom_count':len(s['positions']),'camera_ortho_scale':cam.data.ortho_scale,'style':style,'recipe':recipe,'note':'Art-directed display materials, not measured optical properties'},indent=2))
