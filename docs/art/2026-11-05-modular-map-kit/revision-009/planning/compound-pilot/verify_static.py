#!/usr/bin/env python3
"""Pure static ownership/geometry verification. Does not import shared game/importer code."""
import json,math,hashlib
from PIL import Image
from compound_context import load
x=load();O=x.O;p=x.read(O/'scene-compound-pilot.json');before=x.read(O/'input-sha-before.json');checks=[];geometry=[]
def require(ok,label,evidence=None):
 checks.append({'rule':label,'passed':bool(ok),'evidence':evidence})
 if not ok:raise AssertionError(label+': '+str(evidence))
def same(a,b):return len(a)==len(b) and all(math.dist(c,d)<1e-8 for c,d in zip(a,b))
require(all(x.sha(f)==h for f,h in before.items()),'all-frozen-input-SHAs-unchanged',len(before))
require(p['projection']==x.P,'projection-exact-frozen-copy')
sceneids=[s['sceneId'] for s in p['scenes']];modids=[m['persistentId'] for m in p['buildings']];require(len(sceneids)==len(set(sceneids)),'unique-sceneIds');require(len(modids)==len(set(modids)),'unique-module-persistentIds')
oldids={b['persistentId'] for b in x.scene['blocks']};require(not set(modids)&oldids,'no-old-persistentId-reuse')
ownership={};mlookup={m['persistentId']:m for m in p['buildings']};slookup={s['sceneId']:s for s in p['scenes']};surfaceIds=[s['id'] for s in p['groundSurfaces']];require(len(surfaceIds)==len(set(surfaceIds)),'unique-new-surfaceIds');require(not set(surfaceIds)&{s['id'] for s in x.oldground},'no-old-surfaceId-reuse')
for s in p['scenes']:
 ids=s['sourceIndices'];require(len(ids)==len(set(ids)),'no-repeated-source-within-scene-set')
 require(len(ids)==len(s['sourcePolygonsMap']),'source-index-polygon-pair-count')
 for i,poly in zip(ids,s['sourcePolygonsMap']):
  require(i not in ownership,'no-source-cross-scene-reuse',i);ownership[i]=s['sceneId'];require(i not in x.bound|x.reserved,'not-old-bound-or-reserved',i);require(poly==x.c['buildings'][i],'source-polygon-exact-copy',i)
 require(set(ids)=={i for m in p['buildings'] if m['sceneId']==s['sceneId'] for i in m['sourceIndices']},'each-owned-source-referenced-by-scene-module-union')
 require(set(s['moduleIds'])=={m['persistentId'] for m in p['buildings'] if m['sceneId']==s['sceneId']},'scene-module-bidirectional-membership')
 require(set(s['groundSurfaceIds'])=={v['id'] for v in p['groundSurfaces'] if v['sceneId']==s['sceneId']},'scene-ground-membership')
 require(not s['oldSurfaceEdits'] and not s['oldSurfacePermissionRequired'],'no-old-ground-edit-permission-assumed')
require(set(p['sourceIndices'])==set(ownership),'top-level-source-set-is-scene-union')
for m in p['buildings']:
 vr=m['visualReplacementOf'];require(set(vr['sourceIndices'])==set(m['sourceIndices']),'module-replacement-owned-source-set');require(vr['sourcePolygonsMap']==[x.c['buildings'][i] for i in vr['sourceIndices']],'module-replacement-original-polygons');require(vr['sourceSHA256']==x.sha(x.cf) and not vr['sourceDataChanged'],'module-source-SHA-and-data-read-only')
require(p['groundSurfaceCount']==len(p['groundSurfaces']),'ground-surface-count-exact')
require(p['uniqueSourceCount']==len(ownership) and p['sceneCount']==len(sceneids) and p['moduleCount']==len(modids),'counts-sources-scenes-modules-separate',{'sources':len(ownership),'scenes':len(sceneids),'modules':len(modids)})
require(not p['fixtures'] and not p['parkingSpaces'] and not p['parkedVehicles'],'only-trial-native-building-modules-and-ground')
for r in p['roads']:
 src=x.c['roads'][r['sourceRoadArrayIndex']];require(r['sourceNodeIds']==src['nodes'],'complete-source-road-node-IDs-order',src['id']);require(r['nodes']==[x.nodes[nid] for nid in src['nodes']],'complete-source-road-node-coordinates-order',src['id']);require(all(r.get(k)==v for k,v in src.items() if k!='nodes'),'every-other-road-field-exact-including-width-direction',src['id'])
# Geometry audit exact local polygons plus conservative bbox lower-bound proof for every omitted global obstacle.
def audited(poly,ids,isbody,label):
 N=x.nearset(ids);q=x.audit(poly,N);require(not x.failures(q,isbody),'external-clearance:'+label,q)
 bb=x.bbox(poly);carrierbb=x.bbox([v for i in ids for v in x.c['buildings'][i]])
 omittedSources=[x.bgap(bb,b) for i,po,b in x.bs if i not in ids and x.bgap(carrierbb,b)>=80]
 omittedRoads=[x.bgap(bb,b)-r['width']/2 for r,j,a,d,b in x.allsegments if x.bgap(carrierbb,b)>=80]
 omittedWater=[x.bgap(bb,x.bbox(po)) for po in x.water if x.bgap(carrierbb,x.bbox(po))>=80]+[x.bgap(bb,x.bbox([a,b]))-3 for a,b in x.wl if x.bgap(carrierbb,x.bbox([a,b]))>=80]
 omittedGround=[x.bgap(bb,x.bbox(o['poly'])) for o in x.oldground if x.bgap(carrierbb,x.bbox(o['poly']))>=80]
 omittedBody=[x.bgap(bb,x.bbox(o['poly'])) for o in x.oldbody if x.bgap(carrierbb,x.bbox(o['poly']))>=80]
 lower={'otherSources':min(omittedSources,default=9999),'roadsAfterHalfWidth':min(omittedRoads,default=9999),'waterAfterBuffer':min(omittedWater,default=9999),'oldGround':min(omittedGround,default=9999),'oldBody':min(omittedBody,default=9999)}
 limits={'otherSources':2 if isbody else .15,'roadsAfterHalfWidth':2 if isbody else -.001,'waterAfterBuffer':5,'oldGround':1 if isbody else .15,'oldBody':1 if isbody else .15};require(all(lower[k]>=v for k,v in limits.items()),'global-omitted-obstacle-bound:'+label,lower)
 geometry.append({'id':label,'clearance':q,'omittedObstacleGuaranteedLowerBoundsMetres':lower});return q
for m in p['buildings']:
 aid=m['libraryAssetId'];sid=m['sceneId'];require(sid in slookup,'module-known-scene');require(set(m['sourceIndices'])<=set(slookup[sid]['sourceIndices']) and m['sourceIndices'],'module-source-subset-owned-scene');require(aid in ['B01','B02','B03','B04','B05','B06','B07','B08'],'only-admitted-old-native-assets');sc=m['uniformScale'];require(sc in ([1] if aid=='B01' else [.9,1,1.1]),'reasonable-single-positive-scale:'+aid);require(m['rotation']==0 and m['nodeScale']==1,'no-image-rotation-no-second-scale')
 a=x.assets[aid];require(all(abs(v*w-e)<1e-10 for v,w,e in zip(a['worldSizeUnits'],[sc,sc],m['worldSizeUnits'])),'final-worldSize-is-canonical-times-scale-once');require(m['anchorUV']==a['anchorUV'],'anchorUV-retained');require(same(m['footprintPolygonMap'],x.footprint(aid,m['anchorMap'],sc)),'actual-native-footprint-reconstruction');require(m['entryPixel']==x.doors[aid] and math.dist(m['entryMap'],x.pixelmap(x.doors[aid],m['anchorMap'],x.cal[aid],sc))<1e-8,'fixed-visible-native-door-pixel-map')
 require(any(x.inside(m['anchorMap'],x.c['buildings'][i]) for i in m['sourceIndices']),'anchor-in-owned-carrier');audited(m['footprintPolygonMap'],slookup[sid]['sourceIndices'],True,m['persistentId'])
 ap=m['visualApproach'];require(ap['navigationEdgesCreated']==0 and not ap['originalPOIBindingClaimed'],'door-stop-semantic-separation');require(math.dist(ap['centrelineMap'][0],m['walkStartMap'])<1e-8,'walk-start-at-real-threshold');r=next(r for r in x.c['roads'] if r['id']==ap['roadId']);j=ap['segmentIndex'];require(ap['roadNodeRangeInclusive']==[j,j+1],'real-source-road-segment-index');require(all(x.inbounds(x.nodes[nid],'city') for nid in r['nodes'][j:j+2]),'road-approach-segment-blue-entire');a,b=[x.nodes[nid] for nid in r['nodes'][j:j+2]];edge=x.ps(ap['centrelineMap'][-1],a,b)-r['width']/2;require(abs(edge-.03)<1e-7,'walk-end-exact-unchanged-road-shoulder',edge)
 # Initial 0.6m own threshold tolerance is explicit manual-estimate allowance only; every remaining segment/cap must stay outside own body.
 pts=ap['centrelineMap'];d=math.dist(pts[0],pts[1]);cut=x.add(pts[0],x.mul([(pts[1][k]-pts[0][k])/d for k in (0,1)],.6));tail=x.strip(cut,pts[1]);require(tail is not None and x.pp(tail,m['footprintPolygonMap'])>=.05 and all(x.pp(v,m['footprintPolygonMap'])>=.05 for v in ap['polygonsMap'][1:]),'own-entity-clear-after-explicit-threshold-tolerance')
 rt=x.K/'revision-006/integration/assets'/x.assets[aid]['file'];im=Image.open(rt);require(max(im.size)<=280 and x.sha(rt)==x.assets[aid]['sha256'],'shared-runtime-PNG-size-and-SHA:'+aid,{'path':str(rt),'size':im.size,'bytes':rt.stat().st_size,'mode':im.mode})
for i,a in enumerate(p['buildings']):
 for b in p['buildings'][i+1:]:
  gap=x.pp(a['footprintPolygonMap'],b['footprintPolygonMap']);require(gap>=2,'peer-module-body-gap>=2m',gap)
  wg=min([x.pp(po,b['footprintPolygonMap']) for po in a['visualApproach']['polygonsMap']]+[x.pp(po,a['footprintPolygonMap']) for po in b['visualApproach']['polygonsMap']]);require(wg>=.15,'peer-door-path-never-through-peer-module',wg)
for s in p['groundSurfaces']:
 require(s['sceneId'] in slookup and s['owner']==s['sceneId'],'ground-owned-scene');audited(s['polygonMap'],slookup[s['sceneId']]['sourceIndices'],False,s['id'])
 for m in p['buildings']:
  if m['persistentId']==s.get('thresholdOf'):continue
  require(x.pp(s['polygonMap'],m['footprintPolygonMap'])>=.15,'new-ground-outside-every-peer-entity:'+s['id'])
# All paving components form one walkable connected union; garden touches court but never substitutes for paving.
paving=[s for s in p['groundSurfaces'] if s['materialId']=='S01-paving'];seen={0}
while True:
 nxt=seen|{j for j,b in enumerate(paving) if any(x.pp(paving[i]['polygonMap'],b['polygonMap'])<1e-7 for i in seen)}
 if nxt==seen:break
 seen=nxt
require(len(seen)==len(paving),'finite-scene-paving-forms-connected-union',len(seen))
for s in p['groundSurfaces']:
 if s['materialId']=='G02-planting':require(any(x.pp(s['polygonMap'],v['polygonMap'])<1e-7 for v in paving),'garden-adjoins-purposeful-court')
require(all(x.sha(f)==h for f,h in before.items()),'all-input-SHAs-unchanged-after-validation')
result={'status':'passed-static-only-pending-independent-review','planSHA256':x.sha(O/'scene-compound-pilot.json'),'sourceCount':len(ownership),'sceneCount':len(sceneids),'moduleCount':len(modids),'groundSurfaceCount':len(p['groundSurfaces']),'renderedNewCount':0,'userAcceptedNewCount':0,'passedRuleCount':len(checks),'failedRuleCount':0,'checks':checks,'geometry':geometry,'manualFootlineAndHiddenRearUncertaintyRetained':True,'initialOwnDoorThresholdAllowanceMetres':.6,'latestMarketLifeLayerNotInFrozen156SnapshotMustBeRechecked':True}
x.write('static-verification.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['checks','geometry']},ensure_ascii=False))
