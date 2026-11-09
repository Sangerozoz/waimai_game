#!/usr/bin/env python3
"""Append the fixed009 seed once to the existing editable map. Refuses reset/replay."""
import sys
sys.dont_write_bytecode=True
import copy
import neighborhood_export as e
I=e.I;B=I/'batch-009';derived=B/'009-derived-plan.json';P=e.R.parent/'revision-009/planning/first-expansion-batch.json';PS='9360a09116a099e6df54fd2848ee49bd3b39ab7c90d0b5273ba0bfb4089cc9e6'
assert e.sha(P)==PS
if (I/'north-009-increment.json').exists():raise ValueError('009 already appended: preserve user-edited map; export only')
plan=e.read(derived);assert plan['derivation']['parentOriginalSHA256']==PS;e.verify_roads(plan);assert e.sha(e.M)==e.sha(B/'pre-009-neighborhood.tmj')
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};doc=e.read(e.M);old=copy.deepcopy(doc);existing={o['name']:o for l,shift in e.layer_objects(doc['layers'])for o in l['objects']};assert not any(i.startswith('009-')for i in existing);lid=doc['nextlayerid'];oid=doc['nextobjectid'];grounds=[];objects=[];ts=doc['tilesets'][0]
for s in plan['groundSurfaces']:
 q=[e.project(p)for p in s['polygonMap']];x,y=q[0];mat='G07-north-garden'if s['materialId']=='neutral-grass'else s['materialId'];grounds.append({'id':oid,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':mat,'groundRegionId':'north009','purpose':s['purpose'],'ownerBuildingId':s.get('ownerBuildingId','')})});oid+=1
for b in plan['buildings']+plan['fixtures']:
 aid=b['libraryAssetId'];a=assets[aid];assert 'hold'not in a.get('availability','');tile=next(t for t in ts['tiles']if e.props(t)['assetId']==aid);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];x,y=e.project(b['anchorMap']);p={'persistentId':b['persistentId'],'assetId':aid,'groundRegionId':'north009'}
 if 'visualReplacementOf'in b:p.update({'visualReplacementOfJSON':__import__('json').dumps(b['visualReplacementOf'],ensure_ascii=False),'sourceIndex':b['visualReplacementOf']['sourceIndex'],'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixelJSON':__import__('json').dumps(b['entryPixel'])})
 objects.append({'id':oid,'name':b['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties(p)});oid+=1
objects.sort(key=lambda o:o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height'])
doc['layers'].append({'id':lid,'name':'009 north original source-carrier seed — no business remap','type':'group','visible':True,'offsetx':0,'offsety':0,'layers':[{'id':lid+1,'name':'009 connected pedestrian grounds then controlled garden borders','type':'objectgroup','draworder':'index','objects':grounds},{'id':lid+2,'name':'009 native buildings and limited street fixtures — static index','type':'objectgroup','draworder':'index','objects':objects}]});doc['nextlayerid']=lid+3;doc['nextobjectid']=oid
assert doc['layers'][:-1]==old['layers'] and doc['tilesets']==old['tilesets']
e.write(e.M,doc);e.write(I/'north-009-increment.json',{'parentPath':str(P.resolve()),'parentOriginalSHA256':PS,'derivedPath':str(derived.resolve()),'derivedSHA256':e.sha(derived),'preScenePath':str((B/'pre-009-scene.json').resolve()),'preSceneSHA256':e.sha(B/'pre-009-scene.json'),'preTiledSHA256':e.sha(B/'pre-009-neighborhood.tmj'),'activeInstanceIds':[o['name']for o in objects],'activeGroundIds':[s['id']for s in plan['groundSurfaces']],'sourceIndices':[630,633,634,635],'old57ObjectsAnd115GroundsPreserved':True,'newNavigationEdges':0,'newBusinessPOIs':0,'status':'appended-awaiting-export-and-real-view'})
print('Appended',len(objects),'static instances and',len(grounds),'ground surfaces; old map layers/tilesets unchanged')
