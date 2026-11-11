#!/usr/bin/env python3
"""Traceable research projects. Validation uses stdlib; rendering uses Matplotlib."""
import argparse
import copy
import csv
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

KINDS = {"paired", "table", "energy", "methods", "structure3d", "catalyst_surface", "toc", "series", "schematic", "summary", "recipe", "energy_network"}
RELATIONS = {"data_flow", "temporal", "transformation", "contact", "contains", "comparison", "hypothesized_causality"}
STATUSES = {"passed", "failed", "unknown", "not_implemented"}
REVIEWS = {"scientific", "reader", "layout", "publication"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def resolve(root, relative):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError("Project asset escapes project directory: " + str(relative))
    return path


def visual_review_consistency(record, root):
    """Reject contradictory optional visual records, never infer visual quality."""
    gate = record.get("visual_gate")
    if gate is None:
        return []  # Legacy records do not claim the new review protocol.
    errors = []
    if not isinstance(gate, dict) or gate.get("version") != 1:
        return ["visual_gate must be a version 1 object"]
    dimensions = gate.get("dimensions", {})
    if not isinstance(dimensions, dict):
        return ["visual_gate dimensions must be an object"]
    for name in ("story", "hierarchy", "aesthetics", "legibility"):
        item = dimensions.get(name, {})
        if not isinstance(item, dict) or item.get("status") not in {"ready", "revise", "not_reviewed"}:
            errors.append("Invalid visual dimension: " + name)
        elif record.get("status") == "passed" and (item["status"] != "ready" or not isinstance(item.get("observation"), str) or not item["observation"].strip()):
            errors.append("Passed visual review requires observed ready dimension: " + name)
    issues = gate.get("issues", [])
    if not isinstance(issues, list):
        return errors + ["visual_gate issues must be a list"]
    for item in issues:
        if not isinstance(item, dict) or item.get("impact") not in {"blocking", "nonblocking"} or item.get("state") not in {"open", "resolved"}:
            errors.append("Visual issues require impact and state")
        elif record.get("status") == "passed" and item["impact"] == "blocking" and item["state"] == "open":
            errors.append("Passed visual review still has open blocking issue: " + str(item.get("id", "unnamed")))
    if record.get("status") == "passed":
        view = gate.get("viewing", {})
        if not isinstance(view, dict) or view.get("inspected") is not True or not isinstance(view.get("context"), str) or not view["context"].strip():
            errors.append("Passed visual review needs actual viewing context")
        paths = gate.get("artifact_paths", [])
        if not isinstance(paths, list) or not paths:
            errors.append("Passed visual review needs identified artifacts")
        else:
            for path in paths:
                try:
                    if not isinstance(path, str) or not resolve(root, path).is_file():
                        errors.append("Visual artifact missing: " + str(path))
                except ValueError as exc:
                    errors.append(str(exc))
    return errors


def pointer(doc, path):
    current = doc
    if not path.startswith("/"):
        raise ValueError("Expected JSON pointer: " + path)
    for token in path[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def set_pointer(doc, path, value):
    parent_path, token = path.rsplit("/", 1)
    parent = pointer(doc, parent_path) if parent_path else doc
    token = token.replace("~1", "/").replace("~0", "~")
    # Existing fields only: avoid silently misspelled edits.
    if isinstance(parent, list):
        parent[int(token)] = value
    else:
        if token not in parent:
            raise ValueError("No existing field at " + path)
        parent[token] = value


def signature(project, root):
    body = {k: v for k, v in project.items() if k not in {"reviews", "revision", "history", "protected"}}
    files = {}
    for group in ("sources", "datasets", "sections"):
        for item in project.get(group, []):
            if item.get("path"):
                path = resolve(root, item["path"])
                files[item["path"]] = digest(path.read_bytes()) if path.is_file() else None
    for field in ("journal_profile","style_profile","story_plan"):
        if project.get(field):
            profile = resolve(root, project[field])
            files[project[field]] = digest(profile.read_bytes()) if profile.is_file() else None
    for program in (Path(root)/"scripts").glob("*.py"):
        files[str(program.relative_to(root))]=digest(program.read_bytes())
    return digest(json.dumps({"spec": body, "files": files}, sort_keys=True, ensure_ascii=False).encode())


def load_data(dataset, root):
    path = resolve(root, dataset["path"])
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if set(dataset["columns"]) - set(reader.fieldnames or []):
            raise ValueError("Missing CSV columns")
        rows = []
        for row in reader:
            parsed = {}
            for col, dtype in dataset["columns"].items():
                value = row[col]
                if value is None:
                    raise ValueError("Incomplete CSV row")
                if value.strip() == "":
                    parsed[col] = None
                elif dtype == "number":
                    parsed[col] = float(value)
                    if not math.isfinite(parsed[col]):
                        raise ValueError("Nonfinite value in " + col)
                elif dtype == "string":
                    parsed[col] = value
                else:
                    raise ValueError("Column type must be string or number")
            rows.append(parsed)
    key = dataset["row_key"]
    keys = [r[key] for r in rows]
    if not rows or None in keys or len(keys) != len(set(keys)):
        raise ValueError("Empty dataset or missing/duplicate row identity")
    return rows


def validate(project, root, export=None):
    checks = []

    def add(name, status, detail, target="project"):
        checks.append(dict(check=name, status=status, target=target, detail=detail))

    def require(ok, name, detail, target="project"):
        add(name, "passed" if ok else "failed", detail, target)

    require(project.get("schema_version") == 1, "schema_version", "Supported version: 1")
    require(bool(project.get("project", {}).get("question")), "research_question", "A research question is required")
    if project.get('story_plan'):
        import importlib.util
        path=Path(__file__).with_name('story.py')
        loader=importlib.util.spec_from_file_location('research_story',path);module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
        plan_path=resolve(root,project['story_plan']);story=module.validate(read_json(plan_path),plan_path.parent,project)
        require(story['checks_passed'],'story_plan','; '.join(story['errors']) or 'Source observations, reader tasks, panel/prose links and declared decisions resolve')
        if story['selected_story'] is None:add('story_choice','unknown','Exploration is valid; the author has not selected a story. Do not imply an accepted manuscript narrative.')
    maps = {}
    for group in ("sources", "datasets", "entities", "relations", "claims", "figures", "sections"):
        items = project.get(group, [])
        if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
            add("collection_shape", "failed", "Expected list of objects", group)
            items = []
        ids = [x.get("id") for x in items]
        valid = all(isinstance(i, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", i) for i in ids)
        require(valid and len(ids) == len(set(str(i) for i in ids)), "identities", "Unique stable IDs", group)
        maps[group] = {x["id"]: x for x in items if isinstance(x.get("id"), str)}

    def refs(values, group, target):
        require(isinstance(values, list) and all(isinstance(x, str) and x in maps[group] for x in values)
                and len(values) == len(set(values)), "references:" + group,
                "All referenced IDs must exist", target)

    for source in maps["sources"].values():
        sid = source["id"]
        kind = source.get("kind")
        require(kind in {"file", "literature", "synthetic"}, "source_kind", str(kind), sid)
        if source.get("path"):
            require(resolve(root, source["path"]).is_file(), "source_file", source["path"], sid)
        else:
            require(kind == "literature" and bool(source.get("citation")) and bool(source.get("locator")),
                    "source_locator", "Nonfile evidence needs citation and locator", sid)
        if kind == "synthetic":
            require(project.get("project", {}).get("synthetic") is True, "synthetic_label", "Synthetic project must be labeled", sid)
        elif source.get("verified") is not True:
            add("source_verification", "unknown", "Existence is not verification of evidence content", sid)
    data = {}
    for ds in maps["datasets"].values():
        did = ds["id"]
        refs([ds.get("source_id")], "sources", did)
        require(bool(ds.get("conditions")), "conditions", "Conditions/statistical population required", did)
        try:
            data[did] = load_data(ds, root)
            add("csv_identity_and_values", "passed", "Typed finite values; unique nonmissing row IDs; blanks preserved", did)
            for col, dtype in ds["columns"].items():
                if dtype == "number":
                    require(bool(ds.get("units", {}).get(col)), "unit:" + col, "Explicit unit or dimensionless", did)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            add("csv_identity_and_values", "failed", str(exc), did)
        if ds.get("transforms"):
            for transform in ds["transforms"]:
                if transform.get("operation")=="xrd_uniform_grid" and did in data:
                    source=maps["sources"][transform["input_source_id"]]
                    lines=resolve(root,source["path"]).read_text().splitlines()
                    start,step,end=map(float,lines[0].split())
                    values=[float(line) for line in lines[1:] if line.strip()]
                    x,y=transform["x_column"],transform["y_column"]
                    ok=len(values)==len(data[did]) and abs(start+step*(len(values)-1)-end)<1e-7
                    ok=ok and all(abs(row[x]-(start+i*step))<1e-9 and row[y]==values[i] for i,row in enumerate(data[did]))
                    require(ok,"analysis_reproduction","XRD header/grid and every source intensity match the derived CSV",did)
                else:
                    add("analysis_reproduction", "not_implemented", "No execution adapter for this transformation", did)
    for entity in maps["entities"].values():
        refs(entity.get("source_ids", []), "sources", entity["id"])
        require(bool(entity.get("label")) and bool(entity.get("kind")), "entity_identity", "Label and kind required", entity["id"])
    for rel in maps["relations"].values():
        refs([rel.get("from"), rel.get("to")], "entities", rel["id"])
        refs(rel.get("source_ids", []), "sources", rel["id"])
        require(bool(rel.get("source_ids")), "relation_evidence", "Every relation needs a source", rel["id"])
        require(rel.get("type") in RELATIONS, "relation_type", "Typed scientific relation", rel["id"])
        require(rel.get("basis") in {"observed", "computed", "hypothesis", "unknown"}, "relation_basis", "Evidence basis is distinct from presentation", rel["id"])
    for claim in maps["claims"].values():
        cid = claim["id"]
        ev = claim.get("evidence_ids", [])
        require(all(i in maps["sources"] or i in maps["datasets"] for i in ev), "claim_evidence_ids", "Evidence IDs resolve", cid)
        require(claim.get("status") in {"supported", "hypothesis", "contested", "unknown"}, "claim_status", "Explicit evidence status", cid)
        require(bool(claim.get("text")) and bool(claim.get("scope")) and bool(claim.get("limitations")), "claim_scope", "Text, scope and limitations required", cid)
        if claim.get("status") == "supported":
            require(bool(ev), "supported_claim_evidence", "Supported claims require evidence", cid)
    if not maps["figures"]:
        add("project_content", "unknown", "No figures; scaffold is not an accepted research project")
    for fig in maps["figures"].values():
        fid, kind = fig["id"], fig.get("kind")
        for field, group in (("claim_ids", "claims"), ("entity_ids", "entities"), ("relation_ids", "relations")):
            refs(fig.get(field, []), group, fid)
        for field in ("reader_question", "reader_task", "evidence_role", "cannot_infer", "invariants", "caption"):
            require(bool(fig.get(field)), "contract:" + field, "Required visual argument field", fid)
        visual = fig.get("visual", {})
        require(all(isinstance(visual.get(k), (int, float)) and not isinstance(visual.get(k), bool) and math.isfinite(visual[k]) and visual[k] > 0
                    for k in ("width_mm", "height_mm", "font_size")), "physical_size", "Positive physical size and font size", fid)
        if "export_dpi" in visual:
            require(isinstance(visual["export_dpi"],(int,float)) and not isinstance(visual["export_dpi"],bool) and math.isfinite(visual["export_dpi"]) and visual["export_dpi"]>0,"export_resolution","Explicit positive raster export DPI",fid)
        require(fig.get("representation") in {"quantitative", "schematic", "mixed"}, "representation", "Representation is distinct from basis", fid)
        if kind not in KINDS:
            add("renderer", "not_implemented", "No built-in renderer for " + str(kind), fid)
            continue
        try:
            rows = data.get(fig.get("dataset_id"))
            ds = maps["datasets"].get(fig.get("dataset_id"))
            if kind not in {"methods","structure3d","catalyst_surface","toc","schematic"}:
                if rows is None:
                    raise ValueError("A valid dataset_id is required")
                refs([fig["dataset_id"]], "datasets", fid)
            mapping = fig.get("mapping", {})
            if kind in {"structure3d","catalyst_surface","toc","series","schematic","summary","recipe","energy_network"}:
                backend_module().validate_advanced(fig,project,root,maps,data,require,add,resolve)
            elif kind == "paired":
                before, after = mapping["before"], mapping["after"]
                require(ds["columns"][before] == ds["columns"][after] == "number", "paired_numeric", "Numeric paired measurements", fid)
                require(ds["units"][before] == ds["units"][after], "paired_units", "Common measurement unit", fid)
                require(all(r[before] is not None and r[after] is not None for r in rows), "paired_completeness", "Missing pairs require explicit analysis, not silent deletion", fid)
                if "y_limits" in visual:
                    lo, hi = visual["y_limits"]
                    vals = [r[c] for r in rows for c in (before, after) if r[c] is not None]
                    require(lo < hi and all(lo <= v <= hi for v in vals), "visible_values", "Axis range must preserve all points", fid)
            elif kind == "table":
                cols = mapping["columns"]
                require(bool(cols) and all(c in ds["columns"] for c in cols), "table_columns", "Columns bind to source values", fid)
                require(bool(mapping.get("denominator")) and bool(mapping.get("missing_label")), "table_semantics", "Explicit denominator and missing label", fid)
                for col, fmt in mapping.get("formats", {}).items():
                    require(col in cols and ds["columns"].get(col) == "number", "table_format", "Formatting applies to a numeric displayed column", fid)
                    for row in rows:
                        if row.get(col) is not None:
                            format(row[col], fmt)
            elif kind == "energy":
                key, value = ds["row_key"], mapping["value"]
                require(ds["columns"][value] == "number" and bool(ds.get("reference")), "energy_reference", "Numeric energy and common reference required", fid)
                order = mapping["order"]
                require(len(order) == len(set(order)) and set(order) == {r[key] for r in rows}, "energy_order", "Each source state appears exactly once", fid)
                require(all(r[value] is not None for r in rows), "energy_values", "No missing energy values", fid)
                require(all(x in maps["entities"] for x in order), "state_identity", "States map to scientific entities", fid)
                require(bool(fig.get("relation_ids")), "energy_topology", "Path edges required", fid)
                positions = {state: i for i, state in enumerate(order)}
                for rid in fig.get("relation_ids", []):
                    rel = maps["relations"][rid]
                    require(rel["type"] == "transformation" and rel["from"] in positions and rel["to"] in positions
                            and positions.get(rel["to"], -99) - positions.get(rel["from"], 99) == 1,
                            "energy_edge_alignment", "Declared edge matches adjacent plotted states", rid)
                require(len(fig.get("relation_ids", [])) == max(0, len(order)-1), "energy_edge_count", "This renderer supports one fully linked path", fid)
                actual_edges = {(maps["relations"][rid]["from"], maps["relations"][rid]["to"]) for rid in fig.get("relation_ids", [])}
                require(actual_edges == set(zip(order, order[1:])), "energy_edge_coverage", "Exactly the declared adjacent path edges", fid)
                if "y_limits" in visual:
                    lo, hi = visual["y_limits"]
                    require(lo < hi and all(lo <= r[value] <= hi for r in rows), "visible_values", "No clipped states", fid)
            else:
                nodes = visual["nodes"]
                require(set(nodes) == set(fig["entity_ids"]), "method_node_binding", "Layout binds each entity exactly once", fid)
                require(all(len(v) == 2 and all(isinstance(n, (int, float)) and math.isfinite(n) and 0 <= n <= 1 for n in v) for v in nodes.values()),
                        "method_coordinates", "Normalized finite node coordinates", fid)
                for rid in fig.get("relation_ids", []):
                    rel = maps["relations"][rid]
                    require(rel["from"] in nodes and rel["to"] in nodes, "method_edge_binding", "Edge endpoints are visible nodes", rid)
                if mapping.get("topology_source_id"):
                    source = maps["sources"][mapping["topology_source_id"]]
                    expected = read_json(resolve(root, source["path"]))
                    actual = {(maps["relations"][r]["from"], maps["relations"][r]["to"]) for r in fig["relation_ids"]}
                    require(set(expected["nodes"]) == set(nodes) and {tuple(e) for e in expected["edges"]} == actual,
                            "method_source_topology", "Scientific topology matches the independent source file", fid)
                else:
                    add("method_source_topology", "unknown", "No machine-readable topology source provided", fid)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            add("figure_spec", "failed", str(exc), fid)
    for section in maps["sections"].values():
        for field, group in (("claim_ids", "claims"), ("figure_ids", "figures"), ("citation_ids", "sources")):
            refs(section.get(field, []), group, section["id"])
        require(bool(section.get("path")) and resolve(root, section["path"]).is_file(), "manuscript_file", "Linked section source exists", section["id"])
    for guard in project.get("protected", []):
        try:
            require(pointer(project, guard["pointer"]) == guard["value"], "preserved_requirement", guard["pointer"])
        except (KeyError, IndexError, TypeError):
            add("preserved_requirement", "failed", guard["pointer"])
    sig = signature(project, root)
    for category in sorted(REVIEWS):
        records = [r for r in project.get("reviews", []) if r.get("category") == category and r.get("signature") == sig]
        if records:
            review = records[-1]
            status = review.get("status", "unknown")
            if status not in STATUSES:
                status = "failed"
            if category == "reader" and not review.get("independent"):
                status = "unknown"
            record_path = resolve(root, review.get("record_path", ""))
            if not record_path.is_file() or digest(record_path.read_bytes()) != review.get("record_digest"):
                status = "unknown"
            if visual_review_consistency(review, root):
                status = "failed"
            add("manual:" + category, status, "Recorded assessment (not an automatic proof): " + review.get("record_path", ""))
        else:
            add("manual:" + category, "unknown", "No current assessment; any old review is stale")
    add("scientific_inference", "not_implemented", "No automated proof of statistical claims, mechanisms or causal validity")
    if project.get("journal_profile"):
        profile = read_json(resolve(root, project["journal_profile"]))
        policy = profile.get("policy", {})
        current = all(policy.get(k) for k in ("checked_on", "official_url", "applicable_conditions"))
        add("publication_profile", "passed" if current and policy.get("status") == "reviewed" else "unknown",
            "Configuration completeness only; official policy applicability requires human review")
    else:
        add("publication_profile", "unknown", "No target journal/use profile configured")
    if export is not None:
        try:
            manifest = read_json(Path(export) / "manifest.json")
            require(manifest["signature"] == sig, "export_inputs", "Export matches current specification, evidence and manuscript")
            require(set(manifest["figures"]) == set(maps["figures"]), "export_figure_set", "Every figure exported")
            for name, expected in manifest["files"].items():
                path = resolve(export, name)
                require(path.is_file() and digest(path.read_bytes()) == expected, "export_integrity", name)
            for fid, info in manifest["figures"].items():
                import xml.etree.ElementTree as ET
                svg = ET.parse(resolve(export, info["svg"]))
                ids = {e.get("id") for e in svg.iter() if e.get("id")}
                require(set(info["object_ids"]) <= ids, "svg_object_binding", "Expected source-bound objects exist in SVG", fid)
            if manifest.get("typography"):
                require(manifest["typography"]["passed"],"typography","Exported text matches the selected typography tokens")
        except (OSError, ValueError, KeyError) as exc:
            add("export_manifest", "failed", str(exc))
    return {"signature": sig, "checks": checks,
            "counts": {s: sum(c["status"] == s for c in checks) for s in sorted(STATUSES)},
            "automated_checks_passed": not any(c["status"] == "failed" for c in checks if not c["check"].startswith("manual:")),
            "checks_passed": not any(c["status"] == "failed" for c in checks),
            "fully_verified": all(c["status"] == "passed" for c in checks)}


def backend_module():
    import importlib.util
    path=Path(__file__).with_name("scientific_backends.py")
    spec=importlib.util.spec_from_file_location("research_scientific_backends",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def render(project, root, out):
    report = validate(project, root)
    if not report["checks_passed"]:
        raise ValueError("Fix failed checks before rendering")
    if any(f["kind"] not in KINDS for f in project["figures"]):
        raise ValueError("Unsupported figure backend; no partial export")
    import os
    os.environ.setdefault("MPLCONFIGDIR", str(Path(root) / ".matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(Path(root) / ".cache"))
    Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    plt.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42, "font.family": "DejaVu Sans", "svg.hashsalt": "research-harness-v1"})
    backend=backend_module()
    profile=read_json(resolve(root,project["style_profile"])) if project.get("style_profile") else None
    if profile:
        for token in profile["roles"].values():
            if token.get("font_file"):token["font_file"]=str(resolve(root,token["font_file"]))
        plt.rcParams.update({"font.family":profile["font_family"],"mathtext.fontset":profile.get("notation",{}).get("mathtext_fontset","dejavusans")})
        if profile.get("notation",{}).get("mathtext_fontset")=="custom":
            plt.rcParams.update({"mathtext.rm":profile["font_family"],"mathtext.it":profile["font_family"]+":italic","mathtext.bf":profile["font_family"]+":bold"})
    plt.rcParams["image.composite_image"]=False  # Preserve each source-bound raster object ID.
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    entities = {e["id"]: e for e in project["entities"]}
    relations = {e["id"]: e for e in project["relations"]}
    datasets = {d["id"]: d for d in project["datasets"]}
    manifest = {"signature": report["signature"], "figures": {}, "files": {}}
    typography={"passed":True,"figures":{}}
    captions = []
    for spec in project["figures"]:
        v, kind, fid = spec["visual"], spec["kind"], spec["id"]
        fig, ax = plt.subplots(figsize=(v["width_mm"] / 25.4, v["height_mm"] / 25.4), layout="constrained")
        if v.get("layout_mode")=="exact_canvas":
            fig.set_layout_engine(None);ax.set_position([0,0,1,1])
        ax.tick_params(labelsize=v["font_size"])
        colors = v.get("colors", ["#0072B2", "#D55E00"])
        ids = []

        def bind(artist, object_id):
            artist.set_gid(object_id)
            ids.append(object_id)
            return artist

        ds = datasets.get(spec.get("dataset_id"))
        rows = load_data(ds, root) if ds else []
        mapping = spec.get("mapping", {})
        extra_files=[]
        if kind in {"structure3d","catalyst_surface","toc","series","schematic","summary","recipe","energy_network"}:
            extra_files=backend.render_advanced(spec,project,root,fig,ax,bind,out,load_data)
        elif kind == "paired":
            a, b = mapping["before"], mapping["after"]
            for row in rows:
                rid = str(row[ds["row_key"]])
                bind(ax.plot([0, 1], [row[a], row[b]], color="#969696", linewidth=0.8, zorder=1)[0], fid + ":pair:" + rid)
                for x, col, color in ((0, a, colors[0]), (1, b, colors[-1])):
                    bind(ax.scatter([x], [row[col]], color=color, s=24, zorder=2), fid + ":cell:" + rid + ":" + col)
            ax.set_xticks([0, 1], mapping.get("labels", [a, b]))
            ax.set_xlim(-0.35, 1.35)
            ax.set_ylabel(v.get("ylabel", ds["units"][a]), fontsize=v["font_size"])
        elif kind == "table":
            cols = mapping["columns"]
            body = [[mapping["missing_label"] if r[c] is None else format(r[c], mapping.get("formats", {}).get(c, "")) for c in cols] for r in rows]
            headers = [c + (" (" + ds["units"][c] + ")" if c in ds.get("units", {}) else "") for c in cols]
            table = ax.table(cellText=body, colLabels=headers, loc="center", cellLoc="center", edges="horizontal")
            table.auto_set_font_size(False)
            table.set_fontsize(v["font_size"])
            table.scale(1, 1.8)
            for i, row in enumerate(rows, 1):
                for j, col in enumerate(cols):
                    bind(table[i, j], fid + ":cell:" + str(row[ds["row_key"]]) + ":" + col)
            ax.set_axis_off()
            ax.text(0.5, 0.05, "Denominator: " + mapping["denominator"] + " | " + mapping["missing_label"] + " = missing", transform=ax.transAxes,
                    ha="center", fontsize=v["font_size"]-1)
        elif kind == "energy":
            values = {r[ds["row_key"]]: r[mapping["value"]] for r in rows}
            order = mapping["order"]
            for i, state in enumerate(order):
                y = values[state]
                bind(ax.plot([i-0.19, i+0.19], [y, y], color=colors[0], linewidth=2)[0], fid + ":state:" + state)
                ax.annotate(str(y), (i, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=v["font_size"])
            for rid in spec["relation_ids"]:
                rel = relations[rid]
                i, j = order.index(rel["from"]), order.index(rel["to"])
                bind(ax.plot([i+0.19, j-0.19], [values[rel["from"]], values[rel["to"]]], "--", color="#777777", linewidth=0.9)[0], fid + ":edge:" + rid)
            ax.set_xticks(range(len(order)), [entities[s]["label"] for s in order])
            ax.set_ylabel(v.get("ylabel", "Energy (" + ds["units"][mapping["value"]] + ")"), fontsize=v["font_size"])
            ax.set_xlabel("Discrete states | reference: " + ds["reference"], fontsize=v["font_size"])
            ax.margins(y=0.3)
        else:
            nodes = v["nodes"]
            node_boxes = {}
            for eid, (x, y) in nodes.items():
                box = FancyBboxPatch((x-0.10, y-0.055), 0.20, 0.11, boxstyle="round,pad=0.01", facecolor="#EAF3F8", edgecolor=colors[0], zorder=3)
                node_boxes[eid] = box
                bind(ax.add_patch(box), fid + ":entity:" + eid)
                ax.text(x, y, entities[eid]["label"], ha="center", va="center", fontsize=v["font_size"], zorder=4)
            for rid in spec["relation_ids"]:
                rel = relations[rid]
                start, end = nodes[rel["from"]], nodes[rel["to"]]
                arrow = FancyArrowPatch(start, end, patchA=node_boxes[rel["from"]], patchB=node_boxes[rel["to"]],
                                        arrowstyle="-|>", mutation_scale=10, shrinkA=2, shrinkB=3, zorder=2,
                                        linewidth=1, linestyle="--" if rel["basis"] in {"hypothesis", "unknown"} else "-", color="#555555")
                bind(ax.add_patch(arrow), fid + ":edge:" + rid)
                ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+0.04, rel["type"].replace("_", " "),
                        ha="center", fontsize=max(5, v["font_size"]-2), color="#555555")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_axis_off()
        if kind in {"paired", "energy"}:
            ax.spines[["top", "right"]].set_visible(False)
            if "y_limits" in v:
                ax.set_ylim(v["y_limits"])
        if kind != "recipe" or "title" in v:
            title = v.get("title", fid)
            if project["project"].get("synthetic"):
                title = "SYNTHETIC DEMO | " + title
            ax.set_title(title, fontsize=v["font_size"]+1, loc="left", pad=14)
        elif project["project"].get("synthetic"):
            # Recipes own their headings unless visual.title explicitly overrides them.
            title = ax.get_title(loc="left")
            title = "SYNTHETIC DEMO" + (" | " + title if title else "")
            ax.set_title(title, fontsize=v["font_size"]+1, loc="left", pad=14)
        if profile:
            backend.style_figure(fig,profile,v["font_size"])
            # Draw first: tick positions and their actual labels must exist before auditing.
            fig.canvas.draw()
            backend.style_figure(fig,profile,v["font_size"])
            text_report=backend.typography_audit(fig,profile,v["font_size"],fid,bind)
            typography["figures"][fid]=text_report
            typography["passed"] &= text_report["passed"]
        # Quantitative charts and custom recipes need the same rendered-layout
        # observations as scenes. These are review candidates, not aesthetic passes.
        layout_path=out/(fid+".layout.json")
        write_json(layout_path,backend.narrative_module().text_collisions(fig));extra_files.append(layout_path)
        for ext in ("svg", "pdf", "png"):
            name = fid + "." + ext
            metadata = {"Date": None} if ext == "svg" else ({"CreationDate": None, "ModDate": None} if ext == "pdf" else None)
            export_fonts={"svg.fonttype":"path","pdf.fonttype":3} if v.get("text_export")=="outline" else {"svg.fonttype":"none","pdf.fonttype":42}
            with plt.rc_context(export_fonts):
                fig.savefig(out / name, dpi=v.get("export_dpi",180), metadata=metadata)
            manifest["files"][name] = digest((out / name).read_bytes())
        plt.close(fig)
        for extra in extra_files:
            manifest["files"][extra.name]=digest(extra.read_bytes())
        manifest["figures"][fid] = {"svg": fid + ".svg", "object_ids": ids, "dataset_id": spec.get("dataset_id"),
                                   "claim_ids": spec["claim_ids"], "entity_ids": spec["entity_ids"],
                                   "raster_structure_content":kind in {"structure3d","catalyst_surface","toc"}}
        captions.append("## " + fid + "\n\n" + spec["caption"] + "\n")
    (out / "captions.md").write_text("\n".join(captions), encoding="utf-8")
    manifest["files"]["captions.md"] = digest((out / "captions.md").read_bytes())
    write_json(out / "source-spec.json", project)
    manifest["files"]["source-spec.json"] = digest((out / "source-spec.json").read_bytes())
    generator=out/"generator";generator.mkdir(exist_ok=True)
    for program in Path(__file__).parent.glob("*.py"):
        shutil.copy2(program,generator/program.name)
        manifest["files"]["generator/"+program.name]=digest(program.read_bytes())
    manifest["generator_note"]="Rendering programs are snapshotted; input files stay in the project with signatures. Restore prose from its saved manuscript versions when reproducing historical rounds."
    if profile:
        write_json(out/"typography.json",typography)
        manifest["files"]["typography.json"]=digest((out/"typography.json").read_bytes())
        manifest["typography"]={"passed":typography["passed"],"profile":project["style_profile"]}
    write_json(out / "manifest.json", manifest)
    return validate(project, root, out)


def classify(path):
    parts = path.strip("/").split("/")
    if parts[0]=="figures" and len(parts)>3 and parts[2]=="mapping" and parts[3] in {"layout","radius_scale","repeat","selection","show_cell"}:
        return "interpretive"
    if parts[0] == "figures" and len(parts) > 3 and parts[2] == "visual":
        return "presentation" if parts[3] in {"font_size", "export_dpi"} else "interpretive"
    if parts[0] in {"sources", "datasets", "entities", "relations", "claims", "figures", "sections", "project", "journal_profile", "style_profile", "semantic_colors"}:
        return "data"
    raise ValueError("Uneditable administrative field: " + path)


def revise(spec_path, operation):
    old = read_json(spec_path)
    new = copy.deepcopy(old)
    if operation.get("type") not in {"presentation", "interpretive", "data"} or not operation.get("changes"):
        raise ValueError("Revision needs a type and nonempty changes")
    allowed = operation.get("allowed_change", [])
    ranks={"presentation":0,"interpretive":1,"data":2}
    for change in operation["changes"]:
        path = change["path"]
        if path not in allowed or ranks[classify(path)] > ranks[operation["type"]]:
            raise ValueError("Change is outside declared scope or has wrong revision type: " + path)
        set_pointer(new, path, change["value"])
    # Guard values come from the actual old document, never supplied replacements.
    guards = copy.deepcopy(old.get("protected", []))
    for path in operation.get("must_preserve", []):
        if not any(g["pointer"] == path for g in guards):
            guards.append({"pointer": path, "value": copy.deepcopy(pointer(old, path))})
    new["protected"] = guards
    report = validate(new, Path(spec_path).parent)
    if not report["checks_passed"]:
        failed = [c for c in report["checks"] if c["status"] == "failed"]
        raise ValueError("Revision rejected; original unchanged: " + json.dumps(failed, ensure_ascii=False))
    rev = old.get("revision", 0) + 1
    checkpoint = Path(spec_path).parent / ".research-history" / ("revision-%04d.json" % rev)
    if checkpoint.exists():
        raise ValueError("Checkpoint already exists: " + str(checkpoint))
    write_json(checkpoint, {"before": old, "operation": operation})
    new["revision"] = rev
    new.setdefault("history", []).append({"revision": rev, "type": operation["type"], "reason": operation.get("reason", ""),
                                           "checkpoint": str(checkpoint.relative_to(Path(spec_path).parent))})
    write_json(spec_path, new)
    return report


def argument_map(project):
    lines = ["# 主张—证据—图件—正文索引", "", "此索引仅报告声明的连接，不证明主张为真。", ""]
    for claim in project["claims"]:
        cid = claim["id"]
        figs = [f["id"] for f in project["figures"] if cid in f["claim_ids"]]
        sections = [s["id"] for s in project["sections"] if cid in s["claim_ids"]]
        lines.extend(["## " + cid + " [" + claim["status"] + "]", "", claim["text"], "",
                      "证据：" + ", ".join(claim["evidence_ids"]), "", "图件：" + ", ".join(figs), "",
                      "正文：" + ", ".join(sections), "", "边界：" + claim["limitations"], ""])
    return "\n".join(lines)


def init_project(destination, demo=False):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Initialize an empty directory; existing project is not overwritten")
    base = Path(__file__).resolve().parent.parent
    if not (base / "assets" / "blank.json").exists():
        raise ValueError("Initialization must run from installed skill, not copied project runtime")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "scripts").mkdir()
    shutil.copy2(__file__, destination / "scripts" / "research.py")
    shutil.copy2(Path(__file__).with_name("scientific_backends.py"),destination/"scripts/scientific_backends.py")
    shutil.copy2(Path(__file__).with_name("narrative_scene.py"),destination/"scripts/narrative_scene.py")
    for name in ('scene_layout.py','legacy_mattergen_toc.py','energy_network.py','publication_components.py','representations.py'):
        shutil.copy2(Path(__file__).with_name(name),destination/'scripts'/name)
    shutil.copy2(Path(__file__).with_name('story.py'),destination/'scripts/story.py')
    shutil.copy2(Path(__file__).with_name('paper_batch.py'),destination/'scripts/paper_batch.py')
    shutil.copy2(base/'assets/story-blank.json',destination/'story.json')
    structure_source=Path(backend_module().structure_module().__file__)
    shutil.copy2(structure_source,destination/"scripts/structure_render.py")
    shutil.copy2(backend_module().surface_backend().renderer_path(),destination/"scripts/surface_render.py")
    shutil.copy2(Path(__file__).with_name("surface_backend.py"),destination/"scripts/surface_backend.py")
    shutil.copytree(base / "references", destination / "harness-docs")
    for name in ("AGENTS.md", "requirements.txt", "requirements-3d.txt", "patterns.json", "journal-profile.json", "style-profile.json"):
        shutil.copy2(base / "assets" / name, destination / name)
    shutil.copy2(base / "assets" / ("demo.json" if demo else "blank.json"), destination / "research.json")
    initial=read_json(destination/'research.json');initial['story_plan']='story.json';write_json(destination/'research.json',initial)
    if demo:
        shutil.copytree(base / "assets" / "demo-data", destination / "data")
        shutil.copytree(base / "assets" / "demo-manuscript", destination / "manuscript")
    else:
        (destination / "data").mkdir()
        (destination / "manuscript").mkdir()
    (destination / ".gitignore").write_text(".venv/\n.matplotlib/\n.cache/\n.structure-cache/\n.surface-cache/\n__pycache__/\nbuild/\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    init = subs.add_parser("init")
    init.add_argument("destination")
    init.add_argument("--demo", action="store_true")
    for name in ("check", "render", "map", "revise", "record-review"):
        p = subs.add_parser(name)
        p.add_argument("spec")
        if name == "check":
            p.add_argument("--out")
            p.add_argument("--strict", action="store_true")
            p.add_argument("--export")
        elif name in {"render", "map"}:
            p.add_argument("--out", required=True)
        elif name in {"revise", "record-review"}:
            p.add_argument("record")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_project(args.destination, args.demo)
            print("Initialized: " + args.destination)
            return 0
        spec_path = Path(args.spec).resolve()
        project, root = read_json(spec_path), spec_path.parent
        if args.command == "map":
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(argument_map(project), encoding="utf-8")
            return 0
        if args.command == "revise":
            report = revise(spec_path, read_json(args.record))
        elif args.command == "record-review":
            record = read_json(args.record)
            if record.get("category") not in REVIEWS or record.get("status") not in STATUSES:
                raise ValueError("Invalid review category/status")
            if not record.get("reviewer") or not record.get("record_path"):
                raise ValueError("Review needs reviewer and a project-relative record_path")
            if not resolve(root, record["record_path"]).is_file():
                raise ValueError("Review record must exist")
            contradictions = visual_review_consistency(record, root)
            if contradictions:
                raise ValueError("; ".join(contradictions))
            record["signature"] = signature(project, root)
            record["record_digest"] = digest(resolve(root, record["record_path"]).read_bytes())
            record["recorded_at"] = datetime.now(timezone.utc).isoformat()
            project.setdefault("reviews", []).append(record)
            write_json(spec_path, project)
            report = validate(project, root)
        elif args.command == "render":
            report = render(project, root, args.out)
            write_json(Path(args.out) / "validation.json", report)
        else:
            report = validate(project, root, args.export)
            if args.out:
                write_json(args.out, report)
        print(json.dumps({"counts": report["counts"], "automated_checks_passed": report["automated_checks_passed"],
                          "checks_passed": report["checks_passed"],
                          "fully_verified": report["fully_verified"]}, ensure_ascii=False))
        return 1 if report["counts"]["failed"] or (getattr(args, "strict", False) and not report["fully_verified"]) else 0
    except (OSError, ValueError, KeyError, TypeError, ImportError, IndexError, RuntimeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
