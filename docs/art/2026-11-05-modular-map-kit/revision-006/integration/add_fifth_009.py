#!/usr/bin/env python3
"""Append screened fifth v2 batch to actual actual146 map; never initialize/reset/replay."""
import sys
sys.dont_write_bytecode=True
import copy,json,math
import neighborhood_export as e
I=e.I;B=I/'batch-009-r5';D=B/'009r5-derived-plan.json'
P=e.R.parent/'revision-009/planning/fit-round-5/fifth-expansion-batch-v2.json'
PS='f2d391dccd4efb32ea0d1868db8f53abbdecf8df3772f617f6bf79ba3a0bf5e1'
assert e.sha(P)==PS
if (I/'round5-009-increment.json').exists():raise ValueError('Round5 exists: export editable map; refuse duplicate import')
plan=e.read(D);assert plan['derivation']['parentOriginalSHA256']==PS
assert e.sha(e.M)==e.sha(B/'pre-r5-neighborhood.tmj') and e.sha(e.V/'assets/scene-layout.json')==e.sha(B/'pre-r5-scene.json')
e.verify_roads(plan);doc=e.read(e.M);old=copy.deepcopy(doc);lid=doc['nextlayerid'];oid=doc['nextobjectid'];ts=doc['tilesets'][0]
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']}
existing={o['name']for l,shift in e.layer_objects(doc['layers'])for o in l['objects']};grounds=[];objects=[]
for s in sorted(plan['groundSurfaces'],key=lambda s:2 if '-walk-'in s['id']else 1 if '-planted-'in s['id']else 0):
 assert s['id']not in existing
 q=[e.project(p)for p in s['polygonMap']];x,y=q[0]
 # Neutral colors are controlled ground fills, not invented native textures.
 mat=({'#a5b990':'G13-r5-garden'}[s['color']]if s['materialId']=='neutral-grass'else s['materialId'])
 grounds.append({'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':mat,'owner':s['owner'],'purpose':s['purpose'],'sourceCarrierIndicesJSON':json.dumps(s.get('sourceCarrierIndices',[])),'originalPlanColor':s.get('color','')})});oid+=1
for b in plan['buildings']:
 assert b['persistentId']not in existing
 a=assets[b['libraryAssetId']];assert b['rotation']==0 and b['anchorUV']==a['anchorUV']
 assert all(math.isclose(b['worldSizeUnits'][k],a['worldSizeUnits'][k]*b['uniformScale'],rel_tol=1e-12)for k in(0,1))
 binding=b['visualReplacementOf'];assert binding['sourceIndices']and binding['sourceDataChanged']is False
 tile=next(t for t in ts['tiles']if e.props(t)['assetId']==b['libraryAssetId']);w,h=[v*16 for v in b['worldSizeUnits']];u,v=a['anchorUV'];x,y=e.project(b['anchorMap'])
 prop={'persistentId':b['persistentId'],'assetId':b['libraryAssetId'],'sourceIndicesJSON':json.dumps(binding['sourceIndices']),'sourcePolygonsMapJSON':json.dumps(binding['sourcePolygonsMap']),'visualReplacementOfJSON':json.dumps(binding,ensure_ascii=False),'sourceDataChanged':False,'sourceNativeSHA256':b['sourceNativeSHA256'],'uniformScaleCandidate':b['uniformScale'],'resolvedFrameScale':1,'navigationStopNodeId':b['navigationStopNodeId'],'stopAssociation':b['stopAssociation'],'entryPixelJSON':json.dumps(b['entryPixel']),'sceneProgramme':b['programme']}
 objects.append({'id':oid,'name':b['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties(prop)});oid+=1
objects.sort(key=lambda o:o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height'])
doc['layers'].append({'id':lid,'name':'009 fifth v2 batch — distinct public/market/tall/U/residential source-bound plots','type':'group','visible':True,'offsetx':0,'offsety':0,'layers':[{'id':lid+1,'name':str(len(grounds))+' screened original grounds, 1.5m door approaches','type':'objectgroup','draworder':'index','objects':grounds},{'id':lid+2,'name':str(len(objects))+' final-world-frame natives, positive scalar applied once','type':'objectgroup','draworder':'index','objects':objects}]})
doc['nextobjectid']=oid;doc['nextlayerid']=lid+3
assert doc['layers'][:-1]==old['layers']and doc['tilesets']==old['tilesets']
e.write(e.M,doc)
e.write(I/'round5-009-increment.json',{'parentPath':str(P.resolve()),'parentOriginalSHA256':PS,'derivedPath':str(D.resolve()),'derivedSHA256':e.sha(D),'preScenePath':str((B/'pre-r5-scene.json').resolve()),'preSceneSHA256':e.sha(B/'pre-r5-scene.json'),'preTiledSHA256':e.sha(B/'pre-r5-neighborhood.tmj'),'actualBaselineCounts':[146,466],'activeInstanceIds':[o['name']for o in objects],'activeSourceIndices':plan['sourceIndices'],'activeGroundIds':[s['id']for s in plan['groundSurfaces']],'newNavigationEdges':0,'newBusinessPOIs':0,'status':'appended-awaiting-real-Cocos-view'})
print('Appended',len(objects),'native modules and',len(grounds),'grounds; all prior Tiled layers exact')
