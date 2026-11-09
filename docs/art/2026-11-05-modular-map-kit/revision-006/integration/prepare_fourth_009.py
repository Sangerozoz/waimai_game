#!/usr/bin/env python3
"""Freeze actual103/265 and statically screen the SHA-approved fourth batch, per instance."""
import sys
sys.dont_write_bytecode = True
import copy, math, json, shutil
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g

I=e.I; B=I/'batch-009-r4'
P=e.R.parent/'revision-009/planning/fit-round-4/fourth-expansion-batch.json'
PS='51c783395231d246898f715141f74c31cc153ac795f7d7de1b602c69a0fe16d5'
BASE='31a33ff6d27d92f609d7c56ea15769ea51d967fd19fabd7dbf05cbb791335bbf'
assert e.sha(P)==PS
if (I/'round4-009-increment.json').exists(): raise ValueError('Already incrementally applied; export existing editable map instead')
B.mkdir(exist_ok=True)
for src,name in [(e.V/'assets/scene-layout.json','pre-r4-scene.json'),(e.M,'pre-r4-neighborhood.tmj'),(e.V/'assets/asset-manifest.json','pre-r4-asset-manifest.json')]:
 dst=B/name
 if not dst.exists(): shutil.copyfile(src,dst)
 assert e.sha(src)==e.sha(dst),'Current editable baseline differs from frozen pre-r4 snapshot'
assert e.sha(B/'pre-r4-scene.json')==BASE
p=e.read(P); old=e.read(B/'pre-r4-scene.json'); assert [len(old['blocks']),len(old['groundSurfaces'])]==[103,265]
e.verify_roads(p)
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']}
cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']}
aliases={a['id']:a for a in e.read(B/'pre-r4-asset-manifest.json')['assets']}
citypath=Path(p['sources']['city']['cityPath']); city=e.read(citypath); assert e.sha(citypath)==p['sources']['city']['citySHA256']
nodes={n['id']:[n['x'],n['y']] for n in city['nodes']}
ctx=e.read(e.R/'planning/source-context.json'); water=[s['points']for s in ctx['waterAreas']]
roads=[dict(r,points=[nodes[n]for n in r['nodes']])for r in city['roads']]
protect=e.read(I/'central-life/read-only-protection.json')
for path in [P,P.parent/'import-contract.json',citypath,Path(p['sources']['entrySemantics']),I/'asset-library.json',I/'asset-calibration.json']:
 protect[str(path.resolve())]=e.sha(path)
zone=e.R.parent.parent/'2026-11-02-county-zoning/selection.json'
blue=e.read(zone)['regions']['city']['worldPolygonMetresApprox']; protect[str(zone.resolve())]=e.sha(zone)
oldshapes=e.read(I/'batch-009-r3/actual-old-shape-evidence.json')
oldshapes += [{'id':b['persistentId'],'polygon':b['footprintPolygonMap'],'scope':'admitted third-batch actual native positive-scalar footprint'} for b in e.read(I/'batch-009-r3/009r3-derived-plan.json')['buildings']]
oldshapes += [{'id':f['persistentId'],'polygon':f['groundContactPolygonMap'],'scope':f['groundContactMethod']} for f in e.read(I/'central-life/life-layout.json')['newFixtures']]
assert {s['id']for s in oldshapes}=={b['persistentId']for b in old['blocks']}

def bbox(poly): return [min(q[0]for q in poly),min(q[1]for q in poly),max(q[0]for q in poly),max(q[1]for q in poly)]
def boxgap(a,b): return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def indexed(rows): return [(id,poly,bbox(poly))for id,poly in rows]
sourceidx=indexed(enumerate(city['buildings'])); oldidx=indexed((s['id'],s['polygon'])for s in oldshapes)
groundidx=indexed((s['id'],s['polygonMap'])for s in old['groundSurfaces']); wateridx=indexed(enumerate(water))
lifeids={f['persistentId']for f in e.read(I/'central-life/life-layout.json')['newFixtures']}
lifeidx=indexed((s['id'],s['polygon'])for s in oldshapes if s['id']in lifeids)
lifegroundids=set(e.read(I/'central-life-increment.json')['newGroundIds']+e.read(I/'central-life-increment.json')['modifiedGroundIds'])
lifegroundidx=indexed((s['id'],s['polygonMap'])for s in old['groundSurfaces']if s['id']in lifegroundids)
roadbbs=[bbox(r['points'])for r in roads]

def nearest(poly,idx,exclude=()):
 bb=bbox(poly); best=float('inf'); item=None
 for lower,id,q in sorted((boxgap(bb,box),id,q)for id,q,box in idx if id not in exclude):
  if lower>best: break
  d=g.gap(poly,q)
  if d<best: best,item=d,id
 return best,item

def check(poly,own,ownerid):
 if not all(g.inside(q,blue)for q in poly): raise ValueError('Outside approved blue boundary')
 source,srcid=nearest(poly,sourceidx,own); prior,priorid=nearest(poly,oldidx); ground,groundid=nearest(poly,groundidx)
 watergap,wid=nearest(poly,wateridx); life,lid=nearest(poly,lifeidx); lifeground,lgid=nearest(poly,lifegroundidx)
 bb=bbox(poly); rgap=float('inf'); rid=None
 for lower,j in sorted((max(0,boxgap(bb,box)-roads[j]['width']/2),j)for j,box in enumerate(roadbbs)):
  if lower>max(0,rgap): break
  rr=roads[j]; distance=g.line_gap(poly,rr['points'])-rr['width']/2
  if distance<rgap: rgap,rid=distance,rr['id']
 peerGap,peerid=min((g.gap(poly,b['footprintPolygonMap']),b['id'])for b in p['buildings']if b['id']!=ownerid)
 poinear,poinode=min((0 if g.inside(nodes[poi['node']],poly)else min(g.point_segment(nodes[poi['node']],a,z)for a,z in g.edges(poly)),poi['node'])for poi in city['pois'])
 reasons=[]
 for value,label,id in [(source,'other original source',srcid),(prior,'actual103 prior sprite ground/contact',priorid),(ground,'actual265 protected ground',groundid),(watergap,'original water area',wid),(peerGap,'other new body',peerid)]:
  if value<=1e-7: reasons.append(label+' intersection '+str(id))
 if rgap<-.00001: reasons.append('original carriageway intersection '+str(rid))
 if poinear==0: reasons.append('original POI node covered '+poinode)
 row={'otherSourceGap':source,'otherSourceIndex':srcid,'actual103Gap':prior,'nearestPriorInstance':priorid,'actual265GroundGap':ground,'nearestPriorGround':groundid,'actualLife9FixtureGap':life,'nearestLifeFixture':lid,'actualLifeChangedAndNewGroundGap':lifeground,'nearestLifeGround':lgid,'waterPolygonGap':watergap,'waterAreaIndex':wid,'roadEdgeGap':rgap,'roadId':rid,'otherNewBodyGap':peerGap,'otherNewBodyId':peerid,'nearestOriginalPOINodeGap':poinear,'nearestOriginalPOINodeId':poinode,'ownSourceIndicesOnlyExempted':own,'allVerticesBlue':True}
 if reasons: raise ValueError('; '.join(reasons))
 return row

accepted=[]; surfaces=[]; checks=[]; surfacechecks=[]; rejected=[]; native=[]; dooraudits=[]
for count,original in enumerate(p['buildings']):
 b=copy.deepcopy(original); binding=b['visualReplacementOf']; indices=binding['sourceIndices']; polys=binding['sourcePolygonsMap']
 assert indices and len(indices)==len(polys) and all(city['buildings'][index]==poly for index,poly in zip(indices,polys))
 assert binding['sourceSHA256']==e.sha(citypath) and binding['sourceDataChanged']is False
 aid=b['libraryAssetId']; a=assets[aid]; c=cal[aid]; scale=b['uniformScale']
 assert aid in ['B01','B02','B03','B04','B05','B06','B07','B08'] and 'hold'not in a.get('availability','')
 assert b['rotation']==0 and all(math.isclose(b['worldSizeUnits'][k],a['worldSizeUnits'][k]*scale,rel_tol=1e-12)for k in (0,1))
 assert b['anchorUV']==a['anchorUV'] and (aid!='B01'or scale==1)
 raw=Path(a['runtimeDerivation']['source'])
 if aid=='B01':
  prov=I.parent.parent/'revision-005/integration/provenance-check.json'; pv=next(x for x in e.read(prov)if x['id']=='B01'); tool=Path(pv['source'])
 else:
  prov=raw.parent/'provenance.json'; pv=e.read(prov); tool=Path(pv.get('toolSourceAbsolutePath',pv.get('original_tool_output_absolute_path','')))
 assert e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256']; assert e.sha(I/'assets'/a['file'])==a['sha256']
 b['sourceNativeSHA256']=e.sha(raw)
 for f in [raw,prov,tool]: protect[str(f.resolve())]=e.sha(f)
 ap=c.get('anchorPixel',c.get('originalAnchorPixel')); ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU')); q=e.project(b['anchorMap'])
 def pixelmap(pix): return e.unproject([q[k]+16*scale*(pix[k]-ap[k])/ppu for k in (0,1)])
 door=pixelmap(b['entryPixel']); assert math.dist(door,b['entryMap'])<1e-8
 assert nodes[b['navigationStopNodeId']]==b['navigationStopOriginalWorld']
 row={'persistentId':b['id'],'sourceIndices':indices,'canonicalAssetId':aid,'canonicalWorldSizeUnits':a['worldSizeUnits'],'actualWorldSizeUnits':b['worldSizeUnits'],'uniformScaleOnce':scale,'runtimeNodeScale':1,'entryPixel':b['entryPixel'],'actualDoorConvertedMap':door,'entryDifference':math.dist(door,b['entryMap']),'nativePPU':ppu,'anchorUV':a['anchorUV'],'sourceNativeSHA256':e.sha(raw),'nativePath':str(raw),'toolPath':str(tool),'provenancePath':str(prov),'runtimeSHA256':a['sha256']}
 if aid=='B07':
  assert b['entryPixel']==[704,609] and c['stepFrontPixel']==[713,626]
  foot=[pixelmap(pix)for pix in c['occupiedGroundOutlinePixel']]
  assert len(foot)==len(b['footprintPolygonMap'])and max(math.dist(x,y)for x,y in zip(foot,b['footprintPolygonMap']))<1e-8
  assert len(b['courtyardVoidPolygonMap'])==4
  row.update({'stepPixel':c['stepFrontPixel'],'stepMap':pixelmap(c['stepFrontPixel']),'actualUOutlineMap':foot,'courtyardVoidPolygonMap':b['courtyardVoidPolygonMap'],'oldRejectedDoorUsed':False,'hiddenCornerIDs':[4,8],'hiddenCornerReserveCandidate':2,'uncertainty':'25px manual, inferred rear; no surveyed/navigation acceptance'})
 native.append(row)
 try:
  body=check(b['footprintPolygonMap'],indices,b['id']); body['persistentId']=b['id']
  # Expose own doorway/step contacts rather than silently applying all-obstacle exceptions.
  ownhits=[]; path=b['visualApproach']['centrelineMap']; travelled=0
  for start,end in zip(path,path[1:]):
   length=math.dist(start,end); n=max(1,math.ceil(length/.03))
   for j in range(n+1):
    pos=[start[k]+j/n*(end[k]-start[k])for k in (0,1)]
    if g.inside(pos,b['footprintPolygonMap']): ownhits.append(travelled+j/n*length)
   travelled+=length
  dooraudits.append({'persistentId':b['id'],'entryMap':door,'visualApproachStartMap':path[0],'doorToApproachStartMetres':math.dist(door,path[0]),'ownSolidCentrelineContactDistancesMetres':ownhits,'sampleStepMetresMaximum':.03,'scope':'own hand-estimated ground/step contacts only; foreign obstacles never exempt','requiresRuntimeVisualReview':True})
  ownergrounds=[s for s in p['groundSurfaces']if s['owner']==b['id']]; good=[]; localchecks=[]
  for surface in ownergrounds:
   try: sc=check(surface['polygonMap'],indices,b['id']); localchecks.append({'id':surface['id'],'owner':b['id'],**sc}); good.append(surface)
   except ValueError as exc:
    if '-walk-'in surface['id']: raise ValueError('Essential visual approach conflict: '+str(exc))
    rejected.append({'surfaceId':surface['id'],'owner':b['id'],'reason':str(exc),'buildingRetained':True})
  accepted.append(b); surfaces.extend(copy.deepcopy(good)); checks.append(body); surfacechecks.extend(localchecks)
 except ValueError as exc: rejected.append({'persistentId':b['id'],'sourceIndices':indices,'reason':str(exc),'fallbackCreated':False})
 print('checked',count+1,b['id'],flush=True)

active={b['persistentId']for b in accepted}; actualindices=sorted({index for b in accepted for index in b['visualReplacementOf']['sourceIndices']})
derived=copy.deepcopy(p); derived.update({'buildings':accepted,'groundSurfaces':surfaces,'sourceIndices':actualindices,'sourceMappings':[m for m in p['sourceMappings']if m['sceneId']in active],'uniqueSourceCount':len(actualindices),'visualModuleCount':len(accepted),'sceneCount':len(accepted),'derivation':{'parentOriginalPath':str(P.resolve()),'parentOriginalSHA256':PS,'importContractPath':str((P.parent/'import-contract.json').resolve()),'importContractSHA256':e.sha(P.parent/'import-contract.json'),'actualBaseSceneSHA256':e.sha(B/'pre-r4-scene.json'),'actualBaseTiledSHA256':e.sha(B/'pre-r4-neighborhood.tmj'),'actualBaselineCounts':[103,265],'rules':['actual life-street103/265 snapshot protected, never replay94','world frame=canonical*positive scalar already resolved; runtime node scale1','sourceIndices/sourcePolygonsMap retained arrays; sourceDataChanged=false','only own source carrier exempt; all foreign sources/water/roads/POI/blue/prior/peer bodies checked','B07 true door704/609 and step713/626, concave solid and transparent courtyard preserved','no new art/white boxes/business/navigation; original grounds unedited'],'extraInstances':[],'extraGrounds':[],'rejected':rejected}})
for name,data in [('009r4-derived-plan.json',derived),('native-scale-entry-check.json',native),('actual103-body-protection-check.json',checks),('actual265-ground-protection-check.json',surfacechecks),('actual-old-shape-evidence.json',oldshapes),('own-door-approach-review.json',dooraudits),('read-only-protection.json',protect)]: e.write(B/name,data)
print('RESULT',len(accepted),'modules',len(actualindices),'sources',len(surfaces),'grounds; rejected',json.dumps(rejected,ensure_ascii=False),'derivedSHA',e.sha(B/'009r4-derived-plan.json'))
