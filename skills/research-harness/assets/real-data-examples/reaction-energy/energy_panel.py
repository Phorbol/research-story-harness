# Adapted from aicat-network-transfer reconstruction/energy_panel.py.
# Source and limitations: SOURCES.md.
"""Smooth guides through source-bound stationary levels, not a sampled PES."""
import json
from pathlib import Path
import numpy as np
CONFIG=json.loads((Path(__file__).resolve().parent/'config.json').read_text())
SIZE=CONFIG['text_roles_pt'];WEIGHT=CONFIG['text_weights']
BLUE=CONFIG['colors']['blue'];RED=CONFIG['colors']['red'];INK=CONFIG['colors']['ink'];MUTED='#58656A'
COLORS={'deH12':BLUE,'deH13':RED,'water12':BLUE,'water13':RED}
def draw_energy_panel(fig):
    import csv
    root=Path(__file__).resolve().parent
    rows=list(csv.DictReader((root/'data/energy-values.csv').open()))
    data={'paths':[{'id':pid,'levels':[{'state':r['state'],'type':'transition' if r['state'].startswith('TS') else 'minimum','g_eV':float(r['G'])} for r in rows if r['path']==pid]} for pid in ['deH12','deH13','water12','water13']]}
    ax=fig.add_axes([.085,.405,.895,.49])
    positions={'deH12':[0,.7,1.4,2.1,2.8,3.5,4.35,5.15],
               'deH13':[0,.7,1.4,2.1,2.8,3.5,4.35,5.15],
               'water12':[0,.7,1.4,2.1,2.8,3.5],
               'water13':[0,.7,1.4,2.1,2.8,3.5]}
    for path in data['paths']:
        pid=path['id']; levels=list(path['levels']); xs=list(positions[pid])
        if pid=='deH12': xs.extend([8.2,9.0,9.8,10.6,11.4,12.2,13.0,13.8])
        col=COLORS[pid]; dash=(0,(3.4,2)) if pid.startswith('water') else '-'
        for i,level in enumerate(levels):
            x,y=xs[i],level['g_eV']; half=.10 if level['type']=='minimum' else 0
            left,right=x-half,x+half
            if pid=='deH12' and i==7:right=7.45
            if half and (i>1 or pid=='deH12'):
                ax.plot([left,right],[y,y],color=col if i>1 else INK,lw=1.0,zorder=3)
            if i==len(levels)-1:continue
            nx=xs[i+1]-(.10 if levels[i+1]['type']=='minimum' else 0)
            ny=levels[i+1]['g_eV'];t=np.linspace(0,1,65)
            yy=y+(ny-y)*(3*t*t-2*t*t*t)
            if i>0 or pid=='deH12':ax.plot(right+(nx-right)*t,yy,color=col,lw=1.05,ls=dash,zorder=2)
        if pid!='deH12':ax.plot(xs[-1]+.10,levels[-1]['g_eV'],marker='o',ms=2.7,mfc='white',mec=col,mew=.7,zorder=5)
    ax.spines[['top','right']].set_visible(False)
    ax.axhline(0,color='#C4C8CA',lw=.4,zorder=0)
    ax.set_xlim(-.3,15.2);ax.set_ylim(-1.72,2.08)
    ax.set_yticks([-1.5,-1,-.5,0,.5,1,1.5,2]);ax.set_xticks([])
    ax.tick_params(axis='y',labelsize=SIZE['tick'],pad=2,length=2,width=.55)
    ax.set_ylabel('Gibbs free energy (eV)',fontsize=SIZE['axis'],labelpad=3)
    ax.set_xlabel('Reaction sequence',fontsize=SIZE['axis'],labelpad=4)
    fig.text(.025,.90,'a',fontsize=SIZE['panel'],weight=WEIGHT['panel'],color=INK)
    from matplotlib.lines import Line2D
    handles=[Line2D([],[],color=COLORS[pid],lw=1.2,ls=(0,(3.4,2)) if pid.startswith('water') else '-',label=name) for pid,name in [('deH12','1,2-PDO · deH'),('deH13','1,3-PDO · deH'),('water12','1,2-PDO · deH₂O'),('water13','1,3-PDO · deH₂O')]]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.535,.995),ncol=4,frameon=False,fontsize=SIZE['legend'],handlelength=1.7,columnspacing=1.2)
    def label(x,y,t,pid=None,ha='center',weight=WEIGHT['body'],fs=SIZE['annotation']):
        ax.text(x,y,t,fontsize=fs,color=COLORS[pid] if pid else INK,ha=ha,va='center',weight=weight)
    label(0,-.17,'G(g)');label(.7,.40,'G*')
    label(2.10,-.22,'2','deH12',weight=WEIGHT['emphasis']);label(2.1,.33,'3','deH13',weight=WEIGHT['emphasis'])
    label(3.91,.29,'8','deH12',weight=WEIGHT['emphasis']);label(3.50,.94,'9','deH13',weight=WEIGHT['emphasis'])
    label(2.06,1.24,'7','water12',weight=WEIGHT['emphasis']);label(2.05,.82,'1','water13',weight=WEIGHT['emphasis'])
    for x,y,t,pid in [(4.8,1.18,'TS1  1.164','deH12'),(4.8,1.49,'TS2  1.442','deH13'),
                      (3.15,1.59,'TS3  1.705','water13'),(3.15,1.81,'TS4  1.764','water12')]:
        level_name=t.split()[0]
        numeric=next(r['G'] for r in rows if r['path']==pid and r['state']==level_name)
        label(x,y,level_name,pid,ha='left',weight=WEIGHT['emphasis'])
    label(3.55,.05,'13','water12',weight=WEIGHT['emphasis']);label(3.55,.65,'14','water13',weight=WEIGHT['emphasis'])
    label(5.35,.17,'enol + OH*','deH13',ha='left',fs=SIZE['small'])
    label(6.20,-.22,'6 + OH*','deH12',fs=SIZE['annotation'])
    label(9.00,-.72,'acetol*','deH12',fs=SIZE['annotation'])
    label(10.6,-.87,'acetol*\n+ H₂O*','deH12',fs=SIZE['small'])
    label(12.20,-1.28,'11','deH12',weight=WEIGHT['emphasis'])
    label(13.83,-1.48,'1,2-PDO(g) + H₂O*','deH12',fs=SIZE['small'])
    label(9.7,.43,'OH* → H₂O*','deH12',fs=SIZE['small'])
    return ax
