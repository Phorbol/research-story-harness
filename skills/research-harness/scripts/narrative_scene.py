"""Editable, source-bound schematic scenes; no measured-data requirement."""
import json
import importlib.util
from pathlib import Path

TYPES={'text','rect','ellipse','polygon','path','line','arrow','image','sphere','shadow'}
RELATIONS={'data_flow','transformation','temporal','comparison','zoom','feedback','energy_cycle','association'}

def layout_module():
    spec=importlib.util.spec_from_file_location('research_scene_layout',Path(__file__).with_name('scene_layout.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def check_scene(scene, root):
    try:
        scene=layout_module().resolve(scene)
        geometry_errors=layout_module().geometry_errors(scene)
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        return ['Scene layout: '+str(exc)]
    errors=[];objects=scene.get('objects',[]);ids=[o.get('id') for o in objects]
    errors.extend(geometry_errors)
    if not objects or any(not i for i in ids) or len(ids)!=len(set(ids)):errors.append('Objects need unique nonempty IDs')
    if scene.get('track')!='explanatory':errors.append('Schematic scene must declare explanatory track')
    if not scene.get('provenance',{}).get('locator'):errors.append('Reference or concept source locator required')
    if scene.get('geometry_basis') not in {'conceptual','source_coordinates','illustrative_reconstruction'}:errors.append('Declare geometry basis')
    if not scene.get('scope_note'):errors.append('Explicit schematic scope required')
    for o in objects:
        if o.get('type') not in TYPES:errors.append('Unsupported primitive '+str(o.get('type')))
        if not o.get('semantic_id'):errors.append('Object '+str(o.get('id'))+' needs a semantic binding')
        if o.get('type')=='image':
            p=(Path(root)/o['path']).resolve()
            if not p.is_relative_to(Path(root).resolve()) or not p.is_file():errors.append('Missing/escaping image asset')
        if o.get('color_role') and o['color_role'] not in scene.get('palette',{}):errors.append('Undefined color role')
    for e in scene.get('connections',[]):
        if e.get('from') not in ids or e.get('to') not in ids:errors.append('Connection has a missing endpoint')
        if e.get('meaning') not in RELATIONS:errors.append('Connection needs an explicit relation meaning')
        if e.get('basis') not in {'source_schematic','observed','computed','hypothesis','conceptual'}:errors.append('Connection needs evidence basis')
    edgeids=[e.get('id') for e in scene.get('connections',[]) if 'draw' in e]
    if any(not i for i in edgeids) or len(edgeids)!=len(set(edgeids)):errors.append('Drawn connections need unique IDs')
    return errors


def draw_scene(scene,root,ax,bind,fid):
    import numpy as np
    from matplotlib.colors import to_rgb
    import matplotlib.image as mpimg
    from matplotlib.patches import Rectangle,Ellipse,Polygon,PathPatch,FancyArrowPatch,FancyBboxPatch
    from matplotlib.path import Path as MPath
    scene=layout_module().resolve(scene)
    w,h=scene['canvas'];ax.set(xlim=(0,w),ylim=(0,h));ax.set_aspect('equal');ax.set_axis_off()
    mapping=[]
    for o in sorted(scene['objects'],key=lambda x:x.get('z',2)):
        k=o['type'];c=scene.get('palette',{}).get(o.get('color_role'),o.get('color','#263D4C'))
        stroke=o.get('stroke','none');lw=o.get('lw',.8);alpha=o.get('alpha',1);z=o.get('z',2)
        linestyle=o.get('linestyle','-')
        if isinstance(linestyle,list):linestyle=(linestyle[0],tuple(linestyle[1]))
        if k=='text':
            a=ax.text(*o['xy'],o['text'],ha=o.get('ha','left'),va=o.get('va','center'),rotation=o.get('rotation',0),rotation_mode=o.get('rotation_mode','default'),zorder=z)
            a._research_role=o.get('role','body')
            if o.get('color_role'):a._research_color=c;a._research_color_role=o['color_role']
        elif k=='rect':
            x,y,b,h2=o['box'];r=o.get('rounding',0)
            a=FancyBboxPatch((x,y),b,h2,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=c,edgecolor=stroke,linewidth=lw,linestyle=linestyle,alpha=alpha,zorder=z)
            ax.add_patch(a)
        elif k=='ellipse':
            x,y,b,h2=o['box'];a=Ellipse((x+b/2,y+h2/2),b,h2,facecolor=c,edgecolor=stroke,linewidth=lw,linestyle=linestyle,alpha=alpha,zorder=z);ax.add_patch(a)
        elif k=='polygon':
            a=Polygon(o['points'],closed=True,facecolor=c,edgecolor=stroke,linewidth=lw,linestyle=linestyle,alpha=alpha,zorder=z);ax.add_patch(a)
        elif k=='path':
            path=MPath(o['points'],o['codes']);a=PathPatch(path,facecolor=c,edgecolor=stroke,linewidth=lw,linestyle=linestyle,alpha=alpha,zorder=z);ax.add_patch(a)
        elif k=='line':
            pts=o['points'];a=ax.plot([p[0] for p in pts],[p[1] for p in pts],color=c,linewidth=lw,linestyle=linestyle,alpha=alpha,zorder=z)[0]
        elif k=='arrow':
            route={'path':MPath(o['route_points'])} if o.get('route_points') else dict(posA=o['start'],posB=o['end'],connectionstyle=o.get('connectionstyle','arc3,rad=0'),shrinkA=o.get('shrink',0),shrinkB=o.get('shrink',0))
            a=FancyArrowPatch(**route,arrowstyle=o.get('arrowstyle','-|>'),mutation_scale=o.get('head',9),color=c,linewidth=lw,linestyle=linestyle,zorder=z);ax.add_patch(a)
            a._research_connection=o.get('_connection')
        elif k in {'sphere','shadow'}:
            n=192;v=np.linspace(-1,1,n);xx,yy=np.meshgrid(v,v[::-1]);r2=xx*xx+yy*yy;zz=np.sqrt(np.maximum(0,1-r2))
            if k=='shadow':
                rgba=np.zeros((n,n,4));rgba[:,:,:3]=to_rgb(c)
                rgba[:,:,3]=alpha*np.maximum(0,np.exp(-o.get('falloff',3)*r2)-np.exp(-o.get('falloff',3)))/(1-np.exp(-o.get('falloff',3)))
                rgba[:,:,3]*=(r2<=1)
            elif 'material' in o:
                m=o['material'];light=np.array(m.get('light',[-.48,.64,.72]),dtype=float);light/=np.linalg.norm(light)
                diff=np.maximum(0,xx*light[0]+yy*light[1]+zz*light[2])
                half=light+np.array([0,0,1]);half/=np.linalg.norm(half)
                spec=np.maximum(0,xx*half[0]+yy*half[1]+zz*half[2])**m.get('shininess',22)
                dark=np.array(to_rgb(m.get('shadow_color',c)));bright=np.array(to_rgb(m.get('light_color',c)))
                t=np.clip(m.get('ambient',.12)+(1-m.get('ambient',.12))*diff,0,1)
                if m.get('shading')=='linear':t=(1-xx)/2;spec=np.zeros_like(spec)
                rgb=dark[None,None,:]*(1-t[:,:,None])+bright[None,None,:]*t[:,:,None]
                rgb+=m.get('specular',.22)*spec[:,:,None]*(1-rgb)
                rgba=np.ones((n,n,4));rgba[:,:,:3]=np.clip(rgb,0,1);rgba[:,:,3]=(r2<=1)*alpha
            else:
                # Preserve existing scenes unless they explicitly opt into a material.
                light=np.array([-.48,.64,.72]);light/=np.linalg.norm(light);diff=np.maximum(0,xx*light[0]+yy*light[1]+zz*light[2]);gloss=np.maximum(0,zz*diff)**18
                albedo=np.array(to_rgb(c));rgba=np.ones((n,n,4));rgba[:,:,:3]=np.clip(albedo[None,None,:]*(.88+.12*diff[:,:,None])+.16*gloss[:,:,None],0,1);rgba[:,:,3]=(r2<=1)
            x,y,b,h2=o['box'];a=ax.imshow(rgba,extent=[x,x+b,y,y+h2],zorder=z,interpolation='bicubic')
            if stroke!='none':ax.add_patch(Ellipse((x+b/2,y+h2/2),b,h2,facecolor='none',edgecolor=stroke,linewidth=lw,zorder=z+.01))
        else:
            pixels=mpimg.imread(Path(root)/o['path']);extent=o['extent']
            if o.get('fit')=='contain':
                l,r,b,t=extent;ih,iw=pixels.shape[:2];scale=min((r-l)/iw,(t-b)/ih);ww,hh=iw*scale,ih*scale
                extent=[(l+r-ww)/2,(l+r+ww)/2,(b+t-hh)/2,(b+t+hh)/2]
            a=ax.imshow(pixels,extent=extent,zorder=z,interpolation='lanczos')
            if 'ellipse_clip' in o:
                x,y,b,h2=o['ellipse_clip'];clip=Ellipse((x+b/2,y+h2/2),b,h2,transform=ax.transData);a.set_clip_path(clip)
        bind(a,fid+':object:'+o['id'])
        if o.get('gradient') and k in {'rect','ellipse','polygon','path'}:
            # A clipped procedural material layer; the editable boundary stays native.
            g=o['gradient'];bounds=a.get_path().get_extents(a.get_transform()-ax.transData)
            gx,gy=np.meshgrid(np.linspace(0,1,256),np.linspace(1,0,256))
            direction=g.get('direction',[1,0]);t=gx*direction[0]+gy*direction[1]
            t=(t-t.min())/max(float(np.ptp(t)),1e-9)
            stops=g['colors'];pos=np.linspace(0,1,len(stops));rgb=np.array([to_rgb(v) for v in stops])
            pixels=np.stack([np.interp(t,pos,rgb[:,j]) for j in range(3)],axis=-1)
            layer=ax.imshow(pixels,extent=[bounds.x0,bounds.x1,bounds.y0,bounds.y1],zorder=z+.001,alpha=alpha,interpolation='bicubic')
            layer.set_clip_path(a);bind(layer,fid+':object:'+o['id']+':material')
        mapping.append({'id':o['id'],'semantic_id':o['semantic_id'],'type':k,
                        'geometry':{key:o[key] for key in ('box','xy','extent','start','end','route_points') if key in o},
                        'connection':o.get('_connection')})
    return mapping


def text_collisions(fig):
    from matplotlib.text import Text
    fig.canvas.draw();renderer=fig.canvas.get_renderer();texts=[];collisions=[]
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip():texts.append((t,t.get_window_extent(renderer)))
    for i,(a,ra) in enumerate(texts):
        for b,rb in texts[i+1:]:
            # Ignore touching glyph boxes; flag only material 2D intersections.
            x=min(ra.x1,rb.x1)-max(ra.x0,rb.x0);y=min(ra.y1,rb.y1)-max(ra.y0,rb.y0)
            if x>1.5 and y>1.5:collisions.append({'a':a.get_text(),'b':b.get_text(),'overlap_px':[round(x,1),round(y,1)]})
    from matplotlib.patches import FancyArrowPatch
    outside=[];crossings=[];connections=[]
    for t,rect in texts:
        if not fig.bbox.contains(rect.x0,rect.y0) or not fig.bbox.contains(rect.x1,rect.y1):outside.append(t.get_text())
    for arrow in fig.findobj(FancyArrowPatch):
        path=arrow.get_path().transformed(arrow.get_transform())
        # CLOSEPOLY vertices are placeholders, not visible points. Matplotlib's
        # bbox intersection routine can nevertheless intersect the dummy edge.
        # Replace each placeholder with its own subpath's MOVETO before probing.
        if path.codes is not None:
            from matplotlib.path import Path as MPath
            vertices=path.vertices.copy();start=None
            for i,code in enumerate(path.codes):
                if code==MPath.MOVETO:start=vertices[i].copy()
                elif code==MPath.CLOSEPOLY and start is not None:vertices[i]=start
            path=MPath(vertices,path.codes)
        edge=getattr(arrow,'_research_connection',None)
        if edge:connections.append(dict(edge,artist_id=arrow.get_gid(),rendered_path_vertices=path.vertices.tolist()))
        for t,rect in texts:
            if path.intersects_bbox(rect,filled=False):crossings.append({'arrow':arrow.get_gid(),'text':t.get_text()})
    return {'text_pairs_checked':len(texts)*(len(texts)-1)//2,'potential_collisions':collisions,
            'text_outside_page':outside,'arrow_text_intersections':crossings,'anchored_connections':connections,
            'scope':'Rendered text bounds, arrow paths and page bounds. Candidate intersections need inspection; no aesthetic, chemical or 3D-occlusion certification.'}
