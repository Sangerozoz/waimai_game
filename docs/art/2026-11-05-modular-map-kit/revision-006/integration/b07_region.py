"""B07 one-building wide-court comparison, additive to existing regions."""
import copy

def increment_plan(e,plan):
 f=e.I/'b07-wide-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['calibrationPath'])==inc['calibrationSHA256'];assert e.sha(inc['snapshotPath'])==inc['snapshotSHA256'];assert e.sha(e.I/'b07-runtime-subset-plan.json')==inc['derivedSubsetSHA256'];assert e.sha(inc['priorBaselinePath'])==inc['priorBaselineSHA256'];new=e.read(inc['snapshotPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:assert r['nodes']==roads[r['id']]['nodes']and r['width']==roads[r['id']]['width']and r['direction']==roads[r['id']]['direction']
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def add_region(e,layout,blocks,surfaces,assets):
 if not(e.I/'b07-wide-increment.json').exists():return
 inc=e.read(e.I/'b07-wide-increment.json');p=e.read(inc['snapshotPath']);prior=e.read(inc['priorBaselinePath']);ids={b['persistentId']for b in p['buildings']};gids={s['id']for s in p['groundSurfaces']};pts=[q for s in p['groundSurfaces']for q in s['polygonMap']];bounds={'minX':min(q[0]for q in pts)-10,'maxX':max(q[0]for q in pts)+10,'minY':min(q[1]for q in pts)-10,'maxY':max(q[1]for q in pts)+10};layout['groundRegions'].append({'id':'b07wide008','bounds':bounds,'surfaceIds':list(gids),'roadIds':[r['id']for r in p['roads']]});layout['cameraViews']=copy.deepcopy(prior['cameraViews']);layout['camera']=copy.deepcopy(prior['camera']);ex=[]
 for b in blocks:
  if b['persistentId']not in ids:continue
  a=assets[b['assetId']];px=e.project(b['anchorMap']);x,y=[(px[k]-e.META['editorOrigin'][k])/16 for k in (0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ex.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
 for s in surfaces:
  if s['id']in gids:
   for q in s['polygonMap']:
    px=e.project(q);ex.append([(px[k]-e.META['editorOrigin'][k])/16 for k in (0,1)])
 lo=[min(q[k]for q in ex)for k in (0,1)];hi=[max(q[k]for q in ex)for k in (0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in (0,1)]);layout['cameraViews']['ucourt']={'focusMap':focus,'fitWidthUnits':(hi[0]-lo[0])*1.12,'fitHeightUnits':(hi[1]-lo[1])*1.18,'screenOffset':[0,0]};b=p['buildings'][0];path=p['pedestrianConnections'][0]['centrelineMap'];middle=path[1];layout['cameraViews']['ucourt-door']={'focusMap':middle,'fitWidthUnits':14,'fitHeightUnits':14,'screenOffset':[0,0]};layout['b07ComparisonEvidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'calibrationSHA256':inc['calibrationSHA256'],'derivedSubsetSHA256':inc['derivedSubsetSHA256'],'staticWalkUGap':inc['staticWalkUGap'],'doorPointId':11,'stepPointId':12,'noWholeVoidSlab':True}

def patch(e):
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 if 'G06-b07-garden'not in s:
  marker='"G05-garden-soil":"#9b8261"';assert s.count(marker)==1;s=s.replace(marker,marker+',"G06-b07-garden":"#a3bc8a"');f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=ucourt'not in s:s=s.replace('市场后勤</a>','市场后勤</a> · <a href="?view=ucourt">U院比较</a> · <a href="?view=ucourt-door">U院门阶</a>')
 f.write_text(s)
