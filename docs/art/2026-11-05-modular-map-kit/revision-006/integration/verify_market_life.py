#!/usr/bin/env python3
"""Four explicit surface edits + five real fixtures: static/data and actual Cocos evidence only."""
import sys
sys.dont_write_bytecode=True
import math,copy,subprocess
from pathlib import Path
from collections import defaultdict
from PIL import Image
import neighborhood_export as e
import geometry_009 as g
from market_life import approved_prefix
I=e.I;B=I/'market-life';inc=e.read(I/'market-life-increment.json');p=e.read(inc['layoutPath']);old=e.read(inc['preScenePath']);scene=e.read(e.V/'assets/scene-layout.json');manifest=e.read(e.V/'assets/asset-manifest.json');assets={a['id']:a for a in manifest['assets']}
assert e.sha(inc['layoutPath'])==inc['layoutSHA256']and e.sha(inc['preScenePath'])==inc['preSceneSHA256'];assert scene['blocks'][:156]==old['blocks'];approved_prefix(e,scene['groundSurfaces'],old['groundSurfaces'])
authorized=set(p['authorizedOldSurfaceIds']);beforegrounds={s['id']:s for s in old['groundSurfaces']};aftergrounds={s['id']:s for s in scene['groundSurfaces']};modified=[id for id,s in beforegrounds.items()if aftergrounds[id]!=s];assert set(modified)==authorized
assert len(old['groundSurfaces'])-len(modified)==493 and aftergrounds[p['immutableWalkId']]==beforegrounds[p['immutableWalkId']]
assert [s['id']for s in scene['groundSurfaces'][:497]]==[s['id']for s in old['groundSurfaces']]
for k,v in old.items():
 if k not in ['blocks','groundSurfaces','tiledSourceSHA256','cameraViews','groundRegions']:assert scene[k]==v,k
assert all(scene['cameraViews'][k]==v for k,v in old['cameraViews'].items());assert scene['groundRegions'][:len(old['groundRegions'])]==old['groundRegions'];e.verify_roads(scene)
oldassets=e.read(B/'pre-market-asset-manifest.json')['assets'];assert all(assets[a['id']]==a for a in oldassets)
doc=e.read(e.M);pre=e.read(B/'pre-market-neighborhood.tmj');beforeobj={o['name']:(o,shift,l['id'])for l,shift in e.layer_objects(pre['layers'])for o in l['objects']};afterobj={o['name']:(o,shift,l['id'])for l,shift in e.layer_objects(doc['layers'])for o in l['objects']}
for id,(o,shift,lid)in beforeobj.items():
 current,sh,l=afterobj[id];assert sh==shift and l==lid
 if id not in authorized:assert current==o,('Unapproved Tiled object changed',id)
 else:
  allowedfields={'x','y','polygon','properties'};assert all(current[k]==value for k,value in o.items()if k not in allowedfields)
  beforeprops=e.props(o);afterprops=e.props(current);assert all(afterprops[k]==v for k,v in beforeprops.items()if k!='surfaceAssetId')
assert doc['tilesets']==pre['tilesets'];patched=copy.deepcopy(pre['layers'])
for l,shift in e.layer_objects(patched):
 l['objects']=[copy.deepcopy(afterobj[o['name']][0])if o['name']in authorized else o for o in l['objects']]
assert doc['layers'][:-1]==patched,'An old layer/index/offset/visibility changed'
assert afterobj[p['immutableWalkId']]==beforeobj[p['immutableWalkId']]
# New connector polygons sit wholly outside the old path's side edge, with a shared
# boundary only; the old surface retains its own draw order and material.
for ground in p['newGroundSurfaces']:
 if 'immutableWalkEdgeHalfPlane'in ground:
  hp=ground['immutableWalkEdgeHalfPlane'];assert all(sum(hp['normal'][k]*q[k]for k in(0,1))<=hp['constant']+1e-9 for q in ground['polygonMap']);assert g.gap(ground['polygonMap'],beforegrounds[p['immutableWalkId']]['polygonMap'])==0
actual=e.read(B/'market-life-detail-runtime.json');ui={x[0]:x for x in actual['ui']};nodes={x[0]:x for x in actual['order']};oldui={x[0]:x for x in e.read(I/'batch-009-r5/r5-housing-runtime.json')['ui']};frames=defaultdict(set)
for aid,file,frame in actual['frames']:frames[file].add(frame)
assert all(len(ids)==1 for ids in frames.values());checks=[];maxerr=0
for b in scene['blocks']:
 id=b['persistentId'];a=assets[b['assetId']];u=ui[id];n=nodes[id];assert u[3:5]==[1,1]and n[1]==b['editorRenderOrder']
 assert all(math.isclose(u[5+k],a['worldSizeUnits'][k],rel_tol=1e-10)and math.isclose(u[1+k],32*a['worldSizeUnits'][k],rel_tol=1e-10)for k in(0,1))
 q=e.project(b['anchorMap']);error=math.dist(n[3:5],[2*(q[0]-e.META['editorOrigin'][0]),-2*(q[1]-e.META['editorOrigin'][1])]);assert error<1e-4;maxerr=max(maxerr,error)
 if id in oldui:assert u[:5]==oldui[id][:5]
 else:checks.append({'persistentId':id,'assetId':b['sourceAssetId'],'actualUIWidthHeight':u[1:3],'actualWorldFrameUnits':u[5:7],'actualNodeScale':u[3:5],'actualNodeXY':n[3:5],'actualEditorOrder':n[1],'actualSiblingIndex':n[2],'file':a['file'],'fileSHA256':a['sha256'],'frameIndex':next(iter(frames[a['file']])),'projectionDifferencePixels':error})
assert len(ui)==161 and len(actual['order'])==163 and len(checks)==5
assert [r[0]for r in actual['order']if r[0]in ui]==[b['persistentId']for b in sorted(scene['blocks'],key=lambda b:b['editorRenderOrder'])]
assert all(128<b['actualEditorOrder']<155 for b in checks),'New fixtures must interleave, not render over every old sprite'
assert sum(b['sourceAssetId']=='T05'for b in scene['blocks'])==2
files={a['file']for a in manifest['assets']};assert files=={f.name for f in(e.V/'assets').glob('*.png')};oldfiles={a['file']for a in oldassets};assert files==oldfiles
resources=[{'file':f,'bytes':(e.V/'assets'/f).stat().st_size,'size':list(Image.open(e.V/'assets'/f).size),'sha256':e.sha(e.V/'assets'/f)}for f in sorted(files)];assert all(max(r['size'])<=280 for r in resources)
protected=e.read(B/'read-only-protection.json');changed=[path for path,h in protected.items()if not Path(path).is_file()or e.sha(path)!=h];assert not changed,changed
snapshot={str(f):e.sha(f)for f in[e.M,e.V/'assets/scene-layout.json',e.V/'assets/asset-manifest.json']};subprocess.run([sys.executable,str(I/'neighborhood_export.py'),'export'],capture_output=True,text=True,check=True);assert all(e.sha(path)==h for path,h in snapshot.items())
duplicate=subprocess.run([sys.executable,str(I/'add_market_life.py')],capture_output=True,text=True);assert duplicate.returncode!=0 and 'refuse duplicate apply'in duplicate.stderr
surfdiff=[]
for change in p['existingGroundChanges']:
 id=change['surfaceId'];bo,bs,bl=beforeobj[id];ao,as_,al=afterobj[id];surfdiff.append({'surfaceId':id,'worldBefore':beforegrounds[id],'worldAfter':aftergrounds[id],'changedWorldFields':[k for k in beforegrounds[id]if beforegrounds[id][k]!=aftergrounds[id][k]],'tiledBefore':bo,'tiledAfter':ao,'changedTiledFields':[k for k in bo if bo[k]!=ao[k]],'layerIdBeforeAfter':[bl,al],'groupOffsetBeforeAfter':[bs,as_],'reason':change['reason']})
result={'scope':'one market waiting/shade and collection scene, not county/user acceptance','baselineCounts':[156,497],'currentCounts':[161,501],'newFixtures':5,'newGrounds':4,'modifiedExistingGrounds':4,'modifiedGroundIds':modified,'immutableWalkAllFieldsAndTiledObjectExact':True,'other493GroundFieldsAndSequenceExact':True,'old156BlockFieldsActualUIFramesAndFixedRanksExact':True,'allOldTiledSpritesAndOtherGroundObjectsExact':True,'oldLayerMetadataDrawOrderAndOffsetsExact':True,'oldCameraViewsDPathSourceBindingRoadWaterPOINavExact':True,'all161NodesCoordinateUIFrameSizeScaleOrderVerified':True,'actualRuntimeRowsWithDAndShadow':163,'newFractionalRanksInterleaved':True,'maximumNodeProjectionDifferencePixels':maxerr,'allNodeScales1':True,'T05TotalInstances':2,'T05RootMeasured':False,'newVehicles':0,'newParkingSpaces':0,'newBusinessPOIs':0,'newNavigationEdges':0,'sourceBindings':len(scene['visualReplacements']),'uniquePNG':len(resources),'PNGBytes':sum(r['bytes']for r in resources),'newPNGBytes':0,'maximumPNGEdge':max(max(r['size'])for r in resources),'actualTextureStats':actual['textures'],'allRepeatedFilesShareFrame':True,'protectedReadonlyFiles':len(protected),'changedReadonlyFiles':changed,'baselineSceneSHA256':inc['preSceneSHA256'],'baselineTiledSHA256':inc['preTiledSHA256'],'marketLayoutSHA256':inc['layoutSHA256'],'finalSceneSHA256':e.sha(e.V/'assets/scene-layout.json'),'finalTiledSHA256':e.sha(e.M),'sourceCitySHA256':e.sha(e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json'),'originalRoadReferences':len(scene['roads']),'originalCompleteRoadNodeCount':sum(len(r['nodes'])for r in scene['roads']),'reExportByteStable':True,'duplicateApplyRefused':True,'newImagesGenerated':0,'gameTestsTypecheckRegressionRenderMatrixFPSRun':False,'FPSOrMemoryMeasured':False,'userAccepted':False}
e.write(B/'final-verification.json',result);e.write(B/'actual-four-surface-diff.json',surfdiff);e.write(B/'new-five-runtime-node-frame-check.json',checks);e.write(B/'runtime-resource-statistics.json',resources)
print(result)
