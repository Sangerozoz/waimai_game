#!/usr/bin/env python3
"""Executed static data planning only. Python stdlib + Pillow; never edits source data."""
import json, math, hashlib, itertools, html
from pathlib import Path
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
KIT=OUT.parent.parent
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
citypath=ROOT/'delivery-game/assets/resources/map-sample/city.json';zonepath=ROOT/'docs/art/2026-11-02-county-zoning/selection.json'
c=read(citypath);z=read(zonepath);g=read(KIT/'revision-003/road-constraint.json');old=read(KIT/'revision-005/planning/mixed-street-layout.json')
assert all(k in c for k in ['nodes','roads','buildings','areas','waterways','pois'])
assert all(set(['id','x','y'])<=set(n) for n in c['nodes'])
nodes={n['id']:[n['x'],n['y']] for n in c['nodes']};roads={r['id']:r for r in c['roads']}
assert all(set(['id','nodes','width','direction'])<=set(r) and all(i in nodes for i in r['nodes']) for r in c['roads'])
assert all(isinstance(b,list) and all(len(p)==2 for p in b) for b in c['buildings'])
u=g['streetTangentMap'];n=[-u[1],u[0]];P=g['projection']; origin=[-1610,100]
def add(a,b):return [a[0]+b[0],a[1]+b[1]]
def mul(a,k):return [a[0]*k,a[1]*k]
def rect(a,w,d):return [add(add(a,mul(u,x*w/2)),mul(n,y*d/2)) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def ps(p,a,b):
 v=[b[i]-a[i] for i in (0,1)];den=sum(x*x for x in v);t=max(0,min(1,sum((p[i]-a[i])*v[i] for i in (0,1))/den)) if den else 0
 return math.dist(p,[a[i]+t*v[i] for i in (0,1)])
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def ss(a,b,c,d):
 if cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0 and max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):return 0.
 return min(ps(a,c,d),ps(b,c,d),ps(c,a,b),ps(d,a,b))
def edges(poly):return list(zip(poly,poly[1:]+poly[:1]))
def pp(a,b):
 if inside(a[0],b) or inside(b[0],a):return 0.
 return min(ss(p,q,r,s) for p,q in edges(a) for r,s in edges(b))
def pl(poly,a,b):
 if inside(a,poly) or inside(b,poly):return 0.
 return min(ss(p,q,a,b) for p,q in edges(poly))
def inbounds(p,k):
 b=z['regions'][k]['worldBoundsMetresApprox'];return b['minX']<=p[0]<=b['maxX'] and b['minY']<=p[1]<=b['maxY']
def zone(p):return 'denseUrban' if inbounds(p,'urban') else 'suburb' if inbounds(p,'city') else 'outerLandscape' if inbounds(p,'map') else 'outsideRed'
def near(p):return -1820<p[0]<-1400 and -200<p[1]<350
def overlapsWindow(points):return min(p[0] for p in points)<-1400 and max(p[0] for p in points)>-1820 and min(p[1] for p in points)<350 and max(p[1] for p in points)>-200
roadsegments=[(r['id'],i,nodes[a],nodes[b],r['width']/2) for r in c['roads'] for i,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:])) if overlapsWindow([nodes[a],nodes[b]])]
waterpolys=[a['points'] for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3 and overlapsWindow(a['points'])]
# Lines do not encode bank widths: use explicit conservative 3m safety radius, not a surveyed bank.
waterlines=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:]) if overlapsWindow([a,b])]
sourcebuildings=[(i,b) for i,b in enumerate(c['buildings']) if len(b)>=3 and overlapsWindow(b)]
pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node') in nodes and near(nodes[p['node']])]
locked=[b['footprintPolygonMap'] for b in old['buildings']]
def checks(poly,existing):
 rd=min((pl(poly,a,b)-hw,rid,i) for rid,i,a,b,hw in roadsegments)
 wd=min([pp(poly,b) for b in waterpolys]+[pl(poly,a,b)-3 for a,b in waterlines]+[9999])
 bd=min([pp(poly,b) for b in existing]+[9999]);sb=min((pp(poly,b),i) for i,b in sourcebuildings)
 pd=min([min(ps(p,a,b) for a,b in edges(poly)) if not inside(p,poly) else 0 for _,_,p in pois]+[9999])
 return {'roadEdgeMetres':rd[0],'nearestRoadId':rd[1],'nearestRoadSegmentIndex':rd[2],'waterMetres':wd,'buildingGapMetres':bd,'sourceBuildingGapMetres':sb[0],'nearestSourceBuildingIndex':sb[1],'businessEntranceMetres':pd}
def clear(q):return q['roadEdgeMetres']>=2 and q['waterMetres']>=3 and q['buildingGapMetres']>=2.5 and q['sourceBuildingGapMetres']>=1 and q['businessEntranceMetres']>=6
# These are design envelopes, NOT measurements of new native artwork.
dims={b['id']:b['dimensionsCandidate'] for b in old['buildings']}
dims.update({k:dict(frontage=w,depth=d,height=h) for k,w,d,h in [('B06',8,6,7),('B07',10,8,14),('B08',12,8,7),('B09',13,10,8),('B10',12,9,7),('B11',7,6,5)]})
specs=[('N1',[7,8],['B06','B07','B05','B06','B11','B01'],'residential-courtyard'),('N2',[8,9],['B08','B09','B02','B04','B01'],'commercial-civic'),('S1',[14,15],['B10','B11','B07','B05','B03'],'residential-service-mix')]
placed=[];streets=[];rejections=0
for sid,(ia,ib),ids,typ in specs:
 r=roads['149397380-0'];a,b=[nodes[r['nodes'][i]] for i in [ia,ib]];L=math.dist(a,b);t=[(b[i]-a[i])/L for i in (0,1)]
 screen=[t[0]*P['axisX'][i]+t[1]*P['axisY'][i] for i in (0,1)];ang=math.degrees(math.atan2(screen[1],screen[0]));delta=(ang-g['groundEdgeAnglesScreenDeg']['frontage']+90)%180-90
 street={'id':sid,'type':typ,'roadId':r['id'],'nodeIndexRangeInclusive':[ia,ib],'nodeIds':r['nodes'][ia:ib+1],'polylineMap':[a,b],'width':r['width'],'direction':r['direction'],'lengthMetres':L,'actualTangentMap':t,'projectedFrontageDeg':ang,'differenceFromAssetFrontageDeg':delta,'orientationCompatibleCandidate':abs(delta)<=3,'zone':'denseUrban','side':'west; entry faces east toward source road; no mirrored PNG','buildingIds':[]}
 assert abs(delta)<=3
 # Search deterministic free pockets on west side; source buildings and all roads remain obstacles.
 for aid in ids:
  dim=dims[aid];w,d=dim['frontage'],dim['depth'];options=[]
  for s in range(9,int(L)-7,2):
   ref=add(a,mul(t,s))
   for setback in [3,5,8,12,17,23,30,38,46]:
    anchor=add(ref,mul(n,-(r['width']/2+setback+d/2)));poly=rect(anchor,w,d)
    if not all(inbounds(p,'urban') for p in poly):continue
    q=checks(poly,locked+[p['footprintPolygonMap'] for p in placed])
    if not clear(q):rejections+=1;continue
    options.append((setback,s,anchor,poly,q,ref))
  if not options:
   street.setdefault('unplacedAssetGaps',[]).append(aid);continue
  setback,s,anchor,poly,q,ref=min(options,key=lambda v:(v[0],v[1]))
  pid=f'{sid}-{len(street["buildingIds"])+1:02d}-{aid}';street['buildingIds'].append(pid)
  placed.append({'id':pid,'assetId':aid,'streetId':sid,'zone':zone(anchor),'zoneBasis':{'selectionSHA256':sha(zonepath),'region':'urban green','worldBoundsMetresApprox':z['regions']['urban']['worldBoundsMetresApprox'],'allParcelVerticesInsideGreen':all(inbounds(v,'urban') for v in rect(anchor,w+1,d+1))},'anchorMap':anchor,'anchorMeaning':'candidate footprint centre; image contact calibration required','footprintPolygonMap':poly,'parcelPolygonMap':rect(anchor,w+1.0,d+1.0),'candidateDimensionsMetres':dim,'candidateSetbackFromOwnRoadEdgeMetres':setback,'roadReferenceMap':ref,'roadId':r['id'],'roadNodeRangeInclusive':[ia,ib],'entryMap':add(anchor,mul(n,d/2)),'rotationPNG':0,'mirrorPNG':False,'scalePolicy':'positive uniform only, final scale from native ground contact calibration','staticClearance':q,'nativeStatus':'read-only-existing-library' if int(aid[1:])<=5 else 'current-wave-dependency-not-assumed-ready'})
 streets.append(street)
print('placed',len(placed),'streets',[(s['id'],len(s['buildingIds']),s.get('unplacedAssetGaps'),s['differenceFromAssetFrontageDeg']) for s in streets])
# Ground parcels never overwrite the source road. Reserve the building parcel and independent shared courts.
surfaces=[{'id':p['id']+'-parcel','type':'private-paving' if p['streetId']=='N2' else 'residential-garden-base','material':'S01-paving' if p['streetId']=='N2' else 'neutral-grass','polygonMap':p['parcelPolygonMap'],'containsBuildingId':p['id']} for p in placed]
fixtures=[];courtgaps=[]
for s in streets:
 a,b=s['polylineMap'];t=s['actualTangentMap'];L=s['lengthMetres'];found=False
 for cw,cd,along in itertools.product([10,6,4],[8,6,4],range(12,int(L)-8,3)):
  for back in [12,18,27,36,45,54,62]:
   anchor=add(add(a,mul(t,along)),mul(n,-back));poly=rect(anchor,cw,cd)
   q=checks(poly,locked+[p['parcelPolygonMap'] for p in placed]+[v['polygonMap'] for v in surfaces if not v.get('containsBuildingId')])
   if clear(q):
    typ='civic-plaza' if s['id']=='N2' else 'garden-courtyard' if s['id']=='N1' else 'service-parking-court'
    surfaces.append({'id':s['id']+'-court','type':typ,'material':'S01-paving' if s['id']!='N1' else 'neutral-grass','polygonMap':poly,'staticClearance':q,'vehicularAccess':'not asserted; no new road or driveway; parked props only'})
    for j,off in enumerate([-min(3,cw/2-1.2),min(3,cw/2-1.2)]):
     fixtures.append({'id':s['id']+f'-tree-{j}','assetId':'T02' if j else 'T01','anchorMap':add(anchor,mul(u,off)),'groundRadiusCandidateMetres':0.9,'role':'courtyard planting'})
    if s['id']!='N1' and cw>=6 and cd>=6:fixtures.append({'id':s['id']+'-car','assetId':'V01' if s['id']=='N2' else 'V02','anchorMap':add(anchor,mul(n,2)),'candidateFootprintPolygonMap':rect(add(anchor,mul(n,2)),4.2,1.8),'orientationStatus':'requires actual V01/V02 native direction check; parked-only; do not rotate PNG','role':'parked static decoration'})
    found=True;break
  if found:break
 if not found:courtgaps.append(s['id'])
# Lamps use clear 0.25m circular ground proxy, avoiding all planned footprints and source geometry.
for s in streets:
 a,b=s['polylineMap'];t=s['actualTangentMap']
 for along in [12,s['lengthMetres']-12]:
  pos=add(add(a,mul(t,along)),mul(n,-(roads[s['roadId']]['width']/2+2.7)))
  q=checks(rect(pos,.5,.5),locked+[p['parcelPolygonMap'] for p in placed])
  if clear(q):fixtures.append({'id':s['id']+f'-lamp-{along:.0f}','assetId':'L-near','anchorMap':pos,'groundRadiusCandidateMetres':.25,'staticClearance':q,'role':'west verge; use existing inward lamp candidate'})
# Every auxiliary footprint gets independent static results; no claim of render occlusion clearance.
for f in fixtures:
 poly=f.get('candidateFootprintPolygonMap') or rect(f['anchorMap'],2*f.get('groundRadiusCandidateMetres',.25),2*f.get('groundRadiusCandidateMetres',.25))
 f['staticClearance']=checks(poly,locked+[p['footprintPolygonMap'] for p in placed])
for s in surfaces:
 s['roadWaterSourceClearance']=checks(s['polygonMap'],[])
# Audit static auxiliary pair overlaps, using ground envelopes only.
fixturePairs=[]
for a,b in itertools.combinations(fixtures,2):
 def fp(v):return v.get('candidateFootprintPolygonMap') or rect(v['anchorMap'],v.get('groundRadiusCandidateMetres',.25)*2,v.get('groundRadiusCandidateMetres',.25)*2)
 fixturePairs.append({'ids':[a['id'],b['id']],'groundGapMetres':pp(fp(a),fp(b))})
# Store the complete source road graph and water/entrance context unchanged.
snapshot={'source':str(citypath),'sourceSHA256':sha(citypath),'nodes':c['nodes'],'roads':c['roads'],'waterways':c['waterways'],'waterAreas':[a for a in c['areas'] if a.get('kind')=='water'],'pois':c['pois'],'sourceBuildings':c['buildings']}
write('source-context.json',snapshot)
assert read(OUT/'source-context.json')['roads']==c['roads']
sourcePaths=[citypath,zonepath,KIT/'revision-003/road-constraint.json',KIT/'revision-005/planning/mixed-street-layout.json',KIT/'revision-005/integration/mixed-street.tmj',KIT/'revision-005/integration/asset-calibration.json',OUT.parent/'references/approved-25-index.json']
sources=[{'path':str(p),'sha256':sha(p)} for p in sourcePaths]
oldzone=[{'id':b['id'],'anchorMap':b['anchorMap'],'anchorZone':zone(b['anchorMap']),'allFootprintInsideGreen':all(inbounds(p,'urban') for p in b['footprintPolygonMap'])} for b in old['buildings']]
# Read-only observed architecture references, not generation inputs or measured dimensions.
idx=read(OUT.parent/'references/approved-25-index.json')
selections=[]
for num,box,reason in [(1,[483,628,694,779],'完整拱形玻璃市场体量与小型商铺对照；规划商业节点，不复制整张构图'),(11,[683,693,812,815],'中心多层退台楼与低层庭院形成高低差；规划住宅/服务混合街段')]:
 item=next(x for x in idx['sources'] if x['imageNumber']==num);assert sha(item['source'])==item['sha256']
 selections.append({**item,'completeSingleBuildingBoxPixelsApprox':box,'boxStatus':'visually estimated; not precise segmentation; may include immediate apron/context','reason':reason,'purpose':'planning morphology observation only; no image generation or native asset claim'})
write('references/visual-selection.json',{'openedFullSourceImages':[x['source'] for x in selections],'selections':selections,'noUpscaledNativeOrFullNeighborGenerationInput':True})
# Road orientations crossing and bounding the selected neighborhood, with explicit gaps.
orientationgaps=[]
for rid in sorted({rid for rid,i,a,b,hw in roadsegments}):
 r=roads[rid];seg=[]
 for i,(aa,bb) in enumerate(zip(r['nodes'],r['nodes'][1:])):
  a,b=nodes[aa],nodes[bb]
  if math.dist(a,b)<4 or not(any(math.dist(p['anchorMap'],a)<90 or math.dist(p['anchorMap'],b)<90 for p in placed)):continue
  v=[b[j]-a[j] for j in (0,1)];sv=[v[0]*P['axisX'][j]+v[1]*P['axisY'][j] for j in (0,1)];angle=math.degrees(math.atan2(sv[1],sv[0]));delta=(angle-g['groundEdgeAnglesScreenDeg']['frontage']+90)%180-90
  if abs(delta)>3:seg.append({'nodeRangeInclusive':[i,i+1],'nodeIds':[aa,bb],'projectedFrontageDeg':angle,'assetDifferenceDegModulo180':delta})
 if seg:orientationgaps.append({'roadId':rid,'segments':seg,'action':'new native frontage direction if buildings later face this road; no rotation/mirror/shear; no placement assigned here'})
plan={'schemaVersion':1,'status':'executed-static-candidate-not-user-accepted-or-runtime-ready','units':'source city metres; all polygon rings unclosed','sourceSchema':{'nodes':'array of id/x/y','roads':'array id/nodes ordered node IDs/width/direction; all preserved verbatim in source-context.json','buildings':'array of rings of [x,y]','areas':'array kind/points','waterways':'array of line point arrays; bank width absent','pois':'array name/node/kind'},'sources':sources,'sourceGraphSnapshot':{'file':'source-context.json','sha256':sha(OUT/'source-context.json'),'roadsCount':len(c['roads']),'nodesCount':len(c['nodes']),'unalteredNodeOrderWidthsDirections':True},'zoning':{'registration':z['registration'],'regions':z['regions'],'semantics':z['semanticZones'],'precision':'user-approved approximate rectangles, not surveyed; brown frame ignored'},'approved005ZoneAudit':{'buildings':oldzone,'decision':'all five footprints are green denseUrban; suitable as read-only visual/geometry baseline, no relocation needed; new layout excludes these footprints'},'projection':P,'fixedAssetFrame':{'frontageTangentMap':u,'eastNormalMap':n,'frontageScreenDeg':g['groundEdgeAnglesScreenDeg']['frontage'],'depthScreenDeg':g['groundEdgeAnglesScreenDeg']['depth'],'wallVertical':True,'orientationToleranceCandidateDeg':3,'noPNGTransform':True},'streets':streets,'buildings':placed,'groundSurfaces':surfaces,'fixtures':fixtures,'existingBusinessEntrances':[{'sourcePOIIndex':i,'originalPOI':p,'anchorMap':a,'preserved':True} for i,p,a in pois],'orientationGaps':orientationgaps,'unplacedCourtyardGaps':courtgaps,'areaPolicy':'住宅约50%仅全县蓝内总体用地方向；不按本块楼数强凑。三个街段形成两类空间：住宅庭院/服务混合，商业公共设施。','resourcePolicy':{'runtimeMaxEdge':280,'sharedTexturePerAssetId':True,'nativeMastersExcludedFromPackage':True,'referencedBuildingIds':sorted({p['assetId'] for p in placed}),'dependencies':'B01..B05 read-only runtime-280 library; B06..B11/V01/V02 current-wave candidate pending actual provenance/runtime/contact check; no native generation by planning role','noPackageBuilt':True},'cameraSuggestions':{'projectionId':P['id'],'elevationDeg':62.5,'azimuthDeg':45,'focusMap':[-1605,87],'overviewWorldWidthCandidate':220,'closeWorldWidthCandidate':65,'note':'geometry-only suggestions; no browser/render/game validation; camera cannot rotate PNG'},'staticCheckPolicy':{'roadWidthApplied':'all local source segments half-width capsule; line/polygon exact double calculations','waterLinesSafetyRadiusMetres':3,'waterAreaBankMarginMetres':3,'buildingGapTargetMetres':2.5,'sourceBuildingGapTargetMetres':1,'businessEntranceRadiusMetres':6,'rejectedCandidatePositions':rejections,'scope':'static geometry only; candidate footprints/contact estimates, not precise native calibration; no runtime occlusion or route claim','noNewRoadBridgePOI':True}}
# Candidate anchors are ground-centre design anchors, separate from native image pivots.
cal=read(KIT/'revision-005/integration/asset-calibration.json')
assets=[]
for aid in sorted({b['assetId'] for b in placed}|{f['assetId'] for f in fixtures}):
 matches=list((KIT/'revision-005/integration/assets').glob('*'+aid+'*280*.png')) if aid.startswith('B') and int(aid[1:])<=5 else list((OUT.parent/'native').glob('**/'+aid+'-runtime-280.png'))
 if aid=='B01':matches=list((KIT/'revision-005/integration/assets').glob('rt-B01*.png'))
 if aid.startswith('T'):matches=list((KIT/'revision-005/integration/assets').glob('*'+aid+'*.png'))
 if aid=='L-near':matches=list((KIT/'revision-005/integration/assets').glob('L-near-280.png'))
 ac=next((v for v in cal['assets'] if v['id']==aid),None)
 assets.append({'assetId':aid,'sharedTextureKey':aid,'snapshotRuntimeFiles':[{'path':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size),'bytes':p.stat().st_size,'within280':max(Image.open(p).size)<=280} for p in matches],'imageAnchorUV':ac.get('anchorUV') if ac else None,'anchorStatus':'manual/inferred candidate from revision005' if ac else 'current-wave native foot/contact measurement pending','generationByThisRole':False})
plan['resourceDependencies']=assets
# Original roadway connectivity is actual node continuity; this does not create building POIs or paths.
r=roads['149397380-0']
plan['originalRoadConnection']={'roadId':r['id'],'nodeRangeInclusive':[7,15],'nodeIds':r['nodes'][7:16],'polylineMap':[nodes[i] for i in r['nodes'][7:16]],'allNodesInsideGreen':all(inbounds(nodes[i],'urban') for i in r['nodes'][7:16]),'direction':r['direction'],'newGraphEdges':0}
for b in placed:
 blockers=[i for i,poly in sourcebuildings if pl(poly,b['entryMap'],b['roadReferenceMap'])<.5]
 b['entryAccessAudit']={'straightGroundApproachToAssignedRoadSourceBuildingBlockers':blockers,'status':'straight approach blocked; courtyard pedestrian access needs separate static surface planning' if blockers else 'straight ground approach clear of source buildings only; not a route/POI','roadGraphUnchanged':True}
write('next-neighborhood-plan.json',plan)
# SVG/Pillow diagram: explicit geometry draft, source roads/buildings visible; no rendered art claim.
colors={'N1':'#69a97f','N2':'#e9ad5e','S1':'#83a6cd'}
for iso in [False,True]:
 def proj(p):
  x,y=p[0]-origin[0],p[1]-origin[1]
  return (x*P['axisX'][0]+y*P['axisY'][0],x*P['axisX'][1]+y*P['axisY'][1]) if iso else (x,-y)
 ext=[proj(p) for b in placed for p in b['parcelPolygonMap']]+[proj(p) for s in streets for p in s['polylineMap']]
 mn=[min(p[j] for p in ext)-20 for j in (0,1)];mx=[max(p[j] for p in ext)+20 for j in (0,1)]
 W,H=(1400,1050) if iso else (1400,1800);scale=min((W-100)/(mx[0]-mn[0]),(H-180)/(mx[1]-mn[1]))
 def xy(p):q=proj(p);return (50+(q[0]-mn[0])*scale,120+(q[1]-mn[1])*scale)
 im=Image.new('RGB',(W,H),'#f6f5f0');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#f6f5f0"/>']
 def polygon(poly,fill,stroke='#777777'):
  pts=[xy(p) for p in poly];dr.polygon(pts,fill=fill,outline=stroke);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}"/>')
 def line(pts,color,width=1):
  ps=[xy(p) for p in pts];dr.line(ps,fill=color,width=max(1,round(width)));svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" fill="none" stroke="{color}" stroke-width="{width:.2f}"/>')
 def label(pos,txt,color='#222222'):
  x,y=pos;dr.text((x,y),txt,fill=color);svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="sans-serif" font-size="13" fill="{color}">{html.escape(txt)}</text>')
 for i,b in sourcebuildings:polygon(b,'#e6e4df','#cccccc')
 for w in waterpolys:polygon(w,'#b0d8e5')
 for a,b in waterlines:line([a,b],'#8eb9d4',3*scale)
 for rid,i,a,b,hw in roadsegments:line([a,b],'#b8b6b0',hw*2*scale)
 for s in surfaces:polygon(s['polygonMap'],'#dce7c9' if s['type'] in ['residential-garden-base','garden-courtyard'] else '#e2d8c7','#b3ab98')
 for b in old['buildings']:polygon(b['footprintPolygonMap'],'#c4b4ce');label(xy(b['anchorMap']),'005-'+b['id'])
 for b in placed:polygon(b['footprintPolygonMap'],colors[b['streetId']]);label(xy(b['anchorMap']),b['id'])
 for f in fixtures:
  x,y=xy(f['anchorMap']);dr.ellipse((x-4,y-4,x+4,y+4),fill='#356c49' if f['assetId'].startswith('T') else '#4b515a');label((x+5,y+3),f['assetId'])
 for i,p,a in pois:label(xy(a),'POI preserved')
 dr.rectangle((0,0,W,112),fill='#f6f5f0');svg.append(f'<rect x="0" y="0" width="{W}" height="112" fill="#f6f5f0"/>')
 label((28,22),'REV006 GEOMETRY DRAFT - '+('FIXED PROJECTION / ground only' if iso else 'SOURCE WORLD TOP DOWN'))
 label((28,45),'N1 residential courtyard | N2 commercial/civic | S1 residential/service | purple = read-only revision005')
 label((28,68),'Candidate footprints only. All inside green urban zone. Grey: original buildings/roads. No native calibration / game acceptance.')
 label((28,90),f'Scale {scale:.3f} px/source metre; fixed PNG axes, no sprite rotation. Orientation gaps recorded in JSON.')
 svg.append('</svg>');stem='neighborhood-projected-geometry' if iso else 'neighborhood-world-geometry';(OUT/(stem+'.svg')).write_text('\n'.join(svg));im.save(OUT/(stem+'.png'))
# Final integrity check is source hashes + static data inspection, not game tests.
assert all(sha(x['path'])==x['sha256'] for x in sources)
summary={'buildings':len(placed),'streets':len(streets),'groundSurfaces':len(surfaces),'fixtures':len(fixtures),'buildingRoadMinMetres':min(b['staticClearance']['roadEdgeMetres'] for b in placed),'buildingWaterMinMetres':min(b['staticClearance']['waterMetres'] for b in placed),'buildingToSourceMinMetres':min(b['staticClearance']['sourceBuildingGapMetres'] for b in placed),'allBuildingPairsMinMetres':min(pp(a['footprintPolygonMap'],b['footprintPolygonMap']) for a,b in itertools.combinations(placed,2)),'businessEntranceMinMetres':min(b['staticClearance']['businessEntranceMetres'] for b in placed),'allFootprintsGreen':all(all(inbounds(p,'urban') for p in b['footprintPolygonMap']) for b in placed),'sourceHashReadbackUnchanged':True,'roadSnapshotEqual':True,'orientationGapRoadCount':len(orientationgaps),'fixturePairGroundOverlaps':[x for x in fixturePairs if x['groundGapMetres']==0],'fixturePairMinimumMetres':min([x['groundGapMetres'] for x in fixturePairs]+[9999]),'fixtureFailedCandidateClearance':[f['id'] for f in fixtures if not clear(f['staticClearance'])],'sourceInputs':sources}
write('static-check-report.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
