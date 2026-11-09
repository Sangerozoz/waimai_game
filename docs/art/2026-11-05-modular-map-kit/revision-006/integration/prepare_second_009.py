#!/usr/bin/env python3
"""Actual69 baseline, once-scaled round2 seed and bounded courtyard data; no main-map mutation."""
import sys
sys.dont_write_bytecode=True
import copy,hashlib,json,math
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'batch-009-r2';P=e.R.parent/'revision-009/planning/fit-round-2/second-expansion-batch.json';PS='1ba66318371ce8e9ff1ec905335a302d5070f28522a2130f295dc3c9decd92f1'
assert e.sha(P)==PS
if (I/'round2-009-increment.json').exists():raise ValueError('Round2 already appended; export editable map instead')
p=e.read(P);base=e.read(B/'pre-r2-scene.json');assert len(base['blocks'])==69 and len(base['groundSurfaces'])==135;assert e.sha(e.V/'assets/scene-layout.json')==e.sha(B/'pre-r2-scene.json');e.verify_roads(p)
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};ma={a['id']:a for a in e.read(B/'pre-r2-asset-manifest.json')['assets']};citypath=Path(p['sources']['city']['cityPath']);assert e.sha(citypath)==p['sources']['city']['citySHA256'];city=e.read(citypath);nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};sem=Path(p['sources']['semanticsPath']);assert e.sha(sem)==p['sources']['semanticsSHA256'];ctx=e.read(e.R/'planning/source-context.json');water=[a['points']for a in ctx['waterAreas']];roads=[dict(r,points=[nodes[n]for n in r['nodes']])for r in city['roads']]
protect=e.read(B/'read-only-protection.json');first=e.read(I/'batch-009/009-derived-plan.json');first8=[(f['persistentId'],f.get('rootCandidatePolygonMap',f.get('actualFootContactPolygonMap')))for f in first['fixtures']];first4=[s for s in first['groundSurfaces']if s['id'].endswith('-forecourt-base')]
zonefile=e.R.parent.parent/'2026-11-02-county-zoning/selection.json';zones=e.read(zonefile)['regions'];blue=zones['city']['worldPolygonMetresApprox'];protect[str(zonefile.resolve())]=e.sha(zonefile)
u=[-.23417355683909316,.9721948082958105];n=[.9721948082958105,.23417355683909316]
def bbox(poly):return[min(q[0]for q in poly),min(q[1]for q in poly),max(q[0]for q in poly),max(q[1]for q in poly)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
waterbb=[bbox(w)for w in water]
def water_gap(poly):
 bb=bbox(poly);best=float('inf');idx=None
 for lower,i in sorted((boxgap(bb,b),i)for i,b in enumerate(waterbb)):
  if lower>best:break
  d=g.gap(poly,water[i])
  if d<best:best,idx=d,i
 return best,idx
# Conservative billboard rectangles back-projected to ground are used only to prove separation,
# not asserted to be measured old foundations. All actual69 anchors/sizes come from current runtime.
old_envelopes=[]
for b in base['blocks']:
 a=ma[b['assetId']];q=e.project(b['anchorMap']);w,h=[v*16 for v in a['worldSizeUnits']];au,av=a['anchorUV'];poly=[e.unproject(z)for z in [[q[0]-au*w,q[1]-av*h],[q[0]+(1-au)*w,q[1]-av*h],[q[0]+(1-au)*w,q[1]+(1-av)*h],[q[0]-au*w,q[1]+(1-av)*h]]];old_envelopes.append((b['persistentId'],poly))
roadbb=[bbox(r['points'])for r in roads]
def road_gap(poly):
 bb=bbox(poly);best=float('inf');id=None
 for lower,i in sorted((max(0,boxgap(bb,b)-roads[i]['width']/2),i)for i,b in enumerate(roadbb)):
  if lower>max(0,best):break
  r=roads[i];d=g.line_gap(poly,r['points'])-r['width']/2
  if d<best:best,id=d,r['id']
 return best,id

def check(poly,owner,road_contact=False):
 nearest=min((g.gap(poly,q),i)for i,q in enumerate(city['buildings'])if i!=owner);rd,rid=road_gap(poly);wg,wi=water_gap(poly);old=min((g.gap(poly,q),id)for id,q in old_envelopes);gr=min((g.gap(poly,q['polygonMap']),q['id'])for q in base['groundSurfaces']);ff=min((g.gap(poly,q),id)for id,q in first8);fg=min((g.gap(poly,q['polygonMap']),q['id'])for q in first4)
 if nearest[0]<=1e-7:raise ValueError('Other original source building intersection '+str(nearest[1]))
 if rd<-.00001:raise ValueError('Original carriageway intersection '+rid+' '+str(rd))
 if wg<=0:raise ValueError('Original water polygon intersection '+str(wi))
 if old[0]<=0 or gr[0]<=0:raise ValueError('Actual69 sprite/135ground intersection')
 if not all(g.inside(q,blue)for q in poly):raise ValueError('Outside original blue boundary')
 return {'nearestOtherSourceBuildingGap':nearest[0],'nearestOtherSourceIndex':nearest[1],'roadCarriagewayGap':rd,'roadId':rid,'waterPolygonGap':wg,'waterAreaIndex':wi,'actual69ConservativeSpriteEnvelopeGap':old[0],'nearestOldInstance':old[1],'actual135GroundGap':gr[0],'nearestOldGround':gr[1],'actualFirst8FixtureContactGap':ff[0],'nearestFirstFixture':ff[1],'actualFirst4ExtraGroundGap':fg[0],'nearestFirstExtraGround':fg[1],'blueInside':True,'ownSourceOnlyExcluded':owner,'roadContactPermitted':'no crossing; original planned shoulder endpoint'}

nativechecks=[];checks=[];rejected=[];accepted=[];extras=[];surfacechecks=[]
for b in p['buildings']:
 b=copy.deepcopy(b);aid=b['libraryAssetId'];a=assets[aid];c=cal[aid];scale=b['uniformScale'];world=[v*scale for v in a['worldSizeUnits']];assert all(abs(world[k]-b['worldSizeUnits'][k])<1e-10 for k in (0,1));assert a['anchorUV']==b['anchorUV'];binding=b['visualReplacementOf'];own=binding['sourceIndex'];assert city['buildings'][own]==binding['sourcePolygonMap'] and binding['sourceCitySHA256']==e.sha(citypath)
 raw=Path(a['runtimeDerivation']['source']);raw=raw if raw.is_absolute()else e.R.parents[2]/raw
 if aid=='B01':provfile=e.R.parent/'revision-005/integration/provenance-check.json';pv=next(x for x in e.read(provfile)if x['id']=='B01');tool=Path(pv['source'])
 else:provfile=raw.parent/'provenance.json';pv=e.read(provfile);tool=Path(pv['toolSourceAbsolutePath'])
 assert e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256'];assert e.sha(I/'assets'/a['file'])==a['sha256'];b['sourceNativeSHA256']=e.sha(raw)
 for path in [raw,tool,provfile]:protect[str(path.resolve())]=e.sha(path)
 pp=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));ap=c.get('anchorPixel',c.get('originalAnchorPixel'));q=e.project(b['anchorMap']);entry=e.unproject([q[k]+16*scale*(b['entryPixel'][k]-ap[k])/pp for k in (0,1)]);assert math.dist(entry,b['entryMap'])<1e-8;assert nodes[b['navigationStopNodeId']]==b['navigationStopOriginalWorld']
 nc={'id':b['id'],'assetId':aid,'canonicalWorldSizeUnits':a['worldSizeUnits'],'planWorldSizeUnitsAlreadyScaled':b['worldSizeUnits'],'uniformScaleAppliedOnce':scale,'nativePPUUnchanged':pp,'anchorUVUnchanged':a['anchorUV'],'entryPixelFixed':b['entryPixel'],'entryMapConverted':entry,'entryDifference':math.dist(entry,b['entryMap']),'nativePath':str(raw.resolve()),'toolSourcePath':str(tool),'sourceNativeSHA256':e.sha(raw),'runtimeSHA256':a['sha256'],'originalStopId':b['navigationStopNodeId'],'originalStopWorld':nodes[b['navigationStopNodeId']],'visualDoorToStopDistance':math.dist(entry,nodes[b['navigationStopNodeId']]),'associationScope':'new design proximity only, not original building binding; no business mutation'}
 nativechecks.append(nc)
 try:
  bodycheck=check(b['footprintPolygonMap'],own);ss=[s for s in p['groundSurfaces']if s['id'].startswith(b['id']+'-')]
  for s in ss:surfacechecks.append({'id':s['id'],**check(s['polygonMap'],own)})
  # No new5/walk may intersect another new5 body or approach.
  for other in p['buildings']:
   if other['id']==b['id']:continue
   if g.gap(b['footprintPolygonMap'],other['footprintPolygonMap'])<=0 or any(g.gap(s['polygonMap'],other['footprintPolygonMap'])<=0 for s in ss):raise ValueError('New peer footprint/approach intersection '+other['id'])
  ownbody=b['footprintPolygonMap'];path=b['visualApproach']['centrelineMap'];d=[path[-1][k]-entry[k]for k in (0,1)];ll=math.hypot(*d);dd=[v/ll for v in d];contact=[j/100 for j in range(101)if g.inside([entry[k]+j/100*dd[k]for k in (0,1)],ownbody)]
  bodycheck.update({'id':b['id'],'sourceIndex':own,'ownFootprintContactCentrelineFirstMetreMax':max(contact,default=0),'ownFootprintAt0_6m':g.inside([entry[k]+.6*dd[k]for k in (0,1)],ownbody),'canonicalWorldSizeUnits':a['worldSizeUnits'],'actualWorldSizeUnits':world,'uniformScale':scale,'candidateSourceAreaRatio':g.area(ownbody)/g.area(binding['sourcePolygonMap']),'interpretation':'one visual building plus limited yard, not equal-shape original building reconstruction'});checks.append(bodycheck)
  accepted.append(b)
  # A small bounded green courtyard fills the three approved planted sides, never the long approach triangle.
  gardenpoints=ownbody+[q for s in ss if s['materialId']=='neutral-grass'for q in s['polygonMap']];origin=b['anchorMap'];tn=[[sum((q[k]-origin[k])*v[k]for k in (0,1))for v in [u,n]]for q in gardenpoints];lo=[min(q[k]for q in tn)for k in (0,1)];hi=[max(q[k]for q in tn)for k in (0,1)];yard=[[origin[k]+t*u[k]+v*n[k]for k in (0,1)]for t,v in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
  # Keep an additional0.5m yard margin to other original buildings; shrink only NEW optional yard, not the building or original20 surfaces.
  yardcheck=check(yard,own)
  if yardcheck['nearestOtherSourceBuildingGap']>=.5:
   extras.append({'id':b['id']+'-courtyard-lawn','materialId':'neutral-grass','color':'#9fb789','polygonMap':yard,'purpose':'limited household/shop courtyard lawn connecting three approved planted edges; no paving triangle','ownerBuildingId':b['id'],'areaSquareUnits':g.area(yard),'staticCheck':yardcheck})
  else:
   # Source599 has only0.067m at its optional rectangle corner. Use the true footprint plus0.25m inset on the yard sides; original garden strips stay as planned.
   for k in (0,1):lo[k]+=.25;hi[k]-=.25
   yard=[[origin[k]+t*u[k]+v*n[k]for k in (0,1)]for t,v in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]];yc=check(yard,own)
   if yc['nearestOtherSourceBuildingGap']>=.5:extras.append({'id':b['id']+'-courtyard-lawn','materialId':'neutral-grass','color':'#9fb789','polygonMap':yard,'purpose':'small household lawn; optional yard edges inset0.25m to protect adjacent source, approved planted strips unchanged','ownerBuildingId':b['id'],'staticCheck':yc,'optionalYardInsetOnly':.25,'areaSquareUnits':g.area(yard)})
   else:rejected.append({'surfaceId':b['id']+'-courtyard-lawn','reason':'optional rectangular yard would approach other original source closer than0.5m; not added','buildingRetained':True})
  # Compact door apron aligned to existing approach, 2.4m wide x1.2m outward, modest own step contact only.
  side=[-dd[1],dd[0]];apron=[[entry[k]+t*side[k]+z*dd[k]for k in (0,1)]for t,z in [(-1.2,0),(1.2,0),(1.2,1.2),(-1.2,1.2)]]
  try:
   ac=check(apron,own)
   if all(g.gap(apron,o['footprintPolygonMap'])>0 for o in p['buildings']if o['id']!=b['id']):extras.append({'id':b['id']+'-door-apron','materialId':'S01-paving','polygonMap':apron,'purpose':'compact2.4x1.2m pedestrian doorstep apron, meets existing1.5m walk; not a vehicle court','ownerBuildingId':b['id'],'staticCheck':ac})
  except ValueError as exc:rejected.append({'surfaceId':b['id']+'-door-apron','reason':str(exc),'buildingRetained':True})
 except ValueError as exc:rejected.append({'persistentId':b['persistentId'],'reason':str(exc),'fallbackCreated':False})
active={b['id']for b in accepted};grounds=[s for s in p['groundSurfaces']if any(s['id'].startswith(id+'-')for id in active)];derived=copy.deepcopy(p);derived['buildings']=accepted;derived['groundSurfaces']=extras+grounds;derived['derivation']={'parentOriginalPath':str(P.resolve()),'parentOriginalSHA256':PS,'actualBaseScenePath':str((B/'pre-r2-scene.json').resolve()),'actualBaseSceneSHA256':e.sha(B/'pre-r2-scene.json'),'actualBaseTiledSHA256':e.sha(B/'pre-r2-neighborhood.tmj'),'actualBaseCount':[69,135],'frozenPlan57NotUsedAsCurrentBaseline':True,'scaleContract':'plan world frame already scaled; canonical image frame + Tiled width/height once; runtime node scale1','extraGroundIds':[s['id']for s in extras],'extraInstances':[],'rejected':rejected,'rules':['preserve actual69 including first8 fixtures and4 supplemental grounds','only own source carrier exempt; others/water/road/business nodes retained','navigation-stop association metadata only, door independent','no original1.0 instance altered, no source PNG/PPU/UV changed','no large triangular paving hull; limited lawn and compact step apron only']}
e.write(B/'009r2-derived-plan.json',derived);e.write(B/'native-scale-entry-check.json',nativechecks);e.write(B/'geometry-protection-check.json',checks);e.write(B/'ground-protection-check.json',surfacechecks);e.write(B/'read-only-protection.json',protect)
print('Actual69 protected; accepted',len(accepted),'buildings;',len(grounds),'approved grounds +',len(extras),'limited yard/aprons; rejections',rejected,'derivedSHA',e.sha(B/'009r2-derived-plan.json'))
