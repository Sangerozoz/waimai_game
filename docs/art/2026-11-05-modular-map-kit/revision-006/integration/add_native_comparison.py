#!/usr/bin/env python3
"""Append the explicit three-native comparison to the current143 map, without reinitializing."""
import sys
sys.dont_write_bytecode=True
import copy,json,shutil
from pathlib import Path
import neighborhood_export as e
I=e.I;B=I/'native-comparison';P=B/'comparison-plan.json';plan=e.read(P)
if (I/'native-comparison-increment.json').exists():raise ValueError('Comparison exists: refuse duplicate apply; export editable map only')
assert e.sha(e.M)==e.sha(B/'pre-comparison-neighborhood.tmj')and e.sha(e.V/'assets/scene-layout.json')==plan['baselineSceneSHA256']
lib=e.read(I/'asset-library.json');cal=e.read(I/'asset-calibration.json')
assert lib==e.read(B/'pre-comparison-library.json')and cal==e.read(B/'pre-comparison-calibration.json')
for a in plan['assets']:
 assert a['id']not in{a['id']for a in lib['assets']}
 src=e.R.parent/'revision-009/art-expansion/native'/(a['id']+'-001')/a['file'];assert e.sha(src)==a['sha256'];shutil.copyfile(src,I/'assets'/a['file']);lib['assets'].append(a)
cal['assets']+=plan['calibration'];e.write(I/'asset-library.json',lib);e.write(I/'asset-calibration.json',cal)
doc=e.read(e.M);old=copy.deepcopy(doc);ts=doc['tilesets'][0];tileid=max(t['id']for t in ts['tiles'])+1
for a in plan['assets']:
 ts['tiles'].append({'id':tileid,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':e.properties({'assetId':a['id']})});tileid+=1
ts['tilecount']=len(ts['tiles']);oid=doc['nextobjectid'];lid=doc['nextlayerid'];grounds=[];objects=[];by={a['id']:a for a in lib['assets']}
for s in sorted(plan['newGrounds'],key=lambda s:1 if '-walk-'in s['id']else 0):
 q=[e.project(p)for p in s['polygonMap']];x,y=q[0];grounds.append({'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':s['materialId'],'owner':s['owner'],'purpose':s['purpose']})});oid+=1
for item in plan['instances']:
 a=by[item['libraryAssetId']];tile=next(t for t in ts['tiles']if e.props(t)['assetId']==a['id']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];x,y=e.project(item['anchorMap']);props={'persistentId':item['persistentId'],'assetId':a['id'],'sourceNativeSHA256':a['runtimeDerivation']['sourceSHA256'],'comparisonOnly':True}
 if 'visualReplacementOf'in item:props.update({'visualReplacementOfJSON':json.dumps(item['visualReplacementOf']),'sourceIndicesJSON':json.dumps(item['visualReplacementOf']['sourceIndices']),'entryPixelJSON':json.dumps(item['entryPixel'])})
 else:props.update({'ownerBuildingId':item['ownerBuildingId'],'rootOriginMeasured':False})
 objects.append({'id':oid,'name':item['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties(props)});oid+=1
objects.sort(key=lambda o:o['y']-(1-by[e.props(o)['assetId']]['anchorUV'][1])*o['height'])
doc['layers'].append({'id':lid,'name':'009 native low-building and inferred-root shrub comparison — no business binding','type':'group','offsetx':0,'offsety':0,'visible':True,'layers':[{'id':lid+1,'name':'finite new source yards and actual step connections','type':'objectgroup','draworder':'index','objects':grounds},{'id':lid+2,'name':'three individual new native comparisons, no image transforms','type':'objectgroup','draworder':'index','objects':objects}]});doc['nextobjectid']=oid;doc['nextlayerid']=lid+3
assert doc['layers'][:-1]==old['layers']and ts['tiles'][:len(old['tilesets'][0]['tiles'])]==old['tilesets'][0]['tiles']
e.write(e.M,doc)
e.write(I/'native-comparison-increment.json',{'planPath':str(P.resolve()),'planSHA256':e.sha(P),'preScenePath':str((B/'pre-comparison-scene.json').resolve()),'preSceneSHA256':plan['baselineSceneSHA256'],'preTiledSHA256':plan['baselineTiledSHA256'],'actualBaselineCounts':[143,462],'activeInstanceIds':[i['persistentId']for i in plan['instances']],'activeGroundIds':[s['id']for s in plan['newGrounds']],'authority':'parent finite B12/B13 one legal source each, T05 one-or-two garden comparisons; no old ground changes','newBusinessPOIs':0,'newNavigationEdges':0,'status':'appended-awaiting-real-Cocos-comparison'})
print('Appended',len(objects),'new native candidates,',len(grounds),'new finite grounds; existing143/462/tiles exact')
