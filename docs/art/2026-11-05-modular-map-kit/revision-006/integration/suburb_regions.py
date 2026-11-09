"""Additive region data and derived Cocos patch. No old object writes."""
import copy
from pathlib import Path

def increment_plan(e,plan):
 f=e.I/'suburb-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['snapshotPath'])==inc['snapshotSHA256'];assert e.sha(e.I/'008-runtime-subset-plan.json')==inc['derivedSubsetSHA256'];assert e.sha(inc['oldBaselinePath'])==inc['oldBaselineSHA256'];new=e.read(inc['snapshotPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);by={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in by:assert r['nodes']==by[r['id']]['nodes']and r['width']==by[r['id']]['width']and r['direction']==by[r['id']]['direction']
  else:by[r['id']]=r
 out['roads']=list(by.values());out['parkingSpaces']+=new['parkingSpaces'];return out

def add_regions(e,layout,plan,blocks,surfaces,byinst):
 if not(e.I/'suburb-increment.json').exists():return
 inc=e.read(e.I/'suburb-increment.json');new=e.read(inc['snapshotPath']);old=e.read(inc['oldBaselinePath']);newpts=[q for s in new['groundSurfaces']for q in s['polygonMap']];bounds={'minX':min(q[0]for q in newpts)-12,'maxX':max(q[0]for q in newpts)+12,'minY':min(q[1]for q in newpts)-12,'maxY':max(q[1]for q in newpts)+12}
 layout['bounds']=copy.deepcopy(old['bounds']);layout['groundRegions']=[{'id':'legacy006','bounds':old['bounds'],'surfaceIds':[s['id']for s in old['groundSurfaces']],'roadIds':[r['id']for r in old['roads']]},{'id':'suburb008','bounds':bounds,'surfaceIds':[s['id']for s in new['groundSurfaces']],'roadIds':[r['id']for r in new['roads']]}];layout['camera']=copy.deepcopy(old['camera']);layout['cameraViews']=copy.deepcopy(old['cameraViews']);layout['rider']=copy.deepcopy(old['rider']);layout['sceneIncrementSource']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSubsetSHA256':inc['derivedSubsetSHA256']}
 def camera(ids,groundids):
  ex=[]
  for b in blocks:
   if b['persistentId']not in ids:continue
   a=byinst[b['assetId']];p=e.project(b['anchorMap']);x,y=[(p[k]-e.META['editorOrigin'][k])/16 for k in (0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ex.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for s in surfaces:
   if s['id']in groundids:
    for q in s['polygonMap']:
     p=e.project(q);ex.append([(p[k]-e.META['editorOrigin'][k])/16 for k in (0,1)])
  lo=[min(q[k]for q in ex)for k in (0,1)];hi=[max(q[k]for q in ex)for k in (0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in (0,1)]);return{'focusMap':focus,'fitWidthUnits':max(20,(hi[0]-lo[0])*1.12),'fitHeightUnits':max(20,(hi[1]-lo[1])*1.16),'screenOffset':[0,0]}
 ids=[b['persistentId']for b in blocks if b['persistentId'].startswith('008-')];allground=[s['id']for s in new['groundSurfaces']];gardenids=[i for i in ids if i not in ['008-B08','008-service-V02','008-tree-3']];marketids=['008-B08','008-service-V02','008-tree-1','008-tree-3','008-P07'];layout['cameraViews']['suburb']=camera(ids,allground);layout['cameraViews']['garden']=camera(gardenids,[s['id']for s in new['groundSurfaces']if s['id']in ['008-garden-zone']or s['id'].startswith('008-B05-door')or s['id'].startswith('008-B06-door')]);layout['cameraViews']['market']=camera(marketids,[s['id']for s in new['groundSurfaces']if s['id']=='008-service-yard'or s['id'].startswith('008-B08-door')or s['id'].startswith('008-service-side')])

 for b,key in [(next(b for b in new['buildings']if b['id']=='008-B06'),'door-b06'),(next(b for b in new['buildings']if b['id']=='008-B08'),'door-market')]:
  nn=[.9721948082958105,.23417355683909316];layout['cameraViews'][key]={'focusMap':[b['entryMap'][k]+1.5*nn[k]for k in (0,1)],'fitWidthUnits':14,'fitHeightUnits':14,'screenOffset':[0,0]}

def patch(e):
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 if 'o.groundRegion=function()'not in s:
  assert s.count('o.ground=function()')==1;s=s.replace('o.ground=function()','o.groundRegion=function()',1)
  wrapper='o.ground=function(){var saved=this.layout,regions=saved.groundRegions||[{id:"legacy",bounds:saved.bounds,surfaceIds:(saved.groundSurfaces||[]).map(function(s){return s.id}),roadIds:saved.roads.map(function(r){return r.id})}];globalThis.__mapGroundStats=[];for(var region of regions){this.layout=Object.assign({},saved,{bounds:region.bounds,activeGroundRegionId:region.id,groundSurfaces:(saved.groundSurfaces||[]).filter(function(s){return region.surfaceIds.includes(s.id)}),roads:saved.roads.filter(function(r){return region.roadIds.includes(r.id)})});this.groundRegion()}this.layout=saved},'
  assert s.count('o.prepareRiderSizes=function()')==1;s=s.replace('o.prepareRiderSizes=function()',wrapper+'o.prepareRiderSizes=function()',1)
  marker='this.sprite("original-roads",this.frame(l),h,c,[.5,.5])';repl='globalThis.__mapGroundStats.push({id:this.layout.activeGroundRegionId,width:l.width,height:l.height,projectedWidth:h,projectedHeight:c,bounds:this.layout.bounds,surfaceCount:(this.layout.groundSurfaces||[]).length,roadCount:this.layout.roads.length});this.sprite("ground-"+this.layout.activeGroundRegionId,this.frame(l),h,c,[.5,.5])';assert s.count(marker)==1;s=s.replace(marker,repl)
  marker='s.forEach(function(i,k){i.node.setSiblingIndex(k+1)})';assert s.count(marker)==1;s=s.replace(marker,'var groundBase=(this.layout.groundRegions||[{}]).length;s.forEach(function(i,k){i.node.setSiblingIndex(k+groundBase)})')
  s=s.replace('"G03-meadow":"#a7ae8d"','"G03-meadow":"#a7ae8d","G04-suburb-lawn":"#9fb986","G05-garden-soil":"#9b8261"')
  f.write_text(s)
 f=e.V/'assets/main/index.probe41.js';code=f.read_text()
 if '__mapFrameSharing'not in code:
  marker='y:i.node.position.y}})}'
  replacement='y:i.node.position.y}});if(!globalThis.__mapFrameSharing){var frameIds=new Map;globalThis.__mapFrameSharing=Array.from(this.frames.entries()).map(function(p){if(!frameIds.has(p[1]))frameIds.set(p[1],frameIds.size);return{assetId:p[0],file:this.assets.get(p[0]).file,frameIndex:frameIds.get(p[1])}},this)}}'
  assert code.count(marker)==1;f.write_text(code.replace(marker,replacement))
 html=e.V/'index.html';s=html.read_text()
 if '?view=suburb'not in s:s=s.replace('休憩近景</a>','休憩近景</a> · <a href="?view=suburb">郊区整体</a> · <a href="?view=garden">住宅菜园</a> · <a href="?view=market">市场后勤</a>')
 html.write_text(s)
