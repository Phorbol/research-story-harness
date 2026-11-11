# Adapted from acs-volcano-transfer final/generator/volcano_figure.py.
# Data attribution and boundaries: SOURCES.md.
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.lines import Line2D
import json
CONFIG=json.loads((Path(__file__).resolve().parent/'config.json').read_text())
SIZE=CONFIG['text_roles_pt']; WEIGHT=CONFIG['text_weights']
VERSION='typography-refinement-v1'
L=CONFIG['colors']['linear']; B=CONFIG['colors']['branched']; INK='#20282C'; GRAY='#697074'
DESC=r'$\Delta G_{\mathrm{RRS}}(\mathrm{INT4L})$ (kcal mol$^{-1}$)'
CMAP=LinearSegmentedColormap.from_list('B_to_L',[B,'#69B2B7','#FAFAF7','#DEA876',L],N=256)

def data(root,name): return np.genfromtxt(Path(root)/'data'/name,delimiter=',',names=True,dtype=None,encoding='utf8')
def styling():
 mpl.rcParams.update({'font.family':CONFIG['font_family'],'font.weight':WEIGHT['body'],'font.style':'normal','font.size':SIZE['body'],'axes.labelsize':SIZE['axis'],'axes.titlesize':SIZE['title'],'xtick.labelsize':SIZE['tick'],'ytick.labelsize':SIZE['tick'],'axes.linewidth':.65,'xtick.major.width':.55,'ytick.major.width':.55,'xtick.major.size':2.8,'ytick.major.size':2.8,'axes.spines.top':False,'axes.spines.right':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})

def refs(ax,labels=True):
 for item in CONFIG['references']:
  name,x=item['name'],item['descriptor'];col=GRAY if name=='L1' else INK
  ax.axvline(x,c=col,lw=.5,ls=(0,(3,2)),zorder=3)
  if labels: ax.text(x+.5,.96,name,transform=ax.get_xaxis_transform(),va='top',ha='left',fontsize=SIZE['small'],color=col,fontweight=WEIGHT['emphasis'] if name=='L2' else WEIGHT['body'])

def volcano(ax,root,name,title,letter,bind=lambda a,b:None):
 d=data(root,name)
 for field,c,ls in [('L',L,'-'),('B',B,'--')]:
  line,=ax.plot(d['descriptor'],d[field],c=c,lw=1.25,ls=ls,label=field,zorder=4);bind(line,f'{letter}:concentration:{field}')
 for field,c in [('L',L),('B',B)]:
  ax.plot(CONFIG['references'][1]['descriptor'],np.interp(CONFIG['references'][1]['descriptor'],d['descriptor'],d[field]),'o',ms=2.8,mec='white',mew=.45,color=c,zorder=6)
 anchor=CONFIG['references'][1]['descriptor']; lv=np.interp(anchor,d['descriptor'],d['L']);bv=np.interp(anchor,d['descriptor'],d['B'])
 ratio=f'L:B {lv/bv:.1f}:1' if lv>=bv else f'B:L {bv/lv:.1f}:1'
 ax.text(-13.8 if letter=='a' else -11.5,.89 if letter=='a' else .94,ratio,fontsize=SIZE['annotation'],color=L if lv>=bv else B)
 refs(ax);ax.set(xlim=(-30,20),ylim=(0,1.08),xticks=[-30,-20,-10,0,10,20],yticks=[0,.25,.5,.75,1]);ax.set_yticklabels(['0','0.25','0.50','0.75','1.00'])
 ax.set_ylabel('Product concentration (M)');ax.set_xlabel(DESC,labelpad=2.5);ax.set_title(title,loc='left',pad=7,fontweight=WEIGHT['body'])
 ax.text(-.21,1.08,letter,transform=ax.transAxes,fontweight=WEIGHT['panel'],fontsize=SIZE['panel'])

def condition(ax,root,name,title,letter,bind=lambda a,b:None):
 d=data(root,name); x=np.unique(d['descriptor']);t=np.unique(d['condition']);a=d['L'].reshape(len(x),len(t));b=d['B'].reshape(a.shape)
 with np.errstate(divide='ignore',invalid='ignore'): z=np.log10(a/b)
 z=np.ma.masked_invalid(np.clip(z,-2,2))
 ax.set_facecolor('#D9DDDE')
 dx=x[1]-x[0];dt=t[1]-t[0]
 mesh=ax.imshow(z.T,origin='lower',extent=[x[0]-dx/2,x[-1]+dx/2,t[0]-dt/2,t[-1]+dt/2],cmap=CMAP,norm=Normalize(-2,2),aspect='auto',interpolation='nearest');bind(mesh,f'{letter}:log10_L_B')
 ax.contour(x,t,z.T,levels=[0],colors=[INK],linewidths=.7)
 refs(ax)
 ax.set(xlim=(-30,20),xticks=[-30,-20,-10,0,10,20]);ax.set_xlabel(DESC,labelpad=2.5)
 if letter=='c':
  ax.set(ylim=(280,400),yticks=[280,310,340,370,400],ylabel='Temperature (K)')
  for y,label in [(298.15,'a'),(353.15,'b')]:
   ax.axhline(y,c=INK,lw=.7,ls=(0,(1,2)));ax.text(19,y+2,CONFIG['annotation_labels']['temperature_slices'][label],ha='right',fontsize=SIZE['annotation'],fontweight=WEIGHT['body'])
 else:
  times=np.array([2,6,24,72]); ax.set(ylim=(3.8,5.6),yticks=np.log10(times*3600),yticklabels=[str(x) for x in times],ylabel='Reaction time (h; log scale)')
  ax.axhline(np.log10(24*3600),c=INK,lw=.7,ls=(0,(1,2)))
  ax.text(19,np.log10(24*3600)+.035,'24 h',ha='right',fontsize=SIZE['small'])
 ax.set_title(title,loc='left',pad=7,fontweight=WEIGHT['body']);ax.text(-.21,1.08,letter,transform=ax.transAxes,fontweight=WEIGHT['panel'],fontsize=SIZE['panel'])
 return mesh

def draw(fig,root,bind=lambda a,b:None,version='v1',clear=True):
 styling();fig.set_size_inches(*(v/25.4 for v in CONFIG['figure_mm']));
 if clear: fig.clear()
 axs=[fig.add_axes(z) for z in CONFIG['layout']['axes_rects']]
 volcano(axs[0],root,'data_a.csv',CONFIG['titles'][0],'a',bind);volcano(axs[1],root,'data_b.csv',CONFIG['titles'][1],'b',bind)
 condition(axs[2],root,'data_tv_t.csv',CONFIG['titles'][2],'c',bind);m=condition(axs[3],root,'data_tv_time.csv',CONFIG['titles'][3],'d',bind)
 fig.legend(handles=[Line2D([0],[0],c=L,lw=1.5,label='Linear (L)'),Line2D([0],[0],c=B,lw=1.5,ls='--',label='Branched (B)')],loc='upper center',bbox_to_anchor=(.53,.995),ncol=2,frameon=False,fontsize=SIZE['legend'],handlelength=2.5,columnspacing=3)
 cax=fig.add_axes([.25,.075,.58,.018]);cbar=fig.colorbar(m,cax=cax,orientation='horizontal',ticks=[-2,-1,0,1,2]);cbar.ax.set_xticklabels(['1:100','1:10','1:1','10:1','100:1']);cbar.outline.set_linewidth(.45);cbar.ax.tick_params(labelsize=SIZE['colorbar'],pad=2,length=2)
 cbar.set_label('Product ratio L:B  (logarithmic color scale)',fontsize=SIZE['colorbar'],labelpad=2)
 fig.add_artist(Line2D([.10,.135],[CONFIG['layout']['footer_y']]*2,transform=fig.transFigure,color=INK,lw=.7))
 fig.text(.145,CONFIG['layout']['footer_y'],'L = B (model)',fontsize=SIZE['annotation'],va='center')
 from matplotlib.patches import Rectangle
 fig.add_artist(Rectangle((.59,CONFIG['layout']['footer_y']-.006),.012,.012,transform=fig.transFigure,facecolor='#D9DDDE',edgecolor='#9A9FA1',lw=.35))
 fig.text(.615,CONFIG['layout']['footer_y'],'Undefined (0/0)',fontsize=SIZE['annotation'],va='center')
 return axs

def render_figure(spec,project,root,fig,ax,bind,load_data):
 ax.set_visible(False)
 draw(fig,root,bind,version=spec.get('version','v2'),clear=False)

