"""Deterministic offline scenery production. Writes only this delivery directory.
No game import, routing edit, package install, save access, or runtime validation.
"""
from pathlib import Path
from collections import defaultdict, Counter
from array import array
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import json, math, hashlib

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parents[2]
SOURCE=PROJECT/'delivery-game/assets/resources/map-sample/city.json'
SAMPLE=OUT.parent/'2026-11-03-county-sample-production/sample-scene-layout.json'
EXPECTED='536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED, 'Source changed; do not produce against unreviewed source'
raw=json.loads(SOURCE.read_text());sample=json.loads(SAMPLE.read_text())
B={'minX':-2652.59,'maxX':-361.42,'minY':-1282.79,'maxY':867.46}
U={'minX':-1947.26,'maxX':-940.64,'minY':-926.24,'maxY':661.93}
S=sample['bounds'];STEP=2;X0=-2654;Y0=868
W=math.ceil((B['maxX']-X0)/STEP);H=math.ceil((Y0-B['minY'])/STEP)
nodes={n['id']:[n['x'],n['y']] for n in raw['nodes']}
def pix(p):return ((p[0]-X0)/STEP,(Y0-p[1])/STEP)
def world(p):return [round(min(B['maxX'],max(B['minX'],X0+p[0]*STEP)),2),round(min(B['maxY'],max(B['minY'],Y0-p[1]*STEP)),2)]
def inside(p,b=B):return b['minX']<=p[0]<=b['maxX'] and b['minY']<=p[1]<=b['maxY']
def extent(ps,b=B,margin=24):return bool(ps) and max(p[0] for p in ps)>=b['minX']-margin and min(p[0] for p in ps)<=b['maxX']+margin and max(p[1] for p in ps)>=b['minY']-margin and min(p[1] for p in ps)<=b['maxY']+margin
roads=[{**r,'points':[nodes[n] for n in r['nodes']]} for r in raw['roads'] if extent([nodes[n] for n in r['nodes']])]
waters=[a['points'] for a in raw['areas'] if a['kind']=='water' and extent(a['points'])]
waterways=[ps for ps in raw['waterways'] if extent(ps)]
sample_source={b['sourceIndex']:b for b in sample['sourceBuildings']}
source_buildings=[]
for i,ps in enumerate(raw['buildings']):
    if len(ps)<3 or not extent(ps,margin=0):continue
    center=[sum(p[k] for p in ps)/len(ps) for k in (0,1)]
    source_buildings.append(sample_source.get(i,{'id':f'SRC-{i}','sourceIndex':i,'footprint':ps,'heightMetres':(9+3*(i%4)) if inside(center,U) else (3+3*(i%3)),'origin':'original-footprint'}))
# Preserve whole source geometry, but never produce half a building at BLUE.
edge_buildings=[]
for item in source_buildings:
    if not all(inside(v) for v in item['footprint']):
        item['excludedFromProduction']=True
        item['productionExclusionReason']='original footprint not wholly inside BLUE; do not clip, move, or expand boundary'
        edge_buildings.append({'id':item['id'],'sourceIndex':item['sourceIndex'],'reason':item['productionExclusionReason']})
edge_roads=[{'id':r['id'],'reason':'source points outside BLUE; display clipping only; boundary closure pending; no added routing edges'} for r in roads if not all(inside(v) for v in r['points'])]
entrances=[{**p,'groundAnchor':nodes[p['node']]} for p in raw['pois'] if inside(nodes[p['node']])]
# Preserve the sample entrance objects exactly; other references retain raw POI metadata.
se={e['node']:e for e in sample['entrances']}
entrances=[se.get(e['node'],e) for e in entrances]
protected=Image.new('L',(W,H));d=ImageDraw.Draw(protected)
for r in roads:d.line([pix(p) for p in r['points']],fill=255,width=math.ceil((r['width']+5)/STEP),joint='curve')
for ps in waters:d.polygon([pix(p) for p in ps],fill=255)
for ps in waterways:d.line([pix(p) for p in ps],fill=255,width=10,joint='curve')
for b in source_buildings:d.polygon([pix(p) for p in b['footprint']],fill=255)
for e in entrances:
    x,y=pix(e['groundAnchor']);d.ellipse((x-3,y-3,x+3,y+3),fill=255)
protected=protected.filter(ImageFilter.MaxFilter(3)) # additional one-cell conservative margin
# The exact sample rectangle is an authoritative overlay, not regenerated ground.
sample_pixel=(int((S['minX']-X0)/STEP),int((Y0-S['maxY'])/STEP),int((S['maxX']-X0)/STEP),int((Y0-S['minY'])/STEP))
d=ImageDraw.Draw(protected);d.rectangle((sample_pixel[0],sample_pixel[1],sample_pixel[2]-1,sample_pixel[3]-1),fill=255)
blocked=bytearray(protected.tobytes());owners=array('I',[0])*(W*H)
components=[];tile_of={}
def tile_for(x,y):
    p=world((x+.5,y+.5));return (math.floor(p[0]/100),math.floor(p[1]/100))
for y in range(H):
    for x in range(W):
        ix=y*W+x
        if blocked[ix] or owners[ix]:continue
        tile=tile_for(x,y);ident=len(components)+1;owners[ix]=ident;q=[ix]
        for cur in q:
            cx,cy=cur%W,cur//W
            for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                if not (0<=nx<W and 0<=ny<H):continue
                ni=ny*W+nx
                if not blocked[ni] and not owners[ni] and tile_for(nx,ny)==tile:
                    owners[ni]=ident;q.append(ni)
        components.append(q);tile_of[ident]=tile

def rings(cells):
    cells=set(cells);edges=defaultdict(list)
    for ix in sorted(cells):
        x,y=ix%W,ix//W
        for nx,ny,a,b in ((x,y-1,(x,y),(x+1,y)),(x+1,y,(x+1,y),(x+1,y+1)),(x,y+1,(x+1,y+1),(x,y+1)),(x-1,y,(x,y+1),(x,y))):
            if not (0<=nx<W and 0<=ny<H) or ny*W+nx not in cells:edges[a].append(b)
    result=[]
    while edges:
        start=next(iter(edges));p=[start];cur=start;prev=None
        while True:
            choices=edges[cur]
            if prev is None:nxt=choices[0]
            else:
                dx,dy=cur[0]-prev[0],cur[1]-prev[1]
                # Keep filled cells to the right at diagonal contacts.
                priority=[(-dy,dx),(dx,dy),(dy,-dx),(-dx,-dy)]
                nxt=min(choices,key=lambda b:priority.index((b[0]-cur[0],b[1]-cur[1])))
            choices.remove(nxt)
            if not choices:del edges[cur]
            p.append(nxt);prev,cur=cur,nxt
            if cur==start:break
        keep=[p[0]]
        for k in range(1,len(p)-1):
            a,b,c=keep[-1],p[k],p[k+1]
            if (b[0]-a[0])*(c[1]-b[1])!=(b[1]-a[1])*(c[0]-b[0]):keep.append(b)
        keep.append(p[-1]);result.append([world(v) for v in keep])
    return result

styles={
'mixed':('沿街商住与内院','#e6dac9','warm-paving;small-stone-courtyard;controlled-grass'),
'residential':('住宅与生活庭院','#ded9c9','warm-courtyard-paving;low-grass;planted-borders'),
'park':('社区公园与休憩步道','#bbd29e','meadow;warm-gravel-walk;defined-flower-beds'),
'garden':('住区庭院与边角花园','#ccd8b3','low-groundcover;gravel-edge;small-stone-paving'),
'campus':('校舍操场与校园庭院','#d9dfc4','warm-campus-paving;red-sports-surface;controlled-grass'),
'riverfront':('水岸慢行与邻里绿带','#c4d9b2','riverbank-meadow;gravel-walk;recessed-seating'),
'plaza':('街坊活动前场','#eadbc1','warm-stone-paving;low-flower-beds;seating'),
}
parcels=[];newbuild=[];features=[];trees=[];parcel_cells={};feature_serial=0
# Point-to-segment nearest direction, only for noninteractive building alignment.
segments=[]
for r in roads:
    for a,b in zip(r['points'],r['points'][1:]):
        if math.dist(a,b)>4:segments.append((a,b))
def road_angle(p):
    nearest=(1e30,0)
    for a,b in segments:
        dx,dy=b[0]-a[0],b[1]-a[1];l=dx*dx+dy*dy;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l))
        dist=(p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2
        if dist<nearest[0]:nearest=(dist,math.atan2(dy,dx))
    # 15-degree decorative module orientation, never a road quantization.
    return round(nearest[1]/(math.pi/12))*math.pi/12,math.sqrt(nearest[0])
for ident,cells in enumerate(components,1):
    tile=tile_of[ident];center=world((sum(i%W for i in cells)/len(cells)+.5,sum(i//W for i in cells)/len(cells)+.5));zone='urban' if inside(center,U) else 'suburb'
    angle,near=road_angle(center);hashnum=abs(tile[0]*131+tile[1]*29)
    area=len(cells)*4
    kind=('mixed' if zone=='urban' and near<35 else 'residential')
    if area<380:kind='garden'
    elif hashnum%19==0 and area>2800:kind='campus'
    elif hashnum%11==0:kind='park'
    elif near>55 and hashnum%7==0:kind='plaza'
    # Riverfront use only near the original water geometry, no synthetic river.
    rep=cells[len(cells)//2];rp=world((rep%W+.5,rep//W+.5))
    nearwater=any(min((rp[0]-v[0])**2+(rp[1]-v[1])**2 for v in ps)<35**2 for ps in waterways if extent(ps,{'minX':rp[0],'maxX':rp[0],'minY':rp[1],'maxY':rp[1]},35))
    if nearwater and kind not in ('mixed','campus') and area>500:kind='riverfront'
    label,color,material=styles[kind];pid=f'CP-{tile[0]}-{tile[1]}-{ident:04}'
    rs=rings(cells)
    # Exact area of clipped 2m cell outlines, including holes.
    signed=lambda ring:sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))/2
    area_exact=abs(sum(signed(r) for r in rs))
    p={'id':pid,'maskId':ident+10000,'landUse':kind,'name':('城区' if zone=='urban' else '郊区')+label,'areaSquareMetresApprox':round(area_exact,2),'center':center,'rings':rs,'groundColor':color,'groundMaterial':material,'zone':zone,'moduleOrientationRadians':round(angle,6),'tileId':f'{tile[0]}:{tile[1]}','ringFillRule':'evenodd','origin':'new-noninteractive-scenery;2m-raster-decorative-boundary'}
    parcels.append(p);parcel_cells[pid]=cells

occupied=bytearray(blocked)
def footprint_cells(points,pad=0):
    ps=[pix(p) for p in points];x0=math.floor(min(p[0] for p in ps))-pad;y0=math.floor(min(p[1] for p in ps))-pad
    x1=math.ceil(max(p[0] for p in ps))+pad;y1=math.ceil(max(p[1] for p in ps))+pad
    if x0<0 or y0<0 or x1>=W or y1>=H:return []
    mask=Image.new('L',(x1-x0+1,y1-y0+1));ImageDraw.Draw(mask).polygon([(p[0]-x0,p[1]-y0) for p in ps],fill=255)
    if pad:mask=mask.filter(ImageFilter.MaxFilter(pad*2+1))
    return [(y0+y)*W+x0+x for y in range(mask.height) for x in range(mask.width) if mask.getpixel((x,y))]
def safe(points,owner,pad=0):
    if not all(inside(v) for v in points):return []
    cells=footprint_cells(points,pad)
    return cells if cells and all(owners[i]==owner and not occupied[i] for i in cells) else []
def rect(p,w,h,angle=0):
    c,s=math.cos(angle),math.sin(angle)
    return [[round(p[0]+dx*c-dy*s,2),round(p[1]+dx*s+dy*c,2)] for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)]]
def reserve(cells):
    for i in cells:occupied[i]=255
new_feature_ids=[]
def feature(p,kind,points=None,bounds=None,**kw):
    global feature_serial
    feature_serial+=1;f={'id':f'CF-{feature_serial:05}','type':kind,'parcelId':p['id'],**kw}
    if points is not None:f['points']=points
    if bounds is not None:f['bounds']=bounds
    features.append(f);new_feature_ids.append(f['id']);return f

for p in sorted(parcels,key=lambda p:p['id']):
    cells=parcel_cells[p['id']];owner=p['maskId']-10000;urban=p['zone']=='urban';area=p['areaSquareMetresApprox'];angle=p['moduleOrientationRadians']
    # Stable world lattice plus a representative, not arbitrary shuffled pixels.
    candidates=[i for i in cells if (i%W)%6==2 and (i//W)%6==2]
    candidates.sort(key=lambda i:(i//W,i%W));candidates+=cells[::max(1,len(cells)//60)]
    existing_features=len(features);existing_trees=len(trees);existing_build=len(newbuild)
    target=max(1,round(area/(900 if urban else 1900)))
    if p['landUse'] in ('mixed','residential','campus') and area>650:
        if p['landUse']=='campus':
            # Courts are axis aligned for compatibility with sample feature bounds.
            for court_w,court_h in [(42,24),(24,14)]:
                court_done=False
                for ix in candidates:
                    anchor=world((ix%W+.5,ix//W+.5));r=rect(anchor,court_w,court_h);cover=safe(r,owner,1)
                    if cover:
                        feature(p,'sports-court',bounds=[[anchor[0]-court_w/2,anchor[1]+court_h/2],[anchor[0]+court_w/2,anchor[1]-court_h/2]],surface='red-clay-and-muted-green',lineColor='#f8eee0');reserve(cover);court_done=True;break
                if court_done:break
            target=min(3,target)
        for ix in candidates:
            if len(newbuild)-existing_build>=target:break
            anchor=world((ix%W+.5,ix//W+.5))
            w,h=(30,12) if p['landUse']=='campus' else ((22,14) if urban else (16,11))
            fp=rect(anchor,w,h,angle);cover=safe(fp,owner,1)
            if not cover and p['landUse']=='campus':
                fp=rect(anchor,18,9,angle);cover=safe(fp,owner,1)
            if not cover:continue
            building_urban=inside(anchor,U)
            floors=3+((ix+owner)%4) if building_urban else 1+((ix+owner)%3)
            if p['landUse']=='campus':floors=min(floors,4 if building_urban else 3)
            newbuild.append({'id':f'CADD-{len(newbuild)+1:05}','parcelId':p['id'],'footprint':fp,'heightMetres':floors*3,'floorCount':floors,'zone':'urban' if building_urban else 'suburb','module':'school-bar' if p['landUse']=='campus' else 'shop-house' if p['landUse']=='mixed' else 'residential','orientationRadians':angle,'roofColor':['#dfd4bd','#d7c7af','#c8c7b8','#ddd9ca'][(ix+owner)%4],'origin':'new-noninteractive-scenery;not-operating-address'});reserve(cover)
    # Paths follow rows/columns inside each free component and stop at every obstacle.
    if area>450:
        xs=[i%W for i in cells];ys=[i//W for i in cells]
        for yy in range(min(ys)+4,max(ys)-2,18 if urban else 22):
            run=[]
            for xx in range(min(xs),max(xs)+1):
                ix=yy*W+xx
                if owners[ix]==owner and not occupied[ix]:run.append(ix)
                else:
                    if len(run)>=6:
                        a,b=run[0],run[-1];feature(p,'pedestrian-path',points=[world((a%W+.5,a//W+.5)),world((b%W+.5,b//W+.5))],widthMetres=2);reserve(run)
                    run=[]
            if len(run)>=6:
                a,b=run[0],run[-1];feature(p,'pedestrian-path',points=[world((a%W+.5,a//W+.5)),world((b%W+.5,b//W+.5))],widthMetres=2);reserve(run)
    # Physical details spread through the whole parcel, not one label on a lawn.
    count=max(1,round(area/750));placed=0
    for ix in candidates:
        if placed>=count:break
        a=world((ix%W+.5,ix//W+.5));kind='garden-bed' if placed%3 else 'bench';fw,fh=(5,2) if kind=='garden-bed' else (2.5,1)
        pts=rect(a,fw,fh);cover=safe(pts,owner)
        if cover:
            feature(p,kind,bounds=[[round(a[0]-fw/2,2),round(a[1]+fh/2,2)],[round(a[0]+fw/2,2),round(a[1]-fh/2,2)]],material='low-flower-groundcover' if kind=='garden-bed' else 'warm-wood');reserve(cover);placed+=1
    # Restrained ground trees: usually one per 1800–2600m², never roof/water/road.
    target_trees=int(area/(1800 if urban else 2600))
    for ix in reversed(candidates):
        if len(trees)-existing_trees>=target_trees:break
        a=world((ix%W+.5,ix//W+.5));cover=safe(rect(a,6,6),owner,1)
        if cover:
            trees.append({'id':f'CTREE-{len(trees)+1:05}','parcelId':p['id'],'groundAnchor':a,'crownDiameterMetres':5.5,'heightMetres':7,'origin':'ground-tree-no-rooftop'});reserve(cover)
    # Tiny/slender fragments still receive a physical ground detail. It occupies a
    # fraction of one known-safe 2m cell, with no fake walkability implied.
    if len(features)==existing_features and len(trees)==existing_trees and len(newbuild)==existing_build:
        ix=cells[len(cells)//2];a=world((ix%W,ix//W));b=world((ix%W+1,ix//W+1))
        feature(p,'garden-bed',bounds=[[round(a[0]+.05,2),round(a[1]-.05,2)],[round(b[0]-.05,2),round(b[1]+.05,2)]],material='low-groundcover-and-pebble-edge',microPatch=True)
    if p['landUse']=='campus' and (len(newbuild)==existing_build or not any(f['type']=='sports-court' for f in features[existing_features:])):
        # An elongated fragment cannot honestly be called a complete campus.
        kind='residential' if len(newbuild)>existing_build else 'park'
        label,color,material=styles[kind];p.update(landUse=kind,name=('城区' if urban else '郊区')+label,groundColor=color,groundMaterial=material)
        for building in newbuild[existing_build:]:building['module']='residential'
    p['contentCounts']={'buildings':len(newbuild)-existing_build,'features':len(features)-existing_features,'trees':len(trees)-existing_trees}

# The four sample arrays are copied, with every item/field/list value unchanged.
result={'version':1,'date':'2026-11-03','status':'county-scenery-data-produced;not-engine-integrated-or-user-art-accepted','source':str(SOURCE.relative_to(PROJECT)),'sourceSHA256':EXPECTED,'bounds':B,'coordinateUnit':'ground-metres','groundBoundaryPrecision':'2m decorative raster;blue clipping exact at recorded 0.01m bounds;sample original 1m;original source geometry float unchanged','parcels':sample['parcels']+parcels,'addedBuildings':sample['addedBuildings']+newbuild,'sceneFeatures':sample['sceneFeatures']+features,'trees':sample['trees']+trees,'sourceBuildings':source_buildings,'sourceRoads':roads,'sourceWaterPolygons':waters,'sourceWaterways':waterways,'entrances':entrances,'constraints':{'newRoadEdgesAdded':False,'originalMapModified':False,'newOperatingAddressesAdded':False,'waterwayDecorativeProtectionWidthMetres':20,'roadDecorativeProtectionExtraWidthMetres':5,'additionalRasterProtectionMetres':2,'everyUnprotectedCellAssigned':True,'dynamicGameValidationRun':False,'entireDeliveryRouteBoundary':'blue-city-bounds;runtime-enforcement-not-claimed','sampleOverlayAuthoritative':True,'schoolScenesCreateNoOrders':True,'roofTreesAllowed':False,'sourceBuildingsCrossingBlue':'excludedFromProduction;preserve source footprint;never render clipped half-building'},'zones':{'constructionAndDelivery':B,'denseUrban':U,'suburb':'inside constructionAndDelivery outside denseUrban','outerLandscape':'outside BLUE unchanged;not produced by this package;never operating area'},'sampleOverlay':{'source':str(SAMPLE.relative_to(PROJECT)),'sourceSHA256':sha(SAMPLE),'bounds':S,'arraysCopiedUnchanged':['parcels','addedBuildings','sceneFeatures','trees'],'sourceBuildingsUseSampleMetadataWhenPresent':True},'featureSchema':{'sampleFeatureIds':'sample sceneFeatures had no ids; keep unchanged; use positional stable key SF-00000 for tile lookup','newFeatureIds':'CF-*; unique stable IDs','rings':'even-odd fill; preserve all rings, including holes','groundMaterial':'rendering hint, not a gameplay surface'}}
result['productionExclusions']={'sourceBuildings':edge_buildings,'sourceRoads':edge_roads,'sourceBuildingRule':'skip excludedFromProduction for all production rendering; source geometry remains reference only; sample overlay retained unchanged'}
write_exclusions={'date':'2026-11-03',**result['productionExclusions']}
# Stable 100m spatial index: references only, never duplicated object payloads.
# ownerTile stores each object once; overlappingTile references are deduplicated on query.
tiles=defaultdict(lambda:defaultdict(list));objects=[]
def geom_points(kind,item):
    if kind=='parcels':return [v for r in item['rings'] for v in r]
    if kind in ('addedBuildings','sourceBuildings'):return item['footprint']
    if kind=='trees':
        a=item['groundAnchor'];r=item['crownDiameterMetres']/2;return [[a[0]-r,a[1]-r],[a[0]+r,a[1]+r]]
    if kind in ('sceneFeatures',):return item.get('points',item.get('bounds'))
    if kind=='sourceRoads':return item['points']
    if kind=='entrances':return [item['groundAnchor']]
    return item
for kind in ['parcels','addedBuildings','sceneFeatures','trees','sourceBuildings','sourceRoads','sourceWaterPolygons','sourceWaterways','entrances']:
    for ix,item in enumerate(result[kind]):
        ident=item.get('id',item.get('node',f'SF-{ix:05}')) if isinstance(item,dict) else f'{kind}-{ix:05}'
        pts=geom_points(kind,item);minx=min(p[0] for p in pts);maxx=max(p[0] for p in pts);miny=min(p[1] for p in pts);maxy=max(p[1] for p in pts)
        if kind=='sourceRoads':margin=item['width']/2+3
        elif kind=='sourceWaterways':margin=10
        elif kind=='sceneFeatures' and item['type']=='pedestrian-path':margin=item.get('widthMetres',2)/2
        else:margin=0
        objectkey=f'{kind}/{ident}';owner=f'{math.floor((minx+maxx)/200)}:{math.floor((miny+maxy)/200)}'
        refs=[]
        for tx in range(math.floor((minx-margin)/100),math.floor((maxx+margin)/100)+1):
            for ty in range(math.floor((miny-margin)/100),math.floor((maxy+margin)/100)+1):
                if tx*100>B['maxX']+100 or (tx+1)*100<B['minX']-100 or ty*100>B['maxY']+100 or (ty+1)*100<B['minY']-100:continue
                key=f'{tx}:{ty}';tiles[key][kind].append(objectkey);refs.append(key)
        objects.append({'key':objectkey,'collection':kind,'index':ix,'ownerTile':owner,'overlapTiles':refs,'excludedFromProduction':bool(isinstance(item,dict) and item.get('excludedFromProduction')),'bounds':{'minX':minx-margin,'maxX':maxx+margin,'minY':miny-margin,'maxY':maxy+margin}})
result['tileIndex']={'tileSizeMetres':100,'origin':[0,0],'tileKey':'floor(worldX/100):floor(worldY/100)','query':'union object keys from viewport tiles plus camera/building-height padding; deduplicate keys; dereference collection/index; do not walk all objects every frame','objects':objects,'tiles':dict(sorted(tiles.items())),'ownership':'one object record; ownerTile deterministic bbox center; overlap tiles contain references only','sourceGeometry':'some long source features reference conservative AABB tiles; exact clipping is consumer responsibility'}
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
write('county-scene-layout.json',result)
write('production-exclusions.json',write_exclusions)
summary={'date':'2026-11-03','status':result['status'],'bounds':B,'counts':{k:len(result[k]) for k in ['parcels','addedBuildings','sceneFeatures','trees','sourceBuildings','sourceRoads','sourceWaterPolygons','sourceWaterways','entrances']},'samplePreservedCounts':{k:len(sample[k]) for k in ['parcels','addedBuildings','sceneFeatures','trees']},'newExpansionCounts':{'parcels':len(parcels),'addedBuildings':len(newbuild),'sceneFeatures':len(features),'trees':len(trees)},'newLandUse':dict(Counter(p['landUse'] for p in parcels)),'newLandUseAreaSquareMetresApprox':dict((k,round(sum(p['areaSquareMetresApprox'] for p in parcels if p['landUse']==k),2)) for k in styles),'newZones':dict(Counter(p['zone'] for p in parcels)),'newBuildingFloorsByZone':{z:dict(sorted(Counter(b['floorCount'] for b in newbuild if b['zone']==z).items())) for z in ['urban','suburb']},'newFeatureTypes':dict(Counter(f['type'] for f in features)),'sourceBuildingsExcludedFromProduction':len(edge_buildings),'sourceBuildingsEligibleForProduction':len(source_buildings)-len(edge_buildings),'sourceRoadsNeedingBlueClippingOrClosure':len(edge_roads),'tileCount':len(tiles),'spatialObjectCount':len(objects),'decorativeGridMetres':2,'newAssignedGroundSquareMetresApprox':round(sum(p['areaSquareMetresApprox'] for p in parcels),2),'unprotectedCellCount':sum(len(c) for c in components),'newParcelsWithoutPhysicalContent':sum(sum(p['contentCounts'].values())==0 for p in parcels),'runtimeValidationRun':False,'userVisualAcceptance':False}
write('layout-summary.json',summary)
# New data diagrams only. Existing approved raster art is never edited.
FONT='/System/Library/Fonts/STHeiti Light.ttc';BOLD='/System/Library/Fonts/STHeiti Medium.ttc'
def render(name,bounds,title,scale=1.4):
    width=round((bounds['maxX']-bounds['minX'])*scale);height=round((bounds['maxY']-bounds['minY'])*scale)
    canvas=Image.new('RGB',(width+120,height+280),'#fbfaf5');layer=Image.new('RGB',(width,height),'#dcd8ca');dr=ImageDraw.Draw(layer)
    cv=lambda p:((p[0]-bounds['minX'])*scale,(bounds['maxY']-p[1])*scale)
    # XOR ring masks implements even-odd holes, including preserved sample rings.
    from PIL import ImageChops
    for p in result['parcels']:
        pts=[v for r in p['rings'] for v in r]
        if not extent(pts,bounds,0):continue
        mask=Image.new('1',(width,height))
        for ring in p['rings']:
            one=Image.new('1',(width,height));ImageDraw.Draw(one).polygon([cv(v) for v in ring],fill=1);mask=ImageChops.logical_xor(mask,one)
        layer.paste(p['groundColor'],mask=mask)
    dr=ImageDraw.Draw(layer)
    for ps in waters:dr.polygon([cv(v) for v in ps],fill='#9fc5c4')
    for ps in waterways:dr.line([cv(v) for v in ps],fill='#9fc5c4',width=max(1,round(20*scale)),joint='curve')
    for r in sorted(roads,key=lambda r:r['width']):
        dr.line([cv(v) for v in r['points']],fill='#cbbfae',width=max(1,round((r['width']+5)*scale)),joint='curve');dr.line([cv(v) for v in r['points']],fill='#81898b',width=max(1,round(r['width']*scale)),joint='curve')
    for f in result['sceneFeatures']:
        if f['type']=='pedestrian-path':dr.line([cv(v) for v in f['points']],fill='#f3e7d1',width=max(1,round(f['widthMetres']*scale)))
        else:
            a,b=map(cv,f['bounds']);box=(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]));dr.rectangle(box,fill='#bb8d75' if f['type']=='sports-court' else '#819964' if f['type']=='garden-bed' else '#a4774f')
            if f['type']=='sports-court':dr.rectangle((box[0]+3,box[1]+3,box[2]-3,box[3]-3),outline='#f9efdc',width=2)
    for b in result['sourceBuildings']+result['addedBuildings']:
        if not b.get('excludedFromProduction'):dr.polygon([cv(v) for v in b['footprint']],fill='#b9b1a2' if b['id'].startswith('SRC') else '#cba580',outline='#8e8576',width=1)
    for t in result['trees']:
        x,y=cv(t['groundAnchor']);r=t['crownDiameterMetres']*scale/2;dr.ellipse((x-r,y-r,x+r,y+r),fill='#72925d',outline='#617e51')
    for b,color,thick in [(U,'#699958',3),(S,'#cc872d',4)]:
        a,bp=cv([b['minX'],b['maxY']]),cv([b['maxX'],b['minY']]);dr.rectangle((a[0],a[1],bp[0],bp[1]),outline=color,width=thick)
    for e in entrances:
        x,y=cv(e['groundAnchor']);dr.ellipse((x-4,y-4,x+4,y+4),fill='#dc852e',outline='#fff6e6')
    canvas.paste(layer,(60,160));dr=ImageDraw.Draw(canvas)
    dr.text((60,28),title,font=ImageFont.truetype(BOLD,42),fill='#344136')
    dr.text((60,93),'原坐标场景数据图 · 棕灰为原建筑，暖棕为新增布景；橙框样板原样复用，绿框为繁华城区',font=ImageFont.truetype(FONT,23),fill='#596455')
    dr.text((60,height+188),'100m稳定分片 · 公园/校园含实物内容 · 仅装饰分区近似2m，原道路/水系/建筑浮点几何不改',font=ImageFont.truetype(FONT,23),fill='#596455')
    dr.text((60,height+232),'2026-11-03 · © OpenStreetMap contributors · 未引擎接入/游戏测试/用户视觉验收；不是目标美术效果图',font=ImageFont.truetype(FONT,23),fill='#596455')
    assert max(canvas.size)<=4400;canvas.save(OUT/name)
render('01-county-scene-plan.png',B,'县城蓝框 · 全域地块内容安排',1.4)
render('02-urban-scene-detail.png',U,'繁华城区 · 样板与新增街坊接续',2.0)
# Fresh offline integrity evidence, intentionally not game tests.
cell_area=sum((min(B['maxX'],X0+(i%W+1)*STEP)-max(B['minX'],X0+(i%W)*STEP))*(min(B['maxY'],Y0-(i//W)*STEP)-max(B['minY'],Y0-(i//W+1)*STEP)) for c in components for i in c)
checks={'productionSourceBuildingsWhollyInsideBlue':all(all(inside(v) for v in b['footprint']) for b in source_buildings if not b.get('excludedFromProduction')),'sampleSourceBuildingObjectsUnchanged':all(next(b for b in source_buildings if b['id']==sb['id'])==sb for sb in sample['sourceBuildings']),'newRingAreaMatchesAssignedClippedCells':abs(cell_area-summary['newAssignedGroundSquareMetresApprox'])<.02,'newBuildingsAvoidOriginalProtectedRaster':all(bool(footprint_cells(b['footprint'])) and all(not blocked[i] for i in footprint_cells(b['footprint'])) for b in newbuild),'sourceSHA256Matches':sha(SOURCE)==EXPECTED,'sampleSourceSHA256':sha(SAMPLE),'sampleArraysUnchanged':{k:result[k][:len(sample[k])]==sample[k] for k in ['parcels','addedBuildings','sceneFeatures','trees']},'newObjectIdsUnique':len({o['key'] for o in objects})==len(objects),'allNewParcelsHavePhysicalContent':summary['newParcelsWithoutPhysicalContent']==0,'newFeatureGeometryWithinBlue':all(all(inside(v) for v in f.get('points',f.get('bounds'))) for f in features),'everyCampusHasBuildingsAndCourt':all(p['contentCounts']['buildings']>0 and any(f['parcelId']==p['id'] and f['type']=='sports-court' for f in features) for p in parcels if p['landUse']=='campus'),'newBuildingsWithinBlueAndOutsideSample':all(all(inside(v) and not (S['minX']<v[0]<S['maxX'] and S['minY']<v[1]<S['maxY']) for v in b['footprint']) for b in newbuild),'originalBuildingFootprintsUnchanged':all(b['footprint']==raw['buildings'][b['sourceIndex']] for b in source_buildings),'originalRoadFieldsUnchanged':all({k:v for k,v in r.items() if k!='points'}==next(v for v in raw['roads'] if v['id']==r['id']) and r['points']==[nodes[n] for n in r['nodes']] for r in roads),'newDecorativeCellsAssignedExactlyOnce':sum(len(c) for c in components)==sum(1 for v in owners if v),'runtimeOrGameTestsRun':False,'scope':'read-only source/schema/sample-subset/ownership integrity checks only'}
assert all(checks[k] for k in ['productionSourceBuildingsWhollyInsideBlue','sampleSourceBuildingObjectsUnchanged','newRingAreaMatchesAssignedClippedCells','newBuildingsAvoidOriginalProtectedRaster','sourceSHA256Matches','newObjectIdsUnique','allNewParcelsHavePhysicalContent','newFeatureGeometryWithinBlue','everyCampusHasBuildingsAndCourt','newBuildingsWithinBlueAndOutsideSample','originalBuildingFootprintsUnchanged','originalRoadFieldsUnchanged','newDecorativeCellsAssignedExactlyOnce'])
assert all(checks['sampleArraysUnchanged'].values())
write('integrity-report.json',checks)
manifest={'date':'2026-11-03','source':{'path':str(SOURCE.relative_to(PROJECT)),'sha256':sha(SOURCE)},'sample':{'path':str(SAMPLE.relative_to(PROJECT)),'sha256':sha(SAMPLE)},'outputs':[],'status':result['status'],'noRuntimeValidation':True}
for name in ['county-scene-layout.json','layout-summary.json','integrity-report.json','01-county-scene-plan.png','02-urban-scene-detail.png','build-county-layout.py','production-exclusions.json','README.md']:
    p=OUT/name;item={'path':name,'sha256':sha(p),'bytes':p.stat().st_size}
    if p.suffix=='.png':
        with Image.open(p) as im:item['pixels']=list(im.size)
    manifest['outputs'].append(item)
write('production-manifest.json',manifest)
print(json.dumps(summary,ensure_ascii=False,indent=2))
