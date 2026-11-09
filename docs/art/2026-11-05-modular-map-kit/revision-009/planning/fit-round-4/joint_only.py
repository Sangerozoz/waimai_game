#!/usr/bin/env python3
"""Joint multi-region native fit; all writes restricted to round4."""
import ast
from pathlib import Path
if (Path(__file__).resolve().parent/'fourth-expansion-batch.json').exists():
 raise SystemExit('Frozen fourth batch exists; refuse overwrite. Review/import via import-contract.json.')
O=Path(__file__).resolve().parent;R3=O.parent/'fit-round-3'
tree=ast.parse((R3/'fit_round3.py').read_text().split('rows=[];options=[]')[0]);tree.body=[v for v in tree.body if not(isinstance(v,ast.Expr) and isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='write')];exec(compile(tree,'readonly-round3-context','exec'),globals())
# Own write helper above points to round4. Only frozen baseline is consumed, never current viewer.
baseline=K/'revision-009/baselines/visible94/scene-layout.json';tmj=baseline.with_name('neighborhood.tmj');scene=read(baseline);assert len(scene['blocks'])==94 and len(scene['groundSurfaces'])==260
catalogfile=K/'revision-009/art-expansion/catalog.json';catalog=read(catalogfile)
protected={str(f):sha(f) for f in [baseline,tmj,catalogfile,Path(oldseed['source']['cityPath']),I/'asset-calibration.json',I/'asset-library.json']};protected.update({str(f):sha(f) for d in [OLD,OLD/'fit-round-2',R3] for f in d.iterdir() if f.is_file()});write('protected-inputs.json',protected)
protected_polys=[s['polygonMap'] for s in scene['groundSurfaces']]
allcal={**cal}
for name in ['prop-calibration.json','prop-corners-calibration.json']:
 allcal.update({a['id']:a for a in read(I/name)['assets']})
# Baseline ground footprints derived from frozen anchors and stable native controls. Do not use overview camera bounds as physical obstacles.
for block in scene['blocks']:
 aid=block['sourceAssetId'];anchor=block['anchorMap'];co=allcal.get(aid)
 if aid in ['B01','B02','B03','B04','B05','B06','B08']:poly=footprint(aid,anchor,1)
 elif aid=='B07':poly=[add(add(anchor,mul(u,v[0])),mul(n,v[1])) for v in next(b for b in review['assets'] if b['id']=='B07')['conservativeOccupiedPolygonLocalTN']]
 elif co and co.get('groundContactPixelsManual') and len(co['groundContactPixelsManual'])>=3:poly=[pixelmap(v,anchor,co,1) for v in co['groundContactPixelsManual']]
 else:poly=rect(anchor,1.4 if aid.startswith('T') else .6,1.4 if aid.startswith('T') else .6)
 protected_polys.append(poly)
# Use the three frozen planned sets conservatively as additional exclusions (scales never re-applied).
priorbatches=[read(OLD/'first-expansion-batch.json'),read(OLD/'fit-round-2/second-expansion-batch.json'),read(R3/'third-expansion-batch.json')];previous=set()
for b in priorbatches:
 protected_polys += [x['footprintPolygonMap'] for x in b['buildings']]+[s['polygonMap'] for s in b['groundSurfaces']]
 for x in b['buildings']:previous.update(x['visualReplacementOf'].get('sourceIndices',[x['visualReplacementOf'].get('sourceIndex')]))
queue=read(R3/'next-source-fit-queue.json')['sourceOptions'];options=[q for items in queue.values() for q in items if q['sourceIndex']not in previous]
# Special visual types receive actual trials on large candidates, old325 and the37 context-only cases.
doors.update({'B03':[740,1060],'B04':[775,905],'B08':cal['B08']['entryPixel'],'B07':[704,609]})
specialrows=[];specialopts=[]
def actualpoly(aid,anchor,scale):
 if aid=='B07':return [add(add(anchor,mul(u,v[0]*scale)),mul(n,v[1]*scale)) for v in next(b for b in review['assets'] if b['id']=='B07')['conservativeOccupiedPolygonLocalTN']]
 return footprint(aid,anchor,scale)
def audit(poly,ids,newbodies=()):
 pb=bbox(poly);other=min([pp(poly,p) for i,p,bb in bs if i not in ids and gapbox(pb,bb)<80]+[9999]);rg=min([pl(poly,a,b)-r['width']/2 for r,j,a,b,bb in segments if gapbox(pb,bb)<80]+[9999]);wg=min([pp(poly,p) for p in water if gapbox(pb,bbox(p))<80]+[pl(poly,a,b)-3 for a,b in wl if gapbox(pb,bbox([a,b]))<80]+[9999]);pg=min(pp(poly,p) for p in protected_polys if gapbox(pb,bbox(p))<80) if any(gapbox(pb,bbox(p))<80 for p in protected_polys) else 9999
 return {'otherSourceMetres':other,'roadEdgeMetres':rg,'waterSafetyMetres':wg,'visible94AndPriorBatchesMetres':pg,'otherNewBodyMetres':min([pp(poly,p) for p in newbodies]+[9999]),'allVerticesBlue':all(inbounds(v,'city') for v in poly)}
def good(q,body=False):return q['allVerticesBlue'] and q['otherSourceMetres']>=(2 if body else .15) and q['roadEdgeMetres']>=(2 if body else -.001) and q['waterSafetyMetres']>=5 and q['visible94AndPriorBatchesMetres']>=1 and q['otherNewBodyMetres']>=(2 if body else .15)
prevsum=read(R3/'fit-summary.json');old325=[v for v in coverage['sourceBuildings'] if v['status']=='deferred' and v['screening'] and v['sourceArrayIndex']not in previous];large37=[v['sourceIndex'] for v in prevsum['sourceStageLedger'] if v['stage']=='cluster-intent-review'];targetids=list(dict.fromkeys(large37+[v['sourceArrayIndex'] for v in old325]))
# 100 source objects, up to4 types x3 scales x5 anchors; every source included by explicit budget choice.
targetids=sorted(targetids,key=lambda i:(area(c['buildings'][i])<100,math.dist(center(c['buildings'][i]),[-1600,200])))[:100]

specialdata=read(O/'special-type-progress.json');specialrows=specialdata['rows'];specialopts=specialdata['options']
# All options require joint readback against frozen94 and already chosen neighbours; previously passed != newly admitted.
combo=read(R3/'composite-followup-options.json')['manyToOneRecheckAgainstFrozen20'];pool=specialopts+options+([combo] if combo else [])
for x in pool:x.setdefault('sourceIndices',[x['sourceIndex']])
# Select across source-road neighbourhoods while allowing useful special types to lead their scenes.
pool.sort(key=lambda x:(x['assetId']not in ['B03','B04','B07','B08'],x['stratum']['landUseIntent']not in ['mixed','residential'],math.floor(x['anchorMap'][0]/250),math.floor(x['anchorMap'][1]/250),x.get('score',0)))
accepted=[];assigned=set();joint=[];usage=Counter()
while pool and len(assigned)<40:
 # Cap dominance by relative choice, not a geometric rejection. No starvation of an otherwise safe remaining option.
 pool.sort(key=lambda x:(x['assetId']not in ['B03','B04','B07','B08'],usage[x['assetId']],x.get('score',0)))
 x=pool.pop(0);ids=x['sourceIndices']
 if set(ids)&previous or set(ids)&assigned:continue
 if len(assigned)+len(ids)>40:continue
 aid=x['assetId'];intent=x['stratum']['landUseIntent'];A=sum(area(c['buildings'][i]) for i in ids)
 if aid=='B03' and (intent!='mixed' or zone(x['anchorMap'])!='denseUrban') or aid in ['B04','B08'] and intent not in ['mixed','park'] or aid=='B07' and intent not in ['residential','mixed']:
  joint.append({'sourceIndices':ids,'asset':aid,'rule':'programme-landUse-or-density-incompatible;geometry-pass-not-use-proof'});continue
 if A>1200:
  joint.append({'sourceIndices':ids,'asset':aid,'rule':'unknown-large-carrier-programme-deferred;no-factory-to-small-house'});continue
 body=x['footprintPolygonMap'];q=audit(body,ids,[a['footprintPolygonMap'] for a in accepted])
 if not good(q,True):joint.append({'sourceIndices':ids,'asset':x['assetId'],'rule':'body-clearance','clearance':q});continue
 bad=None
 for p in x['approach']['polygonsMap']:
  zq=audit(p,ids,[a['footprintPolygonMap'] for a in accepted])
  if not good(zq):bad=zq;break
 if bad:joint.append({'sourceIndices':ids,'asset':x['assetId'],'rule':'approach-clearance','clearance':bad});continue
 if any(any(pp(p,body)<.15 for p in a['approach']['polygonsMap']) for a in accepted):joint.append({'sourceIndices':ids,'rule':'new-body-blocks-previous-new-walk'});continue
 # All included source segments must sit inside blue, original node/width/direction preserved.
 r=next(r for r in c['roads'] if r['id']==x['approach']['roadId']);j=x['approach']['segmentIndex']
 if not all(inbounds(nodes[i],'city') for i in r['nodes'][j:j+2]):joint.append({'sourceIndices':ids,'rule':'stop-segment-cross-blue'});continue
 accepted.append(x);assigned.update(ids);usage[x['assetId']]+=1
buildings=[];grounds=[];roadids=set();mappings=[];groundrejected=[]
for x in accepted:
 ids=x['sourceIndices'];aid=x['assetId'];scale=x['uniformScale'];pid='009r4-src-'+'-'.join(f'{i:04d}' for i in ids);anchor=x['anchorMap'];ap=x['approach'];meta=x['stratum'];roadids.add(ap['roadId'])
 b={'id':pid,'persistentId':pid,'libraryAssetId':aid,'assetId':aid,'anchorMap':anchor,'uniformScale':scale,'worldSizeUnits':[v*scale for v in assets[aid]['worldSizeUnits']],'anchorUV':assets[aid]['anchorUV'],'rotation':0,'footprintPolygonMap':x['footprintPolygonMap'],'entryMap':x['entryMap'],'entryPixel':x['entryPixel'],'visualDoorPixel':x['entryPixel'],'visualDoorWorld':x['entryMap'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndices':ids,'sourcePolygonsMap':[c['buildings'][i] for i in ids],'sourceSHA256':sha(oldseed['source']['cityPath']),'sourceDataChanged':False},'clusterOfSource':{'sourceIndices':ids,'visualModuleIds':[pid],'strategy':x.get('clusterStrategy','single-source-design-replacement-with-yard'),'uniqueSourceCount':len(ids),'renderedSourceCount':0},'landUseIntent':meta['landUseIntent'],'landUseScope':'approved decorative parcel context; no claim source historical business type known','navigationStopNodeId':meta['nearestOriginalStop']['nodeId'],'navigationStopOriginalWorld':meta['nearestOriginalStop']['anchorMap'],'stopAssociation':'design proximity only; original POI/name/node/route unchanged','visualApproach':ap,'sceneProgramme':{'B01':'street shop forecourt','B02':'office/service forecourt','B03':'vertical mixed office frontage','B04':'neighbourhood public forecourt','B05':'compact residential garden','B06':'residential wing and courtyard','B07':'U-shaped residential court','B08':'covered market forecourt'}[aid],'status':'static-design-candidate-not-rendered-or-accepted'}
 if aid=='B07':b.update(courtyardVoidPolygonMap=[add(add(anchor,mul(u,v[0]*scale)),mul(n,v[1]*scale)) for v in next(v for v in review['assets'] if v['id']=='B07')['courtyardVoidLocalTN']],trueDoorControls=[11,12],rejectedOldDoor=[746,825])
 buildings.append(b);mappings.append({'sourceIndices':ids,'sceneId':pid,'moduleIds':[pid],'programme':b['sceneProgramme'],'nativeOccupiedArea':area(x['footprintPolygonMap']),'sourceAreaSum':sum(area(c['buildings'][i]) for i in ids),'mappingType':'design-scene-reorganisation-not-equal-shape-measurement','residualUse':'individual court/garden and retained unassigned native source context; no source rendered count inflation'})
 for j,p in enumerate(ap['polygonsMap']):grounds.append({'id':pid+f'-walk-{j}','materialId':'S01-paving','polygonMap':p,'purpose':'fixed native door / side court / original road shoulder pedestrian paving','owner':pid})
 # Whole source-court is a useful scene ground where lawful, not mandatory template.
 if aid!='B07':
  for i in ids:grounds.append({'id':pid+f'-source-court-{i}','materialId':'neutral-grass' if aid in ['B05','B06'] else 'S01-paving','color':'#9fb788','polygonMap':c['buildings'][i],'purpose':b['sceneProgramme']+' ground and maintenance yard','owner':pid})
 # A shape-specific forecourt connects directly to fixed native door, with variable depth and real envelope.
 pts=[p for p in x['footprintPolygonMap']];local=[[sum((p[k]-anchor[k])*u[k] for k in (0,1)),sum((p[k]-anchor[k])*n[k] for k in (0,1))] for p in pts];s0,s1=min(p[0] for p in local),max(p[0] for p in local);t0,t1=min(p[1] for p in local),max(p[1] for p in local)
 for j,(gs,gt,gw,gd) in enumerate([((s0+s1)/2,t0-1.2,s1-s0,2.4),(s0-.7,(t0+t1)/2,1.4,t1-t0),(s1+.7,(t0+t1)/2,1.4,t1-t0)]):
  poly=rect(add(add(anchor,mul(u,gs)),mul(n,gt)),gw,gd);grounds.append({'id':pid+f'-planted-pocket-{j}','materialId':'neutral-grass','color':'#a7bc92','polygonMap':poly,'purpose':'household garden edge' if aid in ['B05','B06','B07'] else 'public/mixed planted setback','owner':pid})
# Every exported polygon rechecked; optional grounds rejected individually, never make failed walks disappear.
proof=[];safe=[]
for b in buildings:
 q=audit(b['footprintPolygonMap'],b['clusterOfSource']['sourceIndices'],[x['footprintPolygonMap'] for x in buildings if x['id']!=b['id']]);assert good(q,True);proof.append({'id':b['id'],'kind':'body','clearance':q})
for s in grounds:
 b=next(b for b in buildings if b['id']==s['owner']);q=audit(s['polygonMap'],b['clusterOfSource']['sourceIndices'],[x['footprintPolygonMap'] for x in buildings if x['id']!=b['id']]);walkblocked=any(pp(s['polygonMap'],p)<.1 for x in accepted if '009r4-src-'+'-'.join(f'{i:04d}' for i in x['sourceIndices'])!=b['id'] for p in x['approach']['polygonsMap']) if '-walk-' not in s['id'] else False
 if not good(q) or walkblocked:
  if '-walk-' in s['id']:raise AssertionError((s['id'],q))
  groundrejected.append({'id':s['id'],'clearance':q,'otherNewWalkBlocked':walkblocked});continue
 s['staticClearance']=q;safe.append(s);proof.append({'id':s['id'],'kind':'ground','clearance':q})
grounds=safe
batch={'schemaVersion':1,'version':'009-fit-round4-v1','status':'static-instantiable-multi-region-candidate-not-rendered-or-user-accepted','projection':P,'roads':[{**r,'sourceNodeIds':r['nodes'],'nodes':[nodes[i] for i in r['nodes']]} for r in c['roads'] if r['id']in roadids],'buildings':buildings,'fixtures':[],'groundSurfaces':grounds,'parkingSpaces':[],'parkedVehicles':[],'sourceMappings':mappings,'sourceIndices':sorted(assigned),'uniqueSourceCount':len(assigned),'visualModuleCount':len(buildings),'sceneCount':len(buildings),'protection':{'visible94ScenePath':str(baseline),'visible94SceneSHA256':sha(baseline),'neighborhoodTMJSHA256':sha(tmj),'visibleInstances':94,'visibleGrounds':260,'frozenPreviousBatches':[{'sha256':sha(f),'path':str(f)} for f in [OLD/'first-expansion-batch.json',OLD/'fit-round-2/second-expansion-batch.json',R3/'third-expansion-batch.json']],'futureAdmissionGate':'recheck actual final stable baseline before integration; current writer renderer never read'},'sources':{'city':oldseed['source'],'entrySemantics':str(K/'revision-009/source-entry-semantics.md')},'resourcePolicy':{'maxRuntimeEdge':280,'nativeMastersExcluded':True,'existingReadyAssetsOnly':True,'newB12B13T04T05':'reservations only, not in batch','B09B10B11':'hold','T02':'natural no-pit tree','T01':'pit-tree'},'uncertainty':'native doorstep/hidden ground manually estimated; design source indices and module/scene counts distinct; no original source-building/POI historical binding; no user/render acceptance'}
write('fourth-expansion-batch.json',batch);write('joint-clearance-evidence.json',{'checks':proof,'jointRejected':joint,'optionalGroundRejected':groundrejected});write('batch-manifest.json',{'path':str(O/'fourth-expansion-batch.json'),'sha256':sha(O/'fourth-expansion-batch.json'),'sources':len(assigned),'scenes':len(buildings),'modules':len(buildings),'grounds':len(grounds),'assets':dict(usage)})
assert len(assigned)==sum(len(b['clusterOfSource']['sourceIndices']) for b in buildings);assert all(sha(f)==h for f,h in protected.items());print('FOURTH FROZEN',len(assigned),len(buildings),len(grounds),sha(O/'fourth-expansion-batch.json'),usage,flush=True)
