#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import math,ast
from pathlib import Path
from PIL import Image
import neighborhood_export as e
I=e.I;inc=e.read(I/'b07-wide-increment.json');plan=e.read(inc['snapshotPath']);old=e.read(inc['priorBaselinePath']);doc=e.read(e.M);oldmap=e.read(I/'pre-b07-neighborhood.tmj');oldobj={o['name']:o for l,s in e.layer_objects(oldmap['layers'])for o in l['objects']};newobj={o['name']:o for l,s in e.layer_objects(doc['layers'])for o in l['objects']};assert all(newobj[k]==v for k,v in oldobj.items());layout=e.read(e.V/'assets/scene-layout.json');rt=e.read(I/'runtime-b07-readback.json');actual={x['persistentId']:x for x in rt['order']if x['persistentId']};assert len(actual)==57 and len(layout['blocks'])==57 and len(layout['groundSurfaces'])==115 and len(rt['order'])==59
oldids=[x['persistentId']for x in old['blocks']];assert [x['persistentId']for x in layout['blocks']if x['persistentId']in oldids]==oldids
for b in old['blocks']:
 now=next(x for x in layout['blocks']if x['persistentId']==b['persistentId']);assert now['anchorMap']==b['anchorMap']
for s in old['groundSurfaces']:assert next(x for x in layout['groundSurfaces']if x['id']==s['id'])==s
assert all(layout['cameraViews'][k]==v for k,v in old['cameraViews'].items());assert layout['rider']==old['rider'];assert layout['roads']==old['roads'];e.verify_roads(layout);assert layout['groundRegions'][:2]==old['groundRegions'];errors=[]
for b in layout['blocks']:
 a=actual[b['persistentId']];p=e.project(b['anchorMap']);errors.append(math.dist([(p[0]-896)*2,-(p[1]-896)*2],[a['x'],a['y']]));assert a['editorOrder']==b['editorRenderOrder']
assert max(errors)<1e-4;assert rt['textures']=={'uniqueAssetImages':27,'nativeFramesCreated':25,'canvasFramesCreated':4};assert len(rt['grounds'])==3;assert any(x['id']=='b07wide008'and x['surfaceCount']==13 for x in rt['grounds'])
cal=next(a for a in e.read(I/'asset-calibration.json')['assets']if a['id']=='B07');assert cal['entryPixel']==[704,609]and cal['stepFrontPixel']==[713,626]and not cal['oldRejectedDoorUsed'];raw=Image.open(e.R/'native/B07-001/B07-v1.png');assert raw.getpixel((746,825))[3]==0
review=next(a for a in e.read(inc['calibrationPath'])['assets']if a['id']=='B07');assert cal['nativePixelsPerUnit']==review['nativePixelsPerUnit'];asset=next(a for a in e.read(I/'asset-library.json')['assets']if a['id']=='B07');assert asset['worldSizeUnits']==review['candidateWorldSizeUnits']and asset['anchorUV']==review['anchorUV'];assert e.sha(e.R/'native/B07-001/B07-v1.png')==review['nativeSHA256'];assert e.sha(review['actualToolSourcePath'])==review['nativeSHA256']
# Recompute U and void in actual world using retained positive scale and localT/N; no box approximation.
b=plan['buildings'][0];u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316]
def world(q):return [b['anchorMap'][k]+q[0]*u[k]+q[1]*n[k]for k in (0,1)]
poly=[world(q)for q in review['conservativeOccupiedPolygonLocalTN']];void=[world(q)for q in review['courtyardVoidLocalTN']];assert max(math.dist(q,r)for q,r in zip(poly,b['footprintPolygonMap']))<1e-8;assert max(math.dist(q,r)for q,r in zip(void,b['courtyardVoidPolygonMap']))<1e-8
ns={'math':math};tree=ast.parse((e.R/'planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in ['inside','ps','cross','ss','edges','pp','pl']],type_ignores=[]),'pure-geometry','exec'),ns)
walk=[s for s in plan['groundSurfaces']if s['id'].startswith('008-B07-walk-')];mingap=min(ns['pp'](poly,s['polygonMap'])for s in walk);assert abs(mingap-plan['checks']['minimumWalkOccupiedGapMetres'])<1e-8
# Compute upper-bound overlay area inside convex courtyard; overlapping caps double-counted conservatively.
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(p,p[1:]+p[:1])))/2 if p else 0
def clip(subject,bound):
 orientation=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(bound,bound[1:]+bound[:1]));sgn=1 if orientation>0 else -1;out=subject[:]
 for a,b in zip(bound,bound[1:]+bound[:1]):
  inp=out;out=[]
  if not inp:break
  for prev,cur in zip(inp[-1:]+inp[:-1],inp):
   dp=ns['cross'](a,b,prev)*sgn;dc=ns['cross'](a,b,cur)*sgn
   if (dp>=0)!=(dc>=0):
    t=dp/(dp-dc);out.append([prev[k]+t*(cur[k]-prev[k])for k in (0,1)])
   if dc>=0:out.append(cur)
 return out
covered=sum(area(clip(s['polygonMap'],void))for s in plan['groundSurfaces']);voidarea=area(void);ratio=covered/voidarea;assert ratio<.5
pngs=list((e.V/'assets').glob('*.png'));assert len(pngs)==27 and all(max(Image.open(p).size)<=280 for p in pngs);manifest=e.read(e.V/'assets/asset-manifest.json');assert {p.name for p in pngs}=={a['file']for a in manifest['assets']};protected=e.read(I/'b07-source-protection-before.json');changed=[p for p,h in protected.items()if e.sha(p)!=h];assert not changed,changed;assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['calibrationPath'])==inc['calibrationSHA256'];assert e.sha(plan['sourceEvidence']['corePlanPath'])==plan['sourceEvidence']['coreSHA256']
report=e.read(I/'export-report.json');report.update({'status':'actual-b07-courtyard-shown-small-comparison-not-user-or-navigation-accepted','staticInstances':57,'old56StaticInstancesUnchanged':True,'groundSurfaces':115,'old102GroundPolygonsUnchanged':True,'newB07Instances':1,'newB07GroundPolygons':13,'runtimeNodes':59,'runtimeTextures':rt['textures'],'groundCanvases':rt['grounds'],'allPriorCameraViewsPreserved':True,'sourceRoadsUnchanged':True,'roadCount':len(layout['roads']),'roadNodeCount':sum(len(r['nodes'])for r in layout['roads']),'doorPixel':[704,609],'stepPixel':[713,626],'oldFakeDoorUsed':False,'positiveScaleUnchanged':True,'recomputedMinimumWalkUGapMetresCandidate':mingap,'courtyardVoidAreaCandidate':voidarea,'exportedSurfaceAreaInsideVoidUpperBound':covered,'voidSurfaceCoverageUpperBound':ratio,'noWholeVoidOpaqueSlab':True,'runtimeUniquePNG':27,'runtimePNGBytes':sum(p.stat().st_size for p in pngs),'viewerFiles':sum(1 for p in e.V.rglob('*')if p.is_file()),'viewerTotalBytes':sum(p.stat().st_size for p in e.V.rglob('*')if p.is_file()),'sourceProtectedFiles':len(protected),'allRequiredSourceSHAUnchanged':True,'parentOriginalSHA256':inc['parentOriginalSHA256'],'calibrationSHA256':inc['calibrationSHA256'],'derivedSubsetSHA256':inc['derivedSubsetSHA256'],'maxRuntimeNodePositionError':max(errors),'visualDoorObservation':'actual inner right door/step visible and paving connected; no broad wall blocking seen in magnified screenshot;0.272m remains hand-footprint static candidate, not surveyed clearance or navigation pass','gameTestsRun':False});e.write(I/'export-report.json',report);e.write(I/'b07-source-protection-result.json',{'protectedFiles':len(protected),'allSHAUnchanged':True,'sourceSnapshotSHA256':e.sha(I/'b07-source-protection-before.json'),'parentOriginalSHA256':inc['parentOriginalSHA256'],'calibrationSHA256':inc['calibrationSHA256'],'coreOriginalSHA256':plan['sourceEvidence']['coreSHA256'],'derivedSubsetSHA256':inc['derivedSubsetSHA256'],'TMJSHA256':e.sha(e.M),'allPrior56StaticAnd102GroundPreserved':True});print({k:report[k]for k in ['staticInstances','groundSurfaces','runtimeUniquePNG','runtimePNGBytes','viewerTotalBytes','viewerFiles','sourceProtectedFiles','recomputedMinimumWalkUGapMetresCandidate','voidSurfaceCoverageUpperBound','maxRuntimeNodePositionError']})
