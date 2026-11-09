#!/usr/bin/env python3
"""Source-carrier visual replacement screening + cumulative county coverage. Static data only."""
import ast,json,math,hashlib,itertools,html
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;K=O.parent.parent;ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):(O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
cf=ROOT/'delivery-game/assets/resources/map-sample/city.json';zf=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';lf=ROOT/'docs/art/2026-11-03-county-expansion/county-scene-layout.json';I=K/'revision-006/integration';sf=K/'revision-006/viewer/assets/scene-layout.json'
c=read(cf);z=read(zf);legacy=read(lf);scene=read(sf);assert len(scene['blocks'])==57 and len(scene['groundSurfaces'])==115;assert legacy['sourceSHA256']==sha(cf)
lib=read(I/'asset-library.json');assets={a['id']:a for a in lib['assets']};cal={a['id']:a for a in read(I/'asset-calibration.json')['assets']};review=read(K/'revision-008/calibration/footprint-review.json');P=lib['projection'];u=review['localAxes']['T'];n=review['localAxes']['N']
names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),'<pure-geometry>','exec'))
files=[cf,zf,lf,sf,I/'asset-library.json',I/'asset-calibration.json',I/'neighborhood.tmj',K/'revision-008/calibration/footprint-review.json',K/'revision-007/review/prop-admission.json',ROOT/'docs/product/implementation-baseline.md']
protected={str(f):sha(f) for f in files};write('protected-inputs.json',protected)
nodes={p['id']:[p['x'],p['y']] for p in c['nodes']};assert all(set(['nodes','width','direction'])<=set(r) and all(i in nodes for i in r['nodes']) for r in c['roads'])
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def center(p):return [sum(v[i] for v in p)/len(p) for i in (0,1)]
def ringarea(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges(p)))/2
bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings']) if len(p)>=3];wa=[a['points'] for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3];wl=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:])];segments=[(r,i,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for i,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node') in nodes]
protectpolys=[]
for region in scene['groundRegions']:
 b=region['bounds'];protectpolys.append([[b['minX']-5,b['minY']-5],[b['maxX']+5,b['minY']-5],[b['maxX']+5,b['maxY']+5],[b['minX']-5,b['maxY']+5]])
# Actual raw-pixel contours at unchanged PPU; no nominal rectangles for placement.
def pixelmap(px,anchor,co):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));sx,sy=[(px[i]-ap[i])/ppu for i in (0,1)];a,b=P['axisX'],P['axisY'];dt=a[0]*b[1]-a[1]*b[0];return add(anchor,[(sx*b[1]-sy*b[0])/dt,(a[0]*sy-a[1]*sx)/dt])
doors={'B01':[973,965],'B02':[750,970],'B03':[740,1060],'B04':[775,905],'B05':[810,1070],'B06':cal['B06']['entryPixel'],'B08':cal['B08']['entryPixel']}
def footprint(aid,anchor):
 co=cal[aid];raw=co.get('occupiedGroundOutlinePixel') or co.get('groundCornersPixelLeftFrontRightRear') or [[198,910],[438,1229],[1055,931],[815,612]];return [pixelmap(v,anchor,co) for v in raw]
def strip(a,b,w=1.5):
 L=math.dist(a,b);t=[(b[i]-a[i])/L for i in (0,1)];v=[-t[1],t[0]];return [add(a,mul(v,w/2)),add(b,mul(v,w/2)),add(b,mul(v,-w/2)),add(a,mul(v,-w/2))]
def roadfoot(p,a,b):
 v=[b[i]-a[i] for i in (0,1)];den=sum(q*q for q in v);t=max(0,min(1,sum((p[i]-a[i])*v[i] for i in (0,1))/den)) if den else 0;return [a[i]+t*v[i] for i in (0,1)],t
screening=[];options=[]
# Broad but contiguous urban corridor around existing county centre, excluding protected three regions.
for idx,src,sb in bs:
 C=center(src)
 if not all(inbounds(p,'city') for p in src) or not(-1960<C[0]<-1390 and -520<C[1]<430):continue
 if any(pp(src,p)<8 for p in protectpolys):continue
 nearroads=[(r,i,a,b) for r,i,a,b,bb in segments if boxgap(sb,bb)<70]
 others=[(j,p) for j,p,bb in bs if j!=idx and boxgap(sb,bb)<80];waters=[p for p in wa if boxgap(sb,bbox(p))<80];lines=[(a,b) for a,b in wl if boxgap(sb,bbox([a,b]))<80]
 business=[(i,p,pos) for i,p,pos in pois if inside(pos,src) or min(ps(pos,a,b) for a,b in edges(src))<8]
 row={'sourceIndex':idx,'sourceId':f'city.buildings[{idx}]','businessPOIIndices':[x[0] for x in business],'testedNativeAssets':list(doors),'status':'deferred','reason':'no unchanged-scale native footprint + positive-front door corridor fit in bounded anchor search'}
 if business:
  row['reason']='business carrier examined first: entrance node mapping must be retained; direct native door-to-business-node fit not yet established; no displacement of original entrance'
  screening.append(row);continue
 found=[]
 for aid in doors:
  for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3),(-6,0),(6,0),(0,-6),(0,6)]:
   anchor=add(add(C,mul(u,du)),mul(n,dn));poly=footprint(aid,anchor);pb=bbox(poly)
   if not all(inbounds(p,'city') for p in poly) or not inside(C,poly):continue
   if any(pp(poly,p)<2.5 for j,p in others) or any(pp(poly,p)<8 for p in protectpolys):continue
   if min([pl(poly,a,b)-r['width']/2 for r,i,a,b in nearroads]+[9999])<2:continue
   if any(pp(poly,p)<5 for p in waters) or any(pl(poly,a,b)<8 for a,b in lines):continue
   if any((inside(pos,poly) or min(ps(pos,a,b) for a,b in edges(poly))<6) for i,p,pos in pois):continue
   entry=pixelmap(doors[aid],anchor,cal[aid]);choices=[]
   for r,i,a,b in nearroads:
    foot,t=roadfoot(entry,a,b);D=math.dist(entry,foot)
    if D<r['width']/2+2 or D>40:continue
    direction=[(foot[k]-entry[k])/D for k in (0,1)]
    if sum(direction[k]*n[k] for k in (0,1))<.9:continue
    v=[b[k]-a[k] for k in (0,1)];sv=[v[0]*P['axisX'][k]+v[1]*P['axisY'][k] for k in (0,1)];angle=math.degrees(math.atan2(sv[1],sv[0]));diff=(angle+28.486362688849802+90)%180-90
    if abs(diff)>5:continue
    end=add(foot,mul(direction,-(r['width']/2+.03)));walk=strip(entry,end)
    if any(pp(walk,p)<.2 for j,p in others) or any(pp(walk,p)<8 for p in protectpolys):continue
    if min(pl(walk,a,b)-rr['width']/2 for rr,j,a,b in nearroads)<-.001:continue
    if any(pp(walk,p)<5 for p in waters) or any(pl(walk,a,b)<8 for a,b in lines):continue
    if not all(inbounds(v,'city') for v in walk):continue
    # Do not allow approach to pass through the body: first native doorstep contact only, <=25px manual rim uncertainty.
    if inside(add(entry,mul(direction,.6)),poly):continue
    choices.append((D,abs(diff),r,i,angle,diff,walk,end))
   if choices:
    D,dd,r,i,angle,diff,walk,end=min(choices,key=lambda x:x[:2]);found.append({'sourceIndex':idx,'sourcePolygonMap':src,'assetId':aid,'anchorMap':anchor,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':doors[aid],'walkPolygonMap':walk,'walkEndMap':end,'roadId':r['id'],'segmentIndex':i,'roadScreenAngleDeg':angle,'roadDifferenceDeg':diff,'zone':zone(anchor),'carrierOverlapMeaning':'visual replacement of this exact source index only; source data and POIs unchanged','score':D+math.hypot(du,dn)+dd*2})
 if found:
  row.update(status='feasible-candidate',reason='actual native polygon clears other source buildings and source road/water; own raw carrier exempt; fixed door pixels approach positive-front existing road')
  options.extend(found)
 screening.append(row)
write('source-carrier-screening.json',{'status':'bounded-static-screen-not-global-impossibility','businessCarrierPolicy':'checked before non-business assignment; no original POI/node moved; unresolved mapping deferred','screened':screening,'feasibleOptions':len(options)})
print('OPTIONS',len(options),'SOURCE CARRIERS',sum(x['status']=='feasible-candidate' for x in screening),flush=True)
write('placement-options.json',options)
# Stable seed batch: actual consecutive source-road spans, not six invented block labels.
chosen=[];dropped=[]
for idx,preferred in [(630,'B08'),(631,'B03'),(616,'B06'),(633,'B05'),(634,'B02'),(617,'B04'),(635,'B01')]:
 opt=[x for x in options if x['sourceIndex']==idx];opt.sort(key=lambda x:(x['assetId']!=preferred,x['score']))
 selected=None
 for x in opt:
  poly=x['footprintPolygonMap'];walk=x['walkPolygonMap'];ratio=ringarea(poly)/ringarea(x['sourcePolygonMap'])
  if not .4<ratio<2.5:continue
  if any(pp(poly,b['footprintPolygonMap'])<2.5 or pp(walk,b['footprintPolygonMap'])<.15 or pp(poly,b['walkPolygonMap'])<.15 for b in chosen):continue
  selected=x;break
 if selected:chosen.append(selected)
 else:dropped.append({'sourceIndex':idx,'reason':'new actual footprint/corridor conflicts with earlier retained new contour, or native/source area ratio outside0.4..2.5; no forced placement'})
assert chosen
# Local grounds from actual contours with declared uses. Perimeter gardens are small safe strips, not a whole-county grass blanket.
ground=[];buildings=[];blocks={};roads_needed=set();parcelLinks={}
for x in chosen:
 aid=x['assetId'];idx=x['sourceIndex'];bid=f'009-src-{idx:04d}';anchor=x['anchorMap'];poly=x['footprintPolygonMap'];pb=bbox(poly)
 nearparcels=sorted([(min(pp(poly,ring) for ring in p['rings']),p) for p in legacy['parcels'] if p.get('rings')],key=lambda v:v[0]);intent=nearparcels[0][1];parcelLinks[idx]=intent['id']
 blockid=f'009-{x["roadId"]}-span-{x["segmentIndex"]:02d}'
 block=blocks.setdefault(blockid,{'id':blockid,'sourceRoadId':x['roadId'],'nodeIndexRangeInclusive':[x['segmentIndex'],x['segmentIndex']+1],'buildingIds':[],'legacyParcelIntents':[],'functionalOrganization':[],'status':'static-seed-subset-not-runtime'})
 block['buildingIds'].append(bid);block['legacyParcelIntents'].append({'id':intent['id'],'landUse':intent['landUse'],'name':intent.get('name'),'areaSquareMetresApprox':intent.get('areaSquareMetresApprox'),'geometrySourceSHA256':sha(lf),'use':'geometry/function context only, not legacy low-fidelity building module'});block['functionalOrganization'].append({'B08':'local covered market and pedestrian entry','B06':'low-rise residence with private garden','B05':'small residence with doorstep and pocket planting','B04':'community facility forecourt','B03':'small vertical office/commercial frontage','B02':'office/service frontage','B01':'small street shop'}[aid])
 b={'id':bid,'persistentId':bid,'libraryAssetId':aid,'assetId':aid,'anchorMap':anchor,'uniformScale':1,'rotation':0,'anchorUV':assets[aid]['anchorUV'],'worldSizeUnits':assets[aid]['worldSizeUnits'],'footprintPolygonMap':poly,'entryMap':x['entryMap'],'entryPixel':x['entryPixel'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndex':idx,'sourceId':f'city.buildings[{idx}]','sourcePolygonMap':x['sourcePolygonMap'],'sourceSHA256':sha(cf),'sourceDataRemoved':False,'visualPolicy':'suppress only this raw source polygon visual in future renderer when replacement accepted; all other raw source targets remain explicitly deferred','candidateToSourceAreaRatio':ringarea(poly)/ringarea(x['sourcePolygonMap'])},'originalBusinessEntrances':[],'businessNodeMapping':'non-business source carrier; no POI attached within8m; no new POI','blockId':blockid,'legacyParcelId':intent['id'],'doorApproach':{'polygonMap':x['walkPolygonMap'],'endMap':x['walkEndMap'],'widthMetres':1.5,'targetRoadId':x['roadId'],'targetNodeRangeInclusive':[x['segmentIndex'],x['segmentIndex']+1],'doorPixelsFixed':True,'manualOwnThresholdUncertainty':'first native step/contact may touch manual ground rim; first0.6m must be outside body; not precise doorway level certification'},'roadAngleDifferenceDeg':x['roadDifferenceDeg'],'sourceNativeSHA256':assets[aid].get('sourceNativeSHA256'),'zone':x['zone'],'status':'assigned-static-seed-not-yet-displayed'}
 buildings.append(b);roads_needed.add(x['roadId'])
 ground.append({'id':bid+'-walk','materialId':'S01-paving','polygonMap':x['walkPolygonMap'],'purpose':'continuous1.5m fixed native door-to-original-road pedestrian connection','blockId':blockid})
 # Small complete pocket ground attached to building rear/side; evaluate against every other source building and road.
 localcoords=[[sum((v[k]-anchor[k])*u[k] for k in (0,1)),sum((v[k]-anchor[k])*n[k] for k in (0,1))] for v in poly];umin,umax=min(v[0] for v in localcoords),max(v[0] for v in localcoords);nmin,nmax=min(v[1] for v in localcoords),max(v[1] for v in localcoords)
 gardens=[]
 for localbox in [[umin,nmin-2,umax,nmin],[umin-1,nmin,umin,nmax],[umax,nmin,umax+1,nmax]]:
  a,t,d,v=localbox;gp=[add(add(anchor,mul(u,s)),mul(n,q)) for s,q in [(a,t),(d,t),(d,v),(a,v)]];gb=bbox(gp)
  if not all(inbounds(p,'city') for p in gp):continue
  if any(pp(gp,p)<.1 for j,p,bb in bs if j!=idx and boxgap(gb,bb)<5):continue
  if any(pl(gp,a,b)-r['width']/2<.1 for r,i,a,b,bb in segments if boxgap(gb,bb)<r['width']/2+5):continue
  if any(pp(gp,b['footprintPolygonMap'])<.1 for b in buildings if b['id']!=bid):continue
  if any(pp(gp,p)<5 for p in wa if boxgap(gb,bbox(p))<10):continue
  gardens.append(gp)
 for j,gp in enumerate(gardens):ground.append({'id':bid+f'-garden-{j}','materialId':'neutral-grass','color':'#9db486','polygonMap':gp,'purpose':'maintained residential garden' if aid in ['B05','B06'] else 'facility or shop planted edge','blockId':blockid})
 b['groundOrganization']={'doorConnection':bid+'-walk','pocketGardenSurfaceIds':[bid+f'-garden-{j}' for j in range(len(gardens))],'remainingOriginalLand':'legacy parcel geometry retained as deferred contextual ground; no claim complete rendering of parcel'}
# Protect all other new footprints/walks from every exported pocket garden. Unsafe ones omitted, never force.
safe=[]
for s in ground:
 if '-garden-' in s['id']:
  owner=s['id'].split('-garden-')[0]
  if any(pp(s['polygonMap'],b['footprintPolygonMap'])<.1 or pp(s['polygonMap'],b['doorApproach']['polygonMap'])<.1 for b in buildings if b['id']!=owner):continue
 safe.append(s)
ground=safe
roadrows=[{**r,'nodes':[nodes[i] for i in r['nodes']],'sourceNodeIds':r['nodes']} for r in c['roads'] if r['id']in roads_needed]
# Actual contiguous source node spans and source-side access chain preserved.
blocklist=list(blocks.values());blocklist.sort(key=lambda b:b['nodeIndexRangeInclusive'][0]);assert len(roadrows)==1
for a,b in zip(blocklist,blocklist[1:]):assert a['nodeIndexRangeInclusive'][1]==b['nodeIndexRangeInclusive'][0]
batch={'schemaVersion':1,'version':'009-first-expansion-seed-v1','status':'static-instantiable-seed-not-runtime-or-user-accepted','projection':P,'roads':roadrows,'buildings':buildings,'fixtures':[],'groundSurfaces':ground,'parkingSpaces':[],'parkedVehicles':[],'blocks':blocklist,'source':{'cityPath':str(cf),'citySHA256':sha(cf),'approvedCountyLayoutPath':str(lf),'approvedCountyLayoutSHA256':sha(lf),'reuse':'original parcels/land-use context only; no old extruded geometry/textures'},'protectedExisting':{'scenePath':str(sf),'sceneSHA256':sha(sf),'staticInstances':57,'groundSurfaces':115,'allExistingCameraViews':scene['cameraViews'],'regionProtectionPolygonsMap':protectpolys},'scope':{'targetFutureBlocks':[6,12],'currentFeasibleSeedBlocks':len(blocklist),'currentBuildings':len(buildings),'reasonBelowTarget':'only three consecutive node spans qualified in northern corridor; additional west/south disconnected candidates deferred, not re-labelled as contiguous blocks','stillDeferred':'suburban transition and more complete block coverage; this seed does not claim full county or full original parcel rendering'},'resourcePolicy':{'allowedAssetIds':sorted({b['assetId'] for b in buildings}),'runtimeMaxEdge':280,'sharedImageFrameByFileSHA':True,'nativeMastersExcluded':True,'B09B10B11':'hold','T03':'no new placement','P09':'not placed'},'droppedSeedCandidates':dropped,'staticEvidence':'source-carrier-screening.json','uncertainty':'actual native hand-estimated pixel controls/door levels; first native step contact uncertainty remains; no runtime render certification'}
write('first-expansion-batch.json',batch)
write('seed-manifest.json',{'version':batch['version'],'path':str(O/'first-expansion-batch.json'),'sha256':sha(O/'first-expansion-batch.json'),'blocks':len(blocklist),'buildings':len(buildings),'groundSurfaces':len(ground),'protectedInputs':protected})
print('SEED READY',len(blocklist),len(buildings),sha(O/'first-expansion-batch.json'),flush=True)
