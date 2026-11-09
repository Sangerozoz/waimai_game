#!/usr/bin/env python3
"""Actual consumer contract, exported bytes and Cocos readback audit; no game tests."""
import sys
sys.dont_write_bytecode=True
import copy,math,subprocess
from pathlib import Path
from collections import defaultdict
from PIL import Image
import neighborhood_export as e
sys.path.insert(0,str(e.R.parent/'revision-009/pipeline'))
from compound_contract import source_accounting,validate_candidate,require,PARENT_SHA

I=e.I;B=I/'compound-pilot';inc=e.read(I/'compound-pilot-increment.json');plan=e.read(inc['derivedPath']);old=e.read(inc['preScenePath']);scene=e.read(e.V/'assets/scene-layout.json');manifest=e.read(e.V/'assets/asset-manifest.json');assets={a['id']:a for a in manifest['assets']};citypath=e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json';city=e.read(citypath)
require(e.sha(inc['parentPath'])==PARENT_SHA and e.sha(inc['derivedPath'])==inc['derivedSHA256'],'Original/derived SHA changed')
reserved={i for r in e.read(e.R.parent/'revision-009/planning/fit-round-4/usage-contracts.json')['reservations']for i in r['sourceIndices']}
validation=validate_candidate(plan,old,city,e.sha(citypath),reserved)
require(scene['blocks'][:161]==old['blocks'],'Old161 full fields changed');require(scene['groundSurfaces'][:501]==old['groundSurfaces'],'Old501 full fields changed')
for key,value in old.items():
 if key not in ['blocks','groundSurfaces','roads','tiledSourceSHA256','cameraViews','groundRegions','visualReplacements']:require(scene[key]==value,'Old scene metadata changed: '+key)
require(scene['visualReplacements'][:81]==old['visualReplacements'],'Old81 source records rewritten')
require(all(scene['cameraViews'][k]==v for k,v in old['cameraViews'].items()),'Old camera changed')
require(scene['groundRegions'][:len(old['groundRegions'])]==old['groundRegions'],'Old region changed')
require(scene['roads'][:len(old['roads'])]==old['roads'],'Old road record fields/order changed');e.verify_roads(scene)
road=next(r for r in scene['roads']if r['id']=='605760963-0');require(road['width']==5 and road['direction']==1 and len(road['nodes'])==4,'Required complete road differs')
doc=e.read(e.M);pre=e.read(B/'pre-compound-neighborhood.tmj');require(doc['layers'][:-1]==pre['layers']and doc['tilesets']==pre['tilesets'],'Existing editable Tiled layers/objects/tiles changed')
newlayers=doc['layers'][-1]['layers'];require(len(newlayers[0]['objects'])==5 and len(newlayers[1]['objects'])==2,'Scene not appended atomically as two/five')
classes=[e.props(o)['surfaceClass']for o in newlayers[0]['objects']];require(classes[-2:]==['door-walk','door-walk']and classes.index('garden')<classes.index('door-walk'),'Ground ordering does not protect door routes')
oldassets=e.read(B/'pre-compound-asset-manifest.json')['assets'];require(all(assets[a['id']]==a for a in oldassets),'Old frame aliases/physical sizes changed')
accounting=source_accounting(scene);require(scene['sourceAccounting']==accounting,'Runtime source count not derived from union/ownership')
require([accounting[k]for k in ['uniqueSourceCount','sourceOwningSceneCount','sourceBoundModuleCount']]==[82,82,83],'Source/scene/module count conflated')
require(accounting['ownershipBySource']['125']=='scene:'+inc['sceneId'],'Shared source125 has wrong owner')
require(len(scene['compoundScenes'])==1 and scene['compoundScenes'][0]['moduleIds']==inc['moduleIds'],'Explicit compound registry missing')
# Explicitly prove a later read of the existing valid scene treats its two module
# bindings as one owner. This is not a duplicate append or a migration of old records.
require(source_accounting(copy.deepcopy(scene))==accounting,'Published shared owner not recognized')
runtime=e.read(B/'compound-detail-runtime.json');ui={r[0]:r for r in runtime['ui']};nodes={r[0]:r for r in runtime['order']};oldui={r[0]:r for r in e.read(I/'market-life/market-life-detail-runtime.json')['ui']};frames=defaultdict(set)
for aid,file,frame in runtime['frames']:frames[file].add(frame)
require(all(len(v)==1 for v in frames.values()),'Repeated runtime files did not share a frame')
checks=[];maxerr=0
for b in scene['blocks']:
 id=b['persistentId'];a=assets[b['assetId']];u=ui[id];n=nodes[id];require(u[3:5]==[1,1]and n[1]==b['editorRenderOrder'],'Node scale/order mismatch')
 require(all(math.isclose(u[5+k],a['worldSizeUnits'][k],rel_tol=1e-10)and math.isclose(u[1+k],32*a['worldSizeUnits'][k],rel_tol=1e-10)for k in(0,1)),'Runtime UI/world frame mismatch')
 p=e.project(b['anchorMap']);err=math.dist(n[3:5],[2*(p[0]-e.META['editorOrigin'][0]),-2*(p[1]-e.META['editorOrigin'][1])]);require(err<1e-4,'Node coordinate mismatch');maxerr=max(maxerr,err)
 if id in oldui:require(u[:5]==oldui[id][:5],'Old actual UI size changed')
 else:
  input=next(m for m in plan['buildings']if m['persistentId']==id);canonical=next(a for a in e.read(I/'asset-library.json')['assets']if a['id']==b['sourceAssetId'])
  require(all(math.isclose(u[5+k],canonical['worldSizeUnits'][k]*input['uniformScale'],rel_tol=1e-12)for k in(0,1)),'UniformScale applied twice')
  require(b['nativeFootlineEvidence']==input['nativeFootlineEvidence'],'Manual footline source evidence lost')
  checks.append({'persistentId':id,'sceneId':b['sceneId'],'sourceIndices':b['sourceIndices'],'sourceNativeSHA256':b['sourceNativeSHA256'],'libraryAssetId':b['sourceAssetId'],'canonicalWorldFrame':canonical['worldSizeUnits'],'uniformScaleOnce':input['uniformScale'],'actualWorldFrameUnits':u[5:7],'actualUISizePixels':u[1:3],'actualNodeScale':u[3:5],'actualNodeXY':n[3:5],'projectionDifferencePixels':err,'editorOrder':n[1],'actualSiblingIndex':n[2],'file':a['file'],'sha256':a['sha256'],'frameIndex':next(iter(frames[a['file']]))})
require(len(ui)==163 and len(runtime['order'])==165 and len(checks)==2,'Actual runtime count differs')
require([r[0]for r in runtime['order']if r[0]in ui]==[b['persistentId']for b in sorted(scene['blocks'],key=lambda b:b['editorRenderOrder'])],'Actual relative order differs')
require(all(128<r['editorOrder']<129 for r in checks),'New modules not interleaved around market depth')
files={a['file']for a in manifest['assets']};require(files=={a['file']for a in oldassets}=={p.name for p in(e.V/'assets').glob('*.png')},'Runtime package includes unused/new images')
resources=[{'file':f,'bytes':(e.V/'assets'/f).stat().st_size,'size':list(Image.open(e.V/'assets'/f).size),'sha256':e.sha(e.V/'assets'/f)}for f in sorted(files)];require(all(max(r['size'])<=280 for r in resources),'PNG exceeds280')
protected=e.read(B/'read-only-protection.json');changed=[p for p,h in protected.items()if not Path(p).is_file()or e.sha(p)!=h];require(not changed,'Protected input changed: '+str(changed))
negative=e.read(B/'consumer-negative-preflight.json');require(len(negative['cases'])==12 and all(c['rejected']and c['mainSHAUnchanged']for c in negative['cases']),'Missing real consumer rejection evidence')
duplicate=e.read(B/'duplicate-apply-rejection.json');require(duplicate['rejected']and duplicate['mainSHAUnchanged'],'Duplicate apply did not preserve main map')
tx=e.read(B/'transaction-journal.json');require(tx['status']=='committed'and tx['allModulesAndGroundsValidatedBeforeCommit'],'Transaction not committed as a validated whole')
require(all(e.sha(row['target'])==row['afterSHA256']for row in tx['publishTargets']),'Published files differ from validated transaction')
require(e.read(B/'aborted-stage-evidence.json')['mainInputsUnchanged'],'Aborted stage affected publication')
paths=[e.M,e.V/'assets/scene-layout.json',e.V/'assets/asset-manifest.json',e.V/'index.html',e.V/'assets/main/index.probe41.js'];before={str(p):e.sha(p)for p in paths}
subprocess.run([sys.executable,str(I/'neighborhood_export.py'),'export'],capture_output=True,text=True,check=True)
require(all(e.sha(path)==h for path,h in before.items()),'Repeated export changed map/manifest/HTML/renderer bytes')
result={'scope':'single limited actual source125 compound scene only, not bulk/art/navigation/user/county acceptance','actualBaselineCounts':{'statics':161,'grounds':501,'sourceUnion':81,'sourceOwners':81,'sourceBoundModules':81},'actualCurrentCounts':{'statics':163,'grounds':506,'sourceUnion':82,'sourceOwners':82,'sourceBoundModules':83},'thisIncrement':{'sources':1,'scenes':1,'modules':2,'grounds':5},'allOld161BlocksAndActualUIFixedRanksExact':True,'allOld501GroundFieldsAndOrderExact':True,'old81SourceRecordsByteEquivalentFieldsExact':True,'oldCamerasDWaterPOINavAndMarketLayerExact':True,'existingTiledAllLayersObjectsOffsetsTilesExact':True,'existingRoadRecordsAndCompleteNodesExact':True,'oldAssetAliasesAndCalibrationScalePreserved':True,'all163RuntimeNodeCoordinatesUISizesScalesAndOrderVerified':True,'actualRowsWithDAndShadow':165,'newModulesUseResolvedWorldSizeNodeScale1':True,'B01ManualFourFootPixelsAnd25pxUncertaintyCarried':True,'maximumNodeProjectionDifferencePixels':maxerr,'sameSource125HasOneExplicitSceneOwner':True,'publishedCompoundOwnerRecognizedOnSubsequentRead':True,'negativePreflightCasesRejected':12,'duplicateApplyRejectedMainSHAUnchanged':True,'transactionWholeSceneCommitted':True,'abortedStageBeforeLiveMutationPreserved':True,'repeatExportMapManifestHTMLRendererByteStable':True,'uniquePNG':len(resources),'PNGBytes':sum(r['bytes']for r in resources),'newPNGBytes':0,'maximumPNGEdge':max(max(r['size'])for r in resources),'actualTextureStats':runtime['textures'],'sharedFilesShareImageFrame':True,'protectedReadonlyFiles':len(protected),'changedProtectedFiles':changed,'parentOriginalSHA256':PARENT_SHA,'derivedSHA256':inc['derivedSHA256'],'baselineSceneSHA256':inc['preSceneSHA256'],'baselineTiledSHA256':inc['preTiledSHA256'],'finalSceneSHA256':e.sha(e.V/'assets/scene-layout.json'),'finalTiledSHA256':e.sha(e.M),'sourceCitySHA256':e.sha(citypath),'originalRoadReferences':len(scene['roads']),'completeOriginalRoadNodeCount':sum(len(r['nodes'])for r in scene['roads']),'newBusinessPOIs':0,'newNavigationEdges':0,'newNativeComparisonInstances':0,'generatedImages':0,'gameTestsTypecheckRegressionRenderMatrixFPSRun':False,'userAccepted':False,'bulkProductionSupported':False,'FPSOrMemoryMeasured':False}
e.write(B/'final-verification.json',result);e.write(B/'new-two-runtime-node-frame-check.json',checks);e.write(B/'runtime-resource-statistics.json',resources);e.write(B/'source-scene-module-accounting.json',accounting)
print(result)

