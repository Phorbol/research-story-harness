"""Create a shared display scene from complete finite, fully occupied ASE-readable coordinates."""
import argparse,json
from pathlib import Path
import numpy as np
from ase.io import read
from ase.data import covalent_radii,atomic_numbers
from ase.data.colors import jmol_colors
p=argparse.ArgumentParser(description=__doc__);p.add_argument('structure');p.add_argument('--style',required=True);p.add_argument('--origin',required=True,choices=['experimental','calculated','idealized','generated-conformer']);p.add_argument('--bonds',help='Explicit JSON list of {a,b,order,aromatic}; no distance guessing');p.add_argument('--out',required=True);args=p.parse_args()
a=read(args.structure);cfg=json.loads(Path(args.style).read_text())
if a.pbc.any() or a.info.get('occupancy'):raise ValueError('This lightweight adapter is for finite fully occupied objects; use ovito-structure for periodic/mixed-site preparation.')
if not len(a) or not np.isfinite(a.positions).all():raise ValueError('Empty or nonfinite coordinates')
colors={e:'#'+''.join(f'{round(float(v)*255):02X}' for v in jmol_colors[atomic_numbers[e]]) for e in set(a.get_chemical_symbols())};colors.update(cfg.get('colors',{}))
radii={e:float(covalent_radii[atomic_numbers[e]])*.72 for e in set(a.get_chemical_symbols())};radii.update(cfg.get('radii',{}))
bonds=json.loads(Path(args.bonds).read_text()) if args.bonds else []
for b in bonds:
 if not all(isinstance(b[k],int) and 0<=b[k]<len(a) for k in ['a','b']) or b['a']==b['b']:raise ValueError('Bond indices outside source topology')
s={'name':Path(args.structure).stem,'origin':{'kind':args.origin,'source':str(Path(args.structure).resolve())},'units':'angstrom','positions':a.positions.tolist(),'elements':a.get_chemical_symbols(),'tags':a.get_tags().tolist(),'colors':colors,'radii':radii,'bonds':bonds,'camera':cfg['camera'],'size':cfg.get('size',[1500,1100])}
Path(args.out).write_text(json.dumps(s,indent=2));print(args.out)
