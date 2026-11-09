#!/usr/bin/env python3
"""Bounded second source-fit round. Writes this directory only; old planning never executed."""
import ast,json,math,hashlib,itertools,html
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;OLD=O.parent;K=OLD.parent.parent;ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(f,d):(O/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
oldseed=read(OLD/'first-expansion-batch.json');assert sha(OLD/'first-expansion-batch.json')=='9360a09116a099e6df54fd2848ee49bd3b39ab7c90d0b5273ba0bfb4089cc9e6'
coverage=read(OLD/'county-coverage-index.json');c=read(oldseed['source']['cityPath']);legacy=read(oldseed['source']['approvedCountyLayoutPath']);zf=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';z=read(zf);I=K/'revision-006/integration';lib=read(I/'asset-library.json');assets={a['id']:a for a in lib['assets']};cal={a['id']:a for a in read(I/'asset-calibration.json')['assets']};review=read(K/'revision-008/calibration/footprint-review.json');P=oldseed['projection'];u=review['localAxes']['T'];n=review['localAxes']['N']
names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),'<pure-geometry>','exec'))
# Freeze every old009 planning artifact, actual source city and stable calibration. Do not read a changing renderer.
protected={str(f):sha(f) for f in OLD.iterdir() if f.is_file()};protected.update({str(zf):sha(zf),oldseed['source']['cityPath']:sha(oldseed['source']['cityPath']),str(I/'asset-library.json'):sha(I/'asset-library.json'),str(I/'asset-calibration.json'):sha(I/'asset-calibration.json'),str(K/'revision-009/source-entry-semantics.md'):sha(K/'revision-009/source-entry-semantics.md')});write('protected-inputs.json',protected)
nodes={p['id']:[p['x'],p['y']] for p in c['nodes']}
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def gapbox(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def center(p):return [sum(v[k] for v in p)/len(p) for k in (0,1)]
def area(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges(p)))/2
bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings']) if len(p)>=3];segments=[(r,i,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for i,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))];water=[a['points'] for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3];wl=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:])];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node') in nodes]
protected_polys=oldseed['protectedExisting']['regionProtectionPolygonsMap']+[s['polygonMap'] for s in oldseed['groundSurfaces']]+[b['footprintPolygonMap'] for b in oldseed['buildings']]
parcelmeta=[(p,bbox([v for ring in p['rings'] for v in ring])) for p in legacy['parcels']]
def projectvector(v):return [v[0]*P['axisX'][k]+v[1]*P['axisY'][k] for k in (0,1)]
def angle(v):q=projectvector(v);return (math.degrees(math.atan2(q[1],q[0]))+90)%180-90
def strata(i):
 src=c['buildings'][i];C=center(src);edge=max(edges(src),key=lambda e:math.dist(*e));sv=[edge[1][k]-edge[0][k] for k in (0,1)];A=area(src);near=sorted(parcelmeta,key=lambda v:gapbox(bbox(src),v[1]))[:8];p=min(near,key=lambda v:min(math.dist(C,center(r)) for r in v[0]['rings']))[0];poi=min(pois,key=lambda x:math.dist(C,x[2]));return {'sourceIndex':i,'sourceId':f'city.buildings[{i}]','centerMap':C,'areaSquareMetres':A,'areaBand':'small<100' if A<100 else 'medium100..400' if A<400 else 'large>400','sourceLongestEdgeScreenDeg':angle(sv),'sourceDirectionMeaning':'measured footprint edge, not proof of a door/frontage','legacyParcelId':p['id'],'landUseIntent':p['landUse'],'intentIsSourceBuildingTypeProof':False,'nearestOriginalStop':{'poiIndex':poi[0],'nodeId':poi[1]['node'],'name':poi[1]['name'],'anchorMap':poi[2],'distanceMetres':math.dist(C,poi[2]),'association':'proposed design association only; source schema has no building binding'}}
remaining=[b for b in coverage['sourceBuildings'] if b['status']=='deferred'];untested=[b for b in remaining if b['screening'] is None];assert len(untested)==679
strat=[strata(b['sourceArrayIndex']) for b in untested];strat.sort(key=lambda x:(x['nearestOriginalStop']['distanceMetres']>90,x['areaSquareMetres']>400,math.dist(x['centerMap'],[-1500,150]),x['sourceIndex']))
write('untested-strata.json',{'uniqueSourceCount':len(strat),'rows':strat})
doors={'B05':[810,1070],'B06':cal['B06']['entryPixel'],'B01':[973,965],'B02':[750,970]}
def pixelmap(px,anchor,co,scale):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));sx,sy=[(px[k]-ap[k])/ppu*scale for k in (0,1)];a,b=P['axisX'],P['axisY'];dt=a[0]*b[1]-a[1]*b[0];return add(anchor,[(sx*b[1]-sy*b[0])/dt,(a[0]*sy-a[1]*sx)/dt])
def footprint(aid,anchor,scale):
 co=cal[aid];q=co.get('occupiedGroundOutlinePixel') or co.get('groundCornersPixelLeftFrontRightRear') or [[198,910],[438,1229],[1055,931],[815,612]];return [pixelmap(v,anchor,co,scale) for v in q]
def strip(a,b,w=1.5):
 D=math.dist(a,b)
 if D<.001:return None
 v=[-(b[1]-a[1])/D,(b[0]-a[0])/D];return [add(a,mul(v,w/2)),add(b,mul(v,w/2)),add(b,mul(v,-w/2)),add(a,mul(v,-w/2))]
def foot(p,a,b):
 v=[b[k]-a[k] for k in (0,1)];dt=sum(q*q for q in v);t=max(0,min(1,sum((p[k]-a[k])*v[k] for k in (0,1))/dt)) if dt else 0;return [a[k]+t*v[k] for k in (0,1)],t
rows=[];options=[]
# Explicit budget: first100 untested carriers;3 scale values,9 anchors,4 families,3 nearest roads,3 finite approach templates.
for meta in strat[:100]:
 idx=meta['sourceIndex'];src=c['buildings'][idx];C=meta['centerMap'];sb=bbox(src);reject=Counter();success=[];scale_attempts=Counter()
 others=[(i,p) for i,p,bb in bs if i!=idx and gapbox(sb,bb)<100];roads=[(r,j,a,b) for r,j,a,b,bb in segments if gapbox(sb,bb)<75];ww=[p for p in water if gapbox(sb,bbox(p))<100];ll=[(a,b) for a,b in wl if gapbox(sb,bbox([a,b]))<100]
 if meta['areaSquareMetres']>500:
  rows.append({**meta,'stage':'cluster-intent-review','result':'deferred','rejectedByRule':{'carrier-large-or-composite-needs-functional-proof':1},'clusterReview':{'evaluated':True,'oneSourceMultipleModulesPermitted':True,'candidatePattern':'two-to-four modules plus court, no navigation changes','decision':'defer; nearest decorative landUse is not evidence large original carrier is residential, school or factory; no secret factory-to-houses substitution'}});continue
 for aid in ['B05','B06','B01','B02']:
  for scale in ([1] if aid=='B01' else [.9,1,1.1]):
   for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3),(-6,0),(6,0),(0,-6),(0,6)]:
    scale_attempts[f'{aid}@{scale}']+=1
    anchor=add(add(C,mul(u,du)),mul(n,dn));poly=footprint(aid,anchor,scale)
    if not all(inbounds(v,'city') for v in poly):reject['cross-blue']+=1;continue
    if not inside(C,poly):reject['carrier-centre-not-covered']+=1;continue
    if any(pp(poly,p)<3 for p in protected_polys):reject['protected57-or-frozen-seed']+=1;continue
    if any(pp(poly,p)<2 for i,p in others):reject['neighbour-source-footprint']+=1;continue
    if min([pl(poly,a,b)-r['width']/2 for r,j,a,b in roads]+[9999])<2:reject['source-road-half-width']+=1;continue
    if any(pp(poly,p)<5 for p in ww) or any(pl(poly,a,b)<8 for a,b in ll):reject['water-buffer']+=1;continue
    entry=pixelmap(doors[aid],anchor,cal[aid],scale);out=add(entry,mul(n,1.1));own_after=add(entry,mul(n,.6))
    if inside(own_after,poly):reject['fixed-native-door-rim-uncertainty']+=1;continue
    near=sorted(roads,key=lambda r:math.dist(entry,foot(entry,r[2],r[3])[0]))[:3]
    fit=None
    for r,j,a,b in near:
     q,t=foot(entry,a,b);D=math.dist(q,entry)
     if D<=r['width']/2+1 or D>55:reject['road-shoulder-reach-budget']+=1;continue
     d=[(q[k]-entry[k])/D for k in (0,1)];end=add(q,mul(d,-(r['width']/2+.03)))
     mid=add(out,mul(u,sum((end[k]-out[k])*u[k] for k in (0,1))))
     routes=[('direct',[entry,end]),('front-side-L',[entry,out,mid,end]),('wider-side-L',[entry,add(entry,mul(n,3)),add(end,mul(n,3)),end])]
     for kind,pts in routes:
      pts=[v for k,v in enumerate(pts) if k==0 or math.dist(v,pts[k-1])>.001];polys=[strip(a,b) for a,b in zip(pts,pts[1:])];polys += [rect(v,1.5,1.5) for v in pts[1:-1]]
      if any(any(pp(p,b)<.15 for i,b in others) for p in polys):reject['approach-neighbour-source']+=1;continue
      if any(min(pl(p,a,b)-rr['width']/2 for rr,kk,a,b in roads)<-.001 for p in polys):reject['approach-road-half-width']+=1;continue
      if any(any(pp(p,w)<5 for w in ww) or any(pl(p,a,b)<8 for a,b in ll) for p in polys):reject['approach-water-buffer']+=1;continue
      if any(any(pp(p,q)<3 for q in protected_polys) or not all(inbounds(v,'city') for v in p) for p in polys):reject['approach-protection-or-blue']+=1;continue
      # Own body is exempt only at native threshold first0.6m, not along the rest of approach.
      if any(pp(p,poly)<.05 for p in polys[1:]):reject['approach-own-body-after-threshold']+=1;continue
      aa=add(entry,mul([(pts[1][k]-entry[k])/math.dist(entry,pts[1]) for k in (0,1)],min(.6,math.dist(entry,pts[1])*.9)))
      if pp(strip(aa,pts[1]),poly)<.05:reject['approach-own-body-after-threshold']+=1;continue
      fit={'roadId':r['id'],'segmentIndex':j,'routeTemplate':kind,'centrelineMap':pts,'polygonsMap':polys,'targetRoadT':t,'roadScreenDeg':angle([b[k]-a[k] for k in (0,1)])};break
     if fit:break
    if not fit:reject['bounded-approach-templates-exhausted']+=1;continue
    success.append({'sourceIndex':idx,'stratum':meta,'assetId':aid,'anchorMap':anchor,'uniformScale':scale,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':doors[aid],'approach':fit,'score':math.hypot(du,dn)+abs(scale-1)*5+math.dist(entry,fit['centrelineMap'][-1])});break
   if any(x['assetId']==aid for x in success):break
  if len(success)>=3:break
 row={**meta,'stage':'native-footprint-and-approach','result':'accepted-fit-option' if success else 'rejected-in-bounded-search','rejectedByRule':dict(reject),'attemptedAssetScales':dict(scale_attempts),'scaleSearchPolicy':'stop at first successful scale per family; untried scale is not a failed scale','positiveScaleCandidateValues':[.9,1,1.1],'B01BaselineScale':1,'feasibleAssetScales':[{'assetId':x['assetId'],'uniformScale':x['uniformScale'],'routeTemplate':x['approach']['routeTemplate']} for x in success]};rows.append(row);options.extend(success)
 write('fit-progress.json',{'processedUniqueSources':len(rows),'testedSources':rows,'fitOptions':options,'budgetUniqueSources':100})
print('FIT OPTIONS',len(options),'sources',len({x['sourceIndex'] for x in options}),flush=True)
# Joint admission adds explicit source-coverage and inter-candidate rules, not retroactive 'no fit'.
accepted=[];joint=[]
for idx,desired in [(602,'B06'),(609,'B01'),(598,'B05'),(599,'B06'),(418,'B01'),(223,'B05')]:
 candidates=[v for v in options if v['sourceIndex']==idx];candidates.sort(key=lambda v:(v['assetId']!=desired,v['score']))
 chosen=None
 for v in candidates:
  ratio=area(v['footprintPolygonMap'])/area(c['buildings'][idx])
  if ratio<.35 or ratio>2.5:joint.append({'sourceIndex':idx,'rule':'single-module-area-proxy-needs-cluster-review','ratio':ratio,'note':'screening policy, not proven physical impossibility; multi-module intention permitted with land-use evidence'});continue
  if any(pp(v['footprintPolygonMap'],q['footprintPolygonMap'])<2 or any(pp(p,q['footprintPolygonMap'])<.15 for p in v['approach']['polygonsMap']) or any(pp(p,v['footprintPolygonMap'])<.15 for p in q['approach']['polygonsMap']) for q in accepted):joint.append({'sourceIndex':idx,'rule':'joint-new-body-or-corridor'});continue
  chosen=v;break
 if chosen:accepted.append(chosen)
 assert len({x['sourceIndex'] for x in accepted})==len(accepted)
buildings=[];ground=[];roadids=set();source_decisions=[]
for x in accepted:
 idx=x['sourceIndex'];aid=x['assetId'];bid=f'009r2-src-{idx:04d}';sc=x['uniformScale'];ap=x['approach'];meta=x['stratum'];roadids.add(ap['roadId']);poly=x['footprintPolygonMap'];anchor=x['anchorMap']
 buildings.append({'id':bid,'persistentId':bid,'libraryAssetId':aid,'assetId':aid,'anchorMap':anchor,'uniformScale':sc,'anchorUV':assets[aid]['anchorUV'],'worldSizeUnits':[v*sc for v in assets[aid]['worldSizeUnits']],'rotation':0,'footprintPolygonMap':poly,'entryMap':x['entryMap'],'entryPixel':x['entryPixel'],'visualDoorPixel':x['entryPixel'],'visualDoorWorld':x['entryMap'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndex':idx,'sourceId':f'city.buildings[{idx}]','sourcePolygonMap':c['buildings'][idx],'sourceCitySHA256':sha(oldseed['source']['cityPath']),'sourceDataUnchanged':True},'clusterOfSource':{'sourceIndices':[idx],'visualModuleIds':[bid],'uniqueSourceCount':1,'remainingSpaceUse':'original carrier residue designated doorstep/garden ground only where static clearance allows; not a hidden claim original building function known'},'navigationStopNodeId':meta['nearestOriginalStop']['nodeId'],'navigationStopOriginalWorld':meta['nearestOriginalStop']['anchorMap'],'navigationStopAssociation':'new design proximity association only; source schema contains no original building/door binding; original stops/routes/name unchanged','navigationEdgesAdded':0,'landUseIntent':meta['landUseIntent'],'landUseEvidenceScope':'nearby approved decorative parcel context only, not proof original building historical function','sceneRole':'residential courtyard' if aid in ['B05','B06'] else 'small mixed street shop','visualApproach':ap,'status':'assigned-static-candidate-not-rendered-or-user-accepted','humanScaleCandidate':'positive uniform0.9/1/1.1 only; native door/step proportions retained; B01 old baseline and all existing instances unchanged'})
 for j,p in enumerate(ap['polygonsMap']):ground.append({'id':bid+f'-walk-{j}','materialId':'S01-paving','polygonMap':p,'purpose':'1.5m pedestrian door-to-source-shoulder; no road/stop/route edge added'})
 # Attach safe rear/side pocket garden to full doorstep arrangement; no isolated object on arbitrary tiles.
 localcoords=[[sum((p[k]-anchor[k])*u[k] for k in (0,1)),sum((p[k]-anchor[k])*n[k] for k in (0,1))] for p in poly];s0,s1=min(p[0] for p in localcoords),max(p[0] for p in localcoords);t0,t1=min(p[1] for p in localcoords),max(p[1] for p in localcoords)
 others=[(i,p) for i,p,bb in bs if i!=idx and gapbox(bbox(poly),bb)<50];nr=[(r,j,a,b) for r,j,a,b,bb in segments if gapbox(bbox(poly),bb)<50]
 for j,(ss0,tt0,ss1,tt1) in enumerate([(s0,t0-1.5,s1,t0),(s0-1,t0,s0,t1),(s1,t0,s1+1,t1)]):
  gp=[add(add(anchor,mul(u,s)),mul(n,t)) for s,t in [(ss0,tt0),(ss1,tt0),(ss1,tt1),(ss0,tt1)]]
  if any(pp(gp,p)<.1 for i,p in others) or any(pl(gp,a,b)-r['width']/2<.1 for r,kk,a,b in nr) or not all(inbounds(p,'city') for p in gp):continue
  if any(pp(gp,b['footprintPolygonMap'])<.1 for b in buildings if b['id']!=bid):continue
  if any(any(pp(gp,p)<.1 for p in q['approach']['polygonsMap']) for q in accepted if q['sourceIndex']!=idx):continue
  ground.append({'id':bid+f'-garden-{j}','materialId':'neutral-grass','color':'#9fb789','polygonMap':gp,'purpose':'household planted edge' if aid in ['B05','B06'] else 'mixed shop pocket green','noNaturalForestClaim':True})
# No side effect on old57 renderer: protected snapshot comes solely from frozen seed source.
batch={'schemaVersion':1,'version':'009-fit-round2-increment-v1','status':'static-instantiable-candidate-not-rendered-or-user-accepted','projection':P,'roads':[{**r,'sourceNodeIds':r['nodes'],'nodes':[nodes[i] for i in r['nodes']]} for r in c['roads'] if r['id']in roadids],'buildings':buildings,'fixtures':[],'groundSurfaces':ground,'parkingSpaces':[],'parkedVehicles':[],'frozenFirstBatch':{'path':str(OLD/'first-expansion-batch.json'),'sha256':sha(OLD/'first-expansion-batch.json')},'sources':{'city':oldseed['source'],'semanticsPath':str(K/'revision-009/source-entry-semantics.md'),'semanticsSHA256':sha(K/'revision-009/source-entry-semantics.md')},'protectedExisting':oldseed['protectedExisting'],'resourcePolicy':{'runtimeMaxEdge':280,'existingPNGOnly':True,'positiveUniformOnly':True,'oldB01T01ReferenceUnchanged':True,'T02':'natural tree without tree pit, reusable in lawful natural context; not a multiple-species forest claim','T01':'tree-pit tree','B09B10B11':'hold','P09':'not placed'},'uncertainty':'native ground and doorstep controls manually estimated; first0.6m door rim/step contact needs visual admission; no original source building/POI historical binding asserted'}
write('second-expansion-batch.json',batch);write('second-batch-manifest.json',{'path':str(O/'second-expansion-batch.json'),'sha256':sha(O/'second-expansion-batch.json'),'uniqueSourceCount':len(buildings),'visualModuleCount':len(buildings),'groundCount':len(ground),'status':batch['status']})
write('fit-summary.json',{'schemaVersion':1,'baselineDeferred':1004,'baselinePreviouslyScreenedDeferred':325,'baselineUntested':679,'thisRoundUniqueSourcesScreened':len(rows),'thisRoundAcceptedFitOptionsUniqueSources':len({x['sourceIndex'] for x in options}),'thisRoundAssignedUniqueSources':len(accepted),'thisRoundResults':dict(Counter(x['result'] for x in rows)),'allDeferredPipelineStageCounts':{'previousBoundedFixedScaleOnly':325,'newBoundedRound2Processed':len(rows),'stillNoScreening':679-len(rows)},'rejectedByRuleAttemptCounts':dict(sum((Counter(x['rejectedByRule']) for x in rows),Counter())),'attemptCountsAreNotSourceCounts':True,'uniqueSourceCountsWithRuleTriggered':dict(sum((Counter(set(x['rejectedByRule'])) for x in rows),Counter())),'terminalSourceOutcomes':dict(Counter(x['result'] for x in rows)),'old325RetestPerformed':False,'newScaleSuccessNotEvidenceScale1Failed':True,'sourceRows':rows,'jointAdmissionDecisions':joint,'untestedSources':[x['sourceIndex'] for x in strat[100:]],'budget':{'uniqueSources':100,'scales':[.9,1,1.1],'B01ScaleOnly':1,'anchorOffsetsMaxMetres':6,'roadsPerAttempt':3,'approachTemplates':['direct','front-side-L','wider-side-L']},'semantics':'untested != bounded failure != real resource deficit; source IDs counted once; original325 old search results do not imply new round failure','T02Correction':'T02 is natural tree without pit; T01 has pit'})
assert all(sha(f)==h for f,h in protected.items());print('INCREMENT READY',len(buildings),len(ground),sha(O/'second-expansion-batch.json'),flush=True)
