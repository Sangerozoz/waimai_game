#!/usr/bin/env python3
"""Static original-coordinate site search. Writes only revision008/planning."""
import ast,json,math,hashlib,itertools,html
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;K=O.parent.parent;ROOT=next(x for x in O.parents if (x/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d):(O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Read-only shared elementary segment/polygon math; never import executable legacy planners.
tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'}
exec(compile(ast.Module(body=[t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name in names],type_ignores=[]),'<read-only-geometry-functions>','exec'))
cityfile=ROOT/'delivery-game/assets/resources/map-sample/city.json';zonefile=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';c=read(cityfile);z=read(zonefile);g=read(K/'revision-003/road-constraint.json');u=g['streetTangentMap'];n=[-u[1],u[0]];P=g['projection']
I=K/'revision-006/integration';sceneFile=K/'revision-006/viewer/assets/scene-layout.json';scene=read(sceneFile);assert len(scene['blocks'])==43 and len(scene['groundSurfaces'])==85
inputfiles=[cityfile,zonefile,K/'revision-003/road-constraint.json',I/'asset-library.json',I/'asset-calibration.json',I/'prop-calibration.json',I/'prop-corners-calibration.json',I/'REPORT.md',I/'REPORT-rest-corner.md',I/'neighborhood.tmj',sceneFile,K/'revision-007/review/prop-admission.json']
protected={str(f):sha(f) for f in inputfiles};write('protected-inputs.json',protected)
nodes={v['id']:[v['x'],v['y']] for v in c['nodes']};assert all(all(i in nodes for i in r['nodes']) for r in c['roads'])
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def overlap(a,b,pad=0):return not(a[2]+pad<b[0] or a[0]-pad>b[2] or a[3]+pad<b[1] or a[1]-pad>b[3])
segments=[(r,i,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for i,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))]
bs=[(i,b,bbox(b)) for i,b in enumerate(c['buildings']) if len(b)>=3];ws=[(i,a['points'],bbox(a['points'])) for i,a in enumerate(c['areas']) if a.get('kind')=='water' and len(a.get('points',[]))>=3];wl=[(i,a,b,bbox([a,b])) for i,w in enumerate(c['waterways']) for a,b in zip(w,w[1:])];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node') in nodes]
protpts=[p['anchorMap'] for p in scene['blocks']]+[v for s in scene['groundSurfaces'] for v in s['polygonMap']];protb=bbox(protpts);protectpoly=[[protb[0]-15,protb[1]-15],[protb[2]+15,protb[1]-15],[protb[2]+15,protb[3]+15],[protb[0]-15,protb[3]+15]]
# Search whole blue-minus-green. Facing along fixed u; no world-axis surrogate for street tangent.
candidates=[];roadcount=0
for r,i,a,b,bb in segments:
 L=math.dist(a,b)
 if L<40 or r.get('bridge'):continue
 t=[(b[k]-a[k])/L for k in (0,1)];sv=[t[0]*P['axisX'][j]+t[1]*P['axisY'][j] for j in (0,1)];angle=math.degrees(math.atan2(sv[1],sv[0]));delta=(angle-g['groundEdgeAnglesScreenDeg']['frontage']+90)%180-90
 if abs(delta)>5:continue
 roadcount+=1
 for f in [.25,.5,.75]:
  ref=add(a,mul(t,L*f));anchor=add(ref,mul(n,-(r['width']/2+24)))
  poly=rect(anchor,58,40);pb=bbox(poly)
  if not all(inbounds(v,'city') for v in poly) or any(inbounds(v,'urban') for v in poly) or pp(poly,protectpoly)<30:continue
  buildings=[(j,p) for j,p,bx in bs if overlap(pb,bx,3)]
  hits=[j for j,p in buildings if pp(poly,p)<2]
  roads=[(rr,j,p,q) for rr,j,p,q,bx in segments if overlap(pb,bx,rr['width']/2+3)]
  rg=min([pl(poly,p,q)-rr['width']/2 for rr,j,p,q in roads]+[9999])
  water=min([pp(poly,p) for j,p,bx in ws if overlap(pb,bx,15)]+[pl(poly,a,b)-3 for j,a,b,bx in wl if overlap(pb,bx,15)]+[9999])
  if rg<1 or water<8:continue
  if any(inside(pos,poly) or min(ps(pos,a,b) for a,b in edges(poly))<10 for _,_,pos in pois):continue
  candidates.append({'roadId':r['id'],'segmentIndex':i,'nodeIds':r['nodes'][i:i+2],'tangentMap':t,'roadScreenAngle':angle,'assetAngleDifferenceDeg':delta,'referenceMap':ref,'anchorMap':anchor,'polygonMap':poly,'width':r['width'],'direction':r['direction'],'sourceBuildingIntersections':hits,'roadEdgeGapMetres':rg,'waterSafetyGapMetres':water,'distanceToProtectedSampleMetres':pp(poly,protectpoly),'zone':'suburb','score':len(hits)*1000+abs(delta)*10+math.dist(anchor,[-1590,75])/100})
candidates.sort(key=lambda v:v['score']);unique=[]
for ca in candidates:
 if all(math.dist(ca['anchorMap'],v['anchorMap'])>80 for v in unique):unique.append(ca)
 if len(unique)==4:break
write('site-candidates.json',{'screenedSameFamilyRoadSegmentCount':roadcount,'eligibleSiteSamples':len(candidates),'rankedDistinctSites':unique,'policy':'58x40m entire blue-minus-green site, road edge>=1m, water margin>=8m, actual source building conflicts counted; no replacements assumed without further evidence'})
print('SITES',[(x['roadId'],x['segmentIndex'],x['anchorMap'],x['sourceBuildingIntersections']) for x in unique],flush=True)
if not unique:raise SystemExit('No compliant site found; inspect site-candidates.json')
site=unique[0];C=site['anchorMap'];S=site['polygonMap'];SB=bbox(S)
lib=read(I/'asset-library.json');assets={a['id']:a for a in lib['assets']};cal={a['id']:a for a in read(I/'asset-calibration.json')['assets']};pc={a['id']:a for a in read(I/'prop-corners-calibration.json')['assets']}
def at(s,t):return add(add(C,mul(u,s)),mul(n,t))
def local(p):q=[p[i]-C[i] for i in (0,1)];return [sum(q[i]*u[i] for i in (0,1)),sum(q[i]*n[i] for i in (0,1))]
def rectangle(s0,t0,s1,t1):return [at(s0,t0),at(s1,t0),at(s1,t1),at(s0,t1)]
def pixelmap(px,anchor,co):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));sx,sy=[(px[i]-ap[i])/ppu for i in (0,1)];a,b=P['axisX'],P['axisY'];det=a[0]*b[1]-a[1]*b[0];return add(anchor,[(sx*b[1]-sy*b[0])/det,(a[0]*sy-a[1]*sx)/det])
def actual(aid,anchor):
 co=cal.get(aid,pc.get(aid));pts=co.get('occupiedGroundOutlinePixel') or co.get('groundCornersPixelLeftFrontRightRear') or co.get('groundContactPixelsManual');return [pixelmap(v,anchor,co) for v in pts]
nearsegments=[(r,i,a,b) for r,i,a,b,bb in segments if overlap(SB,bb,r['width']/2+100)]
nearbuildings=[(i,b) for i,b,bb in bs if overlap(SB,bb,100)];nearwater=[(i,b) for i,b,bb in ws if overlap(SB,bb,100)];nearwaterlines=[(i,a,b) for i,a,b,bb in wl if overlap(SB,bb,100)]
def nearest_building(poly):
 pb=bbox(poly)
 def lower(bb):return math.hypot(max(bb[0]-pb[2],pb[0]-bb[2],0),max(bb[1]-pb[3],pb[1]-bb[3],0))
 best=math.inf;index=None
 for gap,i,b in sorted((lower(bb),i,b) for i,b,bb in bs):
  if gap>best:break
  v=pp(poly,b)
  if v<best:best,index=v,i
 return best,index
def static(poly):
 return {'roadEdgeMetres':min([pl(poly,a,b)-r['width']/2 for r,i,a,b in nearsegments]+[9999]),'sourceBuildingMetres':nearest_building(poly)[0],'nearestSourceBuildingIndex':nearest_building(poly)[1],'waterSafetyMetres':min([pp(poly,b) for i,b in nearwater]+[pl(poly,a,b)-3 for i,a,b in nearwaterlines]+[9999]),'protectedSampleMetres':pp(poly,protectpoly),'allVerticesBlue':all(inbounds(v,'city') for v in poly),'allVerticesOutsideGreen':all(not inbounds(v,'urban') for v in poly),'businessEntranceMetres':min([0 if inside(pos,poly) else min(ps(pos,a,b) for a,b in edges(poly)) for _,_,pos in pois]+[9999])}
buildings=[]
for aid,s,t,door in [('B05',-20,0,[810,1070]),('B06',-5,0,cal['B06']['entryPixel']),('B08',16,1,cal['B08']['entryPixel'])]:
 anchor=at(s,t);poly=actual(aid,anchor);entry=pixelmap(door,anchor,cal[aid]);q=static(poly);assert q['roadEdgeMetres']>2 and q['sourceBuildingMetres']>2 and q['waterSafetyMetres']>8
 buildings.append({'id':'008-'+aid,'persistentId':'008-'+aid,'assetId':aid,'libraryAssetId':aid,'anchorMap':anchor,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':door,'entryEvidence':'006 read-only actual native pixel -> original PPU/anchor -> world; B05 retained door estimate810,1070','worldSizeUnits':assets[aid]['worldSizeUnits'],'anchorUV':assets[aid]['anchorUV'],'uniformScale':1,'rotation':0,'visualReplacementOf':None,'zone':'suburb','staticClearance':q,'status':'core-static-ground-plan-native-manual-calibration','groundControlUncertainty':'hand-estimated ground controls; hidden rear inferred; not precision registration'})
for a,b in itertools.combinations(buildings,2):assert pp(a['footprintPolygonMap'],b['footprintPolygonMap'])>3
# Complete grounds: a continuous meadow base, meaningful garden and service-yard zones, door aprons and foot paths.
ground=[{'id':'008-site-lawn','materialId':'neutral-grass','color':'#9fb986','polygonMap':S,'purpose':'continuous tended courtyard ground, no unplanned bare gaps'}, {'id':'008-garden-zone','materialId':'neutral-soil','color':'#9b8261','polygonMap':rectangle(-27,-19,2,-10),'purpose':'small household vegetable garden with walking aisles; no commercial farm/POI'}, {'id':'008-service-yard','materialId':'S01-paving','polygonMap':rectangle(5,-19,27,-8),'purpose':'market rear logistics courtyard and static parking; no drivable navigation connection'}]
walks=[]
def strip(a,b,w=1.5):
 L=math.dist(a,b);t=[(b[i]-a[i])/L for i in (0,1)];v=[-t[1],t[0]];return [add(a,mul(v,w/2)),add(b,mul(v,w/2)),add(b,mul(v,-w/2)),add(a,mul(v,-w/2))]
def walk(pid,pts,owner=None):
 polys=[strip(a,b) for a,b in zip(pts,pts[1:]) if math.dist(a,b)>.001]
 # Square turn joints explicitly included and checked, not invisible centreline-only connections.
 polys += [rect(v,1.5,1.5) for v in pts[1:-1]]
 result=[]
 for j,poly in enumerate(polys):
  q=static(poly);assert q['roadEdgeMetres']>=-.03 and q['sourceBuildingMetres']>1 and q['waterSafetyMetres']>8
  hits=[]
  for b in buildings:
   gap=pp(poly,b['footprintPolygonMap'])
   if gap<.1:
    if owner==b['id'] and j==0:
     # Native front contact can be slightly inside the manually inferred rim. Explicitly bounded exception.
     startlocal=local(pts[0]);outside=add(pts[0],mul(n,.6));assert not inside(outside,b['footprintPolygonMap'])
     # Measure the inferred rim overlap along outward n at the two threshold corners.
     outline=[local(v) for v in b['footprintPolygonMap']];entry_s,entry_t=local(pts[0]);front=[]
     for sample_s in [entry_s-.75,entry_s,entry_s+.75]:
      vals=[]
      for aa,bb in edges(outline):
       if min(aa[0],bb[0])-1e-9<=sample_s<=max(aa[0],bb[0])+1e-9 and abs(bb[0]-aa[0])>1e-9:vals.append(aa[1]+(sample_s-aa[0])/(bb[0]-aa[0])*(bb[1]-aa[1]))
      if vals:front.append(max(vals))
     penetration=max(0,max(front)-entry_t) if front else 0
     co=cal[b['assetId']];ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));screen_n=[n[0]*P['axisX'][k]+n[1]*P['axisY'][k] for k in (0,1)];pixel_depth=penetration*math.hypot(*screen_n)*ppu
     assert pixel_depth<=25,(pid,'door rim uncertainty exceeded',pixel_depth)
     hits.append({'ownDoorThresholdOnly':True,'inferredRimOverlapDepthMetres':penetration,'equivalentNativePixels':pixel_depth,'declaredGroundControlUncertaintyPixels':25,'noDoorPixelsMoved':True,'interpretation':'doorstep/contact within manual ground-control uncertainty; requires integration visual check, not proven walk through wall'})
    else:raise AssertionError((pid,'building collision',b['id'],j,gap))
  result.append({'polygonMap':poly,'staticClearance':q,'doorThresholdException':hits})
  ground.append({'id':pid+f'-{j}','materialId':'S01-paving','polygonMap':poly,'purpose':'pedestrian ground only','ownerBuildingId':owner})
 walks.append({'id':pid,'ownerBuildingId':owner,'centrelineMap':pts,'widthMetres':1.5,'surfaces':result,'navigationEdgesAdded':0})
for b in buildings:
 e=b['entryMap'];s,t=local(e);walk(b['id']+'-door',[e,at(s,15)],b['id'])
walk('008-common-front',[at(-27,15),at(27,15)])
# Join existing road side exactly at its source half-width, on the same fixed-ground family.
r=next(r for r in c['roads'] if r['id']==site['roadId']);ia=site['segmentIndex'];aa,bb=[nodes[r['nodes'][j]] for j in [ia,ia+1]]
start=at(0,15);v=[bb[j]-aa[j] for j in (0,1)];den=sum(x*x for x in v);tt=max(0,min(1,sum((start[j]-aa[j])*v[j] for j in (0,1))/den));q=[aa[j]+tt*v[j] for j in (0,1)];dn=math.dist(start,q);end=add(q,mul([(start[j]-q[j])/dn for j in (0,1)],r['width']/2+.02));walk('008-road-shoulder-link',[start,end])
walk('008-garden-side-aisle',[at(-27,15),at(-27,-8),at(1,-8)])
walk('008-garden-soil-link',[at(-24,-8),at(-24,-11),at(0,-11)])
walk('008-service-side-aisle',[at(27,15),at(27,-8),at(6,-8)])
fixtures=[]
for j,s in enumerate([-21,-14,-7]):
 anchor=at(s,-15);poly=actual('P08',anchor);fixtures.append({'id':f'008-bed-{j}','persistentId':f'008-bed-{j}','assetId':'P08','libraryAssetId':'P08','anchorMap':anchor,'footprintPolygonMap':poly,'worldSizeUnits':assets['P08']['worldSizeUnits'],'anchorUV':assets['P08']['anchorUV'],'status':'garden-context-static-candidate','uniformScale':1})
for aid,s,t in [('P06',-23,-18),('P07',-25,-16)]:
 anchor=at(s,t);co=pc[aid];ends=actual(aid,anchor);poly=strip(*ends,w=.18);fixtures.append({'id':'008-'+aid,'persistentId':'008-'+aid,'assetId':aid,'libraryAssetId':aid,'anchorMap':anchor,'footprintPolygonMap':poly,'worldSizeUnits':assets[aid]['worldSizeUnits'],'anchorUV':assets[aid]['anchorUV'],'actualGroundSpanMetres':co['candidateGroundSpanFromHeightScale'],'role':'one isolated short garden marker; not closed/seamless standard fence','uniformScale':1})
for j,(s,t) in enumerate([(-12,8),(7,8),(-25,-5),(2,-18)]):
 anchor=at(s,t);fixtures.append({'id':f'008-tree-{j}','persistentId':f'008-tree-{j}','assetId':'T02','libraryAssetId':'T02','anchorMap':anchor,'footprintPolygonMap':rect(anchor,1.2,1.2),'canopyEnvelopeCandidateRadiusMetres':1.6,'worldSizeUnits':assets['T02']['worldSizeUnits'],'anchorUV':assets['T02']['anchorUV'],'role':'courtyard/garden shade; ground-root envelope candidate','uniformScale':1})
slot=rectangle(11,-17,19,-13);center=at(15,-15);body=rect(center,5.8,2.05);vananchor=add(center,mul(n,2.05/2));parking=[{'id':'008-service-van-slot','polygonMap':slot,'dimensionsCandidateMetres':[8,4],'purpose':'static market logistics only; no vehicle navigation/driveway claim'}];vehicles=[{'id':'008-service-V02','persistentId':'008-service-V02','libraryAssetId':'V02-v2','assetId':'V02-v2','anchorMap':vananchor,'anchorMeaning':'near-side visible wheel-contact midpoint, center +n*1.025; NOT vehicle body centre','candidateBodyPolygonMap':body,'candidateDimensionsLengthWidthHeight':[5.8,2.05,2.7],'parkingSpaceId':parking[0]['id'],'worldSizeUnits':assets['V02-v2']['worldSizeUnits'],'anchorUV':assets['V02-v2']['anchorUV'],'uniformScale':1,'role':'parked decoration only; no AI/delivery/catalogue changes'}]
assert all(inside(v,slot) for v in body)
objects=[(b['id'],b['footprintPolygonMap']) for b in buildings]+[(f['id'],f['footprintPolygonMap']) for f in fixtures]+[(vehicles[0]['id'],body)]
pairs=[]
for (aid,a),(bid,b) in itertools.combinations(objects,2):
 d=pp(a,b);assert d>.1,(aid,bid,d);pairs.append({'ids':[aid,bid],'gapMetres':d})
for f in fixtures+vehicles:
 poly=f.get('footprintPolygonMap',f.get('candidateBodyPolygonMap'));q=static(poly);assert q['sourceBuildingMetres']>2 and q['roadEdgeMetres']>2 and q['waterSafetyMetres']>8
 f['staticClearance']=q
 gaps=[pp(poly,sf['polygonMap']) for w in walks for sf in w['surfaces']];assert min(gaps)>.1,(f['id'],'walk gap',min(gaps));f['walkGapMetres']=min(gaps)
# Directed graph connectivity only through original node pairs with both endpoints blue; no new edges.
from collections import deque
adj={}
for rr in c['roads']:
 for a,b in zip(rr['nodes'],rr['nodes'][1:]):
  if not inbounds(nodes[a],'city') or not inbounds(nodes[b],'city'):continue
  if rr['direction']>=0:adj.setdefault(a,[]).append((b,rr['id']))
  if rr['direction']<=0:adj.setdefault(b,[]).append((a,rr['id']))
startnode=r['nodes'][ia];target='1623821577'
def bfs(a,b):
 todo=deque([a]);prev={a:None}
 while todo:
  x=todo.popleft()
  if x==b:break
  for y,rid in adj.get(x,[]):
   if y not in prev:prev[y]=(x,rid);todo.append(y)
 if b not in prev:return None
 seq=[b];rids=[]
 while seq[-1]!=a:
  x,rid=prev[seq[-1]];seq.append(x);rids.append(rid)
 return {'nodeIds':seq[::-1],'roadIdsPerEdge':rids[::-1],'lengthMetres':sum(math.dist(nodes[a],nodes[b]) for a,b in zip(seq,seq[1:]))}
connection={'startSourceNodeId':startnode,'protectedSampleSourceNodeId':target,'forward':bfs(startnode,target),'return':bfs(target,startnode),'rule':'only existing road node pairs, source direction0 bidirectional/+1 forward/-1 reverse; blue rectangle convex, both endpoints blue => complete straight segment blue'}
assert connection['forward'] and connection['return']
roadids=set(connection['forward']['roadIdsPerEdge']+connection['return']['roadIdsPerEdge']+[site['roadId']]);selectedroads=[{**rr,'nodes':[nodes[i] for i in rr['nodes']],'sourceNodeIds':rr['nodes']} for rr in c['roads'] if rr['id']in roadids]
for rr in selectedroads:
 original=next(v for v in c['roads'] if v['id']==rr['id']);assert rr['sourceNodeIds']==original['nodes'] and rr['nodes']==[nodes[i] for i in original['nodes']]
# No source replacement needed: explicitly document alternatives and why not use them today.
reserved={'id':'008-wide-hold-reserve','site':unique[1],'status':'alternative unoccupied site for future irregular-footprint fitting, NOT active ground/ready assets','heldAssets':['B07','B09','B11'],'reason':'do not read concurrent revision008/calibration; no guessed boxes/doors; reserve58x40 site only, fit after actual outline/courtyard/short-side door review'}
plan={'schemaVersion':1,'version':'008-suburb-v1','status':'static-feasible-core-candidate-not-runtime-or-user-accepted','projection':P,'roads':selectedroads,'buildings':buildings,'fixtures':fixtures,'groundSurfaces':ground,'parkingSpaces':parking,'parkedVehicles':vehicles,'sourceCity':{'path':str(cityfile),'sha256':sha(cityfile),'schemaConfirmed':{'nodes':'id/x/y','roads':'id/nodes ordered IDs/width/direction','buildings':'indexed raw polygon arrays; no original per-building ID field','pois':'name/node/kind'}},'zoning':{'path':str(zonefile),'sha256':sha(zonefile),'regions':z['regions'],'registration':z['registration'],'selectedZone':'blue city inside / green urban outside = suburb','approximateNotSurveyed':True},'selectedSite':site,'siteCandidatesFile':'site-candidates.json','protected006':{'scenePath':str(sceneFile),'sceneSHA256':sha(sceneFile),'instances':43,'groundSurfaces':85,'expandedProtectionPolygonMap':protectpoly,'allOriginalInstancesAndGroundUnchanged':True},'coreResources':sorted({o.get('assetId') for o in buildings+fixtures+vehicles}),'resourcePolicy':{'runtimeMaxEdge':280,'sharedTexturePerAssetId':True,'nativeMastersNotPackaged':True,'onlyExistingResources':True,'P04':'v2 only; not used','P09':'comparison-only excluded','P06P07':'different actual short spans, independent sections, no standard closed loop','P02':'excluded; no fuel by houses/table/garden'},'dependencies':[reserved],'originalRoadConnection':connection,'orientation':{'assetFrontageScreenDeg':g['groundEdgeAnglesScreenDeg']['frontage'],'assetDepthScreenDeg':g['groundEdgeAnglesScreenDeg']['depth'],'actualRoadScreenDeg':site['roadScreenAngle'],'differenceDegModulo180':site['assetAngleDifferenceDeg'],'PNGTransform':'none; world translation only, scale1','minimumNewNativeDirectionsRequiredForCore':0,'sideRoadGaps':'no new building faces other roads; no blanket27-direction production request'},'checks':{'pairMinMetres':min(x['gapMetres'] for x in pairs),'pairs':pairs,'sourceBuildingIntersections':0,'visualReplacementCount':0,'sourceReplacementPolicy':'source indices can be visual carriers if business/geometry evidence supports; empty sites found, so no replacement required or assumed','nativeGroundControls':'actual hand-estimated pixel outlines/PPU, not nominal dimension boxes; contact uncertainty remains','sourceDataChanged':False,'newPOIs':0,'newNavigationEdges':0,'newDrivableRoads':0},'cameraSuggestions':{'focusMap':C,'projectionId':P['id'],'overviewWidthUnits':95,'overviewHeightUnits':85,'note':'same-map next increment, camera centre suggestion only; no browser or renderer executed'}}
plan['pedestrianConnections']=walks
plan['selectedSite']['actualEnvelopeStaticClearance']=static(S)
plan['sourceAreaContext']=[{'sourceAreaIndex':i,'kind':a.get('kind'),'sourceArrayUnchanged':True} for i,a in enumerate(c['areas']) if len(a.get('points',[]))>=3 and inside(C,a['points'])]
plan['resourceDependencies']=[]
for aid in plan['coreResources']:
 a=assets[aid];f=I/'assets'/a['file'];assert f.is_file() and sha(f)==a['sha256'] and max(Image.open(f).size)<=280
 plan['resourceDependencies'].append({'assetId':aid,'path':str(f),'sha256':sha(f),'runtimeSize':list(Image.open(f).size),'bytes':f.stat().st_size,'worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'calibrationSource':str(I/('prop-corners-calibration.json' if aid.startswith('P') else 'asset-calibration.json')),'imageFrameSharingKey':a['sha256']})
plan['checks']['walkSourceBuildingMinMetres']=min(sf['staticClearance']['sourceBuildingMetres'] for w in walks for sf in w['surfaces'])
plan['checks']['walkDoorThresholdExceptions']=[{'walkId':w['id'],'surfaceIndex':i,'detail':sf['doorThresholdException']} for w in walks for i,sf in enumerate(w['surfaces']) if sf['doorThresholdException']]
write('next-district-plan.json',plan)
write('source-local-context.json',{'sourceSHA256':sha(cityfile),'roads':[{**rr,'nodes':[nodes[i] for i in rr['nodes']],'sourceNodeIds':rr['nodes']} for rr in c['roads'] if any(rr['id']==r['id'] for r,i,a,b in nearsegments)],'sourceBuildings':[{'sourceId':f'city.buildings[{i}]','sourceIndex':i,'polygonMap':b} for i,b in nearbuildings],'waterAreas':[{'sourceIndex':i,'polygonMap':b} for i,b in nearwater],'waterLines':[{'sourceIndex':i,'segmentMap':[a,b]} for i,a,b in nearwaterlines],'businessEntrances':[{'sourceIndex':i,'poi':p,'anchorMap':pos} for i,p,pos in pois if math.dist(pos,C)<200]})
# Exact fixed-ground projection diagram; explicitly not a game screenshot.
W,H=1500,1100;scale=12
project=lambda p:[(p[0]-C[0])*P['axisX'][j]+(p[1]-C[1])*P['axisY'][j] for j in (0,1)]
def xy(p):q=project(p);return [750+q[0]*scale,550+q[1]*scale]
im=Image.new('RGB',(W,H),'#f5f4ed');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f5f4ed"/>']
def drawpoly(p,fill,stroke='#888888'):
 pts=[xy(v) for v in p];dr.polygon(pts,fill=fill,outline=stroke);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}"/>')
def line(a,b,color,width):
 pts=[xy(a),xy(b)];dr.line(pts,fill=color,width=max(1,round(width)));svg.append(f'<line x1="{pts[0][0]}" y1="{pts[0][1]}" x2="{pts[1][0]}" y2="{pts[1][1]}" stroke="{color}" stroke-width="{width}"/>')
def label(p,txt):
 x,y=p;dr.text((x,y),txt,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="14">{html.escape(txt)}</text>')
for i,b in nearbuildings:drawpoly(b,'#e4e0da','#c5c0b9')
for i,b in nearwater:drawpoly(b,'#a8cbdc')
for r,i,a,b in nearsegments:line(a,b,'#aeaba4',r['width']*scale)
for sf in ground:drawpoly(sf['polygonMap'],sf.get('color','#e2d6b9'))
for b in buildings:drawpoly(b['footprintPolygonMap'],'#c98d61' if b['assetId']=='B08' else '#88aa78');label(xy(b['anchorMap']),b['assetId']);x,y=xy(b['entryMap']);dr.ellipse((x-4,y-4,x+4,y+4),fill='red')
for f in fixtures:drawpoly(f['footprintPolygonMap'],'#527955' if f['assetId']=='T02' else '#946e4a');label(xy(f['anchorMap']),f['assetId'])
drawpoly(slot,'#bbb7ab');drawpoly(body,'#8e9faf');label(xy(vananchor),'V02 5.8x2.05 / wheel anchor')
label(xy(at(-15,-11)),'HOUSEHOLD GARDEN');label(xy(at(15,-10)),'MARKET SERVICE YARD');label(xy(end),'SOURCE ROAD EDGE')
dr.rectangle((0,0,W,110),fill='#f5f4ed');svg.append(f'<rect width="{W}" height="110" fill="#f5f4ed"/>');label([24,22],'REV008 SUBURBAN COURTYARD - STATIC GEOMETRY DRAFT / NOT GAME RENDER');label([24,46],f'Blue inside / green outside. Source road {site["roadId"]} nodes {ia}..{ia+1}; fixed native orientation; no sprite transforms.');label([24,70],'Actual manual native footprints, fixed door pixels; lawns / private gardens / market logistics split; held B07 B09 B11 not placed.');svg.append('</svg>');(O/'district-projected.svg').write_text('\n'.join(svg));im.save(O/'district-projected.png')
assert all(sha(f)==h for f,h in protected.items())
report=f'''# 008郊区宽院落：静态可行核心

稳定输入/输出：next-district-plan.json。首选源路{site['roadId']}第{ia}段，中心{C}；58×40m，完整蓝内绿外，源楼零交叠，现有43实例/85地面保护区距离{site['distanceToProtectedSampleMetres']:.1f}m。原road/node顺序/宽/方向、原楼、水、业务入口均只读。候选筛查见site-candidates.json：先用真实原坐标找宽空地，再按006手估原生足迹/门像素落位，不按7×6小盒子硬塞。所有源建筑是原数组索引，无虚构OSM楼ID；本次空地足够，visualReplacementOf均null，没有原址替换或删源楼。

核心三栋：B05、B06住宅＋B08小市场；三菜畦P08、P06/P07各一独立短段、四株T02，后勤V02一辆。统一比例1及原生图机位，住宅菜园与市场后勤以实际地面分区；整块草坪基底＋菜园土面＋后勤铺地＋1.5m门前/侧院/路肩步行连接，非孤立小瓷砖。V02保持5.8×2.05车身，8×4停车槽；anchor是近侧轮接地中点=center+n×1.025，未缩车。停车不新增可行车通道/交通AI/导航边。P06约1.475m、P07约0.838m，各自短段，不作无缝闭环。P04只认v2但此次不用，P09比较hold、P02油箱不放住宅/桌旁。

真实道路投影{site['roadScreenAngle']:.3f}°，与资产frontage模180差{site['assetAngleDifferenceDeg']:+.3f}°；现有族直接用，核心新朝向需求0。从原节点{startnode}到样板节点{target}已按原方向做蓝内去/回连通核对，原有节点链与道路ID逐边保留。只证明源图静态连通，未新增导航边/POI，未跑游戏。原完整相关道路保留，不裁节点迁就场景。

静态检查含源半路宽/水/源楼/新足迹/道具/步行面，实例间最小净距{plan['checks']['pairMinMetres']:.3f}m。原生角点、门位和隐蔽后角均为006手估，精密标定未解决；门起点只由真实像素/PPU转换，不搜索改门偏移。B06/B08首段门槛与手估地脚边界有轻微交叠，逐项量化为等效原生像素并限制在25px地脚控制误差内，明确列doorThresholdException；不是其他楼/源楼穿透，也不称精密门槛认证；别楼/源楼/道路均严格检查。实际公差结果见主JSON。

第二个58×40m备选空地保留供B07/U院、B09/壳顶、B11/短向门及更宽体量后续匹配：未读或等待revision008/calibration在写资料，不先标ready，不画矩形替身。当前核心不依赖这三项。若其真实足迹需更宽/侧向进院，必须另核，不强塞。原生长边/短边残差保持，不旋转PNG。

只写revision008/planning。脚本plan_district.py已实际执行；输出JSON/本报告/投影SVG与PNG均为几何规划，不称运行、用户验收或整县完成。未生图/浏览器/服务器/游戏tests/typecheck/回归/存档/提交。来源与保护SHA见protected-inputs.json，执行末逐项保持。资源按assetId共享既有≤280图；原生母版不进包。
'''
(O/'REPORT.md').write_text(report)
write('delivery-manifest.json',{'status':plan['status'],'files':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in [O/'next-district-plan.json',O/'district-projected.png',O/'REPORT.md',O/'plan_district.py']],'sourceProtectionUnchanged':True})
print('DONE',sha(O/'next-district-plan.json'),len(buildings),len(fixtures),len(ground),connection['forward']['lengthMetres'],flush=True)
