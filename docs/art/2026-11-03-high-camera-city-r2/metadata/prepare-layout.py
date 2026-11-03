"""Author R2 candidates, source-road references and geometric art guide only."""
import json,copy,math,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-11-03-high-camera-city'
layout=json.loads((OLD/'scene-layout.json').read_text());cityPath=Path(layout['source']['path']);city=json.loads(cityPath.read_text());ns={n['id']:[n['x'],n['y']] for n in city['nodes']}
layout['revision']=2;layout['status']='r2-production-in-progress-not-tested';layout['priorRoute']=copy.deepcopy(layout['rider']['route'])
t=layout['parcels'][0]['localAxes']['alongRoadNorth'];delta=[-26*v for v in t]
main=layout['parcels']
for p in main:
    p['artStatus']='native-r2-height-edit-pending'
    for b in p['buildings']:b['heightMeters']+=3;b['heightSource']='R2 nominal guide, not exact painted measurement'
east=copy.deepcopy(main[1]);east['id']='parcel-east-south';east['assetId']='HC-P-EAST-LOW';east['artStatus']='reuse-native-approved-v1-candidate'
def move(p):return [p[i]+delta[i] for i in range(2)]
for key in ['anchorMap']:east[key]=move(east[key])
for key in ['groundPolygon','artBoundaryMapCandidate']:
    if key in east:east[key]=[move(p) for p in east[key]]
for b in east['buildings']:
    b['id']='south-'+b['id'];b['heightMeters']-=3;b['wallFootprint']=[move(p) for p in b['wallFootprint']];b['entranceMap']=move(b['entranceMap']);b['heightSource']='Reuse v1 nominal guide'
east.pop('guide',None)
west0=main[0];front=west0['anchorMap'];n=west0['localAxes']['depthAwayFromRoad']
def world(d,l,z=0):return [front[i]+n[i]*d+t[i]*l for i in range(2)]+[z]
def p2(p):return [round(x,7) for x in p[:2]]
ground=[world(0,-25),world(18,-25),world(18,-13),world(0,-13)]
fp=[world(4.5,-23.5),world(12.5,-23.5),world(12.5,-14.5),world(4.5,-14.5)]
west=dict(id='parcel-west-corner',assetId='HC-P-WEST-CORNER',bank='west',anchorMap=p2(world(0,-19)),groundPolygon=[p2(p) for p in ground],localAxes=west0['localAxes'],artStatus='guide-only-art-pending',
    buildings=[dict(id='west-corner-building',wallFootprint=[p2(p) for p in fp],heightMeters=12,carriagewayEdgeSetbackMeters=6.3,nearestRoadId='149397380-0',frontageNormalMap=[-v for v in n],entranceMap=p2(world(4.5,-19)),entranceVisible=True)])
axes=layout['projection'];origin=axes['originMap']
def project(p):return [sum((p[j]-origin[j])*axes['axis'+['X','Y'][j]][i] for j in range(2))+(p[2] if len(p)>2 else 0)*axes['axisZ'][i] for i in range(2)]
top=[p[:2]+[12] for p in fp];pts=[project(p) for p in ground+fp+top];minx,miny=map(min,zip(*pts));maxx,maxy=map(max,zip(*pts));ppu=min(880/(maxx-minx),840/(maxy-miny));offset=[512-ppu*(minx+maxx)/2,512-ppu*(miny+maxy)/2]
def pix(p):q=project(p);return [offset[i]+q[i]*ppu for i in range(2)]
im=Image.new('RGBA',(1024,1024),(0,0,0,0));dr=ImageDraw.Draw(im);dr.polygon([tuple(pix(p)) for p in ground],fill='#e7dfcd',outline='#8a806d',width=3)
dr.line([tuple(pix(ground[0])),tuple(pix(ground[3]))],fill='#d3a34f',width=4)
faces=[]
for i in range(4):j=(i+1)%4;faces.append(([fp[i],fp[j],top[j],top[i]],sum(project(p)[1] for p in [fp[i],fp[j]])))
for face,_ in sorted(faces,key=lambda x:x[1]):dr.polygon([tuple(pix(p)) for p in face],fill='#d1ccbe',outline='#6b6c68',width=2)
dr.polygon([tuple(pix(p)) for p in top],fill='#f6f0e3',outline='#6b6c68',width=3)
px,py=pix(world(4.5,-19,1));dr.rectangle((px-8,py-14,px+8,py+14),fill='#ae7045')
for d,l in [(2.2,-23),(15,-16)]:
    pool=[world(d-.7,l-.7),world(d+.7,l-.7),world(d+.7,l+.7),world(d-.7,l+.7)];dr.polygon([tuple(pix(p)) for p in pool],fill='#94a87b',outline='#aa9c80',width=3)
    px,py=pix(world(d,l,3.1));dr.ellipse((px-19,py-19,px+19,py+19),fill='#8fa575',outline='#6d855b',width=2)
(R/'guides').mkdir(exist_ok=True);im.save(R/'guides/west-corner-guide.png')
west['guide']=dict(file='guides/west-corner-guide.png',nativeSize=[1024,1024],pixelsPerUnit=ppu,originPixel=offset,controlPoints=[dict(name=f'ground-{i}',map=p2(p),pixel=pix(p)) for i,p in enumerate(ground)])
layout['parcels']=main+[east,west]
for r in city['roads']:
    if r['id']=='149396705-0':
        layout['roads'].append(dict(id=r['id'],width=r['width'],kind=r['kind'],direction=r['direction'],sourceNodeIds=r['nodes'],nodes=[ns[k] for k in r['nodes']]))
layout['source']['roadIds']=list(dict.fromkeys(layout['source']['roadIds']+['149396705-0']))
a,b=[-1596.7,96.27],[-1582.32,36.57];f=(44-a[1])/(b[1]-a[1]);newEnd=[a[0]+f*(b[0]-a[0]),44]
layout['rider']['route']=[layout['priorRoute'][0],newEnd];layout['rider']['map']=layout['priorRoute'][0];layout['rider']['notes']='Memory-only route extended along the same original centerline segment; no formal business route change.'
layout['bounds']=dict(minX=-1628,maxX=-1548,minY=20,maxY=114)
layout['camera']=dict(focusMap=[origin[0]+t[0]*-7,origin[1]+t[1]*-7],viewWidthUnits=54,screenOffset=[0,0],referenceWidth=720,referenceHeight=1280)
def region(a,b,l0,l1):return [p2(world(a,l0)),p2(world(b,l0)),p2(world(b,l1)),p2(world(a,l1))]
eastFront=layout['parcels'][1]['anchorMap'];en=layout['parcels'][1]['localAxes']['depthAwayFromRoad']
def ew(d,l):return [eastFront[i]+en[i]*d+t[i]*l for i in range(2)]
layout['groundRegions']=[dict(id='west-block-transition',polygon=region(0,18,-13,-11),materialId='S01-paving',tileMeters=3),dict(id='east-block-transition',polygon=[ew(0,-15),ew(18,-15),ew(18,-11),ew(0,-11)],materialId='S01-paving',tileMeters=3)]
layout['notes']+=['R2 uses a narrower original corner sprite on west south to respect existing branch149396705-0, rather than covering it with a repeated wide block.','Nominal3-5storey variation; original source road coordinates, width/direction and source city bytes unchanged.']
(R/'scene-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
for name in ['HC-R-NE-v1.png','HC-R-SW-v1.png','HC-P-EAST-v1.png']:
    shutil.copy2(OLD/name,R/name)
print(json.dumps(dict(parcels=[p['id'] for p in layout['parcels']],roadIds=layout['source']['roadIds'],route=layout['rider']['route'],cornerGuide=west['guide']),indent=2))
