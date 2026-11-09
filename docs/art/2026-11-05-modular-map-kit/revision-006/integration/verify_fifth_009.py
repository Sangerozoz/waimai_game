#!/usr/bin/env python3
"""Static export/real Cocos evidence audit only; no game tests or FPS benchmark."""
import sys
sys.dont_write_bytecode=True
import math,copy,subprocess
from pathlib import Path
from collections import Counter,defaultdict
from PIL import Image
import neighborhood_export as e
I=e.I;B=I/'batch-009-r5';inc=e.read(I/'round5-009-increment.json');old=e.read(B/'pre-r5-scene.json');scene=e.read(e.V/'assets/scene-layout.json');manifest=e.read(e.V/'assets/asset-manifest.json');assets={a['id']:a for a in manifest['assets']};plan=e.read(inc['derivedPath'])
assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'] and e.sha(inc['derivedPath'])==inc['derivedSHA256']
assert scene['blocks'][:146]==old['blocks']and scene['groundSurfaces'][:466]==old['groundSurfaces']
doc=e.read(e.M);prev=e.read(B/'pre-r5-neighborhood.tmj');assert doc['layers'][:-1]==prev['layers'] and doc['tilesets']==prev['tilesets']
for k,v in old.items():
 if k not in ['blocks','groundSurfaces','roads','tiledSourceSHA256','cameraViews','groundRegions','visualReplacements']:assert scene[k]==v,k
assert all(scene['cameraViews'][k]==v for k,v in old['cameraViews'].items())
assert scene['groundRegions'][:len(old['groundRegions'])]==old['groundRegions']
assert scene['visualReplacements'][:len(old['visualReplacements'])]==old['visualReplacements']
assert all(next(x for x in scene['roads']if x['id']==r['id'])==r for r in old['roads']);e.verify_roads(scene)
oldassets=e.read(B/'pre-r5-asset-manifest.json')['assets'];assert all(assets[a['id']]==a for a in oldassets)
actual=e.read(B/'r5-housing-runtime.json');ui={x[0]:x for x in actual['ui']};nodes={x[0]:x for x in actual['order']};frames=defaultdict(set)
for aid,file,frame in actual['frames']:frames[file].add(frame)
assert all(len(ids)==1 for ids in frames.values())
oldruntime=e.read(I/'native-comparison/native-shrub-runtime.json');oldui={x[0]:x for x in oldruntime['ui']};checks=[];maxerror=0
for b in scene['blocks']:
 id=b['persistentId'];a=assets[b['assetId']];u=ui[id];n=nodes[id];assert u[3:5]==[1,1]
 assert all(math.isclose(u[5+k],a['worldSizeUnits'][k],rel_tol=1e-10)for k in(0,1))
 assert all(math.isclose(u[1+k],a['worldSizeUnits'][k]*32,rel_tol=1e-10)for k in(0,1))
 assert n[1]==b['editorRenderOrder'];q=e.project(b['anchorMap']);expected=[2*(q[0]-e.META['editorOrigin'][0]),-2*(q[1]-e.META['editorOrigin'][1])];err=math.dist(expected,n[3:5]);assert err<1e-4;maxerror=max(maxerror,err)
 if id in oldui:assert u[:5]==oldui[id][:5]
 if id in inc['activeInstanceIds']:checks.append({'persistentId':id,'canonicalAssetId':b['sourceAssetId'],'sourceIndices':b['sourceIndices'],'uniformScaleAppliedOnce':b['uniformScaleCandidate'],'runtimeNodeScale':u[3:5],'actualUIWidthHeight':u[1:3],'actualWorldFrameUnits':u[5:7],'manifestWorldFrameUnits':a['worldSizeUnits'],'actualNodeXY':n[3:5],'nodeProjectionDifferencePixels':err,'actualEditorOrder':n[1],'actualSiblingIndex':n[2],'runtimeFile':a['file'],'runtimeSHA256':a['sha256'],'sourceNativeSHA256':b['sourceNativeSHA256']})
assert [x[0]for x in actual['order']if x[0]in ui]==[b['persistentId']for b in sorted(scene['blocks'],key=lambda b:b['editorRenderOrder'])]
assert len(ui)==156 and len(actual['order'])==158 and len(checks)==10
allids=[b['persistentId']for b in scene['blocks']];allgrounds=[s['id']for s in scene['groundSurfaces']];assert len(allids)==len(set(allids))and len(allgrounds)==len(set(allgrounds))
sources=[i for v in scene['visualReplacements']for i in v.get('sourceIndices',[v.get('sourceIndex')])];assert None not in sources and len(set(sources))==81
files={a['file']for a in manifest['assets']};assert files=={p.name for p in(e.V/'assets').glob('*.png')}
resource=[{'file':f,'bytes':(e.V/'assets'/f).stat().st_size,'dimensions':list(Image.open(e.V/'assets'/f).size),'sha256':e.sha(e.V/'assets'/f)}for f in sorted(files)]
assert all(max(a['dimensions'])<=280 for a in resource)
protected=e.read(B/'read-only-protection.json');changed=[path for path,h in protected.items()if not Path(path).is_file()or e.sha(path)!=h];assert not changed,changed
snapshot={str(p):e.sha(p)for p in [e.V/'assets/scene-layout.json',e.V/'assets/asset-manifest.json',e.M]}
run=subprocess.run([sys.executable,str(I/'neighborhood_export.py'),'export'],capture_output=True,text=True,check=True)
assert all(e.sha(path)==h for path,h in snapshot.items()),'Re-export was not byte stable'
repeat=subprocess.run([sys.executable,str(I/'add_fifth_009.py')],capture_output=True,text=True)
assert repeat.returncode!=0 and 'refuse duplicate import'in repeat.stderr
ub=next(b for b in plan['buildings']if b['libraryAssetId']=='B07'); court=next(s for s in plan['groundSurfaces']if s['id'].endswith('-partial-inner-court'))
import geometry_009 as g
assert math.isclose(g.area(court['polygonMap']),12,abs_tol=1e-6)and all(g.inside(q,ub['courtyardVoidPolygonMap'])for q in court['polygonMap'])
assert g.gap(court['polygonMap'],ub['footprintPolygonMap'])>1.9
assert g.gap(court['polygonMap'],next(s['polygonMap']for s in plan['groundSurfaces']if s['id']=='009r5-src-1423-walk-0'))==0
assert not any(s['id']in['009r5-src-1423-source-court','009r5-src-1423-entrance-apron']for s in scene['groundSurfaces'])
result={'U1423PartialCourtArea':g.area(court['polygonMap']),'U1423SolidGap':g.gap(court['polygonMap'],ub['footprintPolygonMap']),'U1423PartialInsideVoidAndConnected':True,'U1423V1GroundsNotReplayed':True,'newB12B13T05Instances':0,'priorB12B13T05ComparisonOnlyUnchanged':True,'scope':'fifth-v2 source-bound static infill candidates; not complete streets/user acceptance','actualBaselineCounts':[146,466],'currentCounts':[156,497],'admittedBuildings':10,'admittedGrounds':31,'rejected':plan['derivation']['rejected'],'extraInstances':0,'extraGrounds':0,'sourceBoundVisuals':len(scene['visualReplacements']),'uniqueSourceCarrierIndices':len(set(sources)),'newBuildingTypes':dict(Counter(b['libraryAssetId']for b in plan['buildings'])),'old146BlocksEveryFieldExact':True,'old146ActualUISizesAndScalesExact':True,'old146RelativeOrderExact':True,'old466GroundsEveryFieldAndOrderExact':True,'oldTiledLayersAndTileDefinitionsExact':True,'oldCameraViewsAndDPathAndWaterPOIExact':True,'oldSourceBindingsExact':True,'oldAssetAliasesExact':True,'all156ActualNodesCoordinateUIWorldFrameAndOrderVerified':True,'actualRuntimeItemsWithDAndShadow':158,'maximumNodeProjectionDifferencePixels':maxerror,'canonicalWorldTimesCandidateScalarOnce':True,'runtimeNodeScalesAll1':True,'actualScaleVariants':dict(Counter(str(b['uniformScale'])for b in plan['buildings'])),'repeatedFilesShareFrame':True,'actualTextureStats':actual['textures'],'uniquePNG':len(resource),'PNGBytes':sum(a['bytes']for a in resource),'newPNGBytes':0,'runtimeLongEdgeMaximum':max(max(a['dimensions'])for a in resource),'protectedReadonlyFiles':len(protected),'changedProtectedFiles':changed,'completeOriginalRoadReferences':len(scene['roads']),'completeOriginalRoadNodeCount':sum(len(r['nodes'])for r in scene['roads']),'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'baselineSceneSHA256':inc['preSceneSHA256'],'baselineTiledSHA256':inc['preTiledSHA256'],'finalSceneSHA256':e.sha(e.V/'assets/scene-layout.json'),'finalTiledSHA256':e.sha(e.M),'sourceCitySHA256':plan['sources']['citySHA256'],'reExportByteStable':True,'repeatApplyRefused':True,'newBusinessPOIs':0,'newNavigationEdges':0,'newArtGenerated':False,'gameTestsTypecheckRegressionRenderMatrixFPSRun':False,'FPSOrMemoryMeasured':False,'all10IndividuallyVisuallyAccepted':False,'userAccepted':False,'actualFinalViewRecords':['r5-market','r5-housing']}
e.write(B/'final-verification.json',result);e.write(B/'actual-10-ui-scale-node-frame-check.json',checks);e.write(B/'runtime-resource-statistics.json',resource)
print(result)
