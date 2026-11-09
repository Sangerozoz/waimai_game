#!/usr/bin/env python3
"""Apply explicit four-surface differences and append five real fixtures, without init/reset."""
import sys
sys.dont_write_bytecode=True
import copy
import neighborhood_export as e
I=e.I;B=I/'market-life';P=B/'market-layout.json'
if (I/'market-life-increment.json').exists():raise ValueError('Market life exists: refuse duplicate apply; preserve map and export only')
p=e.read(P);assert e.sha(e.M)==p['baselineTiledSHA256']and e.sha(e.V/'assets/scene-layout.json')==p['baselineSceneSHA256'];doc=e.read(e.M);old=copy.deepcopy(doc);found={}
for layer,shift in e.layer_objects(doc['layers']):
 for o in layer['objects']:found[o['name']]=(o,shift,layer['id'])
for d in p['existingGroundChanges']:
 o,shift,lid=found[d['surfaceId']];before=copy.deepcopy(o);pts=[e.project(q)for q in d['after']['polygonMap']];x,y=pts[0];o['x']=x-shift[0];o['y']=y-shift[1];o['polygon']=[{'x':a-x,'y':b-y}for a,b in pts]
 for prop in o['properties']:
  if prop['name']=='surfaceAssetId':prop['value']=d['after']['materialId']
 d['tiledBefore']={'object':before,'layerId':lid,'groupOffset':shift};d['tiledAfter']={'object':copy.deepcopy(o),'layerId':lid,'groupOffset':shift}
oid=doc['nextobjectid'];lid=doc['nextlayerid'];ts=doc['tilesets'][0];lib={a['id']:a for a in e.read(I/'asset-library.json')['assets']};grounds=[];objects=[]
for s in p['newGroundSurfaces']:
 pts=[e.project(q)for q in s['polygonMap']];x,y=pts[0];grounds.append({'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in pts],'properties':e.properties({'surfaceAssetId':s['materialId'],'owner':s['owner'],'purpose':s['purpose']})});oid+=1
for f in p['newFixtures']:
 a=lib[f['libraryAssetId']];tile=next(t for t in ts['tiles']if e.props(t)['assetId']==a['id']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];x,y=e.project(f['anchorMap']);objects.append({'id':oid,'name':f['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'assetId':a['id'],'persistentId':f['persistentId'],'ownerBuildingId':f['ownerBuildingId'],'purpose':f['purpose'],'sourceNativeSHA256':f['sourceNativeSHA256']})});oid+=1
objects.sort(key=lambda o:o['y']-(1-lib[e.props(o)['assetId']]['anchorUV'][1])*o['height'])
doc['layers'].append({'id':lid,'name':'0587 market entrance waiting, tree-shaded seat and collection corner','type':'group','visible':True,'offsetx':0,'offsety':0,'layers':[{'id':lid+1,'name':'four finite connected landings/branches, old1.5m walk not overdrawn','type':'objectgroup','draworder':'index','objects':grounds},{'id':lid+2,'name':'five native fixtures, original scale/direction','type':'objectgroup','draworder':'index','objects':objects}]});doc['nextlayerid']=lid+3;doc['nextobjectid']=oid
e.write(B/'tiled-four-surface-diff.json',p['existingGroundChanges']);e.write(e.M,doc)
e.write(I/'market-life-increment.json',{'layoutPath':str(P.resolve()),'layoutSHA256':e.sha(P),'preScenePath':str((B/'pre-market-scene.json').resolve()),'preSceneSHA256':p['baselineSceneSHA256'],'preTiledSHA256':p['baselineTiledSHA256'],'actualBaselineCounts':[156,497],'modifiedGroundIds':[d['surfaceId']for d in p['existingGroundChanges']],'newGroundIds':[s['id']for s in p['newGroundSurfaces']],'newFixtureIds':[f['persistentId']for f in p['newFixtures']],'authority':'parent explicit0587 four-surface art permission, immutable1.5m door route and old156 protected','newBusinessPOIs':0,'newNavigationEdges':0,'status':'applied-awaiting-real-Cocos-market-view'})
print('Applied4 authorized ground changes, appended5 fixtures and4 new grounds; old sprites/other grounds unchanged')
