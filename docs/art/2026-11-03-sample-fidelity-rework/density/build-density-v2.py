"""Produce the revised sample density from immutable source geometry, offline only."""
from pathlib import Path
from collections import defaultdict,Counter
from array import array
from PIL import Image,ImageDraw,ImageFilter,ImageChops,ImageFont
import json,hashlib,math
O=Path(__file__).resolve().parent;ROOT=O.parents[3]
SRC=ROOT/'delivery-game/assets/resources/map-sample/city.json'
OLD=ROOT/'docs/art/2026-11-03-county-sample-production/sample-scene-layout.json'
FEEDBACK=O.parent/'user-feedback.json'
SHA='536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==SHA
raw=json.loads(SRC.read_text());old=json.loads(OLD.read_text());feedback=json.loads(FEEDBACK.read_text())
B=old['bounds'];R=.5;W=760;H=880;N=W*H
xy=lambda p:((p[0]-B['minX'])/R,(B['maxY']-p[1])/R)
world=lambda p:[round(B['minX']+p[0]*R,4),round(B['maxY']-p[1]*R,4)]
inside=lambda p:B['minX']<=p[0]<=B['maxX'] and B['minY']<=p[1]<=B['maxY']
nodes={n['id']:[n['x'],n['y']] for n in raw['nodes']}
roads=old['sourceRoads'];waters=old['sourceWaterPolygons'];waterways=old['sourceWaterways'];original=old['sourceBuildings'];entrances=old['entrances']
# Pixel masks measure unions at 0.5m; original geometry arrays are never snapped.
def layer():return Image.new('L',(W,H))
road_mask=layer();water_mask=layer();building_mask=layer();entrance_mask=layer();road_safe=layer();water_safe=layer()
for r in roads:
    for mask,width in [(road_mask,r['width']),(road_safe,r['width']+5)]:
        d=ImageDraw.Draw(mask);ps=[xy(p) for p in r['points']];d.line(ps,fill=255,width=max(1,round(width/R)),joint='curve')
        rr=width/R/2
        for p in [ps[0],ps[-1]]:d.ellipse((p[0]-rr,p[1]-rr,p[0]+rr,p[1]+rr),fill=255)
for ps in waters:
    ImageDraw.Draw(water_mask).polygon([xy(p) for p in ps],fill=255)
for ps in waterways:ImageDraw.Draw(water_mask).line([xy(p) for p in ps],fill=255,width=round(20/R),joint='curve')
water_safe=water_mask.filter(ImageFilter.MaxFilter(5)) # 1m beyond conservative 20m channel
for b in original:ImageDraw.Draw(building_mask).polygon([xy(p) for p in b['footprint']],fill=255)
for e in entrances:
    x,y=xy(e['groundAnchor']);ImageDraw.Draw(entrance_mask).ellipse((x-10,y-10,x+10,y+10),fill=255)
existing_safe=building_mask.filter(ImageFilter.MaxFilter(7)) # 1.5m outside source footprints
protected=layer()
for m in [road_safe,water_safe,existing_safe,entrance_mask]:protected=ImageChops.lighter(protected,m)
ImageDraw.Draw(protected).rectangle((0,0,W-1,H-1),outline=255,width=2) # 1m sample edge
free=ImageChops.invert(protected);base_free_count=free.histogram()[255];free_area=base_free_count*R*R
pb=protected.tobytes();owners=array('I',[0])*N;components=[]
for i in range(N):
    if pb[i] or owners[i]:continue
    owner=len(components)+1;q=[i];owners[i]=owner
    for cur in q:
        x,y=cur%W,cur//W
        for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=nx<W and 0<=ny<H:
                ni=ny*W+nx
                if not pb[ni] and not owners[ni]:owners[ni]=owner;q.append(ni)
    components.append(q)
segments=[]
for road in roads:
    for a,b in zip(road['points'],road['points'][1:]):
        if math.dist(a,b)>1:segments.append((a,b,road['id'],road['width']))
def nearest(p):
    best=(1e30,None)
    for a,b,rid,width in segments:
        dx,dy=b[0]-a[0],b[1]-a[1];l=dx*dx+dy*dy;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l));q=[a[0]+t*dx,a[1]+t*dy];dist=(q[0]-p[0])**2+(q[1]-p[1])**2
        if dist<best[0]:best=(dist,(math.atan2(dy,dx),q,rid,width))
    return math.sqrt(best[0]),best[1]
angles={}
for owner,cells in enumerate(components,1):
    center=world((sum(i%W for i in cells)/len(cells),sum(i//W for i in cells)/len(cells)))
    angle=nearest(center)[1][0];angles[owner]=round(angle/(math.pi/36))*(math.pi/36) # 5 degree decor only
occupied=protected.copy();new_mask=layer();buildings=[];area_sum=0.;placement_records=[]
def rect(p,w,h,a):
    c,s=math.cos(a),math.sin(a)
    return [[round(p[0]+dx*c-dy*s,4),round(p[1]+dx*s+dy*c,4)] for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)]]
def local_mask(points,pad=0):
    ps=[xy(v) for v in points];x0=math.floor(min(p[0] for p in ps))-pad-1;y0=math.floor(min(p[1] for p in ps))-pad-1;x1=math.ceil(max(p[0] for p in ps))+pad+1;y1=math.ceil(max(p[1] for p in ps))+pad+1
    if x0<0 or y0<0 or x1>=W or y1>=H:return None
    m=Image.new('L',(x1-x0+1,y1-y0+1));ImageDraw.Draw(m).polygon([(x-x0,y-y0) for x,y in ps],fill=255)
    if pad:m=m.filter(ImageFilter.MaxFilter(2*pad+1))
    return (x0,y0,x1+1,y1+1),m

def can_place(points,pad=2,mask=None):
    if not all(inside(p) for p in points):return None
    shape=local_mask(points,pad)
    if shape is None:return None
    box,m=shape
    return shape if not ImageChops.multiply((mask or occupied).crop(box),m).getbbox() else None

def put(mask,shape):
    box,m=shape;mask.paste(255,(box[0],box[1]),m)
# Candidate lattice is sampled at 2m, buildings then share their local block direction.
candidates=[]
for y in range(6,H-6,4):
    for x in range(6,W-6,4):
        ix=y*W+x;owner=owners[ix]
        if not owner:continue
        p=world((x+.5,y+.5));distance,street=nearest(p)
        candidates.append((round(distance,1),y,x,owner,p))
candidates.sort(key=lambda v:(v[0],v[1],v[2]))
# Larger varied modules first; small fillers are a final irregular-lot fallback.
passes=[(38,24),(34,20),(30,22),(28,18),(24,16),(22,14),(18,12),(14,10),(12,8),(9,7)]
for passnum,(bw,bh) in enumerate(passes):
    before=len(buildings)
    for distance,y,x,owner,p in candidates:
        if area_sum/free_area>=.60:break
        if occupied.getpixel((x,y)):continue
        a=angles[owner];fp=rect(p,bw,bh,a);shape=can_place(fp)
        # Rotating by 90 degrees packs differently shaped legal residual plots.
        if shape is None:
            fp=rect(p,bw,bh,a+math.pi/2);shape=can_place(fp)
        if shape is None:continue
        facing=nearest(p)[1];normal=[facing[1][0]-p[0],facing[1][1]-p[1]];length=math.hypot(*normal) or 1
        floors=[3,4,4,5,3,6][len(buildings)%6];bid=f'DV2-B{len(buildings)+1:03}'
        module='corner-shop-house' if len(buildings)%7==0 else 'continuous-shop-house' if distance<28 else 'courtyard-apartment'
        style={'id':'approved-bright-town-shop-v2','wallPalette':['#f6e9ce','#faeedb','#efd7b5'][len(buildings)%3],'roofPalette':['#e4e6df','#d9dfdd','#f0e8da'][len(buildings)%3],'shopAccent':['#ef9a36','#edb44b','#db773d'][len(buildings)%3],'windowTone':'muted-blue-reflective-glass-no-global-blue-wash','roof':'flat-parapet-no-trees','floorHeightMetres':3,'shopFloorHeightMetres':3,'facadeVariation':len(buildings)%6}
        buildings.append({'id':bid,'parcelId':f'DV2-BLOCK-{owner:03}','footprint':fp,'groundAnchor':p,'heightMetres':floors*3,'floorCount':floors,'module':module,'styleProfile':style,'streetFacingHint':{'sourceRoadId':facing[2],'nearestOriginalRoadPoint':[round(v,4) for v in facing[1]],'normalToStreet':[round(v/length,6) for v in normal],'roadWidthMetres':facing[3],'roadGeometryUnchanged':True},'origin':'v2-new-noninteractive-building;not-order-address'})
        put(occupied,shape);put(new_mask,local_mask(fp,0));area_sum+=bw*bh
    placement_records.append({'moduleSizeMetres':[bw,bh],'placed':len(buildings)-before,'newFootprintAreaAccumulated':round(area_sum,2),'coverageOfPreplacementFreeGround':round(area_sum/free_area,6)})
    if area_sum/free_area>=.60:break
# Every remaining land surface becomes compact paving, except small explicit pockets.
actual_union=layer()
for m in [road_mask,water_mask,building_mask,new_mask]:actual_union=ImageChops.lighter(actual_union,m)
residual=ImageChops.invert(actual_union);green=layer();features=[];trees=[]
# Spread small pockets around the sample, no single campus or broad park retained.
used_tiles=set();green_shapes=[]
for distance,y,x,owner,p in reversed(candidates):
    if len(green_shapes)>=28:break
    tile=(int((p[0]-B['minX'])//60),int((p[1]-B['minY'])//60))
    if tile in used_tiles:continue
    fp=rect(p,8,8,0);shape=can_place(fp,pad=0)
    if shape:
        put(green,shape);put(occupied,shape);green_shapes.append((p,fp));used_tiles.add(tile)
        trees.append({'id':f'DV2-T{len(trees)+1:03}','parcelId':None,'groundAnchor':p,'crownDiameterMetres':5.5,'heightMetres':6.5,'origin':'ground-pocket-tree-no-rooftop'})
# Additional low planters at shop fronts are much smaller than the old lawn parcels.
for distance,y,x,owner,p in candidates:
    if len(features)>=40:break
    if distance>22 or (x+y)%20!=0:continue
    fp=rect(p,3,1.5,0);shape=can_place(fp,pad=0)
    if shape:
        put(green,shape);put(occupied,shape);features.append({'id':f'DV2-F{len(features)+1:03}','type':'garden-bed','parcelId':None,'bounds':[[p[0]-1.5,p[1]+.75],[p[0]+1.5,p[1]-.75]],'material':'low-groundcover-in-raised-planter','physicalAreaSquareMetres':4.5})
# Extract multi-ring ground patches at 0.5m, with holes retained. Ground can run under
# awnings but never fills source road/water/building holes.
def components_for(mask):
    pixels=mask.tobytes();seen=bytearray(N);result=[]
    for ix in range(N):
        if not pixels[ix] or seen[ix]:continue
        q=[ix];seen[ix]=1
        for i in q:
            x,y=i%W,i//W
            for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if 0<=nx<W and 0<=ny<H:
                    ni=ny*W+nx
                    if pixels[ni] and not seen[ni]:seen[ni]=1;q.append(ni)
        result.append(q)
    return result

def rings(cells):
    cellset=set(cells);edges=defaultdict(list)
    for ix in sorted(cells):
        x,y=ix%W,ix//W
        for nx,ny,a,b in [(x,y-1,(x,y),(x+1,y)),(x+1,y,(x+1,y),(x+1,y+1)),(x,y+1,(x+1,y+1),(x,y+1)),(x-1,y,(x,y+1),(x,y))]:
            if not(0<=nx<W and 0<=ny<H) or ny*W+nx not in cellset:edges[a].append(b)
    result=[]
    while edges:
        start=next(iter(edges));path=[start];cur=start;prev=None
        while True:
            opts=edges[cur]
            if prev is None:nxt=opts[0]
            else:
                dx,dy=cur[0]-prev[0],cur[1]-prev[1];priority=[(-dy,dx),(dx,dy),(dy,-dx),(-dx,-dy)]
                nxt=min(opts,key=lambda v:priority.index((v[0]-cur[0],v[1]-cur[1])))
            opts.remove(nxt)
            if not opts:del edges[cur]
            path.append(nxt);prev,cur=cur,nxt
            if cur==start:break
        simple=[path[0]]
        for i in range(1,len(path)-1):
            a,b,c=simple[-1],path[i],path[i+1]
            if (b[0]-a[0])*(c[1]-b[1])!=(b[1]-a[1])*(c[0]-b[0]):simple.append(b)
        simple.append(path[-1]);result.append([world(v) for v in simple])
    return result

parcels=[];ground_owners=array('I',[0])*N
paved=ImageChops.subtract(residual,green)
for kind,mask,color,material in [('compact-courtyard',paved,'#e7dfd0','warm-small-format-paving;compact-courtyard;no-lawn'),('pocket-garden',green,'#b2c18c','small-ground-planter-only;no-large-lawn')]:
    for cells in components_for(mask):
        pid=f'DV2-P{len(parcels)+1:03}';center=world((sum(i%W for i in cells)/len(cells)+.5,sum(i//W for i in cells)/len(cells)+.5))
        parcels.append({'id':pid,'landUse':kind,'name':'紧凑内院与必要人行空间' if kind=='compact-courtyard' else '微型口袋绿地/花槽','groundColor':color,'groundMaterial':material,'areaSquareMetresApprox':len(cells)*R*R,'center':center,'rings':rings(cells),'ringFillRule':'evenodd','origin':'v2-rebuilt-derived-ground;0.5m-decorative-boundary'})
        for i in cells:ground_owners[i]=len(parcels)
for item in trees+features:
    p=item.get('groundAnchor')
    if p is None:a,b=item['bounds'];p=[(a[0]+b[0])/2,(a[1]+b[1])/2]
    x,y=map(int,xy(p));owner=ground_owners[y*W+x];item['parcelId']=parcels[owner-1]['id'] if owner else None
# Blocks reserve protected geometry plus all residual local spaces. They are not POIs.
blocks=[]
for owner,cells in enumerate(components,1):
    if not any(b['parcelId']==f'DV2-BLOCK-{owner:03}' for b in buildings):continue
    blocks.append({'id':f'DV2-BLOCK-{owner:03}','source':'preplacement-buildable-component','rings':rings(cells),'areaSquareMetresApprox':len(cells)*R*R,'noninteractive':True})
# Existing renderer expects building.parcelId to resolve in parcels. Keep legal free
# block geometry as a transparent ground record with no additional counted surface.
for block in blocks:
    pts=[v for r in block['rings'] for v in r]
    parcels.append({'id':block['id'],'landUse':'built-block','name':'连续商住建筑组团','groundColor':'#e7dfd0','groundMaterial':'none;group-reference-only','areaSquareMetresApprox':block['areaSquareMetresApprox'],'center':[(min(v[0] for v in pts)+max(v[0] for v in pts))/2,(min(v[1] for v in pts)+max(v[1] for v in pts))/2],'rings':block['rings'],'ringFillRule':'evenodd','renderGround':False,'areaAccountingRole':'reference-only-not-extra-land-area','origin':'v2-building-group-reference'})
# Exact per-footprint planar area and exact rectangular clipping for originals.
def clip_polygon(ps):
    p=[list(v) for v in ps]
    if p and p[0]==p[-1]:p.pop()
    for axis,limit,sign in [(0,B['minX'],1),(0,B['maxX'],-1),(1,B['minY'],1),(1,B['maxY'],-1)]:
        q=[]
        for a,b in zip(p,p[1:]+p[:1]):
            ia=(a[axis]-limit)*sign>=0;ib=(b[axis]-limit)*sign>=0
            if ia:q.append(a)
            if ia!=ib:
                t=(limit-a[axis])/(b[axis]-a[axis]);v=[a[k]+t*(b[k]-a[k]) for k in (0,1)];v[axis]=limit;q.append(v)
        p=q
        if not p:break
    return p
area=lambda ps:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]+ps[:1]))/2) if ps else 0
original_exact=sum(area(clip_polygon(b['footprint'])) for b in original)
new_exact=sum(area(b['footprint']) for b in buildings)
mask_area=lambda m:round(m.histogram()[255]*R*R,4)
total=380*440;orig_union=mask_area(building_mask);new_union=mask_area(new_mask);green_area=mask_area(green);paved_area=mask_area(paved)
free_paving=ImageChops.multiply(paved,free);protected_paving=ImageChops.multiply(paved,protected)
near_new_paving=ImageChops.multiply(free_paving,new_mask.filter(ImageFilter.MaxFilter(13)))
# Disjoint cover accounting precedence: water > actual road > original > new > green > paving.
remaining=Image.new('L',(W,H),255);cover={}
for label,mask in [('water',water_mask),('originalRoadSurface',road_mask),('originalBuildings',building_mask),('newBuildings',new_mask),('green',green),('pavingAndNecessaryOpenLand',paved)]:
    take=ImageChops.multiply(remaining,mask);cover[label]=mask_area(take);remaining=ImageChops.subtract(remaining,take)
summary={'date':'2026-11-03','status':'density-v2-produced-not-engine-integrated-or-user-accepted','bounds':B,'sampleAreaSquareMetres':total,'maskResolutionMetres':R,'sourceBuildingCount':len(original),'newBuildingCount':len(buildings),'floorDistribution':dict(sorted(Counter(b['floorCount'] for b in buildings).items())),'moduleDistribution':dict(Counter(b['module'] for b in buildings)),'sourceFootprintAreaSumClippedExactSquareMetres':round(original_exact,4),'sourceFootprintUnionRasterSquareMetres':orig_union,'newFootprintAreaSumExactSquareMetres':round(new_exact,4),'newFootprintUnionRasterSquareMetres':new_union,'preplacementFreeGroundAreaSquareMetres':free_area,'newExactFootprintCoverageOfPreplacementFreeGround':round(new_exact/free_area,6),'newRasterFootprintCoverageOfPreplacementFreeGround':round(new_union/free_area,6),'newAndOriginalBuildingUnionFractionOfWholeSampleApprox':round(mask_area(ImageChops.lighter(new_mask,building_mask))/total,6),'greenAreaSquareMetresApprox':green_area,'greenFractionOfPreplacementFreeGroundApprox':round(green_area/free_area,6),'greenFractionOfWholeSampleApprox':round(green_area/total,6),'pavingAndNecessaryOpenLandAreaSquareMetresApprox':paved_area,'pavingAndNecessaryOpenLandFractionOfWholeSampleApprox':round(paved_area/total,6),'pavingBreakdownSquareMetresApprox':{'requiredProtectedSetbacksAndSidewalks':mask_area(protected_paving),'remainingPreplacementFreeGroundPaving':mask_area(free_paving),'ofFreePavingWithin3mOfNewBuildings':mask_area(near_new_paving),'ofFreePavingFurtherThan3mFromNewBuildings':mask_area(ImageChops.subtract(free_paving,near_new_paving))},'buildingCoverageOfNonRoadNonWaterLandApprox':round((cover['originalBuildings']+cover['newBuildings'])/(total-cover['water']-cover['originalRoadSurface']),6),'wholeSampleDisjointCoverageSquareMetresApprox':cover,'disjointCoverageTotalSquareMetres':round(sum(cover.values()),4),'unassignedRasterSquareMetres':mask_area(remaining),'parcels':len(parcels),'groundParcels':sum(p.get('renderGround',True) for p in parcels),'buildingGroupReferenceParcels':len(blocks),'trees':len(trees),'features':len(features),'pocketGardenMaximumConnectedAreaSquareMetresApprox':max([p['areaSquareMetresApprox'] for p in parcels if p['landUse']=='pocket-garden'] or [0]),'placementPasses':placement_records,'targetInterpretation':'PM production target, not user-approved numerical parameter: new footprint about50-65% of preplacement free ground; green <=8-12%; small lawns not target to fill','targetNewCoverageReached':.50<=new_exact/free_area<=.65,'targetGreenUpperLimitReached':green_area/free_area<=.12,'precisionNotes':['Original raw floating geometry unchanged.','Analytic per-original-footprint areas are clipped to the sample then summed; overlaps can double count. Union figures use 0.5m raster instead.','Exact new-footprint sum uses shoelace and nonoverlapping rectangles; raster footprint area includes conservative edge pixels.','Free denominator excludes actual roads plus2.5m per-side sidewalk, conservative20m waterway+1m bank margin, original buildings+1.5m margin,5m entrance disks,1m sample edge.','Placement adds1m expanded mask around each new building; adjacent buildings retain about2m service/pedestrian spacing plus raster conservatism.','Paving includes required sidewalks, original-building setbacks, bank access, microcourtyards and residual alleys; it is not all a plaza.'],'runtimeTestsRun':False,'userVisualAcceptance':False}
result={'version':2,'date':'2026-11-03','status':summary['status'],'source':str(SRC.relative_to(ROOT)),'sourceSHA256':SHA,'bounds':B,'coordinateUnit':'ground-metres','groundBoundaryPrecision':'0.5m raster only for decorative ground;source floats unchanged;new footprint vertices 0.0001m rounding','parcels':parcels,'addedBuildings':buildings,'sceneFeatures':features,'trees':trees,'sourceBuildings':original,'sourceRoads':roads,'sourceWaterPolygons':waters,'sourceWaterways':waterways,'entrances':entrances,'constraints':{'newRoadEdgesAdded':False,'originalMapModified':False,'newOperatingAddressesAdded':False,'roofTreesAllowed':False,'waterwayDecorativeProtectionWidthMetres':20,'roadSidewalkPerSideMetres':2.5,'existingBuildingProtectionMetres':1.5,'newBuildingClearancePerSideMetres':1,'dynamicGameValidationRun':False,'supersedesDerivedSampleLayoutOnly':str(OLD.relative_to(ROOT)),'sourceGeometryAndSampleBoundsFrozen':True},'densitySummary':summary,'feedbackSource':{'path':str(FEEDBACK.relative_to(ROOT)),'sha256':sha(FEEDBACK),'rejectedOriginalDerivativePreserved':True},'renderNotes':['renderGround=false built-block parcels are grouping/reference only; skip ground fill for them.','Other rings are evenodd, with original/new building holes retained.','Source buildings keep original footprints and heights; use sourceIndex for deterministic facade variation.','New styleProfile and streetFacingHint guide facade/shop orientation; they do not add routes or operating addresses.']}
def write(n,o): (O/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
write('sample-scene-layout-v2.json',result);write('density-summary.json',summary)
print(json.dumps({'interfaceReady':str(O/'sample-scene-layout-v2.json'),'newBuildings':len(buildings),'newCoverage':summary['newExactFootprintCoverageOfPreplacementFreeGround'],'greenFraction':summary['greenFractionOfPreplacementFreeGroundApprox'],'footprintArea':round(new_exact,2),'freeArea':free_area,'targetReached':summary['targetNewCoverageReached']},ensure_ascii=False),flush=True)
# New flat planning image, drawn from new data, never edit user-provided images.
SCALE=5;im=Image.new('RGB',(W//2*SCALE+100,H//2*SCALE+330),'#faf9f3');dr=ImageDraw.Draw(im)
cv=lambda p:(50+(p[0]-B['minX'])*SCALE,150+(B['maxY']-p[1])*SCALE)
# Paint the masks as a data visualization; preserve source geometry on top.
ground=Image.new('RGB',(W,H),'#e7dfd0');ground.paste('#aebb8a',mask=green);ground.paste('#9dbfbc',mask=water_mask);ground.paste('#778187',mask=road_mask);ground.paste('#b8b5a9',mask=building_mask);ground.paste('#d4ac79',mask=new_mask);im.paste(ground.resize((1900,2200),Image.Resampling.NEAREST),(50,150));dr=ImageDraw.Draw(im)
for b in original+buildings:
    points=[cv(v) for v in b['footprint']];dr.line(points+[points[0]],fill='#797c72' if 'sourceIndex' in b else '#886849',width=2)
for t in trees:
    x,y=cv(t['groundAnchor']);rr=t['crownDiameterMetres']*SCALE/2;dr.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#728d4d',outline='#5c743f',width=2)
for e in entrances:
    x,y=cv(e['groundAnchor']);dr.ellipse((x-10,y-10,x+10,y+10),fill='#e98c2f',outline='#fff6df',width=3)
# Original geometry can extend beyond the sample: clip margins after source outline draw.
for box in [(0,0,im.width,149),(0,150,49,im.height),(1951,150,im.width,im.height),(0,2351,im.width,im.height)]:dr.rectangle(box,fill='#faf9f3')
f=lambda size,b=False:ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc' if b else '/System/Library/Fonts/STHeiti Light.ttc',size)
dr.text((50,25),'首块样板 v2 · 建筑为主的连续商住',font=f(43,True),fill='#344136')
dr.text((50,90),'暖棕：新增建筑  灰：原楼体  浅暖色：必要步道/紧凑内院  绿色：微型口袋绿地',font=f(25),fill='#596455')
dr.text((50,2380),f'新增楼体 {len(buildings)}栋 / 足迹 {new_exact:,.0f}m² / 剩余可布置地面覆盖 {new_exact/free_area:.1%}',font=f(27,True),fill='#344136')
dr.text((50,2425),f'绿地 {green_area:,.0f}m² / 可布置地面 {green_area/free_area:.1%}；原道路、水系、原楼体及两个入口保持',font=f(26),fill='#596455')
dr.text((50,2470),'380×440m · 0.5m装饰栅格 · 新数据规划图，非美术成品/游戏截图 · 未游戏测试/用户视觉验收',font=f(23),fill='#596455')
im.save(O/'01-sample-density-v2-plan.png')
# Read-only data checks, not runtime/game tests.
new_polygons_clear=all(not ImageChops.multiply(protected.crop(local_mask(b['footprint'],0)[0]),local_mask(b['footprint'],0)[1]).getbbox() for b in buildings)
def polygons_disjoint(a,b):
    for poly in [a,b]:
        for v,w in zip(poly,poly[1:]):
            axis=[-(w[1]-v[1]),w[0]-v[0]]
            if not any(axis):continue
            pa=[v[0]*axis[0]+v[1]*axis[1] for v in a];pb=[v[0]*axis[0]+v[1]*axis[1] for v in b]
            if max(pa)<min(pb)-1e-8 or max(pb)<min(pa)-1e-8:return True
    return False
checks={'newFootprintsPairwiseDisjointAnalytic':all(polygons_disjoint(a['footprint'],b['footprint']) for i,a in enumerate(buildings) for b in buildings[i+1:]),'allFeatureAndTreeParcelReferencesResolve':all(item.get('parcelId') in {p['id'] for p in parcels} for item in trees+features),'sourceSHA256Unchanged':sha(SRC)==SHA,'sourceArraysUnchanged':{k:result[k]==old[k] for k in ['sourceBuildings','sourceRoads','sourceWaterPolygons','sourceWaterways','entrances']},'originalFootprintsMatchRaw':all(b['footprint']==raw['buildings'][b['sourceIndex']] for b in original),'originalRoadFloatPointsMatchRawNodes':all(r['points']==[nodes[n] for n in r['nodes']] for r in roads),'newFootprintsInsideSample':all(all(inside(v) for v in b['footprint']) for b in buildings),'newFootprintsAvoidOriginalProtectedRaster':new_polygons_clear,'allNewBuildingIdsUnique':len(set(b['id'] for b in buildings))==len(buildings),'allNewBuildingParcelReferencesResolve':all(any(p['id']==b['parcelId'] for p in parcels) for b in buildings),'wholeSampleAreaAccounted':sum(cover.values())==total and mask_area(remaining)==0,'newNonOverlappingAreaEvidence':'greedy placement rejects any intersection with all previous padded footprints before reserving each placement','rawSourceAndOldDerivativeNotWritten':True,'runtimeTestsRun':False}
assert all(checks[k] for k in ['newFootprintsPairwiseDisjointAnalytic','allFeatureAndTreeParcelReferencesResolve','sourceSHA256Unchanged','originalFootprintsMatchRaw','originalRoadFloatPointsMatchRawNodes','newFootprintsInsideSample','newFootprintsAvoidOriginalProtectedRaster','allNewBuildingIdsUnique','allNewBuildingParcelReferencesResolve','wholeSampleAreaAccounted']);assert all(checks['sourceArraysUnchanged'].values())
write('integrity-report.json',checks)
manifest={'date':'2026-11-03','sourceSHA256':SHA,'oldDerivedSourceSHA256':sha(OLD),'feedbackSHA256':sha(FEEDBACK),'outputs':[],'runtimeTestsRun':False}
for name in ['sample-scene-layout-v2.json','density-summary.json','01-sample-density-v2-plan.png','build-density-v2.py','integrity-report.json','README.md']:
    p=O/name;item={'path':name,'sha256':sha(p),'bytes':p.stat().st_size}
    if p.suffix=='.png':
        with Image.open(p) as img:item['pixels']=list(img.size)
    manifest['outputs'].append(item)
write('manifest.json',manifest)
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
