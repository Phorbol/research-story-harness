"""Resolve editable scene groups and semantic ports without changing scientific objects.

Coordinates are canvas units (use mm for publication scenes), y increases upward.
Layout is deterministic. It does not choose the story or certify aesthetics.
"""
import copy
import math

PORTS = {'center': (.5,.5), 'north': (.5,1), 'south': (.5,0),
         'east': (1,.5), 'west': (0,.5), 'northwest': (0,1),
         'northeast': (1,1), 'southwest': (0,0), 'southeast': (1,0)}


def finite(values):
    return all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in values)


def bounds(obj):
    if 'box' in obj:
        x,y,w,h=obj['box'];return [x,y,w,h]
    if 'extent' in obj:
        l,r,b,t=obj['extent'];return [l,b,r-l,t-b]
    if obj.get('type')=='text' and 'xy' in obj:
        x,y=obj['xy'];return [x,y,0,0]
    if 'points' in obj:
        xs,ys=zip(*obj['points']);return [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]
    raise ValueError('Object has no anchorable geometry: '+obj['id'])


def port(obj, name):
    if name not in PORTS:raise ValueError('Unknown anchor port: '+str(name))
    x,y,w,h=bounds(obj);u,v=PORTS[name];return [x+u*w,y+v*h]


def resolve(scene):
    out=copy.deepcopy(scene);objects=out['objects'];byid={o['id']:o for o in objects}
    groups=out.get('layout',{}).get('groups',[])
    placed=set()
    for group in groups:
        box=group.get('box')
        if box is None:
            box=bounds(byid[group['parent']]);p=group.get('padding',0)
            box=[box[0]+p,box[1]+p,box[2]-2*p,box[3]-2*p]
        x,y,w,h=box;children=group['children'];n=len(children);gap=group.get('gap',0)
        direction=group['direction'];weights=group.get('weights',[1]*n)
        if direction not in {'row','column'} or not n or len(weights)!=n or not finite(weights) or min(weights)<=0:
            raise ValueError('Layout group needs row/column, children and positive weights')
        total=(w if direction=='row' else h)-gap*(n-1)
        if not finite(box+[gap]) or min(w,h,total)<=0 or gap<0:raise ValueError('Layout does not fit its frame')
        cursor=x if direction=='row' else y+h
        for id,weight in zip(children,weights):
            if id in placed:raise ValueError('Object occurs in multiple layout groups: '+id)
            obj=byid[id]
            if obj['type'] not in {'rect','ellipse','image','sphere','shadow'}:raise ValueError('Grouped children need rectangular bounds')
            size=total*weight/sum(weights)
            cell=[cursor,y,size,h] if direction=='row' else [x,cursor-size,w,size]
            if obj['type']=='image':obj['extent']=[cell[0],cell[0]+cell[2],cell[1],cell[1]+cell[3]]
            else:obj['box']=cell
            placed.add(id);cursor+=(size+gap)*(1 if direction=='row' else -1)
    pending=[o for o in objects if 'anchor' in o]
    while pending:
        remaining=[];resolved=False;pending_ids={o['id'] for o in pending}
        for obj in pending:
            a=obj['anchor'];target=a['object']
            if target in pending_ids:remaining.append(obj);continue
            xy=port(byid[target],a.get('port','center'));offset=a.get('offset',[0,0])
            if len(offset)!=2 or not finite(offset):raise ValueError('Invalid anchor offset')
            xy=[xy[i]+offset[i] for i in range(2)]
            if obj['type']=='text':obj['xy']=xy
            elif obj['type'] in {'rect','ellipse','image','sphere','shadow'}:
                w,h=obj['size'];u,v=PORTS[a.get('self_port','center')];x,y=xy[0]-u*w,xy[1]-v*h
                if obj['type']=='image':obj['extent']=[x,x+w,y,y+h]
                else:obj['box']=[x,y,w,h]
            else:raise ValueError('Anchors support text and bounded objects')
            resolved=True
        if not resolved:raise ValueError('Cyclic anchors: '+', '.join(o['id'] for o in remaining))
        pending=remaining
    for edge in out.get('connections',[]):
        if 'draw' not in edge:continue
        d=edge['draw'];id='connection-'+edge['id']
        if id in byid:raise ValueError('Generated connection ID collides: '+id)
        start=port(byid[edge['from']],d.get('from_port','east'))
        end=port(byid[edge['to']],d.get('to_port','west'))
        obj=dict(type='arrow',id=id,semantic_id=edge['id'],start=start,end=end,z=4,**{
            k:d[k] for k in ('color','color_role','lw','head','linestyle','connectionstyle','arrowstyle') if k in d})
        if d.get('via'):obj['route_points']=[start]+d['via']+[end]
        obj['_connection']={'id':edge['id'],'from':edge['from'],'to':edge['to'],
                            'from_port':d.get('from_port','east'),'to_port':d.get('to_port','west')}
        objects.append(obj);byid[id]=obj
    return out


def geometry_errors(scene):
    errors=[];w,h=scene['canvas']
    if not finite([w,h]) or min(w,h)<=0:return ['Canvas must have positive finite dimensions']
    strict=scene.get('schema_version',1)>=2
    for o in scene['objects']:
        if o['type']=='arrow':points=o.get('route_points',[o['start'],o['end']])
        elif strict:
            x,y,b,t=bounds(o);points=[[x,y],[x+b,y+t]]
            if b<0 or t<0:errors.append(o['id']+': reversed geometry')
        else:continue
        if any(len(p)!=2 or not finite(p) for p in points):errors.append(o['id']+': nonfinite coordinates')
        elif any(not(-1e-7<=x<=w+1e-7 and -1e-7<=y<=h+1e-7) for x,y in points):
            errors.append(o['id']+': geometry outside canvas')
    return errors
