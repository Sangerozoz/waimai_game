"""Author geometric art guides from unchanged road coordinates; no existing image edits."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / '2026-11-03-modular-city-assets' / 'sample-layout.json'
old = json.loads(OLD.read_text())
theta = math.radians(62.5)
S, C, Q = math.sin(theta), math.cos(theta), math.sqrt(.5)
a, b = (-1596.7, 96.27), (-1582.32, 36.57)
f = (75-a[1])/(b[1]-a[1])
center = [a[0]+f*(b[0]-a[0]), 75.0]
length = math.dist(a,b)
t = [(a[i]-b[i])/length for i in range(2)]
nw = [-t[1],t[0]]

def project(p):
    x,y = p[0]-center[0],p[1]-center[1]
    z = p[2] if len(p)>2 else 0
    return [(x-y)*Q,(x+y)*S*Q-z*C]

def rnd(p): return [round(x,7) for x in p]
parcels=[]
for bank,sign in [('west',1),('east',-1)]:
    n=[sign*v for v in nw]
    front=[center[i]+n[i]*5.8 for i in range(2)]
    def world(d,l,z=0): return [front[i]+n[i]*d+t[i]*l for i in range(2)]+[z]
    ground=[world(0,-11),world(18,-11),world(18,11),world(0,11)]
    buildings=[]
    for j,(l0,l1,h) in enumerate([(-10,-1,9),(1,10,10.5)]):
        fp=[world(4.5,l0),world(12.5,l0),world(12.5,l1),world(4.5,l1)]
        buildings.append(dict(id=f'{bank}-building-{j+1}',wallFootprint=[rnd(p[:2]) for p in fp],heightMeters=h,
            carriagewayEdgeSetbackMeters=6.3,nearestRoadId='149397380-0',
            frontageNormalMap=rnd([-v for v in n]),entranceMap=rnd(world(4.5,(l0+l1)/2)[:2]),entranceVisible=bank=='west'))
    pts=ground+[p[:2]+[h] for item in buildings for p in item['wallFootprint'] for h in [0,item['heightMeters']]]
    projected=[project(p) for p in pts]
    minx,miny=map(min,zip(*projected)); maxx,maxy=map(max,zip(*projected))
    ppu=min(880/(maxx-minx),820/(maxy-miny))
    offset=[512-ppu*(minx+maxx)/2,512-ppu*(miny+maxy)/2]
    def pix(p):
        q=project(p); return (offset[0]+q[0]*ppu,offset[1]+q[1]*ppu)
    im=Image.new('RGBA',(1024,1024),(0,0,0,0)); dr=ImageDraw.Draw(im)
    dr.polygon([pix(p) for p in ground], fill='#e7dfcd',outline='#877d68',width=3)
    # Street boundary stays empty; gold is the exact front edge, not a road.
    dr.line([pix(ground[0]),pix(ground[3])],fill='#d3a34f',width=5)
    for item in sorted(buildings,key=lambda z:sum(project(p)[1] for p in z['wallFootprint'])):
        fp=[p+[0] for p in item['wallFootprint']]; top=[p[:2]+[item['heightMeters']] for p in fp]
        faces=[]
        for k in range(4):
            k1=(k+1)%4
            faces.append(([fp[k],fp[k1],top[k1],top[k]],sum(project(p)[1] for p in [fp[k],fp[k1]])))
        for face,_ in sorted(faces,key=lambda z:z[1]):
            dr.polygon([pix(p) for p in face],fill='#d5cfc0',outline='#686b6c',width=2)
        dr.polygon([pix(p) for p in top],fill='#f7f1e5',outline='#686b6c',width=3)
        if item['entranceVisible']:
            ep=world(4.5,(-5.5 if item['id'].endswith('1') else 5.5),1.0)
            px,py=pix(ep);dr.rectangle((px-7,py-10,px+7,py+10),fill='#ad7045')
    # Planned planting pools behind the parcel front edge, small trees only.
    for d,l in [(2.4,-8),(2.4,8),(15.8,0)]:
        pool=[world(d-.8,l-.8),world(d+.8,l-.8),world(d+.8,l+.8),world(d-.8,l+.8)]
        dr.polygon([pix(p) for p in pool],fill='#8d9970',outline='#a99b7c',width=3)
        px,py=pix(world(d,l,3.4));dr.ellipse((px-20,py-20,px+20,py+20),fill='#91a879',outline='#68845b',width=2)
    (ROOT/'guides').mkdir(exist_ok=True)
    im.save(ROOT/'guides'/f'{bank}-parcel-guide.png')
    parcels.append(dict(id=f'parcel-{bank}',assetId=f'HC-P-{bank.upper()}',bank=bank,anchorMap=rnd(front),
        groundPolygon=[rnd(p[:2]) for p in ground],buildings=buildings,
        guide=dict(file=f'guides/{bank}-parcel-guide.png',nativeSize=[1024,1024],pixelsPerUnit=ppu,originPixel=offset,
            controlPoints=[dict(name=f'ground-{i}',map=rnd(p[:2]),pixel=rnd(pix(p))) for i,p in enumerate(ground)]),
        localAxes=dict(depthAwayFromRoad=rnd(n),alongRoadNorth=rnd(t)),
        artStatus='guide-only-native-art-pending'))
layout=dict(schemaVersion=1,status='production-in-progress-not-game-tested',
    projection=dict(id='orthographic-e62.5-a45-v1',elevationDeg=62.5,azimuthDeg=45,canvasYDown=True,
        axisX=[Q,S*Q],axisY=[-Q,S*Q],axisZ=[0,-C],originMap=center),
    source=old['source'],roads=old['roads'],parcels=parcels,
    bounds=dict(minX=-1626,maxX=-1558,minY=48,maxY=114),
    rider=dict(roadId='149397380-0',route=old['rider']['route'],mode='memory-only-demonstration',directions=['ne','sw'],
        referenceCanvasWidthPxAt720=62.76729916734202,minimumCanvasWidthPxAt720=125.53459833468404),
    notes=['Original source city and all selected road nodes/widths/directions unchanged.',
        'New parcel/building geometry is isolated candidate art, not movement of source building or business coordinates.',
        'Guides are authored geometric references, never final runtime box buildings.',
        'No testing/typecheck/page automation/save access.'])
(ROOT/'scene-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(center=center,parcels=[dict(id=p['id'],guide=p['guide']) for p in parcels]),indent=2))
