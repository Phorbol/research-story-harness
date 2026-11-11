"""Common-reference, source-bound discrete energy paths; no inferred barriers or curves."""
import json
from pathlib import Path


def validate(spec,project,maps,data,require,add):
    fid=spec['id'];m=spec['mapping'];ds=maps['datasets'][spec['dataset_id']];rows=data[ds['id']]
    key=ds['row_key'];value=m['value'];x=m['x'];kind=m['state_kind'];states={r[key]:r for r in rows}
    require(ds['columns'].get(value)==ds['columns'].get(x)=='number','path_numeric','Energy and display order use numeric columns',fid)
    require(bool(ds.get('reference')) and bool(ds.get('energy_type')) and bool(ds.get('uncertainty')),
            'path_reference','Explicit common reference, energy type and uncertainty/absence required',fid)
    require(all(r[value] is not None and r[x] is not None for r in rows),'path_values','Missing states may not silently disappear or become zero',fid)
    require(all(r[kind] in {'intermediate','transition_state'} for r in rows),'path_state_kind','TS identity must be explicit; no guessed peaks',fid)
    paths=m['paths'];ids=[p['id'] for p in paths];edges=set();used=set()
    require(bool(paths) and len(ids)==len(set(ids)),'path_ids','Unique path identities',fid)
    for p in paths:
        seq=p['states'];used.update(seq)
        require(len(seq)>=2 and len(seq)==len(set(seq)) and all(s in states for s in seq),'path_states','Each path uses known unique states; unfold cycles explicitly',p['id'])
        if all(s in states and states[s][x] is not None for s in seq):
            require(all(states[a][x]<states[b][x] for a,b in zip(seq,seq[1:])),'path_order','Increasing discrete progress coordinate',p['id'])
        edges.update(zip(seq,seq[1:]))
    require(used==set(states),'path_coverage','Every selected source row appears; shared states use one identity/value',fid)
    require(used==set(spec['entity_ids']),'path_entities','Displayed state IDs match scientific entities',fid)
    actual={(maps['relations'][r]['from'],maps['relations'][r]['to']) for r in spec['relation_ids']}
    require(edges==actual and all(maps['relations'][r]['type']=='transformation' for r in spec['relation_ids']),
            'path_topology','Drawn path adjacencies match declared transformations',fid)
    if spec['visual'].get('y_limits'):
        lo,hi=spec['visual']['y_limits'];require(lo<hi and all(r[value] is not None and lo<=r[value]<=hi for r in rows),'path_visible_values','All selected energies stay in axis range',fid)
    add('path_physics','unknown','Common-reference consistency, state/TS assignments and chemical mechanism require original-source review',fid)


def render(spec,project,root,fig,ax,bind,out,load_data):
    ds=next(d for d in project['datasets'] if d['id']==spec['dataset_id']);rows=load_data(ds,root)
    m=spec['mapping'];v=spec['visual'];fid=spec['id'];key=ds['row_key'];states={r[key]:r for r in rows}
    value,x,kind=m['value'],m['x'],m['state_kind'];half=v.get('platform_half_width',.14)
    colors=v.get('colors',['#286AA6','#B56332','#3E8C82']);shown=set();edges=[]
    ax.axhline(0,color='#C8CED2',linewidth=.55,zorder=0)
    for i,path in enumerate(m['paths']):
        color=colors[i%len(colors)];line=path.get('linestyle',['-','--',':','-.'][i%4]);seq=path['states']
        for a,b in zip(seq,seq[1:]):
            ra,rb=states[a],states[b]
            if rb[x]-ra[x]<=2*half:raise ValueError('Energy platforms overlap; reduce platform_half_width or increase display spacing')
            artist=ax.plot([ra[x]+half,rb[x]-half],[ra[value],rb[value]],color=color,linewidth=.85,linestyle=line,zorder=1)[0]
            bind(artist,fid+':path:'+path['id']+':'+a+':'+b);edges.append({'path':path['id'],'from':a,'to':b})
        # Legend line style redundantly encodes path identity.
        ax.plot([],[],color=color,linestyle=line,linewidth=1.3,label=path['label'])
        for sid in seq:
            if sid in shown:continue
            shown.add(sid);r=states[sid]
            shared=sum(sid in p['states'] for p in m['paths'])>1;c='#283846' if shared else color
            bind(ax.plot([r[x]-half,r[x]+half],[r[value],r[value]],color=c,linewidth=1.7,zorder=3)[0],fid+':state:'+sid)
            if r[kind]=='transition_state':bind(ax.scatter([r[x]],[r[value]],marker='^',s=17,color=c,zorder=4),fid+':ts:'+sid)
            if sid in v.get('label_states',list(states)):
                offset=v.get('state_label_offsets',{}).get(sid,[0,7]);label=r[m.get('label',key)]
                if v.get('show_values'):label+='\n'+format(r[value],v.get('value_format','.2f'))
                t=ax.annotate(label,(r[x],r[value]),xytext=offset,textcoords='offset points',ha='center',va='bottom' if offset[1]>=0 else 'top',color=c)
                t._research_role='note';t._research_color=c;bind(t,fid+':label:'+sid)
    ax.set_ylabel(v.get('ylabel',ds['energy_type']+' ('+ds['units'][value]+')'))
    ax.set_xlabel(v.get('xlabel','Reaction progress (discrete states; not a distance)'))
    ax.set_xticks([]);ax.spines[['top','right','bottom']].set_visible(False)
    ax.margins(x=.06,y=.22)
    if v.get('y_limits'):ax.set_ylim(v['y_limits'])
    legend=ax.legend(frameon=False,loc=v.get('legend_location','best'),fontsize=v['font_size'])
    for t in legend.get_texts():t._research_role='legend'
    dest=Path(out)/(fid+'.data-map.json')
    dest.write_text(json.dumps({'dataset_id':ds['id'],'reference':ds['reference'],'energy_type':ds['energy_type'],
        'uncertainty':ds['uncertainty'],'states':rows,'edges':edges,
        'encoding':'Measured/computed values at discrete states. Straight connecting segments are guides, not sampled PES or kinetic trajectories.'},indent=2)+'\n')
    return [dest]
