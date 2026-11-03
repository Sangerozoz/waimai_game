"""Author one complete-region structural guide from source geometry; no sprite composition."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];source=Path('delivery-game/assets/resources/map-sample/city.json');city=json.loads(source.read_text());nodes={n['id']:[n['x'],n['y']] for n in city['nodes']}
bounds=dict(minX=-1640,maxX=-1520,minY=20,maxY=140);origin=[-1580,80];theta=math.radians(62.5);q=math.sqrt(.5);s=math.sin(theta);c=math.cos(theta)
P=7.8;offset=[768,810]
def project(p):
    x,y=p[0]-origin[0],p[1]-origin[1];z=p[2] if len(p)>2 else 0;return [offset[0]+P*(x-y)*q,offset[1]+P*((x+y)*s*q-z*c)]
def inside(p):return bounds['minX']<=p[0]<=bounds['maxX'] and bounds['minY']<=p[1]<=bounds['maxY']
def clip(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];lo,hi=0.,1.
    for p,z in [(-dx,a[0]-bounds['minX']),(dx,bounds['maxX']-a[0]),(-dy,a[1]-bounds['minY']),(dy,bounds['maxY']-a[1])]:
        if abs(p)<1e-12:
            if z<0:return None
        elif p<0:lo=max(lo,z/p)
        else:hi=min(hi,z/p)
    return None if lo>hi else [[a[0]+lo*dx,a[1]+lo*dy],[a[0]+hi*dx,a[1]+hi*dy]]
im=Image.new('RGBA',(1536,1536),(0,0,0,0));dr=ImageDraw.Draw(im);ground=[[-1640,20],[-1520,20],[-1520,140],[-1640,140]];dr.polygon([tuple(project(p)) for p in ground],fill='#dbe0c9')
roads=[];segments=[];controls=[]
for r in city['roads']:
    pts=[nodes[n] for n in r['nodes']];visible=[]
    for a,b in zip(pts,pts[1:]):
        part=clip(a,b)
        if part:visible.append(part);segments.append((r,part))
    if visible:
        roads.append(dict(id=r['id'],nodes=pts,sourceNodeIds=r['nodes'],width=r.get('width',5),direction=r.get('direction',0),kind=r.get('kind'),displaySegments=visible))
        for seg in visible:
            for p in seg:
                if min(abs(p[0]-bounds['minX']),abs(p[0]-bounds['maxX']),abs(p[1]-bounds['minY']),abs(p[1]-bounds['maxY']))<1e-5:controls.append(dict(kind='source-road-at-region-edge',roadId=r['id'],map=p,pixel=project(p)))
# Source road corridors, not freehand invented streets.
def corridor(part,width,color):
    a,b=part;dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    if length<1e-8:return
    nx,ny=-dy/length*width/2,dx/length*width/2
    poly=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
    dr.polygon([tuple(project(p)) for p in poly],fill=color)
for r,part in segments:corridor(part,r.get('width',5)+3.6,'#bdb9a9')
for r,part in segments:corridor(part,r.get('width',5),'#828887')
buildings=[]
for idx,foot in enumerate(city['buildings']):
    if all(inside(p) for p in foot):
        poly=foot[:-1] if foot[0]==foot[-1] else foot
        h=[12,15,12,15,18][len(buildings)%5]
        buildings.append(dict(sourceReferenceIndex=idx,footprint=poly,heightNominal=h,role='structural-reference-not-formal-building-mutation'))
for item in sorted(buildings,key=lambda b:sum(project(p)[1] for p in b['footprint'])/len(b['footprint'])):
    foot=item['footprint'];top=[p+[item['heightNominal']] for p in foot];faces=[]
    for j in range(len(foot)):
        k=(j+1)%len(foot);faces.append(([foot[j],foot[k],top[k],top[j]],sum(project(p)[1] for p in [foot[j],foot[k]])))
    for face,_ in sorted(faces,key=lambda f:f[1]):dr.polygon([tuple(project(p)) for p in face],fill='#d4cdbb',outline='#a29e91')
    dr.polygon([tuple(project(p)) for p in top],fill='#f2ecde',outline='#9c9e94',width=2)
for nid in ['1623821577','1623821431']:
    if nid in nodes and inside(nodes[nid]):controls.append(dict(kind='source-junction',sourceNodeId=nid,map=nodes[nid],pixel=project(nodes[nid])))
(R/'guides').mkdir(exist_ok=True);out=R/'guides/region-A-structure.png';im.save(out)
meta=dict(id='REGION-A',productionUnit='whole-multi-block-region',bounds=bounds,nominalSizeMeters=[120,120],originMap=origin,
    projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True,axisX=[q,s*q],axisY=[-q,s*q],axisZ=[0,-c],nativePixelsPerUnit=P,originPixel=offset),
    source=dict(file=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest()),roads=roads,buildingReferences=buildings,controlPoints=controls,
    guide=dict(file='guides/region-A-structure.png',nativeSize=list(im.size),sha256=hashlib.sha256(out.read_bytes()).hexdigest()),
    status='structural-guide-only-not-new-runtime-map',notes=['One whole region input, not separate building sprites. Guide boxes never ship as final art.','All source road nodes/widths/directions retained; display clip only. Source buildings are structural references.','Native generation must preserve geometry; control point fit/seams are not assumed from prompt.'])
(R/'region-A-structure.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(region=meta['id'],sizeMeters=meta['nominalSizeMeters'],sourceBuildingReferences=len(buildings),sourceRoads=len(roads),edgeJunctionControlPoints=len(controls),guide=meta['guide']),indent=2))
