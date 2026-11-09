#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import copy,hashlib
from pathlib import Path
import neighborhood_export as e
I,R,lib=e.I,e.R,e.lib;P=R.parent/'revision-008/planning/next-district-plan.json';SHA='a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758';assert e.sha(P)==SHA
if (I/'suburb-increment.json').exists():raise ValueError('008 already applied; preserve editable map and export only')
plan=e.read(P);baseline=e.read(e.V/'assets/scene-layout.json');assert e.sha(e.V/'assets/scene-layout.json')==plan['protected006']['sceneSHA256'];assert len(baseline['blocks'])==43 and len(baseline['groundSurfaces'])==85;e.verify_roads(plan)
for name,path in [('pre-008-scene.json',e.V/'assets/scene-layout.json'),('pre-008-neighborhood.tmj',e.M),('pre-008-asset-manifest.json',e.V/'assets/asset-manifest.json'),('pre-008-export-report.json',I/'export-report.json')]:e.write(I/name,e.read(path))
protected={str(p.resolve()):e.sha(p)for root in [R.parent/'revision-008/planning',R.parent/'revision-008/calibration',R.parent/'revision-007',R.parent/'revision-005']for p in root.rglob('*')if p.is_file()};protected[str(Path(plan['sourceCity']['path']).resolve())]=e.sha(plan['sourceCity']['path']);e.write(I/'suburb-source-protection-before.json',protected)
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};deps=[]
for a in plan['resourceDependencies']:
 liba=assets[a['assetId']];assert liba['sha256']==a['sha256'];assert liba['worldSizeUnits']==a['worldSizeUnits'] and liba['anchorUV']==a['anchorUV'];deps.append({'id':a['assetId'],'sha256':a['sha256'],'sameScaleAndAnchorAsLibrary':True})
# Actual entry pixels -> existing anchor/PPU -> fixed projection world; no inherited B05 annotation used for B06/B08.
entries=[]
for b in plan['buildings']:
 c=cal[b['assetId']];px=e.project(b['anchorMap']);raw=c.get('anchorPixel',c.get('originalAnchorPixel'));ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));actual=e.unproject([px[k]+(b['entryPixel'][k]-raw[k])/ppu*16 for k in (0,1)]);err=__import__('math').dist(actual,b['entryMap']);assert err<1e-8;entries.append({'id':b['id'],'entryPixel':b['entryPixel'],'actualConvertedDoorMap':actual,'planEntryMap':b['entryMap'],'worldDifference':err})
doc=e.read(e.M);existing={o['name']:copy.deepcopy(o)for l,shift in e.layer_objects(doc['layers'])for o in l['objects']};ids={o['id']for l,shift in e.layer_objects(doc['layers'])for o in l['objects']};assert all(not p.startswith('008-')for p in existing);oid=max(ids)+1;maxlayer=max(l['id']for l in doc['layers']);group={'id':maxlayer+1,'name':'008 郊区可行核心 — independent source-ground region','type':'group','visible':True,'offsetx':0,'offsety':0,'layers':[]};grounds=[];objects=[];ts=doc['tilesets'][0]
for s in plan['groundSurfaces']:
 q=[e.project(p)for p in s['polygonMap']];x,y=q[0];mat={'neutral-grass':'G04-suburb-lawn','neutral-soil':'G05-garden-soil'}.get(s['materialId'],s['materialId']);grounds.append({'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':mat,'groundRegionId':'suburb008','color':s.get('color','')})});oid+=1
for b in plan['buildings']+plan['fixtures']+plan['parkedVehicles']:
 aid=b['libraryAssetId'];a=assets[aid];tile=next((t for t in ts['tiles']if e.props(t)['assetId']==aid),None)
 if tile is None:
  tile={'id':max(t['id']for t in ts['tiles'])+1,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':e.properties({'assetId':aid})};ts['tiles'].append(tile)
 w,h=[q*16 for q in a['worldSizeUnits']];au,av=a['anchorUV'];x,y=e.project(b['anchorMap']);objects.append({'id':oid,'name':b['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-au*w,'y':y+(1-av)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'persistentId':b['persistentId'],'assetId':aid,'groundRegionId':'suburb008','parkingSpaceId':b.get('parkingSpaceId','')})});oid+=1
objects.sort(key=lambda o:o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height']);group['layers']=[{'id':maxlayer+2,'name':'008 complete ground and1.5m walks','type':'objectgroup','draworder':'index','objects':grounds},{'id':maxlayer+3,'name':'008 static index order','type':'objectgroup','draworder':'index','objects':objects}];doc['layers'].append(group);ts['tilecount']=len(ts['tiles']);doc['nextlayerid']=maxlayer+4;doc['nextobjectid']=oid;doc['infinite']=True;doc['width']=0;doc['height']=0
for l,shift in e.layer_objects(doc['layers']):
 for o in l['objects']:
  if o['name']in existing:assert o==existing[o['name']]
e.write(e.M,doc);e.write(I/'008-parent-plan-snapshot.json',plan);e.write(I/'008-runtime-subset-plan.json',{'parentOriginalPath':str(P.resolve()),'parentOriginalSHA256':SHA,'rules':['append all13 core instances and17 ground polygons, scale1','old43 instances and85 ground kept exactly','separate finite ground bounds per source region','full source roads deduplicated byID; no navigation edges added'],'activeInstanceIds':[o['name']for o in objects],'activeGroundIds':[s['id']for s in plan['groundSurfaces']],'heldAssetsExcluded':['B07','B09','B10','B11','P02','P09']})
e.write(I/'suburb-increment.json',{'parentPath':str(P.resolve()),'parentOriginalSHA256':SHA,'snapshotPath':str((I/'008-parent-plan-snapshot.json').resolve()),'snapshotSHA256':e.sha(I/'008-parent-plan-snapshot.json'),'derivedSubsetSHA256':e.sha(I/'008-runtime-subset-plan.json'),'oldBaselinePath':str((I/'pre-008-scene.json').resolve()),'oldBaselineSHA256':e.sha(I/'pre-008-scene.json'),'deps':deps,'actualEntryChecks':entries,'oldStaticObjectsPreserved':43,'oldGroundSurfacesPreserved':85,'newStaticInstances':13,'newGroundSurfaces':17,'sourceRoadsFullNodeOrderChecked':True,'doorThresholdExceptionPolicy':'parent permits own-building manual contact0.124/0.192m only; not other source buildings/roads/water'})
print('Appended',len(objects),'objects and',len(grounds),'grounds; old map objects unchanged')
