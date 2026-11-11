"""Construct idealized, unrelaxed particle/support illustrations, not paper coordinates.

Both models share geometry and substitution sites. No phase stability, interface
registry, contact angle, adsorption site or catalytic mechanism is inferred.
"""
from pathlib import Path
import argparse,json,numpy as np
from ase.build import bulk
from ase.io import write
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',default='rebuilt-models');args=p.parse_args()
out=Path(args.out);out=out if out.is_absolute() else ROOT/out;out.mkdir(parents=True,exist_ok=True)
support=bulk('ZnO','wurtzite',a=3.25,c=5.21,u=.382).repeat((16,14,2))
support.positions[:,:2]-=support.positions[:,:2].mean(axis=0)
support=support[(abs(support.positions[:,0])<20)&(abs(support.positions[:,1])<15)]
support.positions[:,2]-=support.positions[:,2].min()
cluster=bulk('Pd','fcc',a=3.89,cubic=True).repeat((9,9,9))
cluster.positions-=cluster.positions.mean(axis=0);cluster.rotate((1,1,1),(0,0,1),rotate_cell=True)
rr=np.linalg.norm(cluster.positions,axis=1);cluster=cluster[(rr<13.5)&(cluster.positions[:,2]>-1.0)]
cluster.positions[:,2]-=cluster.positions[:,2].min();cluster.positions[:,2]+=support.positions[:,2].max()+2.45
rng=np.random.default_rng(17);indices=np.sort(rng.choice(len(cluster),size=round(len(cluster)*.35),replace=False))
models={}
for alloy in ['Zn','Cu']:
 c=cluster.copy();symbols=c.get_chemical_symbols()
 for i in indices:symbols[i]=alloy
 c.set_chemical_symbols(symbols);a=support+c;a.pbc=False;a.set_cell([50,45,40]);a.set_tags([0]*len(support)+[1]*len(c))
 a.info.update(model_origin='constructed_illustration',not_paper_coordinates=True,not_relaxed=True)
 name='illustrative-Pd'+alloy+'-ZnO.extxyz';write(out/name,a)
 models[alloy]=dict(path=name,atoms=len(a),support_atoms=len(support),particle_atoms=len(c),substitution_count=len(indices),formula=a.get_chemical_formula())

record=dict(origin='constructed_illustration',not_paper_coordinates=True,not_relaxed=True,same_geometry_both_models=True,parameter_status='Illustration choices only; not fitted, relaxed, or scientific defaults.',parameters=dict(Pd_fcc_a_A=3.89,ZnO_wurtzite_a_A=3.25,ZnO_c_A=5.21,ZnO_u=.382,particle_radius_A=13.5,substitution_fraction=.35,random_seed=17,vertical_gap_A=2.45),models=models)
(out/'construction.json').write_text(json.dumps(record,indent=2))
print(json.dumps(models,indent=2))
