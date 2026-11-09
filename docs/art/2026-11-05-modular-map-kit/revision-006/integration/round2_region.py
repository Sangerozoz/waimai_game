"""Round2 native source-carrier increment on actual69, preserving all previous scene fields."""
import copy,math

def increment_plan(e,plan):
 f=e.I/'round2-009-increment.json'
 if not f.exists():return plan
 inc=e.read(f);assert e.sha(inc['parentPath'])==inc['parentOriginalSHA256'];assert e.sha(inc['derivedPath'])==inc['derivedSHA256'];assert e.sha(inc['preScenePath'])==inc['preSceneSHA256'];new=e.read(inc['derivedPath']);assert new['projection']==plan['projection'];out=copy.deepcopy(plan);by={r['id']:r for r in out['roads']}
 for r in new['roads']:
  if r['id']in by:assert r==by[r['id']]
  else:by[r['id']]=r
 out['roads']=list(by.values());return out

def add_regions(e,layout,blocks,surfaces,assets):
 f=e.I/'round2-009-increment.json'
 if not f.exists():return
 inc=e.read(f);new=e.read(inc['derivedPath']);old=e.read(inc['preScenePath']);assert blocks[:69]==old['blocks'],'Actual old69 metadata/position/order changed';assert surfaces[:135]==old['groundSurfaces'],'Actual old135 grounds changed';roads=layout['roads'];ts=layout['tiledSourceSHA256'];layout.clear();layout.update(copy.deepcopy(old));layout.update({'blocks':blocks,'groundSurfaces':surfaces,'roads':roads,'tiledSourceSHA256':ts})
 mapping={b['persistentId']:b for b in new['buildings']};cal={a['id']:a for a in e.read(e.I/'asset-calibration.json')['assets']}
 for b in blocks[69:]:
  if b['persistentId']not in mapping:continue
  item=mapping[b['persistentId']];binding=item['visualReplacementOf'];b.update({'visualReplacementOf':copy.deepcopy(binding),'sourceIndex':binding['sourceIndex'],'sourcePolygon':binding['sourcePolygonMap'],'sourceSHA256':binding['sourceCitySHA256'],'sourceNativeSHA256':item['sourceNativeSHA256'],'uniformScaleCandidate':item['uniformScale'],'entryPixel':item['entryPixel'],'entryMap':item['entryMap'],'navigationStopNodeId':item['navigationStopNodeId'],'navigationStopOriginalWorld':item['navigationStopOriginalWorld'],'navigationStopAssociation':item['navigationStopAssociation'],'newBusinessPOIs':0,'navigationEdgesAdded':0})
 groups=[('r2-courts',['009r2-src-0602','009r2-src-0609','009r2-src-0599'],['149396529-0','149396552-0']),('r2-north-shop',['009r2-src-0418'],['149287627-0']),('r2-south-home',['009r2-src-0223'],['733760357-0'])]
 for regionid,ids,roadids in groups:
  grounds=[s for s in new['groundSurfaces']if any(s['id'].startswith(pid+'-')for pid in ids)];points=[q for s in grounds for q in s['polygonMap']];bounds={'minX':min(q[0]for q in points)-8,'maxX':max(q[0]for q in points)+9,'minY':min(q[1]for q in points)-9,'maxY':max(q[1]for q in points)+9}
  layout['groundRegions'].append({'id':regionid,'bounds':bounds,'surfaceIds':[s['id']for s in grounds],'roadIds':roadids,'maxCanvasEdge':2048,'role':'finite source-site courtyard; full road nodes stored, drawing clip only'})
  ext=[]
  for b in blocks:
   if b['persistentId']not in ids:continue
   a=assets[b['assetId']];q=e.project(b['anchorMap']);x,y=[(q[k]-e.META['editorOrigin'][k])/16 for k in (0,1)];w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  for q in points:
   xy=e.project(q);ext.append([(xy[k]-e.META['editorOrigin'][k])/16 for k in (0,1)])
  lo=[min(q[k]for q in ext)for k in (0,1)];hi=[max(q[k]for q in ext)for k in (0,1)];focus=e.unproject([e.META['editorOrigin'][k]+8*(lo[k]+hi[k])for k in (0,1)]);layout['cameraViews'][regionid]={'focusMap':focus,'fitWidthUnits':max(20,(hi[0]-lo[0])*1.35),'fitHeightUnits':max(20,(hi[1]-lo[1])*1.35),'screenOffset':[0,-65],'activeGroundRegionIds':[regionid]}
 # Equal world-unit camera windows for real old1.0 and new0.9, at their actual separate map sites.
 for name,pid,region in [('r2-scale-original','008-B06','suburb008'),('r2-scale-new','009r2-src-0602','r2-courts')]:
  b=next(b for b in blocks if b['persistentId']==pid);a=assets[b['assetId']];q=e.project(b['anchorMap']);w,h=a['worldSizeUnits'];u,v=a['anchorUV'];focus=e.unproject([q[0]+(.5-u)*w*16,q[1]+(.5-v)*h*16]);layout['cameraViews'][name]={'focusMap':focus,'fitWidthUnits':22,'fitHeightUnits':22,'screenOffset':[0,0],'activeGroundRegionIds':[region],'scaleComparisonActualPersistentId':pid,'equalCameraWindowWorldUnits':22}
 centers=[]
 for pid in ['009r2-src-0602','009r2-src-0599']:
  b=next(b for b in blocks if b['persistentId']==pid);a=assets[b['assetId']];q=e.project(b['anchorMap']);w,h=a['worldSizeUnits'];u,v=a['anchorUV'];centers.append(e.unproject([q[0]+(.5-u)*w*16,q[1]+(.5-v)*h*16]))
 layout['cameraViews']['r2-homes']={'focusMap':[sum(p[k]for p in centers)/2 for k in (0,1)],'fitWidthUnits':58,'fitHeightUnits':42,'screenOffset':[0,-65],'activeGroundRegionIds':['r2-courts']}
 b=next(b for b in blocks if b['persistentId']=='009r2-src-0609');a=assets[b['assetId']];q=e.project(b['anchorMap']);w,h=a['worldSizeUnits'];u,v=a['anchorUV'];focus=e.unproject([q[0]+(.5-u)*w*16,q[1]+(.5-v)*h*16]);layout['cameraViews']['r2-shop609']={'focusMap':focus,'fitWidthUnits':18,'fitHeightUnits':18,'screenOffset':[0,-65],'activeGroundRegionIds':['r2-courts']}
 layout['visualReplacements']+= [{'persistentId':b['persistentId'],'libraryAssetId':b['libraryAssetId'],'sourceIndex':b['visualReplacementOf']['sourceIndex'],'sourcePolygon':b['visualReplacementOf']['sourcePolygonMap'],'visualReplacementOf':copy.deepcopy(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryMap':b['entryMap'],'navigationStopNodeId':b['navigationStopNodeId'],'navigationStopOriginalWorld':b['navigationStopOriginalWorld'],'associationScope':b['navigationStopAssociation'],'rawSourceVisualPresentBefore':False,'suppressedRawSourceInstanceCount':0,'newBusinessPOIs':0,'navigationEdgesAdded':0}for b in new['buildings']]
 layout['round2Evidence']={'parentOriginalSHA256':inc['parentOriginalSHA256'],'derivedSHA256':inc['derivedSHA256'],'actualPreSceneSHA256':inc['preSceneSHA256'],'actualProtectedCount':[69,135],'sourceIndices':[b['visualReplacementOf']['sourceIndex']for b in new['buildings']],'canonicalScaleContract':'UI size canonical*uniformScale once, node localScale1; image/frame shared','newBusinessPOIs':0,'navigationEdgesAdded':0,'navigationAssociationNotOriginalBinding':True}

def patch(e):
 if not(e.I/'round2-009-increment.json').exists():return
 f=e.V/'assets/main/index.probe41.js';s=f.read_text()
 if '"G08-r2-courtyard"'not in s:
  marker='"G07-north-garden":"#9db486"';assert s.count(marker)==1;s=s.replace(marker,marker+',"G08-r2-courtyard":"#9fb789"')
 if '__mapUIDimensions'not in s:
  marker='frameIndex:frameIds.get(p[1])}},this)}}';assert s.count(marker)==1
  replace='frameIndex:frameIds.get(p[1])}},this);globalThis.__mapUIDimensions=this.items.filter(function(i){return Number.isFinite(i.editorOrder)}).map(function(i){var ui=i.node.getComponent(l);return{persistentId:i.persistentId,nodeName:i.node.name,uiWidth:ui.contentSize.width,uiHeight:ui.contentSize.height,nodeScaleX:i.node.scale.x,nodeScaleY:i.node.scale.y,worldFrameUnits:[ui.contentSize.width/this.ppm,ui.contentSize.height/this.ppm],anchorPoint:[ui.anchorPoint.x,ui.anchorPoint.y]}},this)}}'
  s=s.replace(marker,replace)
 if 'viewInitialZoom:this.initialZoom'not in s:
  marker='nodeScaleY:i.node.scale.y,worldFrameUnits:';assert s.count(marker)==1;s=s.replace(marker,'nodeScaleY:i.node.scale.y,viewInitialZoom:this.initialZoom,projectionPixelsPerUnit:this.ppm,worldFrameUnits:')
 f.write_text(s)
 f=e.V/'index.html';s=f.read_text()
 if '?view=r2-courts'not in s:s=s.replace('北段与旧区关系</a>','北段与旧区关系</a> · <a href="?view=r2-courts">第二批住宅组</a> · <a href="?view=r2-north-shop">第二批北铺</a> · <a href="?view=r2-south-home">第二批南宅</a> · <a href="scale-compare.html">1.0/0.9实景对照</a>')
 if '?view=r2-homes'not in s:s=s.replace('第二批住宅组</a>','第二批住宅组</a> · <a href="?view=r2-homes">双住宅近景</a> · <a href="?view=r2-shop609">609门前</a>')
 if 'id="map-preview-toolbar"'not in s:s=s.replace('<div style="position:fixed;top:12px;left:12px;', '<div id="map-preview-toolbar" style="position:fixed;top:12px;left:12px;')
 if 'r2-embed-style'not in s:s=s.replace('</head>','<style id="r2-embed-style">html.preview-embed #map-preview-toolbar{display:none}</style><script>if(new URLSearchParams(location.search).has("embed"))document.documentElement.classList.add("preview-embed")</script></head>')
 f.write_text(s)
