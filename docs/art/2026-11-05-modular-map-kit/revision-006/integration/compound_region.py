"""Export adapter for exactly the reviewed source125 scene; not bulk scene production."""
import copy,math,sys

def increment(e):
 pending=getattr(e,'_compound_pending',None)
 if pending:return pending
 path=e.I/'compound-pilot-increment.json'
 return e.read(path)if path.exists()else None

def increment_plan(e,plan):
 inc=increment(e)
 if not inc:return plan
 for path,sha in [(inc['parentPath'],inc['parentOriginalSHA256']),(inc['derivedPath'],inc['derivedSHA256']),(inc['preScenePath'],inc['preSceneSHA256'])]:assert e.sha(path)==sha
 new=e.read(inc['derivedPath']);e.verify_roads(new);out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:
   for key in ['nodes','width','direction']:assert r[key]==roads[r['id']][key]
   if 'sourceNodeIds'in roads[r['id']]:assert r['sourceNodeIds']==roads[r['id']]['sourceNodeIds']
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def apply(e,layout,blocks,surfaces,assets,report):
 inc=increment(e)
 if not inc:return
 pipe=e.R.parent/'revision-009/pipeline';sys.path.insert(0,str(pipe))
 from compound_contract import source_accounting,validate_candidate
 new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath']);citypath=e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json';city=e.read(citypath)
 reserved={i for r in e.read(e.R.parent/'revision-009/planning/fit-round-4/usage-contracts.json')['reservations']for i in r['sourceIndices']}
 validate_candidate(new,old,city,e.sha(citypath),reserved)
 assert blocks[:161]==old['blocks']and surfaces[:501]==old['groundSurfaces'],'Pilot changed actual161/501'
 assert len(blocks)==163 and len(surfaces)==506,'Pilot scene must append as a whole'
 roads=layout['roads'];tiledsha=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':tiledsha})
 by={b['persistentId']:b for b in new['buildings']};oldrank={b['persistentId']:b['editorRenderOrder']for b in old['blocks']}
 # Interleave only new modules between existing depth slots; every old value stays
 # fixed, including the market's fractional ranks. Check native frame overlap in QA.
 context=[b for b in old['blocks']if b['persistentId'].startswith('009r4-')or b['persistentId'].startswith('market-life-')];context.sort(key=lambda b:b['editorRenderOrder']);slots={}
 for b in blocks[161:]:
  depth=e.project(b['anchorMap'])[1];pos=next((j for j,x in enumerate(context)if e.project(x['anchorMap'])[1]>depth),len(context));slots.setdefault(pos,[]).append(b)
 for pos,items in slots.items():
  left=context[pos-1]['editorRenderOrder']if pos else context[0]['editorRenderOrder']-1;right=context[pos]['editorRenderOrder']if pos<len(context)else left+1
  for j,b in enumerate(sorted(items,key=lambda b:e.project(b['anchorMap'])[1])):
   item=by[b['persistentId']];b['editorRenderOrder']=left+(right-left)*(j+1)/(len(items)+1)
   b.update({k:copy.deepcopy(item[k])for k in ['sceneId','sourceIndices','visualReplacementOf','footprintPolygonMap','entryPixel','entryMap','sourceNativeSHA256','nativeFootlineEvidence','originalSemanticStatus','scenicRole']});b.update({'sourcePolygonsMap':item['visualReplacementOf']['sourcePolygonsMap'],'uniformScaleCandidate':item['uniformScale'],'resolvedNodeScale':1,'sourceDataChanged':False,'newBusinessPOIs':0,'navigationEdgesAdded':0});oldrank[b['persistentId']]=b['editorRenderOrder']
 for r in report:r['editorRenderOrder']=oldrank[r['persistentId']]
 mapping={s['id']:s for s in new['groundSurfaces']}
 for s in surfaces[501:]:
  input=mapping[s['id']];assert s['materialId']==input['materialId']and all(math.dist(a,b)<1e-8 for a,b in zip(s['polygonMap'],input['polygonMap']))
  for key in ['sceneId','owner','moduleIds','purpose','surfaceClass','thresholdOf']:
   if key in input:s[key]=copy.deepcopy(input[key])
 scene=copy.deepcopy(new['scenes'][0]);scene['runtimeScope']='one local Cocos compound comparison, not navigation/business/user acceptance'
 layout['compoundScenes']=layout.get('compoundScenes',[])+[scene]
 layout['visualReplacements']+=[{'persistentId':b['persistentId'],'sceneId':b['sceneId'],'libraryAssetId':b['libraryAssetId'],'sourceIndices':b['sourceIndices'],'sourcePolygonsMap':b['visualReplacementOf']['sourcePolygonsMap'],'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'footprintPolygonMap':b['footprintPolygonMap'],'nativeFootlineEvidence':copy.deepcopy(b['nativeFootlineEvidence']),'originalSemanticStatus':'unknown','scenicRole':b['scenicRole'],'originalBusinessBindingClaimed':False,'sourceDataChanged':False,'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['buildings']]
 layout['sourceAccounting']=source_accounting(layout)
 def view(name,ids,withOldMarket):
  selected=[b for b in blocks if b['persistentId']in ids];points=[p for s in surfaces if s['id']in mapping or(withOldMarket and(s['id'].startswith('market-life-')or s['id'].startswith('009r4-src-0587-')))for p in s['polygonMap']];ext=[]
  for b in selected:
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for p in points:
   q=e.project(p);ext.append([(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
  lo=[min(q[k]for q in ext)for k in(0,1)];hi=[max(q[k]for q in ext)for k in(0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)]);width=(hi[0]-lo[0])*1.12;height=(hi[1]-lo[1])*1.12;vh=max(height,width/2);vw=vh*2.1;c=e.project(focus);world=[e.unproject([c[0]+16*dx,c[1]+16*dy])for dx in[-vw/2,vw/2]for dy in[-vh/2,vh/2]]+points
  region='compound-ground-'+name;layout['groundRegions'].append({'id':region,'bounds':{'minX':min(q[0]for q in world)-2,'maxX':max(q[0]for q in world)+2,'minY':min(q[1]for q in world)-2,'maxY':max(q[1]for q in world)+2},'surfaceIds':list(mapping),'roadIds':[r['id']for r in roads],'includeAllSceneReferences':True,'maxCanvasEdge':2048,'role':'finite one-source/two-module scene comparison, original full road references'})
  layout['cameraViews'][name]={'focusMap':focus,'fitWidthUnits':width,'fitHeightUnits':height,'screenOffset':[0,0],'activeGroundRegionIds':[region]}
 moduleids=set(by);marketids={b['persistentId']for b in old['blocks']if b['persistentId']=='009r4-src-0587'or b['persistentId'].startswith('market-life-')}
 view('compound-market',moduleids|marketids,True);view('compound-detail',moduleids,False)
 layout['compoundPilotEvidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'baselineSceneSHA256':inc['preSceneSHA256'],'baselineCounts':[161,501,81],'newSceneId':inc['sceneId'],'newSourceUnionCount':1,'newModuleCount':2,'newGroundCount':5,'oldSourceRecordsUnchanged':True,'footlinesManuallyEstimatedNotPrecise':True,'sourceCountUsesUnion':True,'newBusinessPOIs':0,'newNavigationEdges':0,'bulkProductionAuthorized':False,'FPSOrMemoryMeasured':False,'userAccepted':False}

def patch(e):
 if not increment(e):return
 f=e.V/'index.html';s=f.read_text()
 if '?view=compound-market'not in s:s=s.replace('市场候场与休息</a>','市场候场与休息</a> · <a href="?view=compound-market">源125复合院落</a>')
 f.write_text(s)
