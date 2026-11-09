"""One art-complete central vignette on frozen94; no source or original sprite transforms."""
import copy,math

def apply(e,layout,blocks,surfaces,assets,report):
 path=e.I/'central-life-increment.json'
 if not path.exists():return
 inc=e.read(path);assert e.sha(inc['layoutPath'])==inc['layoutSHA256'];assert e.sha(inc['preScenePath'])==inc['preSceneSHA256'];plan=e.read(inc['layoutPath']);old=e.read(inc['preScenePath']);assert len(old['blocks'])==94 and len(old['groundSurfaces'])==260
 bypid={b['persistentId']:b for b in blocks};oldids={b['persistentId']for b in old['blocks']};newfixtures={f['id']:f for f in plan['newFixtures']}
 oldassets={a['id']:a for a in e.read(e.I/'central-life/pre-life-asset-manifest.json')['assets']}
 for b in old['blocks']:
  actual=copy.deepcopy(bypid[b['persistentId']]);actual['editorRenderOrder']=b['editorRenderOrder'];assert actual==b,('Original94 transform/source metadata altered',b['persistentId']);assert assets[b['assetId']]['worldSizeUnits']==oldassets[b['assetId']]['worldSizeUnits']
 # Fixed old editor ranks remain0..93. Fractional insertion ranks expose Tiled's local
 # depth insertion while keeping all old94 fields and relative order exactly unchanged.
 oldr3=[b for b in old['blocks']if b['persistentId'].startswith('009r3-')]
 def qdepth(anchor):return e.project(anchor)[1]
 slots={}
 for id,f in newfixtures.items():
  pos=next((j for j,b in enumerate(oldr3)if qdepth(b['anchorMap'])>qdepth(bypid[id]['anchorMap'])),len(oldr3));slots.setdefault(pos,[]).append(id)
 newblocks=[];orders={b['persistentId']:b['editorRenderOrder']for b in old['blocks']}
 for pos,ids in slots.items():
  left=oldr3[pos-1]['editorRenderOrder']if pos else oldr3[0]['editorRenderOrder']-1;right=oldr3[pos]['editorRenderOrder']if pos<len(oldr3)else left+1
  for j,id in enumerate(sorted(ids,key=lambda id:qdepth(bypid[id]['anchorMap']))):orders[id]=left+(right-left)*(j+1)/(len(ids)+1)
 for id,f in newfixtures.items():
  row=copy.deepcopy(bypid[id]);row['editorRenderOrder']=orders[id];row['scenePurpose']=f['purpose'];row['ownerBuildingId']=f['owner'];row['groundContactMethod']=f['groundContactMethod'];row['groundContactPolygonMap']=f['groundContactPolygonMap'];newblocks.append(row)
 # Later SHA-gated increments pass through; never truncate back to the life94 base.
 extras=[copy.deepcopy(b)for b in blocks if b['persistentId']not in oldids and b['persistentId']not in newfixtures]
 blocks[:]=copy.deepcopy(old['blocks'])+newblocks+extras
 for row in report:
  if row['persistentId']in orders:row['editorRenderOrder']=orders[row['persistentId']]
 actualgrounds={s['id']:s for s in surfaces};diff={d['surfaceId']:d for d in plan['existingGroundChanges']}
 for s in old['groundSurfaces']:
  expected=diff[s['id']]['after']if s['id']in diff else s
  if s['id']in diff:
   actual=actualgrounds[s['id']];assert actual['id']==expected['id']and actual['materialId']==expected['materialId'];assert len(actual['polygonMap'])==len(expected['polygonMap'])and all(math.dist(a,b)<1e-9 for a,b in zip(actual['polygonMap'],expected['polygonMap']))
  else:assert actualgrounds[s['id']]==expected,('Unapproved ground field changed',s['id'])
 assert surfaces[:164]==old['groundSurfaces'][:164]
 for id in plan['selectedThirdBatchBuildingIds']:assert actualgrounds[id+'-walk-0']==next(s for s in old['groundSurfaces']if s['id']==id+'-walk-0')
 immutable_ground_ids={q['id']for q in old['groundSurfaces']} - set(diff)
 assert [s['id']for s in surfaces if s['id']in immutable_ground_ids]==[s['id']for s in old['groundSurfaces']if s['id']in immutable_ground_ids]
 tiledsha=layout['tiledSourceSHA256'];roads=layout['roads'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':tiledsha})
 def view(name,ids,points,width=None,height=None,focus=None):
  ex=[]
  for b in blocks:
   if b['persistentId']not in ids:continue
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in(0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ex.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   p=e.project(q);ex.append([(p[k]-e.META['editorOrigin'][k])/16 for k in(0,1)])
  lo=[min(p[k]for p in ex)for k in(0,1)];hi=[max(p[k]for p in ex)for k in(0,1)];f=focus or e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in(0,1)])
  region='central-life-ground';layout['cameraViews'][name]={'focusMap':f,'fitWidthUnits':width or(hi[0]-lo[0])*1.14,'fitHeightUnits':height or(hi[1]-lo[1])*1.14,'screenOffset':[0,-65],'activeGroundRegionIds':[region]}
 selected=set(plan['selectedThirdBatchBuildingIds']);allids=selected|set(newfixtures);pts=[p for s in surfaces if any(s['id'].startswith(id+'-')for id in selected)or s['id']in inc['newGroundIds']for p in s['polygonMap']]
 bounds={'minX':min(p[0]for p in pts)-7,'maxX':max(p[0]for p in pts)+9,'minY':min(p[1]for p in pts)-7,'maxY':max(p[1]for p in pts)+7}
 context=[p for s in old['groundSurfaces']if s['id'].startswith('009r2-src-0609-')for p in s['polygonMap']]
 bounds['minY']=min(bounds['minY'],min(p[1]for p in context)-2)
 layout['groundRegions'].append({'id':'central-life-ground','bounds':bounds,'surfaceIds':[s['id']for s in surfaces if s['id']in inc['newGroundIds']or any(s['id'].startswith(id+'-')for id in selected)],'roadIds':[r['id']for r in old['roads']],'includeAllSceneReferences':True,'maxCanvasEdge':2048,'role':'one complete local street vignette; all prior geometry retained'})
 view('life-street',allids,pts)
 view('life-detail',{'009r3-src-0610'}|{id for id,f in newfixtures.items()if f['owner']=='009r3-src-0610'},[],width=22,height=14,focus=[-1247.2,188.8])
 layout['centralLifeEvidence']={'authority':inc['authority'],'baselineSceneSHA256':inc['preSceneSHA256'],'layoutSHA256':inc['layoutSHA256'],'selectedBuildingIds':plan['selectedThirdBatchBuildingIds'],'modifiedGroundIds':inc['modifiedGroundIds'],'newGroundIds':inc['newGroundIds'],'newFixtureIds':inc['newFixtureIds'],'old94TransformsFramesAndRelativeOrderUnchanged':True,'oldEditorRanksUnchanged':True,'newFractionalEditorRanks':{id:orders[id]for id in newfixtures},'protectedFirst164Grounds':True,'original1_5mWalksUnchanged':True,'newBusinessPOIs':0,'newNavigationEdges':0,'scope':'local art organisation only, not a source geometry/navigation change or county/user acceptance'}

def patch(e):
 if not(e.I/'central-life-increment.json').exists():return
 f=e.V/'index.html';s=f.read_text()
 if '?view=life-street'not in s:s=s.replace('第三批办公街段</a>','第三批办公街段</a> · <a href="?view=life-street">完整街巷候选</a> · <a href="?view=life-detail">商服休憩细节</a>')
 f.write_text(s)
