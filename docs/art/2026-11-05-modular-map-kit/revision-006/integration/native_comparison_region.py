"""Three explicitly admitted comparison instances, preserving the whole actual143 baseline."""
import copy,math

def increment_plan(e,plan):
 f=e.I/'native-comparison-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['planPath'])==inc['planSHA256'];new=e.read(inc['planPath']);out=copy.deepcopy(plan)
 city=e.read(e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json');nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};by={r['id']:r for r in out['roads']}
 for id in {b['sourceRoadId']for b in new['instances']if 'sourceRoadId'in b}:
  source=next(r for r in city['roads']if r['id']==id)
  if id not in by:by[id]={'id':id,'nodes':[nodes[n]for n in source['nodes']],'sourceNodeIds':source['nodes'],'width':source['width'],'direction':source['direction']}
 out['roads']=list(by.values());return out

def apply(e,layout,blocks,surfaces,assets,report):
 f=e.I/'native-comparison-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['planPath']);old=e.read(inc['preScenePath']);assert blocks[:143]==old['blocks']
 from market_life import approved_prefix
 approved_prefix(e,surfaces,old['groundSurfaces'])
 roads=layout['roads'];sha=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':sha})
 by={b['persistentId']:b for b in new['instances']};ranks={b['persistentId']:b['editorRenderOrder']for b in old['blocks']}
 for j,b in enumerate(blocks[143:]):
  if b['persistentId']not in by:continue
  item=by[b['persistentId']];b['editorRenderOrder']=143+j
  if item['libraryAssetId']=='T05':
   nearby=[x for x in old['blocks']if math.dist(x['anchorMap'],b['anchorMap'])<25];depth=e.project(b['anchorMap'])[1];before=[x['editorRenderOrder']for x in nearby if e.project(x['anchorMap'])[1]<depth];after=[x['editorRenderOrder']for x in nearby if e.project(x['anchorMap'])[1]>depth];lo,hi=max(before),min(after);assert lo<hi;b['editorRenderOrder']=(lo+hi)/2
   b.update({'ownerBuildingId':item['ownerBuildingId'],'rootOriginMeasured':False,'rootInferenceUncertaintyPixels':70,'groundContactPolygonMap':item['groundContactPolygonMap']})
  else:
   b.update({k:copy.deepcopy(item[k])for k in ['visualReplacementOf','entryMap','entryPixel','stepFrontMap','stepFrontPixel','footprintPolygonMap','landUseIntent','sourceNativeSHA256']});b.update({'sourceIndices':item['visualReplacementOf']['sourceIndices'],'sourcePolygonsMap':item['visualReplacementOf']['sourcePolygonsMap'],'sourceDataChanged':False,'navigationEdgesAdded':0,'newBusinessPOIs':0})
  b.update({'comparisonOnly':True,'sceneProgramme':item['sceneProgramme']});ranks[b['persistentId']]=b['editorRenderOrder']
 for row in report:
  if row['persistentId']in ranks:row['editorRenderOrder']=ranks[row['persistentId']]
 layout['visualReplacements']+=[{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceIndices':b['visualReplacementOf']['sourceIndices'],'sourcePolygonsMap':b['visualReplacementOf']['sourcePolygonsMap'],'visualReplacementOf':b['visualReplacementOf'],'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'comparisonOnly':True,'sourceDataChanged':False,'originalBusinessBindingClaimed':False,'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['instances']if 'visualReplacementOf'in b]
 def view(name,ids,points,focus=None,width=None,height=None):
  selected=[b for b in blocks if b['persistentId']in ids];ext=[]
  for b in selected:
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   p=e.project(q);ext.append([(p[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
  lo=[min(p[k]for p in ext)for k in(0,1)];hi=[max(p[k]for p in ext)for k in(0,1)]
  center=focus or e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)])
  # Derive finite map bounds from all actually selected projected frame corners.
  world=[e.unproject([e.META['editorOrigin'][0]+16*x,e.META['editorOrigin'][1]+16*y])for x in [lo[0],hi[0]]for y in[lo[1],hi[1]]]+points
  bounds={'minX':min(p[0]for p in world)-8,'maxX':max(p[0]for p in world)+8,'minY':min(p[1]for p in world)-8,'maxY':max(p[1]for p in world)+8}
  layout['groundRegions'].append({'id':name,'bounds':bounds,'surfaceIds':[s['id']for s in new['newGrounds']],'roadIds':[r['id']for r in roads],'includeAllSceneReferences':True,'maxCanvasEdge':2048,'role':'finite actual native comparison, prior geometry read-only'})
  layout['cameraViews'][name]={'focusMap':center,'fitWidthUnits':width or max(20,(hi[0]-lo[0])*1.15),'fitHeightUnits':height or max(20,(hi[1]-lo[1])*1.15),'screenOffset':[0,0],'activeGroundRegionIds':[name]}
 ids={b['libraryAssetId']:b['persistentId']for b in new['instances']}
 if 'B12'in ids:
  points=[p for s in new['newGrounds']if s['owner']==ids['B12']for p in s['polygonMap']];view('native-low',{ids['B12'],'009r4-src-1730'},points)
 if 'B13'in ids:view('native-shop',{ids['B13']},[p for s in new['newGrounds']if s['owner']==ids['B13']for p in s['polygonMap']])
 if 'T05'in ids:view('native-shrub',{'009r3-src-0612','life-central-612-tree','life-central-612-bench',ids['T05']},[],focus=[-1250.7,205.8],width=23,height=18)
 layout['nativeComparisonEvidence']={'baselineSceneSHA256':inc['preSceneSHA256'],'baselineCounts':[143,462],'planSHA256':inc['planSHA256'],'instanceIds':inc['activeInstanceIds'],'newGroundIds':inc['activeGroundIds'],'B13CleanUsesOriginalCropMapping':True,'T05RootMeasured':False,'comparisonOnly':True,'newBusinessPOIs':0,'newNavigationEdges':0,'FPSOrMemoryMeasured':False}

def patch(e):
 if not(e.I/'native-comparison-increment.json').exists():return
 f=e.V/'index.html';s=f.read_text()
 if '?view=native-low'not in s:s=s.replace('住宅院落</a>','住宅院落</a> · <a href="?view=native-low">低住宅比较</a> · <a href="?view=native-shop">低街铺比较</a> · <a href="?view=native-shrub">灌木层次</a>')
 f.write_text(s)
