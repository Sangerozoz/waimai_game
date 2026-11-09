#!/usr/bin/env python3
"""Frozen round3 input -> individually admitted native plots, protecting actual74/164."""
import sys
sys.dont_write_bytecode=True
import copy,math
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'batch-009-r3';P=e.R.parent/'revision-009/planning/fit-round-3/third-expansion-batch.json';PS='654ccb00f1f75af0f487c9d2d3f7e8f88b06258ca1f73542dcc950978c1a6a12'
assert e.sha(P)==PS
if (I/'round3-009-increment.json').exists():raise ValueError('Round3 already appended; keep existing map edits and export only')
p=e.read(P);old=e.read(B/'pre-r3-scene.json');assert len(old['blocks'])==74 and len(old['groundSurfaces'])==164;assert e.sha(e.V/'assets/scene-layout.json')==e.sha(B/'pre-r3-scene.json');e.verify_roads(p)
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};aliases={a['id']:a for a in e.read(B/'pre-r3-asset-manifest.json')['assets']};citypath=Path(p['sources']['city']['cityPath']);city=e.read(citypath);assert e.sha(citypath)==p['sources']['city']['citySHA256'];nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};ctx=e.read(e.R/'planning/source-context.json');water=[s['points']for s in ctx['waterAreas']];roads=[dict(r,points=[nodes[n]for n in r['nodes']])for r in city['roads']];protect=e.read(B/'read-only-protection.json');sem=Path(p['sources']['semantics']);protect[str(sem.resolve())]=e.sha(sem)
zonefile=e.R.parent.parent/'2026-11-02-county-zoning/selection.json';blue=e.read(zonefile)['regions']['city']['worldPolygonMetresApprox'];protect[str(zonefile.resolve())]=e.sha(zonefile)
prior1=e.read(I/'batch-009/009-derived-plan.json');prior2=e.read(I/'batch-009-r2/009r2-derived-plan.json');exactprior={x['persistentId']:x for x in prior1['buildings']+prior1['fixtures']+prior2['buildings']};oldshapes=[]
for b in old['blocks']:
 a=aliases[b['assetId']];prior=exactprior.get(b['persistentId']);poly=None;scope='conservative billboard inverse-projection; used only when no closer ground control'
 if prior:
  candidate=prior.get('footprintPolygonMap',prior.get('actualFootContactPolygonMap',prior.get('rootCandidatePolygonMap')))
  if candidate:
   canonical=assets[b['sourceAssetId']];planned=prior.get('worldSizeUnits',canonical['worldSizeUnits']);scale=a['worldSizeUnits'][0]/planned[0];assert math.isclose(scale,a['worldSizeUnits'][1]/planned[1],rel_tol=1e-9);poly=[[b['anchorMap'][k]+(q[k]-prior['anchorMap'][k])*scale for k in (0,1)]for q in candidate];scope='actual prior admitted native footprint/contact adjusted from current runtime anchor/size'
 if poly is None:
  q=e.project(b['anchorMap']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];poly=[e.unproject(x)for x in [[q[0]-u*w,q[1]-v*h],[q[0]+(1-u)*w,q[1]-v*h],[q[0]+(1-u)*w,q[1]+(1-v)*h],[q[0]-u*w,q[1]+(1-v)*h]]]
 oldshapes.append({'id':b['persistentId'],'polygon':poly,'scope':scope})
first8=[s for s in oldshapes if s['id']in {f['persistentId']for f in prior1['fixtures']}];secondExtraIds=set(prior2['derivation']['extraGroundIds']);actualSecondExtras=[s for s in old['groundSurfaces']if s['id']in secondExtraIds];assert len(first8)==8 and len(actualSecondExtras)==9

def bbox(poly):return[min(q[0]for q in poly),min(q[1]for q in poly),max(q[0]for q in poly),max(q[1]for q in poly)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def indexed(rows):return[(id,poly,bbox(poly))for id,poly in rows]
sourceidx=indexed(enumerate(city['buildings']));oldidx=indexed((s['id'],s['polygon'])for s in oldshapes);groundidx=indexed((s['id'],s['polygonMap'])for s in old['groundSurfaces']);wateridx=indexed(enumerate(water));extraidx=indexed((s['id'],s['polygonMap'])for s in actualSecondExtras);firstidx=indexed((s['id'],s['polygon'])for s in first8);roadbbs=[bbox(r['points'])for r in roads]
def nearest(poly,idx,exclude=()):
 bb=bbox(poly);best=float('inf');item=None
 for lower,id,q in sorted((boxgap(bb,box),id,q)for id,q,box in idx if id not in exclude):
  if lower>best:break
  d=g.gap(poly,q)
  if d<best:best,item=d,id
 return best,item

def check(poly,own,peer=True,ownerid=None):
 if not all(g.inside(q,blue)for q in poly):raise ValueError('Outside blue boundary')
 source,srcid=nearest(poly,sourceidx,own);prior,priorid=nearest(poly,oldidx);ground,groundid=nearest(poly,groundidx);watergap,wid=nearest(poly,wateridx);second,secondid=nearest(poly,extraidx);first,fid=nearest(poly,firstidx)
 bb=bbox(poly);rgap=float('inf');rid=None
 for lower,j in sorted((max(0,boxgap(bb,box)-roads[j]['width']/2),j)for j,box in enumerate(roadbbs)):
  if lower>max(0,rgap):break
  rr=roads[j];distance=g.line_gap(poly,rr['points'])-rr['width']/2
  if distance<rgap:rgap,rid=distance,rr['id']
 reasons=[]
 for value,label,id in [(source,'other original source',srcid),(prior,'actual74 prior sprite ground/contact',priorid),(ground,'actual164 prior ground',groundid),(watergap,'original water area',wid)]:
  if value<=1e-7:reasons.append(label+' intersection '+str(id))
 if rgap<-.00001:reasons.append('original carriageway intersection '+str(rid))
 peerGap=float('inf');peerid=None
 if peer:
  for b in p['buildings']:
   if b['id']==ownerid:continue
   gap=g.gap(poly,b['footprintPolygonMap'])
   if gap<peerGap:peerGap,peerid=gap,b['id']
  if peerGap<=1e-7:reasons.append('new candidate body intersection '+str(peerid))
 poinear=float('inf');poinode=None
 for poi in city['pois']:
  q=nodes[poi['node']];dist=0 if g.inside(q,poly)else min(g.point_segment(q,a,z)for a,z in g.edges(poly))
  if dist<poinear:poinear,poinode=dist,poi['node']
 if poinear==0:reasons.append('original POI node covered '+poinode)
 result={'otherSourceGap':source,'otherSourceIndex':srcid,'actual74Gap':prior,'nearestPriorInstance':priorid,'actual164GroundGap':ground,'nearestPriorGround':groundid,'actualFirst8FixtureGap':first,'nearestFirstFixture':fid,'actualSecond9ExtraGroundGap':second,'nearestSecondExtraGround':secondid,'waterPolygonGap':watergap,'waterAreaIndex':wid,'roadEdgeGap':rgap,'roadId':rid,'otherNewBodyGap':peerGap,'otherNewBodyId':peerid,'nearestOriginalPOINodeGap':poinear,'nearestOriginalPOINodeId':poinode,'ownSourceIndicesOnlyExempted':own,'allVerticesBlue':True}
 if reasons:raise ValueError('; '.join(reasons))
 return result

accepted=[];surfaces=[];checks=[];surfacechecks=[];rejected=[];native=[]
for count,b in enumerate(p['buildings']):
 b=copy.deepcopy(b);binding=b['visualReplacementOf'];indices=binding['sourceIndices'];polys=binding['sourcePolygonsMap'];assert indices and len(indices)==len(polys);assert all(city['buildings'][index]==poly for index,poly in zip(indices,polys));assert binding['sourceSHA256']==e.sha(citypath)and binding['sourceDataChanged']is False;aid=b['libraryAssetId'];a=assets[aid];c=cal[aid];scale=b['uniformScale'];assert all(math.isclose(b['worldSizeUnits'][k],a['worldSizeUnits'][k]*scale,rel_tol=1e-12)for k in (0,1));assert b['anchorUV']==a['anchorUV'];assert aid!='B01'or scale==1
 raw=Path(a['runtimeDerivation']['source']);raw=raw if raw.is_absolute()else e.R.parents[3]/raw
 if aid=='B01':prov=I.parent.parent/'revision-005/integration/provenance-check.json';pv=next(x for x in e.read(prov)if x['id']=='B01');tool=Path(pv['source'])
 elif aid=='B02':prov=raw.parent/'provenance.json';pv=e.read(prov);tool=Path(pv['original_tool_output_absolute_path'])
 else:prov=raw.parent/'provenance.json';pv=e.read(prov);tool=Path(pv['toolSourceAbsolutePath'])
 assert e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256'];assert e.sha(I/'assets'/a['file'])==a['sha256'];b['sourceNativeSHA256']=e.sha(raw)
 for f in [raw,prov,tool]:protect[str(f.resolve())]=e.sha(f)
 ap=c.get('anchorPixel',c.get('originalAnchorPixel'));ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));q=e.project(b['anchorMap']);door=e.unproject([q[k]+16*scale*(b['entryPixel'][k]-ap[k])/ppu for k in (0,1)]);assert math.dist(door,b['entryMap'])<1e-8;assert nodes[b['navigationStopNodeId']]==b['navigationStopOriginalWorld'];native.append({'persistentId':b['id'],'sourceIndices':indices,'canonicalAssetId':aid,'canonicalWorldSizeUnits':a['worldSizeUnits'],'actualWorldSizeUnits':b['worldSizeUnits'],'uniformScaleOnce':scale,'entryPixel':b['entryPixel'],'actualDoorConvertedMap':door,'entryDifference':math.dist(door,b['entryMap']),'nativePPU':ppu,'anchorUV':a['anchorUV'],'sourceNativeSHA256':e.sha(raw),'nativePath':str(raw),'toolPath':str(tool),'provenancePath':str(prov),'runtimeSHA256':a['sha256']})
 try:
  body=check(b['footprintPolygonMap'],indices,ownerid=b['id']);body['persistentId']=b['id'];path=b['visualApproach']['centrelineMap'];end=path[-1];dd=[end[k]-door[k]for k in (0,1)];ll=math.hypot(*dd);direction=[v/ll for v in dd];touch=[j/100 for j in range(101)if g.inside([door[k]+j/100*direction[k]for k in (0,1)],b['footprintPolygonMap'])];body.update({'ownDoorContactFirstMetreMax':max(touch,default=0),'ownFootprintAt0_6m':g.inside([door[k]+.6*direction[k]for k in (0,1)],b['footprintPolygonMap'])})
  ownergrounds=[s for s in p['groundSurfaces']if s['owner']==b['id']];good=[];localchecks=[]
  for surface in ownergrounds:
   try:sc=check(surface['polygonMap'],indices,ownerid=b['id']);localchecks.append({'id':surface['id'],'owner':b['id'],**sc});good.append(surface)
   except ValueError as exc:
    if '-walk-'in surface['id']:raise ValueError('Essential visual approach conflict: '+str(exc))
    rejected.append({'surfaceId':surface['id'],'owner':b['id'],'reason':str(exc),'buildingRetained':True})
  accepted.append(b);surfaces.extend(copy.deepcopy(good));checks.append(body);surfacechecks.extend(localchecks)
 except ValueError as exc:rejected.append({'persistentId':b['id'],'sourceIndices':indices,'reason':str(exc),'fallbackCreated':False})
 print('checked',count+1,b['id'],flush=True)
active={b['persistentId']for b in accepted};actualindices=sorted({index for b in accepted for index in b['visualReplacementOf']['sourceIndices']});derived=copy.deepcopy(p);derived.update({'buildings':accepted,'groundSurfaces':surfaces,'sourceIndices':actualindices,'sourceMappings':[m for m in p['sourceMappings']if any(id in active for id in m['scenePersistentIds'])],'uniqueSourceCount':len(actualindices),'visualModuleCount':len(accepted),'derivation':{'parentOriginalPath':str(P.resolve()),'parentOriginalSHA256':PS,'actualBaseSceneSHA256':e.sha(B/'pre-r3-scene.json'),'actualBaseTiledSHA256':e.sha(B/'pre-r3-neighborhood.tmj'),'actualBaselineCounts':[74,164],'readPlanningFrozenSnapshotsAsCurrentBaseline':False,'rules':['sourceIndices/sourcePolygonsMap kept as arrays; sourceDataChanged=false','plan frame already scaled once; runtime nodeScale1','actual74/164 plus actual second9 supplemental surfaces and first8 fixtures hard protected','only own sourceIndices exempt; original source/road/water/POI/blue and peers remain checked','original96 intended surfaces used individually; no uniform triangular forecourt template','no extra art/white boxes/new business/navigation'], 'extraInstances':[],'extraGrounds':[],'rejected':rejected}})
e.write(B/'009r3-derived-plan.json',derived);e.write(B/'native-scale-entry-check.json',native);e.write(B/'actual74-body-protection-check.json',checks);e.write(B/'actual164-ground-protection-check.json',surfacechecks);e.write(B/'actual-old-shape-evidence.json',oldshapes);e.write(B/'read-only-protection.json',protect)
print('RESULT',len(accepted),'modules',len(actualindices),'sources',len(surfaces),'grounds; rejected',rejected,'derivedSHA',e.sha(B/'009r3-derived-plan.json'))
