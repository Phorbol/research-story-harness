"""Drug-pair map and exact response examples from published data."""
from common import *

def example(ax,x,y,w,h,s,t,panel,summary):
 rect(ax,x-9,y+h+6.5,5,5,C['opposite_signs'] if s=='DAP' else C['sensitive'])
 txt(ax,x-6.5,y+h+9,panel,role='panel',ha='center',color='white');txt(ax,x,y+h+9,s+' → '+t,role='subtitle')
 txt(ax,x,y+h+4.5,summary,role='note')
 xmin=-10;xmax=3;px=lambda v:x+(v-xmin)/(xmax-xmin)*w
 line(ax,[(px(0),y-2),(px(0),y+h)],color=C['muted'],lw=.7)
 for k,r in enumerate(get(s,t)):
  yy=y+h-3-k*(h-5)/3
  line(ax,[(px(0),yy),(px(r['value']),yy)],color=col(r['value']),lw=1.1)
  a=Circle((px(r['value']),yy),.85,fc=col(r['value']),ec=C['muted'] if not r['value'] else 'white',lw=.5);a.set_gid('Evidence:'+r['id']);ax.add_patch(a)
  txt(ax,x-2.2,yy,str(k+1),role='tick',ha='right')
  txt(ax,px(r['value']),yy+2.6,f"{r['value']:.2f}" if r['value'] else '0',role='data_value',ha='center')
 line(ax,[(x,y-2),(x+w,y-2)],color=C['border'])
 for val in [-8,-4,0,2]:
  line(ax,[(px(val),y-2),(px(val),y-2.8)],color=C['muted'],lw=.5);txt(ax,px(val),y-5.5,str(val).replace('-','−'),role='tick',ha='center')

def evidence_final(f=None,ax=None):
 if f is None:f,ax=fig(178,126)
 txt(ax,4,121,'Sign agreement depends on the drug pair',role='title')
 txt(ax,174,121,'210 directed pairs',role='subtitle',ha='right')
 counts=Counter(cat(get(s,t)) for s in N for t in N if s!=t)
 labs=['4/4 sensitive','4/4 resistant','Opposite signs','One sign + zero','4/4 threshold zero']
 xs=[4,38,72,106,140]
 for k,x in enumerate(xs):
  rect(ax,x,106.3,2.8,8.5,CC[k],C['border'],.5)
  txt(ax,x+4.5,112.9,str(counts[k]),role='subtitle',color=CC[k] if k<3 else INK)
  txt(ax,x+4.5,107.5,labs[k],role='note')
 line(ax,[(4,103),(174,103)],color=C['border'],lw=.6)
 txt(ax,4,99.4,'a',role='panel');txt(ax,10,99.4,'Drug-pair map',role='subtitle')
 mx=18;my=25;size=70;step=size/15
 for i,t in enumerate(N):
  for j,s in enumerate(N):
   xx=mx+j*step;yy=my+(14-i)*step
   rect(ax,xx,yy,step,step,CC[cat(get(s,t))] if i!=j else C['direct_response'],C['border'] if i!=j and cat(get(s,t))==4 else 'white',.45,gid=f'Evidence:pair:{s}-{t}')
   if i==j:line(ax,[(xx+1.6,yy+3.1),(xx+3.1,yy+1.6)],color=C['one_sign_plus_zero'],lw=.6)
 for i,n in enumerate(N):
  txt(ax,mx-1.7,my+(14-i)*step+step/2,n,role='tick',ha='right')
  txt(ax,mx+i*step+step/2,my-4.5,n,role='tick',ha='center',rotation=90)
 txt(ax,53,14.4,'Selecting drug',role='axis',ha='center')
 txt(ax,4,my+size/2,'Testing drug',role='axis',ha='center',rotation=90)
 for s,t,letter in [('DAP','CRO','b'),('CRO','RIF','c')]:
  j=N.index(s);i=N.index(t);xx=mx+j*step;yy=my+(14-i)*step
  rect(ax,xx+.1,yy+.1,step-.2,step-.2,'none',INK,1.3)
  rect(ax,xx+.45,yy+.45,step-.9,step-.9,'none','white',.4)
  txt(ax,xx+step/2,yy+step/2,letter,role='example_locator',ha='center',color='white')
 example(ax,116,69,55,22,'DAP','CRO','b','Opposite signs across isolates')
 example(ax,116,27,55,22,'CRO','RIF','c','All four more sensitive')
 txt(ax,143,14.4,r'log₂(IC$_{50}$ / ancestor IC$_{50}$)',role='axis',ha='center')
 txt(ax,105,80,'Isolate',role='axis',ha='center',rotation=90)
 txt(ax,105,38,'Isolate',role='axis',ha='center',rotation=90)
 txt(ax,4,7,'Each map cell: four independent isolates. Diagonal: direct response, excluded.',role='note')
 txt(ax,4,3.3,'Responses relative to the ancestor; counts are not future probabilities.',role='note')
 return f

