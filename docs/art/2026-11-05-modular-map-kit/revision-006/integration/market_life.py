"""Strict four-surface art permission and one useful market-life overlay on actual156."""
import copy,math

def approved_prefix(e,actual,before):
 """Only parent-authorized market changes may differ from earlier frozen ground baselines."""
 f=e.I/'market-life-increment.json'
 if not f.exists():assert actual[:len(before)]==before;return
 inc=e.read(f);assert e.sha(inc['layoutPath'])==inc['layoutSHA256'];plan=e.read(inc['layoutPath']);changes={d['surfaceId']:d['after']for d in plan['existingGroundChanges']}
 assert set(changes)==set(plan['authorizedOldSurfaceIds'])and len(changes)==4
 assert len(actual)>=len(before),'Protected ground surface missing'
 for current,old in zip(actual,before):
  assert current['id']==old['id'],'Old ground sequence/ID altered'
  if old['id']not in changes:assert current==old,('Unapproved old ground modified',old['id']);continue
  expected=changes[old['id']];assert current.keys()==expected.keys()and current['materialId']==expected['materialId']
  assert len(current['polygonMap'])==len(expected['polygonMap'])and all(math.dist(a,b)<1e-9 for a,b in zip(current['polygonMap'],expected['polygonMap']))

def apply(e,layout,blocks,surfaces,assets,report):
 f=e.I/'market-life-increment.json'
 if not f.exists():return
 inc=e.read(f);assert e.sha(inc['layoutPath'])==inc['layoutSHA256']and e.sha(inc['preScenePath'])==inc['preSceneSHA256'];plan=e.read(inc['layoutPath']);old=e.read(inc['preScenePath'])
 assert blocks[:156]==old['blocks'],'Old156 block fields/frame/ranks changed';approved_prefix(e,surfaces,old['groundSurfaces'])
 ranks={b['persistentId']:b['editorRenderOrder']for b in old['blocks']};by={b['persistentId']:b for b in blocks};fixtures={f['persistentId']:f for f in plan['newFixtures']};r4=[b for b in old['blocks']if b['persistentId'].startswith('009r4-')];slots={}
 for id in fixtures:
  depth=e.project(by[id]['anchorMap'])[1];pos=next((j for j,b in enumerate(r4)if e.project(b['anchorMap'])[1]>depth),len(r4));slots.setdefault(pos,[]).append(id)
 for pos,ids in slots.items():
  left=r4[pos-1]['editorRenderOrder']if pos else r4[0]['editorRenderOrder']-1;right=r4[pos]['editorRenderOrder']if pos<len(r4)else left+1
  for j,id in enumerate(sorted(ids,key=lambda id:e.project(by[id]['anchorMap'])[1])):ranks[id]=left+(right-left)*(j+1)/(len(ids)+1)
 for b in blocks[156:]:
  if b['persistentId']not in fixtures:continue
  item=fixtures[b['persistentId']];b.update({'editorRenderOrder':ranks[b['persistentId']],'ownerBuildingId':item['ownerBuildingId'],'scenePurpose':item['purpose'],'groundContactPolygonMap':item['groundContactPolygonMap'],'groundContactMethod':item['groundContactMethod']})
  if item['libraryAssetId']=='T05':b.update({'rootOriginMeasured':False,'rootInferenceUncertaintyPixels':70,'comparisonOnly':True})
 for row in report:
  if row['persistentId']in ranks:row['editorRenderOrder']=ranks[row['persistentId']]
 roads=layout['roads'];sha=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':sha})
 ids={plan['ownerBuildingId']}|set(fixtures);points=[q for s in surfaces if s['id']in plan['authorizedOldSurfaceIds']+[plan['immutableWalkId']]+inc['newGroundIds']for q in s['polygonMap']];ext=[]
 for b in blocks:
  if b['persistentId']not in ids:continue
  a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
 for q in points:
  px=e.project(q);ext.append([(px[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
 lo=[min(q[k]for q in ext)for k in(0,1)];hi=[max(q[k]for q in ext)for k in(0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)])
 fitw=(hi[0]-lo[0])*1.12;fith=(hi[1]-lo[1])*1.12;vh=max(fith,fitw/2);vw=vh*2.1;c=e.project(focus);world=[e.unproject([c[0]+16*dx,c[1]+16*dy])for dx in[-vw/2,vw/2]for dy in[-vh/2,vh/2]]+points
 bounds={'minX':min(q[0]for q in world)-2,'maxX':max(q[0]for q in world)+2,'minY':min(q[1]for q in world)-2,'maxY':max(q[1]for q in world)+2}
 layout['groundRegions'].append({'id':'market-life-ground','bounds':bounds,'surfaceIds':inc['modifiedGroundIds']+inc['newGroundIds']+[plan['immutableWalkId']],'roadIds':[r['id']for r in old['roads']],'includeAllSceneReferences':True,'maxCanvasEdge':2048,'role':'one bounded market entrance/waiting/shade and collection area; original roads only'})
 layout['cameraViews']['market-life']={'focusMap':focus,'fitWidthUnits':fitw,'fitHeightUnits':fith,'screenOffset':[0,0],'activeGroundRegionIds':['market-life-ground']}
 base=e.project(next(b['anchorMap']for b in old['blocks']if b['persistentId']==plan['ownerBuildingId']))
 layout['cameraViews']['market-life-detail']={'focusMap':e.unproject([base[0]+16*3,base[1]+16*6.5]),'fitWidthUnits':26,'fitHeightUnits':17,'screenOffset':[0,0],'activeGroundRegionIds':['market-life-ground']}
 layout['marketLifeEvidence']={'baselineCounts':[156,497],'baselineSceneSHA256':inc['preSceneSHA256'],'layoutSHA256':inc['layoutSHA256'],'modifiedGroundIds':inc['modifiedGroundIds'],'newGroundIds':inc['newGroundIds'],'newFixtureIds':inc['newFixtureIds'],'immutableWalkId':plan['immutableWalkId'],'old156AllFieldsAndFixedRanksPreserved':True,'other493GroundsEveryFieldAndOrderPreserved':True,'T05TotalCount':2,'T05RootMeasured':False,'newParkingSpaces':0,'newVehicles':0,'newBusinessPOIs':0,'newNavigationEdges':0,'userAccepted':False}

def patch(e):
 if not(e.I/'market-life-increment.json').exists():return
 f=e.V/'index.html';s=f.read_text()
 if '?view=market-life'not in s:s=s.replace('第五批住宅邻区</a>','第五批住宅邻区</a> · <a href="?view=market-life">市场候场与休息</a>')
 f.write_text(s)
