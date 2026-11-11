"""Harness adapter for source-bound adsorbate/surface state sequences."""
import hashlib,importlib.util,json
from pathlib import Path


def renderer_path():
    here=Path(__file__).resolve()
    for path in [here.with_name('surface_render.py'),here.parents[2]/'ovito-structure/scripts/surface_render.py']:
        if path.is_file():return path
    raise ImportError('Install updated ovito-structure or copy surface_render.py into project scripts/')


def renderer_module():
    spec=importlib.util.spec_from_file_location('research_surface_renderer',renderer_path())
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def prepare(spec,project,root,render=False):
    """Registered inputs and explicit identity; checking creates no images or metadata files."""
    from matplotlib.colors import to_rgb
    root=Path(root).resolve();sources={s['id']:s for s in project['sources']}
    source=sources.get(spec['mapping'].get('job_source_id'))
    if not source or not source.get('path'):raise ValueError('Catalyst surface needs mapping.job_source_id')
    path=(root/source['path']).resolve()
    if not path.is_relative_to(root):raise ValueError('Surface job escapes project')
    job=json.loads(path.read_text());registered={(root/s['path']).resolve()for s in project['sources']if s.get('path')}
    files=[(path.parent/s['path']).resolve()for s in job['states']]
    if any(not p.is_relative_to(root) or p not in registered for p in files):
        raise ValueError('Every surface state must be a registered project source file')
    colors={e:list(to_rgb(c))for e,c in project.get('semantic_colors',{}).get('element',{}).items()}
    colors.update(job.get('style',{}).get('colors',{}));overrides={'style':{'colors':colors}}
    renderer=renderer_module()
    if not render:
        meta=renderer.render_surface_job(path,verify_only=True,write_outputs=False,project_root=root,job_overrides=overrides)
    else:
        import importlib.metadata
        key={'job':job,'files':[hashlib.sha256(p.read_bytes()).hexdigest()for p in files],
             'renderer':hashlib.sha256(renderer_path().read_bytes()).hexdigest(),
             'ovito':importlib.metadata.version('ovito'),'overrides':overrides}
        token=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();folder=root/'.surface-cache'/token
        record=folder/'metadata.json'
        meta=json.loads(record.read_text())if record.is_file()else None
        if meta is not None and not all((folder/s['file']).is_file()for s in meta['states'].values()):meta=None
        if meta is None:
            meta=renderer.render_surface_job(path,output_dir=folder,project_root=root,job_overrides=overrides)
            record.write_text(json.dumps(meta,indent=2)+'\n')
        meta['asset_directory']=str(folder.relative_to(root))
    wanted=spec['mapping'].get('states',list(meta['states']))
    if not wanted or any(s not in meta['states']for s in wanted):raise ValueError('Unknown/empty surface state selection')
    labels=spec['mapping'].get('atom_labels',{})
    if any(str(i)not in meta['states'][wanted[0]]['atom_pixels']for i in labels):
        raise ValueError('Atom labels must refer to declared source focus atoms')
    return meta,wanted


def validate(spec,project,root,require,add):
    meta,states=prepare(spec,project,root)
    require(meta['source_coordinates_unchanged'],'surface_coordinates','Source coordinates preserved; display transforms recorded separately',spec['id'])
    require(meta['classification']in {'source tags','explicit adsorbate_indices'},'surface_identity','Source tags or explicit indices identify substrate and adsorbate',spec['id'])
    require(bool(meta['substrate_patch_atoms'])and bool(meta['adsorbate_indices']),'surface_components','Nonempty substrate patch and single-copy adsorbate',spec['id'])
    require(all(len(meta['states'][s]['display_source_indices'])==meta['states'][s]['display_atoms']for s in states),
            'surface_image_mapping','All display atoms retain source identity and substrate lattice image',spec['id'])
    add('surface_visibility','unknown','Shared camera and source identities checked; focus occlusion, pixel registration and chemical interpretation require visual/source review',spec['id'])


def text(ax,x,y,value,role='body',**kw):
    t=ax.text(x,y,value,**kw);t._research_role=role;return t


def draw_state(ax,spec,root,meta,state,bind,object_id,labels=True):
    import matplotlib.image as mpimg
    from matplotlib import patheffects
    info=meta['states'][state];path=Path(root)/meta['asset_directory']/info['file']
    bind(ax.imshow(mpimg.imread(path)),object_id+':raster:'+state);ax.set_axis_off()
    if labels:
        for atom,label in spec['mapping'].get('atom_labels',{}).items():
            x,y=info['atom_pixels'][str(atom)]
            dx,dy=spec['visual'].get('atom_label_offsets_px',{}).get(str(atom),[0,-35])
            t=text(ax,x+dx,y+dy,label,role='structure_label',ha='center',va='center',zorder=6)
            t._research_color='#182E40';t.set_path_effects([patheffects.withStroke(linewidth=1.4,foreground='white')])
            bind(t,object_id+':source-atom:'+str(atom)+':label:'+state)


def render(spec,project,root,ax,bind,out):
    ax.set_axis_off();meta,states=prepare(spec,project,root,render=True);count=len(states);fid=spec['id']
    titles=spec['visual'].get('state_titles',{});letters=spec['visual'].get('panel_letters',True)
    for i,state in enumerate(states):
        child=ax.inset_axes([i/count,.20,.98/count,.66]);draw_state(child,spec,root,meta,state,bind,fid+':state:'+state)
        title=(chr(97+i)+'  'if letters else'')+titles.get(state,state)
        text(ax,(i+.49)/count,.91,title,ha='center',role='subtitle')
        if spec['visual'].get('show_distances',False):
            rows=[]
            for key,value in meta['states'][state]['distances_A'].items():
                a,b=map(int,key.split()[0].split('-'));symbols=meta['atom_symbols'];rows.append(f'{symbols[a]}–{symbols[b]}  {value:.2f} Å')
            text(ax,(i+.49)/count,.13,'\n'.join(rows),ha='center',role='note',va='top')
    if spec['visual'].get('note'):text(ax,.5,.01,spec['visual']['note'],ha='center',role='note',va='bottom')
    dest=Path(out)/(fid+'.surface.json');dest.write_text(json.dumps(meta,indent=2)+'\n');return [dest]
