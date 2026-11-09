#!/usr/bin/env python3
"""Freeze local neighbouring scenes, with complete finite courts, not remote counts."""
from pathlib import Path
# refuse frozen v2 overwrite
if (Path(__file__).resolve().parent/'fifth-expansion-batch-v2.json').exists():
 raise SystemExit('Frozen v2 exists; do not rebuild; consume import-contract.json.')
exec(compile(Path(__file__).with_name('plan_fifth.py').read_text().split('for idx in sorted(localids')[0],'readonly-local-context','exec'),globals())
progress=read(O/'local-fit-progress.json');pool=progress['newFitOptions'];accepted=[];assigned=set();reject=[];usage=Counter()
# Existing focus distance is primary, preserving two neighbourhood limits. No county-wide count chase.
while pool and len(assigned)<20:
 pool.sort(key=lambda x:(x['distanceToExistingFocusMetres']>105,usage[x['assetId']],x['distanceToExistingFocusMetres'],x['score']))
 x=pool.pop(0);idx=x['sourceIndex'];aid=x['assetId'];meta=x['stratum'];intent=meta.get('landUseIntent',meta.get('sourceLandUseIntent'))
 if idx in assigned or idx in bound or idx in reserved:continue
 if math.dist(x['anchorMap'],regions[x['regionId']])>140:reject.append({'sourceIndex':idx,'rule':'outside-fixed-local-neighbourhood'});continue
 if aid=='B03' and (intent!='mixed' or zone(x['anchorMap'])!='denseUrban') or aid in ['B04','B08'] and intent not in ['mixed','park'] or aid=='B07' and intent not in ['mixed','residential']:reject.append({'sourceIndex':idx,'rule':'programme'});continue
 if not good(audit(x['footprintPolygonMap'],[idx],[a['footprintPolygonMap'] for a in accepted]),True):reject.append({'sourceIndex':idx,'asset':aid,'rule':'body-vs-current143-or-new'});continue
 if any(not good(audit(p,[idx],[a['footprintPolygonMap'] for a in accepted])) for p in x['approach']['polygonsMap']):reject.append({'sourceIndex':idx,'asset':aid,'rule':'walk-vs-current143-or-new'});continue
 if any(any(pp(p,x['footprintPolygonMap'])<.15 for p in a['approach']['polygonsMap']) for a in accepted):reject.append({'sourceIndex':idx,'rule':'body-obstructs-admitted-walk'});continue
 r=next(r for r in c['roads'] if r['id']==x['approach']['roadId']);j=x['approach']['segmentIndex']
 if not all(inbounds(nodes[nid],'city') for nid in r['nodes'][j:j+2]):reject.append({'sourceIndex':idx,'rule':'source-road-segment-cross-blue'});continue
 accepted.append(x);assigned.add(idx);usage[aid]+=1
buildings=[];grounds=[];roadsneeded=set();scenes=[]
for x in accepted:
 idx=x['sourceIndex'];aid=x['assetId'];sc=x['uniformScale'];pid=f'009r5-src-{idx:04d}';anchor=x['anchorMap'];ap=x['approach'];roadsneeded.add(ap['roadId']);meta=x['stratum'];nearest=min(pois,key=lambda v:math.dist(anchor,v[2]));role='residential courtyard' if aid in ['B05','B06','B07'] else 'mixed street-service forecourt'
 b={'id':pid,'persistentId':pid,'libraryAssetId':aid,'assetId':aid,'anchorMap':anchor,'uniformScale':sc,'nodeScale':1,'worldSizeUnits':[v*sc for v in assets[aid]['worldSizeUnits']],'anchorUV':assets[aid]['anchorUV'],'rotation':0,'footprintPolygonMap':x['footprintPolygonMap'],'entryMap':x['entryMap'],'entryPixel':x['entryPixel'],'visualDoorPixel':x['entryPixel'],'visualDoorWorld':x['entryMap'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndices':[idx],'sourcePolygonsMap':[c['buildings'][idx]],'sourceSHA256':sha(cf),'sourceDataChanged':False},'clusterOfSource':{'sourceIndices':[idx],'sceneIds':[pid+'-plot'],'moduleIds':[pid],'uniqueSourceCount':1,'rendered':0},'regionId':x['regionId'],'programme':role,'landUseIntent':meta['landUseIntent'],'landUseEvidence':'approved prior decorative context; no invented historical source-business type','navigationStopNodeId':nearest[1]['node'],'navigationStopOriginalWorld':nearest[2],'originalStopName':nearest[1]['name'],'stopAssociation':'proposed proximity design only, no original source-building binding claimed; no nav edges added','visualApproach':ap,'status':'static-local-infill-not-rendered-or-user-accepted'}
 if aid=='B07':b.update(courtyardVoidPolygonMap=[add(add(anchor,mul(u,v[0]*sc)),mul(n,v[1]*sc)) for v in b07['courtyardVoidLocalTN']],nativeStepFrontPixel=[713,626],trueDoorControlIds=[11,12])
 buildings.append(b)
 for j,p in enumerate(ap['polygonsMap']):grounds.append({'id':pid+f'-walk-{j}','owner':pid,'materialId':'S01-paving','polygonMap':p,'purpose':'native door-to-source road shoulder1.5m pedestrian connection'})
 # Try a whole maintained plot, not just three strips. Exact ground may lie under this new sprite, never under another.
 local=[[sum((p[k]-anchor[k])*u[k] for k in (0,1)),sum((p[k]-anchor[k])*n[k] for k in (0,1))] for p in x['footprintPolygonMap']+c['buildings'][idx]];s0,s1=min(v[0] for v in local),max(v[0] for v in local);t0,t1=min(v[1] for v in local),max(v[1] for v in local)
 def at(s,t):return add(add(anchor,mul(u,s)),mul(n,t))
 def localrect(a,t,b,v):return [at(a,t),at(b,t),at(b,v),at(a,v)]
 candidates=[]
 if aid!='B07':
  candidates += [('complete-maintained-court',localrect(s0-1,t0-1,s1+1,t1+2),'neutral-grass' if aid in ['B05','B06'] else 'S01-paving','whole finite maintained yard/forecourt; actual occupant unchanged')]
 candidates += [('source-court',c['buildings'][idx],'neutral-grass' if aid in ['B05','B06'] else 'S01-paving','declared source-carrier yard as whole-purpose ground'),('entrance-apron',rect(add(x['entryMap'],mul(n,1.8)),4,3.6),'S01-paving','doorstep gathering/apron connected to fixed native door and walk; not a floating tile')]
 # Optional useful garden/soft-ground area, not a whole-street repeated band.
 candidates += [('rear-garden',localrect(s0,t0-4,s1,t0-1),'neutral-grass','rear household planted garden, deliberately maintained and separate from forecourt')]
 for name,p,mat,why in candidates:grounds.append({'id':pid+'-'+name,'owner':pid,'polygonMap':p,'materialId':mat,'color':'#a5b990','purpose':why})
 scenes.append({'id':pid+'-plot','sourceIndices':[idx],'moduleIds':[pid],'regionId':x['regionId'],'programme':role,'distanceToExistingFocusMetres':x['distanceToExistingFocusMetres'],'existingFocus':regions[x['regionId']],'designReason':'fill a missing real source lot within existing neighbourhood; old surfaces unmodified','notWholeDistrictComplete':True})
proof=[];safe=[];optionalreject=[]
for b in buildings:
 q=audit(b['footprintPolygonMap'],b['clusterOfSource']['sourceIndices'],[p['footprintPolygonMap'] for p in buildings if p['id']!=b['id']]);assert good(q,True);proof.append({'id':b['id'],'kind':'body','clearance':q})
for s in grounds:
 b=next(b for b in buildings if b['id']==s['owner']);idx=b['clusterOfSource']['sourceIndices'][0];q=audit(s['polygonMap'],[idx],[p['footprintPolygonMap'] for p in buildings if p['id']!=b['id']]);blocked=any(pp(s['polygonMap'],p)<.15 for bb in buildings if bb['id']!=b['id'] for p in bb['visualApproach']['polygonsMap']) if '-walk-'not in s['id'] else False
 if not good(q) or blocked:
  if '-walk-'in s['id']:raise AssertionError((s['id'],q))
  optionalreject.append({'id':s['id'],'clearance':q,'blocksNewWalk':blocked});continue
 if s['id'].endswith('entrance-apron') and pp(s['polygonMap'],b['footprintPolygonMap'])>0:
  # The apron must actually connect to this native threshold strip.
  assert any(pp(s['polygonMap'],p)==0 for p in b['visualApproach']['polygonsMap'])
 s['staticClearance']=q;safe.append(s);proof.append({'id':s['id'],'kind':'ground','clearance':q})
grounds=safe
# Require at least one finite court per new scene; scene with only thin door corridor isn't considered complete local infill.
removed=[]
for b in list(buildings):
 usable=[s for s in grounds if s['owner']==b['id'] and ('maintained-court'in s['id'] or s['id'].endswith('source-court') or s['id'].endswith('entrance-apron'))]
 if not usable:removed.append({'sourceIndex':b['clusterOfSource']['sourceIndices'][0],'reason':'only narrow path fits, no complete court/apron; rejected rather than repeat sparse strip template'});buildings.remove(b)
kept={b['id'] for b in buildings};grounds=[s for s in grounds if s['owner']in kept];scenes=[s for s in scenes if s['moduleIds'][0]in kept];assigned={i for b in buildings for i in b['clusterOfSource']['sourceIndices']};proof=[q for q in proof if q['id']in kept or any(s['id']==q['id'] for s in grounds)]
for s in scenes:s['groundSurfaceIds']=[g['id'] for g in grounds if g['owner']==s['moduleIds'][0]]
for b in buildings:
 assert b['navigationStopOriginalWorld']==nodes[b['navigationStopNodeId']]
roadsneeded={b['visualApproach']['roadId'] for b in buildings}
batch={'schemaVersion':1,'version':'009-fit-round5-local-infill-v1','status':'static-local-infill-candidate-not-rendered-or-user-accepted','projection':P,'roads':[{**r,'sourceNodeIds':r['nodes'],'nodes':[nodes[i] for i in r['nodes']]} for r in c['roads'] if r['id']in roadsneeded],'buildings':buildings,'fixtures':[],'groundSurfaces':grounds,'parkingSpaces':[],'parkedVehicles':[],'scenes':scenes,'sourceIndices':sorted(assigned),'uniqueSourceCount':len(assigned),'sceneCount':len(scenes),'moduleCount':len(buildings),'protection':{'snapshotPath':str(sf),'snapshotSHA256':sha(sf),'snapshotInstances':143,'snapshotGrounds':462,'snapshotBoundSources':69,'mixedSchemaBindingsFile':'baseline-source-bindings.json','priorFilesAllReadOnly':True,'finalAdmissionGate':'recheck actual latest stable increment including in-flight alley detailing and native comparisons; never reset live map from snapshot'},'sources':{'cityPath':str(cf),'citySHA256':sha(cf),'semanticsPath':str(K/'revision-009/source-entry-semantics.md')},'resourcePolicy':{'existingAdmittedB01throughB08Only':True,'runtimeMaxEdge':280,'sharedTextureFrame':True,'worldSizeUnitsAreFinal':True,'uniformScaleIsProvenanceOnly':True,'nodeScale':1,'heldAssetsNotUsed':['B09','B10','B11','T04'],'newComparisonAssetsNotAssumedReady':['B12','B13','T05'],'usageContractSourceReservationsPreserved':sorted(reserved)},'locality':{'allowedTwoFocusRegions':regions,'maxFocusDistanceMetres':140,'U0176ExistingOptionCount':0,'U0176NotPaddedWithRemoteLots':True,'purpose':'only infill market/housing neighbourhoods, not county-wide disconnected source count'},'unimplementedExistingSceneSuggestions':[{'focus':'market0587','suggestion':'existing public apron/local prop relations could be integrated after owner final baseline; no existing ground or prop modified here'},{'focus':'housing1735-1739','suggestion':'connect plot scene rhythm with existing detailed alley without widening road; this plan adds only its own checked court/entry'}],'uncertainty':'actual native outlines/hidden feet and first0.6m door threshold manual; no fake surveyed measurements or original building-POI binding; static geometry is not render acceptance'}
assert len(assigned)==len(buildings) and assigned.isdisjoint(bound|reserved)
write('fifth-expansion-batch.json',batch);write('baseline-source-bindings.json',{'uniqueSourceCount':len(bound),'bindings':binding_evidence,'readbackCompatibility':'sourceIndex/sourcePolygon and sourceIndices/sourcePolygonsMap both supported','noOldRecordRewritten':True});write('joint-clearance-evidence.json',{'proof':proof,'jointRejected':reject,'optionalSurfaceRejected':optionalreject,'onlyPathScenesRemoved':removed,'old143BodyControls':oldbody})
write('import-contract.json',{'batchSHA256':sha(O/'fifth-expansion-batch.json'),'worldSizeUnits':'final canonical x uniformScale already resolved ONCE; importer must not multiply again','uniformScale':'provenance only','nodeScale':1,'footprintEntryAndAnchorMap':'already final source-world coordinates; do not rescale','newInstancingOnly':'never replace scene snapshot or rewrite old source mappings','finalRecheckRequired':'latest completed actual baseline, including native comparison reserved source changes','B07':'door11[704,609] with original step12[713,626], exact U outline/void, old746,825 never a door'})
summary={'status':'locality-limited-bounded-fit','baseline':{'visible':143,'grounds':462,'boundUniqueSources':69},'initialExistingOptionPool':{'scope':'round3 completed queue only, excludes bound/reserved','optionsInsideTwo140mRegions':len(existing),'uniqueSourcesInsideTwoRegions':len({x['sourceIndex'] for x in existing}),'aroundU0176':0},'localAlternativeTrial':{'budgetSources':45,'processedSources':len(progress['rows']),'assetScaleAttempts':dict(sum((Counter(r.get('actualAssetScaleAttempts',{})) for r in progress['rows']),Counter())),'approachAttempts':dict(sum((Counter(r.get('actualApproachAttempts',{})) for r in progress['rows']),Counter())),'rejectedByRuleAttempts':dict(sum((Counter(r.get('rejectedByRule',{})) for r in progress['rows']),Counter())),'noWholeCountyRescan':True},'final':{'sources':len(assigned),'scenes':len(scenes),'modules':len(buildings),'groundPolygons':len(grounds),'sourceIndices':sorted(assigned),'byRegion':dict(Counter(b['regionId'] for b in buildings)),'visualTypeCounts':dict(Counter(b['assetId'] for b in buildings)),'renderedNew':0,'acceptedByUser':False},'rejectionFiles':'joint-clearance-evidence.json','existingStageCountersNotOverwritten':True,'provenanceScaleAppliedExactlyOnce':True,'additionalNativeTop2':[],'localGapAssessment':'bounded old-body/door/ground refusals are not proof new native direction alone necessary; no broad production order','physicalIntentUnknownSourceStage':'defer, no function invented from geometry'}
write('joint-fit-summary.json',summary);write('batch-manifest.json',{'path':str(O/'fifth-expansion-batch.json'),'sha256':sha(O/'fifth-expansion-batch.json'),'counts':summary['final']});assert all(sha(f)==h for f,h in protected.items());print('FIFTH FROZEN',summary['final'],sha(O/'fifth-expansion-batch.json'),flush=True)
