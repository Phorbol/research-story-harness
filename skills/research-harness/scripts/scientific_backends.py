"""Structure, trace and graphical-abstract backends plus shared typography."""
import hashlib
import importlib.util
import json
from pathlib import Path

ADVANCED_KINDS = {"catalyst_surface", "structure3d", "series", "toc", "schematic", "summary", "recipe", "energy_network"}


def local_module(name):
    spec=importlib.util.spec_from_file_location('research_'+name,Path(__file__).with_name(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def surface_backend():
    path=Path(__file__).with_name('surface_backend.py')
    spec=importlib.util.spec_from_file_location('research_surface_backend',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def structure_module():
    here = Path(__file__).resolve()
    candidates = [here.with_name("structure_render.py"), here.parents[2]/"ovito-structure/scripts/structure_render.py"]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("research_structure_renderer", path)
            module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            return module
    raise ImportError("Install ovito-structure beside research-harness, or copy its structure_render.py into project scripts/")


def narrative_module():
    path=Path(__file__).with_name("narrative_scene.py")
    spec=importlib.util.spec_from_file_location("narrative_scene_backend",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_advanced(fig, project, root, maps, data, require, add, resolve):
    fid, kind, mapping = fig["id"], fig["kind"], fig.get("mapping", {})
    if kind == 'energy_network':
        local_module('energy_network').validate(fig,project,maps,data,require,add)
    elif kind == 'recipe':
        source=maps['sources'].get(mapping.get('recipe_source_id'))
        require(bool(source and source.get('path','').endswith('.py')),'recipe_source','Project-local reviewed Python rendering program required',fid)
        if source:require(resolve(root,source['path']).is_file(),'recipe_program','Rendering recipe file exists',fid)
        require(bool(fig.get('dataset_id')),'recipe_dataset','Quantitative recipe binds an explicit dataset',fid)
        if fig.get('dataset_id') in maps['datasets']:require(bool(maps['datasets'][fig['dataset_id']].get('uncertainty')),'recipe_uncertainty','Dataset uncertainty or its absence must be explicit',fid)
        add('recipe_semantics','unknown','Project code, statistical/physical transformation and reader task require source review; execution is not scientific proof',fid)
    elif kind == "summary":
        ds=maps["datasets"][fig["dataset_id"]];rows=data[fig["dataset_id"]]
        value=mapping["value"];require(ds["columns"].get(value)=="number","summary_values","Summary values bind numeric source columns",fid)
        require(bool(ds.get("uncertainty")),"summary_uncertainty","Declare SD/SE/CI or not-applicable counts",fid)
        require(all(r[value] is not None for r in rows),"summary_completeness","No implicit omitted summary",fid)
        if mapping.get("error"):
            error=mapping["error"];require(all(r[error] is not None and r[error]>=0 for r in rows),"summary_errors","Uncertainty bars are explicit, finite and nonnegative",fid)
        if mapping.get("xscale")=="log":require(all(r[value]>0 for r in rows),"summary_log","Logarithmic count values must be positive",fid)
    elif kind == "schematic" or (kind == "toc" and mapping.get("scene_source_id")):
        source=maps["sources"].get(mapping.get("scene_source_id"))
        require(bool(source and source.get("path")),"schematic_source","Source-bound editable scene required",fid)
        if source:
            scene=json.loads(resolve(root,source["path"]).read_text())
            errors=narrative_module().check_scene(scene,root)
            require(not errors,"schematic_semantics","; ".join(errors) or "Typed topology, object bindings, source and schematic scope resolve",fid)
    elif kind == "catalyst_surface":
        surface_backend().validate(fig,project,root,require,add)
    elif kind == "structure3d":
        source = maps["sources"].get(mapping.get("source_id"))
        require(bool(source and source.get("path")), "structure_source", "Actual structure source required", fid)
        if source and source.get("path"):
            scene = structure_module().structure_scene(resolve(root,source["path"]),mapping)
            require(bool(scene["particles"]),"structure_selection","Nonempty source-bound selection",fid)
            require(all(len(v.get("direction",[]))==3 and len(v.get("up",[]))==3 for v in fig["visual"].get("views",[])),
                    "structure_camera","Explicit direction and up vectors per view",fid)
            require(bool(fig["visual"].get("views")),"structure_views","One or more actual 3D views required",fid)
            if any(len(s["occupancy"])>1 for s in scene["source_sites"]):
                require(bool(mapping.get("occupancy_note")),"occupancy_disclosure","Mixed-site color meaning and fractions must be disclosed",fid)
            add("structure_visibility","unknown","Selection checked; camera occlusion and scientifically adequate context still need visual review",fid)
    elif kind == "series":
        ds=maps["datasets"][fig["dataset_id"]];rows=data[fig["dataset_id"]]
        require(bool(mapping.get("series")),"trace_series","Explicit source columns for each series",fid)
        for item in mapping.get("series",[]):
            x,y=item["x"],item["y"]
            require(ds["columns"].get(x)==ds["columns"].get(y)=="number","trace_numeric","Axes bind numeric columns",fid)
            missing=[r for r in rows if r[x] is None or r[y] is None]
            require(not missing or (mapping.get("missing_policy")=="omit_blank_xy_pairs" and all(r[x] is None and r[y] is None for r in missing)),
                    "trace_completeness","Blank pairs may be omitted only with an explicit policy; unmatched values fail",fid)
            for axis,col in [("x",x),("y",y)]:
                if axis+"_limits" in fig["visual"]:
                    lo,hi=fig["visual"][axis+"_limits"]
                    require(lo<hi and all(lo<=r[col]<=hi for r in rows if r[col] is not None),"trace_visible_values","No silently clipped observations",fid)
    elif kind == "toc":
        add("legacy_toc_template","unknown","Legacy MatterGen-specific four-block template; new TOCs use scene_source_id",fid)
        blocks=mapping.get("blocks",[])
        require(mapping.get("layout") in {"linear","evidence_hub","comparison"},"toc_layout","Supported narrative layout",fid)
        require(len(blocks)==4 and len({b["id"] for b in blocks})==4,"toc_blocks","Four individually bound narrative blocks",fid)
        for b in blocks:
            require(bool(b.get("title")) and bool(b.get("body")) and bool(b.get("claim_ids")),"toc_argument","Each block has a scoped claim and text",b["id"])
            require(all(c in maps["claims"] for c in b.get("claim_ids",[])),"toc_claim_binding","Claims resolve",b["id"])
            for ref in b.get("figure_ids",[]):
                require(ref in maps["figures"] and maps["figures"][ref]["kind"] in {"structure3d","catalyst_surface","series"},"toc_asset_binding","Only actual structures/traces may be embedded",b["id"])
        ids={b["id"] for b in blocks}
        for edge in mapping.get("links",[]):
            require(edge["from"] in ids and edge["to"] in ids and edge.get("meaning") in {"workflow","comparison","evidence"},
                    "toc_relation","Typed narrative links, not unqualified causality",fid)
        require(bool(mapping.get("boundary")),"toc_boundary","Contribution boundaries remain visible",fid)


def text(ax,x,y,value,role="body",**kwargs):
    artist=ax.text(x,y,value,**kwargs);artist._research_role=role
    return artist


def structure_asset(spec,project,root,view):
    import importlib.metadata
    module=structure_module();sources={s["id"]:s for s in project["sources"]}
    mapping=dict(spec["mapping"])
    palette=project.get("semantic_colors",{}).get("element",{})
    mapping["element_colors"]={**palette,**mapping.get("element_colors",{})}
    scene=module.structure_scene(Path(root)/sources[mapping["source_id"]]["path"],mapping)
    key={"scene":scene,"view":view,"ovito":importlib.metadata.version("ovito"),"pixels":[1000,800],"quality":"final", "renderer_revision":2}
    token=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest()
    folder=Path(root)/".structure-cache";folder.mkdir(exist_ok=True)
    image=folder/(token+".png");record=folder/(token+".json")
    if not image.is_file() or not record.is_file():
        metadata=module.render_ovito(scene,image,view,(1000,800),"final")
        scene["render"]=metadata
        record.write_text(json.dumps(scene,indent=2)+"\n")
    return image,json.loads(record.read_text())


def draw_structure(ax,spec,project,root,view,bind,object_id):
    import matplotlib.image as mpimg
    path,scene=structure_asset(spec,project,root,view)
    bind(ax.imshow(mpimg.imread(path)),object_id)
    ax.set_axis_off()
    return scene


def draw_trace(ax,spec,project,root,load_data,bind,compact=False):
    datasets={d["id"]:d for d in project["datasets"]}
    ds=datasets[spec["dataset_id"]];rows=load_data(ds,root)
    palette=project.get("semantic_colors",{}).get("series",["#1D6B78","#D29136","#6370B2","#A35470"])
    for i,item in enumerate(spec["mapping"]["series"]):
        selected=[r for r in rows if r[item["x"]] is not None and r[item["y"]] is not None]
        line=ax.plot([r[item["x"]] for r in selected],[r[item["y"]] for r in selected],
                     color=palette[i%len(palette)],linewidth=.8 if compact else 1.1,label=item["label"])[0]
        bind(line,spec["id"]+":trace:"+item["id"]+(":compact" if compact else ""))
    ax.set_xlabel(spec["visual"]["xlabel"]);ax.set_ylabel(spec["visual"]["ylabel"])
    ax.spines[["top","right"]].set_visible(False)
    if len(spec["mapping"]["series"])>1 and not compact:
        ax.legend(frameon=False,loc="best",handlelength=1.2,labelspacing=.25)
    if not compact:
        for axis in ("x","y"):
            limits=spec["visual"].get(axis+"_limits")
            if limits:getattr(ax,"set_"+axis+"lim")(limits)
    if compact:
        ax.set_axis_off()
        text(ax,0,1.02,"XRD: raw scan" if len(spec["mapping"]["series"])==1 else "Indentation: 4 traces",role="legend",transform=ax.transAxes,ha="left",va="bottom")


def render_advanced(spec,project,root,fig,ax,bind,out,load_data):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fid=spec["id"];kind=spec["kind"];extras=[]
    theme=spec["visual"].get("theme",{})
    if kind=='energy_network':
        return local_module('energy_network').render(spec,project,root,fig,ax,bind,out,load_data)
    if kind=='recipe':
        source=next(s for s in project['sources'] if s['id']==spec['mapping']['recipe_source_id'])
        path=(Path(root)/source['path']).resolve()
        if not path.is_relative_to(Path(root).resolve()):raise ValueError('Recipe escapes project')
        loader=importlib.util.spec_from_file_location('project_figure_recipe',path);module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
        module.render_figure(spec,project,Path(root),fig,ax,bind,load_data)
        return []
    if kind=="summary":
        ds=next(d for d in project["datasets"] if d["id"]==spec["dataset_id"]);rows=load_data(ds,root);m=spec["mapping"];ys=list(range(len(rows)));values=[r[m["value"]] for r in rows]
        color=spec["visual"].get("colors",["#148592"])[0]
        if m.get('geometry')=='bar':
            errors=[r[m['error']] for r in rows] if m.get('error') else None
            bars=ax.bar(ys,values,yerr=errors,width=.68,color=color,edgecolor=spec['visual'].get('edgecolor','#222222'),linewidth=.7,capsize=3,error_kw={'elinewidth':1})
            for bar,row in zip(bars,rows):bind(bar,fid+':value:'+str(row[ds['row_key']]))
            ax.set_xticks(ys,[r[m['label']] for r in rows]);ax.set_ylabel(spec['visual']['ylabel']);ax.set_ylim(bottom=0)
            if spec['visual'].get('y_limits'):ax.set_ylim(spec['visual']['y_limits'])
            ax.spines[['top','right']].set_visible(False);ax.tick_params(direction='out');ax.margins(x=.08)
            dest=Path(out)/(fid+'.data-map.json');dest.write_text(json.dumps({'dataset_id':ds['id'],'rows':[{'row_id':r[ds['row_key']],'value':r[m['value']],'error':r[m['error']] if m.get('error') else None} for r in rows],'uncertainty':ds['uncertainty'],'units':ds['units']},indent=2)+'\n');return [dest]
        if m.get("xscale")=="log":
            ax.set_xscale("log");base=min(values)*.55
            for i,value in enumerate(values):bind(ax.plot([base,value],[i,i],color="#D6E1E5",linewidth=3)[0],fid+":count:"+str(i))
        errors=[r[m["error"]] for r in rows] if m.get("error") else None
        container=ax.errorbar(values,ys,xerr=errors,fmt="o",color=color,ecolor=color,capsize=3,markersize=5,elinewidth=1.1)
        bind(container.lines[0],fid+":values");ax.set_yticks(ys,[r[m["label"]] for r in rows]);ax.invert_yaxis();ax.margins(y=.3,x=.12);ax.set_xlabel(spec["visual"]["xlabel"])
        for spine in ["top","right","left"]:ax.spines[spine].set_visible(False)
        ax.tick_params(axis="y",length=0);ax.grid(axis="x",color="#E9EFF2",linewidth=.6);ax.set_axisbelow(True)
        for i,row in enumerate(rows):
            label=format(row[m["value"]],m.get("format",",.0f"))
            if errors is not None:label+=" ± "+format(errors[i],m.get("format",".2f"))
            text(ax,1.02,i,label,role="legend",transform=ax.get_yaxis_transform(),ha="left")
        dest=Path(out)/(fid+".data-map.json");dest.write_text(json.dumps({"dataset_id":ds["id"],"rows":[{"row_id":r[ds["row_key"]],"value":r[m["value"]],"error":r[m["error"]] if m.get("error") else None} for r in rows],"uncertainty":ds["uncertainty"],"units":ds["units"]},indent=2)+"\n");return [dest]
    if kind=="schematic" or (kind=="toc" and spec["mapping"].get("scene_source_id")):
        source=next(s for s in project["sources"] if s["id"]==spec["mapping"]["scene_source_id"])
        scene=json.loads((Path(root)/source["path"]).read_text())
        objects=narrative_module().draw_scene(scene,root,ax,bind,fid)
        dest=Path(out)/(fid+".narrative-map.json");dest.write_text(json.dumps({"objects":objects,"connections":scene.get("connections",[]),"geometry_basis":scene["geometry_basis"],"scope_note":scene["scope_note"]},indent=2)+"\n");return [dest]
    if kind=="series":
        draw_trace(ax,spec,project,root,load_data,bind)
        ds=next(d for d in project["datasets"] if d["id"]==spec["dataset_id"])
        rows=load_data(ds,root);record=[]
        for item in spec["mapping"]["series"]:
            used=[r[ds["row_key"]] for r in rows if r[item["x"]] is not None and r[item["y"]] is not None]
            record.append({"series_id":item["id"],"x_column":item["x"],"y_column":item["y"],"source_row_ids_in_plot_order":used,
                           "blank_xy_pairs_omitted":len(rows)-len(used),"policy":spec["mapping"].get("missing_policy","reject")})
        dest=Path(out)/(fid+".data-map.json");dest.write_text(json.dumps(record,indent=2)+"\n");extras.append(dest)
        return extras
    if kind=="catalyst_surface":
        return surface_backend().render(spec,project,root,ax,bind,out)
    if kind=="structure3d":
        ax.set_axis_off();views=spec["visual"]["views"];count=len(views)
        scenes=[]
        for i,view in enumerate(views):
            child=ax.inset_axes([i/count,.15,.98/count,.78])
            scenes.append(draw_structure(child,spec,project,root,view,bind,fid+":raster:"+str(i)))
            text(ax,(i+.5)/count,.12,view.get("label",view["name"]),ha="center",va="top",role="note")
        note=spec["mapping"].get("occupancy_note", "Actual source coordinates; displayed bonds are distance neighbours.")
        text(ax,.5,.01,note,ha="center",va="bottom",role="note",wrap=True)
        dest=Path(out)/(fid+".scene.json");dest.write_text(json.dumps(scenes,indent=2)+"\n");extras.append(dest)
        return extras
    # Compatibility only: the old four-block MatterGen example is isolated.
    return local_module('legacy_mattergen_toc').render(spec,project,root,fig,ax,bind,out,load_data,
                (text,draw_trace,draw_structure,surface_backend))


def style_figure(fig,profile,base_size):
    from matplotlib.text import Text
    from matplotlib.axes import Axes
    family=profile["font_family"]
    ratio=base_size/profile["roles"]["body"]["size_pt"]
    for ax in fig.findobj(Axes):
        for axis in (ax.xaxis,ax.yaxis):
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                tick.label1._research_role="tick";tick.label2._research_role="tick"
        for label in (ax.xaxis.label,ax.yaxis.label):label._research_role="axis"
        for title in (ax.title,ax._left_title,ax._right_title):title._research_role="title"
        if ax.get_legend():
            for label in ax.get_legend().get_texts():label._research_role="legend"
    for t in fig.findobj(Text):
        role=getattr(t,"_research_role","body");token=profile["roles"].get(role,profile["roles"]["body"])
        t.set_fontfamily(token.get("font_family",family));t.set_fontsize(token["size_pt"]*ratio)
        if token.get("font_file"):t.get_fontproperties().set_file(token["font_file"])
        t.set_fontweight(token["weight"]);t.set_fontstyle(token["style"])
        t.set_color(getattr(t,"_research_color",token.get("color",profile["text_color"])))


def typography_audit(fig,profile,base_size,fid,bind):
    from matplotlib.text import Text
    from matplotlib import font_manager
    from matplotlib.colors import to_rgba
    from matplotlib.ft2font import FT2Font
    records=[];ratio=base_size/profile["roles"]["body"]["size_pt"]
    for i,t in enumerate(fig.findobj(Text)):
        if not t.get_visible() or not t.get_text():continue
        role=getattr(t,"_research_role","body");expected=profile["roles"].get(role,profile["roles"]["body"])
        if not t.get_gid():t.set_gid(fid+":text:"+str(i))
        resolved=font_manager.findfont(t.get_fontproperties(),fallback_to_default=False)
        ok=t.get_fontfamily()==[expected.get("font_family",profile["font_family"])] and t.get_fontweight()==expected["weight"] and t.get_fontstyle()==expected["style"] and abs(t.get_fontsize()-expected["size_pt"]*ratio)<1e-6 and to_rgba(t.get_color())==to_rgba(getattr(t,"_research_color",expected.get("color",profile["text_color"])))
        # Raw Unicode glyphs must exist in the resolved text font. MathText has a separate parser/fontset.
        missing=[] if "$" in t.get_text() else sorted({ch for ch in t.get_text() if not ch.isspace() and not FT2Font(resolved).get_char_index(ord(ch))})
        # An explicit misspelt role must not silently pass as body text.
        role_known=role in profile["roles"]
        ok=ok and not missing and role_known
        if expected.get("font_file"):ok=ok and Path(resolved).resolve()==Path(expected["font_file"]).resolve()
        records.append({"missing_glyphs":missing,"role_known":role_known,"id":t.get_gid(),"text":t.get_text(),"role":role,"family":t.get_fontfamily(),"size_pt":t.get_fontsize(),
                        "weight":t.get_fontweight(),"style":t.get_fontstyle(),"color":t.get_color(),"resolved_font":Path(resolved).name,"font_file_override":bool(expected.get("font_file")),"passed":ok})
    return {"passed":all(r["passed"] for r in records),"records":records,
            "scope":"Actual Matplotlib text attributes and font availability. Math semantic correctness and visual collisions still need review."}
