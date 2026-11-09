#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import json,math,ast,copy
from pathlib import Path
import neighborhood_export as e
I,R,lib=e.I,e.R,e.lib
P=R/'planning/next-neighborhood-plan-access-v2.json';SHA='f14674986d26a205177bd50798230ed3ef37d404ec68ca65996a7049c2e708df'
# Only pure geometry functions compiled from read-only planning script; no top-level planning code executed.
ns={'math':math}
tree=ast.parse((R/'planning/build_plan.py').read_text());names=['inside','ps','cross','ss','edges','pp','pl']
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'readonly-geometry','exec'),ns)
pp,pl,inside=ns['pp'],ns['pl'],ns['inside']
assert e.sha(P)==SHA
p=e.read(P);old=e.read(lib.OLD/'viewer/assets/scene-layout.json');oldm=e.read(lib.OLD/'viewer/assets/asset-manifest.json');library=e.read(I/'asset-library.json');assets={a['id']:a for a in library['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};ctx=e.read(R/'planning/source-context.json');city=e.read(ctx['source']);nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};roads={r['id']:r for r in city['roads']};u=p['fixedAssetFrame']['frontageTangentMap'];n=p['fixedAssetFrame']['eastNormalMap'];report=[]
def pixelmap(px,anchor,aid):
 c=cal[aid];rawanchor=c.get('anchorPixel',c.get('originalAnchorPixel'));ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));delta=[(px[k]-rawanchor[k])/ppu*16 for k in (0,1)];screen=e.project(anchor);return e.unproject([screen[k]+delta[k] for k in (0,1)])
def footprint(b,anchor):
 aid=b['assetId'];c=cal[aid]
 if c.get('occupiedGroundOutlinePixel'):pts=c['occupiedGroundOutlinePixel']
 elif c.get('groundCornersPixelLeftFrontRightRear'):pts=c['groundCornersPixelLeftFrontRightRear']
 elif aid=='B01':
  # frozen005 native calibration visible corners with inferred rear
  pts=[[198,910],[438,1229],[1055,931],[815,612]]
 else:raise ValueError('No real native ground controls '+aid)
 return [pixelmap(q,anchor,aid) for q in pts]
# Nearby full original road segments/source footprints, never adjusted to accommodate sprites.
segments=[(r['id'],r['width'],nodes[a],nodes[b]) for r in city['roads'] for a,b in zip(r['nodes'],r['nodes'][1:]) if all(-1850<q[0]<-1400 and -200<q[1]<350 for q in [nodes[a],nodes[b]])]
src=[q for q in ctx['sourceBuildings'] if q and max(v[0] for v in q)>-1800 and min(v[0] for v in q)<-1450 and max(v[1] for v in q)>-150 and min(v[1] for v in q)<300]
oldpoly=[]
for ob in e.read(lib.OLD/'planning/mixed-street-layout.json')['buildings']:oldpoly.append(footprint(dict(assetId=ob['id']),ob['anchorMap']))
selected=[];polys=[];skipped=['S1-01-B10']
for b in p['buildings']:
 if b['id']=='S1-01-B10':report.append({'id':b['id'],'decision':'excluded','reason':'parent requires hold B10 pending separately notified revision'});continue
 aid=b['assetId'];doorpx=b['entryAccessAudit']['nativeDoorEvidence']['observedDoorGroundPixelApprox'];original=b['anchorMap'];actualdoor=pixelmap(doorpx,original,aid);delta=[b['entryMap'][k]-actualdoor[k] for k in (0,1)];anchor=[original[k]+delta[k] for k in (0,1)];poly=footprint(b,anchor)
 roadgap=min(pl(poly,a,z)-w/2 for rid,w,a,z in segments);sourcegap=min(pp(poly,q) for q in src);newgap=min([pp(poly,q) for q in oldpoly+polys] or [999])
 # Confirm existing approved 1.5m corridor is not crossed by another real ground footprint.
 walk=next(c for c in p['pedestrianConnections'] if c['buildingId']==b['id']);corr=walk['surfacePolygonsMap'];walkgap=min([pp(w,q) for w in corr for q in oldpoly+polys]or[999])
 good=roadgap>=.1 and sourcegap>=.1 and newgap>=.1 and walkgap>=.05
 row={'id':b['id'],'assetId':aid,'originalAnchorMap':original,'appliedAnchorMap':anchor,'wholeSpriteTranslationMap':delta,'doorPixelFixed':doorpx,'fixedDoorMap':b['entryMap'],'roadEdgeGap':roadgap,'sourceBuildingGap':sourcegap,'priorNewBuildingGap':newgap,'walkVsPriorNewGap':walkgap,'nativeGroundPolygonMap':poly,'decision':'retained' if good else 'excluded','reason':'native-ground and fixed-door whole-sprite fit, positive library scale1' if good else 'real native footprint intersects source road/source building/accepted or prior placed building/corridor'}
 report.append(row)
 if not good:skipped.append(b['id']);continue
 nb=copy.deepcopy(b);nb.update({'persistentId':b['id'],'libraryAssetId':aid,'anchorMap':anchor});selected.append(nb);polys.append(poly)
# Symmetric checks against every kept walk prevent later placed building blocking earlier path.
for b,poly in list(zip(selected,polys)):
 conflicts=[]
 for other in selected:
  if other['id']==b['id']:continue
  walk=next(c for c in p['pedestrianConnections'] if c['buildingId']==other['id'])
  if any(pp(poly,w)<.05 for w in walk['surfacePolygonsMap']):conflicts.append(other['id'])
 if conflicts:skipped.append(b['id']);next(x for x in report if x['id']==b['id']).update({'decision':'excluded','reason':'native footprint obstructs other approved 1.5m walk','blockedWalks':conflicts})
selected=[b for b in selected if b['id']not in skipped]
plan={'schemaVersion':1,'status':'derived-runtime-subset-not-parent-original','projection':old['projection'],'buildings':selected,'fixtures':[],'groundSurfaces':copy.deepcopy(old['groundSurfaces']),'parkingSpaces':[],'parkedVehicles':[],'comparisonAssets':['T03'],'rider':old['rider'],'derivation':{'parentInputPath':str(P.resolve()),'parentApprovedSHA256':SHA,'rules':['exclude S1-01-B10 and its exclusive walk/parcel','reuse005 blocks unchanged by persistentId','translate whole new sprite only to fixed native door and approved walk start; no change to actual door pixels/scale','exclude only conflicting native ground instances','deduplicate full source roads by ID'],'excludedInstances':skipped}}
# Accepted005 objects retain exact exported coordinates/scale, not planning approximation.
for block in old['blocks']:
 a=next(a for a in oldm['assets'] if a['id']==block['assetId']);aid=block['sourceAssetId'];plan['fixtures'].append({'persistentId':block['persistentId'],'libraryAssetId':aid,'anchorMap':block['anchorMap'],'retained005':True})
for s in p['groundSurfaces']:
 owner=s.get('containsBuildingId',s.get('buildingId'))
 if owner in skipped or any(s['id'].startswith(k+'-')for k in skipped):continue
 q=copy.deepcopy(s);q['materialId']=s.get('materialId','G01-lawn' if s.get('material')=='neutral-grass' else 'S01-paving');plan['groundSurfaces'].append(q)
# Parking spaces derive from explicit planned parked-vehicle candidate footprints. Verify actual body envelope.
for f in p['fixtures']:
 aid=f['assetId']
 if aid.startswith('V'):
  aid+='-v2';c=cal[aid];slot=f['candidateFootprintPolygonMap'];length,width,height=c['candidateDimensionsLengthWidthHeight'];center=f['anchorMap'];actual=[ [center[k]+t*u[k]+z*n[k] for k in (0,1)]for t,z in [(-length/2,-width/2),(length/2,-width/2),(length/2,width/2),(-length/2,width/2)]]
  court=next(s['polygonMap'] for s in p['groundSurfaces']if s['id']==f['id'].split('-')[0]+'-court');gap=min(pl(actual,a,z)-w/2 for rid,w,a,z in segments);walkpolys=[w for conn in p['pedestrianConnections']if conn['buildingId']not in skipped for w in conn['surfacePolygonsMap']];walkgap=min(pp(actual,w) for w in walkpolys)
  # Candidate slot centre -> near-side wheel-midpoint anchor; retain actual crop world size.
  anchor=[center[k]+width/2*n[k]for k in (0,1)]
  good=all(inside(v,slot)for v in actual) and all(inside(v,court)for v in actual) and gap>.1 and walkgap>.1
  report.append({'id':f['id'],'assetId':aid,'decision':'retained-static-comparison'if good else'excluded','reason':'candidate body inside planned court, no road/walk overlap'if good else'actual candidate vehicle length/width cannot fit original planned individual slot/court/clearance','roadEdgeGap':gap,'walkGap':walkgap,'candidateBodyPolygonMap':actual})
  if good:
   slotid=f['id']+'-planned-parking';plan['parkingSpaces'].append({'id':slotid,'polygonMap':slot,'sourceCandidateSlot':slot,'sourceFixtureId':f['id'],'policy':'within already planned parking courtyard only; no new vehicle access'});plan['parkedVehicles'].append({'persistentId':f['id'],'libraryAssetId':aid,'parkingSpaceId':slotid,'anchorMap':anchor})
 else:
  # Existing approved fixture positions only; discard if root/foot intrudes actual building or walk.
  pos=f['anchorMap'];radius=f.get('groundRadiusCandidateMetres',.25)
  if any(inside(pos,q)or min(ns['ps'](pos,a,z)for a,z in ns['edges'](q))<radius for q in polys):continue
  plan['fixtures'].append({'persistentId':f['id'],'libraryAssetId':aid,'anchorMap':pos})
roadids={r['id']for r in old['roads']}|{s['roadId']for s in p['streets']};plan['roads']=[]
for rid in sorted(roadids):
 r=copy.deepcopy(roads[rid]);r['sourceNodeIds']=r['nodes'];r['nodes']=[nodes[n]for n in r['nodes']];plan['roads'].append(r)
assert len({b['persistentId']for b in plan['buildings']+plan['fixtures']+plan['parkedVehicles']})==len(plan['buildings']+plan['fixtures']+plan['parkedVehicles']);e.verify_roads(plan)
e.write(I/'runtime-subset-plan.json',plan);e.write(I/'placement-screening.json',{'parentSHA256':SHA,'status':'hand-native-ground-static-screening-not-precision-or-navigation','rows':report,'newBuildingCount':len(selected),'oldBuildingCount':5,'skipped':skipped,'sourceRoadsFullAndUnchanged':True})
print('subset',len(selected),'new buildings;',len(plan['parkedVehicles']),'parked comparisons; excluded',skipped)
