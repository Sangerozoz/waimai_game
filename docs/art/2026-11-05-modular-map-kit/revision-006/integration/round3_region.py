"""Round3 source-array binding and finite-view ground references in the same006 viewer."""
import copy

def increment_plan(e,plan):
 f=e.I/'round3-009-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['derivedPath'])==inc['derivedSHA256'];assert e.sha(inc['preScenePath'])==inc['preSceneSHA256'];new=e.read(inc['derivedPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);roads={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in roads:assert r==roads[r['id']]
  else:roads[r['id']]=r
 out['roads']=list(roads.values());return out

def add_regions(e,layout,blocks,surfaces,assets):
 f=e.I/'round3-009-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath']);assert blocks[:74]==old['blocks'],'Actual old74 metadata/position/order changed';assert surfaces[:164]==old['groundSurfaces'],'Actual old164 grounds changed';roads=layout['roads'];ts=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':ts})
 mapped={b['persistentId']:b for b in new['buildings']}
 for b in blocks[74:]:
  if b['persistentId']not in mapped:continue
  item=mapped[b['persistentId']];binding=item['visualReplacementOf'];b.update({'visualReplacementOf':copy.deepcopy(binding),'sourceIndices':copy.deepcopy(binding['sourceIndices']),'sourcePolygonsMap':copy.deepcopy(binding['sourcePolygonsMap']),'sourceSHA256':binding['sourceSHA256'],'sourceDataChanged':False,'sourceNativeSHA256':item['sourceNativeSHA256'],'uniformScaleCandidate':item['uniformScale'],'entryPixel':item['entryPixel'],'entryMap':item['entryMap'],'navigationStopNodeId':item['navigationStopNodeId'],'navigationStopOriginalWorld':item['navigationStopOriginalWorld'],'stopAssociation':item['stopAssociation'],'newBusinessPOIs':0,'navigationEdgesAdded':0})
 def region_and_view(name,ids,cap=2048,margin=1.3):
  selected=[b for b in blocks if b['persistentId']in ids];grounds=[s for s in new['groundSurfaces']if s['owner']in ids];points=[q for s in grounds for q in s['polygonMap']]
  ext=[]
  for b in selected:
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in (0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   p=e.project(q);ext.append([(p[k]-e.META['editorOrigin'][k])/16 for k in (0,1)])
  assert selected and points;bounds={'minX':min(q[0]for q in points)-14,'maxX':max(q[0]for q in points)+14,'minY':min(q[1]for q in points)-14,'maxY':max(q[1]for q in points)+14}
  # These are view-limited references, not baked PNGs. The engine clips all intersecting
  # existing/new surfaces and full original roads in this finite region, preserving source arrays.
  layout['groundRegions'].append({'id':name,'bounds':bounds,'surfaceIds':[s['id']for s in grounds],'roadIds':[r['id']for r in new['roads']],'maxCanvasEdge':cap,'includeAllSceneReferences':True,'role':'finite partial-district overview'if cap==1536 else'finite local native neighborhood window'})
  lo=[min(q[k]for q in ext)for k in (0,1)];hi=[max(q[k]for q in ext)for k in (0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in (0,1)])
  layout['cameraViews'][name]={'focusMap':focus,'fitWidthUnits':max(22,(hi[0]-lo[0])*margin),'fitHeightUnits':max(22,(hi[1]-lo[1])*margin),'screenOffset':[0,-65],'activeGroundRegionIds':[name]}
 allids=set(mapped);region_and_view('r3-overview',allids,1536,1.18)
 overview=next(r for r in layout['groundRegions']if r['id']=='r3-overview')
 for prior in old['groundRegions']:
  if prior['id']not in ['legacy006','north009','r2-north-shop']:continue
  for key in ['minX','minY']:overview['bounds'][key]=min(overview['bounds'][key],prior['bounds'][key])
  for key in ['maxX','maxY']:overview['bounds'][key]=max(overview['bounds'][key],prior['bounds'][key])
 overview['role']='finite coarse relationship view incl visible prior-city context; fixed1536 cap, never full county'
 # Mixed new-source close-ups, with old nearby2nd-batch plots drawn through the same finite clip.
 region_and_view('r3-central',{'009r3-src-0593','009r3-src-0610','009r3-src-0612'},margin=1.2)
 region_and_view('r3-northeast',{'009r3-src-0487','009r3-src-0486','009r3-src-0485','009r3-src-0484'})
 region_and_view('r3-office',{'009r3-src-0562'},margin=1.2)
 region_and_view('r3-south',{'009r3-src-0191','009r3-src-0640','009r3-src-0115'})
 region_and_view('r3-large-home',{'009r3-src-0557'})
 layout['round3SourceMappings']=copy.deepcopy(new['sourceMappings'])
 layout['visualReplacements']+=[{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceIndices':copy.deepcopy(b['visualReplacementOf']['sourceIndices']),'sourcePolygonsMap':copy.deepcopy(b['visualReplacementOf']['sourcePolygonsMap']),'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'navigationStopNodeId':b['navigationStopNodeId'],'navigationStopOriginalWorld':b['navigationStopOriginalWorld'],'associationScope':b['stopAssociation'],'sourceDataChanged':False,'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['buildings']]
 layout['round3Evidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'actualPreSceneSHA256':inc['preSceneSHA256'],'actualProtectedCount':[74,164],'sourceIndices':new['sourceIndices'],'districtOrganization':copy.deepcopy(new['districtOrganization']),'canonicalScaleContract':'frame=canonical*uniformScale exactly once; runtime node scale1','uniqueAdmittedSources':new['uniqueSourceCount'],'admittedVisualModules':len(new['buildings']),'admittedGrounds':len(new['groundSurfaces']),'navigationAssociationNotOriginalBinding':True,'newBusinessPOIs':0,'navigationEdgesAdded':0,'limitedGroundMaximumCanvasEdge':2048,'overviewMaximumCanvasEdge':1536,'FPSOrMemoryMeasured':False}

def patch(e):
 if not(e.I/'round3-009-increment.json').exists():return
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 if '"G09-r3-planted"'not in s:
  marker='"G08-r2-courtyard":"#9fb789"';assert s.count(marker)==1;s=s.replace(marker,marker+',"G09-r3-planted":"#9fb584"')
 if '"G10-r3-courtyard"'not in s:
  marker='"G09-r3-planted":"#9fb584"';assert s.count(marker)==1;s=s.replace(marker,marker+',"G10-r3-courtyard":"#a5bb8c"')
 if '__mapGroundReferenceMode'not in s:
  marker='groundSurfaces:(saved.groundSurfaces||[]).filter(function(s){return region.surfaceIds.includes(s.id)}),roads:saved.roads.filter(function(r){return region.roadIds.includes(r.id)})'
  repl='groundSurfaces:(saved.groundSurfaces||[]).filter(function(s){if(!(region.includeAllSceneReferences||(saved.round3Evidence&&region.id==="r2-courts")))return region.surfaceIds.includes(s.id);var xs=s.polygonMap.map(function(p){return p[0]}),ys=s.polygonMap.map(function(p){return p[1]});return Math.max.apply(Math,xs)>=region.bounds.minX&&Math.min.apply(Math,xs)<=region.bounds.maxX&&Math.max.apply(Math,ys)>=region.bounds.minY&&Math.min.apply(Math,ys)<=region.bounds.maxY}),roads:saved.roads.filter(function(r){if(!(region.includeAllSceneReferences||(saved.round3Evidence&&region.id==="r2-courts")))return region.roadIds.includes(r.id);return r.nodes.some(function(p,i){if(!i)return false;var q=r.nodes[i-1],m=r.width/2+1.8;return Math.max(p[0],q[0])+m>=region.bounds.minX&&Math.min(p[0],q[0])-m<=region.bounds.maxX&&Math.max(p[1],q[1])+m>=region.bounds.minY&&Math.min(p[1],q[1])-m<=region.bounds.maxY})})'
  assert s.count(marker)==1;s=s.replace(marker,repl);s=s.replace('this.layout=saved},o.prepareRiderSizes','this.layout=saved;globalThis.__mapGroundReferenceMode="finite bounds, original complete geometry; no new navigation"},o.prepareRiderSizes',1)
 f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=r3-central'not in s:s=s.replace('1.0/0.9实景对照</a>','1.0/0.9实景对照</a> · <a href="?view=r3-overview">第三批关系</a> · <a href="?view=r3-central">第三批混合街巷</a> · <a href="?view=r3-northeast">第三批东北住区</a> · <a href="?view=r3-office">第三批办公街段</a>')
 f.write_text(s)
