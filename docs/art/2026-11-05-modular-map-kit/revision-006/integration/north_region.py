"""009 first source-carrier seed, additive adapter for the existing006 exporter."""
import copy

def increment_plan(e,plan):
 f=e.I/'north-009-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['derivedPath'])==inc['derivedSHA256'];assert e.sha(inc['preScenePath'])==inc['preSceneSHA256']
 new=e.read(inc['derivedPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:assert r==roads[r['id']]
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def add_region(e,layout,blocks,surfaces,assets):
 f=e.I/'north-009-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath']);assert blocks[:57]==old['blocks'],'Old57 placement/order fields changed';assert surfaces[:115]==old['groundSurfaces'],'Old115 ground fields changed'
 # Preserve every old field, view, path, region and ordering; only explicitly append authorized data.
 fresh=copy.deepcopy(layout);layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':fresh['roads'],'tiledSourceSHA256':fresh['tiledSourceSHA256']})
 mapped={b['persistentId']:b for b in new['buildings']}
 for b in blocks[57:]:
  if b['persistentId']in mapped:
   source=mapped[b['persistentId']];binding=source['visualReplacementOf'];b.update({'visualReplacementOf':copy.deepcopy(binding),'sourceIndex':binding['sourceIndex'],'sourcePolygon':binding['sourcePolygonMap'],'sourceSHA256':binding['sourceSHA256'],'sourceNativeSHA256':source['sourceNativeSHA256'],'entryPixel':source['entryPixel'],'entryMap':source['entryMap']})
 ids={b['persistentId']for b in new['buildings']+new['fixtures']};gids=[s['id']for s in new['groundSurfaces']];points=[q for s in new['groundSurfaces']for q in s['polygonMap']]+new['roads'][0]['nodes'][:4]
 bounds={'minX':min(q[0]for q in points)-8,'maxX':max(q[0]for q in points)+12,'minY':min(q[1]for q in points)-9,'maxY':max(q[1]for q in points)+9}
 layout['groundRegions'].append({'id':'north009','bounds':bounds,'surfaceIds':gids,'roadIds':[r['id']for r in new['roads']],'maxCanvasEdge':2048,'role':'finite northern original-road spans0/1/2; full source geometry stored, view clipping only'})
 layout['defaultActiveGroundRegionIds']=[r['id']for r in old['groundRegions']]
 def camera(objectids,groundids,active=['north009'],margin=1.35):
  ex=[]
  for b in blocks:
   if b['persistentId']not in objectids:continue
   a=assets[b['assetId']];p=e.project(b['anchorMap']);x,y=[(p[k]-e.META['editorOrigin'][k])/16 for k in (0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ex.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for s in surfaces:
   if s['id']in groundids:
    for q in s['polygonMap']:
     p=e.project(q);ex.append([(p[k]-e.META['editorOrigin'][k])/16 for k in (0,1)])
  lo=[min(q[k]for q in ex)for k in (0,1)];hi=[max(q[k]for q in ex)for k in (0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in (0,1)])
  return {'focusMap':focus,'fitWidthUnits':max(18,(hi[0]-lo[0])*margin),'fitHeightUnits':max(18,(hi[1]-lo[1])*margin),'screenOffset':[0,-65],'activeGroundRegionIds':active}
 layout['cameraViews']['north']=camera(ids,gids)
 for key,subset in [('north-market',['009-src-0630']),('north-offices',['009-src-0633','009-src-0634']),('north-shop',['009-src-0635'])]:
  subids=set(subset)|{f['persistentId']for f in new['fixtures']if f.get('ownerBuildingId')in subset};sg=[s['id']for s in new['groundSurfaces']if any(s['id'].startswith(p)for p in subset)]
  layout['cameraViews'][key]=camera(subids,sg)
 layout['cameraViews']['north-link']=camera(ids|{b['persistentId']for b in old['blocks']if b['persistentId'].startswith('N1-')},gids,['legacy006','north009'])
 for b in new['buildings']:
  end=b['doorApproach']['endMap'];door=b['entryMap'];focus=[(end[k]+door[k])/2 for k in (0,1)]
  layout['cameraViews']['north-door-'+str(b['visualReplacementOf']['sourceIndex'])]={'focusMap':focus,'fitWidthUnits':18,'fitHeightUnits':16,'screenOffset':[0,0],'activeGroundRegionIds':['north009']}
 layout['visualReplacements']=[{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'sourceIndex':b['visualReplacementOf']['sourceIndex'],'sourcePolygon':b['visualReplacementOf']['sourcePolygonMap'],'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'businessMapping':b['businessNodeMapping'],'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'scope':'only four mapped source carriers; other source targets deferred'}for b in new['buildings']]
 layout['north009Evidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedPlanSHA256':inc['derivedSHA256'],'pre009SceneSHA256':inc['preSceneSHA256'],'sourceCarrierIndices':[630,633,634,635],'existingRawSourcePolygonLayer':False,'newBusinessPOIs':0,'newNavigationEdges':0,'status':'runtime-candidate-requires-actual-visual-review'}

def patch(e):
 if not(e.I/'north-009-increment.json').exists():return
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 marker='d=Math.min(1,3072/Math.max(h,c))'
 if marker in s:s=s.replace(marker,'d=Math.min(1,(this.layout.maxCanvasEdge||3072)/Math.max(h,c))',1)
 marker='bounds:region.bounds,activeGroundRegionId:region.id,'
 if marker in s:s=s.replace(marker,'bounds:region.bounds,maxCanvasEdge:region.maxCanvasEdge,activeGroundRegionId:region.id,',1)
 marker='globalThis.__mapGroundStats=[];for(var region of regions)'
 if marker in s and 'var active=saved.camera.activeGroundRegionIds||saved.defaultActiveGroundRegionIds;'not in s:s=s.replace(marker,'var active=saved.camera.activeGroundRegionIds||saved.defaultActiveGroundRegionIds;regions=active?regions.filter(function(r){return active.includes(r.id)}):regions;this.activeGroundCount=regions.length;globalThis.__mapActiveGroundRegionIds=regions.map(function(r){return r.id});globalThis.__mapGroundStats=[];for(var region of regions)',1)
 s=s.replace('var groundBase=(this.layout.groundRegions||[{}]).length','var groundBase=this.activeGroundCount||(this.layout.groundRegions||[{}]).length')
 marker='"G06-b07-garden":"#a3bc8a"'
 if '"G07-north-garden"'not in s:
  assert s.count(marker)==1;s=s.replace(marker,marker+',"G07-north-garden":"#9db486"')
 f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=north'not in s:s=s.replace('U院门阶</a>','U院门阶</a> · <a href="?view=north">北侧连续街段</a> · <a href="?view=north-market">北侧市场</a> · <a href="?view=north-offices">双办公近景</a> · <a href="?view=north-link">北段与旧区关系</a>')
 f.write_text(s)
