"""Source-bound OVITO views for ordered periodic catalyst slabs.

Adapted from the user-provided ovito-catalyst-surface package (received 2026-11-05).
See references/catalyst-surfaces.md for provenance, job schema and limitations.

python surface_render.py job.json [--preview | --verify-only] [--strip]

Use source tags or explicit adsorbate_indices. Only substrate images are tiled;
adsorbates are displayed once with recorded MIC unwrapping. One orthographic
camera serves all states. Metadata retain source identity, display images, radii,
focus projections, local MIC distances and any cutaway. Distance-based sticks
are a display convention, not a chemical bond or transition-state validation.
"""
import argparse
import json
import math
import os
import hashlib
import re
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import numpy as np  # noqa: E402
from ase.data import atomic_numbers, covalent_radii  # noqa: E402
from ase.io import read  # noqa: E402

# Metallic radii for coordination number 12 (A), the usual close-packing radii.  Elements not listed
# are fitted from the slab itself (half the median nearest-neighbour distance, see fitted_radius).
METALLIC_RADIUS = {
    'Li': 1.52, 'Na': 1.86, 'K': 2.27, 'Rb': 2.48, 'Cs': 2.65, 'Be': 1.12, 'Mg': 1.60, 'Ca': 1.97, 'Sr': 2.15,
    'Ba': 2.22, 'Sc': 1.62, 'Y': 1.80, 'La': 1.87, 'Ti': 1.47, 'Zr': 1.60, 'Hf': 1.59, 'V': 1.34, 'Nb': 1.46,
    'Ta': 1.46, 'Cr': 1.28, 'Mo': 1.39, 'W': 1.39, 'Mn': 1.27, 'Tc': 1.36, 'Re': 1.37, 'Fe': 1.26, 'Ru': 1.34,
    'Os': 1.35, 'Co': 1.25, 'Rh': 1.34, 'Ir': 1.36, 'Ni': 1.24, 'Pd': 1.37, 'Pt': 1.39, 'Cu': 1.28, 'Ag': 1.44,
    'Au': 1.44, 'Zn': 1.34, 'Cd': 1.51, 'Hg': 1.51, 'Al': 1.43, 'In': 1.67, 'Tl': 1.70, 'Pb': 1.75,
}
NONMETALS = {'H', 'B', 'C', 'N', 'O', 'F', 'Si', 'P', 'S', 'Cl', 'As', 'Se', 'Br', 'Te', 'I'}
# Adsorbate display radii retained from the supplied visual preset; muted CPK colours.
ADSORBATE_RADIUS = {'H': 0.56, 'C': 0.86, 'N': 0.84, 'O': 0.86}
ADSORBATE_COLOR = {'H': (1.00, 0.99, 0.91), 'C': (0.16, 0.21, 0.25), 'N': (0.23, 0.38, 0.76),
                   'O': (0.86, 0.15, 0.10), 'S': (0.90, 0.74, 0.22), 'P': (0.93, 0.55, 0.20),
                   'F': (0.56, 0.80, 0.42), 'Cl': (0.30, 0.68, 0.32), 'B': (0.95, 0.65, 0.62)}
# Substrate palette by abundance: the majority element first.  Fix colours per element in the job file
# when several figures must agree.
METAL_PALETTE = [(0.55, 0.63, 0.71), (0.80, 0.83, 0.86), (0.74, 0.67, 0.58), (0.60, 0.70, 0.63),
                 (0.68, 0.62, 0.72), (0.47, 0.52, 0.57)]
DEFAULTS = {
    'output_dir': 'renders', 'prefix': 'surface', 'adsorbate_tag': 2, 'request': [], 'cutaway': {'atoms': [], 'transparency': 0.8},
    'style': {'radii': {}, 'colors': {}, 'metal_radius_scale': 1.0, 'layer_darkening': 0.10, 'bond_factor': 1.2,
              'bond_width': 0.32, 'background': [0.36, 0.42, 0.48]},
    'scene': {'layers': 4, 'keep_radius': None, 'layer_gap': 0.85},
    'camera': {'elevation': 50.0, 'azimuth': 10.0, 'half_height': 5.4, 'target_up': 0.6, 'size': [900, 720]},
    'renderer': {'engine': 'tachyon', 'ao_samples': 48, 'ao_brightness': 0.8, 'aa_samples': 12, 'direct_light': 0.85,
                 'shadows': True},
}


def merged(job):
    cfg = json.loads(json.dumps(DEFAULTS))
    for k, v in job.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    return cfg


def fitted_radius(atoms, idx, sub):
    """Half the median nearest-substrate-neighbour distance of the atoms idx (an element not in the table)."""
    d = atoms.get_all_distances(mic=True)
    nn = [min(d[i, j] for j in sub if j != i) for i in idx]
    return 0.5 * float(np.median(nn))


def layers_of(z, sub, gap):
    """Layer index of every substrate atom, 0 = top, splitting where heights differ by more than gap."""
    layer_z = []
    for v in sorted(z[sub], reverse=True):
        if not layer_z or abs(v - layer_z[-1]) > gap:
            layer_z.append(v)
    return {int(i): int(np.argmin([abs(z[i] - lz) for lz in layer_z])) for i in sub}, len(layer_z)


def render_surface_job(job_path, *, preview=False, verify_only=False, strip=False,
                       output_dir=None, project_root=None, write_outputs=True, job_overrides=None):
    """Adapted from the user-supplied ovito-catalyst-surface v1.0; local rendering only.

    Source data stay immutable; periodic display images and adsorbate MIC unwrapping are
    separate, recorded display transforms. Verification can run without writing artifacts.
    """
    args = argparse.Namespace(job=Path(job_path), preview=preview, verify_only=verify_only, strip=strip)
    if not write_outputs and not verify_only:
        raise ValueError('Read-only preparation requires verify_only=True')
    job = json.loads(args.job.read_text())
    cfg = merged(job)
    for key, value in (job_overrides or {}).items():
        if isinstance(value, dict) and isinstance(cfg.get(key), dict):
            cfg[key].update(value)
        else:
            cfg[key] = value
    base = args.job.resolve().parent
    root = Path(project_root).resolve() if project_root is not None else base
    out = Path(output_dir).resolve() if output_dir is not None else (base / cfg['output_dir']).resolve()
    if not out.is_relative_to(root):
        raise ValueError('Surface output directory escapes the project')
    if write_outputs:
        out.mkdir(parents=True, exist_ok=True)
    st, sc, cam_cfg, rnd = cfg['style'], cfg['scene'], cfg['camera'], cfg['renderer']

    names = [s['name'] for s in cfg['states']]
    if not names or len(set(names)) != len(names) or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', n) for n in names):
        raise ValueError('States require unique safe names')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', cfg['prefix']):
        raise ValueError('Unsafe surface output prefix')
    paths = [(base / s['path']).resolve() for s in cfg['states']]
    if any(not p.is_relative_to(root) for p in paths):
        raise ValueError('Surface state path escapes the project')
    atoms = [read(str(p), index=s.get('frame', -1)) for p, s in zip(paths, cfg['states'])]
    original = [a.positions.copy() for a in atoms]
    ref = atoms[0]
    if not all(len(a) == len(ref) and (a.numbers == ref.numbers).all() for a in atoms):
        raise ValueError('States differ in atom count or element order; stable identity is required')
    if not all(np.allclose(a.cell.array, ref.cell.array, atol=1e-8, rtol=0) and np.array_equal(a.pbc, ref.pbc) for a in atoms):
        raise ValueError('A surface sequence requires the same cell and PBC in every state')
    if any(not np.isfinite(a.positions).all() for a in atoms):
        raise ValueError('Non-finite source coordinates')
    for a in atoms:
        if any(len(v) != 1 or abs(sum(v.values())-1) > 1e-6 for v in a.info.get('occupancy', {}).values()):
            raise ValueError('Mixed occupancy needs general structure3d; provide an explicit ordered surface model here')
    sym = ref.get_chemical_symbols()
    tags = ref.get_tags()
    if 'adsorbate_indices' in cfg:
        ids = cfg['adsorbate_indices']
        if not ids or len(set(ids)) != len(ids) or any(type(i) is not int or not 0 <= i < len(ref) for i in ids):
            raise ValueError('adsorbate_indices must be unique source atom indices')
        ads = np.array(sorted(ids), dtype=int)
        classification = 'explicit adsorbate_indices'
    elif (tags == cfg['adsorbate_tag']).any():
        ads = np.flatnonzero(tags == cfg['adsorbate_tag'])
        classification = 'source tags'
        if any(not np.array_equal(a.get_tags() == cfg['adsorbate_tag'], tags == cfg['adsorbate_tag']) for a in atoms):
            raise ValueError('Source adsorbate tags differ across states; stable identity is required')
    elif cfg.get('allow_element_inference', False):
        ads = np.array([i for i, s in enumerate(sym) if s in NONMETALS])
        classification = 'explicitly requested nonmetal heuristic; not chemistry verification'
    else:
        raise ValueError('Provide adsorbate_indices or source adsorbate tags; do not infer oxide/support identity from element names')
    sub = np.array([i for i in range(len(ref)) if i not in set(ads.tolist())])
    if not len(ads) or not len(sub):
        raise ValueError('A catalyst surface needs both substrate and adsorbate atoms')
    request = [(int(i), int(j), str(k)) for i, j, k in cfg['request']]
    if any(not 0 <= i < len(ref) or not 0 <= j < len(ref) or k not in {'break','form'} for i,j,k in request):
        raise ValueError('Requested bond guides need valid atom identities and break/form semantics')
    focus = cfg.get('focus_atoms') or sorted({i for i, j, _ in request} | {j for i, j, _ in request})
    if not focus:
        focus = [int(ads[0])]
    for i in focus:
        assert 0 <= i < len(ref), f'focus atom {i} out of range'

    cell = ref.cell.array
    normal = np.cross(cell[0], cell[1])
    if np.linalg.norm(normal) < 1e-10:
        raise ValueError('Surface cell vectors must define a finite plane')
    if not ref.pbc[:2].all():
        raise ValueError('Periodic substrate patches require in-plane PBC; use general structure3d for finite clusters')
    normal /= np.linalg.norm(normal)

    def unwrapped(a):
        pos = a.positions.copy()
        for j in ads:
            if j != focus[0]:
                pos[j] = pos[focus[0]] + a.get_distance(focus[0], int(j), mic=True, vector=True)
        for j in focus:                                       # focus atoms in the substrate, if any
            if j not in set(ads.tolist()) and j != focus[0]:
                pos[j] = pos[focus[0]] + a.get_distance(focus[0], int(j), mic=True, vector=True)
        return pos

    P = [unwrapped(a) for a in atoms]
    centre_atoms = cfg.get('center_atoms') or focus
    if any(type(i) is not int or not 0 <= i < len(ref) for i in centre_atoms):
        raise ValueError('Invalid center atom')
    centre = np.mean([p[centre_atoms].mean(axis=0) for p in P], axis=0)
    o = cfg.get('orient') or [focus[0], focus[-1]]
    if len(o) != 2 or any(type(i) is not int or not 0 <= i < len(ref) for i in o):
        raise ValueError('orient requires two valid source atom indices')
    right0 = P[0][o[1]] - P[0][o[0]]
    right0 -= normal * (right0 @ normal)
    if np.linalg.norm(right0) < 0.2:                          # degenerate (vertical or single atom): use cell a
        right0 = cell[0] - normal * (cell[0] @ normal)
    right0 /= np.linalg.norm(right0)

    # radii and colours actually used
    radii, colors, source = {}, {}, {}
    # majority first; ties broken by atomic number so that colours do not depend on set order between runs
    metals_by_count = sorted({sym[i] for i in sub}, key=lambda e: (-sum(sym[i] == e for i in sub), atomic_numbers[e]))
    for e in sorted(set(sym)):
        idx = [i for i in range(len(ref)) if sym[i] == e]
        if e in st['radii']:
            radii[e], source[e] = float(st['radii'][e]), 'job'
        elif e in ADSORBATE_RADIUS:
            radii[e], source[e] = ADSORBATE_RADIUS[e], 'adsorbate table'
        elif e in NONMETALS:
            radii[e], source[e] = 1.2 * float(covalent_radii[atomic_numbers[e]]), '1.2 x covalent'
        elif e in METALLIC_RADIUS:
            radii[e], source[e] = st['metal_radius_scale'] * METALLIC_RADIUS[e], 'metallic (CN12)'
        else:
            radii[e], source[e] = st['metal_radius_scale'] * fitted_radius(ref, idx, sub), 'fitted from slab'
    fixed = {tuple(st['colors'][e]) for e in metals_by_count if e in st['colors']}
    palette = iter([c for c in METAL_PALETTE if c not in fixed])  # never repeat a colour fixed in the job
    for e in metals_by_count:
        if e in st['colors']:
            colors[e] = tuple(st['colors'][e])
        elif e in NONMETALS:                                  # e.g. oxide or sulfide support: muted CPK
            c = ADSORBATE_COLOR.get(e, (0.6, 0.6, 0.6))
            colors[e] = tuple(0.5 * x + 0.5 * 0.70 for x in c)
        else:
            colors[e] = next(palette, (0.62, 0.66, 0.70))
    for e in sorted({sym[i] for i in ads}):
        colors.setdefault(e, tuple(st['colors'].get(e, ADSORBATE_COLOR.get(e, (0.55, 0.55, 0.55)))))

    # substrate patch: periodic images in the plane, top layers, within keep_radius of the centre
    z = ref.positions @ normal
    layer_of, n_layers = layers_of(z, sub, sc['layer_gap'])
    el, hh = math.radians(cam_cfg['elevation']), cam_cfg['half_height']
    w, h = cam_cfg['size']
    if not math.isfinite(hh) or hh <= 0 or min(w,h) <= 0 or not 0 < cam_cfg['elevation'] < 90:
        raise ValueError('Positive camera extent/pixels and elevation in (0,90) are required')
    if args.preview:
        w, h = w // 2, h // 2
    half_w = hh * cam_cfg['size'][0] / cam_cfg['size'][1]
    keep = sc['keep_radius'] or max(12.0, 1.6 * math.hypot(hh / max(math.sin(el), 0.3), half_w))
    n_img = int(math.ceil(keep / min(np.linalg.norm(cell[0]), np.linalg.norm(cell[1])))) + 1
    patch = []
    patch_images = []
    for i in sub:
        if layer_of[int(i)] >= sc['layers']:
            continue
        for s1 in range(-n_img, n_img + 1):
            for s2 in range(-n_img, n_img + 1):
                shift = s1 * cell[0] + s2 * cell[1]
                v = ref.positions[i] + shift - centre
                if np.linalg.norm(v - normal * (v @ normal)) <= keep:
                    patch.append((int(i), shift))
                    patch_images.append([s1,s2,0])

    # orthographic camera: elevation above the surface plane, azimuth from the view perpendicular to orient
    depth_dir = np.cross(normal, right0)
    az = math.radians(cam_cfg['azimuth'])
    horizontal = math.cos(az) * depth_dir + math.sin(az) * right0
    d = math.cos(el) * horizontal - math.sin(el) * normal
    d /= np.linalg.norm(d)
    right = np.cross(d, normal)
    right /= np.linalg.norm(right)
    up = np.cross(right, d)
    target = centre + normal * cam_cfg['target_up']
    cam = target - d * 60.0
    scale = min(w, h) / (2 * hh)                              # pixels per A; OVITO's ortho fov spans the shorter side

    if any(not math.isfinite(v) or v <= 0 for v in radii.values()):
        raise ValueError('Display radii must be positive and finite')
    if rnd['engine'] not in {'tachyon','ospray'}:
        raise ValueError('Unknown surface renderer; no silent fallback')
    meta = dict(job=job, effective_config=cfg, preview=args.preview, radii=radii, radius_source=source,
                colors={k: list(v) for k, v in colors.items()}, substrate_layers_found=n_layers,
                substrate_patch_atoms=len(patch), periodic_images=n_img, keep_radius_A=keep,
                adsorbate_indices=ads.tolist(), substrate_indices=sub.tolist(), classification=classification,
                source_files=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frame=s.get('frame',-1)) for p,s in zip(paths,cfg['states'])],
                atom_symbols=sym,
                camera=dict(direction=d.tolist(), up=up.tolist(), right=right.tolist(), position=cam.tolist(),
                            half_height_A=hh, size_px=[w, h]),
                states={})
    if not args.verify_only:
        from ovito.data import DataCollection
        from ovito.pipeline import Pipeline, StaticSource
        from ovito.vis import OSPRayRenderer, TachyonRenderer, Viewport
        import ovito
        meta['OVITO'] = ovito.version_string
        if rnd['engine'] == 'ospray':
            material_options = {k: rnd[k] for k in ('material_type', 'standard_shininess', 'standard_specular_brightness', 'direct_light_angular_diameter') if k in rnd}
            renderer = OSPRayRenderer(refinement_iterations=rnd.get('preview_iterations', 2) if args.preview else rnd.get('refinement_iterations', 8),
                                      samples_per_pixel=rnd.get('preview_samples_per_pixel', 2) if args.preview else rnd.get('samples_per_pixel', 8), denoising_enabled=True,
                                      ambient_light_enabled=True, ambient_brightness=rnd['ao_brightness'],
                                      direct_light_intensity=rnd['direct_light'], **material_options)
        else:
            renderer = TachyonRenderer(ambient_occlusion=True,
                                       ambient_occlusion_samples=8 if args.preview else rnd['ao_samples'],
                                       ambient_occlusion_brightness=rnd['ao_brightness'], antialiasing=True,
                                       antialiasing_samples=3 if args.preview else rnd['aa_samples'],
                                       direct_light=True, direct_light_intensity=rnd['direct_light'],
                                       shadows=rnd['shadows'])
    ads_list = ads.tolist()
    for name, a, pos in zip(names, atoms, P):
        disp, rad, col = [], [], []
        for i, shift in patch:
            disp.append(a.positions[i] + shift)
            rad.append(radii[sym[i]])
            shade = 1.0 - st['layer_darkening'] * layer_of[i]
            col.append(tuple(shade * c for c in colors[sym[i]]))
        for j in ads_list:
            disp.append(pos[j])
            rad.append(radii[sym[j]])
            col.append(colors[sym[j]])
        disp = np.array(disp)
        transparent = []
        source_indices = [i for i,_ in patch] + ads_list
        image_shifts = patch_images + [None for _ in ads_list]
        focus_display = {}
        for i in set(focus) | set(cfg['cutaway']['atoms']):
            candidates = [k for k,source_index in enumerate(source_indices) if source_index == i]
            if not candidates:
                raise ValueError('A requested focus/cutaway atom was excluded by the display patch')
            focus_display[i] = min(candidates, key=lambda k: np.linalg.norm(disp[k]-pos[i]))
        for hidx in cfg['cutaway']['atoms']:
            ph, rh = disp[focus_display[hidx]], radii[sym[hidx]]
            for k, (i, _) in enumerate(patch):
                v = disp[k] - ph
                perp = v - d * (v @ d)
                if v @ d < 0 and np.linalg.norm(perp) < rad[k] + 0.5 * rh:
                    transparent.append(k)
        pix = {str(i): [w / 2 + (disp[focus_display[i]] - cam) @ right * scale, h / 2 - (disp[focus_display[i]] - cam) @ up * scale] for i in focus}
        meta['states'][name] = dict(
            file=f"{cfg['prefix']}_{name}.png", atom_pixels=pix, display_atoms=len(disp),
            transparent_display_atoms=sorted(set(transparent)),
            source_to_focus_display={str(i):focus_display[i] for i in focus},
            display_source_indices=source_indices, display_lattice_images=image_shifts,
            adsorbate_display_shifts_A={str(i):(pos[i]-a.positions[i]).tolist() for i in ads_list},
            distances_A={f'{i}-{j} {k}': a.get_distance(i, j, mic=True) for i, j, k in request})
        if args.verify_only:
            continue
        data = DataCollection()
        p = data.create_particles(count=len(disp))
        p.create_property('Position', data=disp)
        p.create_property('Radius', data=np.array(rad))
        p.create_property('Color', data=np.array(col))
        if transparent:
            tr = np.zeros(len(disp))
            tr[sorted(set(transparent))] = cfg['cutaway']['transparency']
            p.create_property('Transparency', data=tr)
        p.vis.rendering_quality = type(p.vis.rendering_quality).HighQuality
        first = len(patch)
        pairs = []
        for x, i in enumerate(ads_list):
            for y in range(x + 1, len(ads_list)):
                j = ads_list[y]
                if a.get_distance(i, j, mic=True) < st['bond_factor'] * (covalent_radii[a.numbers[i]] + covalent_radii[a.numbers[j]]):
                    pairs.append((first + x, first + y))
        if pairs:
            b = p.create_bonds(count=len(pairs), vis_params={'width': st['bond_width']})
            b.create_property('Topology', data=pairs)
        pipe = Pipeline(source=StaticSource(data=data))
        pipe.add_to_scene()
        try:
            vp = Viewport(type=Viewport.Type.Ortho, camera_dir=d, camera_up=normal, camera_pos=cam, fov=hh)
            vp.render_image(filename=str(out / meta['states'][name]['file']), size=(w, h),
                            background=tuple(st['background']), alpha=bool(cfg.get('transparent_background', False)), renderer=renderer)
        finally:
            pipe.remove_from_scene()
    for a, o0 in zip(atoms, original):
        assert np.array_equal(a.positions, o0), 'source coordinates were modified'
    meta['source_coordinates_unchanged'] = True
    if write_outputs:
        (out / f"{cfg['prefix']}_metadata.json").write_text(json.dumps(meta, indent=1))
    if args.strip and not args.verify_only:
        from PIL import Image
        ims = [Image.open(out / meta['states'][n]['file']) for n in names]
        strip = Image.new('RGB', (sum(i.width for i in ims), max(i.height for i in ims)), 'white')
        x = 0
        for im in ims:
            strip.paste(im, (x, 0))
            x += im.width
        strip.save(out / f"{cfg['prefix']}_strip.png")
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('job', type=Path)
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--verify-only', action='store_true')
    ap.add_argument('--strip', action='store_true')
    args = ap.parse_args()
    meta = render_surface_job(args.job,preview=args.preview,verify_only=args.verify_only,strip=args.strip)
    print(json.dumps(dict(status='verified' if args.verify_only else 'rendered',states=list(meta['states']),
                         radii=meta['radii'],radius_source=meta['radius_source'],
                         substrate_patch_atoms=meta['substrate_patch_atoms'])))


if __name__ == '__main__':
    main()
