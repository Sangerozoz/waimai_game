"""Create new coordinate-based sample plans, never edit accepted raster artwork."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
SOURCE = PROJECT / 'delivery-game/assets/resources/map-sample/city.json'
DATA = json.loads(SOURCE.read_text())
BOUNDS = {'minX': -1720, 'maxX': -1340, 'minY': -240, 'maxY': 200}
W, H = 380, 440
NODES = {n['id']: (n['x'], n['y']) for n in DATA['nodes']}
FONT = '/System/Library/Fonts/STHeiti Light.ttc'
BOLD = '/System/Library/Fonts/STHeiti Medium.ttc'
RNG = random.Random(1103)


def xy(p):
    return (round(p[0] - BOUNDS['minX']), round(BOUNDS['maxY'] - p[1]))


def world(p):
    return [round(BOUNDS['minX'] + p[0], 2), round(BOUNDS['maxY'] - p[1], 2)]


def inside(p, margin=0):
    return BOUNDS['minX'] + margin <= p[0] <= BOUNDS['maxX'] - margin and BOUNDS['minY'] + margin <= p[1] <= BOUNDS['maxY'] - margin


def has_extent(ps, margin=20):
    return ps and max(p[0] for p in ps) >= BOUNDS['minX'] - margin and min(p[0] for p in ps) <= BOUNDS['maxX'] + margin and max(p[1] for p in ps) >= BOUNDS['minY'] - margin and min(p[1] for p in ps) <= BOUNDS['maxY'] + margin


roads = []
water = []
waterways = []
existing = []
road_mask = Image.new('L', (W, H))
water_mask = Image.new('L', (W, H))
building_mask = Image.new('L', (W, H))
rd, wd, bd = map(ImageDraw.Draw, (road_mask, water_mask, building_mask))
for r in DATA['roads']:
    ps = [NODES[n] for n in r['nodes']]
    if not has_extent(ps):
        continue
    roads.append({**r, 'points': ps})
    rd.line([xy(p) for p in ps], fill=255, width=round(r['width'] + 5), joint='curve')
for a in DATA['areas']:
    if a['kind'] == 'water' and has_extent(a['points']):
        water.append(a['points'])
        wd.polygon([xy(p) for p in a['points']], fill=255)
for ps in DATA['waterways']:
    if has_extent(ps):
        waterways.append(ps)
        wd.line([xy(p) for p in ps], fill=255, width=20, joint='curve')
for i, ps in enumerate(DATA['buildings']):
    if len(ps) < 3 or not has_extent(ps, 0):
        continue
    existing.append({'id': f'SRC-{i}', 'sourceIndex': i, 'footprint': ps, 'heightMetres': [10, 13, 16, 19][i % 4], 'origin': 'original-footprint'})
    bd.polygon([xy(p) for p in ps], fill=255)
protected = Image.new('L', (W, H))
protected.paste(road_mask)
protected.paste(255, mask=water_mask)
protected.paste(255, mask=building_mask)
for node in ['1623821046', '9657208284']:
    cx, cy = xy(NODES[node])
    ImageDraw.Draw(protected).ellipse((cx-5, cy-5, cx+5, cy+5), fill=255)
protected = protected.filter(ImageFilter.MaxFilter(3))
px = protected.load()
owners = [[0] * W for _ in range(H)]
components = []
for y in range(H):
    for x in range(W):
        if px[x, y] or owners[y][x]:
            continue
        ident = len(components) + 1
        q = [(x, y)]
        owners[y][x] = ident
        for cx, cy in q:
            for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
                if 0 <= nx < W and 0 <= ny < H and not px[nx, ny] and not owners[ny][nx]:
                    owners[ny][nx] = ident
                    q.append((nx, ny))
        components.append(q)


def rings(cells):
    cellset = set(cells)
    edges = defaultdict(list)
    for x, y in cells:
        for neighbor, a, b in [((x,y-1),(x,y),(x+1,y)), ((x+1,y),(x+1,y),(x+1,y+1)), ((x,y+1),(x+1,y+1),(x,y+1)), ((x-1,y),(x,y+1),(x,y))]:
            if neighbor not in cellset:
                edges[a].append(b)
    result = []
    while edges:
        start = next(iter(edges))
        path = [start]
        current = start
        while True:
            nxt = edges[current].pop()
            if not edges[current]:
                del edges[current]
            path.append(nxt)
            current = nxt
            if current == start:
                break
        simplified = [path[0]]
        for i in range(1, len(path)-1):
            a, b, c = simplified[-1], path[i], path[i+1]
            if (b[0]-a[0])*(c[1]-b[1]) != (b[1]-a[1])*(c[0]-b[0]):
                simplified.append(b)
        simplified.append(path[-1])
        result.append([world(p) for p in simplified])
    return result


seeds = [
    (-1654,-24,'campus','校园与运动场','#d9dfc4'),
    (-1460,54,'mixed','沿街商住与内院','#e6dac9'),
    (-1498,-22,'park','中心社区公园','#bbd29e'),
    (-1484,141,'residential','北部住宅庭院','#ded9c9'),
    (-1662,66,'mixed','西部店屋与住区','#e6dac9'),
    (-1570,154,'mixed','北部临街店屋','#e6dac9'),
    (-1516,-151,'mixed','食堂后场与生活街坊','#e6dac9'),
    (-1545,54,'park','狭长口袋公园','#bbd29e'),
    (-1530,-197,'residential','南部住宅庭院','#ded9c9'),
    (-1362,-30,'garden','东侧住区绿地','#ccd8b3'),
    (-1411,132,'garden','东部内院与活动场地','#ccd8b3'),
    (-1675,179,'residential','西北住宅庭院','#ded9c9'),
    (-1612,-193,'garden','南部庭院花园','#ccd8b3'),
    (-1676,-190,'residential','西南沿街住宅','#ded9c9'),
    (-1596,-81,'riverfront','北岸慢行绿带','#c4d9b2'),
    (-1358,-114,'garden','东南住区庭院','#ccd8b3'),
    (-1613,-151,'mixed','南岸沿街小店','#e6dac9'),
    (-1641,113,'plaza','晴川广场入口前场','#eadbc1'),
]
parcels = []
parcel_cells = {}
for index, cells in enumerate(components):
    cx = sum(x for x,y in cells)/len(cells)
    cy = sum(y for x,y in cells)/len(cells)
    center = world((cx,cy))
    seed = min(seeds, key=lambda s: math.dist(center,s[:2]))
    kind, name, color = seed[2:]
    if len(cells) < 700:
        kind, name, color = 'garden', '边角绿地与庭院', '#ccd8b3'
    ident = f'P{index+1:03}'
    parcels.append({'id':ident,'maskId':index+1,'landUse':kind,'name':name,'areaSquareMetresApprox':len(cells),'center':center,'rings':rings(cells),'groundColor':color,'origin':'new-scene-content-proposal;1m-raster-derived-decorative-boundary'})
    parcel_cells[ident] = cells

placed_mask = protected.copy()
new_buildings = []
features = []
trees = []


def safe_rect(x,y,w,h, owner, pad=3):
    x,y,w,h=map(round,(x,y,w,h))
    if x-pad < 0 or y-pad < 0 or x+w+pad >= W or y+h+pad >= H:
        return False
    pixels=placed_mask.load()
    return all(owners[yy][xx] == owner and not pixels[xx,yy] for yy in range(y-pad,y+h+pad+1) for xx in range(x-pad,x+w+pad+1))


def place_building(x,y,w,h, parcel, school=False):
    if not safe_rect(x,y,w,h,parcel['maskId']):
        return False
    fp=[world(v) for v in [(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]]
    item={'id':f'ADD-{len(new_buildings)+1:03}','parcelId':parcel['id'],'footprint':fp,'heightMetres':10 if school else [10,13,16][len(new_buildings)%3],'module':'school-bar' if school else 'shop-house' if parcel['landUse']=='mixed' else 'residential','origin':'new-noninteractive-scenery;not-operating-address'}
    new_buildings.append(item)
    ImageDraw.Draw(placed_mask).rectangle((x-3,y-3,x+w+3,y+h+3),fill=255)
    return True


for parcel in sorted(parcels,key=lambda p:-p['areaSquareMetresApprox']):
    cells=parcel_cells[parcel['id']]
    if parcel['landUse']=='campus':
        for x,y in sorted(cells,key=lambda v:(v[1],v[0])):
            if safe_rect(x,y,54,32,parcel['maskId'],4):
                features.append({'type':'sports-court','parcelId':parcel['id'],'bounds':[world((x,y)),world((x+54,y+32))]})
                ImageDraw.Draw(placed_mask).rectangle((x-4,y-4,x+58,y+36),fill=255)
                break
        for x,y in sorted(cells,key=lambda v:(v[0],v[1])):
            if place_building(x,y,40,12,parcel,True):
                break
        for x,y in sorted(cells,reverse=True):
            if place_building(x,y,28,12,parcel,True):
                break
    elif parcel['landUse'] in ['mixed','residential'] and len(cells)>=1200:
        attempts=0
        for y in range(min(v[1] for v in cells)+4,max(v[1] for v in cells)-10,24):
            for x in range(min(v[0] for v in cells)+4,max(v[0] for v in cells)-18,30):
                if place_building(x,y,21,13,parcel):
                    attempts+=1
                if attempts>=max(2,len(cells)//1100):
                    break
            if attempts>=max(2,len(cells)//1100):
                break
    if len(cells)>900:
        # Pedestrian paths are scenery, never added to the road-routing graph.
        center=xy(parcel['center'])
        run=[]
        for x in range(max(0,center[0]-55),min(W,center[0]+56)):
            y=center[1]
            if owners[y][x]==parcel['maskId'] and not placed_mask.getpixel((x,y)):
                run.append((x,y))
            elif run:
                if len(run)>8:features.append({'type':'pedestrian-path','parcelId':parcel['id'],'points':[world(run[0]),world(run[-1])],'widthMetres':2.5})
                run=[]
        if len(run)>8:features.append({'type':'pedestrian-path','parcelId':parcel['id'],'points':[world(run[0]),world(run[-1])],'widthMetres':2.5})
        if parcel['landUse'] in ['park','garden','campus','plaza']:
            run=[]
            for y in range(max(0,center[1]-45),min(H,center[1]+46)):
                x=center[0]
                if owners[y][x]==parcel['maskId'] and not placed_mask.getpixel((x,y)):
                    run.append((x,y))
                elif run:
                    if len(run)>8:features.append({'type':'pedestrian-path','parcelId':parcel['id'],'points':[world(run[0]),world(run[-1])],'widthMetres':2.5})
                    run=[]
            if len(run)>8:features.append({'type':'pedestrian-path','parcelId':parcel['id'],'points':[world(run[0]),world(run[-1])],'widthMetres':2.5})
        for feature_type, fw, fh, limit in [('garden-bed',7,3,3),('bench',3,1,3)]:
            added=0
            for x,y in sorted(cells,key=lambda v:abs(v[0]-center[0])+abs(v[1]-center[1]))[::11]:
                if safe_rect(x,y,fw,fh,parcel['maskId'],2):
                    features.append({'type':feature_type,'parcelId':parcel['id'],'bounds':[world((x,y)),world((x+fw,y+fh))]})
                    ImageDraw.Draw(placed_mask).rectangle((x-2,y-2,x+fw+2,y+fh+2),fill=255)
                    added+=1
                    if added>=limit:break
    count=max(1,min(12,len(cells)//650)) if len(cells)>120 else 0
    for _ in range(count*30):
        if count<=0:break
        x,y=RNG.choice(cells)
        if safe_rect(x-3,y-3,6,6,parcel['maskId'],1):
            trees.append({'id':f'TREE-{len(trees)+1:03}','parcelId':parcel['id'],'groundAnchor':world((x,y)),'crownDiameterMetres':5.5,'heightMetres':7,'origin':'ground-tree-no-rooftop'})
            ImageDraw.Draw(placed_mask).ellipse((x-4,y-4,x+4,y+4),fill=255)
            count-=1


data={'version':1,'date':'2026-11-03','status':'sample-scene-layout-produced-not-engine-validated-or-user-art-accepted','source':str(SOURCE.relative_to(PROJECT)),'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'bounds':BOUNDS,'coordinateUnit':'ground-metres','groundBoundaryPrecision':'1m raster for decorative parcels only;road and original footprint geometry remains original float coordinates','parcels':parcels,'addedBuildings':new_buildings,'sceneFeatures':features,'trees':trees,'sourceBuildings':existing,'sourceRoads':roads,'sourceWaterPolygons':water,'sourceWaterways':waterways,'entrances':[{'name':'榕树街食堂','node':'1623821046','groundAnchor':NODES['1623821046']},{'name':'晴川广场','node':'9657208284','groundAnchor':NODES['9657208284']}],'constraints':{'newRoadEdgesAdded':False,'originalMapModified':False,'newOperatingAddressesAdded':False,'waterwayDecorativeProtectionWidthMetres':20,'roadDecorativeProtectionExtraWidthMetres':5,'everyUnprotectedCellAssigned':True,'dynamicGameValidationRun':False}}
(ROOT/'sample-scene-layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def ft(size,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,size)


def draw_top():
    scale=4
    im=Image.new('RGB',(W*scale+640,H*scale+220),'#fcfbf7')
    d=ImageDraw.Draw(im)
    left,top=70,150
    conv=lambda p:(left+(p[0]+1720)*scale,top+(200-p[1])*scale)
    # Ground mask colors assign every free metre to a designed land-use patch.
    ground=Image.new('RGB',(W,H),'#e1ddcf');gp=ground.load()
    by_owner={p['maskId']:p for p in parcels}
    for y in range(H):
        for x in range(W):
            owner=owners[y][x]
            if owner:
                color=by_owner[owner]['groundColor'].lstrip('#')
                gp[x,y]=tuple(int(color[i:i+2],16) for i in (0,2,4))
    im.paste(ground.resize((W*scale,H*scale),Image.Resampling.NEAREST),(left,top))
    for a in water:d.polygon([conv(p) for p in a],fill='#9fc5c4')
    for ps in waterways:d.line([conv(p) for p in ps],fill='#9fc5c4',width=20*scale,joint='curve')
    for road in sorted(roads,key=lambda r:r['width']):
        ps=[conv(p) for p in road['points']]
        d.line(ps,fill='#cabfae',width=round((road['width']+5)*scale),joint='curve')
        d.line(ps,fill='#7d8588',width=round(road['width']*scale),joint='curve')
    for f in features:
        if f['type']=='pedestrian-path':d.line([conv(p) for p in f['points']],fill='#f1e7d2',width=10)
        elif f['type']=='sports-court':
            a,b=map(conv,f['bounds']);box=[a[0],a[1],b[0],b[1]]
            d.rounded_rectangle(box,radius=40,fill='#c38f79',outline='#f9eee0',width=4)
            d.rectangle((a[0]+25,a[1]+25,b[0]-25,b[1]-25),fill='#a6ba94',outline='#f9eee0',width=3)
            d.line(((a[0]+b[0])/2,a[1]+25,(a[0]+b[0])/2,b[1]-25),fill='#f9eee0',width=3)
        else:
            a,b=map(conv,f['bounds']);d.rectangle((a[0],a[1],b[0],b[1]),fill='#789764' if f['type']=='garden-bed' else '#a87d51',outline='#5e7151')
    for b in existing+new_buildings:
        d.polygon([conv(v) for v in b['footprint']],fill='#b7afa0' if b['origin']=='original-footprint' else '#cfac82',outline='#776f62',width=2)
    for tree in trees:
        x,y=conv(tree['groundAnchor']);rad=tree['crownDiameterMetres']*scale/2
        d.ellipse((x-rad,y-rad,x+rad,y+rad),fill='#6e925c',outline='#567c4d',width=2)
    d.rectangle((left,top,left+W*scale,top+H*scale),outline='#bc832f',width=5)
    for p in sorted(parcels,key=lambda p:-p['areaSquareMetresApprox'])[:18]:
        x,y=conv(p['center']);label=p['id'];bb=d.textbbox((0,0),label,font=ft(25,True));w=bb[2]+12
        d.rounded_rectangle((x-w/2,y-20,x+w/2,y+18),radius=6,fill='#fffdf5',outline='#8c8a77',width=1)
        d.text((x,y-1),label,font=ft(25,True),fill='#3f4a38',anchor='mm')
    for e in data['entrances']:
        x,y=conv(e['groundAnchor']);d.ellipse((x-10,y-10,x+10,y+10),fill='#e88829',outline='#fff8e9',width=3)
    # Original geometry may extend beyond sample bounds; clip presentation margins.
    for box in [(0,0,im.width,top-1),(0,top,left-1,im.height),(left+W*scale+1,top,im.width,im.height),(0,top+H*scale+1,im.width,im.height)]:
        d.rectangle(box,fill='#fcfbf7')
    d.rectangle((left,top,left+W*scale,top+H*scale),outline='#bc832f',width=5)
    d.text((70,35),'首块样板 · 地块内容安排',font=ft(55,True),fill='#29382f')
    d.text((72,104),'原道路、水系、建筑占地和取送入口保留；空白地块安排完整场景。',font=ft(28),fill='#657064')
    x=left+W*scale+55;y=155
    d.text((x,y),'地块用途',font=ft(36,True),fill='#29382f');y+=65
    for p in sorted(parcels,key=lambda p:-p['areaSquareMetresApprox'])[:18]:
        d.text((x,y),p['id']+' '+p['name'],font=ft(25),fill='#4b5545');y+=56
    y+=40
    for text in ['棕灰屋顶：原始建筑','暖棕屋顶：补景建筑','绿色：有内容的庭院/公园','校园：校舍＋运动场','浅色细线：场地步道','所有新增内容仅属场景','不新增道路或经营地址']:
        d.text((x,y),text,font=ft(25),fill='#657064');y+=47
    d.text((70,H*scale+175),'380×440m · 2026-11-03 · © OpenStreetMap contributors · 新地块用途为样板制作安排',font=ft(25),fill='#657064')
    im.save(ROOT/'01-parcel-layout.png')


def draw_structure():
    # Original geometry projected as a structural reference, not final game art.
    size=2048;scale=9.7;center=(-1530,-20)
    im=Image.new('RGB',(size,size),'#dddccf');d=ImageDraw.Draw(im)
    def pnt(p,z=0):
        dx=p[0]-center[0];dy=p[1]-center[1]
        return(size/2+.8660254*scale*(dx-dy),size/2-.5*scale*(dx+dy)-z*scale)
    def polygon(points,fill,outline=None,z=0):
        d.polygon([pnt(p,z) for p in points],fill=fill,outline=outline)
    for p in parcels:
        for ring in p['rings']:
            polygon(ring,p['groundColor'])
    for poly in water:polygon(poly,'#9fc5c4')
    for ps in waterways:d.line([pnt(p) for p in ps],fill='#9fc5c4',width=round(20*scale*.72),joint='curve')
    for r in sorted(roads,key=lambda r:r['width']):
        ps=[pnt(p) for p in r['points']]
        d.line(ps,fill='#d3cabb',width=round((r['width']+5)*scale*.72),joint='curve')
        d.line(ps,fill='#778389',width=round(r['width']*scale*.72),joint='curve')
    for f in features:
        if f['type']=='pedestrian-path':d.line([pnt(v) for v in f['points']],fill='#f5e8d1',width=round(2.5*scale*.72))
        elif f['type']=='sports-court':
            a,b=f['bounds'];poly=[a,[b[0],a[1]],b,[a[0],b[1]],a];polygon(poly,'#bc8f7c','#f8eee1')
            mid=[(a[0]+b[0])/2,(a[1]+b[1])/2];rect=[[a[0]+5,a[1]-5],[b[0]-5,a[1]-5],[b[0]-5,b[1]+5],[a[0]+5,b[1]+5]];polygon(rect,'#a5b68c','#f8eee1')
            d.line([pnt([mid[0],a[1]-5]),pnt([mid[0],b[1]+5])],fill='#fff5e4',width=3)
        else:
            a,b=f['bounds'];poly=[a,[b[0],a[1]],b,[a[0],b[1]],a];polygon(poly,'#789764' if f['type']=='garden-bed' else '#a87d51','#647751')
    scene=[('building',b) for b in existing+new_buildings]+[('tree',t) for t in trees]
    scene.sort(key=lambda item: sum(item[1]['groundAnchor']) if item[0]=='tree' else sum(sum(v) for v in item[1]['footprint'])/len(item[1]['footprint']),reverse=True)
    for kind,item in scene:
        if kind=='tree':
            v=item['groundAnchor'];x,y=pnt(v);rad=24
            d.line((x,y,x,y-47),fill='#8c7959',width=7)
            d.ellipse((x-rad,y-76,x+rad,y-28),fill='#74985c',outline='#567d4b',width=3)
            continue
        poly=item['footprint'];height=item['heightMetres']
        for a,b in zip(poly,poly[1:]+poly[:1]):
            polygon3=[pnt(a),pnt(b),pnt(b,height),pnt(a,height)]
            d.polygon(polygon3,fill='#dfd0b6' if b[0]-a[0]>=0 else '#c0c6b9',outline='#9da398')
            length=math.dist(a,b)
            if length>5:
                for z in range(3,round(height)-1,3):
                    for j in range(1,max(2,round(length/4))):
                        t=j/max(2,round(length/4));v=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
                        sx,sy=pnt(v,z);d.rectangle((sx-3,sy-8,sx+3,sy+7),fill='#70929e')
        polygon(poly,'#eee7d9','#a7afa1',height)
        if item.get('module')=='shop-house':
            a,b=poly[0],poly[1];d.line([pnt(a,3),pnt(b,3)],fill='#dc8e3b',width=9)
    im.save(ROOT/'02-structure-reference.png')
    (ROOT/'projection.json').write_text(json.dumps({'purpose':'structural-image-guide-only-not-runtime-camera-approval','centerGroundMetres':center,'canvasPixels':[size,size],'scalePixelsPerMetre':scale,'equations':['screenX=1024+0.8660254*scale*((x-centerX)-(y-centerY))','screenY=1024-0.5*scale*((x-centerX)+(y-centerY))-height*scale'],'roadGeometry':'original-city-json','buildingHeights':'PM module-height proposals, not surveyed data'},ensure_ascii=False,indent=2)+'\n')


draw_top()
draw_structure()
summary={'parcels':len(parcels),'unprotectedGroundSquareMetresAssigned':sum(len(c) for c in components),'addedNoninteractiveBuildings':len(new_buildings),'groundTrees':len(trees),'sceneFeatures':len(features),'campusSportsCourts':sum(f['type']=='sports-court' for f in features),'largeParcels':[{k:p[k] for k in ['id','landUse','name','areaSquareMetresApprox','center']} for p in sorted(parcels,key=lambda p:-p['areaSquareMetresApprox'])[:18]]}
(ROOT/'layout-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='largeParcels'},ensure_ascii=False))
