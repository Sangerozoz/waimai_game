#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import copy,json
import neighborhood_export as e
I=e.I;B=I/'central-life';P=B/'life-layout.json'
if (I/'central-life-increment.json').exists():raise ValueError('Life increment already exists; preserve editable map and export only')
plan=e.read(P);assert e.sha(e.M)==plan['baselineTiledSHA256'];doc=e.read(e.M);before=copy.deepcopy(doc);allrows={o['name']:o for l,sh in e.layer_objects(doc['layers'])for o in l['objects']};lib={a['id']:a for a in e.read(I/'asset-library.json')['assets']};ts=doc['tilesets'][0];oid=doc['nextobjectid']
for diff in plan['existingGroundChanges']:
 o=allrows[diff['surfaceId']];assert e.props(o)['surfaceAssetId']==diff['before']['materialId'];assert '-walk-'not in o['name']
 for p in o['properties']:
  if p['name']=='surfaceAssetId':p['value']=diff['after']['materialId']
 if diff['after']['polygonMap']!=diff['before']['polygonMap']:
  coords=[e.project(q)for q in diff['after']['polygonMap']];x,y=coords[0];o['x']=x;o['y']=y;o['polygon']=[{'x':a-x,'y':b-y}for a,b in coords]
groundlayer=next(l for l,sh in e.layer_objects(doc['layers'])if any(o['name']=='009r3-src-0593-walk-0'for o in l['objects']));spritelayer=next(l for l,sh in e.layer_objects(doc['layers'])if any(o['name']=='009r3-src-0593'for o in l['objects']));ground_before=[];ground_after=[]
for diff in plan['existingGroundChanges']:
 if 'drawPlacement'not in diff:continue
 o=allrows[diff['surfaceId']];groundlayer['objects'].remove(o);walk=diff['surfaceId'].split('-carrier-court-')[0]+'-walk-0';pos=next(j for j,p in enumerate(groundlayer['objects'])if p['name']==walk);groundlayer['objects'].insert(pos,o)
for s in plan['newGroundSurfaces']:
 assert s['id']not in allrows;points=[e.project(p)for p in s['polygonMap']];x,y=points[0];o={'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in points],'properties':e.properties({'surfaceAssetId':s['materialId'],'owner':s['owner'],'purpose':s['purpose'],'lifeGround':True})};oid+=1
 (ground_before if s['tiledInsertion']=='before-third-grounds'else ground_after).append(o)
groundlayer['objects']=ground_before+groundlayer['objects']+ground_after
newobjects=[]
for f in plan['newFixtures']:
 assert f['id']not in allrows;a=lib[f['libraryAssetId']];tile=next(t for t in ts['tiles']if e.props(t)['assetId']==a['id']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];x,y=e.project(f['anchorMap']);newobjects.append({'id':oid,'name':f['id'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'persistentId':f['id'],'assetId':a['id'],'owner':f['owner'],'purpose':f['purpose'],'lifeGround':True,'contextualAdmission':f.get('contextualAdmission','existing admitted local comparison asset')})});oid+=1
# Insert new rows by actual ground depth without changing any old row's relative order.
def depth(o):return o['y']-(1-lib[e.props(o)['assetId']]['anchorUV'][1])*o['height']
for new in sorted(newobjects,key=depth):
 pos=next((j for j,old in enumerate(spritelayer['objects'])if depth(old)>depth(new)),len(spritelayer['objects']));spritelayer['objects'].insert(pos,new)
doc['nextobjectid']=oid
current={o['name']:o for l,sh in e.layer_objects(doc['layers'])for o in l['objects']};allowed={d['surfaceId']for d in plan['existingGroundChanges']};originalnames={o['name']for l,sh in e.layer_objects(before['layers'])for o in l['objects']}
for l,sh in e.layer_objects(before['layers']):
 for o in l['objects']:
  if o['name']not in allowed:assert current[o['name']]==o,('Original object altered',o['name'])
oldorder=[o['name']for l,sh in e.layer_objects(before['layers'])for o in l['objects']if'gid'in o];neworder=[o['name']for l,sh in e.layer_objects(doc['layers'])for o in l['objects']if'gid'in o and o['name']in originalnames];assert oldorder==neworder;e.write(e.M,doc)
e.write(I/'central-life-increment.json',{'layoutPath':str(P.resolve()),'layoutSHA256':e.sha(P),'preScenePath':str((B/'pre-life-scene.json').resolve()),'preSceneSHA256':e.sha(B/'pre-life-scene.json'),'preTiledSHA256':e.sha(B/'pre-life-neighborhood.tmj'),'authority':'parent explicitly authorized selected third-batch ground art edits and existing admitted local props; no new source-plan approval claimed','selectedThirdBatchBuildingIds':plan['selectedThirdBatchBuildingIds'],'modifiedGroundIds':[d['surfaceId']for d in plan['existingGroundChanges']],'newGroundIds':[s['id']for s in plan['newGroundSurfaces']],'newFixtureIds':[f['id']for f in plan['newFixtures']],'oldSpriteRelativeOrderPreserved':True,'originalWalksUnchanged':True,'protectedFirst74And164':True})
print('Applied selected material edits',len(allowed),'new props',len(newobjects),'new floors',len(ground_before)+len(ground_after),'old94 relative order unchanged')
