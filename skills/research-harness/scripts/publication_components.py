"""Physical-size panel composition and source-bound energy-difference annotations.

These components arrange declared scientific content; they do not infer a story,
kinetics, chemical identity, or aesthetic acceptance.
"""
import math

def stationary_energy_path(ax, states, *, order, unit, positions=None, edges=(),
                           energy='energy', position='x', kind='kind',
                           plateau_width=.16, plateau_kinds=('minimum','intermediate'),
                           guide='smoothstep', open_endpoints=(), color='#2478A5',
                           linewidth=1., linestyle='-', bind=lambda *a:None,
                           prefix='path'):
    """Draw declared stationary energies; guides are not a sampled PES.

    states maps IDs to source records; order declares all states to retain.
    Each record needs energy (finite or None for missing), x and kind
    (minimum|intermediate|transition_state|state). unit is explicit and shared. positions
    may override x for a second medium without changing source energies.
    Only explicitly supplied consecutive edges are drawn. Missing endpoints
    split a path, and an edge cannot jump an intervening missing state.
    plateau_width is a full x-data width, scalar or ID->width mapping; only
    plateau_kinds get platforms. guide is smoothstep, linear, or None.
    open_endpoints marks declared unreconstructed tails, without extending
    the curve or inventing a destination. Returned records include missing
    states and actual export artist IDs; no kind or barrier is inferred.
    """
    if not isinstance(unit,str) or not unit.strip():raise ValueError('Declare the source energy unit')
    order=list(order);edges=list(edges);open_endpoints=set(open_endpoints)
    if not order or len(set(order))!=len(order):raise ValueError('Declare unique ordered source state IDs')
    if guide not in {'smoothstep','linear',None}:raise ValueError('Unknown discrete-state guide')
    records=[];lookup={};ids=[];segments=[]
    for sid in order:
        row=states[sid];y=row[energy];x=positions[sid] if positions is not None else row[position]
        if not math.isfinite(x):raise ValueError('Finite source/layout x required')
        if y is not None and not math.isfinite(y):raise ValueError('Use None for missing energy')
        if row[kind] not in {'minimum','intermediate','transition_state','state'}:raise ValueError('Declare a source state kind')
        if row.get('unit',unit)!=unit:raise ValueError('Mixed energy units require conversion before drawing')
        width=plateau_width.get(sid,0.) if hasattr(plateau_width,'get') else plateau_width
        if not math.isfinite(width) or width<0:raise ValueError('Finite nonnegative platform width required')
        half=width/2 if row[kind] in plateau_kinds else 0.
        record=dict(id=sid,energy=y,x=x,kind=row[kind],unit=unit,missing=y is None,half_width=half,artist_ids=[])
        records.append(record);lookup[sid]=record
    if any(b['x']<=a['x'] for a,b in zip(records,records[1:])):raise ValueError('Layout x must increase in source order')
    adjacent=set(zip(order,order[1:]));seen=set()
    for edge in edges:
        pair=tuple(edge)
        if pair not in adjacent or pair in seen:raise ValueError('Edges must be unique consecutive source-state pairs')
        seen.add(pair)
        a,b=(lookup[s] for s in pair)
        if a['x']+a['half_width']>=b['x']-b['half_width']:raise ValueError('Platforms overlap; reduce widths or spread layout x')
    if not open_endpoints.issubset(lookup):raise ValueError('Unknown open endpoint')
    for sid in open_endpoints:
        if lookup[sid]['missing'] or any(a==sid and not lookup[b]['missing'] for a,b in seen):
            raise ValueError('An open endpoint must be a finite terminal state of a declared segment')
    def tag(artist,name,state_ids):
        aid=prefix+':'+name;artist.set_gid(aid);bind(artist,aid);ids.append(aid)
        for sid in state_ids:lookup[sid]['artist_ids'].append(aid)
    for r in records:
        if r['missing']:continue
        sid,x,y,half=r['id'],r['x'],r['energy'],r['half_width']
        if half:
            tag(ax.plot([x-half,x,x+half],[y,y,y],color=color,lw=linewidth,ls=linestyle)[0],sid+':level',[sid])
        tag(ax.plot([x],[y],marker='o' if sid in open_endpoints else '.',ms=3,
                    mfc='white' if sid in open_endpoints else color,mec=color,
                    linestyle='none',zorder=3)[0],sid+':anchor',[sid])
    if guide is not None:
        for a_id,b_id in edges:
            a,b=lookup[a_id],lookup[b_id]
            if a['missing'] or b['missing']:continue
            # Convex interpolation is bounded by these two exact source levels.
            t=[i/64 for i in range(65)]
            weights=[v*v*(3-2*v) for v in t] if guide=='smoothstep' else t
            left=a['x']+a['half_width'];right=b['x']-b['half_width']
            xx=[left+(right-left)*v for v in t]
            yy=[(1-w)*a['energy']+w*b['energy'] for w in weights]
            tag(ax.plot(xx,yy,color=color,lw=linewidth,ls=linestyle,zorder=2)[0],a_id+'->'+b_id+':guide',[a_id,b_id])
            segments.append([a_id,b_id])
    return dict(source_states=order,states=records,unit=unit,guide=guide,
                segments=segments,open_endpoints=[s for s in order if s in open_endpoints],artist_ids=ids)

def audit_publication_size(pdf_path, target_mm, *, tolerance_mm=.1):
    """Read actual PDF size and extractable text sizes, without visual approval.

    The caller supplies the verified target for this figure's purpose.
    Outlined/raster text is not measured. The PDF is never modified.
    """
    import fitz
    if len(target_mm)!=2 or any(not math.isfinite(v) or v<=0 for v in target_mm):
        raise ValueError('Explicit positive target width and height in mm required')
    if not math.isfinite(tolerance_mm) or tolerance_mm<0:
        raise ValueError('Nonnegative finite size tolerance required')
    pages=[]
    with fitz.open(pdf_path) as doc:
        if not len(doc):raise ValueError('PDF has no pages')
        for n,page in enumerate(doc,1):
            actual=[page.rect.width*25.4/72,page.rect.height*25.4/72]
            scale=min(t/a for t,a in zip(target_mm,actual))
            sizes=[s['size'] for b in page.get_text('dict')['blocks']
                   for line in b.get('lines',[]) for s in line.get('spans',[])
                   if s.get('text','').strip()]
            smallest=min(sizes) if sizes else None
            pages.append(dict(page=n,actual_mm=actual,
                matches_target=all(abs(a-t)<=tolerance_mm for a,t in zip(actual,target_mm)),
                fits_target=all(a<=t+tolerance_mm for a,t in zip(actual,target_mm)),
                scale_to_fit=scale,extractable_text_min_pt=smallest,
                implied_fit_text_min_pt=smallest*scale if smallest is not None else None))
    return dict(target_mm=list(target_mm),pages=pages,
                all_pages_match_target=all(p['matches_target'] for p in pages),
                all_pages_fit_target=all(p['fits_target'] for p in pages),
                visual_acceptance='not_assessed',
                text_scope='Extractable PDF text only; outlined and raster text remain unmeasured')

def save_publication(fig, prefix, *, dpi=600, target_mm=None):
    """Save PDF/SVG/PNG at the figure's physical size, without tight cropping.

    dpi controls rasterized artists and resampled images as well as PNG.
    It cannot add detail to a low-resolution input; inspect embedded image
    resolution in the exported PDF. Text/font policy stays with the caller.
    """
    from pathlib import Path
    import matplotlib as mpl
    if not math.isfinite(dpi) or dpi<=0:raise ValueError('Positive export DPI required')
    if target_mm is not None:
        if len(target_mm)!=2 or any(not math.isfinite(v) or v<=0 for v in target_mm):
            raise ValueError('Explicit positive target width and height in mm required')
        if any(abs(a*25.4-t)>.1 for a,t in zip(fig.get_size_inches(),target_mm)):
            raise ValueError('Working canvas differs from the declared delivery size; recompose before export')
    prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    paths={ext:Path(str(prefix)+'.'+ext) for ext in ('pdf','svg','png')}
    # bbox_inches=None alone inherits savefig.bbox='tight' from rcParams.
    with mpl.rc_context({'savefig.bbox':None}):
        for ext,path in paths.items():fig.savefig(path,dpi=dpi,bbox_inches=None)
    return {ext:str(path) for ext,path in paths.items()}

def panel_grid(fig, primary_ax, *, rows, cols, margins_mm, gap_mm=(8,8), row_weights=None, col_weights=None):
    """Return top-to-bottom, left-to-right axes with equal physical gutters.

    margins_mm = left, right, top, bottom. gap_mm = horizontal, vertical.
    Sizes refer to plotting areas, not text bounding boxes. Use the same axes
    limits explicitly when comparing magnitudes; sharing is not inferred.
    """
    if rows<1 or cols<1:raise ValueError('Positive panel counts required')
    width,height=fig.get_size_inches()*25.4;l,r,t,b=margins_mm;gx,gy=gap_mm
    if not all(math.isfinite(float(v)) and v>=0 for v in [l,r,t,b,gx,gy]):raise ValueError('Finite nonnegative margins/gutters required')
    rw=row_weights or [1]*rows;cw=col_weights or [1]*cols
    if len(rw)!=rows or len(cw)!=cols or any(not math.isfinite(v) or v<=0 for v in rw+cw):raise ValueError('Positive weights matching the panel grid required')
    aw=width-l-r-gx*(cols-1);ah=height-t-b-gy*(rows-1)
    if min(aw,ah)<=0:raise ValueError('Panel grid does not fit the physical page')
    fig.set_layout_engine(None);axes=[];frames=[];top=height-t
    for i in range(rows):
        h=ah*rw[i]/sum(rw);left=l
        for j in range(cols):
            w=aw*cw[j]/sum(cw);frame=[left,top-h,w,h]
            normalized=[frame[0]/width,frame[1]/height,w/width,h/height]
            ax=primary_ax if not axes else fig.add_axes(normalized)
            ax.set_position(normalized);axes.append(ax);frames.append(frame);left+=w+gx
        top-=h+gy
    return axes,frames

def panel_heading(ax,label,title,*,offset_pt=8,bind=lambda *a:None,prefix='panel'):
    """A restrained panel letter and title sharing one baseline."""
    t=ax.annotate(label+'  '+title,(0,1),xycoords='axes fraction',xytext=(0,offset_pt),textcoords='offset points',ha='left',va='bottom')
    t._research_role='panel';bind(t,prefix+':heading');return t

def energy_difference(ax,states,spec,*,energy='energy',position='step',kind='kind',edges=None,bind=lambda *a:None,prefix='gap'):
    """Draw a difference from explicit source states, never a freehand height.

    spec: from, to, semantic (activation|desorption|difference), x (rail lane),
    label_xy (axes-data coordinates), unit, color, optional symbol/precision.
    Activation requires a reported destination TS and a declared adjacent edge.
    Desorption is a state-energy cost, NOT automatically a kinetic barrier.
    Returns state IDs, exact energies/difference and artist identities.
    """
    a,b=spec['from'],spec['to']
    if a not in states or b not in states:raise ValueError('Unknown energy-difference state')
    va,vb=states[a][energy],states[b][energy]
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in [va,vb]):raise ValueError('Energy differences require finite source values')
    semantic=spec['semantic']
    if semantic not in {'activation','desorption','difference'}:raise ValueError('Declare energy-difference semantics')
    if semantic=='activation' and (states[b][kind]!='transition_state' or edges is None or (a,b) not in edges):raise ValueError('Activation annotation requires a reported adjacent TS')
    if semantic=='activation' and vb<va:raise ValueError('Negative forward activation difference requires source review')
    if not spec.get('unit'):raise ValueError('Use the source energy unit explicitly')
    x=spec['x'];color=spec.get('color','#293F4B');ids=[]
    def tag(artist,name):
        id=prefix+':'+name;bind(artist,id);ids.append(id);return artist
    arrow=ax.annotate('',xy=(x,vb),xytext=(x,va),arrowprops=dict(arrowstyle='<->',color=color,lw=.8,mutation_scale=7,shrinkA=0,shrinkB=0))
    tag(arrow.arrow_patch,'span')
    for name,state,y in [('from',states[a],va),('to',states[b],vb)]:
        if spec.get('guides',True):tag(ax.plot([state[position],x],[y,y],color=color,lw=.5,linestyle=(0,(2,2)),alpha=.55,zorder=1)[0],name+'-guide')
        tag(ax.plot([x-.07,x+.07],[y,y],color=color,lw=.8)[0],name+'-cap')
    symbol=spec.get('symbol',r'$\Delta G^{\ddagger}$' if semantic=='activation' else r'$\Delta G_{\mathrm{des}}$' if semantic=='desorption' else r'$\Delta G$')
    label=symbol+' = '+format(vb-va,'.'+str(spec.get('precision',2))+'f')+' '+spec['unit']
    t=ax.text(*spec['label_xy'],label,ha=spec.get('ha','center'),va='center',color=color)
    t._research_role='note';t._research_color=color;tag(t,'label')
    return dict(source_states=[a,b],energies=[va,vb],difference=vb-va,semantic=semantic,artist_ids=ids)
