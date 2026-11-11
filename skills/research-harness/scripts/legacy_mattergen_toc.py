"""Frozen MatterGen four-block example. Generic graphical abstracts use scene_source_id."""
from pathlib import Path

def render(spec,project,root,fig,ax,bind,out,load_data,helpers):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fid=spec['id'];extras=[];theme=spec['visual'].get('theme',{})
    text,draw_trace,draw_structure,surface_backend=helpers
    # A TOC contains actual structure/trace assets, bound text, and typed links.
    mapping=spec["mapping"];blocks=mapping["blocks"];layout=mapping["layout"]
    figures={f["id"]:f for f in project["figures"]}
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_axis_off()
    if layout=="linear":
        boxes=[[.015,.22,.22,.64],[.267,.22,.22,.64],[.519,.22,.22,.64],[.771,.22,.22,.64]]
    elif layout=="evidence_hub":
        boxes=[[.32,.78,.36,.19],[.015,.23,.27,.48],[.34,.22,.32,.49],[.72,.20,.27,.53]]
    else:
        boxes=[[.015,.85,.97,.12],[.015,.32,.46,.48],[.525,.32,.46,.48],[.015,.13,.97,.14]]
    boxmap={b["id"]:rect for b,rect in zip(blocks,boxes)}
    for i,(block,(x,y,w,h)) in enumerate(zip(blocks,boxes)):
        bind(ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.005,rounding_size="+str(theme.get("rounding",.008)),
             facecolor=theme.get("panel_face","#F5F7FA") if i!=2 else theme.get("focus_face","#EBF2F3"),edgecolor=theme.get("panel_edge","#D5DDE5"),linewidth=theme.get("panel_linewidth",.65),zorder=1)),fid+":block:"+block["id"])
        text(ax,x+.018,y+h-.025,block["title"],role="subtitle",ha="left",va="top",zorder=5)
        body_x=x+.27 if layout=="comparison" and block["id"]=="design" else x+.018
        text(ax,body_x,y+.025,block["body"],role="note",ha="left",va="bottom",zorder=5)
        refs=block.get("figure_ids",[])
        if not refs:
            if h>.4:
                for row,label in enumerate([r"Condition $c$",r"Denoise $A, X, L$","Filter candidates"]):
                    yy=y+h-.19-row*.13
                    text(ax,x+w/2,yy,label,role="body",ha="center",va="center")
                    if row<2:ax.add_patch(FancyArrowPatch((x+w/2,yy-.035),(x+w/2,yy-.09),arrowstyle="-|>",mutation_scale=8,color="#637985",linewidth=.8))
            continue
        if figures[refs[0]]["kind"]in {"structure3d","catalyst_surface"}:
            ref=figures[refs[0]]
            child=ax.inset_axes([x+.005,y+.11,w-.01,max(.06,h-.19)])
            if ref['kind']=='catalyst_surface':
                backend=surface_backend();meta,states=backend.prepare(ref,project,root,render=True)
                chosen=block.get('surface_state',states[0])
                if chosen not in states:raise ValueError('Unknown TOC surface_state')
                backend.draw_state(child,ref,root,meta,chosen,bind,fid+':asset:'+block['id'],labels=False)
            else:draw_structure(child,ref,project,root,ref["visual"]["views"][0],bind,fid+":asset:"+block["id"])
        else:
            for j,refid in enumerate(refs):
                # In the comparison layout evidence uses two horizontally aligned traces.
                if layout=="comparison":
                    rect=[x+.27+j*.34,y+.035,.30,h-.065]
                else:
                    rect=[x+.025,y+.14+j*(h-.22)/len(refs),w-.05,(h-.30)/len(refs)]
                child=ax.inset_axes(rect)
                draw_trace(child,figures[refid],project,root,load_data,bind,compact=True)
    if layout!="comparison":
        for edge in mapping.get("links",[]):
            a=boxmap[edge["from"]];b=boxmap[edge["to"]]
            if layout=="linear":start=(a[0]+a[2]+.003,a[1]+a[3]/2);end=(b[0]-.003,b[1]+b[3]/2)
            else:start=(a[0]+a[2]/2,a[1]);end=(b[0]+b[2]/2,b[1]+b[3]) if a[1]>b[1]+b[3] else (b[0],b[1]+b[3]/2)
            bind(ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=9,color="#637985",linewidth=.8,zorder=0)),fid+":link:"+edge["from"]+":"+edge["to"])
    text(ax,.015,.035,mapping["boundary"],role="note",ha="left",va="bottom")
    text(ax,.015,.005,"Re-analysis and visual-method study of Zeni et al., Nature (2025); no new synthesis or modulus fit.",role="note",ha="left",va="bottom",color="#687481")
    return extras


