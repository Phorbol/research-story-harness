"""Independent populations, a complete sign matrix and a linked value column."""
from common import *
import fitz


def bacterium(ax,x,y,r=1,fill=None):
 e=Ellipse((x,y),2*r,1.65*r,angle=25,fc=fill or C['culture_fill'],ec=C['culture_outline'],lw=.65)
 ax.add_patch(e)
 line(ax,[(x-.22*r,y+.55*r),(x+.22*r,y-.55*r)],color=C['culture_outline'],lw=.45)


def culture(ax,x,y,gid):
 # Vessel and contents are conceptual, not a measurement of volume or cell number.
 w=7.8;bottom=y-5.4;top=y+5.2
 path=MPath([(x-w/2,top),(x-w/2,bottom+2),(x-w/2,bottom),(x+w/2,bottom),(x+w/2,bottom+2),(x+w/2,top)], [1,2,4,4,4,2])
 patch=PathPatch(path,fc=C['culture_fill'],ec=C['culture_outline'],lw=.95);patch.set_gid(gid);ax.add_patch(patch)
 ax.add_patch(Ellipse((x,top),w,2,fc='white',ec=C['culture_outline'],lw=.8))
 line(ax,[(x-3.45,y+1.9),(x+3.45,y+1.9)],color=C['culture_outline'],lw=.55)
 for dx,dy in [(-1.3,-1.2),(1,-1.4),(-.4,-3.2)]:bacterium(ax,x+dx,y+dy,.9,fill='white')


def clone(ax,x,y,gid):
 # A clonal isolate icon; the drawn cocci do not encode abundance.
 a=Ellipse((x,y),10,9,fc=C['isolate_field'],ec='none');a.set_gid(gid);ax.add_patch(a)
 for dx,dy in [(-1.5,-.8),(1.4,-.8),(-.05,1.55)]:bacterium(ax,x+dx,y+dy,1.4,fill='white')


def draw(f=None,ax=None):
 if f is None:f,ax=fig(178,94)
 txt(ax,4,89,'Four independent isolates form one collateral relation',role='title')
 txt(ax,4,82,r'$\it{E.\ faecalis}$ V583',role='body')
 txt(ax,106,82,'15 testing drugs · sign only',role='subtitle',ha='center')
 txt(ax,158,82,'DAP → CRO',role='subtitle',ha='center',color=C['opposite_signs'])
 txt(ax,24,75.5,'DAP selection',role='subtitle',ha='center')
 txt(ax,24,70.7,'8 days; increasing concentration',role='note',ha='center')
 txt(ax,53,74,'Single-colony\nisolate',role='subtitle',ha='center',linespacing=1.2)
 ys=[60,47,34,21]
 # Larger experimental objects retain a continuous identity on each row.
 for dx,dy in [(-.75,0),(.75,0),(0,1.3)]:bacterium(ax,5.5+dx,66.4+dy,.85)
 line(ax,[(5.5,64.8),(5.5,21)],color=C['culture_outline'],lw=.9)
 for k,y in enumerate(ys):
  arrow(ax,(5.5,y),(18.7,y),color=C['culture_outline'],lw=.9)
  txt(ax,12,y+3.2,str(k+1),role='data_value',ha='center')
  culture(ax,24,y,f'Fig1:population-{k+1}')
  arrow(ax,(28.7,y),(46.5,y),color=C['culture_outline'],lw=.9)
  clone(ax,53,y,f'Fig1:single-colony-isolate-{k+1}')
  arrow(ax,(59,y),(72,y),color=C['culture_outline'],lw=.9)
 # Complete 15-column matrix: CRO has exactly the same position and cell width.
 gx=76.1;step=4.25;rmark=1.65
 crox=gx+3*step
 rect(ax,crox-2.15,17.3,4.3,47.2,C['focus_field'],C['opposite_signs'],.65,gid='Fig1:CRO-column-focus')
 for y in ys:line(ax,[(gx-2.1,y),(gx+14*step+2.1,y)],color=C['border'],lw=.45,zorder=.5)
 for j,t in enumerate(N):
  x=gx+j*step
  txt(ax,x,69.8,t,role='subtitle' if t=='CRO' else 'tick',ha='center',rotation=90,color=C['opposite_signs'] if t=='CRO' else INK)
  for k,row in enumerate(get('DAP',t)):
   v=row['value'];patch=Circle((x,ys[k]),rmark,fc=col(v),ec=C['muted'] if v==0 else col(v),lw=.5)
   patch.set_gid('Fig1:sign:'+row['id']);ax.add_patch(patch)
   txt(ax,x,ys[k],'−' if v<0 else '+' if v>0 else '0',role='sign_mark',ha='center',color='white' if v else INK)
 # A short, label-level connector identifies the numeric readout without cutting through data.
 line(ax,[(crox,73.3),(crox,76.4),(142.8,76.4)],color=C['opposite_signs'],lw=.8)
 arrow(ax,(142.8,76.4),(145,76.4),color=C['opposite_signs'],lw=.8)
 txt(ax,158,71.9,r'log₂(IC$_{50}$ /'+'\n'+r'ancestor IC$_{50}$)',role='note',ha='center',linespacing=1.25)
 for k,row in enumerate(get('DAP','CRO')):
  v=row['value'];t=txt(ax,158,ys[k],('+' if v>0 else '')+(f'{v:.2f}' if v else '0'),role='focus_value',ha='center',color=col(v) if v else INK)
  t.set_gid('Fig1:numeric:'+row['id'])
 # Secondary reading aids and study totals do not compete with the experimental unit.
 line(ax,[(gx-1.7,16),(gx+1.7,16)],color=INK,lw=.8)
 txt(ax,gx,12.7,'Direct',role='note',ha='center')
 for x,v,label in [(88,-1,'Sensitive'),(112,1,'Resistant'),(138,0,'Threshold zero')]:
  a=Circle((x,12.7),1.15,fc=col(v),ec=C['muted'] if v==0 else col(v),lw=.4);ax.add_patch(a)
  txt(ax,x+2.6,12.7,label,role='note')
 txt(ax,31,12.7,'Four independent populations',role='note',ha='center')
 line(ax,[(4,8.4),(174,8.4)],color=C['border'],lw=.6)
 txt(ax,4,5.5,'15 selections × 4 isolates × 15 test drugs = 900 values',role='body')
 txt(ax,4,2.1,'60 direct responses excluded → 840 collateral values → 210 directed drug pairs',role='note')
 return f


