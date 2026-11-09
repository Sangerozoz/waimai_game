"""Fourth batch: actual103 baseline protection, source bindings, finite region references."""
import copy,math

def increment_plan(e,plan):
 f=e.I/'round4-009-increment.json'
 if not f.exists():return plan
 inc=e.read(f)
 for path,sha in [(inc['parentPath'],inc['parentOriginalSHA256']),(inc['derivedPath'],inc['derivedSHA256']),(inc['preScenePath'],inc['preSceneSHA256'])]:assert e.sha(path)==sha
 new=e.read(inc['derivedPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:assert r==roads[r['id']]
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def add_regions(e,layout,blocks,surfaces,assets,report):
 f=e.I/'round4-009-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath'])
 assert blocks[:103]==old['blocks'],'Life-street103 block fields changed'
 assert surfaces[:265]==old['groundSurfaces'],'Life-street265 grounds changed'
 roads=layout['roads'];ts=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':ts})
 mapped={b['persistentId']:b for b in new['buildings']};ranks={b['persistentId']:b['editorRenderOrder']for b in old['blocks']}
 for j,b in enumerate(blocks[103:]):
  if b['persistentId']not in mapped:continue
  item=mapped[b['persistentId']];binding=item['visualReplacementOf'];b['editorRenderOrder']=103+j;ranks[b['persistentId']]=103+j
  b.update({'visualReplacementOf':copy.deepcopy(binding),'sourceIndices':copy.deepcopy(binding['sourceIndices']),'sourcePolygonsMap':copy.deepcopy(binding['sourcePolygonsMap']),'sourceSHA256':binding['sourceSHA256'],'sourceDataChanged':False,'sourceNativeSHA256':item['sourceNativeSHA256'],'uniformScaleCandidate':item['uniformScale'],'entryPixel':item['entryPixel'],'entryMap':item['entryMap'],'navigationStopNodeId':item['navigationStopNodeId'],'navigationStopOriginalWorld':item['navigationStopOriginalWorld'],'stopAssociation':item['stopAssociation'],'sceneProgramme':item['sceneProgramme'],'landUseIntent':item['landUseIntent'],'newBusinessPOIs':0,'navigationEdgesAdded':0})
  if item['libraryAssetId']=='B07':b.update({'courtyardVoidPolygonMap':copy.deepcopy(item['courtyardVoidPolygonMap']),'trueDoorControls':[11,12],'rejectedOldDoorUsed':False})
 for row in report:
  if row['persistentId']in ranks:row['editorRenderOrder']=ranks[row['persistentId']]

 def addview(name,ids,cap=2048,margin=1.15):
  selected=[b for b in blocks if b['persistentId']in ids];grounds=[s for s in new['groundSurfaces']if s['owner']in ids];points=[q for s in grounds for q in s['polygonMap']];ext=[]
  assert selected and points
  for b in selected:
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   p=e.project(q);ext.append([(p[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
  bounds={'minX':min(q[0]for q in points)-12,'maxX':max(q[0]for q in points)+12,'minY':min(q[1]for q in points)-12,'maxY':max(q[1]for q in points)+12}
  layout['groundRegions'].append({'id':name,'bounds':bounds,'surfaceIds':[s['id']for s in grounds],'roadIds':[r['id']for r in new['roads']],'maxCanvasEdge':cap,'includeAllSceneReferences':True,'role':'finite fourth-batch local source-bound region; no county-wide baked image'})
  lo=[min(q[k]for q in ext)for k in(0,1)];hi=[max(q[k]for q in ext)for k in(0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)])
  layout['cameraViews'][name]={'focusMap':focus,'fitWidthUnits':max(24,(hi[0]-lo[0])*margin),'fitHeightUnits':max(24,(hi[1]-lo[1])*margin),'screenOffset':[0,-65],'activeGroundRegionIds':[name]}
 # One bounded relationship frame, plus three useful close-ups. Other sources
 # remain individually reachable by a finite query camera, not forty image tests.
 views={'r4-relations':['1515','1513','1511','0176','0131'],'r4-tall-u':['0176','0131'],'r4-market':['0587'],'r4-residential':['1739','1737','1736','1735']}
 for name,ids in views.items():addview(name,{'009r4-src-'+id for id in ids},1536 if name=='r4-relations'else 2048,1.16)
 layout['cameraViews']['r4-relations']['screenOffset']=[0,0]
 for b in new['buildings']:addview('r4-'+b['persistentId'][-4:],{b['persistentId']},1536,1.2)
 layout['round4SourceMappings']=copy.deepcopy(new['sourceMappings'])
 layout['visualReplacements']+=[{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceIndices':copy.deepcopy(b['visualReplacementOf']['sourceIndices']),'sourcePolygonsMap':copy.deepcopy(b['visualReplacementOf']['sourcePolygonsMap']),'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'navigationStopNodeId':b['navigationStopNodeId'],'navigationStopOriginalWorld':b['navigationStopOriginalWorld'],'associationScope':b['stopAssociation'],'sourceDataChanged':False,'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['buildings']]
 layout['round4Evidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'actualPreSceneSHA256':inc['preSceneSHA256'],'actualProtectedCount':[103,265],'sourceIndices':new['sourceIndices'],'canonicalScaleContract':'resolved worldSizeUnits already canonical*positive scalar once; runtime nodeScale1; anchorUV/PPU fixed','uniqueAdmittedSources':new['uniqueSourceCount'],'admittedVisualModules':len(new['buildings']),'admittedGrounds':len(new['groundSurfaces']),'newBusinessPOIs':0,'navigationEdgesAdded':0,'navigationAssociationNotOriginalBinding':True,'nativeGroundIsManuallyEstimated':True,'groundOrderDerivation':'new bases first, planted pockets second, original 1.5m door walks last, original roads above all ground; old265 untouched','limitedGroundMaximumCanvasEdge':2048,'overviewMaximumCanvasEdge':1536,'FPSOrMemoryMeasured':False}

def patch(e):
 if not(e.I/'round4-009-increment.json').exists():return
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 for name,color in [('G11-r4-courtyard','#9fb788'),('G12-r4-planted','#a7bc92')]:
  if '"'+name+'"'not in s:
   marker='"G10-r3-courtyard":"#a5bb8c"';assert s.count(marker)==1;s=s.replace(marker,marker+',"'+name+'":"'+color+'"')
 f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=r4-relations'not in s:s=s.replace('商服休憩细节</a>','商服休憩细节</a> · <a href="?view=r4-relations">第四批局部关系</a> · <a href="?view=r4-tall-u">高楼与U院</a> · <a href="?view=r4-market">市场门前</a> · <a href="?view=r4-residential">住宅院落</a>')
 f.write_text(s)
