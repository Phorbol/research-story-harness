"""Shared source-backed plotting helpers for the three-figure example."""
import csv,json,math,sys,shutil
from pathlib import Path
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Ellipse,Rectangle,FancyArrowPatch,FancyBboxPatch,PathPatch
from matplotlib.path import Path as MPath
P=Path(__file__).resolve().parents[1]; ROOT=P.parent
STYLE=json.loads((P/'style-profile.json').read_text()); C=STYLE['semantic_colors']; INK=STYLE['text_color']
plt.rcParams.update({'font.family':STYLE['font_family'],'svg.fonttype':'none','pdf.fonttype':42,'axes.unicode_minus':True})
rows=list(csv.DictReader((P/'data/collateral.csv').open()))
for r in rows:r['value']=float(r['value'])
N=['DAP','AMP','OXA','CRO','FOF','TET','DOX','TGC','SPT','LZD','CHL','CIP','LVX','NIT','RIF']
CATS=['All sensitive','All resistant','Opposite signs','One sign + zero','All zero']
CC=[C[k] for k in ['sensitive','resistant','opposite_signs','one_sign_plus_zero','all_zero']]
def get(s,t):return sorted([r for r in rows if r['selecting']==s and r['testing']==t],key=lambda r:int(r['replicate']))
def cat(rs):
 a=sum(r['value']<0 for r in rs);b=sum(r['value']>0 for r in rs)
 return 0 if a==4 else 1 if b==4 else 2 if a and b else 4 if a+b==0 else 3
def col(v):return C['sensitive'] if v<0 else C['resistant'] if v>0 else C['within_threshold']
def txt(ax,x,y,s,role='body',ha='left',color=None,**kw):
 d=STYLE['roles'][role];t=ax.text(x,y,s,fontsize=d['size_pt'],fontweight=d['weight'],fontstyle=d['style'],ha=ha,va='center',color=color or INK,**kw);t._role=role;t._research_role=role;return t
def rect(ax,x,y,w,h,fc,ec='none',lw=.6,gid=None):
 a=Rectangle((x,y),w,h,fc=fc,ec=ec,lw=lw);a.set_gid(gid);ax.add_patch(a);return a
def line(ax,xy,color=None,lw=.7,**kw):return ax.plot(*zip(*xy),color=color or C['border'],lw=lw,**kw)[0]
def arrow(ax,a,b,color=None,lw=.8,rad=0):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=6,lw=lw,color=color or C['muted'],connectionstyle=f'arc3,rad={rad}'))
def cell(ax,x,y,r=1.5,v=None,gid=None):
 c=C['organism_fill'] if v is None else col(v);ec=C['muted'] if v is None or v==0 else c
 e=Ellipse((x,y),2*r,1.7*r,angle=25,fc=c,ec=ec,lw=.65);e.set_gid(gid);ax.add_patch(e)
 # septum gives bacterial identity, not a molecular mechanism
 line(ax,[(x-.25*r,y+.65*r),(x+.25*r,y-.65*r)],color='white' if v is not None and v else C['muted'],lw=.45)
def colony(ax,x,y,r=1,v=None):
 for dx,dy in [(-.8,-.2),(.85,-.2),(0,1.2)]:cell(ax,x+dx*r,y+dy*r,r,v)
def fig(w,h):
 f=plt.figure(figsize=(w/25.4,h/25.4));ax=f.add_axes([0,0,1,1]);ax.set(xlim=(0,w),ylim=(0,h));ax.axis('off');return f,ax

