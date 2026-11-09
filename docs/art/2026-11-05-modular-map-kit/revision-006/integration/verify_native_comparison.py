#!/usr/bin/env python3
"""Static/data and actual Cocos evidence audit for three native comparisons, no game testing."""
import sys
sys.dont_write_bytecode=True
import math,subprocess
from pathlib import Path
from collections import defaultdict
from PIL import Image
import neighborhood_export as e
I=e.I;B=I/'native-comparison';inc=e.read(I/'native-comparison-increment.json');plan=e.read(inc['planPath']);old=e.read(B/'pre-comparison-scene.json');scene=e.read(e.V/'assets/scene-layout.json');manifest=e.read(e.V/'assets/asset-manifest.json');assets={a['id']:a for a in manifest['assets']}
assert e.sha(inc['planPath'])==inc['planSHA256'];assert scene['blocks'][:143]==old['blocks']and scene['groundSurfaces'][:462]==old['groundSurfaces']
doc=e.read(e.M);prev=e.read(B/'pre-comparison-neighborhood.tmj');assert doc['layers'][:-1]==prev['layers'];assert doc['tilesets'][0]['tiles'][:len(prev['tilesets'][0]['tiles'])]==prev['tilesets'][0]['tiles']
for k,v in old.items():
 if k not in ['blocks','groundSurfaces','roads','tiledSourceSHA256','cameraViews','groundRegions','visualReplacements']:assert scene[k]==v,k
assert all(scene['cameraViews'][k]==v for k,v in old['cameraViews'].items());assert scene['groundRegions'][:len(old['groundRegions'])]==old['groundRegions'];assert scene['visualReplacements'][:69]==old['visualReplacements']
assert all(next(x for x in scene['roads']if x['id']==r['id'])==r for r in old['roads']);e.verify_roads(scene)
oldassets=e.read(B/'pre-comparison-asset-manifest.json')['assets'];assert all(assets[a['id']]==a for a in oldassets)
lib=e.read(I/'asset-library.json');cal=e.read(I/'asset-calibration.json');oldlib=e.read(B/'pre-comparison-library.json');oldcal=e.read(B/'pre-comparison-calibration.json');assert lib['assets'][:len(oldlib['assets'])]==oldlib['assets'];assert cal['assets'][:len(oldcal['assets'])]==oldcal['assets']
actual=e.read(B/'native-shrub-runtime.json');ui={r[0]:r for r in actual['ui']};nodes={r[0]:r for r in actual['order']};oldui={r[0]:r for r in e.read(I/'batch-009-r4/r4-u-court-runtime.json')['ui']};frames=defaultdict(set)
for aid,file,frame in actual['frames']:frames[file].add(frame)
assert all(len(s)==1 for s in frames.values());checks=[];maxerr=0
for b in scene['blocks']:
 id=b['persistentId'];a=assets[b['assetId']];u=ui[id];n=nodes[id];assert u[3:5]==[1,1];assert n[1]==b['editorRenderOrder']
 assert all(math.isclose(u[5+k],a['worldSizeUnits'][k],rel_tol=1e-10)and math.isclose(u[1+k],32*a['worldSizeUnits'][k],rel_tol=1e-10)for k in(0,1))
 q=e.project(b['anchorMap']);err=math.dist(n[3:5],[2*(q[0]-e.META['editorOrigin'][0]),-2*(q[1]-e.META['editorOrigin'][1])]);assert err<1e-4;maxerr=max(maxerr,err)
 if id in oldui:assert u[:5]==oldui[id][:5]
 else:checks.append({'id':id,'assetId':b['sourceAssetId'],'actualUI':u[1:3],'actualWorldFrameUnits':u[5:7],'nodeScale':u[3:5],'actualEditorOrder':n[1],'actualSiblingIndex':n[2],'actualNodeXY':n[3:5],'runtimeFile':a['file'],'runtimeSHA256':a['sha256'],'projectionDifferencePixels':err})
assert len(ui)==146 and len(checks)==3 and len(actual['order'])==148
assert [r[0]for r in actual['order']if r[0]in ui]==[b['persistentId']for b in sorted(scene['blocks'],key=lambda b:b['editorRenderOrder'])]
files={a['file']for a in manifest['assets']};assert files=={f.name for f in(e.V/'assets').glob('*.png')};assert 'B13-runtime-280.png'not in files and 'B13-runtime-280-clean.png'in files
resources=[{'file':f,'bytes':(e.V/'assets'/f).stat().st_size,'size':list(Image.open(e.V/'assets'/f).size),'sha256':e.sha(e.V/'assets'/f)}for f in sorted(files)];assert all(max(r['size'])<=280 for r in resources)
for c in plan['calibration']:
 box=c['cropBox'];assert c['worldSizeUnits']==[(box[2]-box[0])/c['nativePixelsPerUnit'],(box[3]-box[1])/c['nativePixelsPerUnit']];assert c['anchorUV']==[(c['anchorPixel'][0]-box[0])/(box[2]-box[0]),(c['anchorPixel'][1]-box[1])/(box[3]-box[1])]
protected=e.read(B/'read-only-protection.json');changed=[p for p,h in protected.items()if not Path(p).is_file()or e.sha(p)!=h];assert not changed,changed
before={str(p):e.sha(p)for p in[e.V/'assets/scene-layout.json',e.V/'assets/asset-manifest.json',e.M]};subprocess.run([sys.executable,str(I/'neighborhood_export.py'),'export'],capture_output=True,text=True,check=True);assert all(e.sha(p)==h for p,h in before.items())
repeat=subprocess.run([sys.executable,str(I/'add_native_comparison.py')],capture_output=True,text=True);assert repeat.returncode!=0 and 'refuse duplicate apply'in repeat.stderr
sources=[i for r in scene['visualReplacements']for i in r.get('sourceIndices',[r.get('sourceIndex')])];assert len(set(sources))==71 and len(scene['visualReplacements'])==71
result={'scope':'B12/B13 each one real source carrier and one inferred-root T05 garden comparison only','baselineCounts':[143,462],'currentCounts':[146,466],'newInstances':3,'newGrounds':4,'rejectedCurrentCandidates':plan['rejected'],'old143BlocksAndActualUIExact':True,'old143OrderExact':True,'old462GroundFieldsAndOrderExact':True,'allExistingTiledLayersAndTilesExact':True,'oldCameraViewsDRouteSourceBindingPOIWaterExact':True,'oldCanonicalLibraryAndCalibrationEntriesExact':True,'libraryContainerFilesIntentionallyExtendedOnly':True,'B01T01PPUFrameAndAnchorPreserved':True,'all146RuntimeNodeCoordinateSizeScaleAndOrderVerified':True,'runtimeRowsWithDAndShadow':148,'maximumNodeProjectionDifferencePixels':maxerr,'cropWorldFrameAndAnchorPixelTransformVerified':True,'allNodeScales1':True,'T05RootMeasured':False,'T05EditorOrder':next(b['editorRenderOrder']for b in scene['blocks']if b['sourceAssetId']=='T05'),'repeatedFileFramesShared':True,'actualTextureStats':actual['textures'],'uniqueRuntimePNG':len(resources),'runtimePNGBytes':sum(r['bytes']for r in resources),'newPNGBytes':sum(r['bytes']for r in resources if r['file']in{a['file']for a in plan['assets']}),'runtimeMaximumLongEdge':max(max(r['size'])for r in resources),'B13OriginalNotPacked':True,'sourceCarrierBindings':71,'originalCompleteRoadReferences':len(scene['roads']),'originalCompleteRoadNodes':sum(len(r['nodes'])for r in scene['roads']),'protectedReadonlyFileCount':len(protected),'changedReadonlyFiles':changed,'baselineSceneSHA256':inc['preSceneSHA256'],'baselineTiledSHA256':inc['preTiledSHA256'],'comparisonPlanSHA256':inc['planSHA256'],'finalSceneSHA256':e.sha(e.V/'assets/scene-layout.json'),'finalTiledSHA256':e.sha(e.M),'sourceCitySHA256':e.sha(e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json'),'reExportByteStable':True,'duplicateApplyRefused':True,'newBusinessPOIs':0,'newNavigationEdges':0,'generatedImages':0,'gameTestsTypecheckRegressionRenderMatrixFPSRun':False,'userAccepted':False,'bulkBuildingOrPlantAdmission':False}
e.write(B/'final-verification.json',result);e.write(B/'new-three-runtime-node-frame-check.json',checks);e.write(B/'runtime-resource-statistics.json',resources)
print(result)
