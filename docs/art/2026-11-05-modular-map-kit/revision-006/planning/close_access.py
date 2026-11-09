#!/usr/bin/env python3
"""Static pedestrian-surface closure; no road graph, source artwork or image transforms."""
import json,math,hashlib,heapq,itertools,html
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
# Reuse exact source geometry functions without running the previous placement/export body.
context=(O/'build_plan.py').read_text().split('# These are design envelopes')[0]
exec(compile(context,str(O/'build_plan.py'),'exec'),globals())
plan=read(O/'backup-entry-before/next-neighborhood-plan.json');baseline=read(O/'backup-entry-before/static-check-report.json')
before=sha(citypath);input_hashes={x['path']:sha(x['path']) for x in plan['sources']}
original=plan['buildings'];retained=[];excluded=[]
# Read full native images before entering these fixed door observations. Fraction is NEVER optimized by routing.
observed={
 'B01':('revision-003/B01-road-aligned-native-v1.png',[973,965],.87,'front door at right end; rooftop door ignored'),
 'B02':('revision-005/native/B02-001/B02-v1.png',[750,970],.53,'ground glass entrance beneath middle recessed bay'),
 'B03':('revision-005/native/B03-001/B03-v1.png',[740,1060],.59,'ground entrance under front canopy'),
 'B04':('revision-005/native/B04-001/B04-v1.png',[775,905],.545,'ground glazed entrance under long canopy'),
 'B05':('revision-005/native/B05-001/B05-v1.png',[810,1070],.584,'single front door and visible step'),
 'B06':('revision-006/native/B06-001/B06-v1.png',[715,1055],.46,'single door in joining bay; front step retained'),
 'B08':('revision-006/native/B08-001/B08-v1.png',[850,790],.378,'leftmost central front stair/door; not a newly invented opening'),
 'B10':('revision-006/native/B10-001/B10-v1.png',[170,960],.20,'visible side personnel door; roller shutter not used as pedestrian door')}
reasons={'B07':'U形楼的门位于内院后墙；旧矩形包络未标定U形内院空腔/台阶，不将正面中点虚当门，暂剔除，待原生U形地基/门位标定。','B09':'曲面展馆入口/台阶与旧矩形包络不能可靠对应；门位/弧形地基未标定，暂剔除，不把弧墙任意一点当入口。','B11':'真实原生已回齐；主卷帘在短向立面，人员门在附属体。旧7×6矩形不能可靠覆盖附属体/短向门接地，不把卷帘或人员门虚构到长边正中；待真实足迹校准后重排。'}
for b in original:
 aid=b['assetId']
 if aid in reasons:
  excluded.append({'id':b['id'],'assetId':aid,'previousAnchorMap':b['anchorMap'],'reason':reasons[aid],'boundedConclusion':'not declared globally impossible; excluded from current accessible subset','previousEntryAudit':b['entryAccessAudit']});continue
 native,pixel,frac,note=observed[aid];path=KIT/native
 assert path.is_file()
 w,d=b['candidateDimensionsMetres']['frontage'],b['candidateDimensionsMetres']['depth']
 local=[-w/2+w*frac,d/2] if aid!='B10' else [-w/2,-d/2+d*frac]
 outward=n if aid!='B10' else mul(u,-1)
 b['previousEntryMap']=b['entryMap'];b['entryMap']=add(add(b['anchorMap'],mul(u,local[0])),mul(n,local[1]))
 b['entryOutwardNormalMap']=outward
 b['entryEvidence']={'nativeSource':str(path),'nativeSHA256':sha(path),'nativeSize':list(Image.open(path).size),'observedDoorGroundPixelApprox':pixel,'doorIdentity':note,'fixedLocalDoorTNMetresCandidate':local,'frontageOrSideEdgeFractionApprox':frac,'precision':'manual visual approximation projected onto candidate ground edge; not precise native registration','doorPixelsEdited':False,'doorOffsetChosenByRouteSearch':False,'anchorMoved':False}
 retained.append(b)
write('references/entry-observations-initial.json',{'status':'manual-native-observation-not-survey','observations':[{'id':b['id'],**b['entryEvidence']} for b in retained],'excluded':excluded})
# A* searches empty ground only. Existing road half-width capsules are obstacles; connection terminates at their outer edge.
RADIUS=.75;MARGIN=.10;STEP=1.;MAX_EXPANSIONS=18000
paths=[];results=[]
def pointPoly(p,poly):return 0 if inside(p,poly) else min(ps(p,a,b) for a,b in edges(poly))
def bbox(poly):return [min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
def boxdist(p,b):return math.hypot(max(b[0]-p[0],0,p[0]-b[2]),max(b[1]-p[1],0,p[1]-b[3]))
source_obstacles=[('source-building',str(i),poly) for i,poly in sourcebuildings]+[('accepted005',str(i),poly) for i,poly in enumerate(locked)]+[('water-area',str(i),poly) for i,poly in enumerate(waterpolys)]
fixture_obstacles=[]
for f in plan['fixtures']:
 poly=f.get('candidateFootprintPolygonMap') or rect(f['anchorMap'],2*f.get('groundRadiusCandidateMetres',.25),2*f.get('groundRadiusCandidateMetres',.25))
 fixture_obstacles.append(('fixture',f['id'],poly))

# Try small anchor translations only when the fixed native-door spur is obstructed.
# The door local coordinate and artwork orientation remain fixed for every attempt.
relocations=[]
def slot_ok(building,anchor):
 w,d=building['candidateDimensionsMetres']['frontage'],building['candidateDimensionsMetres']['depth'];poly=rect(anchor,w,d)
 others=[b['footprintPolygonMap'] for b in retained if b['id']!=building['id']]
 q=checks(poly,locked+others)
 if not clear(q) or not all(inbounds(v,'urban') for v in rect(anchor,w+1,d+1)):return False
 if any(pp(poly,v[2])<.1 for v in fixture_obstacles):return False
 local=building['entryEvidence']['fixedLocalDoorTNMetresCandidate'];entry=add(add(anchor,mul(u,local[0])),mul(n,local[1]));start=add(entry,mul(building['entryOutwardNormalMap'],RADIUS+.3))
 obstacle_polys=[v[2] for v in source_obstacles+fixture_obstacles]+others
 if any(pointPoly(start,p)<RADIUS+MARGIN+.02 for p in obstacle_polys):return False
 if min(ps(start,a,b)-hw for _,_,a,b,hw in roadsegments)<RADIUS+MARGIN+.02:return False
 # Exact butt strip from fixed native threshold, not a centreline-only collision test.
 tangent=[-building['entryOutwardNormalMap'][1],building['entryOutwardNormalMap'][0]]
 strip=[add(entry,mul(tangent,RADIUS)),add(start,mul(tangent,RADIUS)),add(start,mul(tangent,-RADIUS)),add(entry,mul(tangent,-RADIUS))]
 if any(pp(strip,p)<MARGIN for p in obstacle_polys):return False
 if min(pl(strip,a,b)-hw for _,_,a,b,hw in roadsegments)<0:return False
 if any(pointPoly(pos,strip)<6 for _,_,pos in pois):return False
 return True
for building in retained:
 original_anchor=building['anchorMap'][:]
 if slot_ok(building,original_anchor):continue
 choices=sorted([(a,b) for a in [-8,-6,-4,-2,0,2,4,6,8] for b in [-8,-6,-4,-2,0,2,4,6,8] if a or b],key=lambda v:(math.hypot(*v),abs(v[1]),v))
 for du,dn in choices:
  candidate=add(add(original_anchor,mul(u,du)),mul(n,dn))
  if not slot_ok(building,candidate):continue
  building['anchorMap']=candidate;w,d=building['candidateDimensionsMetres']['frontage'],building['candidateDimensionsMetres']['depth'];building['footprintPolygonMap']=rect(candidate,w,d);building['parcelPolygonMap']=rect(candidate,w+1,d+1)
  local=building['entryEvidence']['fixedLocalDoorTNMetresCandidate'];building['entryMap']=add(add(candidate,mul(u,local[0])),mul(n,local[1]))
  building['entryEvidence'].update(anchorMoved=True,anchorTranslationTNMetres=[du,dn],previousAnchorMap=original_anchor)
  building['staticClearance']=checks(building['footprintPolygonMap'],locked+[b['footprintPolygonMap'] for b in retained if b['id']!=building['id']])
  ownroad=roads[building['roadId']];ia,ib=building['roadNodeRangeInclusive'];a,b=[nodes[ownroad['nodes'][i]] for i in [ia,ib]];v=[b[i]-a[i] for i in (0,1)];den=sum(x*x for x in v);t=max(0,min(1,sum((candidate[i]-a[i])*v[i] for i in (0,1))/den));building['roadReferenceMap']=[a[i]+t*v[i] for i in (0,1)];building['candidateSetbackFromOwnRoadEdgeMetres']=pl(building['footprintPolygonMap'],a,b)-ownroad['width']/2
  for sf in plan['groundSurfaces']:
   if sf.get('containsBuildingId')==building['id']:sf['polygonMap']=building['parcelPolygonMap']
  relocations.append({'id':building['id'],'previousAnchorMap':original_anchor,'newAnchorMap':candidate,'translationTNMetres':[du,dn],'doorLocalOffsetUnchanged':True});break

def segmentRect(a,b,r):
 L=math.dist(a,b)
 if L<1e-8:return None
 v=[(b[i]-a[i])/L for i in (0,1)];m=[-v[1],v[0]]
 return [add(a,mul(m,r)),add(b,mul(m,r)),add(b,mul(m,-r)),add(a,mul(m,-r))]
def circle(p,r):return [[p[0]+r*math.cos(2*math.pi*i/16)/math.cos(math.pi/16),p[1]+r*math.sin(2*math.pi*i/16)/math.cos(math.pi/16)] for i in range(16)]
def route_polys(points):return [q for a,b in zip(points,points[1:]) if (q:=segmentRect(a,b,RADIUS))]+[circle(p,RADIUS) for p in points[1:-1]]
for building in retained:
 bid=building['id'];entry=building['entryMap'];out=building['entryOutwardNormalMap'];start=add(entry,mul(out,RADIUS+.3))
 obstacles=source_obstacles+fixture_obstacles+[('new-building',b['id'],b['footprintPolygonMap']) for b in retained]
 boxes=[(kind,oid,poly,bbox(poly)) for kind,oid,poly in obstacles]
 own=building['footprintPolygonMap']
 def polygon_audit(polys,terminal=None):
  mins={'sourceBuildingMetres':9999.,'newBuildingMetres':9999.,'fixtureMetres':9999.,'waterAreaMetres':9999.,'waterLineSafetyMetres':9999.,'roadEdgeMetres':9999.,'businessEntranceMetres':9999.}
  collisions=[]
  for k,poly in enumerate(polys):
   for kind,oid,ob in obstacles:
    d=pp(poly,ob)
    if kind=='new-building' and oid==bid and k==0:
     # Butt end touches this fixed door's own boundary; all vertices are on exterior half-plane.
     if any(sum((v[i]-entry[i])*out[i] for i in (0,1))< -1e-7 for v in poly):collisions.append(['own-door-overlap',oid,k])
     continue
    key='sourceBuildingMetres' if kind in ['source-building','accepted005'] else 'newBuildingMetres' if kind=='new-building' else 'fixtureMetres' if kind=='fixture' else 'waterAreaMetres'
    mins[key]=min(mins[key],d)
    if d<MARGIN-1e-7:collisions.append([kind,oid,k,d])
   for rid,i,a,b,hw in roadsegments:
    d=pl(poly,a,b)-hw;mins['roadEdgeMetres']=min(mins['roadEdgeMetres'],d)
    if d< -1e-7:collisions.append(['road',rid,i,k,d])
   for a,b in waterlines:
    d=pl(poly,a,b)-3;mins['waterLineSafetyMetres']=min(mins['waterLineSafetyMetres'],d)
    if d<3:collisions.append(['water-line-margin',k,d])
   for _,_,p in pois:
    d=pointPoly(p,poly);mins['businessEntranceMetres']=min(mins['businessEntranceMetres'],d)
    if d<6:collisions.append(['business-entrance',k,d])
  return mins,collisions
 def clearance(p):
  for kind,oid,poly,bb in boxes:
   if boxdist(p,bb)<=RADIUS+MARGIN+.02 and pointPoly(p,poly)<RADIUS+MARGIN+.02:return False
  if min(ps(p,a,b)-hw for _,_,a,b,hw in roadsegments)<RADIUS+MARGIN+.02:return False
  if any(ps(p,a,b)<RADIUS+6.02 for a,b in waterlines):return False
  if any(math.dist(p,pos)<6+RADIUS+.02 for _,_,pos in pois):return False
  return inbounds(p,'urban')
 def foot(p,a,b):
  L2=sum((b[i]-a[i])**2 for i in (0,1));t=max(0,min(1,sum((p[i]-a[i])*(b[i]-a[i]) for i in (0,1))/L2)) if L2 else 0
  return [a[i]+t*(b[i]-a[i]) for i in (0,1)],t
 def roadGoal(p):
  ds=[]
  for rid,i,a,b,hw in roadsegments:
   q,t=foot(p,a,b);D=math.dist(p,q);ds.append((D-hw,rid,i,q,hw,t))
  return min(ds)
 def endpoint(p,road):
  _,rid,i,q,hw,t=road;D=math.dist(p,q)
  return add(q,mul([(p[j]-q[j])/D for j in (0,1)],hw+.02))
 def walk_edge(a,b):
  # Capsule skeleton, with slightly conservative radius for 16-gon turn caps.
  rr=RADIUS/math.cos(math.pi/16)+MARGIN
  for kind,oid,poly,bb in boxes:
   if min(a[0],b[0])-rr>bb[2] or max(a[0],b[0])+rr<bb[0] or min(a[1],b[1])-rr>bb[3] or max(a[1],b[1])+rr<bb[1]:continue
   if pl(poly,a,b)<rr:return False
  if any(ss(a,b,c,d)-hw<rr for _,_,c,d,hw in roadsegments):return False
  return True
 # First butt spur audited separately; don't permit the door to migrate to another facade point.
 initial=segmentRect(entry,start,RADIUS);mi,initialbad=polygon_audit([initial])
 cache={};came={};dist={(0,0):0};queue=[(0,0,(0,0))];expanded=0;solution=None
 def pt(k):return [start[0]+STEP*k[0],start[1]+STEP*k[1]]
 if not initialbad and clearance(start):
  while queue and expanded<MAX_EXPANSIONS:
   _,cost,k=heapq.heappop(queue)
   if cost!=dist.get(k):continue
   p=pt(k);expanded+=1;rg=roadGoal(p)
   if RADIUS+.1<=rg[0]<=RADIUS+2.5:
    end=endpoint(p,rg);poly=segmentRect(p,end,RADIUS)
    if poly:
     _,bad=polygon_audit([poly])
     # Audit excludes own-door exception for a distant final leg, recheck own explicitly.
     if not bad and pp(poly,own)>=MARGIN:
      chain=[k]
      while chain[-1] in came:chain.append(came[chain[-1]])
      chain.reverse();points=[entry]+[pt(v) for v in chain]+[end]
      # Greedy simplification requires exact capsule clearance; first door spur remains unchanged.
      smooth=[entry,start];j=1
      while j<len(points)-1:
       far=j+1
       for trial in range(len(points)-2,j,-1):
        if walk_edge(points[j],points[trial]):far=trial;break
       smooth.append(points[far]);j=far
      # Remove duplicate points.
      smooth=[v for i,v in enumerate(smooth) if i==0 or math.dist(v,smooth[i-1])>1e-8]
      psurf=route_polys(smooth);minima,bad=polygon_audit(psurf)
      if not bad:solution=(smooth,psurf,minima,rg);break
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
    nxt=(k[0]+dx,k[1]+dy);v=pt(nxt)
    if math.dist(start,v)>100:continue
    if nxt not in cache:cache[nxt]=clearance(v)
    if not cache[nxt] or not walk_edge(p,v):continue
    nc=cost+math.hypot(dx,dy)*STEP
    if nc+1e-9<dist.get(nxt,math.inf):
     dist[nxt]=nc;came[nxt]=k;heur=max(0,roadGoal(v)[0]-RADIUS)
     heapq.heappush(queue,(nc+heur,nc,nxt))
 if solution:
  points,polys,minima,rg=solution
  path={'id':bid+'-walk','buildingId':bid,'doorStartMap':entry,'centrelineMap':points,'widthMetres':2*RADIUS,'surfacePolygonsMap':polys,'materialId':'S01-paving','purpose':'pedestrian ground paving only; no navigation edges or drivable road','targetRoadId':rg[1],'targetNodeRangeInclusive':[rg[2],rg[2]+1],'targetRoadHalfWidthMetres':rg[4],'targetSegmentParameter':rg[5],'terminalPolygonRoadEdgeGapMetres':minima['roadEdgeMetres'],'staticMinimumClearances':minima,'staticCollisionCount':0,'searchExpandedNodes':expanded,'entryPositionFixedBeforeSearch':True,'routeType':'ground corridor via empty space; may join different existing road shoulder than frontage axis'}
  paths.append(path);building['entryAccessAudit']={'status':'static-native-observation-candidate-connected','blockingCount':0,'pedestrianSurfaceId':path['id'],'targetRoadId':rg[1],'nativeDoorEvidence':building['entryEvidence'],'doorThresholdContactOnly':'own footprint contact at first butt end allowed; no own footprint interior paving','runtimeOrNavigationClaim':False}
  print(bid,'CONNECTED',len(points),'points',expanded,'nodes',flush=True)
 else:
  excluded.append({'id':bid,'assetId':building['assetId'],'previousAnchorMap':building['anchorMap'],'reason':'固定可见门候选点的1.5m步行铺地在本次100m/18000节点静态搜索内未找到满足源楼/新楼/半路宽/树车/水/原业务入口净距的连接；不移动图中门，剔除本候选。','initialSpurCollisions':initialbad,'searchExpandedNodes':expanded,'boundedConclusion':'bounded search failure, not proof no global geometric route exists','entryEvidence':building['entryEvidence']})
  print(bid,'EXCLUDED',expanded,initialbad[:1],flush=True)
kept={p['buildingId'] for p in paths};plan['buildings']=[b for b in retained if b['id'] in kept]
# Drop ground parcels for excluded buildings; retain original shared courts/fixtures as static layout context.
plan['groundSurfaces']=[s for s in plan['groundSurfaces'] if not s.get('containsBuildingId') or s['containsBuildingId'] in kept]
for path in paths:
 for i,poly in enumerate(path['surfacePolygonsMap']):plan['groundSurfaces'].append({'id':path['id']+f'-{i:02d}','type':'pedestrian-paving','materialId':'S01-paving','polygonMap':poly,'pedestrianSurfaceId':path['id'],'navigationEdge':False,'drivable':False})
plan['pedestrianConnections']=paths;plan['excludedCandidates']=excluded
for street in plan['streets']:street['buildingIds']=[b['id'] for b in plan['buildings'] if b['streetId']==street['id']]
plan['entryClosure']={'activeBuildingCount':len(kept),'activeEntryBlockerCount':0,'excludedCount':len(excluded),'originalFiveBlockedIds':[b['id'] for b in original if b.get('entryAccessAudit',{}).get('straightGroundApproachToAssignedRoadSourceBuildingBlockers')],'noDoorOffsetOptimization':True,'allActiveDoorStartsFromNativeVisualObservation':True,'walkWidthMetres':1.5,'obstacleClearanceTargetMetres':MARGIN,'scope':'candidate geometry and hand-estimated native door correspondences; not precise native calibration or game/navigation acceptance','sourceCitySHA256':before,'unchangedSourceInputs':input_hashes,'anchorTranslations':relocations,'searchBounds':'1m grid,100m radius from fixed door,18000 expanded nodes per candidate; conservative existing footprints retained as obstacles','pathsAvoidEvenExcludedFootprintsDuringSearch':True}
# Original five audit IDs must refer to the unmodified archived plan.
archive=read(O/'backup-entry-before/next-neighborhood-plan.json')
plan['entryClosure']['originalFiveBlockedIds']=[b['id'] for b in archive['buildings'] if b['entryAccessAudit']['straightGroundApproachToAssignedRoadSourceBuildingBlockers']]
plan['entryClosure']['originalFiveDisposition']=[{'id':bid,'resolution':'pedestrian surface attached to fixed observed native door' if bid in kept else next(x['reason'] for x in excluded if x['id']==bid)} for bid in plan['entryClosure']['originalFiveBlockedIds']]
for dep in plan['resourceDependencies']:
 aid=dep['assetId']
 if aid.startswith('B') and int(aid[1:])>=6:
  files=list((OUT.parent/'native').glob('**/'+aid+'-runtime-280.png'))
  dep['snapshotRuntimeFiles']=[{'path':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size),'bytes':p.stat().st_size,'within280':max(Image.open(p).size)<=280} for p in files]
  dep['nativeExists']=bool(list((OUT.parent/'native').glob('**/'+aid+'-v1.png')))
  dep['anchorStatus']='native exists; hand-estimated or uncalibrated physical footprint; do not treat old placeholder as measured geometry'
for aid in ['B07','B09','B11']:
 for ex in excluded:
  if ex['assetId']==aid:
   native=list((OUT.parent/'native').glob('**/'+aid+'-v1.png'))
   ex['actualNativeSourceEvidence']=[{'path':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size)} for p in native]
write('references/entry-observations.json',{'status':'manual-native-observation-not-survey','activeObservations':[{'id':b['id'],**b['entryEvidence']} for b in plan['buildings']],'excludedNativeEvidence':excluded})
plan['status']='static-access-subset-candidate-not-runtime-or-user-accepted'
plan['resourcePolicy']['referencedBuildingIds']=sorted({b['assetId'] for b in plan['buildings']})
plan['entryClosure']['orientationGapsPreservedVerbatim']=plan['orientationGaps']==archive['orientationGaps']
assert all(sha(path)==value for path,value in input_hashes.items()) and sha(citypath)==before
write('next-neighborhood-plan.json',plan)
write('entry-access-report.json',{'summary':plan['entryClosure'],'connected':paths,'excluded':excluded})
# Every exported surface is an explicit actual polygon. Draw source context + doors + exact corridors.
colors={'N1':'#69a97f','N2':'#e9ad5e','S1':'#83a6cd'}
for iso in [False,True]:
 def proj(p):
  x,y=p[0]+1610,p[1]-100
  return (x*P['axisX'][0]+y*P['axisY'][0],x*P['axisX'][1]+y*P['axisY'][1]) if iso else (x,-y)
 ext=[proj(v) for b in original for v in b['parcelPolygonMap']];lo=[min(p[i] for p in ext)-20 for i in (0,1)];hi=[max(p[i] for p in ext)+20 for i in (0,1)]
 W,H=(1500,1100) if iso else (1400,1800);sc=min((W-100)/(hi[0]-lo[0]),(H-190)/(hi[1]-lo[1]))
 def xy(p):v=proj(p);return [50+(v[0]-lo[0])*sc,135+(v[1]-lo[1])*sc]
 im=Image.new('RGB',(W,H),'#f6f5f0');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f6f5f0"/>']
 def poly(ps,fill,stroke='#aaaaaa'):
  pts=[xy(v) for v in ps];dr.polygon(pts,fill=fill,outline=stroke);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}"/>')
 def ln(ps,color,width):
  pts=[xy(v) for v in ps];dr.line(pts,fill=color,width=max(1,round(width)));svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"/>')
 def text(pos,txt,color='#222222'):
  x,y=pos;dr.text((x,y),txt,fill=color);svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="12" fill="{color}">{html.escape(txt)}</text>')
 for _,b in sourcebuildings:poly(b,'#e6e4df','#cccccc')
 for b in waterpolys:poly(b,'#b0d8e5')
 for a,b in waterlines:ln([a,b],'#8eb9d4',3*sc)
 for rid,i,a,b,hw in roadsegments:ln([a,b],'#b8b6b0',2*hw*sc)
 for s in plan['groundSurfaces']:
  if s['type']!='pedestrian-paving':poly(s['polygonMap'],'#e2d8c7')
 for b in old['buildings']:poly(b['footprintPolygonMap'],'#c4b4ce')
 for b in original:
  if b['id'] not in kept:
   pts=b['footprintPolygonMap'];poly(pts,'#eee9e6','#c8a49c');ln([pts[0],pts[2]],'#c06b62',2);ln([pts[1],pts[3]],'#c06b62',2)
 for path in paths:
  for v in path['surfacePolygonsMap']:poly(v,'#fff2a6','#a98a2e')
 for b in plan['buildings']:
  poly(b['footprintPolygonMap'],colors[b['streetId']]);text(xy(b['anchorMap']),b['id'])
  x,y=xy(b['entryMap']);dr.ellipse((x-3,y-3,x+3,y+3),fill='#9f283c');svg.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#9f283c"/>')
 for path in paths:
  ln(path['centrelineMap'],'#c27816',1);text(xy(path['centrelineMap'][-1]),'edge')
 for f in plan['fixtures']:
  x,y=xy(f['anchorMap']);dr.ellipse((x-3,y-3,x+3,y+3),fill='#315d40')
 dr.rectangle((0,0,W,115),fill='#f6f5f0');svg.append(f'<rect width="{W}" height="115" fill="#f6f5f0"/>')
 text((25,20),f'REV006 ACCESS GEOMETRY DRAFT | {len(kept)} connected candidates | {len(excluded)} excluded | 0 active entry blockers')
 text((25,42),'Yellow = actual 1.5m pedestrian polygons; red dots = fixed observed door candidates; crossed footprints = excluded')
 text((25,64),'Grey = unchanged original road/building; purple = unchanged revision005; native image pivots/door estimates remain approximate')
 text((25,86),'No new road / navigation edge / POI. Road widths used. Native PNGs never rotated, mirrored or altered.')
 stem='neighborhood-projected-geometry' if iso else 'neighborhood-world-geometry';svg.append('</svg>');(O/(stem+'.svg')).write_text('\n'.join(svg));im.save(O/(stem+'.png'))
summary={**baseline,'buildings':len(kept),'groundSurfaces':len(plan['groundSurfaces']),'entryAccess':plan['entryClosure'],'entryPathsAllCollisionFree':all(p['staticCollisionCount']==0 for p in paths),'entryPathMinSourceBuildingClearanceMetres':min([p['staticMinimumClearances']['sourceBuildingMetres'] for p in paths]+[9999]),'entryPathMinNewBuildingClearanceMetres':min([p['staticMinimumClearances']['newBuildingMetres'] for p in paths]+[9999]),'entryPathMinRoadEdgeMetres':min([p['staticMinimumClearances']['roadEdgeMetres'] for p in paths]+[9999]),'earlierBuildingClearances':'baseline conservative lower bounds; active set is subset with unchanged anchors'}
write('static-check-report.json',summary)
print(json.dumps(plan['entryClosure'],ensure_ascii=False,indent=2))
