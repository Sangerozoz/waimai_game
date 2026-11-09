#!/usr/bin/env python3
"""Admit bounded source clusters, freeze cumulative scene batch; no renderer mutation."""
from pathlib import Path
exec(compile(Path(__file__).with_name('fit_round3.py').read_text().split('rows=[];options=[]')[0],'round3-readonly-setup','exec'),globals())
progress=read(O/'fit-progress.json');rows=progress['testedSources'];options=progress['fitOptions'];combo_trials=[];combo_options=[]
def try_group(ids,parcel,kind):
 srcs=[c['buildings'][i] for i in ids];C=center([v for p in srcs for v in p]);sb=bbox([v for p in srcs for v in p]);reject=Counter();attempts=Counter();others=[(i,p) for i,p,bb in bs if i not in ids and gapbox(sb,bb)<80];rr=[(r,j,a,b) for r,j,a,b,bb in segments if gapbox(sb,bb)<70];ww=[p for p in water if gapbox(sb,bbox(p))<80];ll=[(a,b) for a,b in wl if gapbox(sb,bbox([a,b]))<80]
 outer=max(parcel['rings'],key=lambda p:abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges(p))))
 for aid in ['B06','B05','B02']:
  for scale in [.9,1,1.1]:
   for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
    attempts[f'{aid}@{scale}']+=1;anchor=add(add(C,mul(u,du)),mul(n,dn));poly=footprint(aid,anchor,scale)
    if not all(inbounds(v,'city') and inside(v,outer) for v in poly):reject['blue-or-approved-outer-container']+=1;continue
    if any(pp(poly,p)<2 for i,p in others):reject['unrelated-neighbour-source']+=1;continue
    if any(pp(poly,p)<3 for p in protected_polys):reject['visible69-or-pending5']+=1;continue
    if min([pl(poly,a,b)-r['width']/2 for r,j,a,b in rr]+[9999])<2:reject['source-road-half-width']+=1;continue
    if any(pp(poly,p)<5 for p in ww) or any(pl(poly,a,b)<8 for a,b in ll):reject['water']+=1;continue
    entry=pixelmap(doors[aid],anchor,cal[aid],scale);out=add(entry,mul(n,1.1))
    for r,j,a,b in sorted(rr,key=lambda q:math.dist(entry,foot(entry,q[2],q[3])[0]))[:3]:
     q,t=foot(entry,a,b);D=math.dist(q,entry)
     if D<r['width']/2+2 or D>50:reject['road-shoulder-budget']+=1;continue
     v=[(q[k]-entry[k])/D for k in (0,1)];end=add(q,mul(v,-(r['width']/2+.03)));mid=add(out,mul(u,sum((end[k]-out[k])*u[k] for k in (0,1))))
     for name,pts in [('direct',[entry,end]),('side-L',[entry,out,mid,end])]:
      attempts['approach:'+name]+=1;pts=[p for k,p in enumerate(pts) if k==0 or math.dist(p,pts[k-1])>.001];polys=[strip(a,b) for a,b in zip(pts,pts[1:])]+[rect(p,1.5,1.5) for p in pts[1:-1]]
      if any(any(pp(p,b)<.15 for i,b in others) for p in polys):reject['approach-unrelated-source']+=1;continue
      if any(min(pl(p,a,b)-r['width']/2 for r,j,a,b in rr)<-.001 for p in polys):reject['approach-source-road']+=1;continue
      if any(any(pp(p,b)<3 for b in protected_polys) or not all(inbounds(v,'city') for v in p) for p in polys):reject['approach-protection-or-blue']+=1;continue
      if any(any(pp(p,b)<5 for b in ww) or any(pl(p,a,b)<8 for a,b in ll) for p in polys):reject['approach-water']+=1;continue
      if inside(add(entry,mul(n,.6)),poly) or any(pp(p,poly)<.05 for p in polys[1:]):reject['actual-door-own-body']+=1;continue
      first=strip(add(entry,mul([(pts[1][k]-entry[k])/math.dist(entry,pts[1]) for k in (0,1)],.6)),pts[1])
      if first is None or pp(first,poly)<.05:reject['actual-door-own-body']+=1;continue
      result={'sourceIndex':ids[0],'sourceIndices':ids,'clusterStrategy':kind,'clusterParcel':{'id':parcel['id'],'landUse':parcel['landUse'],'outerRingMap':outer,'scope':'approved outer container including declared source-building holes; design reorganisation, not historical building-type proof'},'stratum':strata(ids[0]),'assetId':aid,'anchorMap':anchor,'uniformScale':scale,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':doors[aid],'approach':{'roadId':r['id'],'segmentIndex':j,'routeTemplate':name,'centrelineMap':pts,'polygonsMap':polys},'score':D}
      combo_trials.append({'sourceIndices':ids,'strategy':kind,'parcelId':parcel['id'],'attempts':dict(attempts),'rejectedByRule':dict(reject),'result':'feasible-design-cluster'});return result
 combo_trials.append({'sourceIndices':ids,'strategy':kind,'parcelId':parcel['id'],'attempts':dict(attempts),'rejectedByRule':dict(reject),'result':'bounded-cluster-fit-failed'});return None
# Enclosing approved outer rings are actual geometric evidence; nearby names alone never grant exemption.
workids={r['sourceIndex'] for r in rows};members={}
for i in workids:
 src=c['buildings'][i];C=center(src)
 if area(src)>250:continue
 if any(math.dist(C,p[2])<15 for p in pois):continue # precaution for nearby stop context, NOT proof node is a door
 for parcel,bb in parcelmeta:
  if parcel['landUse']not in ['residential','mixed']:continue
  if not(bb[0]<=C[0]<=bb[2] and bb[1]<=C[1]<=bb[3]):continue
  outer=max(parcel['rings'],key=lambda p:abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges(p))))
  if all(inside(v,outer) for v in src):members.setdefault(parcel['id'],(parcel,[]))[1].append(i);break
for parcel,ids in list(members.values()):
 for a,b in itertools.combinations(sorted(ids),2):
  if len(combo_trials)>=20:break
  if math.dist(center(c['buildings'][a]),center(c['buildings'][b]))>25:continue
  result=try_group([a,b],parcel,'many-source-to-one-household-or-mixed-courtyard')
  if result:combo_options.append(result)
 if len(combo_trials)>=20:break
# Large source multi-module attempts need enclosing approved same-use geometry; absent evidence is a separate semantic deferral.
large_reviews=[]
for r in rows:
 if r['areaSquareMetres']<400:continue
 src=c['buildings'][r['sourceIndex']];containers=[]
 for p,bb in parcelmeta:
  if p['landUse']not in ['residential','mixed'] or gapbox(bbox(src),bb)>0:continue
  outer=max(p['rings'],key=lambda q:area(q))
  if all(inside(v,outer) for v in src):containers.append(p['id'])
 large_reviews.append({'sourceIndex':r['sourceIndex'],'strategy':'one-source-to-multiple-modules','enclosingSameUseParcels':containers,'decision':'deferred-original-functional-evidence' if not containers else 'eligible-for-later-bounded-module-placement','reason':'no automatic house substitution for unknown factory/compound; source area ratio diagnostic only','countAsRendered':0})
write('combination-evidence.json',{'manyToOneActualTrials':combo_trials,'enclosingParcelMembershipSourceCount':sum(len(v[1]) for v in members.values()),'largeCarrierReviews':large_reviews,'businessSemantics':'no source business binding exists in schema; nearby stop proximity only adds precaution; no node moved','noSingleSpritePerSourceRequirement':True})
pool=combo_options+options
for x in pool:x.setdefault('sourceIndices',[x['sourceIndex']])
# Prefer a geographically continuous connected component. It remains a partial district, not a whole county filled template.
points={i:center(c['buildings'][i]) for x in pool for i in x['sourceIndices']};rem=set(points);components=[]
while rem:
 stack=[rem.pop()];comp=[]
 while stack:
  i=stack.pop();comp.append(i);near=[j for j in rem if math.dist(points[i],points[j])<180];rem.difference_update(near);stack.extend(near)
 components.append(comp)
component=max(components,key=len);eligible=[x for x in pool if set(x['sourceIndices'])<=set(component)];eligible.sort(key=lambda x:(len(x['sourceIndices'])==1,x['stratum']['centerMap'][1],x['score']))
accepted=[];assigned=set();joint=[];uses=Counter()
for idx in sorted(component,key=lambda i:(center(c['buildings'][i])[1],i)):
 if idx in assigned or len(assigned)>=20:continue
 choices=[x for x in eligible if idx in x['sourceIndices'] and not set(x['sourceIndices'])&assigned and len(assigned)+len(x['sourceIndices'])<=20]
 choices.sort(key=lambda x:(len(x['sourceIndices'])==1,uses[x['assetId']],x['score']))
 for x in choices:
  if any(pp(x['footprintPolygonMap'],a['footprintPolygonMap'])<2 or any(pp(p,a['footprintPolygonMap'])<.15 for p in x['approach']['polygonsMap']) or any(pp(p,x['footprintPolygonMap'])<.15 for p in a['approach']['polygonsMap']) for a in accepted):joint.append({'sourceIndices':x['sourceIndices'],'rule':'joint-new-body-or-corridor','asset':x['assetId']});continue
  r=next(r for r in c['roads'] if r['id']==x['approach']['roadId']);j=x['approach']['segmentIndex']
  if not all(inbounds(nodes[v],'city') for v in r['nodes'][j:j+2]):joint.append({'sourceIndices':x['sourceIndices'],'rule':'source-segment-endpoints-outside-blue;no-route-expansion'});continue
  accepted.append(x);assigned.update(x['sourceIndices']);uses[x['assetId']]+=1;break
buildings=[];ground=[];mappings=[];roadids=set()
for seq,x in enumerate(accepted):
 ids=x['sourceIndices'];aid=x['assetId'];sc=x['uniformScale'];pid='009r3-src-'+'-'.join(f'{i:04d}' for i in ids);ap=x['approach'];roadids.add(ap['roadId']);meta=x['stratum']
 buildings.append({'id':pid,'persistentId':pid,'libraryAssetId':aid,'assetId':aid,'anchorMap':x['anchorMap'],'uniformScale':sc,'anchorUV':assets[aid]['anchorUV'],'worldSizeUnits':[v*sc for v in assets[aid]['worldSizeUnits']],'rotation':0,'footprintPolygonMap':x['footprintPolygonMap'],'entryMap':x['entryMap'],'entryPixel':x['entryPixel'],'visualDoorPixel':x['entryPixel'],'visualDoorWorld':x['entryMap'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndices':ids,'sourcePolygonsMap':[c['buildings'][i] for i in ids],'sourceSHA256':sha(oldseed['source']['cityPath']),'sourceDataChanged':False},'clusterOfSource':{'sourceIndices':ids,'visualModuleIds':[pid],'strategy':x.get('clusterStrategy','single-source-design-replacement-with-yard'),'uniqueSourceCount':len(ids),'countAsRendered':0},'landUseIntent':meta['landUseIntent'],'approvedCompoundParcel':x.get('clusterParcel'),'sceneRole':'residential garden compound' if aid in ['B05','B06'] else 'small mixed street frontage','navigationStopNodeId':meta['nearestOriginalStop']['nodeId'],'navigationStopOriginalWorld':meta['nearestOriginalStop']['anchorMap'],'stopAssociation':'design proximity only, not original building binding; no node/route change','visualApproach':ap,'status':'assigned-static-comparison-not-rendered'})
 mappings.append({'sourceIndices':ids,'scenePersistentIds':[pid],'actualNativeOccupiedArea':area(x['footprintPolygonMap']),'rawSourceAreaSum':sum(area(c['buildings'][i]) for i in ids),'coverageMeaning':'design reorganisation with residual yard, not equal-shape surveying or a rendered source-completion count','remainingSpaceUse':'maintained garden/courtyard base only where exact source/road/water/protection clearance permits'})
 for j,p in enumerate(ap['polygonsMap']):ground.append({'id':pid+f'-walk-{j}','materialId':'S01-paving','polygonMap':p,'purpose':'1.5m unchanged native door to original road shoulder; no navigation edge','owner':pid})
 # The full source-carrier ground is purpose-assigned when legal, rather than only a rear cosmetic strip.
 for idx in ids:
  p=c['buildings'][idx];ground.append({'id':pid+f'-carrier-court-{idx}','materialId':'neutral-grass' if aid in ['B05','B06'] else 'S01-paving','color':'#a5bb8c','polygonMap':p,'purpose':'residential tended yard and doorway court' if aid in ['B05','B06'] else 'mixed frontage courtyard','owner':pid,'sourceCarrierIndices':ids})
 # Candidate-specific native envelope side gardens; exact shapes and widths differ by source and native mass.
 anchor=x['anchorMap'];l=[[sum((p[k]-anchor[k])*u[k] for k in (0,1)),sum((p[k]-anchor[k])*n[k] for k in (0,1))] for p in x['footprintPolygonMap']];s0,s1=min(v[0] for v in l),max(v[0] for v in l);t0,t1=min(v[1] for v in l),max(v[1] for v in l)
 for j,(a,t,b,v) in enumerate([(s0,t0-1.5,s1,t0),(s0-1,t0,s0,t1),(s1,t0,s1+1,t1)]):
  poly=[add(add(anchor,mul(u,s)),mul(n,q)) for s,q in [(a,t),(b,t),(b,v),(a,v)]];ground.append({'id':pid+f'-planted-edge-{j}','materialId':'neutral-grass','color':'#9fb584','polygonMap':poly,'purpose':'ground planted edge; no roof trees or forest diversity claim','owner':pid,'sourceCarrierIndices':ids})
# Full readback for bodies and every surface. Only its declared original carrier set is exempt.
proof=[];safe=[]
def audit(poly,exempt,owner=None):
 pb=bbox(poly);srcgap=min([pp(poly,p) for i,p,bb in bs if i not in exempt and gapbox(pb,bb)<80]+[9999]);rg=min([pl(poly,a,b)-r['width']/2 for r,j,a,b,bb in segments if gapbox(pb,bb)<80]+[9999]);wg=min([pp(poly,p) for p in water if gapbox(pb,bbox(p))<80]+[pl(poly,a,b)-3 for a,b in wl if gapbox(pb,bbox([a,b]))<80]+[9999]);pg=min(pp(poly,p) for p in protected_polys);ng=min([pp(poly,b['footprintPolygonMap']) for b in buildings if b['id']!=owner]+[9999]);blue=all(inbounds(v,'city') for v in poly)
 return {'sourceOtherMetres':srcgap,'roadEdgeMetres':rg,'waterSafetyMetres':wg,'visible69Pending5ProtectionMetres':pg,'otherNewBodyMetres':ng,'allVerticesBlue':blue}
for b in buildings:
 q=audit(b['footprintPolygonMap'],b['clusterOfSource']['sourceIndices'],b['id']);assert q['sourceOtherMetres']>=2 and q['roadEdgeMetres']>=2 and q['waterSafetyMetres']>=5 and q['visible69Pending5ProtectionMetres']>=3 and q['otherNewBodyMetres']>=2 and q['allVerticesBlue'];proof.append({'id':b['id'],'kind':'body','clearance':q})
for s in ground:
 b=next(b for b in buildings if b['id']==s['owner']);q=audit(s['polygonMap'],b['clusterOfSource']['sourceIndices'],b['id']);good=q['sourceOtherMetres']>=.1 and q['roadEdgeMetres']>=-.001 and q['waterSafetyMetres']>=5 and q['visible69Pending5ProtectionMetres']>=3 and q['otherNewBodyMetres']>=.1 and q['allVerticesBlue']
 if not good:
  if '-walk-' in s['id']:raise AssertionError((s['id'],q))
  joint.append({'sourceIndices':b['clusterOfSource']['sourceIndices'],'rule':'optional-court-or-garden-rejected','surfaceId':s['id'],'clearance':q});continue
 s['staticClearance']=q;safe.append(s);proof.append({'id':s['id'],'kind':'ground','clearance':q})
ground=safe
# All visible candidate plots connect through the existing blue-inner directed source graph. No graph changes.
from collections import deque
adj={}
for r in c['roads']:
 for a,b in zip(r['nodes'],r['nodes'][1:]):
  if not inbounds(nodes[a],'city') or not inbounds(nodes[b],'city'):continue
  if r['direction']>=0:adj.setdefault(a,[]).append((b,r['id']))
  if r['direction']<=0:adj.setdefault(b,[]).append((a,r['id']))
anchors=[]
for b in buildings:
 ap=b['visualApproach'];r=next(r for r in c['roads'] if r['id']==ap['roadId']);anchors.append(r['nodes'][ap['segmentIndex']])
def bfs(a,b):
 todo=deque([a]);prev={a:None}
 while todo:
  x=todo.popleft()
  if x==b:break
  for y,rid in adj.get(x,[]):
   if y not in prev:prev[y]=(x,rid);todo.append(y)
 if b not in prev:return None
 seq=[b];rs=[]
 while seq[-1]!=a:x,rid=prev[seq[-1]];seq.append(x);rs.append(rid)
 return {'nodeIds':seq[::-1],'roadIdsPerEdge':rs[::-1]}
topology=[{'toPersistentId':b['id'],'forward':bfs(anchors[0],a),'return':bfs(a,anchors[0])} for b,a in zip(buildings,anchors)];assert all(x['forward'] and x['return'] for x in topology)
for t in topology:roadids.update(t['forward']['roadIdsPerEdge']);roadids.update(t['return']['roadIdsPerEdge'])
roads=[{**r,'sourceNodeIds':r['nodes'],'nodes':[nodes[i] for i in r['nodes']]} for r in c['roads'] if r['id']in roadids]
batch={'schemaVersion':1,'version':'009-fit-round3-v1','status':'static-instantiable-district-candidate-not-rendered-or-user-accepted','projection':P,'roads':roads,'buildings':buildings,'fixtures':[],'groundSurfaces':ground,'parkingSpaces':[],'parkedVehicles':[],'sourceMappings':mappings,'sourceIndices':sorted(assigned),'uniqueSourceCount':len(assigned),'visualModuleCount':len(buildings),'districtOrganization':{'candidateConnectedComponentSize':len(component),'sourceNeighbourLinkThresholdMetres':180,'meaning':'partial source lots along existing connected blue-inner road graph; unassigned intervening raw targets remain explicitly unrendered; not whole-district completion','perPlotContent':'actual fixed native door, 1.5m path, source-carrier court where safe and individual planted edges; no whole-street template replication'},'originalTopology':topology,'protection':{'visible69ScenePath':str(visibleFile),'visible69SceneSHA256':sha(visibleFile),'neighborhoodTMJSHA256':sha(tmjFile),'visibleStaticCount':69,'visibleGroundCount':135,'pendingSecondBatchPath':str(secondFile),'pendingSecondSHA256':sha(secondFile),'pendingSources':[b['visualReplacementOf']['sourceIndex'] for b in second['buildings']],'pendingStatus':'reserved-not-assumed-rendered'},'sources':{'city':oldseed['source'],'semantics':str(K/'revision-009/source-entry-semantics.md')},'resourcePolicy':{'onlyExistingPNGs':True,'maxRuntimeEdge':280,'sharedImageFramePerFileSHA':True,'nativeMastersExcluded':True,'existingBaselinesUnchanged':True,'newNativeDirectionsRequired':False,'T02':'natural tree without pit; not multi-species forest completion','T01':'tree-pit tree'},'uncertainty':'manual native ground/doorstep, source function absent where not explicitly typed; design scenic reorganisation/stop association not original business binding; threshold levels need rendering comparison'}
write('third-expansion-batch.json',batch);write('source-combination-map.json',{'sourceMappings':mappings,'uniqueSourceCount':len(assigned),'moduleCount':len(buildings),'sourceDeduplicated':True,'renderedCount':0});write('topology-clearance-evidence.json',{'proof':proof,'topology':topology,'noNewRoadEdges':True})
write('batch-manifest.json',{'path':str(O/'third-expansion-batch.json'),'sha256':sha(O/'third-expansion-batch.json'),'uniqueSources':len(assigned),'modules':len(buildings),'grounds':len(ground)})
newscreen=set(r['sourceIndex'] for r in rows)-set(rechecks);assert len(newscreen)==200
summary={'baselineBlueTotal':1008,'baselineAllSourceTotal':3524,'previousAssignedUniqueSources':9,'newAssignedUniqueSources':len(assigned),'newAssignedFromPrior8Rechecks':len(set(rechecks)&assigned),'newAssignedFromPreviouslyUntested':len(assigned-set(rechecks)),'stillUnassignedBlue':1008-9-len(assigned),'previousUntested':579,'newUniqueSourcesGeometricallyScreened':len(newscreen),'remainingUntested':579-len(newscreen),'recheckedOldFitOptionSourceIds':rechecks,'priorJointReasonsPreserved':prev['jointAdmissionDecisions'],'newJointAdmissionEvidence':joint,'sourceRows':rows,'perAttemptRejectedByRule':dict(sum((Counter(r['rejectedByRule']) for r in rows),Counter())),'uniqueSourceRulesTriggered':dict(sum((Counter(set(r['rejectedByRule'])) for r in rows),Counter())),'largeCompositeContextOnly':large_reviews,'manyToOneTrialCount':len(combo_trials),'manyToOneFitOptionCount':len(combo_options),'countsDoNotEqualRendered':True,'budget':{'newSources':200,'priorOptionRechecks':8,'combinationTrialsMax':20,'assetScales':[.9,1,1.1],'earlySuccessLeavesLaterScalesUntested':True},'minimalResourceNeeds':{'newNativeProvenNecessary':False,'Top2':[],'reason':'current batch fits existing files; no production request from bounded failures alone'}}
write('fit-summary.json',summary);assert all(sha(f)==h for f,h in protected.items());print('BATCH FROZEN',len(assigned),len(buildings),len(ground),sha(O/'third-expansion-batch.json'),flush=True)
