"""Frozen fifth-v2 market/housing infill on actual146; original U void is never filled."""
import copy

def increment_plan(e,plan):
 f=e.I/'round5-009-increment.json'
 if not f.exists():return plan
 inc=e.read(f)
 for path,h in [(inc['parentPath'],inc['parentOriginalSHA256']),(inc['derivedPath'],inc['derivedSHA256']),(inc['preScenePath'],inc['preSceneSHA256'])]:assert e.sha(path)==h
 new=e.read(inc['derivedPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:
   for key in ['nodes','width','direction']:assert r[key]==roads[r['id']][key]
   if 'sourceNodeIds'in r and 'sourceNodeIds'in roads[r['id']]:assert r['sourceNodeIds']==roads[r['id']]['sourceNodeIds']
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def add_regions(e,layout,blocks,surfaces,assets,report):
 f=e.I/'round5-009-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath'])
 assert blocks[:146]==old['blocks'],'Latest146 block metadata/transforms/order changed'
 from market_life import approved_prefix
 approved_prefix(e,surfaces,old['groundSurfaces'])
 roads=layout['roads'];sha=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':sha})
 mapped={b['persistentId']:b for b in new['buildings']};ranks={b['persistentId']:b['editorRenderOrder']for b in old['blocks']}
 for j,b in enumerate(blocks[146:]):
  if b['persistentId']not in mapped:continue
  item=mapped[b['persistentId']];b['editorRenderOrder']=146+j;binding=item['visualReplacementOf']
  b.update({'visualReplacementOf':copy.deepcopy(binding),'sourceIndices':copy.deepcopy(binding['sourceIndices']),'sourcePolygonsMap':copy.deepcopy(binding['sourcePolygonsMap']),'sourceSHA256':binding['sourceSHA256'],'sourceDataChanged':False,'sourceNativeSHA256':item['sourceNativeSHA256'],'uniformScaleCandidate':item['uniformScale'],'entryPixel':item['entryPixel'],'entryMap':item['entryMap'],'navigationStopNodeId':item['navigationStopNodeId'],'navigationStopOriginalWorld':item['navigationStopOriginalWorld'],'stopAssociation':item['stopAssociation'],'sceneProgramme':item['programme'],'regionId':item['regionId'],'landUseIntent':item['landUseIntent'],'newBusinessPOIs':0,'navigationEdgesAdded':0})
  if item['libraryAssetId']=='B07':b.update({'courtyardVoidPolygonMap':copy.deepcopy(item['courtyardVoidPolygonMap']),'trueDoorControls':[11,12],'nativeStepFrontPixel':item['nativeStepFrontPixel'],'rejectedOldDoorUsed':False})
  ranks[b['persistentId']]=b['editorRenderOrder']
 for row in report:
  if row['persistentId']in ranks:row['editorRenderOrder']=ranks[row['persistentId']]
 def view(name,ids,margin=1.12):
  selected=[b for b in blocks if b['persistentId']in ids];grounds=[s for s in surfaces if any(s['id'].startswith(id+'-')for id in ids)];points=[q for s in grounds for q in s['polygonMap']];ext=[]
  for b in selected:
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   a=e.project(q);ext.append([(a[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
  assert selected and points
  lo=[min(q[k]for q in ext)for k in(0,1)];hi=[max(q[k]for q in ext)for k in(0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)])
  bounds={'minX':min(q[0]for q in points)-10,'maxX':max(q[0]for q in points)+10,'minY':min(q[1]for q in points)-10,'maxY':max(q[1]for q in points)+10}
  # Cover the observed landscape viewport, not just the selected ground polygons;
  # otherwise fixed neighbor sprites at the edge appear beyond their clipped yards.
  fitw=max(22,(hi[0]-lo[0])*margin);fith=max(22,(hi[1]-lo[1])*margin);vh=max(fith,fitw/2);vw=vh*2.1;center=e.project(focus)
  visible=[e.unproject([center[0]+16*dx,center[1]+16*dy])for dx in[-vw/2,vw/2]for dy in[-vh/2,vh/2]]
  for key,k,fn in [('minX',0,min),('maxX',0,max),('minY',1,min),('maxY',1,max)]:bounds[key]=fn(bounds[key],fn(q[k]for q in visible))
  layout['groundRegions'].append({'id':name,'bounds':bounds,'surfaceIds':[s['id']for s in grounds],'roadIds':[r['id']for r in roads],'includeAllSceneReferences':True,'maxCanvasEdge':2048,'role':'one local market or residential neighborhood; no cross-district county canvas'})
  layout['cameraViews'][name]={'focusMap':focus,'fitWidthUnits':fitw,'fitHeightUnits':fith,'screenOffset':[0,0],'activeGroundRegionIds':[name]}
 market={b['persistentId']for b in new['buildings']if b['regionId']=='market0587'}|{'009r4-src-0587'}
 view('r5-market',market)
 housing={'009r5-src-1423','009r5-src-1363','009r5-src-1364','009r5-src-1738','009r4-src-1739'}
 view('r5-housing',housing)
 view('r5-housing-front',{'009r5-src-1359','009r5-src-1738','009r4-src-1735','009r4-src-1736','009r4-src-1737','009r4-src-1739'})
 view('r5-1423',{'009r5-src-1423'},1.12)
 layout['round5Scenes']=copy.deepcopy(new['scenes'])
 layout['round5InputRoadRecords']=copy.deepcopy(new['roads'])
 layout['visualReplacements']+=[{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceIndices':b['visualReplacementOf']['sourceIndices'],'sourcePolygonsMap':b['visualReplacementOf']['sourcePolygonsMap'],'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'navigationStopNodeId':b['navigationStopNodeId'],'navigationStopOriginalWorld':b['navigationStopOriginalWorld'],'associationScope':b['stopAssociation'],'originalBusinessBindingClaimed':False,'sourceDataChanged':False,'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['buildings']]
 layout['round5Evidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'actualBaselineSceneSHA256':inc['preSceneSHA256'],'actualBaselineCounts':[146,466],'admittedBuildings':len(new['buildings']),'admittedGrounds':len(new['groundSurfaces']),'schemaAdaptation':['root scenes retained as round5Scenes, no sourceMappings fallback','building programme explicitly exported as sceneProgramme','resolved world frame and nodeScale1; scalar is provenance only','neutral-grass rendered existing controlled-color mechanism as G13-r5-garden'],'U1423PartialCourtArea':12,'U1423DoesNotFillWholeVoid':True,'newBusinessPOIs':0,'newNavigationEdges':0,'newNativeComparisonInstances':0,'newPNGFiles':0,'FPSOrMemoryMeasured':False}

def patch(e):
 if not(e.I/'round5-009-increment.json').exists():return
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 if '"G13-r5-garden"'not in s:
  marker='"G10-r3-courtyard":"#a5bb8c"';assert s.count(marker)==1;s=s.replace(marker,marker+',"G13-r5-garden":"#a5b990"')
 f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=r5-market'not in s:s=s.replace('灌木层次</a>','灌木层次</a> · <a href="?view=r5-market">第五批市场邻区</a> · <a href="?view=r5-housing">第五批住宅邻区</a>')
 f.write_text(s)
