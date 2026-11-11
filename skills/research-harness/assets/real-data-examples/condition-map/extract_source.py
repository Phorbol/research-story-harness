"""Optional: recreate editable CSVs directly from the included author H5 files."""
from pathlib import Path
import csv,h5py
R=Path(__file__).resolve().parent
for name in ['data_a','data_b','data_tv_t','data_tv_time']:
 with h5py.File(R/'source'/f'{name}.h5') as f:
  d=f['data']
  with (R/'data'/f'{name}.csv').open('w',newline='') as out:
   w=csv.writer(out)
   if name in ['data_a','data_b']:
    x=d['descr_all'][()];y=d['prod_conc_'][()];w.writerow(['id','descriptor','L','B']);w.writerows((i,xx,y[0,i],y[1,i]) for i,xx in enumerate(x))
   else:
    x=d['xint'][()];t=d['t_points'][()];y=d['grid'][()];w.writerow(['id','descriptor','condition','L','B'])
    w.writerows((f'{i}_{j}',xx,tt,y[0,i,j],y[1,i,j]) for i,xx in enumerate(x) for j,tt in enumerate(t))
