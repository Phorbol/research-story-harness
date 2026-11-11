#!/usr/bin/env python3
"""Read actual structures with ASE; preserve occupancies; ray trace with OVITO."""
import argparse
import hashlib
import itertools
import json
import math
import os
import copy
from pathlib import Path


STYLE_PRESETS = {
    "solid": {"radius_scale": .90, "crop": False, "render_settings": {
        "ambient_occlusion_brightness": .78, "direct_light_intensity": .72, "shadows": False}},
    "surface": {"radius_scale": .94, "element_radii_angstrom": {"C": .66, "O": .60, "H": .32},
        "crop": False, "render_settings": {"ambient_occlusion_brightness": .78,
        "direct_light_intensity": .72, "shadows": False}},
    "molecule": {"radius_scale": .72, "element_radii_angstrom": {"H": .32},
        "bonds": {"width_angstrom": .18}, "crop": False, "render_settings": {
        "ambient_occlusion_brightness": .82, "direct_light_intensity": .72, "shadows": False}},
}


def resolve_style(spec):
    """Explicit presets are starting points; existing unlabelled specs retain legacy rendering."""
    name = spec.get("style_preset")
    if name is None:
        return copy.deepcopy(spec)
    if name not in STYLE_PRESETS:
        raise ValueError("Unknown style_preset: " + str(name))
    resolved = copy.deepcopy(STYLE_PRESETS[name])
    for key, value in spec.items():
        if key in {"bonds", "render_settings", "element_radii_angstrom"}:
            resolved[key] = {**resolved.get(key, {}), **value}
        else:
            resolved[key] = copy.deepcopy(value)
    return resolved


def particle_styles(scene):
    """Display radii in Angstrom, independent of source coordinates and neighbour topology."""
    import numpy as np
    from ase.data import atomic_numbers, covalent_radii
    from ase.data.colors import jmol_colors
    from matplotlib.colors import to_rgb
    spec = resolve_style(scene["spec"])
    palette = spec.get("element_colors", {})
    scale = float(spec.get("radius_scale", .42))
    overrides = spec.get("element_radii_angstrom", {})
    if not math.isfinite(scale) or scale <= 0 or any(
            not math.isfinite(float(v)) or float(v) <= 0 for v in overrides.values()):
        raise ValueError("Display radii and radius scale must be positive and finite")
    colors, radii = [], []
    for particle in scene["particles"]:
        color = np.zeros(3); radius = 0.
        for element, fraction in particle["occupancy"].items():
            number = atomic_numbers[element]
            color += fraction * np.array(to_rgb(palette[element]) if element in palette else jmol_colors[number])
            radius += fraction * float(overrides.get(element, covalent_radii[number] * scale))
        color += max(0, 1-sum(particle["occupancy"].values())) * np.ones(3)
        colors.append(color); radii.append(float(radius))
    if any(not math.isfinite(r) or r <= 0 for r in radii):
        raise ValueError("Display radii must be positive and finite")
    return colors, radii


def structure_scene(path, spec):
    import numpy as np
    from ase.io import read
    spec = resolve_style(spec)
    path = Path(path)
    atoms = read(path, index=spec.get("frame", -1))
    if not len(atoms) or not np.isfinite(atoms.positions).all():
        raise ValueError("No finite atomic positions")
    if atoms.pbc.any() and (not np.isfinite(atoms.cell.array).all() or abs(atoms.cell.volume) < 1e-10):
        raise ValueError("Periodic structures require a nonsingular unit cell")
    repeat = spec.get("repeat", [1, 1, 1])
    if len(repeat) != 3 or any(type(n) is not int or not 1 <= n <= 8 for n in repeat):
        raise ValueError("repeat requires three integers in 1..8; larger scenes need explicit budgeting")
    selected = spec.get("selection", list(range(len(atoms))))
    if not selected or len(selected) != len(set(selected)) or any(type(i) is not int or not 0 <= i < len(atoms) for i in selected):
        raise ValueError("Selection must contain unique, existing source-site indices")
    if not set(spec.get("must_show_sites", [])) <= set(selected):
        raise ValueError("Selection hides a required source site")
    kinds = atoms.arrays.get("spacegroup_kinds", np.arange(len(atoms)))
    occupancy = atoms.info.get("occupancy", {})
    sites, composition = [], {}
    for index, atom in enumerate(atoms):
        fractions = occupancy.get(str(int(kinds[index])), {atom.symbol: 1.0})
        fractions = {s: float(f) for s, f in fractions.items() if f > 0}
        if not fractions or not all(math.isfinite(v) and 0 < v <= 1 for v in fractions.values()) or sum(fractions.values()) > 1.00001:
            raise ValueError("Invalid fractional occupancy at site " + str(index))
        for symbol, fraction in fractions.items():
            composition[symbol] = composition.get(symbol, 0) + fraction
        sites.append({"source_index": index, "position": atom.position.tolist(), "occupancy": fractions})
    required_elements = set(spec.get("must_show_elements", []))
    visible_elements = {s for i in selected for s in sites[i]["occupancy"]}
    if not required_elements <= visible_elements:
        raise ValueError("Selection hides a required element, including a fractional component")
    if any(len(s["occupancy"]) > 1 or sum(s["occupancy"].values()) < .9999 for s in sites):
        if spec.get("occupancy_mode") != "weighted_color":
            raise ValueError("Mixed/partial occupancy requires explicit occupancy_mode=weighted_color and an occupancy legend")
    particles = []
    for image in itertools.product(*(range(n) for n in repeat)):
        for i in selected:
            particles.append({"id": "site-%d-image-%d-%d-%d" % (i, *image), "source_index": i, "image": list(image),
                              "position": (atoms.positions[i] + np.array(image) @ atoms.cell.array).tolist(),
                              "occupancy": sites[i]["occupancy"]})
    bonds = []
    bond_spec = spec.get("bonds", {"mode": "none"})
    if bond_spec.get("mode") == "cutoff":
        from ase.neighborlist import neighbor_list
        cutoff = bond_spec["cutoff_angstrom"]
        if not math.isfinite(cutoff) or cutoff <= 0 or not bond_spec.get("meaning"):
            raise ValueError("Distance neighbors need a positive cutoff and a declared scientific meaning")
        ii, jj, shifts = neighbor_list("ijS", atoms, cutoff, self_interaction=False)
        lookup = {(p["source_index"], tuple(p["image"])): k for k, p in enumerate(particles)}
        seen = set()
        for a, b, shift in zip(ii, jj, shifts):
            for image in itertools.product(*(range(n) for n in repeat)):
                left, right = lookup.get((int(a), image)), lookup.get((int(b), tuple(np.array(image) + shift)))
                if left is None or right is None or left == right:
                    continue
                key = tuple(sorted([left, right]))
                if key in seen:
                    continue
                seen.add(key)
                pa, pb = np.array(particles[left]["position"]), np.array(particles[right]["position"])
                bonds.append({"from": left, "to": right, "periodic_shift": shift.tolist(), "distance_angstrom": float(np.linalg.norm(pb-pa))})
    elif bond_spec.get("mode") != "none":
        raise ValueError("Supported bond modes: none, cutoff; chemical bonding is not inferred")
    return {"schema_version": 1, "source": {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "model_origin": spec.get("model_origin",atoms.info.get("model_origin","unspecified")),
            "not_relaxed": atoms.info.get("not_relaxed"),
            "not_paper_coordinates": atoms.info.get("not_paper_coordinates")},
            "base_cell": atoms.cell.array.tolist(), "display_cell": (np.diag(repeat) @ atoms.cell.array).tolist(),
            "pbc": atoms.pbc.tolist(), "source_sites": sites, "weighted_composition": composition,
            "particles": particles, "bonds": bonds, "spec": spec,
            "boundary_rule": "Distance edges are shown only when both periodic-image endpoints are in the displayed selection."}


def render_ovito(scene, output, view, size=(1000, 800), quality="draft"):
    # CPU ray tracing still needs OVITO host graphics initialization; do not silently substitute renderers.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import numpy as np
    import ovito
    from ovito.data import DataCollection, Particles, SimulationCell
    from ovito.pipeline import Pipeline, StaticSource
    from ovito.vis import Viewport, TachyonRenderer
    colors, radii = particle_styles(scene)
    data = DataCollection()
    particles = Particles(count=len(scene["particles"]))
    data.objects.append(particles)
    particles.create_property("Position", data=[p["position"] for p in scene["particles"]])
    particles.create_property("Particle Identifier", data=list(range(1,len(scene["particles"])+1)))
    particles.create_property("Source Site", data=[p["source_index"] for p in scene["particles"]])
    particles.create_property("Color", data=colors)
    particles.create_property("Radius", data=radii)
    cell = SimulationCell(pbc=tuple(scene["pbc"]))
    matrix = np.zeros((3,4));matrix[:,:3] = np.array(scene["display_cell"]).T
    cell[...] = matrix
    cell.vis.enabled = scene["spec"].get("show_cell", True)
    cell.vis.line_width = scene["spec"].get("cell_line_width",.035)
    cell.vis.rendering_color = (.47,.52,.59)
    data.objects.append(cell)
    if scene["bonds"]:
        bonds = particles.create_bonds(count=len(scene["bonds"]))
        bonds.create_property("Topology", data=[[b["from"],b["to"]] for b in scene["bonds"]])
        bonds.vis.width = scene["spec"]["bonds"].get("width_angstrom", .10)
    pipeline = Pipeline(source=StaticSource(data=data))
    pipeline.add_to_scene()
    try:
        projection = view.get("projection", "orthographic")
        if projection not in {"orthographic","perspective"}:
            raise ValueError("Unknown projection")
        direction = np.array(view.get("direction", [1,-1,-.8]), dtype=float)
        up = np.array(view.get("up", [0,0,1]), dtype=float)
        if not np.isfinite(direction).all() or np.linalg.norm(direction)<1e-8 or np.linalg.norm(np.cross(direction,up))<1e-8:
            raise ValueError("Camera direction and up must be finite nonparallel vectors")
        viewport = Viewport(type=Viewport.Type.Ortho if projection=="orthographic" else Viewport.Type.Perspective,
                            camera_dir=tuple(direction), camera_up=tuple(up))
        viewport.zoom_all(size=tuple(size))
        viewport.fov *= float(view.get("margin", 1.12))
        if "fov_angstrom" in view:
            if projection != "orthographic" or not math.isfinite(float(view["fov_angstrom"])) or view["fov_angstrom"] <= 0:
                raise ValueError("fov_angstrom requires a positive orthographic field of view")
            viewport.fov = float(view["fov_angstrom"])
        if "camera_pos_angstrom" in view:
            position = np.asarray(view["camera_pos_angstrom"], dtype=float)
            if position.shape != (3,) or not np.isfinite(position).all():
                raise ValueError("camera_pos_angstrom requires three finite coordinates")
            viewport.camera_pos = tuple(position)
        settings = dict(ambient_occlusion=True, shadows=False,
                        ambient_occlusion_samples=12 if quality=="draft" else 40,
                        antialiasing_samples=4 if quality=="draft" else 12)
        allowed = {"ambient_occlusion", "shadows", "ambient_occlusion_samples", "antialiasing_samples",
                   "ambient_occlusion_brightness", "direct_light", "direct_light_intensity"}
        user_settings = scene["spec"].get("render_settings", {})
        if set(user_settings) - allowed:
            raise ValueError("Unsupported Tachyon render setting: " + str(set(user_settings) - allowed))
        settings.update(user_settings)
        renderer = TachyonRenderer(**settings)
        output = Path(output);output.parent.mkdir(parents=True,exist_ok=True)
        viewport.render_image(filename=str(output),size=tuple(size),renderer=renderer,background=tuple(scene["spec"].get("background",[1,1,1])),alpha=bool(scene["spec"].get("transparent_background",False)),crop=bool(scene["spec"].get("crop",True)))
        return {"backend":"OVITO Tachyon CPU","ovito_version":ovito.version_string,
                "camera_pos":list(viewport.camera_pos),"camera_dir":list(viewport.camera_dir),"camera_up":list(viewport.camera_up),
                "fov":viewport.fov,"projection":projection,"quality":quality,"size":list(size),
                "display_radii_angstrom":radii,"render_settings":{key:getattr(renderer,key) for key in sorted(allowed)},
                "crop":bool(scene["spec"].get("crop",True)),
                "raster_content":"3D ray-traced particles; vector labels must be composed separately", "particle_count":len(scene["particles"])}
    finally:
        pipeline.remove_from_scene()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("structure");p.add_argument("spec");p.add_argument("--out",required=True)
    p.add_argument("--quality",choices=["draft","final"],default="draft")
    a=p.parse_args();spec=json.loads(Path(a.spec).read_text())
    scene=structure_scene(a.structure,spec)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    views=spec.get("views",[{"name":"oblique","direction":[1,-1,-.8],"up":[0,0,1]}])
    scene["renders"]={}
    for view in views:
        name=view["name"]
        if not name.replace("-","").replace("_","").isalnum():raise ValueError("Unsafe view name")
        scene["renders"][name]=render_ovito(scene,out/(name+".png"),view,tuple(spec.get("pixel_size",[1000,800])),a.quality)
    (out/"scene.json").write_text(json.dumps(scene,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"source_sites":len(scene["source_sites"]),"display_particles":len(scene["particles"]),
                      "weighted_composition":scene["weighted_composition"],"renders":list(scene["renders"])},ensure_ascii=False))


if __name__=="__main__":main()
